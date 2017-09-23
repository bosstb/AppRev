# coding: utf-8
#遗留问题：IP会变：54.193.59.55


from datetime import datetime
from datetime import timedelta
import json
from flask import Flask,redirect
from flask import render_template
from flask_sockets import Sockets
import random
from views.todos import todos_view
from flask import request
import leancloud
import requests

leancloud.init("h3m2DYtw3OcFUL3XDYeswQTS-gzGzoHsz", "GXxGFssDeCzf8TYXDoFps6P0")


clickList = {}
clickListIsInit = False
app = Flask(__name__)
sockets = Sockets(app)
# 动态路由
app.register_blueprint(todos_view, url_prefix='/todos')


class TokenRecord(leancloud.Object):
    pass


@app.route('/', methods=["GET", "POST"])
def index():
    # 获取IP
    #print request.headers['x-real-ip']
    headers = request.headers
    ip = request.headers['x-real-ip']
    #ip =  request.access_route[-1]
    # if request.headers.getlist("X-Forwarded-For"):
    #     ip = request.headers.getlist("X-Forwarded-For")[0]
    # else:
    #     ip = request.remote_addr
    # if str(ip).find(',') > 0:
    #     ip = str(ip).split(',')[0]
    #UA格式化，取系统类型、版本，语言，平台，版本，手机型号作对比
    uas = request.user_agent
    ua = str(uas.__getattribute__('platform'))
    uas = str(uas).split(")", 1)
    sys_type = uas[0].split(";")
    for item in sys_type:
        if item.find("ndroid") > 0:
            ua = ua + item
            break
    ss = sys_type[-1].split('-')
    ua = ua + ss[-1]

    tokenRecord = TokenRecord()
    if request.method == "GET":
        # args = request.args
        # affiliate = args.get('type')
        #查询未取到数据的包名。
        query = leancloud.Query(TokenRecord)
        query.equal_to('devkey', None)
        query_list = query.find()
        package = query_list[0].get('package')
        return package
    else:
        args = request.args
        devkey = args.get('devkey')
        platform = args.get('platform')
        versionname = args.get('versionname')
        event = args.get('event')
        data = args.get('data')
        adver = args.get('adver')
        flykey = args.get('flykey')
        versioncode = args.get('versioncode')
        if devkey:
            tokenRecord.set('devkey', devkey)
            tokenRecord.set('platform', platform)
            tokenRecord.set('versionname', versionname)
            tokenRecord.set('event', event)
            tokenRecord.set('data', data)
            tokenRecord.set('adver', adver)
            tokenRecord.set('flykey', flykey)
            tokenRecord.set('versioncode', versioncode)
            tokenRecord.save()
            return "OK"
        else:
            return "Where is the token?"


@app.route('/time')
def time():
    return str(datetime.now())


@sockets.route('/echo')
def echo_socket(ws):
    while True:
        message = ws.receive()
        ws.send(message)


if __name__ == '__main__':
    app.run('0.0.0.0')

