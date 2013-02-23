#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:    tool_chain.py 
# Description:  integrate some tools
# Author:       OO4
# Version:      0.0.1   
#----------------------------------------------------------------------------

import argparse
import ConfigParser
import sys
import subprocess
import logging
import re

VAR = 'VAR'
VAR_CMD = r'\$\(\w*\)'
CMD_VAR = r'\$\(\w*\).*[^\r|^\n]'
VAR2CMD = r'$(%s)'

KEYS = {'LOG':('logfile',),
        'STEP':('step',)}

STEPS = ('STEP_%d','dec','cmd')

LOGFORMAT = '%(asctime)-15s %(levelname)s %(message)s' 

if __name__ == '__main__':
        
    #update var vaule to cmd 
    def updateVartoCmd(_varDic,_str):
        _varCmd = re.findall(VAR_CMD, _str)
        _varName = [_v.split('(')[1].split(')')[0].strip()for _v in _varCmd]
        if _varName:
            for _v in _varName:
                try:
                    _str = _str.replace(VAR2CMD%(_v),_varDic[_v])
                except KeyError, e:
                    print 'error: var is not be defined', e
                    logging.error(e)
        return _str
    
#    update var value from cmd's output
    def updateVarVaule(_varDic, _str):
        _vv = re.findall(CMD_VAR, _str)   
        if _vv > 0:
            for _vl in _vv:
                _a,_b =  _vl.strip().split('=')
                _vn = _a.split('(')[1].split(')')[0].strip()
                _vl = _b.strip()
                try:
                    _varDic[_vn] = _vl
                except KeyError, e:
                    print 'error: var is not be defined', e
                    logging.error(e)

    #parser comdline args
    parser = argparse.ArgumentParser(description='a tool for integrate tool chain')
    parser.add_argument('-f', type=argparse.FileType('r'), help='Read FILE as steps.')
    args = parser.parse_args()
    _f = vars(args)['f'] 
    
    if _f == None:
        print 'error: use -f step file'
        sys.exit()
    
    step = {}
    config = ConfigParser.ConfigParser()
    config.readfp(_f)
    
    #get logfile and step number 
    for _sec in KEYS:
        try:
            for _key in KEYS[_sec]:
                step[_sec] = config.get(_sec, _key).strip()
        except ConfigParser.Error , e:
            print 'error:in step file', e
            sys.exit()
    
    #logging
    try:
        logging.basicConfig(filename=step['LOG'], filemode='w', \
            format=LOGFORMAT, level=logging.DEBUG)
    except IOError, e:
        print 'error:', e
        sys.exit()
    
    var = {}
    #get vars
    try:
        for _c in config.items(VAR):
            var[_c[0]]=_c[1]
    except ConfigParser.Error , e:
        print 'error:in step file', e
        logging.error(e)
        sys.exit()
    
    #get steps
    for _i in range(int(step['STEP'])):
        try:
            step[_i] = [config.get(STEPS[0]%(_i), _key).strip() for _key in STEPS[1:]]
        except ConfigParser.Error , e:
            print 'error:in step file', e
            sys.exit()
    
    #execute cmd of steps
    for _i in range(int(step['STEP'])):
        _cmd = updateVartoCmd(var,step[_i][1])
        print 'excute step %d'%(_i),_cmd
        logging.debug('excute step %d: %s'%(_i, _cmd))
        #match and update var in cmd
        try:
            _out = subprocess.check_output(_cmd, shell=True)
            #update var vaule
            updateVarVaule(var,_out)
            logging.debug('result: %s'%(_out))
        except subprocess.CalledProcessError,e:
            print 'error: ', e
            logging.error(e)
