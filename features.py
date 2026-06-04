#features.py
from datetime import datetime

def extract_features(command, timestamp, command_rarity):
    feat=[]
    length = len(command)
    hr = datetime.fromtimestamp(timestamp).hour
    tokens = command.split()
    arg_count = max(0, len(tokens) - 1)
    pipe_count = command.count("|")
    redirect_count = (command.count(">>") + command.count("2>") + command.count("<") + command.replace(">>", "").replace("2>", "").count(">"))
    #network risk
    if any(x in command for x in ["nc ", "ncat", "netcat"]):
        network_risk = 3
    elif any(x in command for x in ["nmap", "masscan"]):
        network_risk = 2
    elif any(x in command for x in ["curl", "wget", "ssh"]):
        network_risk = 1
    else:
        network_risk = 0
    #sudo risk
    shell_escalation = ["su", "bash", "sh", "zsh", "visudo"]
    elevated = ["chmod", "chown", "dd", "mount", "passwd"]
    sudo_risk = 0
    if "sudo" in tokens:
        idx = tokens.index("sudo")
        if idx + 1 < len(tokens):
            next_cmd = tokens[idx + 1]
            if next_cmd in shell_escalation:
                sudo_risk = 3
            elif next_cmd in elevated:
                sudo_risk = 2
            else:
                sudo_risk = 1
        else:
            sudo_risk = 1
    tmp_flag = 1 if "/tmp/" in command else 0

    feat = [length, hr, arg_count, pipe_count, redirect_count, network_risk, sudo_risk, tmp_flag,command_rarity]
    return feat