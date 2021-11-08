import sys
import apache_beam as beam
import csv, json
import logging
from apache_beam.options.pipeline_options import PipelineOptions

def run():
    PROJECT='spring-index-327605'
    BUCKET='twitterdemo'
    table_spec= 'spring-index-327605:Twitter.DEMO'
    table_schema = ( 'author_id:STRING, created_at:TIMESTAMP, id:STRING, lang:STRING, \
                    possibly_sensitive:BOOLEAN, like_count:INTEGER, quote_count:INTEGER, \
                    reply_count:INTEGER, retweet_count:INTEGER, source:STRING, text:STRING')
    TOPIC_PATH='projects/spring-index-327605/topics/TwitterStream'
    
    beam_options = PipelineOptions(
         runner='DataflowRunner',
         project=PROJECT,
         job_name='pubsub2bq20211018',
         temp_location='gs://{}/temp'.format(BUCKET),
         staging_location='gs://{0}/staging/'.format(BUCKET),
         region='us-central1',
        streaming=True
    )
    
    class raw_data(beam.DoFn):
        def process(self, element):
            json_response = json.loads(element.decode("utf-8"))
            raw_value = {'author_id':json_response['data']['author_id'],
                        'created_at':json_response['data']['created_at'],
                        'id':json_response['data']['id'],
                        'lang':json_response['data']['lang'],
                        'possibly_sensitive':json_response['data']['possibly_sensitive'],
                        'like_count':json_response['data']['public_metrics']['like_count'],
                        'quote_count':json_response['data']['public_metrics']['quote_count'],
                        'reply_count':json_response['data']['public_metrics']['reply_count'],
                        'retweet_count':json_response['data']['public_metrics']['retweet_count'],
                        'source':json_response['data']['source'],
                        'text':json_response['data']['text'],
                        }
            yield raw_value

    with beam.Pipeline(options=beam_options) as p:
        (
            p  
            | 'Read From Pub/Sub' >> beam.io.ReadFromPubSub(topic=TOPIC_PATH)
            | 'Get Column' >> beam.ParDo(raw_data())
            | 'Write To BQ' >> beam.io.WriteToBigQuery(
                table_spec,
                schema=table_schema,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND)
        )

if __name__ == '__main__':
   logging.getLogger().setLevel(logging.INFO)
   run()