#!/usr/bin/env python

from twisted.internet.defer import Deferred

def sleep(delay, reactor=None):
    """
    Inline sleep for use in co-routines (Twisted ``inlineCallback`` decorated functions).
    .. seealso::
       * `twisted.internet.defer.inlineCallbacks <http://twistedmatrix.com/documents/current/api/twisted.internet.defer.html#inlineCallbacks>`__
       * `twisted.internet.interfaces.IReactorTime <http://twistedmatrix.com/documents/current/api/twisted.internet.interfaces.IReactorTime.html>`__
    :param delay: Time to sleep in seconds.
    :type delay: float
    :param reactor: The Twisted reactor to use.
    :type reactor: None or provider of ``IReactorTime``.
    """
    if not reactor:
        from twisted.internet import reactor
    d = Deferred()
    reactor.callLater(delay, d.callback, None)
    return d


