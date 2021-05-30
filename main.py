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


class SQLMysql(object):
    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1',
                                    port=3306,
                                    user='root',
                                    passwd='123456',
                                    db='jira')
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
            ding_talk("数据创建错误，事务已回滚", 100000000000, 2)
            return False


def get_login():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/90.0.4430.212 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    s = requests.Session()
    data = "os_username=用户名&os_password=密码&os_destination=&user_role=&atl_token=&login=%E7%99%BB%E5%BD%95"
    url = 'http://jira.com/login.jsp'
    s.post(url, headers=headers, data=data)
    return s


def status(name):
    try:
        s = get_login()
    except Exception:
        ding_talk("JIRA接口数据读取错误~", 10000000000, 2)
        return
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/90.0.4430.212 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Atlassian-Token": "no-check",
        "Origin": "http://jira.com",
    }
    jql = "startIndex=0&filterId=-2&jql=project = 项目名称 AND status in (Resolved) AND status changed DURING (" \
          "startOfWeek(-2), endOfWeek(0)) AND reporter = %s&layoutKey=split-view" % name
    url = 'http://jira.com/rest/issueNav/1/issueTable'
    r = s.post(url, headers=headers, data=jql)
    lists = r.json()
    bug_name = []
    bug_id = lists["issueTable"]["issueIds"]
    for i in range(len(bug_id)):
        bug_name.append(lists["issueTable"]["table"][i]["summary"])
    return {'bug_id': bug_id, 'bug_name': bug_name}


def ding_talk(name, phone, args=1):
    headers = {'Content-Type': 'application/json'}
    api_url = "钉钉推送地址"
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
        ding_talk("JIRA接口数据读取错误", 100000000, 2)
        return
    bug_id = dicts['bug_id']
    bug_name = dicts['bug_name']
    try:
        db = SQLMysql()
    except Exception:
        ding_talk("数据库连接错误，请检查，程序自动关闭", 10000000000, 2)
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

