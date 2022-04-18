import paho.mqtt.client as mqtt
import pymysql
import paho.mqtt.client as mqtt
import time
import random
import ast

db = pymysql.connect("localhost", "root", "jkwry4s45889", "BS",autocommit=True)
# 如遇报错，尝试改为：db = pymysql.connect(host="localhost", user="root", password="admin", database="BS",autocommit=True)
# 或设置自己的user和password
cursor = db.cursor()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code: " + str(rc))

def on_message(client, userdata, msg):
    print("Get a message:")
    # print(msg.topic + " " + str(msg.payload))
    message=ast.literal_eval(str(msg.payload)[2:-1])
    nowtime=message['timestamp']
    # nowtime=time.asctime(time.localtime(int(message['timestamp'])/1000))
    ifalert=message['alert']
    locx=message["lat"]
    locy=message["lng"]
    value=message['value']
    sql="select count(*) from device"
    print(sql)
    cursor.execute(sql)
    devicenum = cursor.fetchone()[0]
    if(devicenum==0):
        return
    deviceid=random.randint(0,devicenum-1)
    sql="select count(*) from historytable where deviceid = %s"%(deviceid)
    print(sql)
    cursor.execute(sql)
    cnt = cursor.fetchone()[0]
    # print(devicenum)
    sql = "INSERT INTO historytable(deviceid, time, locx, locy,id,value,ifoffline ) VALUES (%s, '%s',  %s,  %s,%s,%s,%s)" % \
          (deviceid, nowtime, locx, locy,cnt,value,ifalert)
    print(sql)
    cursor.execute(sql)
    sql="UPDATE device SET locx = '%s' WHERE id = %s"%(locx,deviceid)
    print(sql)
    cursor.execute(sql)
    sql = "UPDATE device SET locy = '%s' WHERE id = %s" % (locy, deviceid)
    print(sql)
    cursor.execute(sql)
    sql = "UPDATE device SET ifoffline = %s WHERE id = %s" % (ifalert, deviceid)
    print(sql)
    cursor.execute(sql)
    db.commit()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect('127.0.0.1', 1883, 600) # 600为keepalive的时间间隔
client.subscribe('testapp', qos=0)
client.loop_forever() # 保持连接