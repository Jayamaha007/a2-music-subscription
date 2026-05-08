"""
ECS backend entry point.
Runs a Flask app on port 80 exposing the full music subscription API.
Includes CORS headers so the frontend can call from a different origin.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from routes.auth import auth_bp
from routes.music import music_bp
from routes.subscriptions import subscriptions_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp)
app.register_blueprint(music_bp)
app.register_blueprint(subscriptions_bp)

# ALB health check endpoint 
@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
