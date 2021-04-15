#!/usr/bin/env python
import pika, sys, os
import json

from obj_extract import ObjectiveExtractor
from ignite import IgniteData

def msq_exractor(data):
    objective = {
            "stage": 0,
            "new_service": False,
            "complaint": "",
            "desc": "",
            "addr": "",
            "mob": "",
            # "loc": "",
            # "lat": "",
            # "long": "",
            "landmark": "",
            "confirm": "",
            "completed": False
        }


    GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey",)
    END_GREETING_INPUTS = ("bye", "quit", "see you")

    PROD = [
        'E Bike',
        'E Trance +',
        'Gorilla Fan',
        'Gorilla Fan Pedestal Fan',
        'Gorilla Fan Wall Mounted',
        'Off Grid Solar Power Plant',
        'On Grid Solar System',
        'Super Fan A1',
        'Super Fan V1',
        'Super Fan X1',
        'On Grid',
        'Off Grid',
        'E Vehicles',
        'Energy Efficient & Renewable Energy Products',
        'Water Heater',
        'battery'
    ]

    ITEMS = PROD + ["New installation", "Buy x", "Cost of"]
    ITEMS = list(set(map(lambda x: x.lower(), ITEMS)))
    Ignite = IgniteData()
    try:
        temp = Ignite.getData(data["idk"])
        if temp.get("stage", 0) > 0:
            objective = temp
    except:
        pass

    print(objective)
    obj = ObjectiveExtractor(data["idk"], data["txt"], objective, ITEMS, GREETING_INPUTS, END_GREETING_INPUTS)
    obj.extract()
    print("Ignite:", Ignite.getData(data["idk"]))

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='hello')

    def callback(ch, method, properties, body):
        print(" [x] Received")
        data = json.loads(body)
        msq_exractor(data)
        

    channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)