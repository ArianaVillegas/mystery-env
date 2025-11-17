import time
from google.cloud import firestore
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

db = firestore.Client()

def get_player(user):
    doc = db.collection("players").document(user).get()
    return doc.to_dict() if doc.exists else None

def create_player(user, max_attempts):
    db.collection("players").document(user).set({
        "username": user,
        "start_time": time.time(),
        "attempts_left": max_attempts,
        "total_reward": 0,
        "history": []
    })

def update_after_action(user, action, reward):
    doc_ref = db.collection("players").document(user)
    doc = doc_ref.get().to_dict()

    new_attempts = max(0, doc["attempts_left"] - 1)
    new_score = doc["total_reward"] + reward

    doc_ref.update({
        "attempts_left": new_attempts,
        "total_reward": new_score,
        "history": firestore.ArrayUnion([{
            "action": action,
            "reward": reward
        }])
    })

def force_timeout(user):
    db.collection("players").document(user).update({
        "attempts_left": 0
    })

def get_leaderboard():
    docs = db.collection("players").stream()
    rows = [d.to_dict() for d in docs]
    rows.sort(key=lambda x: x["total_reward"], reverse=True)
    return rows
