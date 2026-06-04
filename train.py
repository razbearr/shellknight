#train.py
#trains model on isolation on my shell hist, model stored in disk

from sklearn.ensemble import IsolationForest
import pickle
from collections import Counter
import math
from logger import get_all_commands
from features import extract_features
from pathlib import Path

MODEL_PATH = Path(__file__).parent / "models" / "isolation_forest.pkl"


def train():
    cmds = get_all_commands()
    cmds = [c for c in cmds if c["timestamp"] is not None]
    # build command rarity map from shell history
    base_commands = []
    for cmd in cmds:
        tokens = cmd["command"].split()
        if tokens:
            base_commands.append(tokens[0])
    counter = Counter(base_commands)
    total = sum(counter.values())

    x=[]
    for cmd in cmds:
        tokens = cmd["command"].split()
        if not tokens:
            continue
        base_cmd = tokens[0]
        count = counter.get(base_cmd, 0)
        command_rarity = -math.log((count + 1) / (total + 1))
        features = extract_features(cmd["command"],cmd["timestamp"],command_rarity)
        x.append(features)   
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(x)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"model": model,"command_counter": dict(counter),"total_commands": total}, f)
    print("Model trained and saved.")

if __name__ == "__main__":
    train()