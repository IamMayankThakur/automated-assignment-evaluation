 
from flask import Flask
import sqlite3 as sql

app = Flask(__name__)

conn = sql.connect('rides.db')
#conn.execute('DROP TABLE rides_data')
conn.execute('CREATE TABLE rides_data (ride_id BIGINT AUTO_INCREMENT,username TEXT,time_stamp TEXT,source INT,destination INT)')
print("Table created")

conn.close()
