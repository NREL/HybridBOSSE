import yaml
import os
from hybrids_shared_infrastructure.run_BOSSEs import run_BOSSEs
from hybrids_shared_infrastructure.PostSimulationProcessing import PostSimulationProcessing
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# Main API method to run a Hybrid BOS model:
def run_hybrid_BOS(hybrids_input_dict):
    """
    Returns a dictionary with detailed Shared Infrastructure BOS results.
    """
    wind_BOS, solar_BOS = run_BOSSEs(hybrids_input_dict)
    # Store a copy of both solar only and wind only outputs dictionaries:
    wind_only_BOS = wind_BOS.copy()
    solar_only_BOS = solar_BOS.copy()

    print('Hybrid rating:', hybrids_input_dict['hybrid_plant_size_MW'])
    print('Grid rating:', hybrids_input_dict['grid_interconnection_rating_MW'])
    print('wind_only_BOS at ', hybrids_input_dict['wind_plant_size_MW'], ' MW: ' , wind_BOS)
    print('solar_only_BOS ', hybrids_input_dict['solar_system_size_MW_DC'], ' MW: ' , solar_BOS)
    if hybrids_input_dict['wind_plant_size_MW'] > 0:
        # BOS of Wind only power plant:
        print('Wind BOS: ', (wind_BOS['total_bos_cost'] /
                             (hybrids_input_dict['wind_plant_size_MW'] * 1e6)))
    else:
        wind_BOS['total_management_cost'] = 0

    if hybrids_input_dict['solar_system_size_MW_DC'] > 0:
        # BOS of Solar only power plant:
        print('Solar BOS: ', (solar_BOS['total_bos_cost'] /
                              (hybrids_input_dict['solar_system_size_MW_DC'] * 1e6)))
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


yaml_file_path = dict()

# Some preset scenarios:
#
# hybrid_inputs_7.5_7.5_7.5
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Hybrids_BOS_model/' \
#                                     'yaml_inputs/hybrid_inputs_7.5_7.5_7.5.yaml'

# hybrid_inputs_7.5_7.5_15
yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Hybrids_BOS_model/' \
                                    'yaml_inputs/hybrid_inputs_7.5_7.5_15.yaml'

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


def display_results(size_MW, hybrid_dict, wind_only_dict, solar_only_dict):

    hybrid_size_MW = size_MW * 2

    hybrids_df = pd.DataFrame(hybrid_dict['hybrid'].items(), columns=['BOS Component',
                                                                      'USD/Watt'])

    hybrids_df.insert(0, "Project Rating (MW)", hybrid_size_MW, True)
    hybrids_df.insert(3, "Technology", "Hybrid", True)
    hybrids_df.insert(4, "Sub Technology", "Shared-Hybrid", True)

    hybrids_solar_df = pd.DataFrame(
        hybrid_dict['Solar_BOS_results'].items(), columns=['BOS Component', 'USD/Watt'])
    hybrids_solar_df.insert(0, "Project Rating (MW)", hybrid_size_MW, True)
    hybrids_solar_df.insert(3, "Technology", "Hybrid", True)
    hybrids_solar_df.insert(4, "Sub Technology", "Solar-Hybrid", True)

    hybrids_wind_df = pd.DataFrame(
        hybrid_dict['Wind_BOS_results'].items(), columns=['BOS Component', 'USD/Watt'])
    hybrids_wind_df.insert(0, "Project Rating (MW)", hybrid_size_MW, True)
    hybrids_wind_df.insert(3, "Technology", "Hybrid", True)
    hybrids_wind_df.insert(4, "Sub Technology", "Wind-Hybrid", True)

    hybrids_df = hybrids_df.append(hybrids_solar_df, ignore_index=True)
    hybrids_df = hybrids_df.append(hybrids_wind_df, ignore_index=True)

    solar_only_bos = dict()
    solar_only_bos['gridconnection_usd'] = solar_only_dict['total_gridconnection_cost']
    solar_only_bos['substation_cost'] = solar_only_dict['substation_cost']
    solar_only_bos['total_management_cost'] = solar_only_dict['total_management_cost']

    solar_only_bos_df = pd.DataFrame(
        solar_only_dict.items(), columns=['BOS Component',
                                          'USD/Watt'])
    solar_only_bos_df.insert(0, "Project Rating (MW)", size_MW, True)
    solar_only_bos_df.insert(3, "Technology", "Solar", True)
    solar_only_bos_df.insert(4, "Sub Technology", "Solar Only", True)

    wind_only_bos = dict()
    wind_only_bos['total_gridconnection_cost'] = wind_only_dict['total_gridconnection_cost']
    wind_only_bos['total_substation_cost'] = wind_only_dict['total_substation_cost']
    wind_only_bos['total_management_cost'] = wind_only_dict['total_management_cost']
    wind_only_bos_df = pd.DataFrame(
        wind_only_dict.items(), columns=['BOS Component',
                                         'USD/Watt'])
    wind_only_bos_df.insert(0, "Project Rating (MW)", size_MW, True)
    wind_only_bos_df.insert(3, "Technology", "Wind", True)
    wind_only_bos_df.insert(4, "Sub Technology", "Wind Only", True)

    #
    # print(hybrids_df)
    # print(solar_only_bos_df)
    # print(wind_only_bos_df)

    return hybrids_df, solar_only_bos_df, wind_only_bos_df


# size = 5
# min_size = size
# max_size = 10
#
grid_size_multiplier = 0.5
max_grid = 1
#
# x = np.arange(size, (max_size + 2.5), 2.5)
# solar_only_BOS_results = dict()
# wind_only_BOS_results = dict()
# hybrid_BOS_results = dict()
#
# hybrid_csv = pd.DataFrame()
# solar_csv = pd.DataFrame()
# wind_csv = pd.DataFrame()

# hybrid_csv = pd.DataFrame(columns=['Project Rating (MW)', 'BOS Component', 'USD'])
# solar_csv = pd.DataFrame(columns=['Project Rating (MW)', 'BOS Component', 'USD'])
# wind_csv = pd.DataFrame(columns=['Project Rating (MW)', 'BOS Component', 'USD'])
hybrids_scenario_dict = dict()

while grid_size_multiplier <= max_grid:
    size = 5
    min_size = size
    max_size = 500

    x = np.arange(size, (max_size + 2.5), 2.5)
    solar_only_BOS_results = dict()
    wind_only_BOS_results = dict()
    hybrid_BOS_results = dict()

    hybrid_csv = pd.DataFrame()
    solar_csv = pd.DataFrame()
    wind_csv = pd.DataFrame()
    print('grid rating: ', grid_size_multiplier)
    while size <= max_size:

        override_dict = dict()
        # LandBOSSE Crane Breakpoint:
        if size >= 50:
            override_dict['breakpoint_between_base_and_topping_percent'] = 0.38888889
        else:
            override_dict['breakpoint_between_base_and_topping_percent'] = 0

        # LandBOSSE Road Length adder, number of access roads, and number of highway permits:
        if size < 20 :
            override_dict['road_length_adder_m'] = 0
            override_dict['num_hwy_permits'] = 0
            override_dict['num_access_roads'] = 0
        elif size >= 20 and  size < 50:
            override_dict['road_length_adder_m'] = 1000
            override_dict['num_hwy_permits'] = 2
            override_dict['num_access_roads'] = 2
        elif size >= 50 and size < 100:
            override_dict['road_length_adder_m'] = 2135.4
            override_dict['num_hwy_permits'] = 4
            override_dict['num_access_roads'] = 2
        elif size >= 100 and size < 150:
            override_dict['road_length_adder_m'] = 2812.5
            override_dict['num_hwy_permits'] = 8
            override_dict['num_access_roads'] = 2
        elif size >= 150 and size < 200:
            override_dict['road_length_adder_m'] = 3489.6
            override_dict['num_hwy_permits'] = 12
            override_dict['num_access_roads'] = 2
        elif size >= 200 and size < 400:
            override_dict['road_length_adder_m'] = 4166.70
            override_dict['num_hwy_permits'] = 16
            override_dict['num_access_roads'] = 2
        elif size >= 400 and size < 1000 :
            override_dict['road_length_adder_m'] = 6875.10
            override_dict['num_hwy_permits'] = 32
            override_dict['num_access_roads'] = 3
        elif size >= 1000:
            override_dict['road_length_adder_m'] = 15000.30
            override_dict['num_hwy_permits'] = 80
            override_dict['num_access_roads'] = 6

            # Grid Connection, and Substation rating
        grid_size = size * grid_size_multiplier * 2
        override_dict['grid_interconnection_rating_MW'] = grid_size
        if grid_size > 15:
            # Used in 2020 run and based on PV Benchmark Study of 2018
            # override_dict['distance_to_interconnect_mi'] = (0.0263 * grid_size) - 0.2632
            # Used in 2021 run and based on LandBOSSE cost and scaling study
            override_dict['distance_to_interconnect_mi'] = (0.0097 * grid_size) + 0.429
        else:
            override_dict['distance_to_interconnect_mi'] = 0

        if grid_size < 20:
            override_dict['interconnect_voltage_kV'] = 15
        elif 20 <= grid_size < 40:
            override_dict['interconnect_voltage_kV'] = 34.5
        elif 40 <= grid_size < 75:
            override_dict['interconnect_voltage_kV'] = 69       # should be 69
        elif grid_size >= 75:
            override_dict['interconnect_voltage_kV'] = 138      # should be 138

        override_dict['hybrid_substation_rating_MW'] = grid_size

        override_dict['num_turbines'] = size / 2.5
        override_dict['solar_system_size_MW_DC'] = size
        override_dict['wind_plant_size_MW'] = size
        override_dict['wind_construction_time_months'] = ((0.2745 * size) + 2.8235) * 2
        override_dict['solar_construction_time_months'] = ((0.2745 * size) + 2.8235) * 2

        # Assign override_dict to hybrids_scenario_dict:
        hybrids_scenario_dict = read_hybrid_scenario(yaml_file_path)
        print(yaml_file_path)

        # project list file for utility scale
        if size > 15:
            hybrids_scenario_dict['name_of_project_list'] = 'project_list_hybrid_baseline'
        else:
            hybrids_scenario_dict[
                'override_total_management_cost'] = (191304 * size) + 1000000

        hybrids_scenario_dict['development_labor_cost_usd'] = 17000 * size
        hybrids_scenario_dict['hybrid_plant_size_MW'] = override_dict['wind_plant_size_MW'] + \
                                                        override_dict['solar_system_size_MW_DC']

        hybrids_scenario_dict['wind_construction_time_months'] = \
                                        override_dict['wind_construction_time_months']

        hybrids_scenario_dict['solar_construction_time_months'] = \
                                        override_dict['solar_construction_time_months']

        hybrids_scenario_dict['hybrid_construction_months'] = \
            hybrids_scenario_dict['wind_construction_time_months'] + \
            hybrids_scenario_dict['solar_construction_time_months']

        hybrids_scenario_dict['grid_interconnection_rating_MW'] = \
                                            override_dict['grid_interconnection_rating_MW']

        hybrids_scenario_dict['wind_dist_interconnect_mi'] = override_dict['distance_to_interconnect_mi']
        hybrids_scenario_dict['solar_dist_interconnect_mi'] = override_dict['distance_to_interconnect_mi']
        hybrids_scenario_dict['distance_to_interconnect_mi'] = override_dict['distance_to_interconnect_mi']

        hybrids_scenario_dict['hybrid_substation_rating_MW'] = override_dict['hybrid_substation_rating_MW']

        hybrids_scenario_dict['interconnect_voltage_kV'] = override_dict['interconnect_voltage_kV']

        hybrids_scenario_dict['num_turbines'] = override_dict['num_turbines']
        hybrids_scenario_dict['solar_system_size_MW_DC'] = override_dict['solar_system_size_MW_DC']
        hybrids_scenario_dict['wind_plant_size_MW'] = override_dict['wind_plant_size_MW']
        hybrids_scenario_dict['breakpoint_between_base_and_topping_percent'] = \
            override_dict['breakpoint_between_base_and_topping_percent']
        hybrids_scenario_dict['num_hwy_permits'] = override_dict['num_hwy_permits']
        hybrids_scenario_dict['num_access_roads'] = override_dict['num_access_roads']
        hybrids_scenario_dict['road_length_adder_m'] = override_dict['road_length_adder_m']

        hybrid_results, wind_only, solar_only = run_hybrid_BOS(hybrids_scenario_dict)
        # print(hybrid_results)
        hybrid_df, solar_df, wind_df = display_results(size,
                                                       hybrid_results,
                                                       wind_only_dict=wind_only,
                                                       solar_only_dict=solar_only)

        hybrid_csv = hybrid_csv.append(hybrid_df)
        solar_csv = solar_csv.append(solar_df)
        wind_csv = wind_csv.append(wind_df)

        hybrid_BOS_results[str(size)] = hybrid_results['hybrid']['hybrid_BOS_usd_watt']
        wind_only_BOS_results[str(size)] = wind_only['total_bos_cost'] / (size * 1e6)
        solar_only_BOS_results[str(size)] = solar_only['total_bos_cost'] / (size * 1e6)

        size += 2.5  # 2.5 because turbine rating is 2.5 MW

    # print(hybrid_BOS_results)
    # print(wind_only_BOS_results)
    # print(solar_only_BOS_results)
    path = '/Users/pbhaskar/Desktop/Projects/Hybrids_BOS_model/outputs/'
    hybrid_csv.to_csv(path + 'hybrids_' + str(100*grid_size_multiplier) + '_percent_grid.csv', index=False)
    solar_csv.to_csv(path + 'solar_' + str(100*grid_size_multiplier) + '_percent_grid.csv', index=False)
    wind_csv.to_csv(path + 'wind_' + str(100*grid_size_multiplier) + '_percent_grid.csv', index=False)

    writer = pd.ExcelWriter(path + 'BOS_results_' + str(100*grid_size_multiplier) + '_percent_grid.xlsx',
                            engine='xlsxwriter',
                            options={'strings_to_numbers': True})

    df = pd.read_csv(path + 'hybrids_' + str(100*grid_size_multiplier) + '_percent_grid.csv')
    df.to_excel(writer, sheet_name='hybrids', index=False)

    df = pd.read_csv(path + 'solar_' + str(100*grid_size_multiplier) + '_percent_grid.csv')
    df.to_excel(writer, sheet_name='solar', index=False)

    df = pd.read_csv(path + 'wind_' + str(100*grid_size_multiplier) + '_percent_grid.csv')
    df.to_excel(writer, sheet_name='wind', index=False)

    writer.save()

    # hybrid_y = np.asarray(list(hybrid_BOS_results.values()))
    # wind_y = np.asarray(list(wind_only_BOS_results.values()))
    # solar_y = np.asarray(list(solar_only_BOS_results.values()))
    #
    # plt.plot(x, hybrid_y, '-g', label='Hybrid BOS CAPEX - Interconnection Rating = Project Rating '
    #                                   '($/Watt)')
    #
    # plt.plot(x, wind_y, '-b', label='Wind Only BOS CAPEX ($/Watt)')
    # plt.plot(x, solar_y, '#FF4500', label='Solar Only BOS CAPEX ($/Watt)')
    # plt.ylabel('$/Watt')
    # plt.xlabel('Project Rating (MW)')
    # # plt.xticks(np.arange(min_size, max_size+1, 1), rotation=70)
    # plt.legend()
    # # plt.legend(loc='upper center', bbox_to_anchor=(1, 0), ncol=3)
    # plt.show()
    #
    # width = 3.5
    # plt.bar(x, wind_y, width)
    # plt.show()
    grid_size_multiplier += 0.1
