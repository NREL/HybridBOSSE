import yaml
import os
from hybridbosse.hybrids_shared_infrastructure.run_BOSSEs import run_BOSSEs
from hybridbosse.hybrids_shared_infrastructure.PostSimulationProcessing import PostSimulationProcessing
import pandas as pd


# Main API method to run a Hybrid BOS model:
def run(hybrids_input_dict):
    """
    Returns a dictionary with detailed Shared Infrastructure BOS results.
    """
    wind_BOS, solar_BOS = run_BOSSEs(hybrids_input_dict)
    # Store a copy of both solar only and wind only outputs dictionaries:
    wind_only_BOS = wind_BOS.copy()
    solar_only_BOS = solar_BOS.copy()

    # print('wind_only_BOS at ', hybrids_input_dict['wind_plant_size_MW'], ' MW: ' , wind_BOS)
    # print('solar_only_BOS ', hybrids_input_dict['solar_system_size_MW_DC'], ' MW: ' , solar_BOS)
    if hybrids_input_dict['wind_plant_size_MW'] > 0:
        # BOS of Wind only power plant:
        print('')
        # print('Wind BOS: ', (wind_BOS['total_bos_cost'] /
        #                      (hybrids_input_dict['wind_plant_size_MW'] * 1e6)))
    else:
        wind_BOS['total_management_cost'] = 0

    if hybrids_input_dict['solar_system_size_MW_DC'] > 0:
        # BOS of Solar only power plant:
        print('')
        # print('Solar BOS: ', (solar_BOS['total_bos_cost'] /
        #                       (hybrids_input_dict['solar_system_size_MW_DC'] * 1e6)))
    else:
        solar_BOS['total_management_cost'] = 0

    results = dict()
    results['hybrid'] = dict()
    hybrid_BOS = PostSimulationProcessing(hybrids_input_dict, wind_BOS, solar_BOS)
    results['hybrid']['hybrid_BOS_usd'] = hybrid_BOS.hybrid_BOS_usd
    results['hybrid']['hybrid_BOS_usd_watt'] = hybrid_BOS.hybrid_BOS_usd_watt
    results['hybrid']['hybrid_gridconnection_usd'] = hybrid_BOS.hybrid_gridconnection_usd
    results['hybrid']['hybrid_substation_usd'] = hybrid_BOS.hybrid_substation_usd

    results['hybrid']['hybrid_management_development_usd'] = wind_BOS['total_management_cost'] + \
                                                             solar_BOS['total_management_cost'] + \
                                                             hybrid_BOS.site_facility_usd

    results['Wind_BOS_results'] = hybrid_BOS.update_BOS_dict(wind_BOS, 'wind')
    results['Solar_BOS_results'] = hybrid_BOS.update_BOS_dict(solar_BOS, 'solar')
    return results, wind_only_BOS, solar_only_BOS


def read_hybrid_scenario(file_path):
    """
    [Optional method]

    Reads in default hybrid_inputs.yaml (YAML file) shipped with
    hybrids_shared_infrastructure, and returns a python dictionary with all required
    key:value pairs needed to run the hybrids_shared_infrastructure API.
    """
    if file_path:
        input_file_path = file_path['input_file_path']
        with open(input_file_path, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
    else:
        input_file_path = os.path.dirname(__file__)
        with open(input_file_path + '/hybrid_inputs.yaml', 'r') as stream:
            data_loaded = yaml.safe_load(stream)

    hybrids_scenario_dict = data_loaded['hybrids_input_dict']

    if hybrids_scenario_dict['num_turbines'] is None or \
        hybrids_scenario_dict['num_turbines'] == 0:

        hybrids_scenario_dict['num_turbines'] = 0

    hybrids_scenario_dict['wind_plant_size_MW'] = hybrids_scenario_dict['num_turbines'] * \
                                                  hybrids_scenario_dict['turbine_rating_MW']

    hybrids_scenario_dict['hybrid_plant_size_MW'] = hybrids_scenario_dict['wind_plant_size_MW'] + \
                                                    hybrids_scenario_dict['solar_system_size_MW_DC']

    hybrids_scenario_dict['hybrid_construction_months'] = \
        hybrids_scenario_dict['wind_construction_time_months'] + \
        hybrids_scenario_dict['solar_construction_time_months']

    return hybrids_scenario_dict


hybrids_input_dict = dict()
hybrids_input_dict['shared_interconnection'] = True
hybrids_input_dict['distance_to_interconnect_mi'] = 1  # Input not used for projects <= 15 MW
hybrids_input_dict['new_switchyard'] = True
hybrids_input_dict['grid_interconnection_rating_MW'] = 7.5
hybrids_input_dict['interconnect_voltage_kV'] = 15
hybrids_input_dict['shared_substation'] = True
hybrids_input_dict['hybrid_substation_rating_MW'] = 7.5

# Wind farm required inputs
hybrids_input_dict['num_turbines'] = 5
hybrids_input_dict['turbine_rating_MW'] = 1.5
hybrids_input_dict['wind_dist_interconnect_mi'] = 0    # Only used for calculating grid cost of wind only. Input not used for projects <= 15 MW
hybrids_input_dict['wind_construction_time_months'] = 5
hybrids_input_dict['project_id'] = 'hybrids'
# hybrids_input_dict['path_to_project_list'] = '/Users/pbhaskar/Desktop/Projects/Shared Infrastructure/hybrids_shared_infra_tool/'
# hybrids_input_dict['name_of_project_list'] = 'project_list_ge15_dist_05'

# Solar farm required inputs
hybrids_input_dict['solar_system_size_MW_DC'] = 7.5
hybrids_input_dict['solar_construction_time_months'] = 5   # Optional. Overrides the internal scaling MW vs. construction time relationship
hybrids_input_dict['solar_dist_interconnect_mi'] = 0   # Only

# pre-processed input data:
hybrids_input_dict['wind_plant_size_MW'] = hybrids_input_dict['num_turbines'] * \
                                           hybrids_input_dict['turbine_rating_MW']

hybrids_input_dict['hybrid_plant_size_MW'] = hybrids_input_dict['wind_plant_size_MW'] + \
                                             hybrids_input_dict['solar_system_size_MW_DC']

hybrids_input_dict['hybrid_construction_months'] = \
    hybrids_input_dict['wind_construction_time_months'] + \
    hybrids_input_dict['solar_construction_time_months']


hybrid_results, wind_only, solar_only = run(hybrids_input_dict)


print('Hybrid Dictionary Results:')
print('')
print(hybrid_results)
print('')
print('Wind Only Dictionary Results:')
print('')
print(wind_only)
print('')
print('Solar Only Dictionary Results:')
print('')
print(solar_only)
