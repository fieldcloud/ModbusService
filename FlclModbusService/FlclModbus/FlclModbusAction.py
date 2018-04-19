#!/usr/bin/env python


'''
   Python module containing class and methods to create and execute action
'''

from twisted.internet.defer import inlineCallbacks, returnValue

__version__='1.0.0'


class ActionMaker(object):


    def __init__(self, plc, action):
        self.plc=plc
        self.action=action
        self.current_step=0
        self.action_params={'current_step': self.current_step}


    @inlineCallbacks
    def execute(self):
        while self.current_step>=0:
            self.action_params = yield ActionStepper.make_step(self.plc,
                                               self.step, self.action_params)
            self.current_step=self.action_params.get('current_step')
        yield returnValue(self.current_step)


class ActionStepper(object):


    @staticmethod
    @inlineCallbacks
    def make_step(plc, step, params):
        next=-1
        try:
            params=ActionStepper.make_params_from_step(step, params)
            method_name=step.get('method')
            method = getattr(plc, method_name)
            res=method(step.get('params'))
            params=ActionStepper.clear_params(step, params)
        except Exception as e:
            print e.args
        yield returnValue(params)


    def make_params_from_step(step, params):
        step_params=step.get('params')
        for p in step_params:
            if p.get('value') is not None:
                params[p.get('key')]=p.get('value')
            else:
                var_key=params.get('var')
                resp=params.get('responses')
                if resp is not None:
                    var=resp.get('var_key')
                    if var is not None:
                        params[p.get('key')]=var.get('value')
        return params


    def clear_params(step, params):
        step_params=step.get('params')
        for p in step_params:
            if p.get('permanent') == False:
                del params[p.get('key')]
        return params


class ActionBuilder(object):


    @staticmethod
    def create_action_conf(self):
        action_conf={}
        return action_conf


    @staticmethod
    def create_and_add_step(self, action, id, method, params, expec, next):
        step={}
        action.get('steps').append(step)
        return step


