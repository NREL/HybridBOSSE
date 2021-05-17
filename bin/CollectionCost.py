import traceback
import math
import numpy as np
import pandas as pd
from .optimal_matrix_collection import Graph
from .WeatherDelay import WeatherDelay as WD
from .WeatherWindowCSVReader import read_weather_window, extend_weather_window

"""
**CollectionCost.py**
- Created by Matt Shields for Offshore BOS
- Refactored by Parangat Bhaskar for LandBOSSE

NREL - 05/31/2019

This module consists of two classes:

- The first class in this module is the parent class Cable, with a sublass Array that inherits from Cable

- The second class is the ArraySystem class that instantiates the Array class and determines the wind farm layout and calculates total collection system cost
"""

import math
import numpy as np
import traceback
import pandas as pd

from .CostModule import CostModule


class Cable:

    def __init__(self, cable_specs, addl_specs):
        """
        Parameters
        ----------
        cable_specs : dict
            The input dictionary with key value pairs described in the
            class documentation

        addl_specs : dict
            The output dictionary with key value pairs as found on the
            output documentation.

        """

        self.current_capacity = cable_specs['Current Capacity (A)']
        self.rated_voltage    = cable_specs['Rated Voltage (V)']
        self.ac_resistance    = cable_specs['AC Resistance (Ohms/km)']
        self.inductance       = cable_specs['Inductance (mH/km)']
        self.capacitance      = cable_specs['Capacitance (nF/km)']
        self.cost             = cable_specs['Cost (USD/LF)']
        self.line_frequency_hz= addl_specs['line_frequency_hz']

        # only include length in cable object if in manual mode. Otherwise Array object specs. length
        self.total_length = 0

        # Calc additional cable specs
        self.calc_char_impedance(self.line_frequency_hz)
        self.calc_power_factor()
        self.calc_cable_power()

    def calc_char_impedance(self, line_frequency_hz):
        """
        Calculate characteristic impedance of cable, Ohms

        Parameters
        ----------
        line_frequency_hz : int
            Frequency of AC current, Hz
        """
        conductance = 1 / self.ac_resistance

        num = complex(self.ac_resistance, 2 * math.pi * line_frequency_hz * self.inductance)
        den = complex(conductance, 2 * math.pi * line_frequency_hz * self.capacitance)
        self.char_impedance = np.sqrt(num / den)

    def calc_power_factor(self):
        """
        Calculate power factor
        """

        phase_angle = math.atan(np.imag(self.char_impedance) /
                                np.real(self.char_impedance))
        self.power_factor = math.cos(phase_angle)

    def calc_cable_power(self):
        """
        Calculate maximum power transfer through 3-phase cable, MW
        """

        self.cable_power = (np.sqrt(3) * self.rated_voltage * self.current_capacity * self.power_factor / 1000)


class Array(Cable):
    """Array cable base class"""

    def __init__(self, cable_specs, addl_inputs):
        """
        Creates an instance of Array cable.
        (May be multiple instances of different capacity cables in a string)

        Parameters
        ----------
        cable_specs : dict
            Dictionary containing following cable specifications:

            - turbine_rating_MW

            - upstream_turb

            - turbine_spacing_rotor_diameters

            - rotor_diameter_m

        addl_inputs : dict

            - Any additional user inputs

        Returns
        -------
        self.max_turb_per_cable : float
            Maximum number of turbines (at turbine_rating_MW) an individual cable
            can support
        self.num_turb_per_cable : float
            Number of turbines each cable in a string actually supports.
        self.turb_sequence : float
            Ordering of cable in string, starting with smallest cable at 0
        self.downstream_connection : int
            Additional cable length requried to connect between different sized
            cables (for first cable in string only)
        self.array_cable_len : float
            Length of individual cable in a string, km
        """

        super().__init__(cable_specs, addl_inputs)
        self.line_frequency_hz = addl_inputs['line_frequency_hz']
        self.calc_max_turb_per_cable(addl_inputs)
        self.calc_num_turb_per_cable(addl_inputs)
        self.calc_array_cable_len(addl_inputs)

    def calc_max_turb_per_cable(self, addl_inputs):
        """
        Calculate the number of turbines that each cable can support

        Parameters
        ----------
        turbine_rating_MW : int
            Nameplate capacity of individual turbines
        """

        turbine_rating_MW = addl_inputs['turbine_rating_MW']

        self.max_turb_per_cable = np.floor(self.cable_power / turbine_rating_MW)

    def calc_num_turb_per_cable(self, addl_inputs):
        """
        Calculates actual number of turbines per cable, accounting for upstream
        turbines.

        Parameters
        ----------
        upstream_turb : int
            Number of turbines on upstream cables in string
        """

        upstream_turb = addl_inputs['upstream_turb']
        self.turb_sequence = addl_inputs['turb_sequence']

        self.max_turb_per_cable = np.floor(self.cable_power / addl_inputs['turbine_rating_MW'])
        self.num_turb_per_cable = self.max_turb_per_cable - upstream_turb

        if upstream_turb == 0:
            self.downstream_connection = -1
        else:
            self.downstream_connection = 0

    def calc_array_cable_len(self, addl_inputs):
        """
        Calculate array cable length per string, km

        Parameters
        ----------
        turbine_spacing_rotor_diameters : int
            Spacing between turbines in string, # of rotor diameters
        rotor_diameter_m : int or float
            Rotor diameter, m
        """

        turbine_spacing_rotor_diameters = addl_inputs['turbine_spacing_rotor_diameters']
        rotor_diameter_m = addl_inputs['rotor_diameter_m']

        self.calc_turb_section_len(turbine_spacing_rotor_diameters, rotor_diameter_m)

        self.array_cable_len = ((self.num_turb_per_cable + self.downstream_connection) * self.turb_section_length)

    #    @staticmethod
    def calc_turb_section_len(self, turbine_spacing_rotor_diameters, rotor_diameter_m):
        """
        Calculate array cable section length between two turbines. Also, section length == trench length. Which means
        trench_length = cable_length for that section.

        Parameters
        ----------
        turbine_spacing_rotor_diameters : int
            Spacing between turbines in string, # of rotor diameters
        rotor_diameter_m : int or float
            Rotor diameter, m

        Returns
        -------
        turb_connect_len : int
            Length of array cable between two turbines, km
        """

        self.turb_section_length = (turbine_spacing_rotor_diameters * rotor_diameter_m) / 1000

        return self.turb_section_length


class ArraySystem(CostModule):
    """


    \nThis module:

    * Calculates cable length to substation

    * Calculates number of strings in a subarray

    * Calculated number of strings

    * Calculates total cable length for each cable type

    * Calculates total trench length

    * Calculates total collection system cost based on amount of material, amount of labor, price data, cable length, and trench length.



    **Keys in the input dictionary are the following:**

    * Given below are attributes that define each cable type:
        * conductor_size
            (int)   cross-sectional diameter of cable [in mm]



    """

    def __init__(self, input_dict, output_dict):

        self.input_dict = input_dict
        self.output_dict = output_dict
        if 'project_mode' in input_dict:
            mode = input_dict['project_mode']
            if mode == 1 or mode == 2:
                self.cable_specs = input_dict['cable_specs_pd_ac']
            elif mode == 3:
                self.cable_specs = input_dict['cable_specs_pd_dc']
            else:
                exit('Error: {0} is not a valid mode, modes 1, 2, 3, 4 are valid'.format(mode))
        else:
            #self.cable_specs = input_dict['cable_specs_pd_ac']
            pass
        self.output_dict['total_cable_len_km'] = 0
        self.storage_mw_rating = input_dict['storage_system_size_MW_DC']
        self.solar_mw_rating = input_dict['solar_system_size_MW_DC']
        self.wind_mw_rating = input_dict['num_turbines'] * input_dict['turbine_rating_MW']
        self._km_to_LF = 0.0003048    #Units: [km/LF] Conversion factor for converting from km to linear foot.
        self._total_cable_cost = 0
        self._total_turbine_counter = 0
        self._cable_length_km = dict()
        self.check_terminal = 0
        self.project_name = self.input_dict['project_name']
        self.x = self.input_dict['x_coordinate_layout']
        self.y = self.input_dict['y_coordinate_layout']
        self.L = [[coor[0], coor[1]] for coor in zip(self.x, self.y)]# location of nodes [m]
        self.L = np.ndarray((len(self.L), 2), buffer=np.array(self.L))
        self.A = self.input_dict['adj_layout']# adjacency matrix for collection system. Zeroth element is substation
        self.A = np.ndarray((len(self.A), len(self.A)), buffer=np.array(self.A), dtype='i8')
        self.types = self.input_dict['type_layout']
        self.n_segments = len(self.types)-1  # #nodes = # cable segments = # nodes - 1
        self.C = np.zeros(self.n_segments + 1)  # init capacity vector: cable capacity needed at each node
        self.calc_current_properties()

    def calc_current_properties(self):
        """
        Find collection system voltage [kV] and turbine capacity [MW]. Sort cables by current capacity.

        Returns
        -------
        self.collection_V: collection system voltage [kV]
        self.turbine_capacity: turbine capacity [MW] at collection system voltage
        """

        self._total_turbine_counter = 0
        self.check_terminal = 0
        self.collection_V = 9999

        for cable, property in self.cable_specs.head().iterrows():
            rated_voltage_V = property['Rated Voltage (V)']  # Rated Voltage is in kV
            if rated_voltage_V > self.collection_V:
                self.collection_V = rated_voltage_V

        # sort cables by Power capacity
        self.cable_specs.sort_values(by=['Current Capacity (A)', 'Rated Voltage (V)'], inplace=True)
        self.cable_specs = self.cable_specs.reset_index(drop=True)


    def calc_required_segment_capacity(self):
        """
        Find the type of cable needed for each cable segment based on capacity needed
        Cable lengths are in meters in this method
        The code starts with outermost nodes, and adds them to their receiver downstream (receiver) nodes.
        This process continues until the substation is reached and all nodes have been assigned an capacity.
        Giver nodes are the parent nodes that are currently being considered.
        Closed nodes are those that have contributed to all of their child nodes.
        Nodes go from []->receiver->giver->closed
        """
        # find outermost nodes
        for i in range(1, self.n_segments+1):
            if self.A[i, :].sum() == 1:
                self.C[i] = 1

        giver = np.where(self.C > 0)[0]  # nodes that give capacity to downstream nodes
        closed = np.empty(shape=(0, 0))  # nodes that have contributed to all their receiver nodes
        while np.prod(self.C[1:]) == 0:  # run until all turbine nodes are assigned a capacity
            x = np.linspace(1, self.n_segments, self.n_segments, dtype='int64')
            y = np.union1d(closed, giver)
            for i in np.setdiff1d(x, y):  # iterate through all nongiver, nonclosed nodes
                receiver = np.where(self.A[i, :] == 1)[0]  # nodes receiver to node i
                a = len(np.intersect1d(receiver, giver))
                b = (len(receiver) - 1)
                if a == b:  # if all but one receiver node are givers
                    self.C[i] += sum(
                        self.C[receiver]) + 1  # add giver node capacities to current node. +1 for this node's turbine
                    closed = np.append(closed, np.intersect1d(receiver, giver))  # giver nodes are now closed
                    giver = np.append(giver, i)  # add node i to giver nodes
                    giver = np.setdiff1d(giver, closed)  # removed closed nodes from giver

        self.C[0] = self.n_segments  # substation handles all turbines
        #self.C *= self.turbine_power  # scale capacity by turbine current
        #self.C *= self.total_power
        for idx in range(0, len(self.C)):
            node_type = self.types[idx]
            if node_type == 'wind_sub' or node_type == 'wind':
                self.C[idx] *= self.wind_mw_rating
            elif node_type == 'solar':
                self.C[idx] *= self.solar_mw_rating
            elif node_type == 'storage':
                self.C[idx] *= self.storage_mw_rating
            elif node_type == 'substation':
                pass
        """
        Create cable dictionary with cable start point, end point, length, capacity, and bool representing if the cable segment is the terminal
        """
        k = 0  # cable# iterator
        remains = np.ones(self.n_segments + 1)  # turbines still to have cables defined around
        array_dict = dict()
        # keys = {'Start point', 'End point', 'Length', 'Capacity'}
        for i in range(0, self.n_segments):
            for j in np.where(self.A[i, :] * remains == 1)[0]:
                array_dict['cable' + str(k)] = dict()
                array_dict['cable' + str(k)]['Start point'] = self.L[i, :]
                array_dict['cable' + str(k)]['End point'] = self.L[j, :]
                array_dict['cable' + str(k)]['Length'] = ((self.L[i, 0] - self.L[j, 0]) ** 2 + (
                        self.L[i, 1] - self.L[j, 1]) ** 2) ** (1 / 2)
                array_dict['cable' + str(k)]['Power Capacity'] = min(self.C[i], self.C[j])
                array_dict['cable' + str(k)]['Terminal?'] = False
                k += 1  # iterate to make new cable
            remains[i] = False  # prevent duplicate cables
        # add terminal cable
        array_dict['cable' + str(k)] = dict()
        array_dict['cable' + str(k)]['Length'] = 6 * 5280 * self._km_to_LF
        array_dict['cable' + str(k)]['Power Capacity'] = self.n_segments * 6#self.turbine_power
        array_dict['cable' + str(k)]['Terminal?'] = True
        self.array_dict = array_dict

    def estimate_construction_time(self, construction_time_input_data, construction_time_output_data):
        """
        Function to estimate construction time on per turbine basis.

        Parameters
        -------
        duration_construction

        pd.DataFrame
            rsmeans

        pd.DataFrame
            trench_length_km



        Returns
        -------

        (pd.DataFrame) operation_data

        """
        total_construction_time = construction_time_input_data['storage_construction_time_months'] + \
                                  construction_time_input_data['solar_construction_time_months'] + \
                                  construction_time_input_data['wind_construction_time_months']
        collection_construction_time = total_construction_time * 1 / 3  # assumes collection construction occurs for one-third of project duration

        throughput_operations = construction_time_input_data['rsmeans']
        trench_length_km = construction_time_output_data['trench_length_km']
        if construction_time_input_data['turbine_rating_MW'] >= 0.1:
            operation_data = throughput_operations.where(throughput_operations['Module'] == 'Collection').dropna(
                thresh=4)
            # from rsmeans data, only read in Collection related data and filter out the rest:
            cable_trenching = throughput_operations[throughput_operations.Module == 'Collection']
        else:   #switch for small DW
            operation_data = throughput_operations.where(
                throughput_operations['Module'] == 'Small DW Collection').dropna(thresh=4)
            # from rsmeans data, only read in Collection related data and filter out the rest:
            cable_trenching = throughput_operations[throughput_operations.Module == 'Small DW Collection']
        # operation_data = pd.merge()

        # from rsmeans data, only read in Collection related data and filter out the rest:
        cable_trenching = throughput_operations[throughput_operations.Module == 'Collection']

        # Storing data with labor related inputs:
        trenching_labor = cable_trenching[cable_trenching.values == 'Labor']
        trenching_labor_usd_per_hr = trenching_labor['Rate USD per unit'].sum()

        construction_time_output_data['trenching_labor_usd_per_hr']=trenching_labor_usd_per_hr
        trenching_labor_daily_output = trenching_labor['Daily output'].values[0]  # Units:  LF/day  -> where LF = Linear Foot
        trenching_labor_num_workers = trenching_labor['Number of workers'].sum()

        # Storing data with equipment related inputs:
        trenching_equipment = cable_trenching[cable_trenching.values == 'Equipment']
        trenching_cable_equipment_usd_per_hr = trenching_equipment['Rate USD per unit'].sum()
        construction_time_output_data['trenching_cable_equipment_usd_per_hr']=trenching_cable_equipment_usd_per_hr
        trenching_equipment_daily_output = trenching_equipment['Daily output'].values[0]  # Units:  LF/day  -> where LF = Linear Foot
        construction_time_output_data['trenching_labor_daily_output'] = trenching_labor_daily_output
        construction_time_output_data['trenching_equipment_daily_output'] = trenching_equipment_daily_output

        operation_data['Number of days taken by single crew'] = ((trench_length_km / self._km_to_LF) / trenching_labor_daily_output)
        operation_data['Number of crews'] = np.ceil((operation_data['Number of days taken by single crew'] / 30) / collection_construction_time)
        operation_data['Cost USD without weather delays'] = ((trench_length_km / self._km_to_LF) / trenching_labor_daily_output) * (operation_data['Rate USD per unit'] * construction_time_input_data['operational_hrs_per_day'])
        alpha = operation_data[operation_data['Type of cost'] == 'Collection']
        operation_data_id_days_crews_workers = alpha[['Operation ID', 'Number of days taken by single crew', 'Number of crews', 'Number of workers']]

        alpha = operation_data[operation_data['Type of cost'] == 'Labor']
        operation_data_id_days_crews_workers = alpha[['Operation ID', 'Number of days taken by single crew', 'Number of crews', 'Number of workers']]

        # if more than one crew needed to complete within construction duration then assume that all construction
        # happens within that window and use that timeframe for weather delays;
        # if not, use the number of days calculated
        operation_data['time_construct_bool'] = operation_data['Number of days taken by single crew'] > collection_construction_time * 30
        boolean_dictionary = {True: collection_construction_time * 30, False: np.NAN}
        operation_data['time_construct_bool'] = operation_data['time_construct_bool'].map(boolean_dictionary)
        operation_data['Time construct days'] = operation_data[['time_construct_bool', 'Number of days taken by single crew']].min(axis=1)
        num_days = operation_data['Time construct days'].max()


        # No 'management crew' in small DW
        if construction_time_input_data['turbine_rating_MW'] >= 0.1:
            # pull out management data
            crew_cost = self.input_dict['crew_cost']
            crew = self.input_dict['crew'][self.input_dict['crew']['Crew type ID'].str.contains('M0')]
            management_crew = pd.merge(crew_cost, crew, on=['Labor type ID'])
            management_crew = management_crew.assign(per_diem_total=management_crew['Per diem USD per day'] * management_crew['Number of workers'] * num_days)
            management_crew = management_crew.assign(hourly_costs_total=management_crew['Hourly rate USD per hour'] * self.input_dict['hour_day'][self.input_dict['time_construct']] * num_days)
            management_crew = management_crew.assign(total_crew_cost_before_wind_delay=management_crew['per_diem_total'] + management_crew['hourly_costs_total'])
            self.output_dict['management_crew'] = management_crew
            self.output_dict['managament_crew_cost_before_wind_delay'] = management_crew['total_crew_cost_before_wind_delay'].sum()
        else:
            self.output_dict['managament_crew_cost_before_wind_delay'] = 0.0

        construction_time_output_data['operation_data_id_days_crews_workers'] = operation_data_id_days_crews_workers
        construction_time_output_data['operation_data_entire_farm'] = operation_data

        return construction_time_output_data['operation_data_entire_farm']

    def create_manual_ArraySystem(self):

        self.addl_specs = dict()
        self.addl_specs['turbine_rating_MW'] = self.input_dict['turbine_rating_MW']
        self.addl_specs['storage_rating_MW'] = self.input_dict['storage_system_size_MW_DC']
        self.addl_specs['solar_rating_MW'] = self.input_dict['solar_system_size_MW_DC']
        self.addl_specs['mode'] = self.input_dict['project_mode']
        self.addl_specs['line_frequency_hz'] = self.input_dict['line_frequency_hz']

        # calculate cable segment requirements
        self.calc_required_segment_capacity()

        # Loops through all user defined cable types, composing them
        # in ArraySystem

        self.cables = {}
        self.cable_specs = self.cable_specs.T.to_dict()
        n = 0  # to keep tab of number of cables input by user.
        while n < len(self.cable_specs):
            specs = self.cable_specs[n]
            # Create instance of each cable and assign to ArraySystem.cables
            cable = Cable(specs, self.addl_specs)
            n += 1

            # self.cables[name] stores value which is a new instantiation of object of type Cable.
            self.cables[specs['Array Cable']] = cable
            self.output_dict['cables'] = self.cables

        # Calculate total length and cost of each cable type
        # Calculate total cable cost and power dissipated in the collection system:
        dissipated_power = 0  # W
        for segment in self.array_dict:
            for idx, (name, cable) in enumerate(self.cables.items()):
                if cable.current_capacity >= self.array_dict[segment]['Power Capacity']:
                    cable.total_length += self.array_dict[segment]['Length']
                    self.output_dict['total_cable_len_km'] += self.array_dict[segment]['Length']
                    cable.total_cost = (cable.total_length / self._km_to_LF) * cable.cost
                    self._total_cable_cost += (self.array_dict[segment][
                                                   'Length'] / self._km_to_LF) * cable.cost  # Keep running tally of total cable cost used in wind farm.
                    dissipated_power += 3 * (
                                self.array_dict[segment]['Power Capacity'] * 1e6 / self.collection_V * 1000) ** 2 * abs(
                        cable.ac_resistance) * self.array_dict[segment][
                                            'Length'] / 1000  # TODO P=3*I^2*R. IF 3 phase. Divide by 1000 to go from ohm/km->ohm/m
                    break  # only assign one cable to each segment

        # add substation to transmission interconnect cable

        self.output_dict['dissipated_power'] = dissipated_power
        self.output_dict['total_cable_cost'] = self._total_cable_cost


    def calculate_trench_properties(self, trench_properties_input, trench_properties_output):
        """
        Calculates the length of trench needed based on cable length and width of mulcher.
        """

        # units of cubic meters
        trench_properties_output['trench_length_km'] = trench_properties_output['total_cable_len_km']

    def calculate_weather_delay(self, weather_delay_input_data, weather_delay_output_data):
        """Calculates wind delays for roads"""
        # construct WeatherDelay module
        WD(weather_delay_input_data, weather_delay_output_data) #

        # compute weather delay
        wind_delay = pd.DataFrame(weather_delay_output_data['wind_delays'])

        # if greater than 4 hour delay, then shut down for full day (10 hours)
        wind_delay[(wind_delay > 4)] = 10
        weather_delay_output_data['wind_delay_time'] = float(wind_delay.sum())

        return weather_delay_output_data


    def calculate_costs(self, calculate_costs_input_dict, calculate_costs_output_dict):

        #read in rsmeans data:
        # rsmeans = calculate_costs_input_dict['rsmeans']
        operation_data = calculate_costs_output_dict['operation_data_entire_farm']

        per_diem = operation_data['Number of workers'] * operation_data['Number of crews']  * (operation_data['Time construct days'] + np.ceil(operation_data['Time construct days'] / 7)) * calculate_costs_input_dict['rsmeans_per_diem']
        per_diem = per_diem.dropna()

        calculate_costs_output_dict['time_construct_days'] = (calculate_costs_output_dict['trench_length_km'] / self._km_to_LF) / calculate_costs_output_dict['trenching_labor_daily_output']
        wind_delay_fraction = (calculate_costs_output_dict['wind_delay_time'] / calculate_costs_input_dict['operational_hrs_per_day']) / calculate_costs_output_dict['time_construct_days']
        # check if wind_delay_fraction is greater than 1, which would mean weather delays are longer than they can possibily be for the input data
        if wind_delay_fraction > 1:
            raise ValueError('{}: Error: Wind delay greater than 100%'.format(type(self).__name__))
        calculate_costs_output_dict['wind_multiplier'] = 1 / (1 - wind_delay_fraction)

        #Calculating trenching cost:
        calculate_costs_output_dict['Days taken for trenching (equipment)'] = (calculate_costs_output_dict['trench_length_km'] / self._km_to_LF) / calculate_costs_output_dict['trenching_equipment_daily_output']
        calculate_costs_output_dict['Equipment cost of trenching per day {usd/day)'] = calculate_costs_output_dict['trenching_cable_equipment_usd_per_hr'] * calculate_costs_input_dict['operational_hrs_per_day']
        calculate_costs_output_dict['Equipment Cost USD without weather delays'] = (calculate_costs_output_dict['Days taken for trenching (equipment)'] * calculate_costs_output_dict['Equipment cost of trenching per day {usd/day)'])
        calculate_costs_output_dict['Equipment Cost USD with weather delays'] = calculate_costs_output_dict['Equipment Cost USD without weather delays'] *  calculate_costs_output_dict['wind_multiplier']

        if calculate_costs_input_dict['turbine_rating_MW'] >= 0.1:
            trenching_equipment_rental_cost_df = pd.DataFrame([['Equipment rental', calculate_costs_output_dict[
                'Equipment Cost USD with weather delays'], 'Collection']],
                                                              columns=['Type of cost', 'Cost USD',
                                                                       'Phase of construction'])

        # switch for small DW
        else:
            if calculate_costs_output_dict['Equipment Cost USD with weather delays'] < 137:
                calculate_costs_output_dict['Equipment Cost USD with weather delays'] = 137   #cost of renting for a day
                trenching_equipment_rental_cost_df = pd.DataFrame([['Equipment rental', calculate_costs_output_dict[
                    'Equipment Cost USD with weather delays'], 'Collection']],
                                                                  columns=['Type of cost', 'Cost USD',
                                                                           'Phase of construction'])
            else:
                trenching_equipment_rental_cost_df = pd.DataFrame([['Equipment rental', calculate_costs_output_dict[
                    'Equipment Cost USD with weather delays'], 'Small DW Collection']],
                                                                  columns=['Type of cost', 'Cost USD',
                                                                           'Phase of construction'])

        #Calculating labor cost:
        calculate_costs_output_dict['Days taken for trenching (labor)'] = ((calculate_costs_output_dict['trench_length_km'] / self._km_to_LF) / calculate_costs_output_dict['trenching_labor_daily_output'])
        calculate_costs_output_dict['Labor cost of trenching per day (usd/day)'] = (calculate_costs_output_dict['trenching_labor_usd_per_hr'] * calculate_costs_input_dict['operational_hrs_per_day'])# * calculate_costs_input_dict['overtime_multiplier'])
        calculate_costs_output_dict['Total per diem costs (USD)'] = per_diem.sum()
        calculate_costs_output_dict['Labor Cost USD without weather delays'] =((calculate_costs_output_dict['Days taken for trenching (labor)'] * calculate_costs_output_dict['Labor cost of trenching per day (usd/day)']) + (calculate_costs_output_dict['Total per diem costs (USD)'] + calculate_costs_output_dict['managament_crew_cost_before_wind_delay']))
        calculate_costs_output_dict['Labor Cost USD with weather delays'] = calculate_costs_output_dict['Labor Cost USD without weather delays'] * calculate_costs_output_dict['wind_multiplier']

        if calculate_costs_input_dict['turbine_rating_MW'] >= 0.1:
            trenching_labor_cost_df = pd.DataFrame(
                [['Labor', calculate_costs_output_dict['Labor Cost USD with weather delays'], 'Collection']],
                columns=['Type of cost', 'Cost USD', 'Phase of construction'])

        # switch for small DW
        else:
            trenching_labor_cost_df = pd.DataFrame(
                [['Labor', calculate_costs_output_dict['Labor Cost USD with weather delays'], 'Small DW Collection']],
                columns=['Type of cost', 'Cost USD', 'Phase of construction'])

        #Calculate cable cost:
        cable_cost_usd_per_LF_df = pd.DataFrame([['Materials', self._total_cable_cost, 'Collection']],
                                               columns = ['Type of cost', 'Cost USD', 'Phase of construction'])

        # Combine all calculated cost items into the 'collection_cost' dataframe:

        collection_cost = pd.DataFrame([],columns = ['Type of cost', 'Cost USD', 'Phase of construction'])  # todo: I believe Phase of construction here is the same as Operation ID in other modules? we should change to be consistent

        collection_cost = collection_cost.append(trenching_equipment_rental_cost_df)
        collection_cost = collection_cost.append(trenching_labor_cost_df)
        collection_cost = collection_cost.append(cable_cost_usd_per_LF_df)

        # Calculate Mobilization Cost and add to collection_cost dataframe.
        # For utility scale plants, mobilization is assumed to be 5% of the sum of labor, equipment, and material costs.
        # For distributed mode, mobilization is a calculated % that is a function of turbine size.
        if calculate_costs_input_dict['num_turbines'] > 10:
            calculate_costs_output_dict['mob_cost'] = collection_cost['Cost USD'].sum() * 0.05
        else:
            if calculate_costs_input_dict['turbine_rating_MW'] >= 0.1:
                calculate_costs_output_dict['mob_cost'] = collection_cost[
                    'Cost USD'].sum() * self.mobilization_cost_multiplier(calculate_costs_input_dict['turbine_rating_MW'])

            # switch for small DW
            else:  # mobilization cost included in equipment rental cost
                calculate_costs_output_dict['mob_cost'] = 0.0

        mobilization_cost = pd.DataFrame([['Mobilization', calculate_costs_output_dict['mob_cost'], 'Collection']],

                                         columns=['Type of cost', 'Cost USD', 'Phase of construction'])
        collection_cost = collection_cost.append(mobilization_cost)



        #For LandBOSSE API, cost breakdown by type stored as floating point values:
        calculate_costs_output_dict['collection_equipment_rental_usd'] = calculate_costs_output_dict[
            'Equipment Cost USD with weather delays']
        calculate_costs_output_dict['collection_labor_usd'] = calculate_costs_output_dict[
            'Labor Cost USD with weather delays']
        calculate_costs_output_dict['collection_material_usd'] = self._total_cable_cost
        calculate_costs_output_dict['collection_mobilization_usd'] = calculate_costs_output_dict['mob_cost']


        calculate_costs_output_dict['total_collection_cost'] = collection_cost
        calculate_costs_output_dict['summed_collection_cost'] = collection_cost['Cost USD'].sum()   #for landbosse_api

        return collection_cost

    def outputs_for_detailed_tab(self, input_dict, output_dict):
        """
        Creates a list of dictionaries which can be used on their own or
        used to make a dataframe.

        Returns
        -------
        list(dict)
            A list of dicts, with each dict representing a row of the data.
        """
        result = []
        module = 'Collection Cost'

        result.append({
            'unit': 'km',
            'type': 'variable',
            'variable_df_key_col_name': 'Total trench length',
            'value': float(self.output_dict['trench_length_km'])
        })

        result.append({
            'unit': 'km',
            'type': 'variable',
            'variable_df_key_col_name': 'Total cable length',
            'value': float(self.output_dict['total_cable_len_km'])
        })
        cables = ''
        n = 1  # to keep tab of number of cables input by user.
        for cable, specs in self.output_dict['cables'].items():
            if n == len(self.output_dict['cables']):
                cables += str(cable)
            else:
                cables += str(cable) + '  ,  '

            for variable, value in specs.__dict__.items():
                if variable == 'array_cable_len':
                    result.append({
                        'unit': 'km',
                        'type': 'variable',
                        'variable_df_key_col_name': 'Array cable length for cable  ' + cable,
                        'value': float(value)
                    })
                elif variable == 'total_length':
                    result.append({
                        'unit': 'km',
                        'type': 'variable',
                        'variable_df_key_col_name': 'Total cable length for cable  ' + cable,
                        'value': float(value)
                    })

                elif variable == 'total_cost':
                    result.append({
                        'unit': 'usd',
                        'type': 'variable',
                        'variable_df_key_col_name': 'Total cable cost for cable  ' + cable,
                        'value': float(value)
                    })
            n += 1

        for row in self.output_dict['total_collection_cost'].itertuples():
            dashed_row = '{} <--> {} <--> {}'.format(row[1], row[3], math.ceil(row[2]))
            result.append({
                'unit': '',
                'type': 'dataframe',
                'variable_df_key_col_name': 'Type of Cost <--> Phase of Construction <--> Cost in USD ',
                'value': dashed_row,
                'last_number': row[2]
            })


        for _dict in result:
            _dict['project_id_with_serial'] = self.project_name
            _dict['module'] = module

        self.output_dict['collection_cost_csv'] = result
        return result

    def run_module(self):
        """
        Runs the CollectionCost module and populates the IO dictionaries with calculated values.

        """
        try:
            self.input_dict['time_construct'] = 'normal'
            self.input_dict['hour_day'] = {'long': 24, 'normal': 10}
            operational_hrs_per_day = self.input_dict['hour_day'][self.input_dict['time_construct']]
            self.input_dict['operational_hrs_per_day'] = operational_hrs_per_day
            self.create_manual_ArraySystem()
            project_input_dict = self.input_dict['project_input_dict']
            self.calculate_trench_properties(self.input_dict, self.output_dict)
            operation_data = self.estimate_construction_time(self.input_dict, self.output_dict)
            number_of_months_for_construction = int(project_input_dict['Total project construction time (months)'])
            weather_window_input = self.input_dict['weather_window']
            weather_window_intermediate = read_weather_window(weather_window_input)
            extended_weather_window = extend_weather_window(weather_window_intermediate,
                                                            number_of_months_for_construction)
            self.input_dict['weather_window'] = extended_weather_window
            self.input_dict['wind_shear_exponent'] = project_input_dict['Wind shear exponent']

            # pull only global inputs for weather delay from input_dict
            weather_data_keys = ('wind_shear_exponent',
                                 'weather_window')
            # specify collection-specific weather delay inputs
            self.weather_input_dict = dict(
                [(i, self.input_dict[i]) for i in self.input_dict if i in set(weather_data_keys)])
            self.weather_input_dict[
                'start_delay_hours'] = 0  # assume zero start for when collection construction begins (start at beginning of construction time)
            self.weather_input_dict[
                'critical_wind_speed_m_per_s'] = project_input_dict['Non-Erection Wind Delay Critical Speed (m/s)']
            self.weather_input_dict[
                'wind_height_of_interest_m'] = project_input_dict['Non-Erection Wind Delay Critical Height (m)']

            # Compute the duration of the construction for electrical collection
            duration_construction = operation_data['Time construct days'].max(skipna=True)
            days_per_month = 30
            duration_construction_months = duration_construction / days_per_month
            self.output_dict['collection_construction_months'] = duration_construction_months

            # compute and specify weather delay mission time for roads
            operational_hrs_per_day = self.input_dict['hour_day'][self.input_dict['time_construct']]
            mission_time_hrs = duration_construction * operational_hrs_per_day
            self.weather_input_dict['mission_time_hours'] = int(mission_time_hrs)

            self.calculate_weather_delay(self.weather_input_dict, self.output_dict)
            self.calculate_costs(self.input_dict, self.output_dict)
            self.outputs_for_detailed_tab(self.input_dict, self.output_dict)
            # self.output_dict['collection_cost_module_type_operation'] = self.outputs_for_costs_by_module_type_operation(
            #     input_df=self.output_dict['total_collection_cost'],
            #     project_id=self.project_name,
            #     total_or_turbine=True
            # )
            return 0, 0  # module ran successfully
        except Exception as error:
            traceback.print_exc()
            print(f"Fail {self.project_name} CollectionCost")
            self.input_dict['error']['CollectionCost'] = error
            return 1, error  # module did not run successfully

            # self.calculate_trench_properties(self.input_dict, self.output_dict)
            # operation_data = self.estimate_construction_time(self.input_dict, self.output_dict)
            # self.calculate_costs(self.input_dict, self.output_dict)



def get_hybrid_collection_cost_matrix(hybrid_input_dict, wind_x, wind_y):
    """
    Calculates the shared_interconnection costs through the given coordinate system

    """

    if hybrid_input_dict['shared_collection_system']:
        collection_layout = hybrid_input_dict['collection_layout'].values
        coordinate_labels_parts = collection_layout[:, 2:3]
        coordinate_labels = list()
        node_idxs = list()
        substation_count = 0
        for idx in range(0, len(coordinate_labels_parts)):
            label = coordinate_labels_parts[idx][0]
            if substation_count == 0 and label == 'substation':
                substation_count += 1
                coordinate_labels.append(label)
                node_idxs.append(idx)
            elif label == 'solar' or label == 'storage':
                coordinate_labels.append(label)
                node_idxs.append(idx)
            elif label == 'wind':
                pass
            else:
                if substation_count > 1:
                    exit('ERROR: mismatch between # substation nodes')


        xcoordinates_parts = collection_layout[:, :1]
        xcoordinates = list()
        for idx in range(0, len(xcoordinates_parts)):
                coord = xcoordinates_parts[idx][0]
                if idx in node_idxs:
                    xcoordinates.append(coord)


        ycoordinates_parts = collection_layout[:, 1:2]
        ycoordinates = list()
        for idx in range(0, len(ycoordinates_parts)):
                coord = ycoordinates_parts[idx][0]
                if idx in node_idxs:
                    ycoordinates.append(coord)

        coordinate_labels.append('wind_sub')
        node_idxs.append(len(node_idxs))
        xcoordinates.append(wind_x)
        ycoordinates.append(wind_y)

        substation_idx = coordinate_labels.index('substation')
        substation_x = xcoordinates[substation_idx]
        substation_y = ycoordinates[substation_idx]
        xcoordinates.pop(substation_idx)
        ycoordinates.pop(substation_idx)
        if len(xcoordinates) > 0:
            g = Graph(xcoordinates, ycoordinates, substation_x=substation_x, substation_y=substation_y)
            g.primMST()
            return g.adj, g.xCoords, g.yCoords, coordinate_labels, substation_x, substation_y
        else:
            exit("ERROR: Not enough nodes in adjacency matrix")
        # Calculate segment length for total cabeling, find power rating of system
    else:
        exit('ERROR')


def get_wind_adj_matrix(hybrid_input_dict):
    """
    Returns wind turbine ADJ
    matrix from coordinates
    """
    if hybrid_input_dict['shared_collection_system']:
        collection_layout = hybrid_input_dict['collection_layout'].values

        coordinate_labels_parts = collection_layout[:, 2:3]
        coordinate_labels = list()
        wind_turbine_idxs = list()
        for item in coordinate_labels_parts:
            for label in item:
                coordinate_labels.append(label)
        substation_count = 0
        substation_idx = 0
        for index in range(0, len(coordinate_labels)):
            if substation_count == 0 and coordinate_labels[index] == 'substation':
                substation_count += 1
                substation_idx = index
            if coordinate_labels[index] == 'wind':
                wind_turbine_idxs.append(index)
            else:
                if substation_count > 1:
                    exit('ERROR: mismatch between # substation nodes')

        xcoordinates_parts = collection_layout[:, :1]
        xcoordinates = list()
        for item in xcoordinates_parts:
            for coord in item:
                xcoordinates.append(coord)

        ycoordinates_parts = collection_layout[:, 1:2]
        ycoordinates = list()
        for item in ycoordinates_parts:
            for coord in item:
                ycoordinates.append(coord)

        substation_x = xcoordinates[substation_idx]
        substation_y = ycoordinates[substation_idx]
        xcoordinates_wind = [xcoordinates[i] for i in wind_turbine_idxs]
        ycoordinates_wind = [ycoordinates[i] for i in wind_turbine_idxs]
        xcoordinates.pop(substation_idx)
        ycoordinates.pop(substation_idx)
        if len(xcoordinates_wind) > 0:
            g = Graph(xcoordinates_wind, ycoordinates_wind, substation_x=substation_x, substation_y=substation_y)
            g.primMST()
        else:
            exit('ERROR not enough wind turbines present')
        return g.adj, g.xCoords, g.yCoords, substation_x, substation_y
    else:
        exit('ERROR')

def get_ac_hybrid_matrix(hybrid_input_dict):
    """
           Calculates the shared_interconnection costs through the given coordinate system

           """
    #Substation must be at idx 0
    xcoordinates = hybrid_input_dict['x_coordinate_layout']
    ycoordinates = hybrid_input_dict['y_coordinate_layout']
    coordinate_labels = hybrid_input_dict['type_layout']

    non_ac = ['solar', 'storage']
    sub_loc = hybrid_input_dict['sub_loc']
    xcoordinates.insert(0, sub_loc[0])
    ycoordinates.insert(0, sub_loc[1])
    for module in non_ac:
        while coordinate_labels.count(module) != 0:
            end = coordinate_labels.index(module)
            coordinate_labels.pop(end)
            xcoordinates.pop(end)
            ycoordinates.pop(end)

    substation_idx = coordinate_labels.index('substation')
    substation_x = xcoordinates[substation_idx]
    substation_y = ycoordinates[substation_idx]
    xcoordinates.pop(substation_idx)
    ycoordinates.pop(substation_idx)
    if len(xcoordinates) > 0:
        g = Graph(xcoordinates, ycoordinates, substation_x=substation_x, substation_y=substation_y)
        g.primMST()
        return g.adj, g.xCoords, g.yCoords, coordinate_labels
    else:
        print(xcoordinates, ycoordinates)
        exit("ERROR: Not enough nodes in adjacency matrix")


def get_dc_hybrid_matrix(hybrid_input_dict):
    """
        Calculates the shared_interconnection costs through the given coordinate system

        """
    xcoordinates = hybrid_input_dict['x_coordinate_layout']
    ycoordinates = hybrid_input_dict['y_coordinate_layout']
    coordinate_labels = hybrid_input_dict['type_layout']


    #removes all wind
    while coordinate_labels.count('wind_sub') != 0:
        end = coordinate_labels.index('wind_sub')
        coordinate_labels.pop(end)
        xcoordinates.pop(end)
        ycoordinates.pop(end)

    substation_idx = coordinate_labels.index('substation')
    substation_x = xcoordinates[substation_idx]
    substation_y = ycoordinates[substation_idx]
    xcoordinates.pop(substation_idx)
    ycoordinates.pop(substation_idx)
    if len(xcoordinates) > 0:
        g = Graph(xcoordinates, ycoordinates, substation_x=substation_x, substation_y=substation_y)
        g.primMST()
        return g.adj, g.xCoords, g.yCoords, coordinate_labels
    else:
        print(xcoordinates, ycoordinates)
        exit("ERROR: Not enough nodes in adjacency matrix")
    # Calculate segment length for total cabeling, find power rating of system
