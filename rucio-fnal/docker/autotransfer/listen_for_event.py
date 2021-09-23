# Subscribe to the Rucio instance and listen for the completion of a particular event
import time
import sys
import os
import json
import argparse
import queue
import threading
import logging
import stomp


logging.basicConfig(format='%(asctime)-15s %(name)s %(levelname)s %(message)s', level=logging.INFO)
logging.getLogger('stomp.py').setLevel(logging.WARNING)
logger = logging.getLogger('rucio_rabbitmq')


_ack_queue = None
def _send_acks(conn):
    while True:
        ack, msgid = _ack_queue.get()
        try:
            if ack:
                conn.ack(msgid)
            else:
                conn.nack(msgid)
        except (stomp.exception.ConnectionClosedException, stomp.exception.NotConnectedException) as ex:
            pass


class TestListener(stomp.ConnectionListener):
    def __init__(self, conn, sub_id, host, cert, key, vhost, durable):
        self.conn = conn
        self.sub_id = sub_id
        self.host = host
        self.cert = cert
        self.key = key
        self.vhost = vhost
        self.durable = durable
        self.shutdown = False

    def on_disconnected(self):
        if self.shutdown:
            return

    def on_error(self, message):
        logger.error('Received an error "%s"', message)

    def on_message(self, message):
        message_id = message.headers['message-id']
        try:
            msg_data = json.loads(message.body)
        except ValueError:
            logger.error('Unable to decode JSON data')
            _ack_queue.put( (True, message_id) )
            return

        event_type = msg_data['event_type']
        logger.info('Successfully received message: %s', msg_data)

        if event_type == 'transfer-done':
            logger.error(f'Transfer successful: {msg_data}')
            self.shutdown = True

        if event_type == 'transfer-submission_failed':
            logger.error(f'Transfer submission failed: {msg_data}')
            self.shutdown = True



def connect(hosts, cert, key=None, vhost='/', durable=False, unsubscribe=False, topic=None):
    if topic is None:
        raise ValueError('Please provide a topic to subscribe to')

    if key is None:
        key = cert

    conn = stomp.Connection12(
        hosts,
        use_ssl=True,
        ssl_cert_file=cert,
        ssl_key_file=key,
        vhost=vhost,
        heartbeats=(10000,10000)
    )

    if durable:
        sub_id = 'MY SUB ID'
    else:
        import uuid
        sub_id = uuid.uuid1()

    if not unsubscribe:
        listener = TestListener(conn, sub_id, hosts, cert, key, vhost, durable)
        conn.set_listener('TestListener', listener)
    else:
        listener = None

    while True:
        # Retry starting the connection until it works
        try:
            conn.connect(wait=True)
            break
        except stomp.exception.ConnectFailedException:
            logger.warn('Unable to connect; sleeping 10 seconds')
            time.sleep(10)


    # Start up a thread to send acks and nacks for messages
    global _ack_queue
    _ack_queue = queue.Queue()
    ack_thread = threading.Thread(target=_send_acks, args=(conn,))
    ack_thread.daemon = True
    ack_thread.start()

    logger.info('Connected to broker')

    if durable:
        headers = { 'durable': 'true', 'auto-delete': 'false' }
    else:
        headers = None

    conn.subscribe(destination=topic, id=sub_id, ack='client-individual', headers=headers)
    logger.info('Subscribed to %s with id %s', topic, sub_id)


    if unsubscribe:
        # delete the subscription and exit
        # apparently you have to subscribe to a queue before unsubscribing
        # even if it's a durable queue you're trying to delete
        conn.unsubscribe(sub_id, headers)
        logger.info('Unsubscribed from %s with id %s', destination, sub_id)
        conn.disconnect()
        return

    try:
        while True:
            time.sleep(1)
            if listener.shutdown == True:
                logger.info('Shutting down!')
                break
    except KeyboardInterrupt:
        if listener:
            listener.shutdown = True
    finally:
        conn.disconnect()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='Broker host', nargs='+')
    parser.add_argument('--listen-event', help='Event to watch for in the STOMP stream')
    parser.add_argument('--cert', help='Client certificate')
    parser.add_argument('--key', help='Client key')
    parser.add_argument('--topic', help='RabbitMQ Broker topic to sub to')
    parser.add_argument('--durable', help='Create a durable STOMP queue', action='store_true', default=False)
    parser.add_argument('--unsubscribe', help='Delete the subscription (does little without --durable)', action='store_true', default=False)
    parser.add_argument('--debug', help='Debug output', action='store_true', default=False)
    args = parser.parse_args()

    if args.debug:
        logging.getLogger('stomp.py').setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    cert = args.cert or os.environ.get('X509_USER_CERT') or os.path.expanduser('~/.globus/usercert.pem')
    key = args.key or os.environ.get('X509_USER_KEY') or args.cert or os.environ.get('X509_USER_CERT') or os.path.expanduser('~/.globus/userkey.pem')

    hosts = [ tuple(a.split(':',1)) for a in args.host ] # Split list of hostname port args into tuples of (hostname, port)

    try:
        connect(hosts, cert, key, durable=args.durable, unsubscribe=args.unsubscribe, topic=args.topic)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
