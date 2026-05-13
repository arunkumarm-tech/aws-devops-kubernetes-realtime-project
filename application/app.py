from flask import Flask
import socket

app = Flask(__name__)

@app.route("/")
def home():
    return {
        "message": "Welcome to Arun's AWS DevOps Kubernetes Real-Time Project",
        "status": "Application running successfully",
        "hostname": socket.gethostname()
    }

@app.route("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
