import requests
import os
import json
from google.cloud import pubsub_v1


if __name__ == "__main__":
    
    from localpackage.bearer_oauth import bearer_oauth
    import localpackage.twitterapi as twitterapi

    twitterapi.Sample2Pub(bearer_oauth)