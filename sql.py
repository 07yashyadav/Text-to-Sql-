import sqlite3

#connect to sqlite database
connection = sqlite3.connect('students.db')

#cursor object for insrt,create,update,delete ob
cursor = connection.cursor()

#create table
table_info = """
    Create table STUDENT(NAME VARCHAR(25), CLASS VARCHAR(25), SECTION VARCHAR(25),MARKS INT);
"""

cursor.execute(table_info)

#insrt some records
cursor.execute('''INSERT INTO STUDENT VALUES('Yash','10th','A',85)''')
cursor.execute('''INSERT INTO STUDENT VALUES('Monika','9th','B',95)''')
cursor.execute('''INSERT INTO STUDENT VALUES('Anshul','10th','A',75)''')
cursor.execute('''INSERT INTO STUDENT VALUES('Harish','11th','C',65)''')
cursor.execute('''INSERT INTO STUDENT VALUES('Navin','12th','D',55)''')

#Display records
print("inserted records are:")
data = cursor.execute('''SELECT * FROM STUDENT''')

for row in data:
    print(row)

connection.commit() #commit the changes
connection.close() #close the connection

