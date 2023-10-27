import sqlite3
conn = sqlite3.connect('records.sqlite')
c = conn.cursor()
c.execute('''
CREATE TABLE clock_in
(id INTEGER PRIMARY KEY ASC,
trace_id VARCHAR(100) NOT NULL,
emp_num VARCHAR(20) NOT NULL,
emp_name VARCHAR(250) NOT NULL,
store_code VARCHAR(20) NOT NULL,
num_hours_scheduled INTEGER NOT NULL,
timestamp VARCHAR(100) NOT NULL,
late_arrival INTEGER NOT NULL,
date_created VARCHAR(100) NOT NULL)
''')

c.execute('''
CREATE TABLE clock_out
(id INTEGER PRIMARY KEY ASC,
trace_id VARCHAR(100) NOT NULL,
emp_num VARCHAR(20) NOT NULL,
emp_name VARCHAR(250) NOT NULL,
store_code VARCHAR(20) NOT NULL,
num_hours_worked INTEGER NOT NULL,
timestamp VARCHAR(100) NOT NULL,
overtime_hours INTEGER NOT NULL,
date_created VARCHAR(100) NOT NULL)
''')

conn.commit()
conn.close()