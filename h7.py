#!C:\Users\tejas\AppData\Local\Programs\Python\Python310\python.exe

from dbconfig import *
import pymysql
import cgi
import cgitb
cgitb.enable()

#	Establish a cursor for MySQL connection.
db = get_mysql_param()
cnx = pymysql.connect(user=db['user'], 
                      password=db['password'],
                      host=db['host'],
                      # port needed only if it is not the default number, 3306.
                      # port = int(db['port']), 
                      database=db['database'])
                      
cursor = cnx.cursor()

#	Create HTTP response header
print("Content-Type: text/html;charset=utf-8")
print()

#	Create a primitive HTML starter
print ('''<html>
<head></head>
<body>
''')

#	Get HTTP parameter, ctid (caretaker id) and sid (swimmer id)
form = cgi.FieldStorage()
mid = form.getfirst('mid')

if mid is None:
    #	No HTTP parameter: show all levels and swimmer in the levels
    print('<h3>Information about events</h3>')
    print('<ol>')


    query = '''
WITH t1 AS (
         SELECT m1.meetId, m1.title, COUNT(DISTINCT p1.eventId) AS n_events
         FROM Event AS e1 JOIN Meet AS m1 ON (e1.meetId = m1.meetId)
         JOIN participation AS p1 ON (e1.eventId = p1.eventId)
         GROUP BY m1.meetId
),

t2 AS (
     SELECT m2.meetId, m2.title, COUNT(DISTINCT p2.eventId) AS n_events, m2.date, v2.Name
     FROM Event AS e2 JOIN Meet AS m2 ON (e2.MeetId = m2.MeetId)
     JOIN participation AS p2 ON (e2.eventId = p2.eventId)
     JOIN venue AS v2 ON (m2.VenueId = v2.VenueId)
     GROUP BY m2.MeetId
),

t3 AS (
     SELECT m3.MeetId,
     GROUP_CONCAT(CONCAT('<a href="?mid=', m3.meetId, '">', m3.title, '</a>:', n_events, ' events on ', t2.date, ' at ', t2.name, '</li>') SEPARATOR '') AS information
     FROM meet AS m3 JOIN t2 ON (t2.title = m3.title)
     GROUP BY m3.MeetId
)

SELECT t1.title, t3.information
FROM t1 JOIN t3 ON (t1.MeetId = t3.MeetId)

'''
    cursor.execute(query)
    print('<ol>') 
    for ( title, information ) in cursor:
        print( '<li>' + information)
       
    print('</ol>')
    print('</body></html>')
    cursor.close()
    cnx.close()		
    quit()
	
    
if mid is not None:

    query = '''
SELECT m.title AS title,
GROUP_CONCAT(DISTINCT CONCAT('   <li>', 'level ', l.levelId, ': ', l.Level, ' ', l.levelId, '; events', '</li>\n') SEPARATOR '') AS level,
GROUP_CONCAT(DISTINCT CONCAT('  <ol>\n', 'id: ', e.EventId, '; title: ', e.Title, '</ol></li>\n') SEPARATOR '') AS event
FROM meet AS m INNER JOIN event AS e ON (m.MeetId = e.MeetId)
    INNER JOIN participation AS p ON (p.eventId = e.eventId)
    INNER JOIN level AS l ON (l.LevelId = e.LevelId)
    WHERE m.MeetId = %s
    GROUP BY l.Level, l.LevelId
    '''

    cursor.execute(query,(int(mid),))
    (title, level, event) = cursor.fetchone()
    print('<p>More information on meet #'+ mid + ' :' + title + '<ol>' + level + event)
    for ( title, level, event ) in cursor:
        print(level + event + '</ol>' )
    
        
        
cursor.close()
cnx.close()

print ('''</body>
</html>''')