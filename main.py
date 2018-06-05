import os
import logging
from flask import Flask
from flask import request

app = Flask(__name__)
# From https://gist.github.com/seanbehan/547f5fc599bde304c89694a98c102bab
if 'DYNO' in os.environ:
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.ERROR)


@app.route('/verify-results', methods=['GET'])
def hello():
    return "excellent!"

@app.route('/verify-results', methods=['POST'])
def verify_results():
    app.logger.info('%s', request.data)
    return request.data


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)