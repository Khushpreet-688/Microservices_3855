import mysql.connector
import os
# get password from env variable defined in docker file
db_pass = os.environ.get('DB_PASS')
db_conn = mysql.connector.connect(host="kafka-acit3855.canadacentral.cloudapp.azure.com", user="user",
password=db_pass, database="events")
db_cursor = db_conn.cursor()
db_cursor.execute('''
CREATE TABLE clock_in
(id INT NOT NULL AUTO_INCREMENT,
trace_id VARCHAR(100) NOT NULL,
emp_num VARCHAR(20) NOT NULL,
emp_name VARCHAR(250) NOT NULL,
store_code VARCHAR(20) NOT NULL,
num_hours_scheduled INTEGER NOT NULL,
timestamp VARCHAR(100) NOT NULL,
late_arrival INTEGER NOT NULL,
date_created VARCHAR(100) NOT NULL,
CONSTRAINT clock_in_pk PRIMARY KEY (id))
''')
db_cursor.execute('''
CREATE TABLE clock_out
(id INT NOT NULL AUTO_INCREMENT,
trace_id VARCHAR(100) NOT NULL,
emp_num VARCHAR(20) NOT NULL,
emp_name VARCHAR(250) NOT NULL,
store_code VARCHAR(20) NOT NULL,
num_hours_worked INTEGER NOT NULL,
timestamp VARCHAR(100) NOT NULL,
overtime_hours INTEGER NOT NULL,
date_created VARCHAR(100) NOT NULL,
CONSTRAINT clock_out_pk PRIMARY KEY (id))
''')
db_conn.commit()
db_conn.close()