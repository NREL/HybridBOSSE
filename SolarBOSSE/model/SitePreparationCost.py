import pandas as pd
import numpy as np
import math
import traceback
from .CostModule import CostModule


# TODO: Add implementation of road quality
class SitePreparationCost(CostModule):
    """
    **SitePreparationCost.py**

    - Created by Annika Eberle and Owen Roberts on Apr. 3, 2018

    - Refactored by Parangat Bhaskar and Alicia Key on Jun 3, 2019



    **Calculates cost of constructing roads for land-based wind projects:**

    - Get terrain complexity

    - Get turbine spacing

    - Get road width

    - Get number of turbines

    - Get turbine rating

    - Get duration of construction*  #todo: add to process diagram

    - Get road length

    - Get weather data

    - Get road thickness

    - Calculate volume of road based on road thickness, road width, and road length

    - Calculate road labor and equipment costs by operation and type using RSMeans data

    - Calculate man hours and equipment hours for compaction of soil based on road length, road thickness, soil type, road width, and equipment size

    - Calculate man hours and equipment hours for mass material movement based on land cover, terrain complexity, and road length

    - Calculate man hours and equipment hours for rock placement based on equipment size, distance to quarry, and volume of road

    - Calculate man hours and equipment hours for compaction of rock based on road length, road thickness, and rock type

    - Calculate man hours and equipment hours for final grading based on road length

    - Calculate quantity of materials based on volume of materials

    - Calculate material costs by type

    - Calculate material costs using quantity of materials by material type and material prices by material type

    - Sum road costs over all operations and material types to get total costs by type of cost (e.g., material vs. equipment)

    - Return total road costs by type of cost


    **Keys in the input dictionary are the following:**

    - road_length

    - road_width

    - road_thickness

    - crane_width

    - num_access_roads  #TODO: Add to excel inputs sheet

    - num_turbines

    - rsmeans (dataframe)

    - duration_construction

    - wind_delays

    - wind_delay_time

    - material_price (dataframe)

    - rsmeans_per_diem

    - rotor_diameter_m

    - turbine_spacing_rotor_diameters


    **Keys in the output dictionary are the following:**

    - road_length_m

    - road_volume_m3

    - depth_to_subgrade_m

    - crane_path_widthm

    - road_thickess_m

    - road_width_m

    - road_width_m

    - material_volume_cubic_yards

    - road_construction_time

    - topsoil_volume

    - embankment_volume_crane

    - embankment_volume_road

    - rough_grading_area

    - material_needs (dataframe)

    - operation_data (dataframe)

    - total_road_cost



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
        super(SitePreparationCost, self).__init__(input_dict, output_dict, project_name)
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.project_name = project_name

        # Conversion factors. Making this data private (hidden from outside of
        # this class):
        self._meters_per_foot = 0.3
        self._meters_per_inch = 0.025
        self._cubic_yards_per_cubic_meter = 1.30795
        self._square_feet_per_square_meter = 10.7639

        # cubic meters for crane pad and maintenance ring for each turbine
        # (from old BOS model - AI - Access Roads & Site Imp. tab cell J33)
        self._crane_pad_volume = 125

        # conversion factor for converting packed cubic yards to loose cubic
        # yards material volume is about 1.4 times greater than road volume
        # due to compaction
        self._yards_loose_per_yards_packed = 1.39

        # calculated road properties
        self._lift_depth_m = 0.2

    def calculate_road_properties(self, input_dict, output_dict):
        """
        Calculates the volume of road materials need based on length, width,
        and thickness of roads

        Parameters
        ----------

        int num_turbines
            number of turbines in wind farm

        unitless turbine_spacing_rotor_diameters
            Immediate spacing between two turbines as a function of rotor
            diameter

        int rotor_diameter_m
            Rotor diameter

        float crane_width
            Crane width in meters

        float road_thickness
            Road thickness in inches

        float road_width_ft
            Road width in feet



        Returns
        ----------

        road_length_m
            Calculated road length (in m)

        road_volume_m3
            Calculated road volume (in m^3)

        material_volume_cubic_yards
            Material volume required (in cubic yards) based on road volume


        """
        road_width_m = input_dict['road_width_ft'] * self._meters_per_foot
        road_thickness_m = input_dict['road_thickness_in'] * self._meters_per_inch

        # units of cubic meters
        output_dict['road_volume'] = input_dict['road_length_m'] * \
                                     road_width_m * road_thickness_m

        # in cubic meters
        output_dict['road_volume_m3'] = output_dict['road_volume'] + \
                                        self._crane_pad_volume

        output_dict['depth_to_subgrade_m'] = 0.1

        output_dict['crane_path_width_m'] = input_dict['crane_width'] + 1.5

        output_dict['road_thickness_m'] = road_thickness_m
        output_dict['road_width_m'] = road_width_m
        output_dict['material_volume_cubic_yards'] = output_dict['road_volume_m3'] * \
                                                     self._cubic_yards_per_cubic_meter * \
                                                     self._yards_loose_per_yards_packed

        return output_dict

    def estimate_construction_time(self, input_dict, output_dict):
        """
        Estimates construction time of roads for entire project.

        Parameters
        ----------
        float crane_path_width_m
            Width of crane path (in m)

        float road_length_m
            Road length (in m)

        float depth_to_subgrade_m
            Depth to subgarde (in m)

        float road_volume
            Road volume (in m^3)

        float road_thickness_m
            Road thickness (in m)



        Returns
        ----------

        pd.DataFrame operation_data
            Dataframe which conatains following outputs:

            -  Number of days required for construction

            - Number of crews required to complete roads construction in
            specified construction time

            - Cost of labor and equipment rental prior to weather delays

        """
        throughput_operations = input_dict['construction_estimator']
        # assumes road construction occurs for 20% of project time
        # TODO: Find new multiplier to replace 20%
        output_dict['road_construction_time'] = input_dict['construction_time_months'] * 0.20

        # Main switch between small DW wind and (utility scale + distributed wind)
        # select operations for roads module that have data
        operation_data = throughput_operations.where(
            throughput_operations['Module'] == 'Inter-array roads (Solar)').dropna(thresh=4)

        # create list of unique material units for operations
        list_units = operation_data['Units'].unique()

        # units: cubic yards
        output_dict['topsoil_volume'] = input_dict['site_prep_area_m2'] * \
                                        output_dict['depth_to_subgrade_m'] * \
                                        self._cubic_yards_per_cubic_meter

        # units: cubic yards
        output_dict['embankment_volume_crane'] = output_dict['crane_path_width_m'] * \
                                                 input_dict['road_length_m'] * \
                                                 output_dict['depth_to_subgrade_m'] * \
                                                 self._cubic_yards_per_cubic_meter

        # units: cubic yards road
        output_dict['embankment_volume_road'] = \
            output_dict['road_volume_m3'] * self._cubic_yards_per_cubic_meter * \
            math.ceil(output_dict['road_thickness_m'] / self._lift_depth_m)

        # here 10.76391 sq ft = 1 sq m
        output_dict['rough_grading_area'] = \
            (input_dict['site_prep_area_m2'] * 10.76391) / 100000

        material_quantity_dict = {
            'cubic yard': output_dict['topsoil_volume'],
            'embankment cubic yards crane': output_dict['embankment_volume_crane'],
            'embankment cubic yards road': output_dict['embankment_volume_road'],
            'loose cubic yard': output_dict['material_volume_cubic_yards'],
            'Each (100000 square feet)': output_dict['rough_grading_area']}

        material_needs = pd.DataFrame(columns=['Units', 'Quantity of material'])
        for unit in list_units:
            unit_quantity = pd.DataFrame([[unit, material_quantity_dict[unit]]],
                                         columns=['Units', 'Quantity of material'])
            material_needs = material_needs.append(unit_quantity)

        material_needs = material_needs.reset_index(drop=True)
        output_dict['material_needs'] = material_needs

        # join material needs with operational data to compute costs
        operation_data = pd.merge(
            operation_data, material_needs, on=['Units']).dropna(thresh=3)

        operation_data = operation_data.where(
            (operation_data['Daily output']).isnull() == False).dropna(thresh=4)

        # calculate operational parameters and estimate costs without weather delays
        operation_data['Number of days'] = \
            operation_data['Quantity of material'] / operation_data['Daily output']

        operation_data['Number of crews'] = np.ceil(
            (operation_data['Number of days'] / 30) / output_dict['road_construction_time'])

        operation_data['Cost USD without weather delays'] = \
            operation_data['Quantity of material'] * operation_data['Rate USD per unit']

        # if more than one crew needed to complete within construction duration then
        # assume that all construction happens within that window and use that time
        # frame for weather delays; if not, use the number of days calculated
        operation_data['time_construct_bool'] = \
            operation_data['Number of days'] > output_dict['road_construction_time'] * 30

        boolean_dictionary = {True: output_dict['road_construction_time'] * 30,
                              False: np.NAN}
        operation_data['time_construct_bool'] = \
            operation_data['time_construct_bool'].map(boolean_dictionary)

        operation_data['Time construct days'] = \
            operation_data[['time_construct_bool', 'Number of days']].min(axis=1)

        num_days = operation_data['Time construct days'].max()

        # pull out management data
        crew_cost = self.input_dict['crew_cost']

        crew = self.input_dict['crew'][
            self.input_dict['crew']['Crew type ID'].str.contains('M0')]

        management_crew = pd.merge(crew_cost, crew, on=['Labor type ID'])

        per_diem_total = management_crew['Per diem USD per day'] * \
                         management_crew['Number of workers'] * num_days
        management_crew = management_crew.assign(per_diem_total=per_diem_total)

        hourly_costs_total = management_crew['Hourly rate USD per hour'] * \
                             self.input_dict['hour_day'] * num_days
        management_crew = management_crew.assign(hourly_costs_total=hourly_costs_total)

        total_crew_cost_before_wind_delay = management_crew['per_diem_total'] + \
                                            management_crew['hourly_costs_total']
        management_crew = management_crew.assign(total_crew_cost_before_wind_delay=
                                                 total_crew_cost_before_wind_delay)

        self.output_dict['management_crew'] = management_crew
        self.output_dict['management_crew_cost'] = \
            management_crew['total_crew_cost_before_wind_delay'].sum()

        output_dict['operation_data'] = operation_data

        return operation_data

    def calculate_costs(self, input_dict, output_dict):
        """
        Function to calculate total labor, equipment, material, mobilization, and any
        other associated costs after factoring in weather delays.


        Parameters
        ----------
        pd.Dataframe RSMeans
            Dataframe containing labor and equipment rental costs

        pd.DataFrame operation_data
            DataFrame containing estimates for total roads construction time and cost


        Returns
        ----------

        pd.DataFrame total_road_cost
            Dataframe containing following calculated outputs (after weather delay
            considerations):

            - Total labor cost

            - Totoal material cost

            - Total equipment rental cost

            - Total mobilization cost

            - Any other related costs


        """
        construction_estimator = input_dict['construction_estimator']

        material_name = construction_estimator['Material type ID'].\
            where(construction_estimator['Module'] == 'Inter-array roads (Solar)').dropna().unique()

        material_vol = pd.DataFrame([[material_name[0],
                                      output_dict['material_volume_cubic_yards'],
                                      'Loose cubic yard']],
                                    columns=['Material type ID',
                                             'Quantity of material',
                                             'Units'])

        material_data = pd.merge(material_vol,
                                 input_dict['material_price'],
                                 on=['Material type ID'])

        material_data['Cost USD'] = material_data['Quantity of material'] * \
                            pd.to_numeric(material_data['Material price USD per unit'])

        # Material cost of inter-array roads:
        material_cost_of_roads = material_data['Quantity of material'].iloc[0] * \
                    pd.to_numeric(material_data['Material price USD per unit'].iloc[0])

        material_costs = pd.DataFrame([['Materials',
                                        float(material_cost_of_roads),
                                        'Inter-array roads (Solar)']],
                                      columns=['Type of cost',
                                               'Cost USD',
                                               'Phase of construction'])

        operation_data = self.estimate_construction_time(input_dict, output_dict)

        number_workers_combined = operation_data['Number of workers'] * \
                                  operation_data['Number of crews']
        per_diem = number_workers_combined * \
                   (operation_data['Time construct days'] +
                    np.ceil(operation_data['Time construct days'] / 7)) * \
                   input_dict['construction_estimator_per_diem']

        labor_per_diem = per_diem.dropna()

        # output_dict['Total per diem (USD)'] = per_diem.sum()
        labor_equip_data = pd.merge(operation_data[['Operation ID',
                                                    'Units',
                                                    'Quantity of material']],
                                    construction_estimator,
                                    on=['Units', 'Operation ID'])

        labor_equip_data['Calculated per diem'] = per_diem
        labor_data = labor_equip_data[labor_equip_data['Type of cost'] == 'Labor'].copy()

        labor_data['Cost USD'] = ((labor_data['Quantity of material'] *
                                   labor_data['Rate USD per unit'] *
                                   input_dict['overtime_multiplier']) +
                                  labor_per_diem
                                  )

        labor_for_inner_roads_cost_usd = labor_data['Cost USD'].sum() + \
                                         output_dict['management_crew_cost']
        labor_costs = pd.DataFrame([['Labor',
                                     float(labor_for_inner_roads_cost_usd),
                                     'Inter-array roads (Solar)']],
                                   columns=['Type of cost',
                                            'Cost USD',
                                            'Phase of construction'])

        # Filter out equipment costs from construction_estimator tab:
        equipment_data = labor_equip_data[
            labor_equip_data['Module'] == 'Inter-array roads (Solar)'].copy()

        equipment_data = equipment_data[
            equipment_data['Type of cost'] == 'Equipment rental'].copy()

        equipment_data['Cost USD'] = equipment_data['Quantity of material'] * \
                                     equipment_data['Rate USD per unit']

        equip_for_new_roads_cost_usd = equipment_data['Cost USD'].sum()

        equipment_costs = pd.DataFrame([['Equipment rental',
                                         float(equip_for_new_roads_cost_usd),
                                         'Inter-array roads (Solar)']],
                                       columns=['Type of cost',
                                                'Cost USD',
                                                'Phase of construction'])

        # Create empty road cost (showing cost breakdown by type) dataframe:
        road_cost = pd.DataFrame(columns=['Type of cost',
                                          'Cost USD',
                                          'Phase of construction'])

        # Place holder for any other costs not captured in the processes so far
        cost_adder = 0
        additional_costs = pd.DataFrame([['Other',
                                          float(cost_adder),
                                          'Inter-array roads (Solar)']],
                                        columns=['Type of cost',
                                                 'Cost USD',
                                                 'Phase of construction'])

        road_cost = road_cost.append(material_costs)
        road_cost = road_cost.append(equipment_costs)
        road_cost = road_cost.append(labor_costs)
        road_cost = road_cost.append(additional_costs)

        # Calculate mobilization costs:

        equip_material_mobilization_multiplier = \
            0.16161 * (self.input_dict['system_size_MW_DC'] ** (-0.135))

        material_mobilization_USD = material_cost_of_roads * \
                                    equip_material_mobilization_multiplier

        equipment_mobilization_USD = \
            equip_for_new_roads_cost_usd * \
            equip_material_mobilization_multiplier

        labor_mobilization_multiplier = \
            1.245 * (self.input_dict['system_size_MW_DC'] ** (-0.367))

        labor_mobilization_USD = labor_for_inner_roads_cost_usd * \
                                 labor_mobilization_multiplier

        siteprep_mobilization_usd = material_mobilization_USD + \
                                      equipment_mobilization_USD + \
                                      labor_mobilization_USD

        mobilization_costs = pd.DataFrame([['Mobilization',
                                            siteprep_mobilization_usd,
                                            'Inter-array roads (Solar)']],
                                          columns=['Type of cost',
                                                   'Cost USD',
                                                   'Phase of construction'])

        road_cost = road_cost.append(mobilization_costs)
        total_road_cost = road_cost
        output_dict['total_road_cost_df'] = total_road_cost
        output_dict['total_road_cost'] = total_road_cost['Cost USD'].sum()
        return total_road_cost

    def access_road_cost(self):
        """
        A solar array only needs an access road leading up to the array. The inter-array
        roads are lower quality, dirt roads that only need to be able to support ~20 ton
        loads on them. For access road construction, we just use LandBOSSE's SitePrepCost
        module to determine cost of access road construction.
        """
        pass    # TODO: add implementation


    def run_module(self):
        """
        Runs the SitePreparation module and populates the IO dictionaries with calculated values.

        """
        try:
            self.calculate_road_properties(self.input_dict, self.output_dict)
            self.estimate_construction_time(self.input_dict, self.output_dict)
            self.calculate_costs(self.input_dict, self.output_dict)
            return 0, 0  # module ran successfully
        except Exception as error:
            traceback.print_exc()
            print(f"Fail {self.project_name} SitePreparationCost")
            return 1, error  # module did not run successfully
