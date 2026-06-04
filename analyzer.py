# analyzer.py
# reads recent session from sqlite and asks groq if the pattern looks suspicious

import os
from groq import Groq
from logger import get_recent_commands
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


#turns list of cmd dicts into readable chronological text for the LLM
def format_session(commands):
    lines = []
    for cmd in reversed(commands):  # oldest first, chronological order
        flag = "[FLAGGED]" if cmd['flagged'] else ""
        lines.append(f"{flag} {cmd['command']}".strip())
    return "\n".join(lines)

#pulls recent commands from sqlite db and asks groq to asses the session pattern 
def analyze_session(limit=20):
    commands = get_recent_commands(limit)
    if not commands:
        print("No commands in database yet.")
        return
    session_text = format_session(commands)

    prompt = f"""You are a terminal security monitor analyzing a user's recent shell session AS A WHOLE.

Here are their last {limit} commands in chronological order:

{session_text}

Commands marked [FLAGGED] were already caught by regex rules.

Do NOT analyze each command individually.
Analyze the SEQUENCE as a whole story. Look for:
- Reconnaissance patterns (probing system info, users, network)
- Escalating privilege attempts
- Suspicious sequences even if individual commands seem innocent
- Data exfiltration patterns

Respond in exactly this format ONCE for the entire session:
RISK: [LOW/MEDIUM/HIGH/CRITICAL]
PATTERN: [one sentence describing the overall session behavior]
SUSPICIOUS_COMMANDS: [list the specific commands that contributed to the risk]
DETAIL: [2-3 sentences explaining what the sequence of commands suggests]
RECOMMENDATION: [one concrete action the user should take]"""

    response = client.chat.completions.create(model="llama-3.1-8b-instant",max_tokens=300,messages=[{"role": "user", "content": prompt}])
    return response.choices[0].message.content

if __name__ == "__main__":
    result = analyze_session()
    print(result)