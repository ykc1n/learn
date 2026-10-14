import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from datetime import date
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('learning_server', ROOT / 'server.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)

class LearningTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.patch=patch.object(s,'DB',Path(self.temp.name)/'study.sqlite')
        self.patch.start()
        s.init_db()
    def tearDown(self):
        self.patch.stop();self.temp.cleanup()
    def test_streak_boundaries_and_leap_day(self):
        self.assertEqual(s.streak_stats([],date(2026,10,13))['current'],0)
        days=['2026-10-10','2026-10-11','2026-10-12']
        self.assertEqual(s.streak_stats(days,date(2026,10,13))['current'],3)
        self.assertEqual(s.streak_stats(days,date(2026,10,14))['current'],0)
        days+=['2026-10-14']
        st=s.streak_stats(days,date(2026,10,14))
        self.assertEqual((st['current'],st['longest']),(1,3))
        self.assertEqual(s.streak_stats(['2024-02-28','2024-02-29','2024-03-01'],date(2024,3,1))['current'],3)
    def test_one_calendar_day_despite_multiple_visits(self):
        with s.connect() as conn:
            for _ in range(5): s.record_activity(conn)
        st=s.state()['streak']
        self.assertEqual((st['current'],st['totalDays']),(1,1))
    def test_answers_hidden_until_submission_and_sessions_resume(self):
        attempt=s.start_session('quiz:c-ch5')
        self.assertEqual(len(attempt['questions']),5)
        self.assertNotIn('answer',attempt['questions'][0])
        self.assertNotIn('explanation',attempt['questions'][0])
        saved=s.update_session(attempt['id'],{attempt['questions'][0]['id']:2})
        self.assertEqual(saved['answers'][attempt['questions'][0]['id']],2)
        self.assertEqual(s.start_session('quiz:c-ch5')['id'],attempt['id'])
        s.init_db()
        self.assertEqual(s.start_session('quiz:c-ch5')['answers'],saved['answers'])
    def test_grading_validation_and_immutable_completed_attempt(self):
        attempt=s.start_session('quiz:get-started-ch1')
        with self.assertRaises(ValueError):s.update_session(attempt['id'],{},True)
        with self.assertRaises(ValueError):s.update_session(attempt['id'],{'not-a-question':0})
        with s.connect() as conn:
            q=json.loads(conn.execute('SELECT questions FROM sessions WHERE id=?',(attempt['id'],)).fetchone()['questions'])
        answers={item['id']:item['answer'] for item in q}
        result=s.update_session(attempt['id'],answers,True)
        self.assertEqual(result['result']['score'],100)
        self.assertTrue(result['result']['passed'])
        self.assertTrue(all('explanation' in item for item in result['result']['review']))
        unchanged=s.update_session(attempt['id'],{},True)
        self.assertEqual(unchanged['result'],result['result'])
        fresh=s.start_session('quiz:get-started-ch1',True)
        self.assertNotEqual(fresh['id'],attempt['id'])
        self.assertEqual(len(s.state()['attempts']),1)
    def test_eighty_percent_passes_and_sixty_does_not(self):
        for correct_count,passes in [(4,True),(3,False)]:
            a=s.start_session('quiz:c-ch3',True)
            with s.connect() as conn:q=json.loads(conn.execute('SELECT questions FROM sessions WHERE id=?',(a['id'],)).fetchone()['questions'])
            answers={item['id']:item['answer'] if i<correct_count else (item['answer']+1)%4 for i,item in enumerate(q)}
            result=s.update_session(a['id'],answers,True)['result']
            self.assertEqual(result['passed'],passes)
    def test_exam_balanced_and_no_duplicate_questions(self):
        a=s.start_session('exam:scope-closures')
        self.assertEqual(len(a['questions']),20)
        ids=[q['id'] for q in a['questions']]
        self.assertEqual(len(set(ids)),20)
        self.assertEqual(len(set(i.rsplit('-q',1)[0] for i in ids)),10)
    def test_content_and_assessment_coverage(self):
        quizzes=0
        for book in s.CATALOG['books']:
            self.assertIn(book['final'],s.ASSESSMENTS)
            for section in book['sections']:
                for lesson in section['lessons']:
                    self.assertTrue((ROOT/'content'/lesson['path']).is_file())
                    if lesson['kind'] in ['chapter','appendix'] and not lesson.get('placeholder'):
                        self.assertIn(lesson['id'],s.BANK)
                        self.assertEqual(len(s.BANK[lesson['id']]),5)
                        quizzes+=1
        self.assertEqual(quizzes,36 + 43)
        questions=[q for pool in s.BANK.values() for q in pool]
        self.assertEqual(len(questions),5 * quizzes)
        self.assertEqual(len(set(q['id'] for q in questions)),len(questions))
        for q in questions:
            self.assertEqual(len(q['options']),4)
            self.assertEqual(len(set(q['options'])),4)
            self.assertTrue(q['explanation'])
    def test_source_text_unmodified(self):
        source=ROOT.parents[1]/'work/ydkjs'
        if not source.exists():self.skipTest('Original checkout not present')
        for path in source.rglob('*'):
            if path.is_file() and '.git' not in path.parts:
                self.assertEqual(path.read_bytes(),(ROOT/'content/ydkjs'/path.relative_to(source)).read_bytes())
    def test_network_restrictions(self):
        server=type('Fake',(),{'server_address':('192.168.0.122',8081)})()
        self.assertTrue(s.Server.verify_request(server,None,('192.168.0.42',1234)))
        self.assertFalse(s.Server.verify_request(server,None,('8.8.8.8',1234)))
        self.assertFalse(s.Server.verify_request(server,None,('192.168.1.1',1234)))
        self.assertFalse(s.Server.verify_request(server,None,('127.0.0.1',1234)))

    def test_beej_complete_mirror_and_assessments(self):
        import hashlib
        book=next(b for b in s.CATALOG['books'] if b['id']=='beej')
        lessons=[l for section in book['sections'] for l in section['lessons']]
        self.assertEqual([l['number'] for l in lessons],list(range(1,44)))
        self.assertEqual(len(book['sections']),9)
        self.assertNotIn('tcpip',[b['id'] for b in s.CATALOG['books']])
        for l in lessons:
            quiz=s.start_session('quiz:'+l['id'])
            self.assertEqual(quiz['book'],'beej')
            self.assertEqual(len(quiz['questions']),5)
        for section in book['sections']:
            exam=s.start_session(section['exam'])
            self.assertEqual(exam['book'],'beej')
            ids=[q['id'].rsplit('-q',1)[0] for q in exam['questions']]
            self.assertTrue({l['id'] for l in section['lessons']} <= set(ids))
        self.assertEqual(len(s.start_session('final:beej')['questions']),20)
        manifest=json.loads((ROOT/'content/beej/manifest.json').read_text())
        for name,expected in manifest['files'].items():
            self.assertEqual(hashlib.sha256((ROOT/'content/beej'/name).read_bytes()).hexdigest(),expected)

    def test_removed_course_records_do_not_break_state(self):
        with s.connect() as conn:
            conn.execute("INSERT INTO progress(lesson,updated) VALUES ('tcpip-ch1','2026-10-14')")
            conn.execute("INSERT INTO sessions(id,assessment,questions,created) VALUES ('old','quiz:tcpip-ch1','[]','2026-10-14')")
        self.assertNotIn('tcpip-ch1',s.state()['progress'])
        self.assertEqual(s.state()['activeSessions'],[])

    def test_http_reading_assets_and_pdf(self):
        import threading,urllib.request,urllib.error
        server=s.Server(('127.0.0.1',0),s.Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base='http://127.0.0.1:'+str(server.server_port)
        try:
            pdf=b'%PDF-1.4\nC fixture\n%%EOF'
            request=urllib.request.Request(base+'/api/c-pdf',data=pdf,headers={'Content-Type':'application/pdf'})
            with urllib.request.urlopen(request) as response:self.assertTrue(json.load(response)['ok'])
            with urllib.request.urlopen(base+'/api/pdf/c') as response:self.assertEqual(response.read(),pdf)
            with urllib.request.urlopen(base+'/api/lesson/beej-ch2') as response:
                lesson=json.load(response)
                self.assertEqual(lesson['format'],'html')
                self.assertIn('Circuit Switched',lesson['markdown'])
                self.assertNotIn('<style>',lesson['markdown'])
            with urllib.request.urlopen(base+'/books/beej/ip-routing.svg') as response:self.assertIn(b'<svg',response.read())
            for path in ['/books/questions.json','/books/beej/../questions.json','/api/pdf/tcpip','/api/lesson/tcpip-ch1']:
                with self.assertRaises(urllib.error.HTTPError) as error:urllib.request.urlopen(base+path)
                self.assertEqual(error.exception.code,404);error.exception.close()
        finally:
            server.shutdown();server.server_close();thread.join()

if __name__=='__main__':unittest.main()
