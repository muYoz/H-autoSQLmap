# -*- coding: gbk -*-
import time
from selenium import webdriver
from setting import *
import os
import sys
import re
import shutil
import encodings
reload(sys)
sys.setdefaultencoding('utf-8')

path = "cookiesed/"
path_list=os.listdir(path)
path_list.sort()
for root, dirs, files in os.walk(path):
    for name in files:
        if name.endswith(".txt"):
            file = root + "\\" + name
            print(file)


print u''+LOGIN_NAME+u'正在执行作业中......'

chrome_option = webdriver.ChromeOptions()
chrome_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chromedriver.exe"#需要下载这个组件

for name in path_list:
    try:
        driver = webdriver.Chrome(executable_path=chrome_path)
        driver.get(loginUrl)

        driver.find_element_by_id('username').send_keys(LOGIN_NAME)
        driver.find_element_by_id('password').send_keys(LOGIN_PASSWD)

        time.sleep(5)
        driver.find_element_by_id('submitBtn').click()
        time.sleep(5)

        driver.get(getUrl)
        time.sleep(5)
        driver.refresh()
        cookieJar = driver.get_cookies()

        cookieMap = {}

        #抓包看cookie有什么值
        for cell in cookieJar:
            if "SESSION_VALIDATE_KEY" in cell['name']:
                cookieMap["SESSION_VALIDATE_KEY"] = cell['value']
            if "Authorization" in cell['name']:
                cookieMap["Authorization"] = cell['value']
            if "TOKEN_COOKIE_NAME" in cell['name']:
                cookieMap["TOKEN_COOKIE_NAME"] = cell['value']
            if "SCB_SESSION_ID" in cell['name']:
                cookieMap["SCB_SESSION_ID"] = cell['value']
        cookieup = 'Cookie: SCB_SESSION_ID=%s; Authorization=%s; TOKEN_COOKIE_NAME=%s; SESSION_VALIDATE_KEY=%s\n\n' % (cookieMap['SCB_SESSION_ID'],cookieMap['Authorization'], cookieMap['TOKEN_COOKIE_NAME'], cookieMap['SESSION_VALIDATE_KEY'])

        driver.close()

        with open("cookiesed/%s" % name, "r") as f1, open("cookies/%s" % name, "w") as f2:
        #cookiesed文件目录是收动抓取需要跑的数据包，cookies是一个空的目录用于存放要跑的数据包
            lines = []
            for l in f1:
                if r'Cookie' not in l and r'cookie' not in l:
                    lines.append(l)
            f1.close()
            lines.insert(12, cookieup)#登录后替换cookie
            s = ''.join(lines)
            f2.writelines(s)
            f2.close()
            del lines[:]

        shutil.copy("cookies/%s" % name, 'logs/%s' % name)
        f = open('logs/%s' % name, 'a')
        f.write('\n\n')
        f.close()

        os.system(
            "python sqlmap/sqlmap.py -r cookies/%s --dbs --tamper=space2comment  --cookie=COOKIE --batch >> logs/%s" % (
            name, name))

        r = open('logs/%s' % name, 'r')
        log_info = r.readlines()
        r.close()
        for cell in log_info:
            if ('sqlmap resumed the following injection point(s) from stored session:' in cell) or (
                    'sqlmap identified the following injection point(s) with a total of' in cell):
                if os.path.exists('logs/error_%s' % name): os.remove('logs/error_%s' % name)
                #如果有注入参数就将日志前面加个error
                os.rename('logs/%s' % name, 'logs/error_%s' % name)
                break
    except Exception, e:
        continue
