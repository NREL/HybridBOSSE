import traceback
import math
import numpy as np
import pandas as pd
from .CostModule import CostModule


class CollectionCost(CostModule):
    """
    Assumptions:
    1. System contains central inverters of 1 MW rating each. The inverter being
    considered is a containerized solution which includes a co-located LV/MV
    transformer.
    2. PV array is rectangular in design, with an aspect ratio of 1.5:1::L:W
    3. Trench for buried cables from each string inverter runs along the perimeter
     of the system, and up till the combiner box placed at one of the 4 corners of the
     array.

     Shown below is a crude visualization of solar farm floor-plan considered in
     SolarBOSSE. As mentioned above, the aspect ratio of this solar farm is assumed
     to be 1.5:1::L:W. This is a simple, over-generalization of-course, given that it
     is the 1st version of SolarBOSSE (v.1.0.0). This model is being designed in such
     a way that any future interest to allow the user design project layout will be
     possible.

     Key:
     ||| - 3 phase HV power cables (gen-tie)

     ||  - main project road; assumed to have 20+ ton bearing capacity. Also contains
           trench along both sides of the road for output circuit cables (DC), as well
           as MV power cables from each inverter station going all the way to the
           substation.

     === - horizontal road running across the width of project land. Assumed to be of
           lower quality than the main project road, and not meant to support cranes.
           Smaller maintenance vehicles (like Ford F-150 permissible).



             [gen-tie to utility substation/point of interconnection]
                              |||
                              |||
                              |||
                              |||
                   ________   |||
     _____________|inverter|__|||____
    |            ||-------|          |
    |            ||       |substation|
    |            ||       |          |
    |            ||       |__________|
    |            ||                  |
    |            ||                  |
    |            ||________          |
    |            ||inverter|         |
    |============||==================|
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||________          |
    |            ||inverter|         |
    |============||==================|
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||________          |
    |            ||inverter|         |
    |============||==================|
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |____________||__________________|

    Module to calculate:
    1. Wiring requirements of system. This includes:
        a. Source circuit cabling (from string to combiner box located at end of each
         row). The combiner box capacity (number of strings per box) is a user input.
        b. Output circuit; from each combiner box to that string's inverter station.
        c. Power cable home run; from inverter/transformer station (where it is
        transformed to MV) to the plant's substation which is located at the long end
        of the plant.
    """

    def __init__(self, input_dict, output_dict, project_name):
        super(CollectionCost, self).__init__(input_dict, output_dict, project_name)
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.project_name = project_name
        self.m2_per_acre = 4046.86
        self.inch_to_m = 0.0254
        self.m_to_lf = 3.28084
        self._km_to_LF = 3.28084 * 1000

        # Max allowable voltage drop (VD%) in circuits
        self.allowable_vd_percent = 3 / 100

        # Specific resistivity of copper between 25 and 50 deg C:
        self.Cu_specific_resistivity = 11

    def land_dimensions(self):
        """
        Given user defined project area, and assumed aspect ratio of 1.5:1, calculate
        solar farm's length and width (in m)
        """
        land_area_acres = self.input_dict['site_prep_area_acres']
        land_area_m2 = land_area_acres * self.m2_per_acre

        # Determine width & length of project land respectively:
        land_width_m = (land_area_m2 / 1.5) ** 0.5
        self.output_dict['land_width_m'] = land_width_m
        land_length_m = 1.5 * land_width_m

        return land_length_m, land_width_m

    def get_quadrant_dimensions(self):
        """
        1 inverter for every 1 MW_DC worth of panels. Super imposing the project layout
        on a cartesian plane, the main project road (along the long edge of the land)
        is at x = 0. And the souther most part of the project land is at y = 0. The
        area covering each unit MW_DC worth of land will be referred to as a quadrant.

               y
               |
               |
    (-x) ------|----- x
               |
               |
              (-y)
        """
        # Get length and width of each quadrant:
        land_area_acres = self.input_dict['site_prep_area_acres_mw_dc']
        land_area_per_inverter_acres = land_area_acres * \
                                       (self.input_dict['inverter_rating_kW'] / 1000)

        land_area_m2 = land_area_per_inverter_acres * self.m2_per_acre

        # Determine width & length of project land respectively:
        land_width_m = self.output_dict['land_width_m']
        subarray_width_m = land_width_m / 2
        self.output_dict['subarray_width_m'] = subarray_width_m
        land_length_m = land_area_m2 / land_width_m

        return land_length_m, land_width_m

    def inverter_list(self):
        """
        Return a tuple of inverters in the project
        """
        # Get number of inverters in the project
        # dividing by 150 because that's the upper limit on the size of 1 region.
        # Where 1 region is the max size of PV array that the collection module
        # runs for. If the project size is greater than size of region,
        # SolarBOSSE runs the collection cost module
        # (floor(project_size / region) + 1) times.
        if self.input_dict['system_size_MW_DC'] > 150:
            number_of_inverters = 150
        else:
            number_of_inverters = self.input_dict['system_size_MW_DC']

        inverter_list = [n for n in range(round(number_of_inverters))]
        self.output_dict['inverter_list'] = inverter_list
        return inverter_list

    def number_panels_along_x(self):
        """
        Assuming portrait orientation of modules, with 2 modules stacked end-to-end.
        """
        subarray_width_m = self.output_dict['subarray_width_m']

        # Adding 1 inch for mid clamp:
        panel_width_m = self.input_dict['module_width_m'] + self.inch_to_m

        number_panels_along_x = math.floor(subarray_width_m / panel_width_m)
        return number_panels_along_x

    def number_rows_per_subquadrant(self):
        """
        2 sub-quadrants per quadrant; one sub-quadrant on either side of the main
        project road. 2 sub arrays per quadrant; accordingly, 1 sub-array per
        sub-quadrant. And each sub-quadrant is rated for half of quadrant's DC
        rating.
        """
        module_rating_W = self.input_dict['module_rating_W']

        # multiplied by 2 since 2 modules end-to-end in portrait orientation
        single_row_rating_W = 2 * self.number_panels_along_x() * module_rating_W

        # Since each quadrant is sized according to inverter rating (DC)
        inverter_rating_W = self.input_dict['inverter_rating_kW'] * 1000 * \
                            self.input_dict['dc_ac_ratio']
        num_rows_sub_quadrant = math.floor((inverter_rating_W / 2) / single_row_rating_W)
        return num_rows_sub_quadrant

    def number_modules_per_string(self):
        """
        Calculate number of modules per string based on module V_oc and inverter max
        MPPT DC voltage
        """
        number_modules_per_string = math.floor(self.input_dict['inverter_max_mppt_V_DC'] /
                                           self.input_dict['module_V_oc'])

        # string open circuit voltage (used later in VD% calculations):
        self.output_dict['string_V_oc'] = number_modules_per_string * \
                                          self.input_dict['module_V_oc']

        return number_modules_per_string

    def num_strings_per_row(self):
        """
        Combined number of strings from both sub rows
        """
        number_panels_along_x = self.number_panels_along_x()

        # Multiplying by 2 since there are 2 sub rows per row
        num_strings_per_row = 2 * math.floor(number_panels_along_x /
                                             self.number_modules_per_string())
        return num_strings_per_row

    def distance_to_combiner_box(self, number_of_strings):
        """
        Cumulative distance to combiner box at end of each row for all strings in a
        row. Note that this is only the cumulative length of source circuits for 1 of
        the 2 sub rows in a row. Remember that each row has 2 panels in portrait
        orientation stacked end-to-end. Multiply result obtained form this method by
        2 to get total cumulative length of source circuit wire for entire row.
        """
        distance_to_combiner_box = 0    # initialize

        number_modules_per_string = self.number_modules_per_string()

        # Get module length (plus 1" width of mid clamp):
        module_width_m = self.input_dict['module_width_m'] + self.inch_to_m

        number_of_strings_per_sub_row = int(number_of_strings / 2)

        for i in range(number_of_strings_per_sub_row):
            if 0 == i:
                # Distance of terminal module in 1st string from combiner box:
                distance_to_combiner_box = (i + 1) * module_width_m * \
                                           number_modules_per_string

                adder = distance_to_combiner_box + module_width_m

            else:
                # Where adder is the first module in subsequent strings
                distance_to_combiner_box += adder + ((i + 1) * module_width_m *
                                                     number_modules_per_string)

                adder = ((i + 1) * module_width_m * number_modules_per_string) + \
                        module_width_m

        return distance_to_combiner_box

    def source_circuit_wire_length_lf(self,
                                      num_strings_per_row,
                                      number_rows_per_subquadrant):
        """
        Determine total source circuit wire length for each quadrant
        """

        distance_to_combiner_box_per_row = \
            self.distance_to_combiner_box(num_strings_per_row)

        # Multiply by 2 since there are 2 sets of rows in a quadrant:
        source_circuit_wire_length_m = distance_to_combiner_box_per_row * \
                                        number_rows_per_subquadrant * 2

        source_circuit_wire_length_lf = source_circuit_wire_length_m * self.m_to_lf

        return source_circuit_wire_length_lf

    def source_circuit_wire_length_total_lf(self, source_circuit_wire_length_lf,
                                           num_quadrants):
        """
        Returns combined source circuit wire length for all quadrants combined. This
        includes length of wire in each sub row of each sub quadrant.

        Accordingly, length of wire for both sub rows of every row, and both sub
        quadrants of a quadrant has been accounted for up till this point.
        """

        source_circuit_wire_length_total_lf = \
            source_circuit_wire_length_lf * num_quadrants

        self.output_dict['source_circuit_wire_length_total_lf'] = \
            source_circuit_wire_length_total_lf

        return source_circuit_wire_length_total_lf

    def pv_wire_cost(self, system_size_MW_DC, circuit_type, circuit_amps):
        """
        Empirical curve fit of pv wire cost ($/LF) for AWG #10 wire or smaller.
        """
        if system_size_MW_DC > 500:
            volume_order_discount_multiplier = 0.50  # 25 % discount (volume pricing)
        elif system_size_MW_DC > 300:
            volume_order_discount_multiplier = 0.70  # 25 % discount (volume pricing)
        elif system_size_MW_DC > 150:
            volume_order_discount_multiplier = 0.75     # 25 % discount (volume pricing)
        elif system_size_MW_DC > 50:
            volume_order_discount_multiplier = 0.80    # 20 % discount (volume pricing)
        elif system_size_MW_DC > 20:
            volume_order_discount_multiplier = 0.90
        else:
            volume_order_discount_multiplier = 1

        pv_wire_DC_specs = self.input_dict['pv_wire_DC_specs']
        if circuit_type is 'source_circuit':
            cost_usd_lf = pv_wire_DC_specs.loc[
                pv_wire_DC_specs['Size (AWG or kcmil)'] == 10, 'Cost (USD/LF)']

            cost_usd_lf = cost_usd_lf.iloc[0]

        elif circuit_type is 'output_circuit':
            if circuit_amps >= 175:
                cost_usd_lf = \
                    pv_wire_DC_specs.loc[
                        pv_wire_DC_specs['Temperature Rating of Conductor at 75°C ' \
                                         '(167°F) in Amps'] == 175, 'Cost (USD/LF)']
            else:
                cost_usd_lf = \
                    pv_wire_DC_specs.loc[
                        pv_wire_DC_specs['Temperature Rating of Conductor at 75°C ' \
                                         '(167°F) in Amps'] == 150, 'Cost (USD/LF)']

            cost_usd_lf = cost_usd_lf.iloc[0]

        pv_wire_cost = cost_usd_lf * volume_order_discount_multiplier     # $/LF

        return pv_wire_cost

    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><
    # Output circuit calculations:
    def number_strings_quadrant(self, num_strings_per_row, num_rows_per_subquadrant):
        """
        Get number of strings in each quadrant
        """
        number_strings_quadrant = num_strings_per_row * num_rows_per_subquadrant * 2
        return number_strings_quadrant

    def num_strings_parallel(self, num_strings_per_row):
        """
        Starting with the highest allowable number of strings in parallel as possible.
        This is to ensure highest possible output circuit ampacity, which would lead
        to lowest possible max allowable circuit resistance.

        """
        if num_strings_per_row > 24:
            num_strings_parallel = 24
        else:
            num_strings_parallel = num_strings_per_row

        return int(num_strings_parallel)

    def output_circuit_ampacity(self, num_strings_in_parallel):
        """

        """
        string_short_circuit_current = self.input_dict['module_I_SC_DC']

        # Consider 25% safety factor for over irradiance / over-current scenarios
        over_current_factor = 1.25

        output_circuit_ampacity = over_current_factor * \
                                  string_short_circuit_current * \
                                  num_strings_in_parallel

        return output_circuit_ampacity

    def row_spacing_m(self, quadrant_length_m, number_rows_per_subquadrant):
        """

        """
        row_spacing_m = quadrant_length_m / number_rows_per_subquadrant
        return row_spacing_m

    def voltage_drop_V(self):
        """
        Returns maximum allowable Voltage drop (in V) in an output circuit based on
        NEC guidelines.
        """
        voltage_drop_V = self.allowable_vd_percent * self.output_dict['string_V_oc']

        return voltage_drop_V

    def VD_passes(self,
                  circuit_length_m,
                  wire_R_per_kft,
                  max_VD,
                  output_circuit_ampacity):
        """
        Once the wire has been picked based on its ampacity, call this method to
        check whether the VD from using this wire exceeds 3%
        """
        R = wire_R_per_kft * (1 / 1000) * (circuit_length_m * self.m_to_lf)
        VD = R * output_circuit_ampacity
        if VD > max_VD:
            return False
        else:
            return True

    def circular_mils_area(self, circuit_length, current, VD):
        """
        Calculates the wire's circ mils area. This will help in selecting wire
        appropriate for wiring (based on its ampacity and ohms/kFT)
        """
        circular_mills_area = (circuit_length * self.Cu_specific_resistivity *
                               current) / VD
        return circular_mills_area

    def estimate_construction_time(self):
        """
        Function to estimate construction time on per turbine basis.

        Parameters
        -------
        duration_construction

        pd.DataFrame
            construction_estimator

        pd.DataFrame
            trench_length_km


        Returns
        -------

        (pd.DataFrame) operation_data

        """
        # assumes collection construction occurs for 45 % of project duration
        collection_construction_time = self.input_dict[
                                           'construction_time_months'] * 0.45

        throughput_operations = self.input_dict['construction_estimator']
        trench_length_km = self.output_dict['trench_length_km']

        operation_data = throughput_operations.where(
            throughput_operations['Module'] == 'Collection').dropna(thresh=4)

        source_wiring_operations = throughput_operations.where(
            throughput_operations['Module'] == 'Source circuit wiring').dropna(thresh=4)

        output_wiring_operations = throughput_operations.where(
            throughput_operations['Module'] == 'Output circuit wiring').dropna(thresh=4)

        # from construction_estimator data, only read in Collection related data and
        # filter out the rest:
        cable_trenching = throughput_operations[throughput_operations.Module == 'Collection']
        source_wiring = throughput_operations[throughput_operations.Module == 'Source circuit wiring']
        output_wiring = throughput_operations[throughput_operations.Module == 'Output circuit wiring']

        # Storing data with labor related inputs:
        trenching_labor = cable_trenching[cable_trenching.values == 'Labor']
        trenching_labor_usd_per_hr = trenching_labor['Rate USD per unit'].sum()

        self.output_dict['trenching_labor_usd_per_hr'] = trenching_labor_usd_per_hr

        # Units:  LF/day  -> where LF = Linear Foot
        trenching_labor_daily_output = trenching_labor['Daily output'].values[0]
        trenching_labor_num_workers = trenching_labor['Number of workers'].sum()

        # Get labor daily output for source circuit wiring:

        source_wiring_labor = source_wiring[source_wiring.Module == 'Source circuit wiring']

        source_circuit_daily_output = source_wiring_labor.loc[
            source_wiring_labor['Operation ID'] == 'Source circuit wiring', 'Daily output']
        source_circuit_daily_output = source_circuit_daily_output.iloc[0]
        self.output_dict['source_circuit_daily_output'] = source_circuit_daily_output

        # Get labor daily output for output circuit wiring:

        output_wiring_labor = output_wiring[output_wiring.Module == 'Output circuit wiring']

        output_circuit_daily_output = output_wiring_labor.loc[
            output_wiring_labor['Operation ID'] == 'Output circuit wiring', 'Daily output']
        output_circuit_daily_output = output_circuit_daily_output.iloc[0]
        self.output_dict['output_circuit_daily_output'] = output_circuit_daily_output

        # Storing data with equipment related inputs:
        trenching_equipment = cable_trenching[cable_trenching.values == 'Equipment']
        trenching_cable_equipment_usd_per_hr = trenching_equipment['Rate USD per unit'].sum()

        self.output_dict['trenching_cable_equipment_usd_per_hr'] = \
            trenching_cable_equipment_usd_per_hr

        # Units:  LF/day  -> where LF = Linear Foot
        trenching_equipment_daily_output = trenching_equipment['Daily output'].values[0]
        self.output_dict['trenching_labor_daily_output'] = trenching_labor_daily_output
        self.output_dict['trenching_equipment_daily_output'] = trenching_equipment_daily_output

        operation_data['Number of days taken by single crew'] = \
            ((trench_length_km * self._km_to_LF) / trenching_labor_daily_output)

        operation_data['Number of crews'] = \
            np.ceil((operation_data['Number of days taken by single crew'] / 30) /
                    collection_construction_time)

        operation_data['Cost USD without weather delays'] = \
            ((trench_length_km * self._km_to_LF) / trenching_labor_daily_output) * \
            (operation_data['Rate USD per unit'] * self.input_dict['hour_day'])

        # Repeat above steps, for cost of source circuit wiring

        source_wiring_operations['Number of days taken by single crew'] = \
            self.output_dict['source_circuit_wire_length_total_lf'] / source_circuit_daily_output

        source_wiring_operations['Number of crews'] = \
            np.ceil((source_wiring_operations['Number of days taken by single crew'] / 30) /
                    collection_construction_time)

        source_wiring_operations['Cost USD without weather delays'] = \
            self.output_dict['source_circuit_wire_length_total_lf'] * \
            source_wiring_operations['Rate USD per unit']

        self.output_dict['source_wiring_USD_lf'] = \
            source_wiring_operations['Rate USD per unit'].iloc[0]

        # Repeat above steps, for cost of output circuit wiring

        output_wiring_operations['Number of days taken by single crew'] = \
            self.output_dict['output_circuit_wire_length_total_lf'] / output_circuit_daily_output

        output_wiring_operations['Number of crews'] = \
            np.ceil((output_wiring_operations['Number of days taken by single crew'] / 30) /
                    collection_construction_time)

        output_wiring_operations['Cost USD without weather delays'] = \
            self.output_dict['output_circuit_wire_length_total_lf'] * \
            output_wiring_operations['Rate USD per unit']

        self.output_dict['output_wiring_USD_lf'] = \
            output_wiring_operations['Rate USD per unit'].iloc[0]

        alpha = operation_data[operation_data['Type of cost'] == 'Labor']
        operation_data_id_days_crews_workers = alpha[['Operation ID',
                                                      'Number of days taken by single crew',
                                                      'Number of crews',
                                                      'Number of workers']]

        source_wiring_alpha = source_wiring_operations[source_wiring_operations['Type of cost'] == 'Labor']
        source_wiring_id_days_crews_workers = source_wiring_alpha[['Operation ID',
                                                                    'Number of days taken by single crew',
                                                                    'Number of crews',
                                                                    'Number of workers']]

        output_wiring_alpha = output_wiring_operations[output_wiring_operations['Type of cost'] == 'Labor']
        output_wiring_id_days_crews_workers = output_wiring_alpha[['Operation ID',
                                                                   'Number of days taken by single crew',
                                                                   'Number of crews',
                                                                   'Number of workers']]

        operation_data_id_days_crews_workers = pd.merge(operation_data_id_days_crews_workers,
                                                        source_wiring_id_days_crews_workers,
                                                        how='outer')

        operation_data_id_days_crews_workers = pd.merge(operation_data_id_days_crews_workers,
                                                        output_wiring_id_days_crews_workers,
                                                        how='outer')

        operation_data = pd.merge(operation_data, source_wiring_operations, how='outer')
        operation_data = pd.merge(operation_data, output_wiring_operations, how='outer')

        # if more than one crew needed to complete within construction duration then
        # assume that all construction happens within that window and use that timeframe
        # for weather delays;
        # if not, use the number of days calculated
        operation_data['time_construct_bool'] = \
            operation_data['Number of days taken by single crew'] > \
            (collection_construction_time * 30)

        boolean_dictionary = {True: collection_construction_time * 30, False: np.NAN}
        operation_data['time_construct_bool'] = \
            operation_data['time_construct_bool'].map(boolean_dictionary)

        operation_data['Time construct days'] = \
            operation_data[['time_construct_bool',
                            'Number of days taken by single crew']].min(axis=1)

        self.output_dict['num_days'] = operation_data['Time construct days'].max()

        self.output_dict['managament_crew_cost_before_wind_delay'] = 0

        self.output_dict['operation_data_id_days_crews_workers'] = \
            operation_data_id_days_crews_workers

        self.output_dict['operation_data_entire_farm'] = operation_data

        return self.output_dict['operation_data_entire_farm']

    def calculate_costs(self):

        # Read in construction_estimator data:
        # construction_estimator = input_dict['construction_estimator']
        operation_data = self.output_dict['operation_data_entire_farm']

        per_diem = operation_data['Number of workers'] * \
                   operation_data['Number of crews'] * \
                   (operation_data['Time construct days'] +
                    np.ceil(operation_data['Time construct days'] / 7)) * \
                   self.input_dict['construction_estimator_per_diem']

        per_diem = per_diem.dropna()

        self.output_dict['time_construct_days'] = \
            (self.output_dict['trench_length_km'] * self._km_to_LF) / \
            self.output_dict['trenching_labor_daily_output']

        # weather based delays not yet implemented in SolarBOSSE
        self.output_dict['wind_multiplier'] = 1     # Placeholder

        # Calculating trenching cost:
        self.output_dict['Days taken for trenching (equipment)'] = \
            (self.output_dict['trench_length_km'] * self._km_to_LF) / \
            self.output_dict['trenching_equipment_daily_output']

        self.output_dict['Equipment cost of trenching per day {usd/day)'] = \
            self.output_dict['trenching_cable_equipment_usd_per_hr'] * \
            self.input_dict['hour_day']

        self.output_dict['Equipment Cost USD without weather delays'] = \
            self.output_dict['Days taken for trenching (equipment)'] * \
            self.output_dict['Equipment cost of trenching per day {usd/day)']

        self.output_dict['Equipment Cost USD with weather delays'] = \
            self.output_dict['Equipment Cost USD without weather delays'] * \
            self.output_dict['wind_multiplier']

        trenching_equipment_rental_cost_df = \
            pd.DataFrame([['Equipment rental',
                           self.output_dict['Equipment Cost USD with weather delays'],
                           'Collection']],
                         columns=['Type of cost',
                                    'Cost USD',
                                    'Phase of construction'])

        # Calculating trenching labor cost:
        self.output_dict['Days taken for trenching (labor)'] = \
            ((self.output_dict['trench_length_km'] * self._km_to_LF) /
             self.output_dict['trenching_labor_daily_output'])

        self.output_dict['days_taken_source_wiring'] = \
            self.output_dict['source_circuit_wire_length_total_lf'] / \
            self.output_dict['source_circuit_daily_output']

        self.output_dict['days_taken_output_wiring'] = \
            self.output_dict['output_circuit_wire_length_total_lf'] / \
            self.output_dict['output_circuit_daily_output']

        self.output_dict['Labor cost of trenching per day (usd/day)'] = \
            (self.output_dict['trenching_labor_usd_per_hr'] *
             self.input_dict['hour_day'] *
             self.input_dict['overtime_multiplier'])

        self.output_dict['Labor cost of source wiring per day (usd/day)'] = \
            (self.output_dict['source_circuit_daily_output'] *
             self.output_dict['source_wiring_USD_lf'] *
             self.input_dict['overtime_multiplier'])

        self.output_dict['Labor cost of output wiring per day (usd/day)'] = \
            (self.output_dict['output_circuit_daily_output'] *
             self.output_dict['output_wiring_USD_lf'] *
             self.input_dict['overtime_multiplier'])

        self.output_dict['Total per diem costs (USD)'] = per_diem.sum()

        foo = self.output_dict['Labor cost of source wiring per day (usd/day)'] * \
              self.output_dict['days_taken_source_wiring']

        self.output_dict['Labor Cost USD without weather delays'] = \
            ((self.output_dict['Days taken for trenching (labor)'] *
              self.output_dict['Labor cost of trenching per day (usd/day)']
              ) +
             (self.output_dict['Labor cost of source wiring per day (usd/day)'] *
              self.output_dict['days_taken_source_wiring']
              ) +
             (self.output_dict['Labor cost of output wiring per day (usd/day)'] *
              self.output_dict['days_taken_output_wiring']
              ) +
             (self.output_dict['Total per diem costs (USD)'] +
              self.output_dict['managament_crew_cost_before_wind_delay']
              ))

        self.output_dict['Labor Cost USD with weather delays'] = \
            self.output_dict['Labor Cost USD without weather delays'] * \
            self.output_dict['wind_multiplier']

        trenching_labor_cost_df = pd.DataFrame([['Labor',
                                                 self.output_dict['Labor Cost USD with weather delays'],
                                                 'Collection']],
                                               columns=['Type of cost',
                                                        'Cost USD',
                                                        'Phase of construction'])

        # Calculate cable cost:
        cable_cost_usd_per_LF_df = pd.DataFrame([['Materials',
                                                  self.output_dict['total_material_cost'],
                                                  'Collection']],
                                                columns=['Type of cost',
                                                         'Cost USD',
                                                         'Phase of construction'])

        # Combine all calculated cost items into the 'collection_cost' data frame:
        collection_cost = pd.DataFrame([], columns=['Type of cost',
                                                    'Cost USD',
                                                    'Phase of construction'])

        collection_cost = collection_cost.append(trenching_equipment_rental_cost_df)
        collection_cost = collection_cost.append(trenching_labor_cost_df)
        collection_cost = collection_cost.append(cable_cost_usd_per_LF_df)

        # Calculate Mobilization Cost and add to collection_cost data frame:
        equip_material_mobilization_multiplier = \
            0.16161 * (self.input_dict['system_size_MW_DC'] ** (-0.135))

        material_mobilization_USD = self.output_dict['total_material_cost'] * \
                                          equip_material_mobilization_multiplier

        equipment_mobilization_USD = \
            self.output_dict['Equipment Cost USD with weather delays'] * \
            equip_material_mobilization_multiplier

        labor_mobilization_multiplier = \
            1.245 * (self.input_dict['system_size_MW_DC'] ** (-0.367))

        labor_mobilization_USD = \
            self.output_dict['Labor Cost USD with weather delays'] * \
            labor_mobilization_multiplier

        collection_mobilization_usd = material_mobilization_USD + \
                                      equipment_mobilization_USD + \
                                      labor_mobilization_USD

        mobilization_cost = pd.DataFrame([['Mobilization',
                                           collection_mobilization_usd ,
                                           'Collection']],
                                         columns=['Type of cost',
                                                  'Cost USD',
                                                  'Phase of construction'])
        collection_cost = collection_cost.append(mobilization_cost)

        self.output_dict['total_collection_cost_df'] = collection_cost
        self.output_dict['total_collection_cost'] = collection_cost['Cost USD'].sum()

        return self.output_dict['total_collection_cost']

    def run_module_for_150_MW(self):
        """
        Runs the CollectionCost module and populates the IO dictionaries with
        calculated values.

        Parameters
        ----------
        <None>

        Returns
        -------
        tuple
            First element of tuple contains a 0 or 1. 0 means no errors happened
            and 1 means an error happened and the module failed to run. The second
            element either returns a 0 if the module ran successfully, or it returns
            the error raised that caused the failure.

        """

        # l = length ; w = width
        project_l_m, project_w_m = self.land_dimensions()
        l, w = self.get_quadrant_dimensions()
        num_quadrants = len(self.inverter_list())
        number_rows_per_subquadrant = self.number_rows_per_subquadrant()
        num_strings_per_row = self.num_strings_per_row()

        source_circuit_wire_length_lf =\
            self.source_circuit_wire_length_lf(num_strings_per_row,
                                               number_rows_per_subquadrant)

        source_circuit_wire_length_total_lf = \
            self.source_circuit_wire_length_total_lf(source_circuit_wire_length_lf,
                                                     num_quadrants)

        self.output_dict['source_circuit_wire_length_total_lf'] = \
            source_circuit_wire_length_total_lf

        # Begin output circuit calculations:
        num_strings_per_quadrant = \
            self.number_strings_quadrant(num_strings_per_row,
                                         number_rows_per_subquadrant)

        num_strings_parallel = self.num_strings_parallel(num_strings_per_row)

        row_spacing_m = self.row_spacing_m(l, number_rows_per_subquadrant)

        # make a list of rows in each quadrant:
        all_rows = [n for n in range(number_rows_per_subquadrant)]
        row_out_circuit_length_m = all_rows

        # starting with the bottom-most row in a quadrant (which is also the
        # farthest row from the inverter.
        total_out_circuit_length_m = 0  # Initialize
        for row in all_rows:
            row_inverter_distance_m = ((number_rows_per_subquadrant - 1) - row) * \
                                      row_spacing_m
            row_out_circuit_length_m[row] = row_inverter_distance_m * 2
            total_out_circuit_length_m += row_out_circuit_length_m[row]

        # total output circuit length for quadrant (2 sub quadrants per quadrant):
        TOC_length_quadrant_m = total_out_circuit_length_m * 2

        # Total output circuit length for entire farms (all quadrants combined):
        output_circuit_wire_length_total_lf = \
            TOC_length_quadrant_m * self.m_to_lf * num_quadrants

        self.output_dict[
            'output_circuit_wire_length_total_lf'] = output_circuit_wire_length_total_lf

        # Trench length for project (all quadrants combined):
        self.output_dict['trench_length_km'] = (project_l_m / 1000) * 2     # 2 trenches

        # Series of methods to select the right cable for output circuit:
        # Not using this set of implementations for now. That is, I'm assuming the
        # cable selected based solely on circuit ampacity also satisfies the 3 %
        # VD (max) requirement.

        # longest_output_circuit_m = row_out_circuit_length_m[0]
        # max_voltage_drop_V = self.voltage_drop_V()
        # self.VD_passes(longest_output_circuit_m, max_voltage_drop_V,
        # output_circuit_ampacity)

        output_circuit_ampacity = self.output_circuit_ampacity(num_strings_parallel)

        total_material_cost = source_circuit_wire_length_total_lf * \
                                self.pv_wire_cost(self.input_dict['system_size_MW_DC'],
                                                  'source_circuit',
                                                  self.input_dict['module_I_SC_DC'])

        total_material_cost += TOC_length_quadrant_m * self.m_to_lf * num_quadrants * \
                                self.pv_wire_cost(self.input_dict['system_size_MW_DC'],
                                                  'output_circuit',
                                                  output_circuit_ampacity)

        self.output_dict['total_material_cost'] = total_material_cost

        self.estimate_construction_time()
        self.output_dict['total_collection_cost'] = self.calculate_costs()


    def run_module(self):
        """

        """
        try:
            original_site_prep_area_acres = self.input_dict['site_prep_area_acres']
            regions_list = []
            region_iter = 0
            total_collection_cost = 0

            if self.input_dict['system_size_MW_DC'] > 150:
                site_prep_area_regions = self.input_dict['system_size_MW_DC'] / 150

                fraction_site_prep_area_regions = site_prep_area_regions - \
                                                  math.floor(site_prep_area_regions)

                region_iter = math.floor(site_prep_area_regions)

                for i in range(region_iter):
                    regions_list.append(150)    # Stores size (in MW) of the region

                if fraction_site_prep_area_regions > 0:
                    regions_list.append(fraction_site_prep_area_regions * 150)

                for region in regions_list:
                    # Should be site_prep_area_acres_mw_dc and not site_prep_area_acres_mw_ac
                    self.input_dict['site_prep_area_acres'] = \
                        self.input_dict['site_prep_area_acres_mw_ac'] * region

                    self.run_module_for_150_MW()
                    total_collection_cost += self.output_dict['total_collection_cost']

            else:
                self.run_module_for_150_MW()
                total_collection_cost += self.output_dict['total_collection_cost']

            self.input_dict['site_prep_area_acres'] = original_site_prep_area_acres
            self.output_dict['total_collection_cost'] = total_collection_cost
            # self.output_dict['total_collection_cost'] = 65153571

            return 0, 0  # module ran successfully

        except Exception as error:
            traceback.print_exc()
            print(f"Fail {self.project_name} CollectionCost")
            self.input_dict['error']['CollectionCost'] = error
            return 1, error  # module did not run successfully


