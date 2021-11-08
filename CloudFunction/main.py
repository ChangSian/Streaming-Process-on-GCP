#from ratelimit import limits
import requests
import os
import json
from google.cloud import pubsub_v1
from localpackage.bearer_oauth import bearer_oauth
import localpackage.twitterapi as twitterapi

#FIFTEEN_MINUTES = 900

#@limits(calls=50, period=FIFTEEN_MINUTES)
def filtered_stream(data, context):
    #event, context
    #filter_rules
    filter_rules = [
    #    {"value": " (của OR Một) lang:vi", "tag": "language"},
    #    {"value": "(Vietnamese OR Vietnam) lang:en", "tag": "Keyword"},
        {"value": "entity:Vietnam", "tag": "entity"},
    ]

    rules = twitterapi.get_rules()
    delete = twitterapi.delete_all_rules(rules)
    set = twitterapi.set_rules(filter_rules)
    twitterapi.Filtered2Pub(set)

def sample_stream(data, context):
    twitterapi.Sample2Pub()
