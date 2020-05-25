import yaml
import os
from hybrids_shared_infrastructure.run_BOSSEs import run_BOSSEs
from hybrids_shared_infrastructure.PostSimulationProcessing import PostSimulationProcessing


# Main API method to run a Hybrid BOS model:
def run_hybrid_BOS(hybrids_input_dict):
    """
    Returns a dictionary with detailed Shared Infrastructure BOS results.
    """
    wind_BOS, solar_BOS = run_BOSSEs(hybrids_input_dict)
    print('wind_BOS ', wind_BOS)
    print('solar_BOS ', solar_BOS)
    if hybrids_scenario_dict['wind_plant_size_MW'] > 0:
        # BOS of Wind only power plant:
        print('Wind BOS: ', (wind_BOS['total_bos_cost'] /
                             (hybrids_scenario_dict['wind_plant_size_MW'] * 1e6)))
    if hybrids_scenario_dict['solar_system_size_MW_DC'] > 0:
        # BOS of Solar only power plant:
        print('Solar BOS: ', (solar_BOS['total_bos_cost'] /
                              (hybrids_scenario_dict['solar_system_size_MW_DC'] * 1e6)))
    results = dict()
    hybrid_BOS = PostSimulationProcessing(hybrids_input_dict, wind_BOS, solar_BOS)
    results['hybrid_BOS_usd'] = hybrid_BOS.hybrid_BOS_usd
    results['hybrid_BOS_usd_watt'] = hybrid_BOS.hybrid_BOS_usd_watt
    results['hybrid_gridconnection_usd'] = hybrid_BOS.hybrid_gridconnection_usd
    results['hybrid_substation_usd'] = hybrid_BOS.hybrid_substation_usd

    results['hybrid_management_development_usd'] = wind_BOS['total_management_cost'] + \
                                                   solar_BOS['total_management_cost']

    results['Wind_BOS_results'] = hybrid_BOS.update_BOS_dict(wind_BOS, 'wind')
    results['Solar_BOS_results'] = hybrid_BOS.update_BOS_dict(solar_BOS, 'solar')
    return results


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
    hybrids_scenario_dict['wind_plant_size_MW'] = hybrids_scenario_dict['num_turbines'] * \
                                                  hybrids_scenario_dict['turbine_rating_MW']

    hybrids_scenario_dict['hybrid_plant_size_MW'] = hybrids_scenario_dict['wind_plant_size_MW'] + \
                                                    hybrids_scenario_dict['solar_system_size_MW_DC']
    return hybrids_scenario_dict


yaml_file_path = dict()

# Some preset scenarios:
#
# hybrid_inputs_5_wind+5_solar_5_intereconnect
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_5+5_5.yaml'

# hybrid_inputs_0+10_5
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_0+10_5.yaml'


# hybrid_inputs_5+5_10
# yaml_file_path['input_file_path'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
#                                     'Infrastructure/hybrids_shared_infra_tool/shared_' \
#                                     'infra_in_out_scenarios/hybrid_inputs_5+5_10.yaml'

hybrids_scenario_dict = read_hybrid_scenario(yaml_file_path)
outputs = run_hybrid_BOS(hybrids_scenario_dict)
print(outputs)
