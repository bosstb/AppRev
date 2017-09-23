# coding: utf-8

from leancloud import Engine
from leancloud import LeanEngineError
import leancloud

from app import app
import requests

engine = Engine(app)


class AndroidId(leancloud.Object):
    pass


@engine.define
def Hello(**params):
    print params
    return 'androidId missing'


@engine.before_save('Todo')
def before_todo_save(todo):
    content = todo.get('content')
    if not content:
        raise LeanEngineError('内容不能为空')
    if len(content) >= 240:
        todo.set('content', content[:240] + ' ...')
