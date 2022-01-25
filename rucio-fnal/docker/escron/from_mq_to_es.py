'''
Connect to a Rucio message stream and inform a designated endpoinnt of transfer and deletion events
'''
import argparse
import logging
import stomp
import sys
import elasticsearch as es

from json import loads as jloads
from time import sleep

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logFormatter = logging.Formatter("%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s")
logHandler = logging.StreamHandler(sys.stdout)
logHandler.setFormatter(logFormatter)
logger.addHandler(logHandler)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('broker_host',
            help='Rucio message broker URL')
    parser.add_argument('broker_port', type=int,
            help='Rucio message broker port')
    parser.add_argument('broker_queue',
            help='The Rucio message broker queue to subscribe to.')
    parser.add_argument('subscription_id',
            help='ID to be used for the subscription. Used for reconnecting to a SUBSCRIPTION ensure completed processing.', nargs='+')
    parser.add_argument('consumer_host',
            help='The destination ElasticSearch ingest URL.')
    parser.add_argument('consumer_port',
            help='The destination ElasticSearch ingest port.')
    parser.add_argument('--ssl-cert', default='/opt/rucio/hostcert.pem',
            help='SSL Certificate for Rucio connection')
    parser.add_argument('--ssl-key', default='/opt/rucio/hostkey.pem',
            help='SSL Key for Rucio connection')
    parser.add_argument('--chunk-size', type=int, default=1,
            help='Number of STOMP messages to process at once.')
    parser.add_argument('--es_username', default='guest',
            help='The username to connect to ElasticSearch with.')
    parser.add_argument('--es_password', default='guest',
            help='The password to authenticate to the ElasticSearch user with.')
    parser.add_argument('--vhost', default='/',
            help='The virtual host that will be used to connect to the message broker.')
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
  def __init__(self, consumer_host, consumer_port, es_username, es_password):
    es_host = f'https://{consumer_host}:{consumer_port}/ingest'
    self.__es = es.Elasticsearch(es_host)
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
      logger.info("creating doc_type %s %s" % (indexName, typeName))
      ret = self.__create_index_type(indexName,typeName)
      logger.info(ret)
      if not ret: 
        return ret
    """
    res = self.__es.index(index=indexName, doc_type=indexName, body=body)
    #res1 = self.__es1.index(index=indexName,body=body)
    logger.info(res)
    return res['result'] == 'created'
    

class STOMPConsumer(stomp.ConnectionListener):
    def __init__(self, conn, consumer_host, consumer_port, chunk_size, subscription_id, es_username, es_password):
        self.__conn = conn
        self.__chunk_size = chunk_size
        self.__subscription_id = subscription_id
        self.__ids = []
        self.__reports = []
        self.__esConn = ElasticConn(consumer_host, consumer_port, es_username, es_password)
  
    def on_error(self, headers, message):
        pass
        # Send message to StatsD
  
    def on_disconnected(self):
        logger.info('on disconnected')
        sleep(60)
        #self.__conn.start()
        self.__conn.connect(wait=True)
        self.__conn.subscribe(destination=queue, ack='client-individual', id=self.__subscription_id)
  
    def on_message(self, headers, message):
        # Send message to StatsD
        # Sanity check
        #logger.info(headers)
        #logger.info(message)
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
                if k.endswith('_at'):
                    if v:
                        report['payload'][k] = v.split('.')[0]
        except:
            pass
  
        self.__ids.append(msg_id)
        self.__reports.append({'id': msg_id, 'body': report})
  
        if len(self.__reports) >= self.__chunk_size:
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

if __name__ == '__main__':
    logger.info('Getting program arguments:')
    args = parse_arguments()
    logger.info(args)

    conn = stomp.Connection12(
        [ (args.broker_host, args.broker_port) ],
        use_ssl=True,
        ssl_cert_file=args.ssl_cert,
        ssl_key_file=args.ssl_key,
        reconnect_attempts_max=1,
        vhost=args.vhost)
    
    stomp_consumer = STOMPConsumer(
        conn,
        args.consumer_host,
        args.consumer_port,
        args.chunk_size,
        args.subscription_id,
        args.es_username,
        args.es_password)

    try:
        conn.set_listener('', stomp_consumer)
        conn.connect(wait=True)
        conn.subscribe(destination=args.broker_queue, ack='client-individual', id=args.subscription_id)
    except Exception as ex:
        logger.info(f'There was an error while connecting: {str(ex)}')
    while True:
        sleep(3600)
    conn.disconnect()
    logger.info('Disconnecting')
