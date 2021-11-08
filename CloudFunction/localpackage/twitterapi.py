from localpackage.bearer_oauth import bearer_oauth
import os
import json
from google.cloud import pubsub_v1
import time
from datetime import datetime
import http.client
import logging
from google.cloud import logging
import ssl
import requests
from requests_oauthlib import OAuth1
import urllib3
from platform import python_version


# This log can be found in the Cloud Logging console under 'Custom Logs'.
logger_name = "Sample2Pub_CF"
logging_client = logging.Client()
logger = logging_client.logger(logger_name)


def get_rules():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()

def delete_all_rules(rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))

def set_rules(filter_rules):
    if filter_rules is None:
            return None
    payload = {"add": filter_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))

def Filtered2Pub(set):
    error_count = 0
    # https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/guides/connecting
    stall_timeout = 90
    network_error_wait = network_error_wait_step = 0.25
    network_error_wait_max = 16
    http_error_wait = http_error_wait_start = 5
    http_error_wait_max = 320
    http_420_error_wait_start = 480
    chunk_size=500
    
    ##Paramater
    query_params = { 'expansions': 'geo.place_id',
                    'tweet.fields': 'id,text,author_id,created_at,in_reply_to_user_id,lang,public_metrics,source,possibly_sensitive,geo',
                    'user.fields': 'id,name,username,created_at,description,location,public_metrics',
                    'place.fields': 'full_name,id,country,country_code,geo,place_type'}

    # Configure the connection
    publisher = pubsub_v1.PublisherClient()
    topic_name = 'projects/{project_id}/topics/{topic}'.format(
        project_id='spring-index-327605',
        topic='TwitterStream',  # Set this to something appropriate.
    )

    start = time.time()

    try:
        with requests.get("https://api.twitter.com/2/tweets/search/stream", auth=bearer_oauth, params=query_params, stream=True,) as resp:
            if resp.status_code == 200:
                error_count = 0
                http_error_wait = http_error_wait_start
                network_error_wait = network_error_wait_step
                
                print("Stream connected")
                
                #wait on rate limit
                reset = int(resp.headers['x-rate-limit-reset']) - start
                
                for line in resp.iter_lines(chunk_size=chunk_size):
                    if line:
                        json_response = json.loads(line)
                        data = json.dumps(json_response, indent=4, sort_keys=True).encode('utf-8')
                        future = publisher.publish(topic_name, data)
                        future.result()
                    else:
                        log.debug("Received keep-alive signal")
                        
                    limit = time.time() - start

                    if limit > 500  :
                        # closing the connection           
                        resp.close()
                        time.sleep(10)

                        #check execusion
                        print("Close Connection-3")
                        break
                        
                    else:
                        continue
            else:
                print(resp.headers)
                log.error("Stream encountered HTTP error: %d", resp.status_code)
                error_count += 1
                if resp.status_code == 429:
                    if http_error_wait < http_420_error_wait_start:
                        http_error_wait = http_420_error_wait_start

                resp.close()
                time.sleep(http_error_wait)

                http_error_wait *= 2
                if http_error_wait > http_error_wait_max:
                    http_error_wait = http_error_wait_max
                print("Close Connection-3")
                    
    except (requests.ConnectionError, requests.Timeout,
            requests.exceptions.ChunkedEncodingError,
            ssl.SSLError, urllib3.exceptions.ReadTimeoutError,
            urllib3.exceptions.ProtocolError) as exc:
        # This is still necessary, as a SSLError can actually be
        # thrown when using Requests
        # If it's not time out treat it like any other exception
        if isinstance(exc, ssl.SSLError):
            if not (exc.args and "timed out" in str(exc.args[0])):
                raise

        print(resp.headers)
        log.error("Stream connection has errored or timed out")
        resp.close()
        limit = min((time.time() - start), 20)
        time.sleep(limit)
        print("Close Connection-3")

def Sample2Pub():
    """Paramater Setting ."""
    error_count = 0
    stall_timeout = 90
    network_error_wait = network_error_wait_step = 0.25
    network_error_wait_max = 16
    http_error_wait = http_error_wait_start = 5
    http_error_wait_max = 240
    http_429_error_wait_start = 60
    chunk_size=500
    running = True

    ##Query Paramater
    query_params = { 'expansions': 'geo.place_id',
                    'tweet.fields': 'id,text,author_id,created_at,in_reply_to_user_id,lang,public_metrics,source,possibly_sensitive,geo',
                    'user.fields': 'id,name,username,created_at,description,location,public_metrics',
                    'place.fields': 'full_name,id,country,country_code,geo,place_type'}
    
    # Configure the connection
    publisher = pubsub_v1.PublisherClient()
    topic_name = 'projects/{project_id}/topics/{topic}'.format(
        project_id='spring-index-327605',
        topic='SampleStream',  # Set this to something appropriate.
    )

    # Requests Session
    user_agent = (
            f"Python/{python_version()} "
            f"Requests/{requests.__version__} "
        )
    
    session = requests.Session()
    session.headers["User-Agent"] = user_agent

    start = time.time()
    limit = time.time() - start
    try:
        while running and limit <= 480:
            try:
                with session.request(
                        "GET", "https://api.twitter.com/2/tweets/sample/stream", params=query_params, headers=None, data=None,
                        timeout=stall_timeout, stream=True, auth=bearer_oauth,
                        verify=True, proxies={}
                    ) as resp:
                    if resp.status_code == 200:
                        logger.log_text(str(resp.headers), severity="INFO")                   
                        error_count = 0
                        http_error_wait = http_error_wait_start
                        network_error_wait = network_error_wait_step
                        
                        logger.log_text("Stream connected", severity="INFO")
                        
                        
                        for line in resp.iter_lines(chunk_size=chunk_size):
                            if line:
                                json_response = json.loads(line)
                                data = json.dumps(json_response, indent=4, sort_keys=True).encode('utf-8')                       
                                future = publisher.publish(topic_name, data)
                                future.result()
                            #else:
                                #logger.log_text("Received keep-alive signal", severity="DEBUG")
                                
                            limit = time.time() - start

                            if (limit > 480) or (not running):
                                break

                        if resp.raw.closed:
                            logger.log_text("Stream connection closed by Twitter", severity="ERROR")
                            
                    else:
                        logger.log_text(str(resp.status_code), severity="ERROR")
                        logger.log_text(str(resp.headers), severity="ERROR")
                        logger.log_text("Stream encountered HTTP error: %d", severity="ERROR")
                        
                        if not running:
                            break

                        error_count += 1

                        if resp.status_code == 429:               
                            if http_error_wait < http_429_error_wait_start:
                                http_error_wait = http_429_error_wait_start
                
                        time.sleep(http_error_wait)

                        http_error_wait *= 2
                        if http_error_wait > http_error_wait_max:
                            http_error_wait = http_error_wait_max
                        
                        limit = time.time() - start + http_error_wait

                            
            except (requests.ConnectionError, requests.Timeout,
                    requests.exceptions.ChunkedEncodingError,
                    ssl.SSLError, urllib3.exceptions.ReadTimeoutError,
                    urllib3.exceptions.ProtocolError) as exc:
                # This is still necessary, as a SSLError can actually be
                # thrown when using Requests
                # If it's not time out treat it like any other exception
                logger.log_text(str(exc), severity="ERROR")
                if isinstance(exc, ssl.SSLError):
                    if not (exc.args and "timed out" in str(exc.args[0])):
                        raise
                        
                logger.log_text(str(resp.headers), severity="ERROR")
                logger.log_text("Stream connection has errored or timed out", severity="ERROR")

                time.sleep(network_error_wait)
                network_error_wait += network_error_wait_step
                if network_error_wait > network_error_wait_max:
                    network_error_wait = network_error_wait_max
    except Exception as exc:
        logger.log_text(str(exc), severity="INFO")
        logger.log_text("Stream encountered an exception",  severity="INFO")
    finally:
        session.close()
        running = False
        logger.log_text("Stream disconnected",  severity="INFO")
        
    return    