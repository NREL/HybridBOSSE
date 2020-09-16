import math
import traceback
import pytest
import traceback
from CostModule import CostModule
from datetime import datetime


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

    def total_initial_capital_cost(self):
        """
        Classifies project based on installed capacity size.
        Determines total BOS cost based on installed capacity (MW) and head height (feet)
        Cost data is sourced from: “Hydropower Baseline Cost Modelling, Version 2”
         –Oak Ridge National Laboratory https://info.ornl.gov/sites/publications/files/Pub58666.pdf
        """

        P = self.input_dict['system_size_MW_DC']
        H = self.input_dict['head_height_ft']

        if self.input_dict['project_type'] == 'Non-powered Dam':
            # insert key for the 'Non-powered Dam' from lcmcost dataframe
            self.input_dict['uid_lcmcosts'] = 'npd'
            total_icc_cost = 11489245 * P**0.976 * H ** -0.240

        if self.input_dict['project_type'] == 'New Stream-reach Development':
            self.input_dict['uid_lcmcosts'] = 'nsd'
            total_icc_cost = 9605710 * P**0.977 * H ** -0.126

        if self.input_dict['project_type'] == 'Canal/Conduit Project':
            self.input_dict['uid_lcmcosts'] = 'ccd'
            total_icc_cost = 9297820 * P**0.810 * H ** -0.102

        if self.input_dict['project_type'] == 'Pumped Storage Hydropower Project':
            self.input_dict['uid_lcmcosts'] = 'psh'
            if self.input_dict['greenfield_or_existing'] == 'existing infrastructure':
                total_icc_cost = 3008246 * P * math.exp(-0.000460*P)
            elif self.input_dict['greenfield_or_existing'] == 'greenfield':
                total_icc_cost = 4882655 * P * math.exp(-0.000776 * P)

        if self.input_dict['project_type'] == 'Unit Addition Project':
            self.input_dict['uid_lcmcosts'] = 'uap'
            total_icc_cost = 4163746 * P**0.741

        if self.input_dict['project_type'] == 'Generator Rewind Project':
            self.input_dict['uid_lcmcosts'] = 'grp'
            total_icc_cost = 250147 * P**0.817

        self.output_dict['total_initial_capital_cost'] = total_icc_cost
        #self.output_dict['uid_lcmcosts'] = self.input_dict['uid_lcmcosts']

        return total_icc_cost

    def total_bos_cost(self):
    # I am keeping the function as it is from Aaron (guress?)

        df = self.input_dict['usacost']

        bos_percent = df.sum(axis=0)["Sum Product"]/100
        # bos_percent = df.values[23,17]
        # bos_cost = bos_percent * self.output_dict['total_initial_capital_cost']

        #print('Bost Percent direct:', bos_percent)

        return bos_percent



    def project_classification(self):
        """
        Classifies project based on installed capacity size.
        Determines total BOS cost based on installed capacity (MW) and head height (feet)
        Cost data is sourced from: “Hydropower Baseline Cost Modelling, Version 2”
         –Oak Ridge National Laboratory https://info.ornl.gov/sites/publications/files/Pub58666.pdf
        """
        # I think this method or function should dictate which project_data file to use [1, 10, 30, 1000]
        # Determine project classification based on size
        if self.input_dict['system_size_MW_DC'] >= 30:  # Larger than 30MW
            self.input_dict['size_classification'] = 'Large'
            self.input_dict['project_data_file'] = 'project_list_100mw'

        if self.input_dict['system_size_MW_DC'] >= 10:  # Greater than 10MW but less than 30 MW
            self.input_dict['size_classification'] = 'Medium'
            self.input_dict['project_data_file'] = 'project_list_30mw'

        if self.input_dict['system_size_MW_DC'] <= 10:  # Smaller than 10MW
            self.input_dict['size_classification'] = 'Small'
            self.input_dict['project_data_file'] = 'project_list_10mw'

        if self.input_dict['system_size_MW_DC'] <= .100:  # Smaller than 100KW
            self.input_dict['size_classification'] = 'Micro'
            self.input_dict['project_data_file'] = 'project_list_1mw'

        print("Project Type is: ", self.input_dict['project_type'])
        print("Project Size is: ", self.input_dict['system_size_MW_DC'], 'MW')
        print("Project Classification is: ", self.input_dict['size_classification'])
        print('Head Height is: ', self.input_dict['head_height_ft'], ' feet')

        # P = self.input_dict['system_size_MW_DC']
        # H = self.input_dict['head_height_ft']

        # if self.input_dict['project_type'] == 'Non-powered Dam':
        #     total_bos_cost = 11489245 * P**0.976 * H ** -0.240
        #
        # if self.input_dict['project_type'] == 'New Stream-reach Development':
        #     total_bos_cost = 9605710 * P**0.977 * H ** -0.126
        #
        # if self.input_dict['project_type'] == 'Canal/Conduit Project':
        #     total_bos_cost = 9297820 * P**0.810 * H ** -0.102
        #
        # if self.input_dict['project_type'] == 'Pumped Storage Hydropower Project':
        #     if self.input_dict['greenfield_or_existing'] == 'existing infrastructure':
        #         total_bos_cost = 3008246 * P * math.exp(-0.000460*P)
        #     elif self.input_dict['greenfield_or_existing'] == 'greenfield':
        #         total_bos_cost = 4882655 * P * math.exp(-0.000776 * P)
        #
        # if self.input_dict['project_type'] == 'Unit Addition Project':
        #     total_bos_cost = 4163746 * P**0.741
        #
        # if self.input_dict['project_type'] == 'Generator Rewind Project':
        # total_bos_cost = 250147
        #

        self.output_dict['total_initial_capital_cost'] = self.total_initial_capital_cost()
        self.output_dict['total_bos_cost'] = self.total_bos_cost() * self.output_dict['total_initial_capital_cost']
        return self.input_dict, self.output_dict

    def cobb_cost_model(self, uid_case):
        """
        Cobb douglas cost calculation
        """
        # get the row for the uid_case and extract that particular row - based on key

        var1 = self.input_dict['system_size_MW_AC']  # can we make a list power, head_in_ft, gen_rpm, cf or AEP.
        var2 = self.input_dict['head_height_ft']

        # default as power and head_ft - if uid_case = gen_all replace it by rpm = default.
        print('UID Case is: ', uid_case)
        df = self.input_dict['lcmcosts']
        desired_row_for_technology = df.loc[df.uid == uid_case]

        try:
            a_cobb = desired_row_for_technology['A'][0]
            b_cobb = desired_row_for_technology['B'][0]
            c_cobb = desired_row_for_technology['C'][0]
        except:
            a_cobb = desired_row_for_technology['A']
            b_cobb = desired_row_for_technology['B']
            c_cobb = desired_row_for_technology['C']

        # print('Debug')
        cost_cobb = a_cobb * (var1 ** b_cobb) * (var2 ** c_cobb)

        # output_dict['site_access_cost'] = per_ICC * factor * self.output_dict['total_initial_capital_cost']

        return cost_cobb, uid_case

    def cost_escalation_factor(self, lcmcost, uid_case):
        """

        """
        model_year = lcmcost.at['uid_case', 'CostModelYear']
        today = datetime.today()

        current_year = today.year()  # Hard coded for now - make dynamic later

        print(current_year)

        # Use some logic here based on Construction Cost Escalation
        # Here I am using default value as a placeholder
        ce_factor_default = lcmcost.at['uid_case', 'CostEscalationFactor']
        ce_factor = (current_year - model_year) / (current_year - model_year) * ce_factor_default

        return ce_factor, uid_case







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
            self.project_classification()
            self.total_bos_cost()
            #self.total_initial_capital_cost()
            return 0, 0    # module ran successfully
        except Exception as error:
            traceback.print_exc()
            print(f"Fail {self.project_name} ManagementCost")
            self.input_dict['error']['ManagementCost'] = error
            return 1, error  # module did not run successfully
