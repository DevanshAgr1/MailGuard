import json, sqlite3, random
from datetime import datetime, timedelta
from pathlib import Path
BASE = Path(__file__).resolve().parents[2]
DB = BASE / 'spam_detector.db'

def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = conn()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS predictions (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL, message_preview TEXT, prediction TEXT NOT NULL, confidence REAL NOT NULL, risk_level TEXT NOT NULL, source TEXT DEFAULT 'dashboard', processing_time_ms REAL, signals_json TEXT, is_demo INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS model_runs (id INTEGER PRIMARY KEY AUTOINCREMENT, model_version TEXT, trained_at TEXT, model_name TEXT, accuracy REAL, precision REAL, recall REAL, f1 REAL, roc_auc REAL);
    CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
    ''')
    c.commit(); c.close()

def seed_demo():
    init_db(); c = conn()
    count = c.execute('SELECT COUNT(*) FROM predictions WHERE is_demo=1').fetchone()[0]
    if count: c.close(); return count
    random.seed(42)
    samples = [
      ('Congratulations! You won a cash reward. Claim now at http://example.invalid/prize', 'spam', .973, 'high'),
      ('Your transaction has been successfully completed. Thank you for using our service.', 'ham', .991, 'low'),
      ('URGENT: verify your account immediately to avoid suspension. Click the link.', 'spam', .961, 'high'),
      ('Hey, are you joining the study group at 5 today?', 'ham', .984, 'low'),
      ('Limited time offer! Get 70% off your subscription today.', 'spam', .944, 'high'),
      ('Reminder: your assignment submission is due tomorrow.', 'ham', .987, 'low'),
      ('You are selected for a FREE prize. Claim your reward now!', 'spam', .981, 'high'),
      ('Can you send me the notes from class when you get a chance?', 'ham', .995, 'low')]
    now = datetime.now()
    for i in range(160):
        msg, pred, conf, risk = random.choice(samples)
        ts = now - timedelta(days=random.randint(0, 29), hours=random.randint(0, 23), minutes=random.randint(0,59))
        conf2 = max(.72, min(.999, conf + random.uniform(-.045,.008)))
        c.execute('INSERT INTO predictions(timestamp,message_preview,prediction,confidence,risk_level,source,processing_time_ms,signals_json,is_demo) VALUES(?,?,?,?,?,?,?,?,1)',
                  (ts.isoformat(timespec='seconds'), msg[:140], pred, conf2, risk, 'demo', round(random.uniform(8,32),2), json.dumps([])))
    c.commit(); c.close(); return 160

def add_prediction(result, message, source='dashboard', is_demo=0):
    c=conn(); c.execute('INSERT INTO predictions(timestamp,message_preview,prediction,confidence,risk_level,source,processing_time_ms,signals_json,is_demo) VALUES(?,?,?,?,?,?,?,?,?)',
      (datetime.now().isoformat(timespec='seconds'), message[:140], result['prediction'], result['confidence'], result['risk_level'], source, result['processing_time_ms'], json.dumps(result['signals']), is_demo)); c.commit(); c.close()

def recent(limit=50):
    c=conn(); rows=[dict(x) for x in c.execute('SELECT * FROM predictions ORDER BY timestamp DESC LIMIT ?', (limit,)).fetchall()]; c.close(); return rows

def clear_demo():
    c=conn(); c.execute('DELETE FROM predictions WHERE is_demo=1'); n=c.rowcount; c.commit(); c.close(); return n

def analytics():
    c=conn(); rows=c.execute('SELECT * FROM predictions ORDER BY timestamp').fetchall(); c.close()
    total=len(rows); spam=sum(r['prediction']=='spam' for r in rows); ham=total-spam
    daily={}
    for r in rows:
        d=r['timestamp'][:10]; daily.setdefault(d, {'total':0,'spam':0}); daily[d]['total']+=1; daily[d]['spam']+=r['prediction']=='spam'
    confidence=[round(r['confidence']*100,1) for r in rows]
    risks={x:sum(r['risk_level']==x for r in rows) for x in ['low','medium','high']}
    return {'total':total,'spam':spam,'ham':ham,'spam_rate':round(spam/total*100,2) if total else 0,'daily':daily,'confidence':confidence,'risks':risks}
