from LandBOSSE.landbosse.landbosse_api.run import run_landbosse
from SolarBOSSE.main import run_solarbosse

# <><><><><><><><><><><><><><><> RUNNING LandBOSSE API <><><><><><><><><><><><><><><><>
# Required inputs to run hybrids_shared_infrastructure:
hybrids_input_dict = dict()
hybrids_input_dict['shared_interconnection'] = False
hybrids_input_dict['distance_to_interconnect_mi'] = 5
hybrids_input_dict['new_switchyard'] = True

# Wind farm required inputs
hybrids_input_dict['interconnect_voltage_kV'] = 15
hybrids_input_dict['wind_dist_interconnect_mi'] = 0
hybrids_input_dict['num_turbines'] = 5
hybrids_input_dict['turbine_rating_MW'] = 1.5
# hybrids_input_dict['wind_construction_time_months'] = 5
hybrids_input_dict['wind_plant_size_MW'] = hybrids_input_dict['num_turbines'] * \
                                           hybrids_input_dict['turbine_rating_MW']

# Solar farm required inputs
hybrids_input_dict['solar_system_size_MW_DC'] = 5
hybrids_input_dict['solar_construction_time_months'] = 10
hybrids_input_dict['solar_dist_interconnect_mi'] = 5

# This DC_AC_ratio input currently just used in calculating
# grid_dict['system_size_MW_AC'] below.
# TODO: Connect DC_AC_ratio to SolarBOSSE
hybrids_input_dict['DC_AC_ratio'] = 1.2

# =================================== Pre Propressing Script ==========================
if hybrids_input_dict['shared_interconnection']:
    hybrids_input_dict['wind_dist_interconnect_mi'] = 0
    hybrids_input_dict['solar_dist_interconnect_mi'] = 0
    grid_dict = dict()

    grid_dict['distance_to_interconnect_mi'] = \
        hybrids_input_dict['wind_dist_interconnect_mi']

    grid_dict['system_size_MW_AC'] = hybrids_input_dict['wind_plant_size_MW'] + \
                                     (hybrids_input_dict['solar_system_size_MW_DC'] /
                                      hybrids_input_dict['DC_AC_ratio'])



# =====================================================================================

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
    print(LandBOSSE_BOS_results)
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
    print(SolarBOSSE_results)
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><

# Hybrid BOS Results:

total_hybrids_BOS_USD = LandBOSSE_BOS_results['total_bos_cost'] + \
                        SolarBOSSE_results['total_bos_cost']

print('total_hybrids_BOS_USD: $', total_hybrids_BOS_USD)

if SolarBOSSE_results['total_bos_cost'] == 0:
    total_hybrids_BOS_USD_Watt = \
        (LandBOSSE_BOS_results['total_bos_cost'] / (hybrids_input_dict['wind_plant_size_MW'] * 1e6))

elif LandBOSSE_BOS_results['total_bos_cost'] == 0:
    total_hybrids_BOS_USD_Watt = \
        (SolarBOSSE_results['total_bos_cost'] / (hybrids_input_dict['solar_system_size_MW_DC'] * 1e6))

else:
    total_hybrids_BOS_USD_Watt = \
        (LandBOSSE_BOS_results['total_bos_cost'] / (hybrids_input_dict['wind_plant_size_MW'] * 1e6)) + \
        (SolarBOSSE_results['total_bos_cost'] / (hybrids_input_dict['solar_system_size_MW_DC'] * 1e6))

print('total_hybrids_BOS_USD_Watt: $', total_hybrids_BOS_USD_Watt)
