import json
import streamlit_echarts
import mysql.connector

from pyecharts.charts import Map
from pyecharts.charts import Line
from pyecharts import options as opts

conn = mysql.connector.connect(
    host="localhost",
    port="3306",
    user="root",
    passwd="zyc7412369850",
    db="covid-19",
    auth_plugin="mysql_native_password",
    buffered=True
)
province = []
NewValue = []
cur = conn.cursor()
# 该sql语句作用是统计各个省的7日总的确诊病例
sql = "select province,sum(NewCount) from provincedata group by province"
cur.execute(sql)
result = cur.fetchall()

for i in result:
    province.append(i[0])
    NewValue.append(i[1])

# 该sql语句作用是找出哪一个省份确诊最多
sql = "select max(New) from( select sum(NewCount) as New from provincedata group by province) as A"

cur.execute(sql)
result = cur.fetchall()

for i in result:
    MaxSize = i[0]

sequence = list(zip(province, NewValue))
# 通过读取json数据读取地图的坐标画出中国地图
with open("china.json", "r"，encoding="utf-8") as f:
    map = streamlit_echarts.Map("world", json.loads(f.read()), )
c = Map(init_opts=opts.InitOpts(bg_color="white"))
c.add(series_name="确诊病例", data_pair=sequence, maptype="world")

c.set_series_opts(label_opts=opts.LabelOpts(is_show=False))  # 是否展示每个地图板块的名字该处为false
c.set_global_opts(
    title_opts=opts.TitleOpts(title="中国新冠肺炎七日总览图"),
    visualmap_opts=opts.VisualMapOpts(max_=MaxSize),
)  # 设置地图的标题以及颜色分布图的最值

# 画出地图
streamlit_echarts.st_pyecharts(c, map=map, height="500px")

sql = "select Time,sum(NewCount) from provincedata group by Time"
cur.execute(sql)
result = cur.fetchall()
province.clear()
NewValue.clear()

for i in result:
    province.append(i[0])
    NewValue.append(i[1])

# 画出折线图
AllLine = (
    Line()
    .add_xaxis(province)
    .add_yaxis("现存确诊", NewValue)
    .set_global_opts(title_opts=opts.TitleOpts(title="7日内确诊折线图"))
)

streamlit_echarts.st_pyecharts(AllLine)
