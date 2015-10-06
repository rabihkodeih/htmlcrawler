'''
Created on Apr 15, 2012

@author: Rabih Kodeih
'''

import os

def open_file_for_writing(file_name, binary=False):
    mode = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    if binary: mode = mode | os.O_BINARY
    return os.open(rectify_path(file_name), mode)
    
def close_file(file_handle):    
    os.close(file_handle)

def write_file(file_name, content, binary=False):
    mode = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    if binary: mode = mode | os.O_BINARY
    f = os.open(rectify_path(file_name), mode)
    if not binary: content = content.replace('\r', '')
    os.write(f, content)
    os.close(f)
    return os.path.realpath(file_name)

def read_file(file_name):
    f = open(rectify_path(file_name))
    res = f.read()
    f.close()
    return unicode(res)

def rectify_path(path):
    return os.path.join(os.path.dirname(__file__), path).replace(os.path.sep,'/')

def adjoin_paths(*paths):
    _paths = [(p[1:] if (p.startswith('/') or p.startswith('\\')) else p) for p in paths if p]
    return os.path.join(*_paths).replace(os.path.sep, '/')

def ensure_dir_exists(dir_path):    
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        
def append_before_ext(file_name, content):
    name, ext = os.path.splitext(file_name)
    return '%s%s%s' %  (name, content, ext)
    
def uniquify_file_name(path, suggested_file_name):
    unique_file_name = suggested_file_name
    counter = 0
    while os.path.exists(adjoin_paths(path, unique_file_name)): 
        unique_file_name = append_before_ext(suggested_file_name, '_%s' % counter)
        counter += 1
    return unique_file_name

def path_route(target_path, source_path):
    return os.path.relpath(target_path, source_path).replace(os.path.sep, '/')

def dangerous_purge_dir(d):
    try:
        if os.path.isdir(d):
            for k in os.listdir(d):
                dangerous_purge_dir(adjoin_paths(d, k))
            os.rmdir(d)
        else:
            os.remove(d)
    except: pass
    

