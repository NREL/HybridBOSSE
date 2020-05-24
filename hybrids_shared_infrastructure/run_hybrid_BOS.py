from LandBOSSE.landbosse.landbosse_api.run import run_landbosse
from SolarBOSSE.main import run_solarbosse


# <><><><><><><><><><><><><><><> Defining Hybrid Scenario <><><><><><><><><><><><><><><
# Required inputs to run hybrids_shared_infrastructure:
hybrids_input_dict = dict()
hybrids_input_dict['shared_interconnection'] = True
hybrids_input_dict['distance_to_interconnect_mi'] = 5
hybrids_input_dict['new_switchyard'] = True
hybrids_input_dict['grid_interconnection_rating_MW'] = 10
hybrids_input_dict['interconnect_voltage_kV'] = 15

# Wind farm required inputs
hybrids_input_dict['wind_dist_interconnect_mi'] = 0
hybrids_input_dict['num_turbines'] = 5
hybrids_input_dict['turbine_rating_MW'] = 1.5
# hybrids_input_dict['wind_construction_time_months'] = 5
hybrids_input_dict['wind_plant_size_MW'] = hybrids_input_dict['num_turbines'] * \
                                           hybrids_input_dict['turbine_rating_MW']

# Solar farm required inputs
hybrids_input_dict['solar_system_size_MW_DC'] = 5
hybrids_input_dict['solar_construction_time_months'] = 5
hybrids_input_dict['solar_dist_interconnect_mi'] = 5

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><


# <><><><><><><><><><><><><><><> RUNNING LandBOSSE API <><><><><><><><><><><><><><><><>

wind_input_dict = dict()
wind_input_dict['num_turbines'] = hybrids_input_dict['num_turbines']
wind_input_dict['turbine_rating_MW'] = hybrids_input_dict['turbine_rating_MW']

wind_input_dict['interconnect_voltage_kV'] =    \
                                        hybrids_input_dict['interconnect_voltage_kV']

wind_input_dict['distance_to_interconnect_mi'] = \
                                        hybrids_input_dict['wind_dist_interconnect_mi']

wind_input_dict['project_id'] = 'ge15_public_dist'

wind_input_dict['path_to_project_list'] = '/Users/pbhaskar/Desktop/Projects/Shared ' \
                                          'Infrastructure/hybrids_shared_infra_tool/'
wind_input_dict['name_of_project_list'] = 'project_list_ge15_dist_05'

if hybrids_input_dict['wind_plant_size_MW'] < 1:
    LandBOSSE_BOS_results = dict()
    LandBOSSE_BOS_results['total_bos_cost'] = 0
else:
    LandBOSSE_BOS_results = run_landbosse(wind_input_dict)
    print('Wind BOS: ', LandBOSSE_BOS_results)
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><


# <><><><><><><><><><><><><><><> RUNNING SolarBOSSE API <><><><><><><><><><><><><><><><>
solar_system_size = hybrids_input_dict['solar_system_size_MW_DC']
solar_input_dict = dict()
BOS_results = dict()
BOS_results.update({str(solar_system_size)+' MW scenario': ' '})
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

    if solar_system_size <= 20:
        solar_input_dict['interconnect_voltage_kV'] = 34.5

if hybrids_input_dict['solar_system_size_MW_DC'] < 1:
    SolarBOSSE_results = dict()
    SolarBOSSE_results['total_bos_cost'] = 0
else:
    SolarBOSSE_results, detailed_results = run_solarbosse(solar_input_dict)
    print('Solar BOS: ', SolarBOSSE_results)
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><

# Hybrid BOS Results:

total_hybrids_BOS_USD = LandBOSSE_BOS_results['total_bos_cost'] + \
                        SolarBOSSE_results['total_bos_cost']

# =================================== Post Processing Script ==========================

def hybrid_gridconnection(input_dict):
    """
    Function to calculate total costs for transmission and distribution.

    Parameters
    ----------
    <None>

    Returns
    -------
    tuple
        First element of tuple contains a 0 or 1. 0 means no errors happened and
        1 means an error happened and the module failed to run. The second element
        either returns a 0 if the module ran successfully, or it returns the error
        raised that caused the failure.
    """
    output_dict = dict()
    # Switch between utility scale model and distributed model
    # Run utility version of GridConnectionCost for project size > 10 MW:
    if input_dict['system_size_MW'] > 15:
        if input_dict['dist_interconnect_mi'] == 0:
            output_dict['trans_dist_usd'] = 0
        else:
            if input_dict['new_switchyard'] is True:
                output_dict['interconnect_adder_USD'] = \
                    18115 * input_dict['interconnect_voltage_kV'] + 165944
            else:
                output_dict['interconnect_adder_USD'] = 0

            output_dict['trans_dist_usd'] = \
                ((1176 * input_dict['interconnect_voltage_kV'] + 218257) *
                 (input_dict['dist_interconnect_mi'] ** (-0.1063)) *
                 input_dict['dist_interconnect_mi']
                 ) + output_dict['interconnect_adder_USD']

    # Run distributed wind version of GridConnectionCost for project size < 15 MW:
    else:
        # Code below is for newer version of LandBOSSE which incorporates
        # distributed wind into the model. Here POI refers to point of
        # interconnection.
        output_dict['array_to_POI_usd_per_kw'] = \
            1736.7 * ((input_dict['system_size_MW'] * 1000) ** (-0.272))

        output_dict['trans_dist_usd'] = \
            input_dict['system_size_MW'] * 1000 * output_dict['array_to_POI_usd_per_kw']

    return output_dict['trans_dist_usd']


if hybrids_input_dict['shared_interconnection']:

    hybrids_input_dict['dist_interconnect_mi'] = \
        hybrids_input_dict['distance_to_interconnect_mi']

    hybrids_input_dict['system_size_MW'] = \
        hybrids_input_dict['grid_interconnection_rating_MW']

    hybrid_gridconnection_usd = hybrid_gridconnection(hybrids_input_dict)

    total_hybrids_BOS_USD = total_hybrids_BOS_USD + \
                            hybrid_gridconnection_usd - \
                            LandBOSSE_BOS_results['total_gridconnection_cost'] - \
                            SolarBOSSE_results['total_transdist_cost']

# =====================================================================================

print('total_hybrids_BOS_USD: $', total_hybrids_BOS_USD)

if SolarBOSSE_results['total_bos_cost'] == 0:
    total_hybrids_BOS_USD_Watt = \
        (LandBOSSE_BOS_results['total_bos_cost'] / (hybrids_input_dict['wind_plant_size_MW'] * 1e6))

elif LandBOSSE_BOS_results['total_bos_cost'] == 0:
    total_hybrids_BOS_USD_Watt = \
        (SolarBOSSE_results['total_bos_cost'] / (hybrids_input_dict['solar_system_size_MW_DC'] * 1e6))

else:
    total_hybrids_BOS_USD_Watt = total_hybrids_BOS_USD / \
                                 ((hybrids_input_dict['wind_plant_size_MW'] * 1e6) +
                                  (hybrids_input_dict['solar_system_size_MW_DC'] * 1e6))

print('total_hybrids_BOS_USD_Watt: $', total_hybrids_BOS_USD_Watt)


