# A set of utility database functions that can be imported and used across various modules.
# Often used to insert a new row for a new member, or retrieving information about a specific member
# that isn't specific to a particular module

import sqlite3
import os
import os.path
import onebot_config


# lists available server databases
def list_db():
    file_list = os.listdir(path=onebot_config.DB_PATH)
    dbs_list = []
    for file in file_list:
        if file.endswith(".db"):
            dbs_list.append(file.replace(".db", ""))
    return dbs_list


# creates a new database for the specified server_id
# uses sql_schema.sql for initial DB schema
def create_db(server_id):
    db_path = onebot_config.DB_PATH + str(server_id) + ".db"
    db_schema = onebot_config.DB_PATH + "schema.sql"
    if os.path.exists(db_path):
        return
    with open(db_schema, "r", encoding="utf-8") as sql_schema:
        db_schema = sql_schema.read()
    db_create_commands = db_schema.split(";")
    db = sqlite3.connect(db_path)
    db_cursor = db.cursor()
    for command in db_create_commands:
        db_cursor.execute(command)
    db_cursor.close()
    db.commit()
    db.close()


def delete_db(server_id):
    db_path = onebot_config.DB_PATH + str(server_id) + ".db"
    try:
        os.remove(db_path)
    except FileNotFoundError:
        pass


# returns a sqlite3 connection object to the database for the specified server_id
# creates a database for the server automatically if not found
def get_db_connection(server_id):
    db_path = onebot_config.DB_PATH + str(server_id) + ".db"
    if not os.path.exists(db_path):
        create_db(server_id)
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    return db


def get_server_pref(server_id, pref_name):
    db = get_db_connection(server_id)
    db_cursor = db.cursor()
    db_param = (pref_name,)
    db_cursor.execute("SELECT * FROM server_preferences WHERE name = ?;", db_param)
    db_result = db_cursor.fetchone()
    db_cursor.close()
    db.close()
    if not db_result:
        return None
    return db_result["value"]


def set_server_pref(server_id, pref_name, value):
    db = get_db_connection(server_id)
    db_cursor = db.cursor()
    if get_server_pref(server_id, pref_name):
        db_param = (value, pref_name,)
        db_cursor.execute("UPDATE server_preferences SET value = ? WHERE name = ?;", db_param)
    else:
        db_param = (pref_name, value,)
        db_cursor.execute("INSERT INTO server_preferences VALUES (?,?);", db_param)
    db_cursor.close()
    db.commit()
    db.close()


def clear_server_pref(server_id, pref_name):
    db = get_db_connection(server_id)
    db_cursor = db.cursor()
    db_param = (pref_name,)
    db_cursor.execute("DELETE FROM server_preferences WHERE name = ?;", db_param)
    db_cursor.close()
    db.commit()
    db.close()


def get_member_pref(server_id, user_id, pref_name):
    db = get_db_connection(server_id)
    db_cursor = db.cursor()
    db_param = (user_id, pref_name)
    db_cursor.execute("SELECT * FROM member_preferences WHERE user = ? AND name = ?", db_param)
    db_result = db_cursor.fetchone()
    db_cursor.close()
    db.close()
    if not db_result:
        return None
    return db_result["value"]


def set_member_pref(server_id, user_id, pref_name, value):
    db = get_db_connection(server_id)
    db_cursor = db.cursor()
    if get_member_pref(server_id, user_id, pref_name):
        db_param = (value, user_id, pref_name,)
        db_cursor.execute("UPDATE member_preferences SET value = ? WHERE user = ? AND name = ?;", db_param)
    else:
        db_param = (user_id, pref_name, value,)
        db_cursor.execute("INSERT INTO member_preferences VALUES (?,?,?);", db_param)
    db_cursor.close()
    db.commit()
    db.close()
