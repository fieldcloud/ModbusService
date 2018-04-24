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
                                                     self._get_current_step(),
                                                     self.action_params)
            self.current_step=self.action_params.get('current_step')
        yield returnValue(self.current_step)


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
        next=-1
        try:
            params=ActionStepper.make_params_from_step(step, params)
            method_name=step.get('method')
            method = getattr(plc, method_name)
            res= yield method(step.get('params'))
            params=ActionStepper.load_result(step, params, res)
            params['current_step']=ActionStepper.make_condition(step, params)
        except Exception as e:
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
                for k1, v1 in v.iteritems():
                    params['vars'][k1] = v1
        return params


    @staticmethod
    def make_condition(step, params):
        condition = step.get('condition')
        var1=ActionStepper._make_var(condition.get('var1'), params)
        var1=ActionStepper._make_var(condition.get('var2'), params)
        to_eval='{} {} {}'.format(var1, condition.get('operator'), var1)
        res=eval(to_eval)
        if res == True:
            params['current_step'] = condition.get('success')
        else:
            params['current_step'] = condition.get('else')
        return params


    @staticmethod
    def _make_var(var_desc, params):
        var = None
        if var_desc.get('value') is not None:
            var = var_desc.get('value')
        else:
            vars=params.get('vars')
            for k, v in vars:
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


