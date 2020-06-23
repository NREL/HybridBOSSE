from LandBOSSE.landbosse.landbosse_api.run import run_landbosse
from SolarBOSSE.main import run_solarbosse
from hybrids_shared_infrastructure.GridConnectionCost import hybrid_gridconnection
from StorageBOSSE.main import run_storagebosse


def run_BOSSEs(hybrids_input_dict):
    """
    Runs 1) LandBOSSE, and 2) SolarBOSSE as mutually exclusive BOS models.

    """
    # <><><><><><><><><><><><><><><> RUNNING LandBOSSE API <><><><><><><><><><><><><><><><>
    wind_input_dict = dict()
    wind_input_dict['num_turbines'] = hybrids_input_dict['num_turbines']
    wind_input_dict['turbine_rating_MW'] = hybrids_input_dict['turbine_rating_MW']

    wind_input_dict['interconnect_voltage_kV'] =    \
                                            hybrids_input_dict['interconnect_voltage_kV']

    wind_input_dict['distance_to_interconnect_mi'] = \
                                            hybrids_input_dict['wind_dist_interconnect_mi']

    wind_input_dict['grid_system_size_MW'] = hybrids_input_dict['grid_interconnection_rating_MW'] / 2

    # delete line once finished debugging:
    print('wind grid rating : ', wind_input_dict['grid_system_size_MW'])

    wind_input_dict['substation_rating_MW'] = hybrids_input_dict['hybrid_substation_rating_MW'] / 2

    if 'override_total_management_cost' in hybrids_input_dict:
        wind_input_dict['override_total_management_cost'] = \
                                        hybrids_input_dict['override_total_management_cost']

    wind_input_dict['project_id'] = hybrids_input_dict['project_id']
    wind_input_dict['path_to_project_list'] = hybrids_input_dict['path_to_project_list']
    wind_input_dict['name_of_project_list'] = hybrids_input_dict['name_of_project_list']
    if 'development_labor_cost_usd' in hybrids_input_dict:
        wind_input_dict['development_labor_cost_usd'] = hybrids_input_dict['development_labor_cost_usd']

    if hybrids_input_dict['wind_plant_size_MW'] < 1:
        LandBOSSE_BOS_results = dict()
        LandBOSSE_BOS_results['total_bos_cost'] = 0
    else:
        LandBOSSE_BOS_results = run_landbosse(wind_input_dict)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><


    # <><><><><><><><><><><><><><><> RUNNING SolarBOSSE API <><><><><><><><><><><><><><><><>
    solar_system_size = hybrids_input_dict['solar_system_size_MW_DC']
    solar_input_dict = dict()
    BOS_results = dict()
    solar_input_dict['project_list'] = 'project_list_50MW'
    solar_input_dict['system_size_MW_DC'] = solar_system_size

    if 'solar_dist_interconnect_mi' in hybrids_input_dict:
        solar_input_dict['dist_interconnect_mi'] = hybrids_input_dict['solar_dist_interconnect_mi']
    else:
        if solar_system_size <= 10:
            solar_input_dict['dist_interconnect_mi'] = 0
        else:
            solar_input_dict['dist_interconnect_mi'] = (0.0263 * solar_system_size) - 0.2632

    # Define solar_construction_time_months
    if 'solar_construction_time_months' in hybrids_input_dict:
        solar_input_dict['construction_time_months'] = \
            hybrids_input_dict['solar_construction_time_months']
    else:
        if solar_system_size > 50:
            solar_input_dict['construction_time_months'] = 24
        elif solar_system_size <= 20:
            solar_input_dict['construction_time_months'] = 12

        elif solar_system_size <= 10:
            solar_input_dict['construction_time_months'] = 6

    solar_input_dict['interconnect_voltage_kV'] = \
                                        hybrids_input_dict['interconnect_voltage_kV']

    solar_input_dict['grid_system_size_MW_DC'] = \
                                    hybrids_input_dict['grid_interconnection_rating_MW'] / 2

    if 'dc_ac_ratio' in hybrids_input_dict:
        solar_input_dict['grid_size_MW_AC'] = \
            solar_input_dict['grid_system_size_MW_DC'] / hybrids_input_dict['dc_ac_ratio']
    else:
        solar_input_dict['grid_size_MW_AC'] = solar_input_dict['grid_system_size_MW_DC']

    # delete line once finished debugging:
    print('solar grid rating : ', solar_input_dict['grid_size_MW_AC'])

    solar_input_dict['substation_rating_MW'] = hybrids_input_dict['hybrid_substation_rating_MW'] / 2

    if hybrids_input_dict['solar_system_size_MW_DC'] < 1:
        SolarBOSSE_results = dict()
        SolarBOSSE_results['total_bos_cost'] = 0
    else:
        SolarBOSSE_results, detailed_results = run_solarbosse(solar_input_dict)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><

    # <><><><><><><><><><><><><><><> RUNNING StorageBOSSE API <><><><><><><><><><><><><><><><>

    # Establish 'storage_input_dict' using relevant parameters from hybrids_input_dict
    storage_input_dict = dict()
    storage_input_dict['system_size_MW_DC'] = hybrids_input_dict['storage_system_size_MW_DC']
    storage_input_dict['system_size_MWh'] = hybrids_input_dict['storage_system_size_MWh']
    storage_input_dict['project_list'] = hybrids_input_dict['storage_project_list']
    storage_input_dict['construction_time_months'] = 6

    if max(storage_input_dict['system_size_MW_DC'], storage_input_dict['system_size_MWh']) > 50:
        storage_input_dict['construction_time_months'] = 24
    elif max(storage_input_dict['system_size_MW_DC'], storage_input_dict['system_size_MWh']) <= 20:
        storage_input_dict['construction_time_months'] = 12
    elif max(storage_input_dict['system_size_MW_DC'], storage_input_dict['system_size_MWh']) <= 10:
        storage_input_dict['construction_time_months'] = 6

    if hybrids_input_dict['storage_system_size_MW_DC'] == 0:
        StorageBOSSE_BOS_results = dict()
        StorageBOSSE_BOS_results['total_bos_cost'] = 0
    else:
        StorageBOSSE_BOS_results, detailed_results = run_storagebosse(storage_input_dict)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><

    return LandBOSSE_BOS_results, SolarBOSSE_results, StorageBOSSE_BOS_results
