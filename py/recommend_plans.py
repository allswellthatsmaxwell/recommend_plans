import os
os.chdir("/home/mson/home/bind/recommend_plan")
import numpy as np
import pandas as pd
import sqlite3

def pull_table(conn, table):
    return pd.read_sql_query(f"select * from {table}", conn)

conn = sqlite3.connect("bind.db")
services = pull_table(conn, "services")
plans    = pull_table(conn, "plans")
members  = pull_table(conn, "members")
searches = pull_table(conn, "searches")
conn.close()