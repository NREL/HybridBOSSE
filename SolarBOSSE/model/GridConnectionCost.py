import traceback
import pandas as pd
import math
from .CostModule import CostModule


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

    def calculate_costs(self, input_dict, output_dict):
        """
        Function to calculate total costs for transmission and distribution.

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
        # TODO: In the next version update of SolarBOSSE, change grid cost
        #  calculation as a function of grid_size_MW_AC, not grid_system_size_MW_DC

        # Switch between utility scale model and distributed model
        # Run utility version of GridConnectionCost for project size > 10 MW:
        if input_dict['grid_system_size_MW_DC'] > 15:
            if input_dict['dist_interconnect_mi'] == 0:
                output_dict['trans_dist_usd'] = 0
            else:
                if input_dict['new_switchyard'] is True:
                    output_dict['interconnect_adder_USD'] = \
                        18115 * self.input_dict['interconnect_voltage_kV'] + 165944
                else:
                    output_dict['interconnect_adder_USD'] = 0

                output_dict['trans_dist_usd'] = \
                    ((1176 * self.input_dict['interconnect_voltage_kV'] + 218257) *
                     (input_dict['dist_interconnect_mi'] ** (-0.1063)) *
                     input_dict['dist_interconnect_mi']
                     ) + output_dict['interconnect_adder_USD']

        # Run distributed wind version of GridConnectionCost for project size < 15 MW:
        else:
            # Code below is for newer version of LandBOSSE which incorporates
            # distributed wind into the model. Here POI refers to point of
            # interconnection.
            output_dict['array_to_POI_usd_per_kw'] = \
                1736.7 * ((input_dict['grid_size_MW_AC'] * 1000) ** (-0.272))

            output_dict['trans_dist_usd'] = \
                input_dict['grid_size_MW_AC'] * 1000 * output_dict['array_to_POI_usd_per_kw']

        output_dict['trans_dist_usd_df'] = pd.DataFrame([['Other',
                                                          output_dict['trans_dist_usd'],
                                                          'Transmission and Distribution']],
                                                        columns=['Type of cost',
                                                                 'Cost USD',
                                                                 'Phase of construction'])

        output_dict['total_transdist_cost'] = output_dict['trans_dist_usd_df']['Cost USD'].sum()

        return output_dict['trans_dist_usd_df']

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
            self.calculate_costs(self.input_dict, self.output_dict)
            return 0, 0 # module ran successfully
        except Exception as error:
            traceback.print_exc()
            print(f"Fail {self.project_name} GridConnectionCost")
            return 1, error # module did not run successfully

