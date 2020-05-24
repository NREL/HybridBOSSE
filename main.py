import yaml
import os
from hybrids_shared_infrastructure.run_BOSSEs import run_BOSSEs
from hybrids_shared_infrastructure.PostSimulationProcessing import PostSimulationProcessing


# Main API method to run a Hybrid BOS model:
def run_hybrid_BOS(hybrids_input_dict):
    wind_BOS, solar_BOS = run_BOSSEs(hybrids_input_dict)
    print('Wind BOS: ', wind_BOS)
    print('Solar BOS: ', solar_BOS)

    results = dict()
    hybrid_BOS = PostSimulationProcessing(hybrids_input_dict, wind_BOS, solar_BOS)
    results['hybrid_BOS_usd'] = hybrid_BOS.hybrid_BOS_usd()
    return results


def read_hybrid_scenario():
    """
    [Optional method]

    Reads in default hybrid_inputs.yaml (YAML file) shipped with
    hybrids_shared_infrastructure, and returns a python dictionary with all required
    key:value pairs needed to run the hybrids_shared_infrastructure API.
    """
    input_file_path = os.path.dirname(__file__)
    with open(input_file_path + '/hybrid_inputs.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)

    hybrids_scenario_dict = data_loaded['hybrids_input_dict']
    hybrids_scenario_dict['wind_plant_size_MW'] = hybrids_scenario_dict['num_turbines'] * \
                                                  hybrids_scenario_dict['turbine_rating_MW']
    return hybrids_scenario_dict


hybrids_scenario_dict = read_hybrid_scenario()
run_hybrid_BOS(hybrids_scenario_dict)
