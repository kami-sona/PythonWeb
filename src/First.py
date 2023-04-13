import pandas as pd
import streamlit as st
import mysql.connector
import streamlit_echarts
from pyecharts.charts import Bar

url = "http://ncov.dxy.cn/ncovh5/view/pneumonia"
conn = mysql.connector.connect(
    host="localhost",
    port="3306",
    user="root",
    passwd="zyc7412369850",
    db="covid-19",
    auth_plugin="mysql_native_password",
    buffered=True
)
# 创建所需的元组
provincelist = []
NewList = []
CurrentConfrimlist = []
TotalConfrimlist = []
DeadCount = []
CureCount = []
Time = []
GuangDonglist = []

cur = conn.cursor()
sql = "select * from `provincedata` where Time = '2022-11-21'"  # 获取最后的更新时间
cur.execute(sql)
result = cur.fetchall()

for i in result:
    provincelist.append(i[0])
    NewList.append(i[1])
    CurrentConfrimlist.append(i[2])
    TotalConfrimlist.append(i[3])
    DeadCount.append(i[4])
    CureCount.append(i[5])
    Time.append(i[6])

data = pd.DataFrame({
    "省份": provincelist,
    "本日新增": NewList,
    "现有确诊": CurrentConfrimlist,
    "累计确诊": TotalConfrimlist,
    "累计死亡": DeadCount,
    "累计治愈": CureCount,
    "最后统计时间": Time,
}
)
# 画出表格
st.write(data)

# 清空元组，变量复用
Time.clear()
NewList.clear()
sql = "select NewCount,Time from provincedata where province = '北京市'"
cur.execute(sql)
result = cur.fetchall()

for i in result:
    Time.append(i[1])
    NewList.append(i[0])

# 创建树状图添加北京市
bar = Bar()
bar.add_xaxis(Time)
bar.add_yaxis("北京市新增病例", NewList)

sql = "select NewCount from provincedata where province = '广东省'"
cur.execute(sql)
result = cur.fetchall()

for i in result:
    GuangDonglist.append(i[0])

# 创建树状图添加广东省
bar.add_xaxis(Time)
bar.add_yaxis("广东省新增病例", GuangDonglist)

# 画出树状图
streamlit_echarts.st_pyecharts(bar)
cur.close()
conn.close()
