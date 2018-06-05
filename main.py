import json
import os
import sys
import logging
from flask import Flask
from flask import request

app = Flask(__name__)


@app.route('/verify-results', methods=['GET'])
def hello():
    return "excellent!"

@app.route('/verify-results', methods=['POST'])
def verify_results():
    print("form's content is {}".format(request.form))
    payload = request.form.get('payload')
    print('payload is {}'.format(payload))
    payload = json.loads(payload)
    print('Job has {}'.format(payload['state']))
    print('PR: {}'.format(payload['pull_request']))
    matrix = payload['matrix']
    for stage in matrix:
        # We care only about rustfmt stage
        if stage['config']['stage'] == 'rustfmt':
            if stage['state'] == 'failed':
                print('Aha! Rustfmt failed. Do the necessary things')
    return request.data


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)