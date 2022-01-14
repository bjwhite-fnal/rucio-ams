import argparse
import typing
import stomp
import logging
from time import sleep
from json import loads as jloads
import elasticsearch as es

def parse_arguments() -> dict:
    parser = argparse.ArgumentParser()

    #broker = 'msg-dune-rucio.okd.fnal.gov'
    #broker_port = 443
    #queue = '/topic/rucio.events.dune'
    #subscription_id = 1
    #consumer = 'landscape.fnal.gov'
    #consumer_port = 9200
    #ssl_cert_file = '/monitoring/rucio.fnal.gov_crt.pem'
    #ssl_key_file = '/monitoring/rucio.fnal.gov_key.pem'
    #chunksize = 1
    #es_username = "guest"
    #es_password = "guest"
    parser.add_argument('broker_host', help='Rucio message broker URL', nargs='+')
    parser.add_argument('broker_port', help='Rucio message broker port', nargs='+')
    parser.add_argument('broker_queue', help='The Rucio message broker queue to subscribe to.', nargs='+')
    parser.add_argument('subscription_id', help='ID to be used for the subscription. Used for reconnecting to a SUBSCRIPTION ensure completed processing.', nargs='+')
    parser.add_argument('consumer_host', help='The destination ElasticSearch ingest URL.', nargs='+')
    parser.add_argument('consumer_port', help='The destination ElasticSearch ingest port.', nargs='+')
    parser.add_argument('--ssl-cert', default='/opt/rucio/hostcert.pem', help='SSL Certificate for Rucio connection', nargs='+')
    parser.add_argument('--ssl-key', default='/opt/rucio/hostkey.pem', help='SSL Key for Rucio connection', nargs='+')
    parser.add_argument('--chunk-size', type=int, default=1, help='Number of AMQP messages to process at once.', nargs='+')
    parser.add_argument('--es_username', default='guest', help='The username to connect to ElasticSearch with.', nargs='+')
    parser.add_argument('--es_password', default='guest', help='The password to authenticate to the ElasticSearch user with.', nargs='+')

    return parser.parse_args()


indexMap = {
               'rucio_transfer': {
                      "properties": {
                            "created_at": {
                                "type": "date",
                                "format": "yyyy-MM-dd HH:mm:ss"
                            },
                            "event_type": {
                                "type": "keyword",
                            },
                            "activity": {
                                "type": "keyword",
                            },
                            "request-id": {
                                "type": "keyword",
                            },
                            "duration": {
                                "type": "float",
                            },
                            "checksum-adler": {
                                "type": "keyword",
                            },
                            "checksum-md5": {
                                "type": "keyword",
                            },
                            "file-size": {
                                "type": "long",
                            },
                            "bytes": {
                                "type": "long",
                            },
                            "guid": {
                                "type": "keyword",
                            },
                            "previous-request-id": {
                                "type": "keyword",
                            },
                            "protocol": {
                                "type": "keyword",
                            },
                            "scope": {
                                "type": "keyword",
                            },
                            "name": {
                                "type": "keyword",
                            },
                            "src-type": {
                                "type": "keyword",
                            },
                            "src-rse": {
                                "type": "keyword",
                            },
                            "src-url": {
                                "type": "keyword",
                            },
                            "dst-type": {
                                "type": "keyword",
                            },
                            "dst-rse": {
                                "type": "keyword",
                            },
                            "dst-url": {
                                "type": "keyword",
                            },
                            "reason": {
                                "type": "keyword",
                            },
                            "transfer-endpoint": {
                                "type": "keyword",
                            },
                            "transfer-id": {
                                "type": "keyword",
                            },
                            "transfer-link": {
                                "type": "keyword",
                            },
                            "created_at": {
                                "type": "date",
                                "format": "YYYY-MM-DD HH:mm:ss"
                            },
                            "submitted_at": {
                                "type": "date",
                                "format": "YYYY-MM-DD HH:mm:ss"
                            },
                            "started_at": {
                                "type": "date",
                                "format": "YYYY-MM-DD HH:mm:ss"
                            },
                            "transferred_at": {
                                "type": "date",
                                "format": "YYYY-MM-DD HH:mm:ss"
                            },
                            "queued_at": {
                                "type": "date",
                                "format": "YYYY-MM-DD HH:mm:ss"
                            },
                            "tool-id": {
                                "type": "keyword",
                            },
                            "account": {
                                "type": "keyword",
                            },
                      }
               },
               'rucio_deletion': {
                      "properties": {
                            "created_at": {
                                "type": "date",
                                "format": "yyyy-MM-dd HH:mm:ss"
                            },
                            "event_type": {
                                "type": "keyword",
                            },
                            "scope": {
                                "type": "keyword",
                            },
                            "name": {
                                "type": "keyword",
                            },
                            "rse": {
                                "type": "keyword",
                            },
                            "file-size": {
                                "type": "long",
                            },
                            "bytes": {
                                "type": "long",
                            },
                            "url": {
                                "type": "keyword",
                            },
                            "duration": {
                                "type": "float",
                            },
                            "reason": {
                                "type": "keyword",
                            },
                            "created_at": {
                                "type": "date",
                                "format": "YYYY-MM-DD HH:mm:ss"
                            },
                    }
           
           }
    }


class ElasticConn():
  def __init__(self, consumer_host, consumer_port, auth):
    #self.__es = es.Elasticsearch([host_port[0]],http_auth=auth,consumer_port=host_port[1])
    #self.__es1 = es.Elasticsearch(hosts=[{'host': 'tatties.ph.ed.ac.uk', 'port':9200}], http_auth=('elastic','tek@Edinburgh;123'), timeout=200, max_retries=5, retry_on_timeout=True)
    self.__es = es.Elasticsearch(f'https://{consumer_host}:{consumer_port}/ingest')
    self.__index_type = []

  def __create_index_type(self,indexName,typeName):
    if [indexName,typeName] in self.__index_type:
      return True
    try:
      self.__es.indices.create(index=indexName, ignore=400)
      self.__es.indices.put_mapping(index=indexName, doc_type=typeName, body=indexMap[indexName], ignore=400)
    except:
      pass
      
    self.__index_type.append([indexName,typeName])
    return True

  def index_data(self, indexName, typeName, body):
    """
    if [indexName,typeName] not in self.__index_type:
      logging.info("creating doc_type %s %s" % (indexName, typeName))
      ret = self.__create_index_type(indexName,typeName)
      logging.info(ret)
      if not ret: 
        return ret
    """
    res = self.__es.index(index=indexName, doc_type=indexName, body=body)
    #res1 = self.__es1.index(index=indexName,body=body)
    #logging.info(res)
    return res['result'] == 'created'
    

class AMQConsumer(stomp.ConnectionListener):
  def __init__(self, conn, chunksize, subscription_id):
    self.__conn = conn
    self.__chunksize = chunksize
    self.__subscription_id = subscription_id
    self.__ids = []
    self.__reports = []
    self.__esConn = ElasticConn(host_port = (consumer_host, consumer_port), auth = (es_username, es_password))

  def on_error(self, headers, message):
    pass
    # Send message to StatsD

  def on_disconnected(self):
    logging.info('on disconnected')
    sleep(60)
    #self.__conn.start()
    self.__conn.connect(wait=True)
    self.__conn.subscribe(destination=queue, ack='client-individual', id=self.__subscription_id)

  def on_message(self, headers, message):
    # Send message to StatsD
    # Sanity check
    #logging.info(headers)
    #logging.info(message)
    msg_id = headers['message-id']

    if 'resubmitted' in headers:
      # Send message to StatsD
      # Ignore resubmitted messages
      return

    try:
        report = jloads(message)
    except Exception:
      # Corrupt message, ignore
      # Send message to StatsD
      self.__conn.ack(msg_id, self.__subscription_id)
      return

    try:
      report['payload']['created_at'] = report['created_at']
      report['payload']['event_type'] = report['event_type']
      for k,v in report['payload'].items():
        if k.endswith("_at"):
          if v:
            report['payload'][k] = v.split('.')[0]
    except:
      pass

    self.__ids.append(msg_id)
    self.__reports.append({'id': msg_id, 'body': report})

    if len(self.__reports) >= self.__chunksize:
      self.__send_to_es()
      

  def __send_to_es(self):
    for msg in self.__reports:
      event_type = str(msg['body']['event_type']).lower()
      res = False
      if event_type.startswith('transfer'):
        res = self.__esConn.index_data('rucio_transfer', event_type, msg['body']['payload'])
      elif event_type.startswith('deletion'):
        res = self.__esConn.index_data('rucio_deletion', event_type, msg['body']['payload'])
      else:
        self.__conn.ack(msg['id'],self.__subscription_id)
      if res:
        self.__conn.ack(msg['id'],self.__subscription_id)
    self.__reports = []
    self.__ids = []

if __name__ == "__main__":
  logging.basicConfig(level=30)

  args = parse_arguments()

  conn = stomp.Connection(
          host_and_ports=[(args.broker_host, args.broker_port)],\
          use_ssl=True,\
          ssl_cert_file=args.ssl_cert,\
          ssl_key_file=args.ssl_key,\
          reconnect_attempts_max=1
  )

  amq_consumer = AMQConsumer(conn, args.chunk_size, args.subscription_id)

  try:
    conn.set_listener('', amq_consumer)
    conn.start()
    conn.connect(wait=True)
    conn.subscribe(destination=args.broker_queue, ack='client-individual', id=args.subscription_id)
  except:
    logging.error("There was an error while connecting.")
  while True:
    sleep(3600)
  conn.disconnect()
  logging.info('Disconnecting')
