#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 25 14:17:37 2018

@author: mson
"""

import pandas as pd
import numpy as np
import os, sqlite3, random
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

def generate_services(service_universe, p):
    return [service for service in service_universe if random.random() < p]

def generate_services_for_each(ids, service_universe, probas):
    """
    
    """
    contents = []
    for (iden, i) in zip(ids, range(len(ids))):
        p = probas[i % len(probas)]
        services = generate_services(service_universe, p)
        for service in services:
            contents.append([iden, service])
    return pd.DataFrame(contents)

def generate_member_history(service_universe, probas, conn):
    members = pd.read_sql("select * from members", conn)
    histories = generate_services_for_each(members.member_id, service_universe, 
                                           probas)
    histories.columns = ['member_id', 'service']
    return histories

def generate_plan_coverage(service_universe, probas, conn):
    plans = pd.read_sql("select * from plans", conn)
    covered_services = generate_services_for_each(plans.plan, service_universe, 
                                                  probas)
    covered_services.columns = ['plan', 'service']
    return covered_services

def assign_code_grouping(hcpcs_code):
    digits = "".join([str(i) for i in range(10)])
    if hcpcs_code[0] in digits: 
        return 0
    pass

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
service_cost.to_sql(name = "services", con = conn,
                    index = False)
populate_with_defaults(DEFAULT_DATA_DIR, conn, ["plans", "members"])
services = pd.read_sql("select * from services", conn)

coverage_probas = [0.01, 0.33, 0.67, 1]
member_probas = [0.001, 0.01, 0.04]
histories = generate_member_history(services.service, member_probas, conn)
coverages = generate_plan_coverage(services.service, coverage_probas, conn)
histories.to_sql(name = "searches", con = conn, index = False)
coverages.to_sql(name = "plan_coverage", con = conn, index = False)

