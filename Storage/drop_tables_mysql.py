import mysql.connector
import os
# get password from env variable defined in docker file
db_pass = os.environ.get('DB_PASS')
db_conn = mysql.connector.connect(host="kafka-acit3855.canadacentral.cloudapp.azure.com", user="user",
password=db_pass, database="events")
db_cursor = db_conn.cursor()
db_cursor.execute('''
DROP TABLE clock_in, clock_out
''')
db_conn.commit()
db_conn.close()