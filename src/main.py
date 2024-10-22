from flask import Flask
from webhook_handler import webhook

app = Flask(__name__)

UP = {"status": "up"}


@app.route("/")
def index():
    return UP, 200


@app.route("/webhook", methods=["POST"])
def handle_webhook():
    return webhook()


if __name__ == "__main__":
    app.run(host="0.0.0.0")
