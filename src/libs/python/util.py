#!/usr/bin/python3
from __future__ import print_function
import os
import sys
import time
import json
import traceback
from threading import Thread

def eprint(*args, **kwargs):
        print(*args, file=sys.stderr, flush=True, **kwargs)

def lprint():
    eprint(traceback.format_exc())

def get_env(env_vars):
    e_vars = {}
    for var in env_vars:
        if not os.environ.get(var):
            eprint(f"Please set ENVIRONMENT veriable {var!r}")
            sys.exit(-1)
        e_vars[var] = os.environ[var]
    return e_vars

def uniq_name(original_name):
    name = ""
    try:
        for c in original_name:
            if c >= 'a' and c<= 'z':
                name += c.upper()
            elif (c >= 'A' and c<= 'Z') or (c>='0' and c<='9'):
                name += c
            else:
                name += '_'
    except:
        lprint()
    return name

def make_daemon(func_name, func_args:str = ""):
    if func_args == "":
        t = Thread(target=func_name)
    else:
        t = Thread(target=func_name, args=[func_args])
    t.setDaemon(True)
    t.start()

def sys_run_loop_forever(cmd:str):
    def run_loop(cmd:str):
        while True:
            eprint("Run:" + cmd)
            os.system(cmd)
            time.sleep(3)
    make_daemon(run_loop, func_args=cmd)
