#!/usr/bin/env python
from rpc_javascript_client import JavascriptRpcClient
import pika
import uuid
import json
import pprint
import numpy
#init

class Player():
    def __init__(self, name, queue_name):
        self.javascript_rpc = JavascriptRpcClient(queue_name, 'localhost')
        self.name = name

    def action(self, state):
        color = state['color']
        bid = state['current_bid']
        transaction_list = state['transaction_list']
        json_info = json.dumps({'color':color, 'bid':bid, 'transaction-list':[]})
        bidvalue = self.javascript_rpc.call(json_info)
        
        return bidvalue
   




