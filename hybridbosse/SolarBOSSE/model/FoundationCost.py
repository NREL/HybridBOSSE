import traceback
import math
import pandas as pd
import numpy as np
from .CostModule import CostModule

class FoundationCost(CostModule):
    """
    **FoundationCost.py**

    - Refactored by Parangat Bhaskar on May 10, 2020

    \nCalculates the costs of constructing foundations for utility scale solar projects.
    Here, foundations is referring to the concrete pad that holds the inverter +
    transformer container (only).

    Not considered in this module: Racking systems foundation. Ths is done in
    RackingSystemInstallation module.

    * Get number of turbines
    * Get duration of construction
    * Get daily hours of operation*  # todo: add to process diagram
    * Get season of construction*  # todo: add to process diagram
    * [Get region]
    * Get rotor diameter
    * Get hub height
    * Get turbine rating
    * Get buoyant foundation design flag
    * [Get seismic zone]
    * Get tower technology type
    * Get hourly weather data
    * [Get specific seasonal delays]
    * [Get long-term, site-specific climate data]
    * Get price data
    * Get labor rates
    * Get material prices for steel and concrete
    * [Use region to determine weather data]


    \n\nGiven below is the set of calculations carried out in this module:

    * Calculate the foundation loads using the rotor diameter, hub height, and turbine rating

    * Determine the foundation size based on the foundation loads, buoyant foundation design flag, and type of tower technology

    * Estimate the amount of material needed for foundation construction based on foundation size and number of turbines

    * Estimate the amount of time required to construct foundation based on foundation size, hours of operation, duration of construction, and number of turbines

    * Estimate the additional amount of time for weather delays (currently only assessing wind delays) based on hourly weather data, construction time, hours of operation, and season of construction

    * Estimate the amount of labor required for foundation construction based on foundation size, construction time, and weather delay
        * Calculate number of workers by crew type
        * Calculate man hours by crew type

    * Estimate the amount of equipment needed for foundation construction based on foundation size, construction time, and weather delay
        * Calculate number of equipment by equip type
        * Calculate equipment hours by equip type

    - Calculate the total foundation cost based on amount of equipment, amount of labor, amount of material, and price data.


    **Keys in the input dictionary are the following:**

    depth
        (int) depth of foundation [in m]


    component_data
        (pd.DataFrame) data frame with wind turbine component data

    def __init__(self, input_dict, output_dict, project_name):
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.project_name = project_name


    num_turbines
        (int) total number of turbines in wind farm

    duration_construction
        (int) estimated construction time in months

    num_delays
        (int) Number of delay events

    avg_hours_per_delay
        (float) Average hours per delay event

    std_dev_hours_per_delay
        (float) Standard deviation from average hours per delay event

    delay_speed_m_per_s
        (float) wind speed above which weather delays kick in

    start_delay_hours
        (int)

    mission_time_hours
        (int)

    gust_wind_speed_m_per_s
        (float)

    wind_height_of_interest_m
        (int)

    wind_shear_exponent
        (float)

    season_construct
        list of seasons (like ['spring', 'summer']) for the construction.

    time_construct
        list of time windows for constructions. Use ['normal'] for a
        0800 to 1800 schedule 10 hour schedule. Use ['long'] for an
        overnight 1800 to 2359, 0000 to 0759 overnight schedule. Use
        ['normal', 'long'] for a 24-hour schedule.

    operational_hrs_per_day
        (float)


    material_price
        (pd.DataFrame) dataframe containing foundation cost related material prices

    construction_estimator
        (pd.DataFrame) TODO: Formal definition for construction_estimator?


    **Keys in the output dictionary are the following:**

    F_dead_kN_per_turbine
        (float) foundation dead load [in kN]

    F_horiz_kN_per_turbine
        (float) total lateral load [kN]

    M_tot_kN_m_per_turbine
        (float) Moment [kN.m]

    Radius_o_m
        (float) foundation radius based on overturning moment [in m]

    Radius_g_m
        (float) foundation radius based on gapping [in m]

    Radius_b_m
        (float) foundation radius based on bearing pressure [in m]

    Radius_m
        (float) largest foundation radius based on all three foundation design criteria: moment, gapping, bearing [in m]

    foundation_volume_concrete_m3_per_pad
        (float) volume of a round, raft foundation [in m^3]

    steel_mass_short_ton
        (float) short tons of reinforcing steel

    material_needs_per_pad
        (pd.DataFrame) table containing material needs info for -> Steel - rebar, Concrete 5000 psi, Excavated dirt, Backfill.

    operation_data
        (pd.DataFrame) TODO: What's the best one line definition for this?


    **TODO: Weather delay set of outputs -> ask Alicia for formal definitions of these keys.**

    total_foundation_cost
        (pd.DataFrame) summary of foundation costs (in USD) broken down into 4 main categories:
        1. Equipment Rental
        2. Labor
        3. Materials
        4. Mobilization
    """

    def __init__(self, input_dict, output_dict, project_name):
        """
        Parameters
        ----------
        input_dict : dict
            The input dictionary with key value pairs described in the
            class documentation

        output_dict : dict
            The output dictionary with key value pairs as found on the
            output documentation.
        """
        super(FoundationCost, self).__init__(input_dict, output_dict, project_name)
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.project_name = project_name



        #Constants used in FoundationCost class. Making this data private (hidden
        # from outside of this class):
        self._kg_per_tonne = 1000
        self._cubicm_per_cubicft = 0.0283168
        self._steel_density = 9490  # kg / m^3
        self._cubicyd_per_cubicm = 1.30795
        self._ton_per_tonne = 0.907185
        self.inches_per_meter = 0.0254

    def determine_foundation_size(self, input_data, output_data):
        """
        Function to calculate the volume of a round, raft foundation. Assumes
        foundation made of concrete with 1 m thickness.

        Parameters
        -------
        Largest foundation radius based on all three foundation design criteria:
        moment, gapping, bearing [in m] -> Radius_m [in m]

        depth of foundation [in m] -> depth


        Returns
        -------
        Foundation volume [in m^3] -> foundation_volume_concrete_m3_per_pad

        """
        # concrete pad volume in cubic inches:
        output_data['concrete_pad_volume_inch3'] = \
            input_data['concrete_pad_length_inches'] * \
            input_data['concrete_pad_width_inches'] * \
            input_data['concrete_pad_depth_inches']

        output_data['concrete_pad_volume_m3'] = \
            output_data['concrete_pad_volume_inch3'] * (self.inches_per_meter ** 3)

        # add 10" to length and width of concrete width each
        output_data['excavated_volume_m3'] = \
            (input_data['concrete_pad_excavation_depth_inches'] * self.inches_per_meter) * \
            ((input_data['concrete_pad_length_inches'] + 10) * self.inches_per_meter) * \
            ((input_data['concrete_pad_width_inches'] + 10) * self.inches_per_meter)

        output_data['foundation_volume_concrete_m3_per_pad'] = \
            output_data['concrete_pad_volume_m3']

        return output_data


    def estimate_material_needs_per_pad(self, input_data, output_data):
        """
        Function to estimate amount of material based on foundation size and number of
        pads.


        Parameters
        -------
        Foundation concrete volume [in m^3] -> foundation_volume_concrete_m3_per_pad


        Returns
        -------

        (Returns pd.DataFrame) material_needs_per_pad


        """

        steel_mass_short_ton_per_pad = \
            output_data['foundation_volume_concrete_m3_per_pad'] * 0.1 * (
                self._steel_density / self._kg_per_tonne)

        concrete_volume_cubic_yards_per_pad = \
            output_data['foundation_volume_concrete_m3_per_pad'] * 0.9 * \
            self._cubicyd_per_cubicm

        #Assign values to output dictionary:
        output_data['material_needs_per_pad'] = pd.DataFrame([

            ['Steel - rebar', steel_mass_short_ton_per_pad, 'ton (short)'],

            ['Concrete 5000 psi', concrete_volume_cubic_yards_per_pad, 'cubic yards'],

            ['Excavated dirt', output_data['excavated_volume_m3'] *
             self._cubicyd_per_cubicm, 'cubic_yards'],

            ['Backfill', output_data['excavated_volume_m3'] * self._cubicyd_per_cubicm,
             'cubic_yards']],

            columns=['Material type ID', 'Quantity of material', 'Units']
        )

        output_data['steel_mass_short_ton_per_pad'] = steel_mass_short_ton_per_pad

        return output_data['material_needs_per_pad']

    def number_concrete_pads(self):
        """
        SolarBOSSE currently assumes that all projects (regardless of project size)
        use containerized 1 MW inverter that comes with an LV/MV transformer as well.
        Here is a sample inverter+transformer station (for visual purposes only):
        https://www.solarpowerworldonline.com/2011/02/1-mw-solar-inverter-station/
        and
        https://files.sma.de/downloads/SC4xxxUP-DS-en-23.pdf

        """
        # TODO: raise exception when user changes inverter rating to anything less than
        # 1 MW. That is to say, SolarBOSSE only models central MVAC systems only
        # (currently); which means, only central inverters and NOT string inverters.
        inverter_rating_MW = self.input_dict['inverter_rating_kW'] / 1000
        number_concrete_pads = self.input_dict['system_size_MW_DC'] / inverter_rating_MW
        self.output_dict['number_concrete_pads'] = number_concrete_pads
        return number_concrete_pads

    def estimate_construction_time(self, input_data, output_data):
        """
        Function to estimate construction time on per turbine basis.

        Parameters
        -------
        duration_construction

        pd.DataFrame
            construction_estimator

        pd.DataFrame
            material_needs_per_pad



        Returns
        -------

        (pd.DataFrame) operation_data

        """

        # Assuming construction of transformer & inverter pads takes 20% of total
        # project time
        foundation_construction_time = input_data['construction_time_months'] * 0.2
        throughput_operations = input_data['construction_estimator']
        material_needs_per_pad = output_data['material_needs_per_pad']

        quantity_materials_entire_farm = \
            material_needs_per_pad['Quantity of material'] * self.number_concrete_pads()

        # Calculations for estimate construction time will be on entire solar farm
        # basis:
        output_data['material_needs_entire_farm'] = material_needs_per_pad.copy()
        material_needs_entire_farm = output_data['material_needs_entire_farm']

        material_needs_entire_farm['Quantity of material'] = \
            quantity_materials_entire_farm

        operation_data = throughput_operations.where(
            throughput_operations['Module'] == 'Foundations').dropna(thresh=4)

        # operation data for entire solar farm:
        operation_data = pd.merge(material_needs_entire_farm,
                                  operation_data,
                                  on=['Material type ID'], how='outer')

        operation_data['Number of days'] = \
            operation_data['Quantity of material'] / operation_data['Daily output']
        operation_data['Number of crews'] = \
            np.ceil((operation_data['Number of days'] / 30) / foundation_construction_time)

        alpha = operation_data[operation_data['Type of cost'] == 'Labor']
        operation_data_id_days_crews_workers = alpha[['Operation ID',
                                                      'Number of days',
                                                      'Number of crews',
                                                      'Number of workers']]

        # If more than one crew needed to complete within construction duration then
        # assume that all construction happens within that window and use that time-
        # frame for weather delays; if not, use the number of days calculated
        operation_data['time_construct_bool'] = \
            operation_data['Number of days'] > foundation_construction_time * 30

        boolean_dictionary = {True: foundation_construction_time * 30, False: np.NAN}

        operation_data['time_construct_bool'] = \
            operation_data['time_construct_bool'].map(boolean_dictionary)

        operation_data['Time construct days'] = \
            operation_data[['time_construct_bool', 'Number of days']].min(axis=1)

        num_days = operation_data['Time construct days'].max()

        output_data['operation_data_id_days_crews_workers'] = \
            operation_data_id_days_crews_workers

        output_data['operation_data_entire_farm'] = operation_data

        # Management costs accounted for in ManagementCost module of SolarBOSSE
        self.output_dict['managament_crew_cost_before_wind_delay'] = 0

        return output_data['operation_data_entire_farm']

    def calculate_costs(self, input_data, output_data):
        """
        Function to calculate the total foundation cost.

        Keys in input dictionary
        ------------------------
        pd.DataFrame
            material_needs_per_pad

        pd.DataFrame
            material_price

        pd.DataFrame
            operation_data

        wind_delay_time

        operational_hrs_per_day

        wind_multiplier

        pd.DataFrame
            construction_estimator


        Returns
        -------

        (pd.DataFrame) total_foundation_cost


        """

        material_vol_entire_farm = output_data['material_needs_entire_farm']
        material_price = input_data['material_price']

        material_data_entire_farm = pd.merge(material_vol_entire_farm,
                                             material_price,
                                             on=['Material type ID'])

        # material data on a total solar farm basis
        material_data_entire_farm['Cost USD'] = \
            material_data_entire_farm['Quantity of material'] * \
            pd.to_numeric(material_data_entire_farm['Material price USD per unit'])

        operation_data = output_data['operation_data_entire_farm']

        construction_estimator = input_data['construction_estimator']

        labor_equip_data = pd.merge(material_vol_entire_farm,
                                    construction_estimator,
                                    on=['Material type ID'])

        per_diem = \
            operation_data['Number of workers'] * operation_data['Number of crews'] * \
            (operation_data['Time construct days'] +
             np.ceil(operation_data['Time construct days'] / 7)) * input_data['construction_estimator_per_diem']

        where_are_na_ns = np.isnan(per_diem)
        per_diem[where_are_na_ns] = 0
        labor_equip_data['Cost USD'] = (labor_equip_data['Quantity of material'] *
                                        labor_equip_data['Rate USD per unit'] *
                                        input_data['overtime_multiplier']) + per_diem + \
                                       output_data['managament_crew_cost_before_wind_delay']

        self.output_dict['labor_equip_data'] = labor_equip_data

        # Create foundation cost data frame
        foundation_cost = pd.DataFrame(columns=['Type of cost',
                                                'Cost USD',
                                                'Phase of construction'])

        # Create equipment costs row to be appended to foundation_cost
        equipment_dataframe = \
            labor_equip_data[labor_equip_data['Type of cost'].str.match('Equipment rental')]

        equipment_cost_usd_without_delay = (equipment_dataframe['Quantity of material'] *
                                            equipment_dataframe['Rate USD per unit'] *
                                            input_data['overtime_multiplier']) + per_diem

        equipment_cost_usd_with_weather_delays = equipment_cost_usd_without_delay.sum()

        equipment_costs = pd.DataFrame([['Equipment rental',
                                         equipment_cost_usd_with_weather_delays,
                                         'Foundation']],
                                       columns=['Type of cost',
                                                'Cost USD',
                                                'Phase of construction'])

        # Create labor costs row to be appended to foundation_cost
        labor_dataframe = \
            labor_equip_data[labor_equip_data['Type of cost'].str.match('Labor')]

        labor_cost_usd_without_management = (labor_dataframe['Quantity of material'] *
                                             labor_dataframe['Rate USD per unit'] *
                                             input_data['overtime_multiplier']) + per_diem

        labor_cost_usd_with_management = labor_cost_usd_without_management.sum() + \
                                         output_data['managament_crew_cost_before_wind_delay']

        labor_costs = pd.DataFrame([['Labor',
                                     labor_cost_usd_with_management,
                                     'Foundation']],
                                   columns=['Type of cost',
                                            'Cost USD',
                                            'Phase of construction'])

        material_cost_dataframe = pd.DataFrame(columns=['Operation ID',
                                                        'Type of cost',
                                                        'Cost USD'])

        material_cost_dataframe['Operation ID'] = \
            material_data_entire_farm['Material type ID']

        material_cost_dataframe['Type of cost'] = 'Materials'
        material_cost_dataframe['Cost USD'] = material_data_entire_farm['Cost USD']
        material_costs_sum = material_cost_dataframe['Cost USD'].sum()
        material_costs = pd.DataFrame([['Materials',
                                        material_costs_sum,
                                        'Foundation']],
                                      columns=['Type of cost',
                                               'Cost USD',
                                               'Phase of construction'])

        # Append all cost items to foundation_cost
        foundation_cost = foundation_cost.append(equipment_costs)
        foundation_cost = foundation_cost.append(labor_costs)
        foundation_cost = foundation_cost.append(material_costs)

        # calculate mobilization cost as percentage of total foundation cost and add to
        # foundation_cost:
        equip_material_mobilization_multiplier = \
            0.16161 * (self.input_dict['system_size_MW_DC'] ** (-0.135))

        material_mobilization_USD = material_costs_sum * \
                                    equip_material_mobilization_multiplier

        equipment_mobilization_USD = \
            equipment_cost_usd_with_weather_delays * \
            equip_material_mobilization_multiplier

        labor_mobilization_multiplier = \
            1.245 * (self.input_dict['system_size_MW_DC'] ** (-0.367))

        labor_mobilization_USD = labor_cost_usd_with_management * \
                                 labor_mobilization_multiplier

        foundation_mobilization_usd = material_mobilization_USD + \
                                      equipment_mobilization_USD + \
                                      labor_mobilization_USD

        foundation_mob_cost = foundation_mobilization_usd
        mob_cost = pd.DataFrame([['Mobilization', foundation_mob_cost, 'Foundation']],
                                columns=['Type of cost', 'Cost USD', 'Phase of construction'])
        foundation_cost = foundation_cost.append(mob_cost)

        total_foundation_cost = foundation_cost
        output_data['total_foundation_cost_df'] = total_foundation_cost
        output_data['total_foundation_cost'] = total_foundation_cost['Cost USD'].sum()

        return total_foundation_cost

    def run_module(self):
        """
        Runs the FoundationCost module and populates the IO dictionaries with calculated values.

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
        try:
            # Returns foundation volume
            self.determine_foundation_size(self.input_dict, self.output_dict)

            # Returns material volume
            self.estimate_material_needs_per_pad(self.input_dict, self.output_dict)

            # Estimates construction time
            operation_data = self.estimate_construction_time(self.input_dict,
                                                             self.output_dict)

            # duration_construction is in units of days
            # duration_construction_months is in units of months
            days_per_month = 30
            duration_construction = \
                operation_data['Time construct days'].max(skipna=True)
            duration_construction_months = duration_construction / days_per_month

            self.output_dict['foundation_construction_months'] = duration_construction_months

            self.calculate_costs(self.input_dict, self.output_dict)

            return 0, 0   # module ran successfully

        except Exception as error:
            traceback.print_exc()
            print(f"Fail {self.project_name} FoundationCost")
            self.input_dict['error']['FoundationCost'] = error
            return 1, error    # module did not run successfully
