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
    """
    removes db_path, if it exists
    """
    try: 
        os.remove(db_path)
    except FileNotFoundError:
        pass

def populate_with_defaults(data_dir,
                           conn,
                           tables = ["services", 
                                     "plans", 
                                     "plan_coverage", 
                                     "members", 
                                     "searches"]):
    for table in tables:
        try:
            dat = pd.read_csv(f"{data_dir}/{table}.csv")
            dat.to_sql(name = table, con = conn, if_exists = "fail", 
                       index = False)
        except:
            print(f"Skipping creating {table} from defaults.")

def create_tables(sql_path, conn):
    """
    executes the statements in sql_path
    """
    with open(sql_path) as f: sql = f.read()
    statements = sql.split(";")
    for statement in statements:
        conn.execute(statement)
        conn.commit()

def mat1d_to_array(mat):
    assert(mat.shape[1]) == 1
    return mat.reshape(mat.shape[0])

def get_average_service_cost(dat):   
    """
    computes the average of service costs at all the providers (weighted
    by number of times each provider did the service) to get an average
    cost per hcpcs code
    returns: a dataframe with the columns service (which is hcpcs code) and
             cost, one row per hcpcs code
    """
    dat['weighted_cost'] = (dat['line_srvc_cnt'] * 
                            dat['average_submitted_chrg_amt'])
    mean_costs = (dat[['hcpcs_code', 'weighted_cost']].
                  groupby('hcpcs_code').
                  agg(['mean']))
    cost_service = pd.DataFrame({'service': np.array(mean_costs.index), 
                                 'cost': mat1d_to_array(mean_costs.values)})
    return cost_service[['service', 'cost']]

DATA_DIR = "../../../data/claims"
PROVIDER_FILE = "Medicare_Provider_Util_Payment_PUF_CY2015.txt"
DEFAULT_DATA_DIR = "../data"
SQL_CREATE_PATH = "../sql/create_db.sql"
DB_PATH = "../plans_and_services.db"

dat = pd.read_csv(f"{DATA_DIR}/{PROVIDER_FILE}", 
                  skiprows = lambda i: i == 1, 
                  nrows = 10000, 
                  delimiter = "\t")

service_cost = get_average_service_cost(dat)

create_new_database(DB_PATH)
conn = sqlite3.connect(DB_PATH)
service_cost.to_sql(name = "services", con = conn, if_exists = "append", 
                    index = False)
populate_with_defaults(DEFAULT_DATA_DIR, conn)


