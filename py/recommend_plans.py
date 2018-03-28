import os
os.chdir("/home/mson/home/bind/recommend_plan/py")
import numpy as np
import pandas as pd
import sqlite3
from itertools import product

np.set_printoptions(suppress = True)

def pull_table(conn, table):
    return pd.read_sql_query(f"select * from {table}", conn)

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
            index = 'service', columns = 'iden', values = 'present',
            aggfunc = 'sum')
    cols = wide_format_corresp.columns
    rows = wide_format_corresp.index
    return (wide_format_corresp).astype(int).as_matrix(), rows, cols    

#%%

conn = sqlite3.connect("../plans_and_services.db")#"../bind.db")
services = pull_table(conn, "services")
plans    = pull_table(conn, "plans")
coverage = pull_table(conn, "plan_coverage")
members  = pull_table(conn, "members")
searches = pull_table(conn, "searches")
conn.close()

services.sort_values('service', inplace = True)

coverage_mat, cov_rows, cov_cols = make_correspondence_matrix(
        coverage.rename({'plan': 'iden'}, axis = 1), 
        plans.plan, 
        services.service)
uncoverage_mat = 1 - coverage_mat

history_mat, hist_rows, hist_cols = make_correspondence_matrix(
        searches.rename({'member_id': 'iden'}, axis = 1), 
        members.member_id, 
        services.service)

## Assert orderings are the same across matrices and frames.
assert((cov_rows == hist_rows).all())
assert((cov_cols == plans.plan).all())
assert((services.service == hist_rows).all())

costs = np.array(services.cost)
prices = np.array(plans.price)
at_risk_mat = (history_mat.T * -costs).T
actual_risk_mat = np.dot(at_risk_mat.T, uncoverage_mat)

## rows are members, columns are plans, values in cells are
## the negative expected value of having that plan for that member, were
## they to get treatment for every service in their history.
expected_negative_value_mat = actual_risk_mat - prices
