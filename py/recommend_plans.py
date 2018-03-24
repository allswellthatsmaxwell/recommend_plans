import os
os.chdir("/home/mson/home/bind/recommend_plan")
import numpy as np
import pandas as pd
import sqlite3
from itertools import product

def pull_table(conn, table):
    return pd.read_sql_query(f"select * from {table}", conn)

def cross_join(df1, df2):
    key = 'key123'
    df1[key], df2[key] = True, True
    return pd.merge(df1, df2, on = key).drop(key, axis = 1)

def complete_coverage(coverage, plans, services):
    coverage_cross = (pd.DataFrame(
            [(plan, service) for plan, service in product(plans.unique(), 
                                                          services.unique())]))
    coverage_cross.columns = ['plan', 'service']
    coverage = coverage.copy()
    coverage['covered'] = True
    return pd.merge(coverage_cross,
                    coverage,
                    on = ['plan', 'service'], 
                    how = 'left').fillna(False)

def make_coverage_matrix(coverage, plans, services):
    """
    
    """
    coverage_complete = complete_coverage(coverage, plans.plan, 
                                          services.service)
    return (~coverage_complete.
            pivot(index = 'plan', 
                  columns = 'service', 
                  values = 'covered')).astype(int).as_matrix()
    
conn = sqlite3.connect("bind.db")
services = pull_table(conn, "services")
plans    = pull_table(conn, "plans")
coverage = pull_table(conn, "plan_coverage")
members  = pull_table(conn, "members")
searches = pull_table(conn, "searches")
conn.close()

coverage_mat = make_coverage_matrix(coverage, plans, services)
