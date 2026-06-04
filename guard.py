#guard.py
#called by the preexec zsh hook in real time

import sys
from detector import analyze
from logger import log_command, init_db

def check_command(cmd):
    init_db() #safe to call, won't overwrite data
    matches = analyze(cmd)
    if matches:
        match = matches[0]
        log_command(command=cmd, flagged=True, severity=match['severity'], reason=match['reason'])
        print(f"[{match['severity'].upper()}] {cmd}")
        print(f" => {match['reason']}")
        sys.exit(1)
    # all clear
    log_command(command=cmd, flagged=False)
if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(0)  # no command passed, proceed silently
    cmd = sys.argv[1]
    check_command(cmd)