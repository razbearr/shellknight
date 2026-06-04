# validate_features.py
# checks if the features actually separate malicious from benign commands using dtrizna's dataset (from github) as ground truth

import requests
import zipfile
import io
import time
from features import extract_features

def load_datasets():
    print("Loading benign commands from NL2Bash...")
    benign_raw = requests.get("https://raw.githubusercontent.com/dtrizna/slp/main/data/nl2bash.cm").text.strip().split("\n")

    print("Loading malicious commands...")
    zraw = requests.get("https://github.com/dtrizna/slp/raw/main/data/malicious.zip").content
    with zipfile.ZipFile(io.BytesIO(zraw)) as z:
        with z.open("malicious.cm", pwd="infected".encode()) as f:
            malicious_raw = [x.strip().decode() for x in f.readlines()]

    print(f"Loaded {len(benign_raw)} benign, {len(malicious_raw)} malicious commands\n")
    return benign_raw, malicious_raw

def average_features(commands, label):
    # extract features for every command and average each feature (the freq=1 since these cmds arent from my history)
    fake_ts = int(time.time()) #also timestamp is fake yeah 
    all_features = []
    for cmd in commands:
        try:
            f = extract_features(cmd, fake_ts, command_rarity=0)
            all_features.append(f)
        except:
            continue
    
    feature_names = ["length", "hour", "arg_count", 
                     "pipe_count", "redirect_count", 
                     "network_risk", "sudo_risk", "tmp_flag","command_rarity"]
    
    print(f"{label} ({len(all_features)} commands)")
    for i, name in enumerate(feature_names):
        avg = sum(row[i] for row in all_features) / len(all_features)
        print(f"{name}: {avg:.3f}")
    print()
    return all_features

if __name__ == "__main__":
    benign, malicious = load_datasets()
    benign_features = average_features(benign, "BENIGN")
    malicious_features = average_features(malicious, "MALICIOUS")