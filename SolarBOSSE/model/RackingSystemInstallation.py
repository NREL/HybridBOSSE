import traceback
import pandas as pd
import math
import numpy as np
from .CostModule import CostModule


class RackingSystemInstallation(CostModule):
    """
    Class for simulating installation of utility scale ground-mount
    racking system and panel installation. This portion of the project
    will take ~60% of project time. The following activities are
    considered in this class:
    1. Pile driven anchor placement - Using crane with hammer/pile
     driver attachment
    2. Racking system assembly
    3. Solar module installation
    4. Rack wiring
    5. String testing

    """
    def __init__(self, input_dict, output_dict, project_name):
        super(RackingSystemInstallation, self).__init__(input_dict, output_dict, project_name)
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.project_name = project_name

    def cost_per_table(self):
        # store user input balance of material (BOM):
        solar_BOM = self.input_dict['solar_BOM']
        part_per_table_USD = solar_BOM.usd_unit * solar_BOM.units_per_table

        # partial table cost excludes assembly hardware cost:
        partial_table_cost = part_per_table_USD.dropna().sum()
        # Assemble hardware consists of washers, bolts, nuts, wire management ties,
        # etc. Assembly hardware cost is assumed to be 10% of total cost of
        # rest of racking table:
        assembly_hardware_usd = 0.1 * partial_table_cost
        cost_per_table_usd = partial_table_cost + assembly_hardware_usd
        return cost_per_table_usd

    def racking_discount_multiplier(self):
        """
        Apply discounted multiplier for economies of scale. That is, if cost of racking
        calculated by cost_per_table() method is 0.3/Watts for a 1 MW system, apply
        discount (multiplier) to racking system cost for a larger system.
        """
        system_size_MW_DC = self.input_dict['system_size_MW_DC']
        if system_size_MW_DC <= 150:
            discount_multiplier = 1 - ((0.0018 * system_size_MW_DC) - 0.0018)
        else:
            discount_multiplier = 1 - ((0.0009 * system_size_MW_DC) + 0.1105)
        return discount_multiplier

    def racking_cost_USD_watt(self):
        rating_per_table_watts = 2 * 8 * self.input_dict['module_rating_W']
        self.output_dict['rating_per_table_watts'] = rating_per_table_watts

        racking_cost_USD_watt = (self.cost_per_table() / rating_per_table_watts) * \
                                self.racking_discount_multiplier()
        self.output_dict['racking_cost_USD_watt'] = racking_cost_USD_watt

    def total_racking_material_cost_USD(self):
        """
        Hardware cost only (USD)
        """
        total_racking_material_cost_USD = self.output_dict['racking_cost_USD_watt'] * \
                                 self.input_dict['system_size_MW_DC'] * 1e6
        self.output_dict['total_racking_material_cost_USD'] = total_racking_material_cost_USD
        return total_racking_material_cost_USD

    def total_foundation_holes(self):
        """
        Total nunmber of holes that will need to be pile driven. Assumes 3 holes
        per racking table.
        """
        rating_per_table_watts = 2 * 8 * self.input_dict['module_rating_W']
        project_rating_watts = self.input_dict['system_size_MW_DC'] * 1e6
        total_tables_project = project_rating_watts / rating_per_table_watts
        total_foundation_holes = total_tables_project * 3
        self.output_dict['total_foundation_holes'] = total_foundation_holes
        return total_foundation_holes

    def total_foundation_length_LF(self):
        total_foundation_holes = self.output_dict['total_foundation_holes']
        foundation_hole_ft = self.input_dict['foundation_hole_ft']
        total_foundation_length_LF = total_foundation_holes * foundation_hole_ft
        self.output_dict['total_foundation_length_LF'] = total_foundation_length_LF
        return total_foundation_length_LF

    def estimate_construction_time(self):
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
        throughput_operations = self.input_dict['construction_estimator']

        # assumes road construction occurs for 60% of project time
        self.output_dict['installation_time'] = \
            self.input_dict['construction_time_months'] * 0.6

        operation_data = throughput_operations.where(
            throughput_operations['Module'] == 'Racking System Installation').\
            dropna(thresh=4)

        # create list of unique material units for operations
        list_units = operation_data['Units'].unique()

        # units: linear foot (LF)
        total_foundation_length_LF = self.output_dict['total_foundation_length_LF']

        total_foundation_length_LF_dict = {
            '$/LF': total_foundation_length_LF}

        # Here material needs is equivalent to saying cumulative length of
        # foundation holes that need to be drilled:
        material_needs = pd.DataFrame(columns=['Units', 'Quantity of material'])
        for unit in list_units:
            unit_quantity = pd.DataFrame([[unit, total_foundation_length_LF_dict[unit]]],
                                         columns=['Units', 'Quantity of material'])
            material_needs = material_needs.append(unit_quantity)

        material_needs = material_needs.reset_index(drop=True)
        self.output_dict['material_needs'] = material_needs

        # join material needs with operational data to compute costs
        operation_data = pd.merge(
            operation_data, material_needs, on=['Units']).dropna(thresh=3)

        operation_data = operation_data.where(
            (operation_data['Daily output']).isnull() == False).dropna(thresh=4)

        # calculate operational parameters and estimate costs without weather delays
        operation_data['Number of days'] = \
            operation_data['Quantity of material'] / operation_data['Daily output']

        operation_data['Number of crews'] = \
            np.ceil((operation_data['Number of days'] / 30) /
                    self.output_dict['installation_time'])

        operation_data['Cost USD without weather delays'] = \
            operation_data['Quantity of material'] * operation_data['Rate USD per unit']

        # if more than one crew needed to complete within construction duration then
        # assume that all construction happens within that window and use that time
        # frame for weather delays; if not, use the number of days calculated
        operation_data['time_construct_bool'] = \
            operation_data['Number of days'] > self.output_dict['installation_time'] * 30

        boolean_dictionary = {True: self.output_dict['installation_time'] * 30,
                              False: np.NAN}
        operation_data['time_construct_bool'] = \
            operation_data['time_construct_bool'].map(boolean_dictionary)

        operation_data['Time construct days'] = \
            operation_data[['time_construct_bool', 'Number of days']].min(axis=1)


        # TODO: figure out if this cost is non-zero
        self.output_dict['management_crew_cost'] = 0

        self.output_dict['operation_data'] = operation_data

        return operation_data

    def calculate_costs(self):
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
        construction_estimator = self.input_dict['construction_estimator']

        material_costs = pd.DataFrame([['Materials',
                                        self.output_dict['total_racking_material_cost_USD'],
                                        'Racking System Installation']],
                                      columns=['Type of cost',
                                               'Cost USD',
                                               'Phase of construction'])

        operation_data = self.estimate_construction_time()

        number_workers_combined = operation_data['Number of workers'] * \
                                  operation_data['Number of crews']

        per_diem = number_workers_combined * \
                   (operation_data['Time construct days'] +
                    np.ceil(operation_data['Time construct days'] / 7)) * \
                   self.input_dict['construction_estimator_per_diem']

        labor_per_diem = per_diem.dropna()

        # self.output_dict['Total per diem (USD)'] = per_diem.sum()
        labor_equip_data = pd.merge(operation_data[['Operation ID',
                                                    'Units',
                                                    'Quantity of material']],
                                    construction_estimator,
                                    on=['Units', 'Operation ID'])

        labor_equip_data['Calculated per diem'] = per_diem

        labor_data = \
            labor_equip_data[labor_equip_data['Type of cost'] == 'Labor'].copy()

        labor_data['Cost USD'] = ((labor_data['Quantity of material'] *
                                   labor_data['Rate USD per unit'] *
                                   self.input_dict['overtime_multiplier']) +
                                  labor_per_diem
                                  )

        labor_racking_installation = labor_data['Cost USD'].sum() + \
                                         self.output_dict['management_crew_cost']
        labor_costs = pd.DataFrame([['Labor',
                                     float(labor_racking_installation),
                                     'Racking System Installation']],
                                   columns=['Type of cost',
                                            'Cost USD',
                                            'Phase of construction'])

        # Filter out equipment costs from construction_estimator tab:
        equipment_data = labor_equip_data[
            labor_equip_data['Type of cost'] == 'Equipment rental'].copy()

        equipment_data = equipment_data[
            equipment_data['Type of cost'] == 'Equipment rental'].copy()

        equipment_data['Cost USD'] = equipment_data['Quantity of material'] * \
                                     equipment_data['Rate USD per unit']

        equip_racking_installation = equipment_data['Cost USD'].sum()

        equipment_costs = pd.DataFrame([['Equipment rental',
                                         float(equip_racking_installation),
                                         'Racking System Installation']],
                                       columns=['Type of cost',
                                                'Cost USD',
                                                'Phase of construction'])

        # Create empty road cost (showing cost breakdown by type) dataframe:
        racking_cost = pd.DataFrame(columns=['Type of cost',
                                          'Cost USD',
                                          'Phase of construction'])

        # Place holder for any other costs not captured in the processes so far
        cost_adder = 0
        additional_costs = pd.DataFrame([['Other',
                                          float(cost_adder),
                                          'Racking System Installation']],
                                        columns=['Type of cost',
                                                 'Cost USD',
                                                 'Phase of construction'])

        racking_cost = racking_cost.append(material_costs)
        racking_cost = racking_cost.append(equipment_costs)
        racking_cost = racking_cost.append(labor_costs)
        racking_cost = racking_cost.append(additional_costs)

        # Calculate mobilization costs:
        # TODO: convert to user input:
        mob_cost_per_crew = 20000 # NCE 2017 : Pg 604
        labor_mobilization_multiplier = \
            1.245 * (self.input_dict['system_size_MW_DC'] ** (-0.367))

        labor_mobilization_USD = operation_data['Number of crews'][1] * mob_cost_per_crew * \
                                 labor_mobilization_multiplier

        equip_material_mobilization_multiplier = \
            0.16161 * (self.input_dict['system_size_MW_DC'] ** (-0.135))

        material_mobilization_USD = self.output_dict['total_racking_material_cost_USD'] * \
                                    equip_material_mobilization_multiplier

        equipment_mobilization_USD = float(equip_racking_installation) * \
                                     equip_material_mobilization_multiplier

        racking_mobilization_usd = material_mobilization_USD + \
                                    equipment_mobilization_USD + \
                                    labor_mobilization_USD

        mobilization_costs = pd.DataFrame([['Mobilization',
                                            racking_mobilization_usd,
                                            'Racking System Installation']],
                                          columns=['Type of cost',
                                                   'Cost USD',
                                                   'Phase of construction'])

        racking_cost = racking_cost.append(mobilization_costs)
        total_racking_cost = racking_cost
        self.output_dict['total_racking_cost_df'] = total_racking_cost
        self.output_dict['total_racking_cost_USD'] = total_racking_cost['Cost USD'].sum()
        return total_racking_cost

    def run_module(self):
        try:
            # Calculate racking material cost:
            self.racking_cost_USD_watt()
            self.total_racking_material_cost_USD()

            # total foundation results:
            self.total_foundation_holes()
            self.total_foundation_length_LF()

            # calculate total cost:
            # self.estimate_construction_time()
            self.calculate_costs()

            return self.output_dict

        except Exception as error:
            traceback.print_exc()
            print(f"Fail {self.project_name} RackingSystemInstallation")
            return 1, error # module did not run successfully
