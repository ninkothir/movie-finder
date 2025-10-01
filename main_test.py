# pip install python-dotenv
import os
import dotenv
from pathlib import Path
import pymysql


dotenv.load_dotenv(Path('.env'))
dbconfig = {'host': os.environ.get('host'),
            'user': os.environ.get('user'),
            'password': os.environ.get('password'),
            'database': 'hr'}

connection = pymysql.connect(**dbconfig)
cursor = connection.cursor()

cursor.execute(
'''
    show tables
''')

result = cursor.fetchall()
for num, table in enumerate(result, start=1):
    print(f"{num}: {table[0]}")
table = input("Choose table: ")

cursor.execute(f'SELECT * FROM {table}')
result = cursor.fetchall()
print(*result, sep='\n')

cursor.close()
connection.close()

