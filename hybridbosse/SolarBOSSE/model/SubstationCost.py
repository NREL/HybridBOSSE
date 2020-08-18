import traceback
import pandas as pd
import math
from .CostModule import CostModule


class SubstationCost(CostModule):
    """
    **SubstationCost.py**

    - Created by Annika Eberle and Owen Roberts on Dec. 17, 2018

    - Refactored by Parangat Bhaskar and Alicia Key on  June 3, 2019

    Calculates the costs associated with substations for land-based wind projects *(module is currently based on curve fit of empirical data)*


    Get project size (project_size_megawatts = num_turbines * turbine_rating_kilowatt / kilowatt_per_megawatt)
    Get interconnect voltage

    Return total substation costs

    \n\n**Keys in the input dictionary are the following:**

    interconnect_voltage_kV
        (int) project interconnection voltage to substation [in kV]

    project_size_megawatts
        (int) total project size [in MW]

    \n\n**Keys in the output dictionary are the following:**

    substation_cost
        (float) cost of substation [in USD]


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
        super(SubstationCost, self).__init__(input_dict, output_dict, project_name)
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.project_name = project_name

    def calculate_costs(self, input_dict , output_dict):
        """
        Function to calculate Substation Cost in USD

        Parameters
        -------
        interconnect_voltage_kV
            (in kV)

        project_size_megawatts
            (in MW)


        Returns:
        -------
        substation_cost
            (in USD)

        """
        if 'substation_rating_MW' in input_dict:
            input_dict['system_size_MW_AC'] = \
                input_dict['substation_rating_MW'] / input_dict['dc_ac_ratio']

        if input_dict['system_size_MW_AC'] > 15:
            output_dict['substation_cost_usd'] = \
                11652 * (input_dict['interconnect_voltage_kV'] + input_dict['system_size_MW_AC']) + \
                11795 * (input_dict['system_size_MW_AC'] ** 0.3549) + 1526800

        else:
            # TODO: make this a user input
            if input_dict['system_size_MW_AC'] > 10:
                output_dict['substation_cost_usd'] = 1000000
            else:   # that is, < 10 MW_AC
                output_dict['substation_cost_usd'] = 500000

        output_dict['substation_cost_output_df'] = pd.DataFrame([['Other',
                                                                  output_dict['substation_cost_usd'],
                                                                  'Substation']],
                                                                columns=['Type of cost',
                                                                         'Cost USD',
                                                                         'Phase of construction'])

        output_dict['total_substation_cost_df'] = output_dict['substation_cost_output_df']
        output_dict['total_substation_cost'] = \
        output_dict['substation_cost_output_df']['Cost USD'].sum()

        return output_dict['substation_cost_output_df']

    def run_module(self):
        """
        Runs the SubstationCost module and populates the IO dictionaries with calculated values.

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
            self.calculate_costs(self.input_dict, self.output_dict)
            return 0, 0
        except Exception as error:
            traceback.print_exc()
            print(f"Fail {self.project_name} SubstationCost")
            return 1, error
