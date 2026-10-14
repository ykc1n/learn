#!/usr/bin/env python3
"""Create a consistent SQLite backup plus the user's imported PDF."""
import argparse
import os
from datetime import datetime
from pathlib import Path
import shutil
import sqlite3

root=Path(__file__).resolve().parent
database=Path(os.environ.get('NIGHTSPIRIT_DB',str(root/'data/learning.sqlite3')))
parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,default=database.parent/'backups'/datetime.now().strftime('%Y%m%d-%H%M%S'))
args=parser.parse_args()
if not (database).is_file():
    raise SystemExit('The learning database does not exist yet.')
args.output.mkdir(parents=True,exist_ok=False)
with sqlite3.connect(database) as source, sqlite3.connect(args.output/'learning.sqlite3') as destination:
    source.backup(destination)
for pdf in database.parent.glob('*-book.pdf'):
    shutil.copy2(pdf,args.output/pdf.name)
print('Backup saved:',args.output.resolve())
