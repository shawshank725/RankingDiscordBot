import sqlite3

query_to_create_table = """CREATE TABLE IF NOT EXISTS server_data (
    user_id VARCHAR(40) NOT NULL,
    user_name VARCHAR(40),
    level INT NOT NULL,
    xp INT NOT NULL
);"""

query_to_insert = """INSERT INTO server_data (user_id , user_name,level,xp)
VALUES (?,?,1,1);"""

query_to_update = """UPDATE server_data SET xp = ?, level = ? WHERE user_id  = ?;"""

query_to_get_all_users = """
SELECT user_id  FROM server_data;
""" #this will give a list of tuples containing the data userid

query_to_get_user_info = """
SELECT level, xp FROM server_data WHERE user_id  = ?;
"""

query_to_get_users_desc = """
SELECT * FROM server_data ORDER BY level DESC, xp DESC;
"""

query_to_reset = """UPDATE server_data SET xp = 1, level = 1 WHERE level > 1 OR xp > 1;
"""
'''
connection = sqlite3.connect("server_data.db")
cursor_obj = connection.cursor()

cursor_obj.execute(query_to_reset)
connection.commit()

cursor_obj.execute(query_to_insert,(764730713718128690,"ironfiretruth",))
connection.commit()

connection.close()'''

