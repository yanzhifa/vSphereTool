#!/usr/bin/python
# -*- coding:utf-8 -*-
#author: lingyue.wkl
#desc: use to db ops
#---------------------
#2012-02-18 created
#---------------------

import sys,os
import ConfigParser

def test(config_file_path):
    cf = ConfigParser.ConfigParser()
    cf.read(config_file_path)

    s = cf.sections()
    print 'section:', s

    o = cf.options("baseconf")
    print 'options:', o
    
    #host_name = cf.options("host")
    #print host_name

    v = cf.items("baseconf")
    print 'db:', v

    db_host = cf.get("baseconf", "host")
    db_port = cf.getint("baseconf", "port")
    db_user = cf.get("baseconf", "user")
    db_pwd = cf.get("baseconf", "password")

    print db_host, db_port, db_user, db_pwd

    cf.set("baseconf", "db_pass", "123456")
    cf.write(open("config_file_path", "w"))

if __name__ == "__main__":
    test("./db_config.ini")
