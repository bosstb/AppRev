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
import base64


leancloud.init("F0zcG7tAkkjRJgbpMMIasYvy-MdYXbMMI", "gtrh1RJ5W1UNHejuS9V71pJy")


app = Flask(__name__)
sockets = Sockets(app)
# 动态路由
app.register_blueprint(todos_view, url_prefix='/todos')


class token_record(leancloud.Object):
    pass

class Logdata(leancloud.Object):
    pass

class Token_CR(leancloud.Object):
    pass

@app.route('/', methods=["GET", "POST"])
def index():
    # tokenRecord = TokenRecord()
    if request.method == "GET":
        # args = request.args
        # affiliate = args.get('type')
        #查询未取到数据的包名。
        query = leancloud.Query(token_record)
        query.equal_to('geted_token', 0)
        query_list = query.find()
        package = []
        for i in range(0, 10):
            if query_list[i]:
                package.append(query_list[i].get('package'))
        return json.dumps(package)
    else:
        print request.content_type
        print request.form

        if request.content_type == "application/json":
            args = json.loads(request.get_data())
        else:
            args = request.form
        devkey = args.get('devkey')
        platform = args.get('platform')
        versionname = args.get('versionname')
        event = args.get('event')
        data = args.get('data')
        adver = args.get('adver')
        flykey = args.get('flykey')
        versioncode = args.get('versioncode')
        key = args.get("package")
        if key:
            query = leancloud.Query(token_record)
            query.equal_to('package', key)
            query_list = query.find()
            tokenRecord = None
            if query_list:
                objId = query_list[0].get("objectId")
                Todo = leancloud.Object.extend('token_record')
                tokenRecord = Todo.create_without_data(objId)
            else:
                tokenRecord = token_record()
                tokenRecord.set('package', key)

            # 这里修改 location 的值
            tokenRecord.set('devkey', devkey)
            tokenRecord.set('platform', platform)
            tokenRecord.set('versionname', versionname)
            tokenRecord.set('event', event)
            tokenRecord.set('data', data)
            tokenRecord.set('adver', adver)
            tokenRecord.set('flykey', flykey)
            tokenRecord.set('versioncode', versioncode)
            tokenRecord.set('geted_token', 1)
            tokenRecord.set('code', 200)
            tokenRecord.save()
            return "data save success"
        else:
            return "Missing package!"


def getCountry(ip):
    r = requests.post(
        'http://api.db-ip.com/v2/c6f4413393e0ce3d120471ad41f7d7ad5bf77df0/' + str(ip))
    country = json.loads(r.text)
    if r.text.find('error') == -1:
        if country["countryCode"] != 'ZZ':
            countryName = country["countryName"]
        else:
            countryName = 'Unkown'
    else:
        countryName = 'Unkown'
    return  countryName


def logdata(apkg_country_result):
    if apkg_country_result:
        query = leancloud.Query(Logdata)
        query.equal_to('apkg_country_result', apkg_country_result)
        query_list = query.find()
        tokenRecord = None
        if query_list:
            objId = query_list[0].get("objectId")
            Todo = leancloud.Object.extend('Logdata')
            logdata = Todo.create_without_data(objId)
            logdata.set('count', query_list[0].get("count")+1)
            logdata.save()
        else:
            logdata = Logdata()
            logdata.set('apkg_country_result', apkg_country_result)
            logdata.set('count', 1)
            logdata.save()


@app.route('/gettk', methods=["GET", "POST"])
def time():
    if request.method == "POST":
        ip = None
        try:
            ip = request.headers['x-real-ip']
        except:
            print 1
        # 取国家
        if ip:
            countryName = getCountry(ip)
        else:
            countryName = "Unkown"

        if request.content_type == "application/json":
            args = json.loads(request.get_data())
        else:
            args = request.form
        apkg = args.get('apkg')
        ppkg = args.get('ppkg')
        ai = args.get('ai')
        version = args.get('v')
        query = leancloud.Query(token_record)
        query.equal_to('package', apkg)
        query_list_apkg = query.find()
        if query_list_apkg:
            if query_list_apkg[0].get("devkey"):
                query = leancloud.Query(Token_CR)
                query.equal_to('package', ppkg)
                query_list = query.find()
                if query_list:
                    per = int(query_list[0].get("CR"))
                    ran = random.randint(1, 100)
                    ran = float(ran)
                    print str(per) + "|" + str(ran)
                    if ran <= per:
                        data = {
                            "devkey": query_list_apkg[0].get("devkey"),
                            "platform": query_list_apkg[0].get("platform"),
                            "versionname": query_list_apkg[0].get("versionname"),
                            "event": query_list_apkg[0].get("event"),
                            "data": query_list_apkg[0].get("data"),
                            "adver": query_list_apkg[0].get("adver"),
                            "versioncode": query_list_apkg[0].get("versioncode"),
                            "afver": query_list_apkg[0].get("afver"),
                            "flykey": "",
                            "msg": "",
                            "pkg": apkg,
                            "code": 200
                        }
                        logdata(apkg + "_" + countryName + "_" + "ok")
                        return json.dumps(data)
                    else:
                        data = {"data": "", "code": 400, "msg": "Prob"}
                        logdata(apkg + "_" + countryName + "_" + "Prob")
                        return json.dumps(data)
                else:
                    per = 30
                    ran = random.randint(1, 100)
                    ran = float(ran)
                    if ran <= per:
                        data = {
                            "devkey": query_list_apkg[0].get("devkey"),
                            "platform": query_list_apkg[0].get("platform"),
                            "versionname": query_list_apkg[0].get("versionname"),
                            "event": query_list_apkg[0].get("event"),
                            "data": query_list_apkg[0].get("data"),
                            "adver": query_list_apkg[0].get("adver"),
                            "versioncode": query_list_apkg[0].get("versioncode"),
                            "afver": query_list_apkg[0].get("afver"),
                            "flykey": "",
                            "msg": "",
                            "pkg": apkg,
                            "code": 200
                        }
                        logdata(apkg + "_" + countryName + "_" + "ok")
                        return json.dumps(data)
                    else:
                        logdata(apkg + "_" + countryName + "_" + "Prob")
                        data = {"data": "", "code": 400, "msg": "Prob"}
                        return json.dumps(data)
            else:
                data = {"data":"", "code": 400, "msg": "No token"}
                logdata(apkg + "_" + countryName + "_" + "No token")
                return json.dumps(data)
        else:
            data = {"data": "", "code": 400, "msg": "No token"}
            logdata(apkg + "_" + countryName + "_" + "No pkg")
            return json.dumps(data)
    else:
        return "fuck you!"



def desEncode():
    a =1



@app.route('/funny', methods=["GET", "POST"])
def funny():
    if request.method == "POST":
        ip = None
        try:
            ip = request.headers['x-real-ip']
        except:
            print 1
        # 取国家
        if ip:
            countryName = getCountry(ip)
        else:
            countryName = "Unkown"

        if request.content_type == "application/json":
            args = json.loads(request.get_data())
        else:
            args = request.form
        apkg = args.get('apkg')
        ppkg = args.get('ppkg')
        ai = args.get('ai')
        version = args.get('v')
        query = leancloud.Query(token_record)
        query.equal_to('package', apkg)
        query_list_apkg = query.find()
        if query_list_apkg:
            if query_list_apkg[0].get("devkey"):
                query = leancloud.Query(Token_CR)
                query.equal_to('package', ppkg)
                query_list = query.find()
                if query_list:
                    per = int(query_list[0].get("CR"))
                    ran = random.randint(1, 100)
                    ran = float(ran)
                    print str(per) + "|" + str(ran)
                    if ran <= per:
                        data = {
                            "devkey": query_list_apkg[0].get("devkey"),
                            "platform": query_list_apkg[0].get("platform"),
                            "versionname": query_list_apkg[0].get("versionname"),
                            "event": query_list_apkg[0].get("event"),
                            "data": query_list_apkg[0].get("data"),
                            "adver": query_list_apkg[0].get("adver"),
                            "versioncode": query_list_apkg[0].get("versioncode"),
                            "afver": query_list_apkg[0].get("afver"),
                            "flykey": "",
                            "msg": "",
                            "pkg": apkg,
                            "code": 200
                        }
                        logdata(apkg + "_" + countryName + "_" + "ok")
                        return base64.b64encode(str(data))
                    else:
                        data = {"data": "", "code": 400, "msg": "Prob"}
                        logdata(apkg + "_" + countryName + "_" + "Prob")
                        return base64.b64encode(str(data))
                else:
                    per = 30
                    ran = random.randint(1, 100)
                    ran = float(ran)
                    if ran <= per:
                        data = {
                            "devkey": query_list_apkg[0].get("devkey"),
                            "platform": query_list_apkg[0].get("platform"),
                            "versionname": query_list_apkg[0].get("versionname"),
                            "event": query_list_apkg[0].get("event"),
                            "data": query_list_apkg[0].get("data"),
                            "adver": query_list_apkg[0].get("adver"),
                            "versioncode": query_list_apkg[0].get("versioncode"),
                            "afver": query_list_apkg[0].get("afver"),
                            "flykey": "",
                            "msg": "",
                            "pkg": apkg,
                            "code": 200
                        }
                        logdata(apkg + "_" + countryName + "_" + "ok")
                        return base64.b64encode(str(data))
                    else:
                        logdata(apkg + "_" + countryName + "_" + "Prob")
                        data = {"data": "", "code": 400, "msg": "Prob"}
                        return base64.b64encode(str(data))
            else:
                data = {"data":"", "code": 400, "msg": "No token"}
                logdata(apkg + "_" + countryName + "_" + "No token")
                return base64.b64encode(str(data))
        else:
            data = {"data": "", "code": 400, "msg": "No token"}
            logdata(apkg + "_" + countryName + "_" + "No pkg")
            return base64.b64encode(str(data))
    else:
        return "fuck you!"


@sockets.route('/echo')
def echo_socket(ws):
    while True:
        message = ws.receive()
        ws.send(message)



def getlogdata():
    a = 1
    while True:
        cql = " select * from Logdata limit " + str(a) + ",100"
        todo_query = leancloud.Query.do_cloud_query(cql, 1, 4)
        todo_list = todo_query.results
        b = 0
        for item in todo_list:
            print item.attributes.get("apkg_country_result") + "," + str(item.attributes.get("count"))
            b += 1
        a += 100
        if b <99:
            break



if __name__ == '__main__':
    #getlogdata()
    app.run('0.0.0.0')

