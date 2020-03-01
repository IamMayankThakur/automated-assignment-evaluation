from flask import Flask, request, abort, render_template,jsonify, Response
import sqlite3
import requests
import re
pword_pat = re.compile('^[a-fA-F0-9]{40}$')

app = Flask(__name__)

@app.route('/api/v1/users/<username>',methods=['DELETE'])
def del_user(username):

    SQL_query = {"table":"Users","columns":["uname"],"where":"1"}
    username_list = requests.post(url='http://127.0.0.1:5000/api/v1/db/read',json=SQL_query)
    is_present=0
    username_list=username_list.json()

    for x in username_list["uname"]:
        if(username==x):
            is_present=1
            break

    if(is_present):
        print("is_present")
        sql_del = {"insert":[username],"table":"Users","columns":["uname"],"isDelete":"True"}
        requests.post(url='http://127.0.0.1:5000/api/v1/db/write',json=sql_del)
        return Response(status=200)

    else:
        #user not is_present
        return Response(status=400)

@app.route('/api/v1/users', methods=['PUT'])
def add_user():
    print('gfdgdf')
    data = request.get_json()
    uname = data['username']
    pword = data['password']

    SQL_query = {"table":"Users","columns":["uname"] ,"where":"1"}
    username_list = requests.post(url='http://127.0.0.1:5000/api/v1/db/read',json=SQL_query)
    valid=1
    username_list=username_list.json()
    print("9th api called . . .")
    print(username_list)

    for x in username_list:
        if(uname==x):
            valid=0
            break

    if(valid):
        #check password
        print("Password is :"+pword)
        match = re.search(pword_pat,pword)
        if not match:
            #invalid password
            return Response(status=400)
        else:
            #add
            sql_add = {"insert":[uname,pword],"table":"Users","columns":["uname","pwd"],"isDelete":"False"}
            requests.post(url='http://127.0.0.1:5000/api/v1/db/write',json=sql_add)
            return Response(status=201)
    else:
        #invalid uname
        return Response(status=400)
        @app.route('/api/v1/db/write',methods=["POST"])
        def addToDB():
            result={}
            result['status']=200
            try:
                cxn=sqlite3.connect('RideShare.db')
                cursor=cxn.cursor()
                cursor.execute('PRAGMA foreign_keys = ON')
            except Exception as e:
                cxn.close()
                result['status']=400
                print(e)
                return result
            cxn.commit()
            data=request.get_json()
            print(data)
            isDelete=data['isDelete']
            sqlQuery=""
            print(isDelete)
            tableName=data['table']
            insertData=data['insert']
            columns=data['columns']
            if isDelete=="True":
                print("ELSE")
                sqlQuery='DELETE FROM '+tableName+ ' WHERE '+columns[0]+'="'+insertData[0]+'"'
                print(sqlQuery)
            else:
                print("HI")
                sqlQuery='INSERT INTO '+tableName + ' ('
                for i in columns:
                    sqlQuery=sqlQuery+i+','
                sqlQuery=sqlQuery[0:-1]
                sqlQuery=sqlQuery+') VALUES('

                for i in insertData:
                    sqlQuery+='"'+i+'"'+','
                sqlQuery=sqlQuery[0:-1]
                sqlQuery+=')'
                print("\n\n"+sqlQuery)
            try:
                cursor.execute(sqlQuery)
                cxn.commit()
            except Exception as e:
                cxn.close()
                result['status']=400
                print(e)
                return result
            cxn.close()
            return result

        @app.route('/api/v1/db/read',methods=["POST"])
        def readDB():
            print("reading DB. . .")
            result={}
            try:
                cxn=sqlite3.connect('RideShare.db')
                cursor=cxn.cursor()
                cursor.execute('PRAGMA foreign_keys = ON')

            except Exception as e:
                cxn.close()
                result['status']=400
                print(e)
                return result

            cxn.commit()
            data=request.get_json()
            #print(data)

            sqlQuery=""
            tableName=data['table']
            whereClause=data['where']
            columns=data['columns']
            #print("HI")
            sqlQuery='SELECT '
            for i in columns:
                sqlQuery+=i+','
            sqlQuery=sqlQuery[0:-1]
            sqlQuery+=' FROM '+tableName + ' WHERE '+whereClause
            print(sqlQuery)
            try:
                cursor.execute(sqlQuery)
                rows = cursor.fetchall()

                #for row in rows:
                    #print(list(row))

                result["count"]=len(rows)
                result["status"]=200
                k=-1
                for i in columns:
                    result[i]=[]
                    k+=1
                    for data in rows:
                        result[i].append(data[k])

                #print(result)
                cxn.commit()
            except Exception as e:
                cxn.close()
                print(e)
                result['status']=400
                return result
            cxn.close()
            return result

            def sql_fetch(con):

                con=sqlite3.connect('RideShare.db')
                cursor=con.cursor()

                cursorObj1.executesqlQuery=""
                tableName=data['table']
                whereClause=data['where']
                columns=data['columns']
                #print("HI")
                sqlQuery='SELECT '
                for i in columns:
                    sqlQuery+=i+','
                sqlQuery=sqlQuery[0:-1]
                sqlQuery+=' FROM '+tableName + ' WHERE '+whereClause
                print(sqlQuery)
                try:
                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()

                rows = cursorObj.fetchall()

                for row in rows:

                    print(row)

            sql_fetch(con)

@app.route('/api/v1/db/write',methods=["POST"])
def delete_all_task(conn)
def delete_all_tasks(conn):
    """
    Delete all rows in the tasks table
    :param conn: Connection to the SQLite database
    :return:
    """
    sql = 'DELETE FROM Timestamp table'
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
