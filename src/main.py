from flask import Flask
from webhook_handler import webhook

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    return webhook()

if __name__ == '__main__':
    app.run(debug=True)
