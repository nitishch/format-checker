import json
import os
import requests
from flask import Flask
from flask import request
from travis import verify_signature
app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello():
    return "This app is to be used for https://github.com/Wilfred/remacs"

@app.route('/verify-results', methods=['POST'])
def verify_results():
    if not verify_signature(request):
        # Request is bad
        return
    payload = request.form.get('payload')
    payload = json.loads(payload)
    try:
        secret = os.environ['OAUTH_TOKEN']
        gh = GithubHandler(secret)
        if payload['pull_request']:
            # This will always be true if Travis is enabled only for pull
            # requests but keeping it here just in case
            matrix = payload['matrix']
            for stage in matrix:
                # We care only about rustfmt stage
                if stage['config']['stage'] == 'rustfmt':
                    if stage['state'] in ['broken', 'failed', 'errored', 'still failing']:
                    # Travis makes a call only in case of error/failure.
                        gh.post_comment(payload['pull_request_number'])
                    break
    except KeyError as err:
        # This may be because of OAUTH_TOKEN not set/JSON format being
        # different from what is expected
        print('Key error: {}'.format(err))
    finally:
        # Flask expects REST end-points to return something
        return "Handled"


class GithubHandler():
    def __init__(self, secret):
        self.secret = secret
        self.base_url = 'https://api.github.com/repos/nitishch/remacs'

    def post_comment(self, pull_request_id):
        comment_text = "Code format check failed. Please use `rustfmt` to format the code. For instructions, see [CONTRIBUTING.md](https://github.com/Wilfred/remacs/blob/master/CONTRIBUTING.md)"
        url = '{}/issues/{}/comments'.format(self.base_url, pull_request_id)
        headers = {'User-Agent': 'Pesky Bot',
                   'Accept': 'application/vnd.github.v3+json',
                   'Authorization': 'token {}'.format(self.secret)
        }
        body = {'body': comment_text}
        response = requests.post(url, json=body, headers=headers)
        if response.status_code != 201:
            # Log the response body. This might help for debugging later
            print('Response {}: {}'.format(response.status_code, response.json()))


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)