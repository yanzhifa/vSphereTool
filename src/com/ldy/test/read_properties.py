#!/usr/bin/python
# -*- coding:utf-8 -*-
#author: lingyue.wkl
#desc: use to db ops
#---------------------
#2012-02-18 created
#---------------------

#import sys,os
import ConfigParser

class FakeSecHead(object):
    def __init__(self, fp):
        self.fp = fp
        self.sechead = '[asection]\n'

    def readline(self):
        if self.sechead:
            try: 
                return self.sechead
            finally: 
                self.sechead = None
        else: 
            return self.fp.readline()

def test(config_file_path):
    
    cp = ConfigParser.SafeConfigParser()
    cp.readfp(FakeSecHead(open('./db_config.properties')))
    #print cp.items('asection')
    #print
    db_host = cp.get("asection", "host")
    db_port = cp.getint("asection", "port")
    db_user = cp.get("asection", "user")
    db_pwd = cp.get("asection", "password")

    print db_host, db_port, db_user, db_pwd

if __name__ == "__main__":
    test("./db_config.ini")
