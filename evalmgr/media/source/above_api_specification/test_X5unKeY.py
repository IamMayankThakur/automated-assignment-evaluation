import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="PES1201701342",
  auth_plugin='mysql_native_password'
)

mycursor = mydb.cursor()
mycursor.execute("DROP DATABASE a1")
mycursor.execute("CREATE DATABASE a1")
mycursor.execute("USE a1")
mycursor.execute("CREATE TABLE users (uname VARCHAR(255),pswd VARCHAR(255))")
print(mycursor)


