import math
import traceback
import pytest
import traceback


class ManagementCost:
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
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.project_name = project_name

        # Project CAPEX (USD/W_DC)
        # Source: https://www.nrel.gov/docs/fy19osti/72133.pdf
        self.project_capex_usd_w = 1.525 * (self.input_dict['system_size_MW_DC'] ** 0.079)
        self.project_capex_usd = self.project_capex_usd_w * self.input_dict['system_size_MW_DC'] * 1e6

    def insurance(self):
        """
        Calculate insurance costs based on project value, builder size, and project size;
        Source: https://www.nrel.gov/docs/fy10osti/46932.pdf

        Includes:

        Builder's risk

        General liability

        Umbrella policy

        Professional liability

        It uses only the self.project_value attribute in calculations.

        Returns
        -------
        float
            Insurance costs in USD
        """
        insurance_cost = 0.005 * self.project_capex_usd
        self.output_dict['insurance_cost'] = insurance_cost
        return insurance_cost

    def contingency(self):
        contingency_percentage = 0.0197 * (self.input_dict['system_size_MW_DC'] ** 0.0786)
        self.output_dict['contingency_cost'] = contingency_percentage * self.project_capex_usd
        return self.output_dict['contingency_cost']

    def site_facility(self):
        """
        Uses empirical data to estimate cost of site facilities and security, including


        Site facilities:

        Building design and construction

        Drilling and installing a water well, including piping

        Electric power for a water well

        Septic tank and drain field


        Site security:

        Constructing and reinstating the compound

        Constructing and reinstating the batch plant site

        Setting up and removing the site offices for the contractor, turbine supplier, and owner

        Restroom facilities

        Electrical and telephone hook-up

        Monthly office costs

        Signage for project information, safety and directions

        Cattle guards and gates

        Number of access roads



        In main.py, a csv is loaded into a Pandas dataframe. The columns of the
        dataframe must be:

        Size Min (MW)
            Minimum power output for a plant that needs a certain size of
            building.

        Size Max (MW)
            Maximum power output of a plant that need a certain size of
            building.

        Building Area (sq. ft.)
            The area of the building needed to provide O & M support to plants
            with power output between "Size Min (MW)" and "Size Max (MW)".

        Returns
        -------
        float
            Building area in square feet
        """
        df = self.input_dict['site_facility_building_area_df']
        project_size_megawatts = self.input_dict['system_size_MW_DC']
        row = df[(df['Size Max (MW)'] > project_size_megawatts) & (df['Size Min (MW)'] <= project_size_megawatts)]
        building_area_sq_ft = float(row['Building area (sq. ft.)'])

        construction_building_cost = building_area_sq_ft * 125 + 176125

        ps = self.input_dict['system_size_MW_DC']
        ct = self.output_dict['construction_time_months']
        nt = self.input_dict['num_turbines'] # TODO: Find a NT alternative.
        if nt < 30:
            nr = 1
            acs = 30000
        elif nt < 100:
            nr = round(0.05 * nt)
            acs = 240000
        else:
            nr = round(0.05 * nt)
            acs = 390000
        compound_security_cost = 9825 * nr + 29850 * ct + acs + 60 * ps + 62400

        site_facility_cost = construction_building_cost + compound_security_cost
        return site_facility_cost

    def sales_tax(self):
        """

        """
        sales_tax_percent = 0.0328 * (self.input_dict['system_size_MW_DC'] ** 0.0786)
        self.output_dict['total_sales_tax'] = sales_tax_percent * self.project_capex_usd
        return self.output_dict['total_sales_tax']

    def development_overhead_cost(self):
        # Get dev overhead multiplier (% of CAPEX)
        development_overhead_percent = \
            0.226 * (self.input_dict['system_size_MW_DC'] ** (-0.543))

        self.output_dict['development_overhead_cost'] = development_overhead_percent * \
                                                       self.project_capex_usd
        return self.output_dict['development_overhead_cost']

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
        total += self.output_dict['insurance_usd']
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
            self.output_dict['insurance_usd'] = self.insurance()
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
