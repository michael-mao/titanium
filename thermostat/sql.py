#!/usr/bin/python

import csv
import urllib2
import urlparse
import sqlite3 as lite
from collections import defaultdict

db_conn = lite.connect("table.db")
cur = db_conn.cursor()  
  
#initialize the DB 
cur.executescript(            
''' DROP TABLE IF EXISTS Energy;
            CREATE TABLE IF NOT EXISTS 
            Energy(city varchar(50), 
                    start_time varchar(2),
                    cost varchar(6),
                    PRIMARY KEY(city,start_time) ); ''')

csv_data = csv.reader(file('energy_data.csv'))
#input data into SQL database
for row in csv_data:
	cur.execute("""INSERT INTO Energy(city,start_time,cost) VALUES('%s', '%s', '%s')""" % (row[0] , row[1], row[2] ) )
db_conn.commit()

#testing how to extract cost when given times
x = 19
cur.execute('''SELECT COST FROM Energy WHERE start_time = ?;''', (x,))
data = cur.fetchall()
#print data
for x in data:
    print x[0] 
    
#close connection
db_conn.close()        


