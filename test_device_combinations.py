"""
The "test_combinations.py" tests opentumflex for all possible combinations of devices
"""

__author__ = "Babu Kumaran Nalini"
__copyright__ = "2020 TUM-EWK"
__credits__ = []
__license__ = "GPL v3.0"
__version__ = "1.0"
__maintainer__ = "Babu Kumaran Nalini"
__email__ = "babu.kumaran-nalini@tum.de"
__status__ = "Development"

  
# new modules
import opentumflex

# general modules
import os
import itertools
from joblib import Parallel, delayed
import multiprocessing
import tqdm


def run_scenario_parallel(tc, param_con):
    """ run an OpenTUMFlex model for given scenario

    Args:
        - scenario: predefined scenario function which will modify the parameters in opentumflex dictionary to create
          a certain scenario
        - path_input: path of input file which can be used to read devices parameters and forecasting data
        - path_results: path to be saved in for results of the optimization
        - fcst_only: if true, read_data() will only read forecasting data from input file, otherwise it will also read
          device parameters
        - time_limit: determine the maximum duration of optimization in seconds

    Returns:
        opentumflex dictionary with optimization results and flexibility offers

    """

    # initialize with basic time settings
    my_ems = opentumflex.initialize_time_setting(t_inval=15, start_time='2019-12-18 00:00', end_time='2019-12-18 23:45')

    # read devices parameters and forecasting data from xlsx or csv file
    if param_con[0] == opentumflex.scenario_fromfile:
        # read devices parameters and forecasting data from xlsx or csv file
        my_ems = opentumflex.read_data(my_ems, param_con[1], fcst_only=False, to_csv=True)
    else:
        # read only the input time series from the excel table
        my_ems = opentumflex.read_data(my_ems, param_con[1], fcst_only=True, to_csv=False)
        # modify the opentumflex regarding to predefined scenario
        my_ems = param_con[0](my_ems, tc)

    # create Pyomo model from opentumflex data
    m = opentumflex.create_model(my_ems)

    # solve the optimization problem
    m = opentumflex.solve_model(m, solver='glpk', time_limit=param_con[4], troubleshooting=param_con[5])

    # extract the results from model and store them in opentumflex['optplan'] dictionary
    my_ems = opentumflex.extract_res(m, my_ems)

    # visualize the optimization results
    opentumflex.plot_optimal_results(my_ems, show_balance=param_con[5], show_soc=param_con[5])

    # save the data in .xlsx in given path
    if param_con[5]:
        opentumflex.save_results(my_ems, path_results)

    # calculate the flexibility
    # create a group of all flex calculators
    calc_flex = {opentumflex.calc_flex_hp: 'hp',
                 opentumflex.calc_flex_ev: 'ev',
                 opentumflex.calc_flex_chp: 'chp',
                 opentumflex.calc_flex_bat: 'bat',
                 opentumflex.calc_flex_pv: 'pv'}

    # iterate through all the flexibility functions
    for function, device_name in calc_flex.items():
        if my_ems['devices'][device_name]['maxpow'] != 0:
            function(my_ems, reopt=False)

    # plot the results of flexibility calculation
    if param_con[5]:
        for device_name in calc_flex.values():
            if my_ems['devices'][device_name]['maxpow'] != 0:
                opentumflex.plot_flex(my_ems, device_name)

    # plot stacked flexibility of all devices
    if param_con[5]:
        opentumflex.plot_aggregated_flex_power(my_ems)
        opentumflex.plot_aggregated_flex_price(my_ems, plot_flexpr=param_con[5])

    print('Scenario ' + str(tc) + ' completed!')
    return my_ems


if __name__ == '__main__':

    # Input and output file path
    base_dir = os.path.abspath(os.getcwd())
    input_file = r'\..\input\input_data.csv'
    output_dir = r'\..\results'
    path_input_data = base_dir + input_file
    path_results = base_dir + output_dir

    # For parallel testing
    lst = list(itertools.product([0, 1], repeat=5))
    for i in range(len(lst)):
        lst[i] = ''.join([str(x) for x in lst[i]])

    lst = lst[1:]

    param_constant = [opentumflex.scenario_combination_test, path_input_data, path_results, 'glpk', 100, False, False, False, False, False,  'bar', False, False, False]                   # Plot optimized SOC plan

    Parallel(n_jobs=int(multiprocessing.cpu_count()))(
        delayed(run_scenario_parallel)(i, param_constant) for i in lst)

