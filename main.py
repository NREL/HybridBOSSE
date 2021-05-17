import yaml
import os
from bin.run_BOSSEs import run_BOSSEs
from bin.PostSimulationProcessing import PostSimulationProcessing
from bin.CollectionCost import get_hybrid_collection_cost_matrix, get_wind_adj_matrix
import pandas as pd
import sys
from excelio.XlsxDataframeCache import XlsxDataframeCache


# Main API method to run a Hybrid BOS model:
def run_hybrid_BOS(hybrids_input_dict):
    """
    Returns a dictionary with detailed Shared Infrastructure BOS results.
    """

    wind_BOS, solar_BOS, storage_BOS = run_BOSSEs(hybrids_input_dict)
    # Store a copy of both solar only and wind only outputs dictionaries:
    wind_only_BOS = wind_BOS.copy()
    solar_only_BOS = solar_BOS.copy()
    storage_only_BOS = storage_BOS.copy()

    print('wind_only_BOS at ', hybrids_input_dict['wind_plant_size_MW'], ' MW: ' , wind_BOS)
    print('solar_only_BOS ', hybrids_input_dict['solar_system_size_MW_DC'], ' MW: ' , solar_BOS)
    print('storage_only_BOS at ', hybrids_input_dict['storage_system_size_MW_DC'], ' MW and ',
          hybrids_input_dict['storage_system_size_MWh'], ' MWh', storage_BOS)

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

    if hybrids_input_dict['storage_system_size_MW_DC'] > 0:
        # BOS of Storage only power plant:
        print('Storage BOS: ', (storage_BOS['total_bos_cost'] /
                                (hybrids_input_dict['storage_system_size_MW_DC'] * 1e6)))
    else:
        storage_BOS['total_management_cost'] = 0

    results = dict()
    results['hybrid'] = dict()
    hybrid_BOS = PostSimulationProcessing(hybrids_input_dict, wind_BOS, solar_BOS, storage_BOS)
    results['hybrid']['hybrid_BOS_usd'] = hybrid_BOS.hybrid_BOS_usd
    results['hybrid']['hybrid_BOS_usd_watt'] = hybrid_BOS.hybrid_BOS_usd_watt
    results['hybrid']['hybrid_gridconnection_usd'] = hybrid_BOS.hybrid_gridconnection_usd
    results['hybrid']['hybrid_substation_usd'] = hybrid_BOS.hybrid_substation_usd
    results['hybrid']['hybrid_collection_cost_usd'] = hybrid_BOS.hybrid_collection_cost_usd
    results['hybrid']['hybrid_management_development_usd'] = wind_BOS['total_management_cost'] + \
                                                             solar_BOS['total_management_cost'] + \
                                                             storage_BOS['total_management_cost'] + \
                                                             hybrid_BOS.site_facility_usd

    results['Wind_BOS_results'] = hybrid_BOS.update_BOS_dict(wind_BOS, 'wind')
    results['Solar_BOS_results'] = hybrid_BOS.update_BOS_dict(solar_BOS, 'solar')
    results['Storage_BOS_results'] = hybrid_BOS.update_BOS_dict(storage_BOS, 'storage')
    return results, wind_only_BOS, solar_only_BOS, storage_only_BOS


def read_hybrid_scenario(file_path):
    """
    [Optional method]

    Reads in default hybrid_inputs.yaml (YAML file) shipped with
    bin, and returns a python dictionary with all required
    key:value pairs needed to run the bin API.
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

    hybrids_scenario_dict['path_to_project_list'] = hybrids_scenario_dict['path_to_project_list']
#    hybrids_scenario_dict['path_to_project_list'] = os.path.abspath(os.path.dirname(__file__))
    hybrids_scenario_dict['path_to_storage_project_list'] = os.path.join(os.path.abspath(os.path.dirname(__file__))
                                                                         , 'StorageBOSSE')

    return hybrids_scenario_dict


yaml_file_path = dict()

# Some preset scenarios:
#
# hybrid_inputs_7.5_7.5_7.5
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_7.5_7.5_7.5.yaml'


def read_hybrid_input_sheet(hybrid_input_dict):
    """
    Reads the hybrid collection layout xlsx sheet
    and adds inputs into the hybrid_input_dict
    """
    file_name = 'project_data_defaults.xlsx'
    project_full_path = os.path.abspath(file_name)
    project_full_path = os.path.join(project_full_path, '..')
    if 'collection_layout_file_name' in hybrid_input_dict and 'collection_layout_path' in hybrid_input_dict:
        file_name = hybrid_input_dict['collection_layout_file_name']
        path = hybrid_input_dict['collection_layout_path']
        project_full_path = os.path.join(path, file_name)
    # Check if # of turbines and # of solar and storage are correct
    project_data_sheets = \
        XlsxDataframeCache.read_all_sheets_from_xlsx(project_full_path)

    hybrid_input_dict['cable_specs_pd_ac'] = project_data_sheets['cable_specs_ac']
    hybrid_input_dict['cable_specs_pd_dc'] = project_data_sheets['cable_specs_dc']
    hybrid_input_dict['rsmeans'] = project_data_sheets['rsmeans']
    hybrid_input_dict['equip'] = project_data_sheets['equip']
    hybrid_input_dict['equip_price'] = project_data_sheets['equip_price']
    hybrid_input_dict['material_price'] = project_data_sheets['material_price']
    hybrid_input_dict['site_facility_building_area'] = project_data_sheets['site_facility_building_area']
    crew_cost = project_data_sheets['crew_price']
    crew_cost = crew_cost.set_index("Labor type ID", drop=False)
    hybrid_input_dict['rsmeans_per_diem'] = crew_cost.loc['RSMeans', 'Per diem USD per day']
    hybrid_input_dict['crane_specs'] = project_data_sheets['crane_specs']
    hybrid_input_dict['development'] = project_data_sheets['development']
    hybrid_input_dict['crane_specs'] = project_data_sheets['crane_specs']
    hybrid_input_dict['crew_cost'] = project_data_sheets['crew_price']
    hybrid_input_dict['crew'] = project_data_sheets['crew']
    project_input_dict = project_data_sheets['project_list']
    hybrid_input_dict['project_input_dict'] = project_input_dict

    hybrid_input_dict['season_construct'] = ['spring', 'summer', 'fall']
    hybrid_input_dict['time_construct'] = 'normal'
    hybrid_input_dict['hour_day'] = {'long': 24, 'normal': 10}
    hybrid_input_dict['operational_construction_time'] = hybrid_input_dict['hour_day'][
        hybrid_input_dict['time_construct']]

#    hybrids_scenario_dict['path_to_project_list'] = project_input_dict['path_to_project_list']
#        hybrids_scenario_dict['path_to_project_list'] = '/Users/ccampos/Desktop/hybrid_manual_inputs/project_data'
    hybrid_input_dict['fuel_cost'] = project_input_dict['Fuel cost USD per gal']
    hybrid_input_dict['weather_window'] = project_data_sheets['weather_window']
    if hybrid_input_dict['shared_collection_system']:
        hybrid_input_dict['collection_layout'] = project_data_sheets['collection_layout']
        landBOSSE_adjacency_matrix, xcoordinates, ycoordinates, subx, suby = get_wind_adj_matrix(hybrid_input_dict)
        landBOSSE_adjacency_matrix.insert(0, ycoordinates)
        landBOSSE_adjacency_matrix.insert(0, xcoordinates)
        hybrid_input_dict['wind_collection_layout'] = pd.DataFrame(data=landBOSSE_adjacency_matrix)
        adj, x, y, types, xsub, ysub = get_hybrid_collection_cost_matrix(hybrid_input_dict, subx, suby)
        hybrid_input_dict['adj_layout'] = adj
        hybrid_input_dict['x_coordinate_layout'] = x
        hybrid_input_dict['y_coordinate_layout'] = y
        hybrid_input_dict['sub_loc'] = (xsub, ysub)
        hybrid_input_dict['type_layout'] = types

    return hybrid_input_dict
    #Get wind collection layout and pass through land_BOSSE



def display_results(hybrid_dict, wind_only_dict, solar_only_dict, storage_only_dict):

    hybrids_df = pd.DataFrame(hybrid_dict['hybrid'].items(), columns=['Type', 'USD'])

    hybrids_solar_df = pd.DataFrame(
        hybrid_dict['Solar_BOS_results'].items(), columns=['Type', 'USD'])

    hybrids_wind_df = pd.DataFrame(
        hybrid_dict['Wind_BOS_results'].items(), columns=['Type', 'USD'])

    hybrids_storage_df = pd.DataFrame(
        hybrid_dict['Storage_BOS_results'].items(), columns=['Type', 'USD'])

    solar_only_bos = dict()
    solar_only_bos['gridconnection_usd'] = solar_only_dict['total_transdist_cost']
    solar_only_bos['substation_cost'] = solar_only_dict['substation_cost']
    solar_only_bos['total_management_cost'] = solar_only_dict['total_management_cost']

    solar_only_bos_df = pd.DataFrame(
        solar_only_bos.items(), columns=['Solar Only BOS Component', 'USD'])

    wind_only_bos = dict()
    wind_only_bos['total_gridconnection_cost'] = wind_only_dict['total_gridconnection_cost']
    wind_only_bos['total_substation_cost'] = wind_only_dict['total_substation_cost']
    wind_only_bos['total_management_cost'] = wind_only_dict['total_management_cost']
    wind_only_bos_df = pd.DataFrame(
        wind_only_bos.items(), columns=['Wind Only BOS Component', 'USD'])

    storage_only_bos = dict()
    storage_only_bos['gridconnection_usd'] = storage_only_dict['total_transdist_cost']
    storage_only_bos['substation_cost'] = storage_only_dict['substation_cost']
    storage_only_bos['total_management_cost'] = storage_only_dict['total_management_cost']

    storage_only_bos_df = pd.DataFrame(
        storage_only_bos.items(), columns=['Storage Only BOS Component', 'USD'])

    print(hybrids_df)
    print(solar_only_bos_df)
    print(wind_only_bos_df)
    print(storage_only_bos_df)

    return hybrids_df, hybrids_solar_df, hybrids_wind_df, hybrids_storage_df, solar_only_bos, wind_only_bos,\
           storage_only_bos

if __name__ == '__main__':

    #Add Some Paths
    path = os.path.abspath(os.path.dirname(__file__))
    parent_path = os.path.abspath(os.path.join(path, ".."))
    sys.path.append(parent_path)
    sys.path.append("..")
    sys.path.append(".")
    results_r = dict()
    plant_power = [100, 300, 500, 600, 700, 900, 1100]
    for power in plant_power:
        wind_power = 0.4*power # 40 percent
        solar_power = 0.4*power # 40 percent
        storage_power = 0.2*power # 20 percent
        #Create the hybrid_scenario_dict from a yaml file
        hybrids_scenario_dict = read_hybrid_scenario(yaml_file_path)
        hybrids_scenario_dict = read_hybrid_input_sheet(hybrids_scenario_dict)
        # Create hybrid_scenario_dict manually
        #hybrids_scenario_dict = dict()
        # hybrids_scenario_dict = {
        #         "project_name": 'Hybrid_BOSSE',
        #         "project_mode": 2,
        #         "shared_interconnection": True,
        #         "shared_collection_system": True,
        #         "distance_to_interconnect_mi": 1.5,
        #         "line_frequency_hz": 60,
        #         "collection_layout_file_name": 'project_data_defaults',
        #         "collection_layout_path": '/Users/ccampos/Desktop/'
        #         'hybrid_manual_inputs/project_data',
        #         "new_switchyard": True,
        #         "grid_interconnection_rating_MW": 7.5,
        #         "interconnect_voltage_kV": 15,
        #         "shared_substation": True,
        #         "hybrid_substation_rating_MW": 7.5,
        #         "wind_dist_interconnect_mi": 0,
        #         "num_turbines": 5,
        #         "turbine_rating_MW": 1.5,
        #         "wind_construction_time_months": 5,
        #         "project_id": "ge15_public_dist",
        #         "path_to_project_list": "/Users/abarker/Desktop/Hybrid Model/Code/bin",
        #         "name_of_project_list": "project_list_ge15_dist_05",
        #         "solar_system_size_MW_DC": 100,
        #         "dc_ac_ratio": 1.2,
        #         "solar_construction_time_months": 5,
        #         "solar_dist_interconnect_mi": 5,
        #         "storage_system_size_MW_DC": 50,
        #         "storage_system_size_MWh": 5,
        #         "storage_construction_time_months":5,
        #         "path_to_storage_project_list": "/Users/abarker/Desktop/Hybrid Model/Code/bin/StorageBOSSE/project_list_test.xlsx",
        #         "storage_project_list": "project_list_test"
        #
        # }
        #Set custom HybridBOSSE parameters
        # wind_size = 150
        # hybrids_scenario_dict['wind_plant_size_MW'] = wind_size
        hybrids_scenario_dict['wind_plant_size_MW'] = wind_power
        hybrids_scenario_dict['wind_plant_size_MW'] = hybrids_scenario_dict['turbine_rating_MW'] \
                                                      * hybrids_scenario_dict['num_turbines']
        hybrids_scenario_dict['solar_system_size_MW_DC'] = solar_power
        hybrids_scenario_dict['storage_system_size_MW_DC'] = storage_power
        hybrids_scenario_dict['shared_collection_system'] = False
        hybrids_scenario_dict["grid_interconnection_rating_MW"] = wind_power
        hybrids_scenario_dict['hybrid_plant_size_MW'] = wind_power + storage_power + solar_power
        hybrids_scenario_dict["hybrid_substation_rating_MW"] = wind_power + storage_power + solar_power
        hybrids_scenario_dict["hybrid_construction_months"] = wind_power
        hybrids_scenario_dict["interconnect_voltage_kV"] = 15

        if hybrids_scenario_dict['num_turbines'] is None or hybrids_scenario_dict['num_turbines'] == 0:
            hybrids_scenario_dict['num_turbines'] = 0

        hybrids_scenario_dict['wind_plant_size_MW'] = hybrids_scenario_dict['num_turbines'] * \
                                                      hybrids_scenario_dict['turbine_rating_MW']


        hybrids_scenario_dict['hybrid_construction_months'] = \
            hybrids_scenario_dict['wind_construction_time_months'] + \
            hybrids_scenario_dict['solar_construction_time_months']

        hybrids_scenario_dict['path_to_project_list'] = os.path.abspath(os.path.dirname(__file__))
        hybrids_scenario_dict['path_to_storage_project_list'] = os.path.join(os.path.abspath(os.path.dirname(__file__))
                                                                          , 'StorageBOSSE')
        #Setting inteconnect sizes based on project size
        grid_size_multiplier = 1
        grid_size = wind_power #* grid_size_multiplier * 2
        if grid_size > 15:
            hybrids_scenario_dict['distance_to_interconnect_mi'] = (0.0263 * grid_size) - 0.2632
        else:
            hybrids_scenario_dict['distance_to_interconnect_mi'] = 0
        if grid_size < 20:
            hybrids_scenario_dict['interconnect_voltage_kV'] = 15
        elif 20 < grid_size < 40:
            hybrids_scenario_dict['interconnect_voltage_kV'] = 34.5
        elif 40 <= grid_size < 75:
            hybrids_scenario_dict['interconnect_voltage_kV'] = 69  # should be 69
        elif grid_size >= 75:
            hybrids_scenario_dict['interconnect_voltage_kV'] = 138  # should be 138

        hybrid_results, wind_only, solar_only, storage_only = run_hybrid_BOS(hybrids_scenario_dict)

    print(hybrid_results)
    print("<++++++++ HYBRID RESULTS++++++++>")
    print(hybrid_results['Wind_BOS_results'])
    print(hybrid_results['Solar_BOS_results'])
    print(hybrid_results['Storage_BOS_results'])
    print(hybrid_results['hybrid'])

