import math
import traceback
import pytest
import traceback
from .CostModule import CostModule


class ManagementCost(CostModule):
    """
    Source of curve fit cost data:
    https://www.nrel.gov/docs/fy19osti/71714.pdf

    This class models management costs of a BESS plant. Its inputs are
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
        super(ManagementCost, self).__init__(input_dict, output_dict, project_name)
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.project_name = project_name

        # Project CAPEX before management costs (USD)
        # TODO battery costs in here?
        self.project_capex_usd = self.output_dict['total_bos_cost_before_mgmt'] + \
                                 (self.output_dict['num_containers'] * self.input_dict['container_cost'])

    def total_management_cost(self):
        """
        Calculates the total management cost based on curve fit, unless provided by user. Management cost scales with
        project size in MWh. Includes:
        EPC overhead
        Sales tax
        Contingency
        Developer overhead
        EPC/developer net profit

        Returns
        -------
        float
            Total management cost as summed from the outputs of all
            other methods.
        """
        if 'total_management_cost' in self.input_dict:
            self.output_dict['total_management_cost'] = self.input_dict['total_management_cost']
        else:
            self.output_dict['total_management_cost'] = 774272 * self.input_dict['system_size_MWh'] * self.input_dict['system_size_MWh'] ** -0.441
        return self.output_dict['total_management_cost']

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
            self.output_dict['total_management_cost'] = self.total_management_cost()

            return 0, 0    # module ran successfully
        except Exception as error:
            traceback.print_exc()
            print(f"Fail {self.project_name} ManagementCost")
            self.input_dict['error']['ManagementCost'] = error
            return 1, error  # module did not run successfully
