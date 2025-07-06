from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import datetime

app = Flask(__name__)
CORS(app)


client = MongoClient('mongodb://localhost:27017/')
db = client['githubEvents']
collection = db['events']

@app.route('/', methods=['GET'])
def home():
    return "✅ Webhook server is running!"

@app.route('/webhook', methods=['POST'])
def github_webhook():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON received"}), 400

    event_type = request.headers.get('X-GitHub-Event', 'unknown')

   
    if event_type == "ping":
        print("✅ Received ping from GitHub")
        return jsonify({"msg": "pong"}), 200

    
    payload = {
        "action": event_type,
        "author": data.get('sender', {}).get('login', 'unknown'),
        "from_branch": data.get('pull_request', {}).get('head', {}).get('ref'),
        "to_branch": data.get('pull_request', {}).get('base', {}).get('ref'),
        "timestamp": datetime.datetime.utcnow()
    }

    if event_type == "push":
        payload["to_branch"] = data.get("ref", "").split("/")[-1]
        payload["author"] = data.get("pusher", {}).get("name", "unknown")

    
    collection.insert_one(payload)
    print(f"✅ Received GitHub event: {event_type}")
    print("✅ Stored event to MongoDB")

    return jsonify({"status": "success"}), 200


@app.route('/events', methods=['GET'])
def get_events():
    events = list(collection.find().sort('timestamp', -1))
    for e in events:
        e['_id'] = str(e['_id'])  
    return jsonify(events)

if __name__ == '__main__':
    app.run(port=5000)
