import traceback
import math
import numpy as np
import pandas as pd
from .CostModule import CostModule


class CollectionCost(CostModule):
    """
    - Created by Ben Anderson on June 3, 2020

    Calculates the cost of the collection system (cable runs that connect BESS containers to substation)
    Assumptions:
    1. Collection system extends in a straight line from substation to BESS location
    2. BESS containers are in a rectangular grid, and cables run in a grid between them.
       Cables join before run to substation
    3. Cable cost is a constant $/m. Cable sizes are neglected, as the majority of cable costs are from trenching
    """

    def __init__(self, input_dict, output_dict, project_name):
        super(CollectionCost, self).__init__(input_dict, output_dict, project_name)
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.project_name = project_name
        self.m_to_lf = 3.28084
        self._km_to_LF = 3.28084 * 1000

        # Max allowable voltage drop (VD%) in circuits
        self.allowable_vd_percent = 3 / 100

        # Specific resistivity of copper between 25 and 50 deg C:
        self.Cu_specific_resistivity = 11

    def calculate_costs(self):
        self.output_dict['total_collection_length'] = self.input_dict['distance_to_substation'] + \
                                                    self.output_dict['num_containers'] * (self.input_dict['container_width'] + 2*self.input_dict['container_pad_buffer'])
        self.output_dict['total_collection_cost'] = self.output_dict['total_collection_length'] * self.input_dict['collection_cost_per_m']

    def run_module(self):
        try:
            self.calculate_costs()
            return 0, 0  # module ran successfully

        except Exception as error:
            traceback.print_exc()
            print(f"Fail {self.project_name} CollectionCost")
            self.input_dict['error']['CollectionCost'] = error
            return 1, error  # module did not run successfully

