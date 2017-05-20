#!/usr/bin/env python
#-*- coding:utf-8 -*-

from gevent import monkey

monkey.patch_all()

from fastget import FastGet
from hehreq import HehReq
from massget import MassGet

__author__ = 'Beched (https://ahack.ru/)'
__license__ = 'Creative Commons Attribution Non-Commercial Share Alike'
