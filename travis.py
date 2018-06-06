# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import json
import logging

import requests
from OpenSSL.crypto import verify, load_publickey, FILETYPE_PEM, X509
from OpenSSL.crypto import Error as SignatureError

logger = logging.getLogger(__name__)

# Make sure you use the correct config URL, the .org and .com 
# have different keys!
# https://api.travis-ci.org/config
# https://api.travis-ci.com/config
TRAVIS_CONFIG_URL = 'https://api.travis-ci.com/config'

def verify_signature(request):
    signature = _get_signature(request)
    print('Signature: {}'.format(signature))
    payload = request.form.get('payload')
    print('Payload: {}'.format(payload))
    try:
        public_key = _get_travis_public_key()
    except requests.Timeout:
        logger.error({"message": "Timed out when attempting to retrieve Travis CI public key"})
        return HttpResponseBadRequest({'status': 'failed'})
    except requests.RequestException as e:
        logger.error({"message": "Failed to retrieve Travis CI public key", 'error': e.message})
        return HttpResponseBadRequest({'status': 'failed'})
    try:
        check_authorized(signature, public_key, payload)
        print("Check Succeeded")
    except SignatureError:
        # Log the failure somewhere
        print("Check failed")
        return HttpResponseBadRequest({'status': 'unauthorized'})

def check_authorized(signature, public_key, payload):
    """
        Convert the PEM encoded public key to a format palatable for pyOpenSSL,
        then verify the signature
    """
    pkey_public_key = load_publickey(FILETYPE_PEM, public_key)
    certificate = X509()
    certificate.set_pubkey(pkey_public_key)
    verify(certificate, signature, payload, str('sha1'))

def _get_signature(request):
    """
        Extract the raw bytes of the request signature provided by travis
    """
    signature = request.headers['Signature']
    return base64.b64decode(signature)

def _get_travis_public_key():
    """
        Returns the PEM encoded public key from the Travis CI /config endpoint
        """
    response = requests.get(TRAVIS_CONFIG_URL, timeout=10.0)
    response.raise_for_status()
    return response.json()['config']['notifications']['webhook']['public_key']
