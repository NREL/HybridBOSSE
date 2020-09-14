import traceback
import pandas as pd
import math
from HydroBOSSE.model.CostModule import CostModule


class GridConnectionCost(CostModule):
    """
    TransDistCost.py
     - Created by Annika Eberle and Owen Roberts on Dec. 17, 2018
     - Refactored by Parangat Bhaskar and Alicia Key on June 3, 2019

    Calculates the costs associated with transmission and distribution for land-based
    wind projects (module is currently based on curve fit of empirical data)

    * Get distance to interconnection
    * Get interconnection voltage
    * Get toggle for new switchyard
    * Return total transmission and distribution costs

    \n\n**Keys in the input dictionary are the following:**

    dist_interconnect_mi
        (float) distance to interconnection [in miles]

    \n\n**Keys in the output dictionary are the following:**

    trans_dist_usd
        (float) total transmission and distribution costs [in USD]

    """

    def __init__(self, input_dict, output_dict , project_name):
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
        super(GridConnectionCost, self).__init__(input_dict, output_dict, project_name)
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.project_name = project_name

    def calculate_grid_connection_cost(self):
        """
        This is a BOS cost comming out of ICC
        """

        usacost = self.input_dict['usacost']        # this is assumed to be a dataframe

        usacost["pct_grid"] = usacost["%ICC(inFC)"] * usacost["Grid Connection"]

        total_cost_percent = usacost.sum(axis=0)["pct_grid"]/100

        self.output_dict['grid_connection_cost'] = total_cost_percent * self.output_dict['total_initial_capital_cost']

        return self.output_dict



    def run_module(self):
        """
        Runs the TransDistCost module and populates the IO dictionaries with calculated values.

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
            # self.calculate_costs(self.input_dict, self.output_dict)
            self.output_dict['total_collection_cost'] = self.calculate_grid_connection_cost()
            return 0, 0 # module ran successfully
        except Exception as error:
            traceback.print_exc()
            print(f"Fail {self.project_name} GridConnectionCost")
            return 1, error # module did not run successfully

