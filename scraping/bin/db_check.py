import sqlite3

dbname = 'trip_advisor.db'

with sqlite3.connect(dbname) as conn:
	cur = conn.cursor()
	qry = "insert into vietnam ('key') values ('test')"
	cur.execute(qry) 
	conn.commit()
