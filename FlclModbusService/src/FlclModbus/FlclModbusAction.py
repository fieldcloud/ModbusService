#!/usr/bin/env python


'''
   Python module containing class and methods to create and execute action
'''

from twisted.internet.defer import inlineCallbacks, returnValue
from FlclModbus.util import sleep

__version__='1.0.0'


class ActionMaker(object):


    def __init__(self, plc, action):
        self.plc=plc
        self.action=action
        self.current_step=0
        self.action_params={'current_step': self.current_step}


    @inlineCallbacks
    def execute(self):
        try:
            while self.current_step>=0:
                step=self._get_current_step()
                print 'Executing action {}: '.format(step.get('method'))
                self.action_params = yield ActionStepper.make_step(self.plc,
                                                     step, self.action_params)
                self.current_step=self.action_params.get('current_step')
                print 'Next step: {}'.format(self.current_step)
        except Exception as e:
            print 'Error while execute'
            print e.args
            yield sleep(5.0)
        yield returnValue(self.action_params)


    def _get_step(self, steps, id):
        for k in steps:
            if k.get('id') == id:
                return k
        return None


    def _get_current_step(self):
        return self._get_step(self.action.get('steps'), self.current_step)


class ActionStepper(object):


    @staticmethod
    @inlineCallbacks
    def make_step(plc, step, params):
        try:
            print 'Start step: {}'.format(step.get('id'))
            params=ActionStepper.make_params_from_step(step, params)
            method_name=step.get('method')
            method = getattr(plc, method_name)
            res= yield method(params)
            params=ActionStepper.load_result(step, params, res)
            params=ActionStepper.make_condition(step, params)
        except Exception as e:
            print 'error making step'
            print e.args
        yield returnValue(params)


    @staticmethod
    def load_result(step, params, res):
        expected=step.get('result')
        for r in res:
            if r.get('name') is None:
                for e in expected:
                    has_name=r.get('name') is not None
                    if has_name == True and e.get('name') == r.get('name'):
                        params['vars'][e.get('name')]=r.get('value')
                    elif e.get('number') == r.get('number'):
                        params['vars'][e.get('name')]=r.get('value')
        return params


    @staticmethod
    def make_params_from_step(step, params):
        step_params=step.get('params')
        for k, v in step_params.iteritems():
            if k != 'vars':
                params[k] = v
            else:
                if params.get('vars') is None:
                    params['vars']={}
                for k1, v1 in v.iteritems():
                    params['vars'][k1] = v1
        return params


    @staticmethod
    def make_condition(step, params):
        condition = step.get('condition')
        var1=ActionStepper._make_var(condition.get('var1'), params)
        var2=ActionStepper._make_var(condition.get('var2'), params)
        to_eval='{} {} {}'.format(var1, condition.get('operator'), var2)
        res=eval(to_eval)
        if res == True:
            step=condition.get('success')
        else:
            step=condition.get('else')
        params['current_step'] = step
        return params


    @staticmethod
    def _make_var(var_desc, params):
        var = None
        if var_desc.get('val') is not None:
            var = var_desc.get('val')
        else:
            vars=params.get('vars')
            for k, v in vars.iteritems():
                if k==var_desc.get('name'):
                    var=v
        return var


class ActionBuilder(object):


    ''' Not functionnal yet!!!!! '''

    @staticmethod
    def create_action_conf(self):
        action_conf={}
        return action_conf


    @staticmethod
    def create_and_add_step(self, action, id, method, params, expec, next):
        step={}
        action.get('steps').append(step)
        return step


