#logger.py
import sqlite3
from pathlib import Path
import time

#building path
# shellknight db lives in data/ folder
DB_PATH = Path(__file__).parent/"data"/"shellknight.db"

#initializing db
def init_db():
    DB_PATH.parent.mkdir(exist_ok=True) #creates data/ folder if it doesn't already exist
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS commands(id INTEGER PRIMARY KEY AUTOINCREMENT, 
                timestamp INTEGER NOT NULL, command TEXT NOT NULL, flagged INTEGER NOT NULL DEFAULT 0,
                severity TEXT, reason TEXT, session TEXT, ml_score REAL)""")
    con.commit()
    con.close()
    add_ml_score_column() 

#stores a single command event in the database. called by guard.py everytime a cmd is intercepted
def log_command(command, flagged=False, severity=None, reason=None, session=None, timestamp=None, ml_score=None):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor() # ? ? ? ? since placeholders for values cuz secur n prevents sql injection + automatic escaping
    ts = timestamp if timestamp else int(time.time())
    cur.execute("""INSERT INTO commands(timestamp, command, flagged, severity, reason, session, ml_score) 
                VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                (ts, command, 1 if flagged else 0, severity, reason, session, ml_score))
    con.commit()
    con.close()

#reads recent 20 commands from the shellknight db
def get_recent_commands(limit=20):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""SELECT timestamp, command, flagged, severity, reason, session, ml_score FROM commands ORDER BY timestamp DESC LIMIT ?""", (limit,))
    rows = cur.fetchall()
    con.close()
    columns = ["timestamp", "command", "flagged", "severity", "reason", "session", "ml_score"]
    cmds = [dict(zip(columns,row)) for row in rows]
    return cmds

def get_all_commands():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""SELECT timestamp, command, flagged, severity, reason, session, ml_score FROM commands ORDER BY timestamp DESC""")
    rows = cur.fetchall()
    con.close()
    columns = ["timestamp", "command", "flagged", "severity", "reason", "session", "ml_score"]
    cmds = [dict(zip(columns,row)) for row in rows]
    return cmds

# how many times a command is used
# is behavorial baseline

def get_cmd_frequency():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT command, COUNT(*) as frequency FROM commands group by command ORDER BY frequency DESC")
    rows = cur.fetchall()
    con.close()
    columns =["command", "frequency"]
    freq = [dict(zip(columns,row)) for row in rows]
    return freq


#to check if the db is empty
def is_db_empty():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM commands")
    count = cur.fetchone()[0]
    con.close()
    return count == 0

def clear_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("DELETE FROM commands")
    con.commit()
    con.close()
    print("DB cleared.")

def add_ml_score_column():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    try:
        cur.execute("ALTER TABLE commands ADD COLUMN ml_score REAL")
        con.commit()
        print("Added ml_score column.")
    except sqlite3.OperationalError:
        pass  # column already exists, skip silently
    con.close()

def update_ml_score(command, timestamp, ml_score):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""UPDATE commands SET ml_score = ? 
                   WHERE command = ? AND timestamp = ?""",
                (ml_score, command, timestamp))
    con.commit()
    con.close()


#testing
if __name__ == "__main__":
    init_db()
    log_command("ls -la", flagged=False)
    log_command("sudo su", flagged=True, severity="medium", reason="Privilege escalation")
    log_command("git push origin main", flagged=False)
    
    print("Recent commands:")
    for entry in get_recent_commands():
        print(entry)
    
    print("\nFrequency:")
    for entry in get_cmd_frequency():
        print(entry)