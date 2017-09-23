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

#leancloud.init("96Q4GMOz0VpK4JwfeUjEHNWC-MdYXbMMI", "aCAfwt702pPeubx6tnngUWiu")


clickList = {}
clickListIsInit = False
app = Flask(__name__)
sockets = Sockets(app)
# 动态路由
app.register_blueprint(todos_view, url_prefix='/todos')


class AndroidId(leancloud.Object):
    pass


class AndroidIdRepeat(leancloud.Object):
    pass


class PostTest(leancloud.Object):
    pass


class CloudControl(leancloud.Object):
    pass


class ClickRecord(leancloud.Object):
    pass


class AffiliateSetting(leancloud.Object):
    pass


@app.route('/', methods=["GET", "POST"])
def index():
    #首次请求初始化ClickList
    if clickListIsInit == False:
        clickListInit()
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


    clickRecord = ClickRecord()
    if request.method == "GET":
        args = request.args
        affiliate = args.get('af')
        #根据渠道名称获取渠道信息，该渠道名称应以 af 参数配置到下载链接给渠道。
        query = leancloud.Query(AffiliateSetting)
        query.equal_to('name', affiliate)
        query_list = query.find()
        jumpLink = query_list[0].get('jumpLink')
        postLink = query_list[0].get('postLink')
        paras = str(query_list[0].get('parameters')).split(',')

        offer_id = args.get("offer_id")
        affiliate_id = args.get("affiliate_id")
        transaction_id = args.get("transaction_id")
        sub_id = args.get("sub_id")
        clickInfo = {"offer_id": offer_id, "affiliate_id": affiliate_id, "transaction_id": transaction_id,
                     "sub_id": sub_id, "time": datetime.today(), 'af': affiliate, 'postLink': postLink, 'paras': paras}
        clickList[str(ip) + '|' + ua] = clickInfo
        clickRecord.set('ipua', str(ip) + '|' + ua)
        clickRecord.set('clickInfo', clickInfo)
        clickRecord.set('time', datetime.today())
        clickRecord.save()
        print clickList
        return redirect(jumpLink, code=302)
    else:
        androidIdRepeat = AndroidIdRepeat()
        androidId = AndroidId()
        #print headers.get('X-Forwarded-For')
        key = headers.get('Key')
        if key == '123321123':
            #关联ClickInfo
            clickInfo = None
            if clickList.has_key(str(ip) + '|' + ua):
                clickInfo = clickList[str(ip) + '|' + ua]
            # 获取提交的表单
            if request.content_type == "text/plain;charset=UTF-8":
                args = json.loads(request.get_data())
            else:
                args = request.form
            user_androidId = args.get('ai')
            aa =  args.get('aa')
            mo = args.get('mo')
            nt = args.get('nt')
            oc = args.get('oc')
            vn = args.get('vn')
            lang = args.get('vn')
            an = args.get('an')
            on = args.get('on')
            pkg = args.get('pkg')
            me = args.get('me')
            ms = args.get('ms')

            if user_androidId != None:
                print user_androidId
                query = leancloud.Query(AndroidId)
                query.equal_to('ai', user_androidId)
                query_list = query.find()
                # 取国家
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
                if len(query_list) == 0:
                    #判断安卓Id是否存在
                    androidId.set('ai', user_androidId)
                    androidId.set('aa', aa)
                    androidId.set('mo', mo)
                    androidId.set('nt', nt)
                    androidId.set('oc', oc)
                    androidId.set('vn', vn)
                    androidId.set('lang', lang)
                    androidId.set('an', an)
                    androidId.set('IP', ip)
                    androidId.set('ua', ua)
                    androidId.set('on', on)
                    androidId.set('pkg', pkg)
                    androidId.set('me', me)
                    androidId.set('ms', ms)
                    androidId.set('cn', countryName)
                    androidId.set('clickInfo', clickInfo)
                    androidId.save()

                    #获取扣量比例
                    query = leancloud.Query(CloudControl)
                    query.equal_to('versionName', '1.0.0')
                    query_list = query.find()
                    percentage = query_list[0].get('Percentage')
                    ran = random.randint(1, 100)
                    ran = float(ran)
                    print str(percentage) + '||' + str(ran)
                    #按比例扣量
                    #and countryName != 'China'
                    if ran > percentage and clickInfo != None and uas[1] == ' AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30':
                        #从ClickInfo解析渠道信息
                        postLink = str(clickInfo['postLink'])
                        paras = clickInfo['paras']
                        #post
                        postPara = ''
                        for para in paras:
                            if para == 'offer_id':
                                postPara = postPara + '&offer_id=' + str(clickInfo['offer_id'])
                            elif para == 'affiliate_id':
                                postPara = postPara + '&affiliate_id=' + str(clickInfo['affiliate_id'])
                            elif para == 'transaction_id':
                                postPara = postPara + '&transaction_id=' + str(clickInfo['transaction_id'])
                            elif para == 'click_id':
                                postPara = postPara + '&click_id=' + str(clickInfo['transaction_id'])
                            elif para == 'cid':
                                postPara = postPara + '&click_id=' + str(clickInfo['transaction_id'])
                            elif para == 'sub_id':
                                postPara = postPara + '&sub_id=' + str(clickInfo['sub_id'])
                            elif para == 'ip':
                                postPara = postPara + '&ip=' + str(ip)
                            elif para == 'country':
                                postPara = postPara + '&country=' + countryName
                            elif para == 'install_time':
                                postPara = postPara + '&install_time=' + str(datetime.today())
                        url = postLink + '?' + postPara[-(len(postPara)-1):]
                        print 'url:' + url
                        r = requests.post(url)
                        print 'Post Result:' + r.text
                        del clickList[str(ip) + '|' + ua]
                        #Post Test
                        postTest = PostTest()
                        postTest.set('country', countryName)
                        postTest.set('ip', ip)
                        postTest.set('installTime', datetime.today())
                        postTest.set('postPara', postPara)
                        postTest.save()
                        return '数据添加成功，已Post'
                    else:
                        return '数据添加成功，不Post'
                else:
                    androidIdRepeat.set('ai', user_androidId)
                    androidIdRepeat.set('aa', aa)
                    androidIdRepeat.set('mo', mo)
                    androidIdRepeat.set('nt', nt)
                    androidIdRepeat.set('oc', oc)
                    androidIdRepeat.set('vn', vn)
                    androidIdRepeat.set('lang', lang)
                    androidIdRepeat.set('an', an)
                    androidIdRepeat.set('IP', ip)
                    androidIdRepeat.set('ua', ua)
                    androidIdRepeat.set('on', on)
                    androidIdRepeat.set('pkg', pkg)
                    androidIdRepeat.set('me', me)
                    androidIdRepeat.set('ms', ms)
                    androidIdRepeat.set('clickInfo', clickInfo)
                    androidIdRepeat.set('cn', countryName)
                    androidIdRepeat.save()
                    return '安卓Id已存在，已添加至androidIdRepeat表'
            else:
                androidIdRepeat.set('ai', 'missing androidId')
                androidIdRepeat.save()
                return 'androidId missing'
        else:
            return "服务器错误"

def clickListInit():
    query = leancloud.Query(ClickRecord)
    query.greater_than('time', datetime.today()-timedelta(seconds=3600))
    query_list = query.find()
    for item in query_list:
        clickList[item.get('ipua')] = dict(item.get('clickInfo'))
    clickListIsInit = True


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

