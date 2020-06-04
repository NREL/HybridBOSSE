import yaml
import os
from hybrids_shared_infrastructure.run_BOSSEs import run_BOSSEs
from hybrids_shared_infrastructure.PostSimulationProcessing import PostSimulationProcessing
import pandas as pd

# Main API method to run a Hybrid BOS model:
def run_hybrid_BOS(hybrids_input_dict):
    """
    Returns a dictionary with detailed Shared Infrastructure BOS results.
    """
    wind_BOS, solar_BOS = run_BOSSEs(hybrids_input_dict)
    wind_only_bos, solar_only_bos = wind_BOS, solar_BOS
    print('wind_only_BOS at ', hybrids_scenario_dict['wind_plant_size_MW'], ' MW: ' , wind_BOS)
    print('solar_only_BOS ', hybrids_scenario_dict['solar_system_size_MW_DC'], ' MW: ' , solar_BOS)
    if hybrids_scenario_dict['wind_plant_size_MW'] > 0:
        # BOS of Wind only power plant:
        print('Wind BOS: ', (wind_BOS['total_bos_cost'] /
                             (hybrids_scenario_dict['wind_plant_size_MW'] * 1e6)))
    else:
        wind_BOS['total_management_cost'] = 0

    if hybrids_scenario_dict['solar_system_size_MW_DC'] > 0:
        # BOS of Solar only power plant:
        print('Solar BOS: ', (solar_BOS['total_bos_cost'] /
                              (hybrids_scenario_dict['solar_system_size_MW_DC'] * 1e6)))
    else:
        solar_BOS['total_management_cost'] = 0

    results = dict()
    hybrid_BOS = PostSimulationProcessing(hybrids_input_dict, wind_BOS, solar_BOS)
    results['Hybrid_BOS_results'] = dict()
    results['Hybrid_BOS_results']['hybrid_BOS_usd'] = hybrid_BOS.hybrid_BOS_usd
    results['Hybrid_BOS_results']['hybrid_BOS_usd_watt'] = hybrid_BOS.hybrid_BOS_usd_watt
    results['Hybrid_BOS_results']['hybrid_gridconnection_usd'] = hybrid_BOS.hybrid_gridconnection_usd
    results['Hybrid_BOS_results']['hybrid_substation_usd'] = hybrid_BOS.hybrid_substation_usd

    results['Hybrid_BOS_results']['hybrid_management_development_usd'] = wind_BOS['total_management_cost'] + \
                                                   solar_BOS['total_management_cost'] + \
                                                   hybrid_BOS.site_facility_usd


    results['Wind_BOS_results'] = hybrid_BOS.update_BOS_dict(wind_BOS, 'wind')
    results['Solar_BOS_results'] = hybrid_BOS.update_BOS_dict(solar_BOS, 'solar')
    return wind_only_bos, solar_only_bos, results


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
yaml_file_path['input_file_path'] = '/Users/abarker/Desktop/Hybrid Model/Code/' \
                                    'hybrids_shared_infrastructure/hybrid_inputs.yaml'
output_dir = '/Users/abarker/Desktop/Hybrid Model/Code/' \
                                    'hybrids_shared_infrastructure/results'

hybrids_scenario_dict = read_hybrid_scenario(yaml_file_path)
wind_only_bos, solar_only_bos, outputs = run_hybrid_BOS(hybrids_scenario_dict)


outputs_df_wind_only = pd.DataFrame.from_dict(wind_only_bos.items())
outputs_df_solar_only = pd.DataFrame.from_dict(solar_only_bos.items())
outputs_df_wind_hybrid = pd.DataFrame.from_dict(outputs['Wind_BOS_results'])
outputs_df_solar_hybrid = pd.DataFrame.from_dict(outputs['Solar_BOS_results'])
outputs_df_hybrid = pd.DataFrame.from_dict(outputs['Hybrid_BOS_results'].items())
outputs_df = pd.DataFrame.from_dict(outputs)

outputs_df_wind_only.to_csv(os.path.join(output_dir, 'Wind Only.csv'))
outputs_df_solar_only.to_csv(os.path.join(output_dir, 'Solar Only.csv'))
outputs_df_wind_hybrid.to_csv(os.path.join(output_dir, 'Wind (Hybrid).csv'))
outputs_df_solar_hybrid.to_csv(os.path.join(output_dir, 'Solar (Hybrid).csv'))
outputs_df_hybrid.to_csv(os.path.join(output_dir, 'Hybrid.csv'))


print(outputs)
