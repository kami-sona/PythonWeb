import datetime
import re
import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests

DictMonth = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
             "Sept": "09", "Oct": "10",
             "Nov": "11", "Dec": "12"}


# 创建字典，字符串转化


# 将网站的代码爬到本地
def downloaddata(data_url):
    url = urlopen(data_url)  # 打开页面
    soup = BeautifulSoup(url, "html.parser")  # 将爬取数据写入变量

    f = open("data.txt", "w", encoding="utf-8")
    f.write(str(soup))  # 将数据写入文件
    f.close()


# 将爬取的网页代码写入json文件
def get_json():
    f = open("data.txt", "r", encoding="utf-8")
    f_content = f.read()
    f.close()

    json_end = "}catch\(e\){}"

    json_start = "try { window.fetchRecentStatV2 = "  # 正则匹配

    regular_key = json_start + "(.*?)" + json_end

    re_content = re.search(regular_key, f_content, re.S)
    content1 = re_content.group()

    content1 = content1.replace(json_start, "")
    json_end = "}catch(e){}"
    content1 = content1.replace(json_end, "")

    json_end = "}catch\(e\){}"
    json_start = "try { window.getAreaStat = "
    regular_key = json_start + "(.*?)" + json_end
    re_content = re.search(regular_key, f_content, re.S)
    content2 = re_content.group()

    # 去除json字符串的前后关键词
    content2 = content2.replace(json_start, '')
    # 尾巴要去掉转义符号
    json_end = "}catch(e){}"
    content2 = content2.replace(json_end, '')

    return [content1, content2]


# 将数据更新到数据库
def insertinto_sql(conn, local_json_content1, local_json_content2, url):
    cur = conn.cursor()

    json_data = json.loads(local_json_content1)
    json_data2 = json.loads(local_json_content2)
    cur.execute("select max(Time) from `provincedata`")
    result = cur.fetchall()[0][0]
    time = get_time(url)

    if time > result:
        for i in json_data:
            city = i["provinceName"]
            try:
                count = i["yesterdayLocalConfirmedCount"]
            except KeyError:
                return

            sql = "insert into `covid-19`.`provincedata` values('%s',%d,null,null,null,null,'%s')" % (city, count, time)
            cur.execute(sql)
            conn.commit()

        for j in json_data2:
            city = j["provinceName"]
            currentConfirmedCount = j["currentConfirmedCount"]
            confirmedCount = j["confirmedCount"]
            deadCount = j["deadCount"]
            curedCount = j["curedCount"]
            sql = "update `ProvinceData` set `currentConfirmedCount` = %d where (`province` = '%s')" % (
                currentConfirmedCount, city)
            cur.execute(sql)
            conn.commit()
            sql = "update `ProvinceData` set `confirmedCount` = %d where (`province` = '%s')" % (confirmedCount, city)
            cur.execute(sql)
            conn.commit()
            sql = "update `ProvinceData` set `deadCount` = %d where (`province` = '%s')" % (deadCount, city)
            cur.execute(sql)
            conn.commit()
            sql = "update `ProvinceData` set `curedCount` = %d where (`province` = '%s')" % (curedCount, city)
            cur.execute(sql)
            conn.commit()

    cur.close()


# 获取网页最后的更新时间
def get_time(data_url):
    response = requests.get(data_url)
    json_data = response.headers
    str_date = json_data["Date"]
    ready_to_convert_str = "%s-%s-%s" % (str_date[12:16], DictMonth[str_date[8:11]], str_date[5:7])
    date = datetime.datetime.strptime(ready_to_convert_str, "%Y-%m-%d").date()
    return date
