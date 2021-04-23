#!/usr/bin/python3
from __future__ import print_function
import os
import sys
import time
import json
import random
import string
import traceback
from threading import Thread


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, flush=True, **kwargs)

def error(msg):
    eprint(msg)

def warning(msg):
    eprint(msg)

def info(msg):
    eprint(msg)

def debug(msg):
    eprint(msg)

def trace():
    eprint(traceback.format_exc())

def get_env(env_vars):
    e_vars = {}
    for var in env_vars:
        if not os.environ.get(var):
            eprint(f"Please set ENVIRONMENT veriable {var!r}")
            sys.exit(-1)
        e_vars[var] = os.environ[var]
    return e_vars

def uniq_name(original_name, safe_char = '_', uper_case = True):
    name = ""
    for c in original_name:
        if (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or (c>='0' and c<='9'):
            name += c
        elif len(name) > 0 and name[-1] != safe_char:
            name += safe_char
    if len(name) == 0:
        name = ''.join(random.choice(string.ascii_lowercase) for _ in range(12))

    return name.upper() if uper_case else name.lower()

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
            info("Run:" + cmd)
            os.system(cmd)
            time.sleep(3)
    make_daemon(run_loop, func_args=cmd)


if __name__ == "__main__":
    print(uniq_name('345$%^4frseddgrte%^^54gsgt456435112@!@#$%'))
    print(uniq_name('یبربیسییبری    بریبریبر$%^4frseddgrte%^^54gsgt456435112@!@#$%'))
    print(uniq_name('DEFrrf tt rgtert$%^#%4 '))
    print(uniq_name('DEFrrf tt rgtert$%^#%4 ', '-'))
    print(uniq_name('DEFrrf tt rgtert$%^#%4 ', '-', False))
    print(uniq_name('DEFrrf tt rgtert$%^#%4 ', '-', True))
    print(uniq_name('        ', '-', True))
    print(uniq_name('$$$#$$#$$$  %%$%        ', '-', True))
    print(uniq_name('', '-', False))
