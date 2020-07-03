import math
import traceback
import pytest
import traceback
from .CostModule import CostModule


class ManagementCost(CostModule):
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
        super(ManagementCost, self).__init__(input_dict, output_dict, project_name)
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.project_name = project_name

        # Project CAPEX before management costs (USD)
        self.project_capex_usd = self.output_dict['total_bos_cost_before_mgmt'] + \
                                 (0.51 * self.input_dict['system_size_MW_DC'] * 1e6)

    def epc_developer_profit(self):
        """

        """
        if self.input_dict['system_size_MW_DC'] <= 10:
            epc_developer_profit_usd_watt = 0.06
        else:
            epc_developer_profit_usd_watt = 0.05
        self.output_dict['epc_developer_profit'] = epc_developer_profit_usd_watt * \
                                                   self.input_dict['system_size_MW_DC'] * 1e6

        return self.output_dict['epc_developer_profit']

    def contingency(self):
        contingency_usd_watt = 0.03
        self.output_dict['contingency_cost'] = contingency_usd_watt * \
                                               self.input_dict['system_size_MW_DC'] * 1e6

        return self.output_dict['contingency_cost']

    def development_overhead_cost(self):
        # Get dev overhead multiplier (% of CAPEX)
        development_overhead_percent =  \
            0.3177 * (self.input_dict['system_size_MW_DC'] ** (-0.547))

        self.output_dict['development_overhead_cost'] = development_overhead_percent * \
                                                       self.project_capex_usd
        return self.output_dict['development_overhead_cost']

    def sales_tax(self):
        """

        """
        sales_tax_percent = 0.0328 * (self.input_dict['system_size_MW_DC'] ** 0.0786)
        self.output_dict['total_sales_tax'] = sales_tax_percent * self.project_capex_usd
        return self.output_dict['total_sales_tax']

    def total_management_cost(self):
        """
        Calculates the total cost of returned by the rest of the methods.
        This must be called after all the other methods in the module.

        This method uses the outputs for all the other individual costs as
        set in self.output_dict. It does not call the other methods directly.

        Returns
        -------
        float
            Total management cost as summed from the outputs of all
            other methods.
        """
        total = 0
        total += self.output_dict['epc_developer_profit']
        total += self.output_dict['contingency_cost']
        total += self.output_dict['development_overhead_cost']
        total += self.output_dict['total_sales_tax']
        self.output_dict['total_management_cost'] = total
        return total

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
            self.output_dict['epc_developer_profit'] = self.epc_developer_profit()
            self.output_dict['bonding_usd'] = self.contingency()
            self.output_dict['development_overhead_cost'] = self.development_overhead_cost()
            self.output_dict['total_sales_tax'] = self.sales_tax()

            self.output_dict['total_management_cost'] = self.total_management_cost()

            return 0, 0    # module ran successfully
        except Exception as error:
            traceback.print_exc()
            print(f"Fail {self.project_name} ManagementCost")
            self.input_dict['error']['ManagementCost'] = error
            return 1, error  # module did not run successfully
