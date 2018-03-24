
import pandas as pd
import numpy as np

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

def coverage_matrix_creation_ok():
    coverage_frame = get_test_coverage_frame()   
    plans = get_test_plans_frame()
    services = get_test_services_frame()
    coverage_mat = make_coverage_matrix(coverage_frame, plans, services)
    expected_mat = np.array([[0, 0, 0, 1, 0],
                             [1, 1, 0, 0, 0],
                             [1, 1, 1, 0, 1],
                             [0, 0, 0, 0, 0]])
    return np.allclose(coverage_mat, expected_mat)

assert(coverage_matrix_creation_ok())