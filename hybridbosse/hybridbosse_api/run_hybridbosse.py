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


# yaml_file_path = dict()
#
# # Some preset scenarios:
# #
# # hybrid_inputs_7.5_7.5_7.5
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_7.5_7.5_7.5.yaml'

# hybrid_inputs_7.5_7.5_15
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_7.5_7.5_15.yaml'

# hybrid_inputs_15_15_15
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_15_15_15.yaml'

# hybrid_inputs_22.5_22.5_22.5
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_22.5_22.5_22.5.yaml'

# hybrid_inputs_22.5_22.5_45
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_22.5_22.5_45.yaml'

# hybrid_inputs_30_30_30
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_30_30_30.yaml'

# # hybrid_inputs_30_30_60
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_30_30_60.yaml'
#
# # hybrid_inputs_37.5_37.5_37.5
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_37.5_37.5_37.5.yaml'

# # hybrid_inputs_37.5_37.5_75
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \

# hybrid_inputs_45_45_45
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_45_45_45.yaml'

# hybrid_inputs_45_45_90
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_45_45_90.yaml'

# hybrid_inputs_52.5_52.5_52.5
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_52.5_52.5_52.5.yaml'

# hybrid_inputs_52.5_52.5_105
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_52.5_52.5_105.yaml'

# hybrid_inputs_60_60_60
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_60_60_60.yaml'

# hybrid_inputs_60_60_60
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_60_60_120.yaml'

# hybrid_inputs_67.5_67.5_67.5
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_67.5_67.5_67.5.yaml'

# hybrid_inputs_67.5_67.5_130
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_67.5_67.5_130.yaml'

# hybrid_inputs_75_75_75
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_75_75_75.yaml'

# hybrid_inputs_75_75_150
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_75_75_150.yaml'

# hybrid_inputs_82.5_82.5_82.5
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_82.5_82.5_82.5.yaml'

# hybrid_inputs_82.5_82.5_165
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_82.5_82.5_165.yaml'

# hybrid_inputs_90_90_90
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_90_90_90.yaml'

# hybrid_inputs_90_90_180
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_90_90_180.yaml'

# hybrid_inputs_97.5_97.5_97.5
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_97.5_97.5_97.5.yaml'

# hybrid_inputs_97.5_97.5_195
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_97.5_97.5_195.yaml'


# def display_results(hybrid_dict, wind_only_dict, solar_only_dict):
#
#     hybrids_df = pd.DataFrame(hybrid_dict['hybrid'].items(), columns=['Type', 'USD'])
#
#     hybrids_solar_df = pd.DataFrame(
#         hybrid_dict['Solar_BOS_results'].items(), columns=['Type', 'USD'])
#
#     hybrids_wind_df = pd.DataFrame(
#         hybrid_dict['Wind_BOS_results'].items(), columns=['Type', 'USD'])
#
#     solar_only_bos = dict()
#     solar_only_bos['gridconnection_usd'] = solar_only_dict['total_transdist_cost']
#     solar_only_bos['substation_cost'] = solar_only_dict['substation_cost']
#     solar_only_bos['total_management_cost'] = solar_only_dict['total_management_cost']
#
#     solar_only_bos_df = pd.DataFrame(
#         solar_only_bos.items(), columns=['Solar Only BOS Component', 'USD'])
#
#     wind_only_bos = dict()
#     wind_only_bos['total_gridconnection_cost'] = wind_only_dict['total_gridconnection_cost']
#     wind_only_bos['total_substation_cost'] = wind_only_dict['total_substation_cost']
#     wind_only_bos['total_management_cost'] = wind_only_dict['total_management_cost']
#     wind_only_bos_df = pd.DataFrame(
#         wind_only_bos.items(), columns=['Wind Only BOS Component', 'USD'])
#
#     print(hybrids_df)
#     print(solar_only_bos_df)
#     print(wind_only_bos_df)
#
#     return hybrids_df, hybrids_solar_df, hybrids_wind_df, solar_only_bos, wind_only_bos


# hybrids_scenario_dict = read_hybrid_scenario(yaml_file_path)
# hybrid_results, wind_only, solar_only = run(hybrids_scenario_dict)
# print(hybrid_results)
# display_results(hybrid_results, wind_only_dict=wind_only, solar_only_dict=solar_only)
