'''
Created on Nov 7, 2011

@author: Rabih Kodeih
'''
import os
import sys
import time
import traceback
import datetime
from functools import wraps


def write_exception_to_log_file(log_file_path):
    if not os.path.exists(log_file_path):
        open(log_file_path, 'w')
    log = open(log_file_path, 'a')
    print >> log, "Exception occurred at date-time: %s" % datetime.datetime.now().strftime('%Y-%m-%d @ %H:%M:%S')
    print >> log, '-'*60
    traceback.print_exc(file=log)
    print >> log, '-'*60
    log.close()
    print >> sys.stderr, "Exception caught, please check log file: %s" % os.path.realpath(log_file_path)
    return None

def testCase(func):
    @wraps(func)
    def inner_closure(*args, **kwargs):
        ret = func(*args, **kwargs)
        print 'test OK for : %s' % func.__name__
        return ret
    return inner_closure

def log_exceptions(log_file_path):
    def inner_log_exceptions(func):
        '''
        Decorator for logging exceptions
        '''
        def inner_closure(*args, **kws):
            try:
                return func(*args, **kws)
            except BaseException:
                write_exception_to_log_file(log_file_path)
                return None
        return inner_closure
    return inner_log_exceptions

def measureExecutionTime(func):
    '''
    Decorator for timing function execution
    '''
    @wraps(func)
    def inner_closure(*args, **kw):
        t1 = time.time()
        result = func(*args, **kw)
        t2 = time.time()
        print 'elapsed time (secs) : %s' % (t2 - t1)
        return result
    return inner_closure

def confirmUserAction(func):
    '''
    Decorator for confirming user action from the console
    '''
    @wraps(func)
    def innerClosure(*args, **kw):
        if kw.has_key('__confirm'):
            del(kw['__confirm'])
            func(*args, **kw)
            return
        print 'Please confirm by entering (yes):'
        choice = raw_input('>> ')
        if choice.lower() != 'yes': 
            print 'Command canceled'
            return
        func(*args, **kw)
        print 'Command completed successfully'
    return innerClosure

def ignoreExceptions(func):
    '''
    Decorator for ignoring exceptions.
    '''
    @wraps(func)
    def innerClosure(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            return None
    return innerClosure



