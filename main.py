import os
from flask import Flask
from flask import request
app = Flask(__name__)

@app.route('/verify-results', methods=['GET'])
def hello():
    return "excellent!"

@app.route('/verify-results', methods=['POST'])
def verify_results():
    return "excellent!"


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)