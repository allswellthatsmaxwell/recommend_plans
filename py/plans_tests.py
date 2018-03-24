
import pandas as pd
import numpy as np
#from recommend_plans import make_coverage_matrix

def get_test_coverage_frame():
    coverage_frame = pd.DataFrame([['O','Sinusitus'],
                                   ['O','Hip Surgery'],
                                   ['O','Knee Replacement'],
                                   ['O','Carpal Tunnel'],
                                   ['Q','Sinusitus'],
                                   ['Q','STI'],
                                   ['Q','Knee Replacement'],
                                   ['R','STI'],
                                   ['S','Sinusitus'],
                                   ['S','Hip Surgery'],
                                   ['S','STI'],
                                   ['S','Knee Replacement'],
                                   ['S','Carpal Tunnel']])
    coverage_frame.columns = ['plan', 'service']
    return coverage_frame

def get_test_members_frame():
    members_frame = pd.DataFrame(['A', 'B'])
    members_frame.columns = ['member_id']
    return members_frame

def get_test_searches_frame():
    searches_frame = pd.DataFrame([['A','Sinusitus'],
                                   ['A','Hip Surgery'],
                                   ['A','Knee Replacement'],
                                   ['B','Sinusitus'],
                                   ['B','Sinusitus'],
                                   ['B','STI']])
    searches_frame.columns = ['member_id', 'service']
    return searches_frame

def get_test_plans_frame():
    plans = pd.DataFrame(['O', 'Q', 'R', 'S'])
    plans.columns = ['plan']
    return plans

def get_test_services_frame():
    services = pd.DataFrame([['Sinusitus', 5.],
                             ['Hip Surgery', 39000.],
                             ['STI', 20.],
                             ['Knee Replacement', 40000.],
                             ['Carpal Tunnel', 3000.]])
    services.columns = ['service', 'cost']
    return services

def get_test_history_mat():
    searches_frame = get_test_searches_frame()
    services = get_test_services_frame()
    members = get_test_members_frame()
    history_mat, rownames, colnames = make_correspondence_matrix(
        searches_frame.rename({'member_id': 'iden'}, axis = 1), 
        members.member_id, 
        services.service)
    return history_mat, rownames, colnames     

def get_test_coverage_mat():
    coverage_frame = get_test_coverage_frame()   
    plans = get_test_plans_frame()
    services = get_test_services_frame()
    coverage_mat, rownames, colnames = make_correspondence_matrix(
        coverage_frame.rename({'plan': 'iden'}, axis = 1), 
        plans.plan, 
        services.service)
    return coverage_mat, rownames, colnames 

def coverage_matrix_creation_ok():
    coverage_mat, rownames, colnames = get_test_coverage_mat()
    uncoverage_mat = 1 - coverage_mat
    expected_mat = np.array([[0, 0, 0, 1, 0],
                             [1, 1, 0, 0, 0],
                             [1, 1, 1, 0, 1],
                             [0, 0, 0, 0, 0]])
    return np.allclose(uncoverage_mat, expected_mat)

def history_matrix_creation_ok():
    history_mat, rownames, colnames = get_test_history_mat()
    expected_mat = np.array([[0, 1, 1, 0, 1],
                             [0, 0, 0, 1, 2]])
    return np.allclose(history_mat, expected_mat)

    
assert(coverage_matrix_creation_ok())
assert(history_matrix_creation_ok())