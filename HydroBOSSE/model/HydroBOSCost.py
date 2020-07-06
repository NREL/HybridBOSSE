import math
import traceback
import pytest
import traceback
from .CostModule import CostModule


class HydroBOSCost(CostModule):
    """
    Source for all multiplier costs explicitly mention:
    https://www.nrel.gov/docs/fy19osti/72133.pdf

    This class models management costs of a solar plant. Its inputs are
    configured with a dictionary with the key value pairs being the
    inputs into the model.

    """

    def __init__(self, input_dict, output_dict, project_name):
        """
        This method runs all cost calculations in the model based on the
        inputs key value pairs in the dictionary that is the only
        argument.

        Parameters
        ----------
        input_dict : dict
            Dictionary with the inputs key / value pairs

        output_dict : dict
            Dictionary with output key / value pairs.
        """
        super(HydroBOSCost, self).__init__(input_dict, output_dict, project_name)
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.project_name = project_name

        # Project CAPEX before management costs (USD)
        # self.project_capex_usd = self.output_dict['total_bos_cost_before_mgmt'] + \
        #                          (0.51 * self.input_dict['system_size_MW_DC'] * 1e6)

    def total_bos_cost(self):
        """
        Classifies project based on installed capacity size.
        Determines total BOS cost based on installed capacity (MW) and head height (feet)
        Cost data is sourced from: “Hydropower Baseline Cost Modelling, Version 2”
         –Oak Ridge National Laboratory https://info.ornl.gov/sites/publications/files/Pub58666.pdf
        """
        # Determine project classification based on size
        if self.input_dict['system_size_MW_DC'] >= 30:  # Larger than 30MW
            self.input_dict['size_classification'] = 'Large'

        if self.input_dict['system_size_MW_DC'] <= 10:  # Smaller than 10MW
            self.input_dict['size_classification'] = 'Small'

        if self.input_dict['system_size_MW_DC'] <= .100:  # Smaller than 100KW
            self.input_dict['size_classification'] = 'Micro'
        print("Project Type is: ", self.input_dict['project_type'])
        print("Project Size is: ", self.input_dict['system_size_MW_DC'], 'MW')
        print("Project Classification is: ", self.input_dict['size_classification'])
        print('Head Height is: ', self.input_dict['head_height_ft'], ' feet')

        P = self.input_dict['system_size_MW_DC']
        H = self.input_dict['head_height_ft']

        if self.input_dict['project_type'] == 'Non-powered Dam':
            total_bos_cost = 11489245 * P**0.976 * H ** -0.240

        if self.input_dict['project_type'] == 'New Stream-reach Development':
            total_bos_cost = 9605710 * P**0.977 * H ** -0.126

        if self.input_dict['project_type'] == 'Canal/Conduit Project':
            total_bos_cost = 9297820 * P**0.810 * H ** -0.102

        if self.input_dict['project_type'] == 'Pumped Storage Hydropower Project':
            if self.input_dict['greenfield_or_existing'] == 'existing infrastructure':
                total_bos_cost = 3008246 * P * math.exp(-0.000460*P)
            elif self.input_dict['greenfield_or_existing'] == 'greenfield':
                total_bos_cost = 4882655 * P * math.exp(-0.000776 * P)

        if self.input_dict['project_type'] == 'Unit Addition Project':
            total_bos_cost = 4163746 * P**0.741

        if self.input_dict['project_type'] == 'Generator Rewind Project':
            total_bos_cost = 250147 * P**0.817

        self.output_dict['total_bos_cost'] = total_bos_cost

        return self.output_dict['total_bos_cost']

    def run_module(self):
        """
        Runs all the calculation methods in order.

        Parameters
        ----------
        project_name : str
            The name of the project for which this calculation is being done.

        Returns
        -------
        tuple
            First element of tuple contains a 0 or 1. 0 means no errors happened and
            1 means an error happened and the module failed to run. The second element
            depends on the error condition. If the condition is 1, then the second
            element is the error raised that caused the failure. If the condition is
            0 then the second element is 0 as well.
        """
        try:
            self.total_bos_cost()
            return 0, 0    # module ran successfully
        except Exception as error:
            traceback.print_exc()
            print(f"Fail {self.project_name} ManagementCost")
            self.input_dict['error']['ManagementCost'] = error
            return 1, error  # module did not run successfully
