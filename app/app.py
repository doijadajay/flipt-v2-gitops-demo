import os
import requests
from flask import Flask, jsonify, render_template

app = Flask(__name__)

FLIPT_URL = os.getenv(
    "FLIPT_URL",
    "http://flipt-flipt-v2.flipt-demo.svc.cluster.local:8080"
).rstrip("/")
ENVIRONMENT = os.getenv("FLIPT_ENVIRONMENT", "Demo")
NAMESPACE = os.getenv("FLAG_NAMESPACE", "default")
FLAG_KEY = os.getenv("FLAG_KEY", "new-checkout")
ENTITY_ID = os.getenv("ENTITY_ID", "travelco-demo")


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/checkout")
def checkout():
    try:
        response = requests.post(
            f"{FLIPT_URL}/evaluate/v1/boolean",
            headers={
                "Content-Type": "application/json",
                "x-flipt-environment": ENVIRONMENT,
            },
            json={
                "namespaceKey": NAMESPACE,
                "flagKey": FLAG_KEY,
                "entityId": ENTITY_ID,
            },
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()

        enabled = data.get("enabled")
        if not isinstance(enabled, bool):
            raise ValueError(f"Unexpected Flipt response: {data}")

        return jsonify({
            "status": "ok",
            "enabled": enabled,
            "flagKey": FLAG_KEY,
            "environment": ENVIRONMENT,
            "namespace": NAMESPACE,
        })
    except (requests.RequestException, ValueError) as exc:
        return jsonify({
            "status": "error",
            "message": str(exc),
        }), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
