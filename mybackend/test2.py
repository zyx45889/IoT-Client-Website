from flask import request, Flask, jsonify
import ast
import pymysql
import paho.mqtt.client as mqtt
import time
import random
# login ————————
# correct:0
# error: 1 - 密码错误
#        2 - 用户名不存在
#        3 - 邮箱不存在

# register ————————
# correct:0
# error: 1 - 密码不规范
#        2 - 用户名不规范
#        3 - 邮箱不规范
#        4 - 用户名重复
#        5 - 邮箱重复

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
db = pymysql.connect("localhost", "root", "jkwry4s45889", "BS",autocommit=True)
cursor = db.cursor()
# sql = """INSERT INTO user(username,
#          password, userid, email)
#          VALUES ('zyx', 'jkwry4s', 0, '3180105144@zju.edu.cn')"""
# try:
#     # 执行sql语句
#     cursor.execute(sql)
#     # 提交到数据库执行
#     db.commit()
# except:
#     # 如果发生错误则回滚
#     print("aa")
#     db.rollback()


@app.route('/login/', methods=['POST'],endpoint="login")
def post_Data():
    print('get a POST')
    dict=str(request.data)
    dict=dict[2:-1]
    dict=ast.literal_eval(dict)
    name = dict['name']
    age=dict['password']
    mailbox=dict['mailbox']
    if(mailbox==''):
        sql = "select password from user where username='%s'" % (name)
        print(sql)
        cursor.execute(sql)
        temp=cursor.fetchone()
        if(temp==None):
            recognize_info = {'ret': 2}
            return jsonify(recognize_info), 201
        _password = temp[0]
        if(age !=_password):
            recognize_info = {'ret': 1,}
            return jsonify(recognize_info), 201
        sql = "select email from user where username='%s'" % (name)
        print(sql)
        cursor.execute(sql)
        temp = cursor.fetchone()
        recognize_info = {'ret': 0,'mailbox':temp[0]}


    else:
        sql = "select password from user where email='%s'" % (mailbox)
        print(sql)
        cursor.execute(sql)
        temp = cursor.fetchone()
        if (temp== None):
            recognize_info = {'ret': 3}
            return jsonify(recognize_info), 201
        _password = temp[0]
        if (age != _password):
            recognize_info = {'ret': 1}
            return jsonify(recognize_info), 201
        sql = "select username from user where email='%s'" % (mailbox)
        print(sql)
        cursor.execute(sql)
        temp = cursor.fetchone()
        recognize_info = {'ret': 0, 'username': temp[0]}
    return jsonify(recognize_info), 201

@app.route('/register/', methods=['POST'],endpoint="register")
def post_Data():
    print('get a POST')
    dict=str(request.data)
    dict=dict[2:-1]
    dict=ast.literal_eval(dict)
    name = dict['name']
    age=dict['password']
    mailbox=dict['mailbox']
    print(name,age,mailbox)

    # 检查密码规范
    if(len(age)<6):
        recognize_info = {'ret': 1}
        return jsonify(recognize_info), 201

    # 检查用户名规范
    if (len(name) < 6):
        recognize_info = {'ret': 2}
        return jsonify(recognize_info), 201

    # 检查邮箱规范
    if ('@' not in mailbox):
        recognize_info = {'ret': 3}
        return jsonify(recognize_info), 201

    # 检查name重复
    sql="select count(*) from user where username='%s'"%(name)
    print(sql)
    cursor.execute(sql)
    cnt = cursor.fetchone()[0]
    if(cnt!=0):
        recognize_info = {'ret': 4}
        return jsonify(recognize_info), 201

    # 检查邮箱重复
    sql = "select count(*) from user where email='%s'" % (mailbox)
    print(sql)
    cursor.execute(sql)
    cnt = cursor.fetchone()[0]
    if (cnt != 0):
        recognize_info = {'ret': 5}
        return jsonify(recognize_info), 201

    # insert
    sql="select count(*) from user"
    cursor.execute(sql)
    cntid = cursor.fetchone()[0]
    sql = "INSERT INTO user(username, \
           password, email, userid) \
           VALUES ('%s', '%s',  '%s',  '%s')" % \
          (name, age, mailbox,cntid )
    print(sql)
    flag=0
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        flag=1
    except:
        # 如果发生错误则回滚
        print("wrong!")
        db.rollback()
    if(flag==1):
        recognize_info = {'ret': 0}
    else:
        recognize_info = {'ret': -1}
    return jsonify(recognize_info), 201

# 0:成功
# 1:失败
@app.route('/adddevice/', methods=['POST'],endpoint="adddevice")
def post_Data():
    print('get a POST adddevice')
    dict=str(request.data)
    dict=dict[2:-1]
    dict=ast.literal_eval(dict)
    username=dict["username"]
    devicename=dict["devicename"]
    try:
        sql="select userid from user where username = '%s'"% (username)
        print(sql)
        cursor.execute(sql)
        userid = cursor.fetchone()[0]
        sql = "select count(*) from device"
        print(sql)
        cursor.execute(sql)
        devicenum = cursor.fetchone()[0]
        sql="insert into device(name,locx,locy,id,ifoffline) values ('%s',%s,%s,%s,%s)"%(devicename,0,0,devicenum,True)
        print(sql)
        cursor.execute(sql)
        sql="insert into devicetable(userid,deviceid) values (%s,%s)"%(userid,devicenum)
        print(sql)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        recognize_info = {'ret': 1}
        return jsonify(recognize_info), 201
    recognize_info = {'ret': 0}
    return jsonify(recognize_info), 201

@app.route('/getdevice/', methods=['POST'],endpoint="getdevice")
def post_Data():
    print('get a POST getdevice')
    dict=str(request.data)
    dict=dict[2:-1]
    dict=ast.literal_eval(dict)
    username=dict["username"]
    devicenames=[]
    try:
        sql="select userid from user where username = '%s'"% (username)
        print(sql)
        cursor.execute(sql)
        userid = cursor.fetchone()[0]
        sql = "select deviceid from devicetable where userid = %s" % (userid)
        print(sql)
        cursor.execute(sql)
        temp=cursor.fetchall()
        for xx in temp:
            t=xx[0]
            sql = "select name from device where id = %s" % (t)
            print(sql)
            cursor.execute(sql)
            temp=cursor.fetchone()
            print(temp)
            devicenames.append(temp[0])
    except:
        db.rollback()
        recognize_info = {'ret': 1}
        return jsonify(recognize_info), 201
    recognize_info = {'ret': 0,'devicenames':devicenames}
    return jsonify(recognize_info), 201

@app.route('/changedevice/', methods=['POST'],endpoint="changedevice")
def post_Data():
    print('get a POST changedevice')
    dict=str(request.data)
    dict=dict[2:-1]
    dict=ast.literal_eval(dict)
    devicename=dict["devicename_before"]
    newname=dict['devicename_after']
    try:
        sql = "UPDATE device SET name = '%s' WHERE name = '%s'" % (newname, devicename)
        print(sql)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        recognize_info = {'ret': 1}
        return jsonify(recognize_info), 201
    recognize_info = {'ret': 0}
    return jsonify(recognize_info), 201

@app.route('/searchdevice/', methods=['POST'],endpoint="searchdevice")
def post_Data():
    print('get a POST searchdevice')
    dict=str(request.data)
    dict=dict[2:-1]
    dict=ast.literal_eval(dict)
    devicename=dict["devicename"]
    ret_message={}
    try:
        sql="select * from device where name = '%s'"% (devicename)
        print(sql)
        cursor.execute(sql)
        temp=cursor.fetchone()
        print(temp)
        ret_message["locx"]=temp[1]
        ret_message["locy"]=temp[2]
        ret_message["iffoffline"]=temp[4]
        deviceid=temp[3]
        sql = "select sum(value) from historytable where deviceid = %s" % (deviceid)
        print(sql)
        cursor.execute(sql)
        temp = cursor.fetchone()
        ret_message["sum"]=int(temp[0])
    except:
        db.rollback()
        recognize_info = {'ret': 1}
        return jsonify(recognize_info), 201
    print(ret_message)
    recognize_info = {'ret': 0,"ret_message":ret_message}
    return jsonify(recognize_info), 201

@app.route('/gethistory/', methods=['POST'],endpoint="gethistory")
def post_Data():
    print('get a POST gethistory')
    dict=str(request.data)
    dict=dict[2:-1]
    dict=ast.literal_eval(dict)
    devicename=dict["devicename"]
    ret_message={}
    try:
        sql="select * from device where name = '%s'"% (devicename)
        print(sql)
        cursor.execute(sql)
        temp=cursor.fetchone()
        print(temp)
        deviceid=temp[3]
        sql = "select * from historytable where deviceid = %s order by time" % (deviceid)
        print(sql)
        cursor.execute(sql)
        temp = cursor.fetchall()
        history=[]
        for his in temp:
            history.append({
                "time":int(his[1]),
                "time_str":time.asctime(time.localtime(int(his[1])/1000)),
                "locx":his[2],
                "locy":his[3],
                "val":his[5],
                "ifalert":his[6]
            })
        print(history)
        ret_message=history
    except:
        db.rollback()
        recognize_info = {'ret': 1}
        return jsonify(recognize_info), 201
    print(ret_message)
    recognize_info = {'ret': 0,"ret_message":ret_message}
    return jsonify(recognize_info), 201

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=8000)
