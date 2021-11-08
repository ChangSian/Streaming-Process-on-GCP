import requests
import os
import json
from google.cloud import pubsub_v1
import base64

from flask import Flask, request

from localpackage.bearer_oauth import bearer_oauth
import localpackage.twitterapi as twitterapi

app = Flask(__name__)

@app.route('/', methods=["POST"])
def main():
        
    twitterapi.Sample2Pub(bearer_oauth)

    return("", 204)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))