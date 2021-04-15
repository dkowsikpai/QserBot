#!/usr/bin/env python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello')

data = {
    "idk": "dkowsikpai",
    "txt": "no"
}

channel.basic_publish(exchange='', routing_key='hello', body=json.dumps(data))
print(" [x] Sent 'Hello World!'")
connection.close()