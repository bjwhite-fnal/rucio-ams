#!/bin/bash

set -x

cat << EOF > /etc/rabbitmq/rabbitmq.conf

loopback_users.guest = false
listeners.ssl.default = 5671
ssl_options.cacertfile = /etc/rabbitmq/ssl/ca.pem
ssl_options.certfile = /etc/rabbitmq/ssl/hostcert.pem
ssl_options.fail_if_no_peer_cert = true
ssl_options.keyfile = /etc/rabbitmq/ssl/hostkey.pem
ssl_options.verify = verify_peer
ssl_options.depth  = 5

ssl_options.versions.1 = tlsv1.2

# ciphers from https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/TLS_Cipher_String_Cheat_Sheet.md advanced list. Some of these are actually TLS1.3 ciphers and so won't work, but this should be compatible with openssl 1.0.1e+, and so SL6+

#ssl_options.ciphers.1 = TLS_AES_256_GCM_SHA384
#ssl_options.ciphers.2 = TLS_CHACHA20_POLY1305_SHA256
#ssl_options.ciphers.3 = TLS_AES_128_GCM_SHA256
ssl_options.ciphers.1 = DHE-RSA-AES256-GCM-SHA384
ssl_options.ciphers.2 = DHE-RSA-AES128-GCM-SHA256
ssl_options.ciphers.3 = ECDHE-RSA-AES256-GCM-SHA384
ssl_options.ciphers.4 = ECDHE-RSA-AES128-GCM-SHA256

#ssl_options.honor_cipher_order = true
#ssl_options.honor_ecc_order    = true

hipe_compile = false

stomp.listeners.ssl.1 = 0.0.0.0:$RUCIO_MESSENGER_SERVICE_PORT_HTTPS

EOF
