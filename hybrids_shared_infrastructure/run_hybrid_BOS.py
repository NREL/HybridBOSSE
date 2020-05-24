from LandBOSSE.landbosse.landbosse_api.run import run_landbosse
from SolarBOSSE.main import run_solarbosse

# <><><><><><><><><><><><><><><> RUNNING LandBOSSE API <><><><><><><><><><><><><><><><>

# Default inputs on the SAM UI. Commented out since SAM will pass these values
# down to LandBOSSE.
wind_input_dict = dict()
wind_input_dict['num_turbines'] = 100
wind_input_dict['turbine_rating_MW'] = 1.5
wind_input_dict['interconnect_voltage_kV'] = 137
wind_input_dict['distance_to_interconnect_mi'] = 10
wind_input_dict['project_id'] = 'foundation_validation_ge15'
wind_input_dict['turbine_spacing_rotor_diameters'] = 4
wind_input_dict['row_spacing_rotor_diameters'] = 10
wind_input_dict['rotor_diameter_m'] = 77
wind_input_dict['hub_height_meters'] = 80
wind_input_dict['wind_shear_exponent'] = 0.20
wind_input_dict['depth'] = 2.36  # Foundation depth in m
wind_input_dict['rated_thrust_N'] = 589000
wind_input_dict['labor_cost_multiplier'] = 1
wind_input_dict['gust_velocity_m_per_s'] = 59.50

LandBOSSE_BOS_results = run_landbosse(wind_input_dict)
print(LandBOSSE_BOS_results)
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><


# <><><><><><><><><><><><><><><> RUNNING SolarBOSSE API <><><><><><><><><><><><><><><><>
solar_system_size = 5
solar_input_dict = dict()
BOS_results = dict()
BOS_results.update({str(solar_system_size)+' MW scenario': ' '})
solar_input_dict['project_list'] = 'project_list_50MW'
solar_input_dict['system_size_MW_DC'] = solar_system_size

if solar_system_size <= 10:
    solar_input_dict['dist_interconnect_mi'] = 0
else:
    solar_input_dict['dist_interconnect_mi'] = (0.0263 * solar_system_size) - 0.2632

if solar_system_size > 50:
    solar_input_dict['construction_time_months'] = 24
elif solar_system_size <= 20:
    solar_input_dict['construction_time_months'] = 12

elif solar_system_size <= 10:
    solar_input_dict['construction_time_months'] = 6

if solar_system_size <= 20:
    solar_input_dict['interconnect_voltage_kV'] = 34.5

BOS_results, detailed_results = run_solarbosse(solar_input_dict)
print(BOS_results)
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><
