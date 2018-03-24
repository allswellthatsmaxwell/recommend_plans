import os
os.chdir("/home/mson/home/bind/recommend_plan/py")
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

def complete_correspondence(service_correspondence, ids, services):
    """
    expands implicit zeros in service_correspondence to explicit zero
    rows; in other words, if there is a combination of id and service 
    not present in service_correspondence, a row with a 0 is added.
    else the existing row is given a 1. the 1's and 0's go in the new column,
    'present'.
    """
    id_service_cross = (pd.DataFrame(
            [(iden, service) for iden, service in product(ids.unique(), 
                                                          services.unique())]))
    id_service_cross.columns = ['iden', 'service']
    service_correspondence = service_correspondence.copy()
    service_correspondence['present'] = 1
    return pd.merge(id_service_cross,
                    service_correspondence,
                    on = ['iden', 'service'], 
                    how = 'left').fillna(0)

def make_correspondence_matrix(service_correspondence, ids, services):
    """
    Returns: a matrix where rows are ids and columns are services,
    The cell at each [id, service] is 1 if service is present for the id
    and 0 if it is not. 
    Arguments: 
        ids: a dataframe with the column iden
        services: a dataframe with the column service
        coverage: a dataframe with a row present for time service 
        corresponds to id.
    """
    corresp_complete = complete_correspondence(
            service_correspondence, ids, services)
    
    wide_format_corresp = corresp_complete.pivot_table(
            index = 'iden', columns = 'service', values = 'present',
            aggfunc = 'sum')
    cols = wide_format_corresp.columns
    rows = wide_format_corresp.index
    return (wide_format_corresp).astype(int).as_matrix(), rows, cols    
    
conn = sqlite3.connect("../bind.db")
services = pull_table(conn, "services")
plans    = pull_table(conn, "plans")
coverage = pull_table(conn, "plan_coverage")
members  = pull_table(conn, "members")
searches = pull_table(conn, "searches")
conn.close()

coverage_mat, cov_rows, cov_cols = make_correspondence_matrix(
        coverage.rename({'plan': 'iden'}, axis = 1), 
        plans.plan, 
        services.service)
uncoverage_mat = 1 - coverage_mat

history_mat, hist_rows, hist_cols = make_correspondence_matrix(
        searches.rename({'member_id': 'iden'}, axis = 1), 
        members.member_id, 
        services.service)

assert((cov_cols == hist_cols).all())

