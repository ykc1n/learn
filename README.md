# Nightspirit Learn

A private LAN learning library with React, a Python HTTP server, and SQLite.
Read books, take chapter quizzes and section exams, save notes and bookmarks,
and track reading progress and a daily streak. The interface uses a black,
slightly glassy theme with larger reading text.

## Courses

| Course | Reading material | Assessments |
| --- | --- | --- |
| You Don't Know JS Yet, second edition | Complete available unmodified source; unfinished volumes labeled | 25 quizzes, volume exams, final |
| The C Programming Language, second edition | 12 original companion readings; import your own PDF for the book | 11 quizzes, section exams, final |
| Beej's Guide to Network Concepts | Full official version 1.11.1: 43 chapters, projects, and appendices; diagrams and project downloads included | 43 quizzes, 9 section exams, final |

Each quiz has five original questions. Exams select up to 20 questions from the
relevant chapters, with chapter coverage balanced where the limit permits.
The final samples the full question bank; one sitting does not test every
chapter of a long book. Passing is 80%. Attempts resume and retakes keep earlier
results. Reading completion and quiz mastery are tracked separately.

All devices share one learning profile. Notes, results, activity, reading
position, and imported PDFs stay on the server computer. No cloud database,
accounts, or runtime CDN is used. The daily streak uses America/Phoenix time.

## Requirements

- Node.js 24 or newer and npm, for building the frontend.
- Python 3.11 or newer, with timezone data. No Python packages are required.
- Git, to clone the repository.
- A trusted private IPv4 LAN. Linux with systemd is supported for automatic startup.

## Quick start on this computer only

Clone this repository, then open a terminal in its folder:

```sh
npm ci
npm run build
python3 server.py --loopback --port 8081
```

Visit **http://127.0.0.1:8081**. This mode accepts only requests from this
computer. `npm run build` also copies the pinned PDF.js browser assets locally.
The first server start creates `data/learning.sqlite3` automatically.

## Make it available on your Wi-Fi

Find the server computer's private IPv4 address and subnet. On Linux, use:

```sh
ip -4 address
ip -4 route
```

For example, if your Wi-Fi address is `192.168.1.50/24`, the network is
`192.168.1.0/24`. Substitute **your own** values below:

```sh
NIGHTSPIRIT_SUBNET=192.168.1.0/24 python3 server.py --host 192.168.1.50 --port 8081
```

Open **http://192.168.1.50:8081** on another device connected to that Wi-Fi.
Reserve the computer's address in your router's DHCP settings so it remains
stable. The computer must be awake and connected, and the server must be running.

The server binds only to the specified private IPv4 address. It rejects clients
outside the configured subnet, checks the HTTP Host header, and checks Origin
on browser writes. It refuses wildcard/public bind addresses. It does not listen
on IPv6. `--loopback` is the separate mode for machine-only access.

The original installation also supports detecting a Wi-Fi address automatically
on interface `wlp3s0` inside `192.168.0.0/24`. For another computer, prefer the
explicit `--host` option, or set `NIGHTSPIRIT_INTERFACE` and `NIGHTSPIRIT_SUBNET`.

### Keep access private

- Do not create router port-forwarding rules for this service.
- Do not expose it through a public tunnel or public reverse proxy.
- If a host firewall is enabled, allow TCP 8081 only from your private subnet.
  With UFW on Linux, for the example network:

  ```sh
  sudo ufw allow from 192.168.1.0/24 to 192.168.1.50 port 8081 proto tcp
  ```

- A guest Wi-Fi network with client isolation may prevent access; use your trusted LAN.

There is no login or separation between users. Any allowed LAN client can read
and change the shared learning profile, including notes and PDFs. HTTP is
unencrypted, so use this deployment on your trusted LAN. A router or proxy that
rewrites external clients' source addresses can undermine source-subnet checks;
avoid forwarding or proxying outside traffic into the service.

Putting source code on GitHub does not publish the running server. GitHub Pages
cannot run this Python/SQLite application. Deploy it on a local computer using
the instructions here.

## Private domain name

To use `nightspirit.xyz`, create a **local DNS override** in your router or a local
DNS server, pointing the name to the server's private address. All clients must
use that DNS resolver. Then open `http://nightspirit.xyz:8081`.

For a private subdomain of a domain you own, for example `learn.outerwall.xyz`,
set the local DNS override and run:

```sh
NIGHTSPIRIT_SUBNET=192.168.1.0/24 NIGHTSPIRIT_DOMAIN=learn.outerwall.xyz python3 server.py --host 192.168.1.50 --port 8081
```

A DNS name only selects an address; private binding, subnet checks, firewall,
and the absence of external forwarding control access. You do not need a public
DNS record or public hosting for this setup. Browser secure-DNS settings may
bypass your local resolver; configure clients to use the LAN DNS if needed.

## Automatic startup on Linux

After building the frontend, run the installer with your own address and subnet:

```sh
python3 scripts/install-service.py --host 192.168.1.50 --subnet 192.168.1.0/24 --domain nightspirit.xyz
systemctl --user status nightspirit-learn
```

It creates a user service with the correct absolute paths, restricted address
families, read-only application files, and write access to `data/`. It enables
and starts the service. To start it even before you log in:

```sh
sudo loginctl enable-linger "$USER"
```

Useful commands:

```sh
systemctl --user restart nightspirit-learn
systemctl --user stop nightspirit-learn
journalctl --user -u nightspirit-learn -n 50 --no-pager
```

If the address changes, rerun the installer with the new address and adjust DNS.
On Windows or macOS, use the manual Python command; configure your OS's startup
facility if you want it to launch automatically.

## Updates and testing

Back up your data before updating, then:

```sh
git pull --ff-only
npm ci
npm run build
python3 -m unittest discover -s tests
systemctl --user restart nightspirit-learn
```

For a manually launched server, stop and restart the Python command instead.
Tests use temporary SQLite databases, including HTTP tests, and do not alter your
learning profile. They check full Beej coverage and mirror hashes, grading,
resumable attempts, streak boundaries, and restricted asset/PDF access.

## PDFs and backups

Import your own C book PDF in **Library settings → Your PDFs**. It is stored as
`data/c-book.pdf`; the upload limit is 30 MiB. The copyrighted C book is not
included in this repository. Beej's guide needs no PDF import.

Create a consistent SQLite backup:

```sh
python3 backup.py
```

The backup goes to a timestamped folder under `data/backups/` and includes
imported PDFs. You can choose another directory with `--output /path/to/backup`.
The script honors `NIGHTSPIRIT_DB` if you use a custom database location.
Avoid replacing an imported PDF while a backup is running. The UI's JSON export
contains progress, notes, attempts, and activity, but does not contain PDF files.

To restore a database backup, stop the service, preserve the existing `data`
folder, and copy the backup's `learning.sqlite3` and PDFs into a fresh `data`
folder. Restart the service. Do not mix a restored database with old SQLite
`-wal` or `-shm` files.

The repository excludes `data/`, SQLite files, imported PDFs, `.env` files,
`node_modules/`, generated PDF.js assets, and build output. Review `git status`
before committing changes, and never upload personal backups.

## Layout

```text
src/                     React library, reader, quizzes, progress UI
server.py                LAN-only API, server-side grading, SQLite storage
content/catalog.json     Courses, chapters, and assessment grouping
content/questions.json   Original companion quiz bank (never served as an asset)
content/beej/            Complete original HTML mirror and project files
content/ydkjs/           Unmodified licensed JavaScript source
content/c/               Original C companion lessons
scripts/                 Build asset preparation and Linux service installer
tests/                   Backend and content verification
backup.py                Database/PDF backup tool
```

## Licenses

Application code and original companion assessments: MIT. Reproduced book texts
retain their own noncommercial, no-derivatives licenses. See
[THIRD-PARTY.md](THIRD-PARTY.md) and the authors' notices in the reproduced books.
