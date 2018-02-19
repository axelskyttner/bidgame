#!/usr/bin/env python
import pika
from dqn_agent import q_agent
import numpy as np

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))

channel = connection.channel()
queuename = 'player-1-queue'
channel.queue_declare(queue=queuename)

agent = q_agent()
agent.train_model()

def fib(n):
    return agent.predict_next_move(np.array([np.zeros(12)]))

def on_request(ch, method, props, body):
    n = int(body)

    print(" [.] fib(%s)" % n)
    response = fib(n)
    
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                        props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue=queuename)

print(" [x] Awaiting RPC requests")
channel.start_consuming()
