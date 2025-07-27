from flask import Flask, request
import hmac
import hashlib
import os
import subprocess

app = Flask(__name__)
SECRET = os.getenv("WEBHOOK_SECRET", "changeme").encode()


def verify_signature(payload, signature):
    hash_mac = hmac.new(SECRET, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest("sha256=" + hash_mac, signature)


@app.route("/", methods=["POST"])
def webhook():
    sig = request.headers.get("X-Hub-Signature-256")
    if not sig or not verify_signature(request.data, sig):
        return "Forbidden", 403

    # GitHub sends many event types; we care about pushes to main
    payload = request.json
    if payload.get("ref") == "refs/heads/main":
        subprocess.Popen(["/home/pi/auth-bot/poll-github.sh"])
        return "Updated", 200

    return "Ignored", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
