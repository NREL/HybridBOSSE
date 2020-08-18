import traceback
import pandas as pd
import math
from .CostModule import CostModule


class InverterTransformerErection(CostModule):
    """
    Cost of erecting the inverter+transformer container once the concrete pad
    has been constructed and is cured. This module calculates the cost of
    erecting the containers using 20-40 ton cranes.

    This module assumes that it takes 2 hours to offload each inverter+transformer
    container and place on it's respective concrete pad.

    """

    def __init__(self, input_dict, output_dict, project_name):
        super(InverterTransformerErection, self).__init__(input_dict, output_dict, project_name)
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.project_name = project_name
        if 'number_concrete_pads' in self.output_dict:
            self.number_concrete_pads = self.output_dict['number_concrete_pads']
        else:
            self.number_concrete_pads = self.input_dict['system_size_MW_AC'] / \
                                        (self.input_dict['inverter_rating_MW'] * 1000)

        # As mentioned in the module documentation, This module assumes that it takes
        # 2 hours to offload each inverter+transformer container and place on it's
        # respective concrete pad.
        self.total_crane_time = self.number_concrete_pads * 2   # hours

    def days_of_operation(self):
        """
        Calculate days of operation. Assumes a 10 hour workday.
        """
        days_of_operation = math.ceil(self.total_crane_time / self.input_dict['hour_day'])
        self.output_dict['crane_days_of_operation'] = days_of_operation
        return days_of_operation

    def crane_crew_cost(self):
        crew_cost = self.input_dict['crew_cost']
        crew = self.input_dict['crew'][self.input_dict['crew']
                                                ['Crew type ID'].str.contains('C0')]
        crane_crew = pd.merge(crew_cost, crew, on=['Labor type ID'])

        num_days = self.days_of_operation()

        per_diem = crane_crew['Per diem USD per day'] * \
                   crane_crew['Number of workers'] * \
                   num_days

        crane_crew = crane_crew.assign(per_diem_total=per_diem)
        hourly_costs_total = crane_crew['Hourly rate USD per hour'] * \
                             self.input_dict['hour_day'] * \
                             num_days

        crane_crew = crane_crew.assign(hourly_costs_total=hourly_costs_total)
        crane_crew['Cost USD'] = crane_crew['hourly_costs_total'] + \
                                      crane_crew['per_diem_total']

        labor_cost = crane_crew['Cost USD'].sum()

        return labor_cost

    def mobilization_cost(self):
        """
        Returns crane mobilization + demobilization cost (in USD).
        """
        # get mobilization cost:
        equip_price = self.input_dict['equip_price']
        mobilization_cost = equip_price['Mobilization cost USD'][0]
        return mobilization_cost

    def crane_rental_cost(self):
        """
        Returns total cost of crane rental (in USD).
        """
        # get equip rental cost:
        equip_price = self.input_dict['equip_price']
        crane_rental_cost = equip_price['Equipment price USD per hour'][0] * \
                            self.total_crane_time
        return crane_rental_cost

    def crane_fuel_cost(self):
        """
        Returns total cost of crane fuel consumption (in USD).
        """
        # get equip rental cost:
        equip_price = self.input_dict['equip_price']
        crane_fuel_consumption_per_day = equip_price['Fuel consumption gal per day'][0]
        crane_fuel_cost = crane_fuel_consumption_per_day * self.input_dict['fuel_cost']
        return crane_fuel_cost

    def calculate_costs(self, input_dict, output_dict):
        """

        """
        # Initialize total cost data frame
        total_cost = pd.DataFrame(columns=['Type of cost',
                                                'Cost USD',
                                                'Phase of construction'])

        # Get labor cost
        labor_cost = self.crane_crew_cost()
        labor_cost_df = pd.DataFrame([['Labor',
                                     labor_cost,
                                     'InverterTransformerErection']],
                                   columns=['Type of cost',
                                            'Cost USD',
                                            'Phase of construction'])

        # Get crane rental cost:
        crane_rental_cost = self.crane_rental_cost()
        crane_rental_cost_df = pd.DataFrame([['Equipment Rental',
                                              crane_rental_cost,
                                              'InverterTransformerErection']],
                                            columns=['Type of cost',
                                                     'Cost USD',
                                                     'Phase of construction'])

        # Get any associated material costs:
        material_cost = 0
        material_cost_df = pd.DataFrame([['Material',
                                              material_cost,
                                              'InverterTransformerErection']],
                                            columns=['Type of cost',
                                                     'Cost USD',
                                                     'Phase of construction'])

        # Get fuel consumption cost:
        crane_fuel_cost = self.crane_fuel_cost()
        crane_fuel_cost_df = pd.DataFrame([['Fuel',
                                              crane_fuel_cost,
                                              'InverterTransformerErection']],
                                            columns=['Type of cost',
                                                     'Cost USD',
                                                     'Phase of construction'])

        # Get any associated other costs:
        other_cost = 0
        other_cost_df = pd.DataFrame([['Other',
                                              other_cost,
                                              'InverterTransformerErection']],
                                            columns=['Type of cost',
                                                     'Cost USD',
                                                     'Phase of construction'])

        # Get mobilization + demobilization cost:

        mob_cost = self.mobilization_cost()
        mob_cost_df = pd.DataFrame([['Mobilization',
                                     mob_cost,
                                     'InverterTransformerErection']],
                                   columns=['Type of cost',
                                            'Cost USD',
                                            'Phase of construction'])

        total_cost = total_cost.append(labor_cost_df)
        total_cost = total_cost.append(crane_rental_cost_df)
        total_cost = total_cost.append(material_cost_df)
        total_cost = total_cost.append(crane_fuel_cost_df)
        total_cost = total_cost.append(other_cost_df)
        total_cost = total_cost.append(mob_cost_df)

        self.output_dict['total_erection_cost_df'] = total_cost
        self.output_dict['total_erection_cost'] = total_cost['Cost USD'].sum()

    def run_module(self):
        """

        """
        try:
            self.calculate_costs(self.input_dict, self.output_dict)

            return 0, 0   # module ran successfully

        except Exception as error:
            traceback.print_exc()
            print(f"Fail {self.project_name} InverterTransformerErection")
            self.input_dict['error']['InverterTransformerErection'] = error
            return 1, error    # module did not run successfully
