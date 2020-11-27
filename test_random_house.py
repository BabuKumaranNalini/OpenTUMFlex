"""
The "test_random_house.py" tests opentumflex for 50 random houses 
"""

__author__ = "Babu Kumaran Nalini"
__copyright__ = "2020 TUM-EWK"
__credits__ = []
__license__ = "GPL v3.0"
__version__ = "1.0"
__maintainer__ = "Babu Kumaran Nalini"
__email__ = "babu.kumaran-nalini@tum.de"
__status__ = "Development"


import opentumflex
import os

# Input directory
base_dir = os.path.abspath(os.getcwd())
sub_dir = r'test_files_csv'
directory = os.path.join(base_dir, sub_dir)

# Output directory
output_dir = r'\output'
path_results = base_dir + output_dir

# Get all path to test files
filepath=[]
for filename in os.listdir(directory):  
    filepath.append(os.path.join(directory,filename))

# Iterate through all test files
i = 0
for path_input_data in filepath:
    ems = opentumflex.run_scenario(opentumflex.scenario_asinput,
                                   path_input=path_input_data, path_results=path_results,
                                    fcst_only=False, time_limit=10,
                                    show_flex_res=False, show_opt_res=False, save_opt_res=False,
                                    convert_input_tocsv=True, show_aggregated_flex=False,
                                    show_aggregated_flex_price='bar',  troubleshooting=False)
    print('Completed house '+str(i+10))
    i = i+1
