#!/usr/bin/env python


'''


'''

from FlclModbus.FlclModbusAction import ActionMaker
#from FlclModbus.FlclModbusPlc import PlcClient as plc
from FlclModbus.FlclModbusFactory import *
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor

import json

class FlclModbusGateway(object):

    plcs=[]
    plc_conf={}
    action_conf={}


    def __init__(self, plc_file_path, action_file_path):
        self.plc_file_path=plc_file_path
        self.action_file_path=action_file_path
        try:
            with open(self.plc_file_path, 'r') as conf:
                self.plc_conf=json.load(conf)
            with open(self.action_file_path, 'r') as conf:
                self.action_conf=json.load(conf)
            print self.plc_conf
            print self.action_conf
            for plc in self.plc_conf.get('plcs'):
                self.plcs.append(create_plc_client(plc))
        except Exception as e:
            print e.args


    @inlineCallbacks
    def execute_action(self, name, plc_id):
        plc = self._get_plc_by_id(plc_id)
        action = self._get_action_by_name(name)
        if plc is not None and action is not None:
            am = ActionMaker(plc, action)
            last = yield am.execute()


    def _get_plc_by_id(self, id):
        for plc in self.plcs:
            if plc.id==id:
                return plc
        return None


    def _get_action_by_name(self, name):
        for action in self.action_conf.get('actions'):
            if action.get('name')==name:
                return action
        return None


    def run(self):
        reactor.run()        
