#!/usr/bin/env python3
"""Private Wi-Fi learning library. Standard-library HTTP API + SQLite."""
import argparse
from datetime import datetime, date, timedelta
import ipaddress
import json
import math
import mimetypes
import os
from pathlib import Path
import random
import re
import sqlite3
import subprocess
import uuid
import traceback
from zoneinfo import ZoneInfo
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent
DB = Path(os.environ.get('NIGHTSPIRIT_DB', str(ROOT / 'data/learning.sqlite3')))
TZ = ZoneInfo(os.environ.get('NIGHTSPIRIT_TIMEZONE', 'America/Phoenix'))
NETWORK = ipaddress.ip_network(os.environ.get('NIGHTSPIRIT_SUBNET', '192.168.0.0/24'))
CATALOG = json.loads((ROOT / 'content/catalog.json').read_text())
LESSONS = {lesson['id']: lesson for book in CATALOG['books'] for section in book['sections'] for lesson in section['lessons']}
BANK = json.loads((ROOT / 'content/questions.json').read_text())
PDF_BOOKS = {b['id']: b for b in CATALOG['books'] if b.get('pdf') or b['id'] == 'c'}

def pdf_file(book):
    return DB.parent / ('c-book.pdf' if book == 'c' else book + '-book.pdf')

def pdf_setting(book):
    return 'pdf_page' if book == 'c' else 'pdf_page:' + book

EXTRA_EXAMS = json.loads((ROOT / 'content/section-questions.json').read_text()) if (ROOT / 'content/section-questions.json').exists() else {}
ASSESSMENTS = {}
for book in CATALOG['books']:
    for section in book['sections']:
        pool = []
        for lesson in section['lessons']:
            if lesson['id'] in BANK:
                key = 'quiz:' + lesson['id']
                ASSESSMENTS[key] = {'title': lesson['title'] + ' · Quiz', 'kind': 'quiz', 'book': book['id'], 'pool': BANK[lesson['id']]}
                pool.extend(BANK[lesson['id']])
                lesson['quiz'] = key
        pool.extend(EXTRA_EXAMS.get(section['id'], []))
        if pool:
            key = 'exam:' + section['id']
            ASSESSMENTS[key] = {'title': section['title'] + ' · Section exam', 'kind': 'exam', 'book': book['id'], 'pool': pool}
            section['exam'] = key
            section['examQuestions'] = min(20, len(pool))
    final_pool = [q for section in book['sections'] for lesson in section['lessons'] for q in BANK.get(lesson['id'], [])]
    final_pool.extend(q for section in book['sections'] for q in EXTRA_EXAMS.get(section['id'], []))
    key = 'final:' + book['id']
    ASSESSMENTS[key] = {'title': book['title'] + ' · Final exam', 'kind': 'exam', 'book': book['id'], 'pool': final_pool}
    book['final'] = key


def today():
    return datetime.now(TZ).date()


class Connection(sqlite3.Connection):
    def __exit__(self, *args):
        try:
            return super().__exit__(*args)
        finally:
            self.close()


def connect():
    conn = sqlite3.connect(DB, timeout=15, factory=Connection)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    return conn


def init_db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.execute('PRAGMA journal_mode=WAL')
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS progress(lesson TEXT PRIMARY KEY, fraction REAL NOT NULL DEFAULT 0, position REAL NOT NULL DEFAULT 0, completed INTEGER NOT NULL DEFAULT 0, note TEXT NOT NULL DEFAULT '', bookmark INTEGER NOT NULL DEFAULT 0, updated TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS activity(day TEXT PRIMARY KEY, visits INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY, assessment TEXT NOT NULL, questions TEXT NOT NULL, answers TEXT NOT NULL DEFAULT '{}', created TEXT NOT NULL, submitted TEXT, result TEXT);
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        ''')
        if 'position' not in {r['name'] for r in conn.execute('PRAGMA table_info(progress)')}:
            conn.execute('ALTER TABLE progress ADD COLUMN position REAL NOT NULL DEFAULT 0')


def record_activity(conn):
    conn.execute('INSERT INTO activity(day) VALUES (?) ON CONFLICT(day) DO UPDATE SET visits=visits+1', (today().isoformat(),))


def streak_stats(days, now=None):
    now = now or today()
    active = {date.fromisoformat(d) for d in days}
    cursor = now if now in active else now - timedelta(days=1)
    current = 0
    while cursor in active:
        current += 1
        cursor -= timedelta(days=1)
    longest = run = 0
    previous = None
    for day in sorted(active):
        run = run + 1 if previous and day == previous + timedelta(days=1) else 1
        longest = max(longest, run)
        previous = day
    return {'current': current, 'longest': longest, 'today': now.isoformat(), 'activeToday': now in active, 'totalDays': len(active), 'days': sorted(d.isoformat() for d in active), 'timezone': str(TZ)}


def state():
    with connect() as conn:
        progress = {r['lesson']: dict(r) for r in conn.execute('SELECT * FROM progress') if r['lesson'] in LESSONS}
        results = []
        for row in conn.execute('SELECT id,assessment,submitted,result FROM sessions WHERE submitted IS NOT NULL ORDER BY submitted DESC'):
            if row['assessment'] not in ASSESSMENTS: continue
            results.append({'id': row['id'], 'assessment': row['assessment'], 'submitted': row['submitted'], **json.loads(row['result'])})
        active = [dict(r) for r in conn.execute('SELECT id,assessment,created FROM sessions WHERE submitted IS NULL ORDER BY created DESC') if r['assessment'] in ASSESSMENTS]
        days = [r['day'] for r in conn.execute('SELECT day FROM activity')]
        page = conn.execute("SELECT value FROM settings WHERE key='pdf_page'").fetchone()
        pdfs = {}
        for book in PDF_BOOKS:
            file = pdf_file(book)
            saved = conn.execute('SELECT value FROM settings WHERE key=?', (pdf_setting(book),)).fetchone()
            pdfs[book] = {'available': file.exists(), 'page': int(saved['value']) if saved else 1, 'version': file.stat().st_mtime_ns if file.exists() else 0}
    return {'progress': progress, 'attempts': results, 'activeSessions': active, 'streak': streak_stats(days), 'pdfs': pdfs, 'pdfAvailable': pdfs['c']['available'], 'pdfPage': pdfs['c']['page'], 'pdfVersion': pdfs['c']['version']}



def public_session(row):
    questions = json.loads(row['questions'])
    result = {'id': row['id'], 'assessment': row['assessment'], 'title': ASSESSMENTS[row['assessment']]['title'], 'kind': ASSESSMENTS[row['assessment']]['kind'], 'book': ASSESSMENTS[row['assessment']]['book'], 'questions': [{k: q[k] for k in ('id', 'prompt', 'options')} for q in questions], 'answers': json.loads(row['answers']), 'submitted': row['submitted']}
    if row['result']:
        result['result'] = json.loads(row['result'])
    return result


def start_session(key, fresh=False):
    assessment = ASSESSMENTS[key]
    with connect() as conn:
        if not fresh:
            row = conn.execute('SELECT * FROM sessions WHERE assessment=? AND submitted IS NULL ORDER BY created DESC LIMIT 1', (key,)).fetchone()
            if row:
                return public_session(row)
        pool = assessment['pool']
        if assessment['kind'] == 'exam':
            groups = {}
            for q in pool:
                groups.setdefault(q['id'].rsplit('-q', 1)[0], []).append(q)
            # Balanced exams touch every chapter where the 20-question limit permits.
            group_keys = list(groups)
            random.shuffle(group_keys)
            picked = [random.choice(groups[k]) for k in group_keys[:20]]
            picked_ids = {q['id'] for q in picked}
            remaining = [q for q in pool if q['id'] not in picked_ids]
            picked.extend(random.sample(remaining, min(20 - len(picked), len(remaining))))
            random.shuffle(picked)
        else:
            picked = list(pool)
        questions = []
        for q in picked:
            options = list(enumerate(q['options']))
            random.shuffle(options)
            questions.append({**q, 'options': [o[1] for o in options], 'answer': next(i for i, o in enumerate(options) if o[0] == q['answer'])})
        sid = uuid.uuid4().hex
        conn.execute('INSERT INTO sessions(id,assessment,questions,created) VALUES (?,?,?,?)', (sid, key, json.dumps(questions), datetime.now(TZ).isoformat()))
        record_activity(conn)
        return public_session(conn.execute('SELECT * FROM sessions WHERE id=?', (sid,)).fetchone())


def update_session(sid, answers, submit=False):
    with connect() as conn:
        row = conn.execute('SELECT * FROM sessions WHERE id=?', (sid,)).fetchone()
        if not row:
            raise KeyError('Assessment attempt not found')
        if row['submitted']:
            return public_session(row)
        questions = json.loads(row['questions'])
        allowed = {q['id']: q for q in questions}
        if not isinstance(answers, dict) or any(k not in allowed or type(v) is not int or not 0 <= v < len(allowed[k]['options']) for k, v in answers.items()):
            raise ValueError('Invalid answer selection')
        conn.execute('UPDATE sessions SET answers=? WHERE id=?', (json.dumps(answers), sid))
        if submit:
            if len(answers) != len(questions):
                raise ValueError('Answer every question before submitting')
            review = [{'id': q['id'], 'prompt': q['prompt'], 'options': q['options'], 'selected': answers[q['id']], 'answer': q['answer'], 'explanation': q['explanation'], 'correct': answers[q['id']] == q['answer']} for q in questions]
            correct = sum(q['correct'] for q in review)
            score = round(correct * 100 / len(questions))
            result = {'score': score, 'correct': correct, 'total': len(questions), 'passed': correct >= math.ceil(len(questions) * .8), 'review': review}
            conn.execute('UPDATE sessions SET submitted=?,result=? WHERE id=?', (datetime.now(TZ).isoformat(), json.dumps(result), sid))
            record_activity(conn)
        return public_session(conn.execute('SELECT * FROM sessions WHERE id=?', (sid,)).fetchone())


class Server(ThreadingHTTPServer):
    daemon_threads = True
    def verify_request(self, request, client_address):
        ip = ipaddress.ip_address(client_address[0])
        return ip in NETWORK or self.server_address[0] == '127.0.0.1' and ip.is_loopback


class Handler(BaseHTTPRequestHandler):
    server_version = 'Nightspirit/1.0'
    def valid_host(self):
        addr, port = self.server.server_address
        return self.headers.get('Host', '').lower() in {f'{addr}:{port}', f"{os.environ.get('NIGHTSPIRIT_DOMAIN', 'nightspirit.xyz')}:{port}"}

    def respond(self, status, data, mime='application/json', extra=None):
        body = json.dumps(data, ensure_ascii=False).encode() if mime == 'application/json' else data
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Cache-Control', 'no-store' if mime == 'application/json' else 'no-cache')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-src 'self' blob:; object-src 'none'; worker-src 'self'; base-uri 'none'; connect-src 'self'")
        if extra:
            for k, v in extra.items(): self.send_header(k, v)
        self.end_headers()
        if self.command != 'HEAD': self.wfile.write(body)

    def file(self, path, base):
        path = path.resolve()
        if not path.is_relative_to(base.resolve()) or not path.is_file():
            return self.respond(404, {'error': 'File not found'})
        self.respond(200, path.read_bytes(), mimetypes.guess_type(path.name)[0] or 'application/octet-stream')

    def do_GET(self):
        if not self.valid_host(): return self.respond(403, {'error': 'Use the private Wi-Fi address or nightspirit.xyz'})
        path = unquote(urlsplit(self.path).path)
        if path == '/api/catalog': return self.respond(200, CATALOG)
        if path == '/api/state': return self.respond(200, state())
        if path == '/api/export':
            with connect() as conn:
                data = {'version': 1, 'exported': datetime.now(TZ).isoformat(), 'progress': [dict(r) for r in conn.execute('SELECT * FROM progress')], 'activity': [dict(r) for r in conn.execute('SELECT * FROM activity')], 'sessions': [dict(r) for r in conn.execute('SELECT * FROM sessions')]}
            return self.respond(200, data, extra={'Content-Disposition': 'attachment; filename="nightspirit-progress.json"'})
        if path.startswith('/api/lesson/'):
            key = path.removeprefix('/api/lesson/')
            if key not in LESSONS: return self.respond(404, {'error': 'Reading not found'})
            lesson = LESSONS[key]
            text = (ROOT / 'content' / lesson['path']).read_text()
            if lesson.get('format') == 'html': text = re.search(r'<body[^>]*>(.*?)</body>', text, re.S).group(1)
            return self.respond(200, {**lesson, 'markdown': text})
        if path.startswith('/api/session/'):
            with connect() as conn: row = conn.execute('SELECT * FROM sessions WHERE id=?', (path.removeprefix('/api/session/'),)).fetchone()
            return self.respond(200, public_session(row)) if row and row['assessment'] in ASSESSMENTS else self.respond(404, {'error': 'Attempt not found'})
        if path.startswith('/books/'):
            relative = path.removeprefix('/books/')
            book_root = relative.split('/')[0]
            if book_root not in ('ydkjs', 'beej'): return self.respond(404, {'error': 'Reading not found'})
            return self.file(ROOT / 'content' / relative, ROOT / 'content' / book_root)
        if path == '/api/c-pdf': return self.file(pdf_file('c'), DB.parent)
        if path.startswith('/api/pdf/'):
            book = path.removeprefix('/api/pdf/')
            if book not in PDF_BOOKS: return self.respond(404, {'error': 'Unknown PDF book'})
            return self.file(pdf_file(book), DB.parent)
        if path == '/health': return self.respond(200, {'status': 'local server online', 'database': 'sqlite', 'timezone': str(TZ)})
        if path.startswith('/api/'): return self.respond(404, {'error': 'Endpoint not found'})
        dist = ROOT / 'dist'
        if path == '/' or path == '/index.html': return self.file(dist / 'index.html', dist)
        return self.file(dist / path.lstrip('/'), dist)

    do_HEAD = do_GET

    def do_POST(self):
        if not self.valid_host(): return self.respond(403, {'error': 'Private host required'})
        origin = self.headers.get('Origin')
        if origin and origin != 'http://' + self.headers.get('Host', ''):
            return self.respond(403, {'error': 'Same-origin requests only'})
        path = urlsplit(self.path).path
        try:
            pdf_book = 'c' if path == '/api/c-pdf' else path.removeprefix('/api/pdf/') if path.startswith('/api/pdf/') else None
            if pdf_book is not None and pdf_book not in PDF_BOOKS:
                return self.respond(404, {'error': 'Unknown PDF book'})
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= (30 * 1024 * 1024 if pdf_book is not None else 100_000):
                return self.respond(413, {'error': 'Request size is invalid'})
            body = self.rfile.read(length)
            if pdf_book is not None:
                if not body.startswith(b'%PDF-'): raise ValueError('Choose a PDF file')
                tmp = DB.parent / (pdf_book + '-' + uuid.uuid4().hex + '.pdf.tmp')
                tmp.write_bytes(body)
                tmp.replace(pdf_file(pdf_book))
                return self.respond(200, {'ok': True})
            data = json.loads(body)
            if not isinstance(data, dict): raise ValueError('Expected an object')
            if path == '/api/activity':
                with connect() as conn: record_activity(conn)
                return self.respond(200, state()['streak'])
            if path == '/api/progress':
                key = data['lesson']
                if key not in LESSONS: raise ValueError('Unknown reading')
                with connect() as conn:
                    conn.execute('INSERT OR IGNORE INTO progress(lesson,updated) VALUES (?,?)', (key, datetime.now(TZ).isoformat()))
                    row = dict(conn.execute('SELECT * FROM progress WHERE lesson=?', (key,)).fetchone())
                    if 'fraction' in data:
                        value = float(data['fraction'])
                        if not math.isfinite(value) or not 0 <= value <= 1: raise ValueError('Invalid reading position')
                        row['fraction'] = max(row['fraction'], value)
                        row['position'] = value
                    if 'completed' in data:
                        if type(data['completed']) is not bool: raise ValueError('Invalid completion state')
                        row['completed'] = int(data['completed'])
                    if 'bookmark' in data:
                        if type(data['bookmark']) is not bool: raise ValueError('Invalid bookmark')
                        row['bookmark'] = int(data['bookmark'])
                    if 'note' in data:
                        if not isinstance(data['note'], str) or len(data['note']) > 20_000: raise ValueError('Note is too long')
                        row['note'] = data['note']
                    conn.execute('UPDATE progress SET fraction=?,position=?,completed=?,bookmark=?,note=?,updated=? WHERE lesson=?', (row['fraction'], row['position'], row['completed'], row['bookmark'], row['note'], datetime.now(TZ).isoformat(), key))
                    record_activity(conn)
                return self.respond(200, state())
            if path == '/api/start':
                if data.get('assessment') not in ASSESSMENTS: raise ValueError('Unknown assessment')
                return self.respond(200, start_session(data['assessment'], bool(data.get('fresh'))))
            if path == '/api/pdf-page':
                book = data.get('book', 'c')
                if book not in PDF_BOOKS: raise ValueError('Unknown PDF book')
                page = data.get('page')
                if type(page) is not int or not 1 <= page <= 10000: raise ValueError('Invalid page number')
                with connect() as conn:
                    conn.execute("INSERT INTO settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (pdf_setting(book), str(page)))
                    record_activity(conn)
                return self.respond(200, {'ok': True})
            if path in ('/api/answers', '/api/submit'):
                return self.respond(200, update_session(data['session'], data['answers'], path == '/api/submit'))
            return self.respond(404, {'error': 'Endpoint not found'})
        except (ValueError, KeyError, TypeError, OverflowError) as e:
            return self.respond(400, {'error': str(e)})
        except Exception:
            traceback.print_exc()
            return self.respond(500, {'error': 'Unable to save. Please retry.'})


def wifi_address():
    interfaces = json.loads(subprocess.check_output(['ip', '-j', '-4', 'address', 'show', 'dev', os.environ.get('NIGHTSPIRIT_INTERFACE', 'wlp3s0')], text=True))
    for item in interfaces:
        for address in item.get('addr_info', []):
            if ipaddress.ip_address(address['local']) in NETWORK:
                return address['local']
    raise RuntimeError('Original private Wi-Fi network unavailable; refusing to listen.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8081)
    parser.add_argument('--test-loopback', '--loopback', action='store_true')
    parser.add_argument('--host', help='Explicit private IPv4 address on the configured LAN')
    args = parser.parse_args()
    init_db()
    host = '127.0.0.1' if args.test_loopback else args.host or wifi_address()
    if not args.test_loopback:
        address = ipaddress.ip_address(host)
        if address.version != 4 or not address.is_private or address.is_loopback or address not in NETWORK:
            parser.error('--host must be a private IPv4 address within NIGHTSPIRIT_SUBNET')
    with Server((host, args.port), Handler) as server:
        print(f'Local server online: http://{host}:{args.port}', flush=True)
        server.serve_forever()
