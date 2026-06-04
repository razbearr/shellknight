#parser.py
import pathlib
from logger import log_command, init_db, is_db_empty, clear_db


hist_zsh = pathlib.Path.home() / ".zsh_history"
hist_bash = pathlib.Path.home() / ".bash_history"

def parsehist(filepath):
    #reads shell history and returns list of dicts. dict has cmd and (opt) timestamp as keys
    cmds=[]
    with open(filepath,"r",errors="ignore") as f: #erros skips bytes which weren't decoded correctly to avoid crash
        for line in f:
            line = line.strip()
            if not line: #skip empty lines
                continue
            #extended format: example ": 1779179286:0;cd Desktop"
            if line.startswith(":"): 
                try:
                    meta, cmd = line.split(";", 1)
                    timestamps = int(meta.split(":")[1].strip())
                except:
                    continue  
                cmds.append({"timestamp":timestamps, "command":cmd})
            else:
                cmd=line
                cmds.append({"timestamp":None, "command":cmd})
    return cmds

def seed_db_from_history():
    init_db()
    clear_db()
    print("Empty DB detected — seeding from shell history...")

    all_commands = []
    for filepath in [hist_zsh, hist_bash]:
        if filepath.exists():
            cmds = parsehist(filepath)
            all_commands.extend(cmds)
            print(f"  Read {len(cmds)} commands from {filepath}")
        else:
            print(f"  {filepath} not found, skipping.")
    # sort by timestamp so history goes in chronological order
    # commands without timestamps go last
    all_commands.sort(key=lambda x: x["timestamp"] if x["timestamp"] else float("inf"))

    for entry in all_commands:
        log_command(
            command=entry["command"],
            flagged=False,
            timestamp=entry["timestamp"]  # pass historical timestamp
        )
    print(f"Seeded {len(all_commands)} commands into DB.")

if __name__ == "__main__":
    seed_db_from_history()