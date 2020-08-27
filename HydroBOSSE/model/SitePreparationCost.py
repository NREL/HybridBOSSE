import pandas as pd
import numpy as np
import math
import traceback
from CostModule import CostModule




# TODO: Add implementation of road quality
class SitePreparationCost(CostModule):
    """
    **SitePreparationCost.py**

    - Created by Annika Eberle and Owen Roberts on Apr. 3, 2018

    - Refactored by Parangat Bhaskar and Alicia Key on Jun 3, 2019

    - Modified for use with HydroBOSSE by Aaron Barker on Jul. 6, 2020



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


    # Here one function shoudl suffice - sumproduct of array and multiply by the icc cost


    def calculate_siteprep_cost(self, input_dict, output_dict):
        """
        This is a BOS cost comming out of ICC
        """

        # load the USACost as input_dictionary?
        # Here inputdictionary should provide the filename to be used
        file_name = input_dict['file_name']
        #file_name = 'project_list_30MW.xlsx'
        usacost = pd.read_excel(file_name, sheet_name='USACost')
        # usacost = pd.read_excel('project_list_30MW.xlsx', sheet_name='USACost')
        usacost["product08"] = usacost["%ICC(inFC)"] * usacost["08"]

        total_cost = usacost.sum(axis=0)[17]

        output_dict['site_preparation_cost'] = total_cost * self.output_dict['total_initial_capital_cost']

        return output_dict




    def run_module(self):
        """
        Runs the SitePreparation module and populates the IO dictionaries with calculated values.

        """
        try:
            self.calculate_siteprep_cost(self.input_dict, self.output_dict)
            return 0, 0  # module ran successfully
        except Exception as error:
            traceback.print_exc()
            print(f"Fail {self.project_name} SitePreparationCost")
            return 1, error  # module did not run successfully


