import pac
import mysql.connector

if __name__ == '__main__':
    conn = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        passwd="zyc7412369850",
        db="covid-19",
        auth_plugin="mysql_native_password",
        buffered=True
    )
    url = "http://ncov.dxy.cn/ncovh5/view/pneumonia"
    pac.downloaddata(url)
    json_content = pac.get_json()

    pac.insertinto_sql(conn, json_content[0], json_content[1], url)
    conn.close()
