#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 25 14:17:37 2018

@author: mson
"""

import pandas as pd
import numpy as np
import os
import sqlite3
os.chdir("/home/mson/home/bind/recommend_plan/py")
np.set_printoptions(suppress = True)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

def create_new_database(db_path):
    try: 
        os.remove(db_path)
    except FileNotFoundError:
        pass

def create_tables(sql_path, conn):
    with open(sql_path) as f: sql = f.read()
    statements = sql.split(";")
    for statement in statements:
        conn.execute(statement)
        conn.commit()

def mat1d_to_array(mat):
    assert(mat.shape[1]) == 1
    return mat.reshape(mat.shape[0])

def get_average_service_cost(dat):    
    dat['weighted_cost'] = (dat['line_srvc_cnt'] * 
                            dat['average_submitted_chrg_amt'])
    mean_costs = (dat[['hcpcs_code', 'weighted_cost']].
                  groupby('hcpcs_code').
                  agg(['mean']))
    cost_service = pd.DataFrame({'service': np.array(mean_costs.index), 
                                 'cost': mat1d_to_array(mean_costs.values)})
    return cost_service[['service', 'cost']]

DATA_DIR = "../../../data/claims"
DATA_FILE = "Medicare_Provider_Util_Payment_PUF_CY2015.txt"
SQL_CREATE_PATH = "../sql/create_db.sql"
DB_PATH = "../plans_and_services.db"

dat = pd.read_csv(f"{DATA_DIR}/{DATA_FILE}", 
                  skiprows = lambda i: i == 1, 
                  nrows = 10000, 
                  delimiter = "\t")

service_cost = get_average_service_cost(dat)

create_new_database(DB_PATH)
conn = sqlite3.connect(DB_PATH)
create_tables(SQL_CREATE_PATH, conn)
service_cost.to_sql(name = "services", con = conn, if_exists = "append", 
                    index = False)



