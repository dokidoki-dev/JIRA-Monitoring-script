import time
import sys
import requests
import pymysql
import json


# 用户信息
msg = [
    {
        "name": "zhangsan",
        "phone": 1000000000
    },
]
admin_phone = 1800000000

jira_config = {
    "host": "127.0.0.1",
    "post": 3306,
    "user": "root",
    "passwd": '123456',
    "db": "jira",
    "login_jira_url": "http://jira.com/login.jsp",
    "get_bug_url": "http://jira.com/rest/issueNav/1/issueTable",
    "project": "xxx"
}

api_headers = {
    "jira_login_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/90.0.4430.212 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
    },
    "jira_getbug_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/90.0.4430.212 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Atlassian-Token": "no-check",
        "Origin": "http://jira.com",
    }
}
ding_api_url = '钉钉推送地址'


class SQLMysql(object):
    def __init__(self):
        self.conn = pymysql.connect(host=jira_config['host'],
                                    port=jira_config['post'],
                                    user=jira_config['user'],
                                    passwd=jira_config['passwd'],
                                    db=jira_config['db'])
        self.cur = self.conn.cursor()

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def query_one(self, sql, args=None):
        self.cur.execute(sql, args)
        return self.cur.fetchone()

    def create_one(self, sql, args=None):
        try:
            self.cur.execute(sql, args)
            self.conn.commit()
            return True
        except Exception:
            self.conn.rollback()
            ding_talk("数据创建错误，事务已回滚", admin_phone, 2)
            return False


def get_login():
    headers = api_headers['jira_login_headers']
    s = requests.Session()
    data = "os_username=用户名&os_password=密码&os_destination=&user_role=&atl_token=&login=%E7%99%BB%E5%BD%95"
    url = jira_config['login_jira_url']
    s.post(url, headers=headers, data=data)
    return s


def status(name):
    try:
        s = get_login()
    except Exception:
        ding_talk("JIRA接口数据读取错误~", admin_phone, 2)
        return
    headers = api_headers['jira_getbug_headers']
    jql = "startIndex=0&filterId=-2&jql=project = %s AND status in (Resolved) AND status changed DURING (" \
          "startOfWeek(-2), endOfWeek(0)) AND reporter = %s&layoutKey=split-view" % (jira_config['project'], name)
    url = jira_config['get_bug_url']
    r = s.post(url, headers=headers, data=jql)
    lists = r.json()
    bug_name = []
    bug_id = lists["issueTable"]["issueIds"]
    for i in range(len(bug_id)):
        bug_name.append(lists["issueTable"]["table"][i]["summary"])
    return {'bug_id': bug_id, 'bug_name': bug_name}


def ding_talk(name, phone, args=1):
    headers = {'Content-Type': 'application/json'}
    api_url = ding_api_url
    content = name + "----当前状态已变更为已解决，请关注！@%s" % phone
    if args == 2:
        content = name + " @%s" % phone
    json_text = {
        "at": {
            "atMobiles": [
                phone
            ],
            "isAtAll": False
        },
        "text": {
            "content": content
        },
        "msgtype": "text"
    }
    requests.post(api_url, data=json.dumps(json_text), headers=headers)


def controller(name, phone):
    try:
        dicts = status(name)
    except Exception:
        ding_talk("JIRA接口数据读取错误", admin_phone, 2)
        return
    bug_id = dicts['bug_id']
    bug_name = dicts['bug_name']
    try:
        db = SQLMysql()
    except Exception:
        ding_talk("数据库连接错误，请检查，程序自动关闭", admin_phone, 2)
        sys.exit(1)
    sql_query = 'select bugid from jira where bugid = %s'
    sql_create = 'insert into jira (bugid, bugname) value (%s, %s)'
    for i in range(len(bug_id)):
        result = db.query_one(sql_query, [(bug_id[i]), ])
        if result:
            continue
        else:
            rlt = db.create_one(sql_create, [(bug_id[i]), (bug_name[i]), ])
            if rlt:
                time.sleep(3)
                ding_talk(bug_name[i], phone)


if __name__ == '__main__':
    while True:
        time.sleep(600)
        for i in range(len(msg)):
            controller(msg[i]["name"], msg[i]["phone"])

