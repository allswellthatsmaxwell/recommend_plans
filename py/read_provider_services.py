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


def mat1d_to_array(mat):
    assert(mat.shape[1]) == 1
    return mat.reshape(mat.shape[0])

def get_average_service_cost(dat):    
    dat['weighted_cost'] = (dat['line_srvc_cnt'] * 
                            dat['average_submitted_chrg_amt'])
    mean_costs = (dat[['hcpcs_code', 'weighted_cost']].
                  groupby('hcpcs_code').
                  agg(['mean']))
    return pd.DataFrame({'service': np.array(mean_costs.index), 
                         'cost': mat1d_to_array(mean_costs.values)})

DATA_DIR = "../../../data/claims"
FILE = "Medicare_Provider_Util_Payment_PUF_CY2015.txt"
dat = pd.read_csv(f"{DATA_DIR}/{FILE}", 
                  skiprows = lambda i: i == 1, 
                  nrows = 10000, 
                  delimiter = "\t")

service_cost = get_average_service_cost(dat)
