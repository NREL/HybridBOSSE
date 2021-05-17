from copy import deepcopy
from .GridConnectionCost import hybrid_gridconnection
from .SubstationCost import hybrid_substation
from .InverterTransformerErection import InverterTransformerErection
from .ManagementCost import *
from .CollectionCost import ArraySystem, get_ac_hybrid_matrix, get_dc_hybrid_matrix


class PostSimulationProcessing:
    """
    Collection of methods to parse through detailed BOS outputs and 'smart' combine the
    outputs of the BOS models into a single, Hybrid BOS detailed output.
    """
    def __init__(self, hybrids_input_dict, LandBOSSE_BOS_results, SolarBOSSE_results, StorageBOSSE_results):
        self.hybrids_input_dict = hybrids_input_dict
        self.LandBOSSE_BOS_results = LandBOSSE_BOS_results
        self.SolarBOSSE_results = SolarBOSSE_results
        self.StorageBOSSE_results = StorageBOSSE_results
        self.hybrid_gridconnection_usd = self.hybrid_gridconnection_usd()
        self.inverter_cost_usd = self.inverter_cost()
        self.hybrid_substation_usd = self.hybrid_substation_usd()
        self.hybrid_collection_cost_usd = self.hybrid_collection_cost()
        self.site_facility_usd = self.site_facility_hybrid()
        self.developer_profit_USD()
        self.developer_overhead_USD()
        self.hybrid_BOS_usd = self.hybrid_BOS_usd()
        self.hybrid_BOS_usd_watt = self.hybrid_BOS_usd_watt()

    def hybrid_BOS_usd(self):
        """
        Hybrid BOS Results on a total project basis (USD)
        """
        mode = self.hybrids_input_dict['project_mode']
        shared_collection = self.hybrids_input_dict['shared_collection_system']
        total_hybrids_BOS_USD = self.LandBOSSE_BOS_results['total_bos_cost'] + \
                                self.SolarBOSSE_results['total_bos_cost'] + \
                                self.StorageBOSSE_results['total_bos_cost']
        if shared_collection:
            total_hybrids_BOS_USD -= (self.LandBOSSE_BOS_results['total_collection_cost'] +
                                      self.SolarBOSSE_results['total_collection_cost'] +
                                      self.StorageBOSSE_results['total_collection_cost'])

        if mode == 2:
            total_hybrids_BOS_USD += self.inverter_cost_usd



        if self.hybrids_input_dict['wind_plant_size_MW'] == 0:
            self.LandBOSSE_BOS_results['total_gridconnection_cost'] = 0
            self.LandBOSSE_BOS_results['total_substation_cost'] = 0

        if self.hybrids_input_dict['solar_system_size_MW_DC'] == 0:
            self.SolarBOSSE_results['total_transdist_cost'] = 0
            self.SolarBOSSE_results['substation_cost'] = 0

        if self.hybrids_input_dict['storage_system_size_MW_DC'] == 0:
            self.StorageBOSSE_results['total_transdist_cost'] = 0
            self.StorageBOSSE_results['substation_cost'] = 0

        if self.hybrids_input_dict['shared_interconnection']:
            total_hybrids_BOS_USD = total_hybrids_BOS_USD + \
                                    self.hybrid_gridconnection_usd + \
                                    self.hybrid_substation_usd - \
                                    self.LandBOSSE_BOS_results['total_gridconnection_cost'] - \
                                    self.SolarBOSSE_results['total_transdist_cost'] - \
                                    self.LandBOSSE_BOS_results['total_substation_cost'] - \
                                    self.SolarBOSSE_results['substation_cost'] - \
                                    self.StorageBOSSE_results['total_transdist_cost'] - \
                                    self.StorageBOSSE_results['substation_cost']

        return total_hybrids_BOS_USD.sum()

    def hybrid_BOS_usd_watt(self):
        if self.SolarBOSSE_results['total_bos_cost'] == 0:
            # total_hybrids_BOS_USD_Watt = (self.LandBOSSE_BOS_results['total_bos_cost'] /
            #                               (self.hybrids_input_dict['wind_plant_size_MW'] * 1e6))
            total_hybrids_BOS_USD_Watt = (self.hybrid_BOS_usd /
                                          (self.hybrids_input_dict['wind_plant_size_MW'] * 1e6))

        elif self.LandBOSSE_BOS_results['total_bos_cost'] == 0:
            # total_hybrids_BOS_USD_Watt = (self.SolarBOSSE_results['total_bos_cost'] /
            #                               (self.hybrids_input_dict['solar_system_size_MW_DC'] * 1e6))

            total_hybrids_BOS_USD_Watt = (self.hybrid_BOS_usd /
                                          (self.hybrids_input_dict['solar_system_size_MW_DC'] * 1e6))

        else:
            total_hybrids_BOS_USD = self.hybrid_BOS_usd

            total_hybrids_BOS_USD_Watt = total_hybrids_BOS_USD / \
                                         ((self.hybrids_input_dict['solar_system_size_MW_DC'] * 1e6) +
                                          (self.hybrids_input_dict['wind_plant_size_MW'] * 1e6))

        return total_hybrids_BOS_USD_Watt.sum()

    def hybrid_gridconnection_usd(self):
        """

        """
        grid = dict()
        grid['new_switchyard'] = self.hybrids_input_dict['new_switchyard']
        grid['interconnect_voltage_kV'] = self.hybrids_input_dict['interconnect_voltage_kV']

        if self.hybrids_input_dict['shared_interconnection']:

            grid['dist_interconnect_mi'] = \
                self.hybrids_input_dict['distance_to_interconnect_mi']

            grid['system_size_MW'] = self.hybrids_input_dict['grid_interconnection_rating_MW']

            # Shared hybrids Grid Interconnection Cost (USD):
            hybrid_gridconnection_usd = hybrid_gridconnection(grid)

        else:
            hybrid_gridconnection_usd = 0

        return hybrid_gridconnection_usd

    def hybrid_substation_usd(self):
        """

        """
        if self.hybrids_input_dict['shared_substation']:
            hybrid_substation_usd = hybrid_substation(self.hybrids_input_dict)
        else:
            hybrid_substation_usd = 0

        if (self.hybrids_input_dict['project_mode'] == 2 or self.hybrids_input_dict['project_mode'] == 4) and self.hybrids_input_dict['shared_collection_system']:
            hybrid_substation_usd += self.inverter_cost_usd

        return hybrid_substation_usd

    def hybrid_collection_cost(self):
        """

        """
        if self.hybrids_input_dict['shared_collection_system']:
            if self.hybrids_input_dict['project_mode'] == 4:
                dc_outputs = dict()


                hybrid_dc_collection_inputs = self.hybrids_input_dict.copy()
                hybrid_dc_collection_inputs['project_mode'] = 3

                #sets up dictionary for hybrid dc setup
                adj, x, y, types = get_dc_hybrid_matrix(hybrid_dc_collection_inputs)
                hybrid_dc_collection_inputs['adj_layout'] = adj
                hybrid_dc_collection_inputs['x_coordinate_layout'] = x
                hybrid_dc_collection_inputs['y_coordinate_layout'] = y
                hybrid_dc_collection_inputs['type_layout'] = types


                hybrid_collection_cost_dc = ArraySystem(input_dict=hybrid_dc_collection_inputs, output_dict=dc_outputs)
                hybrid_collection_cost_dc.run_module()
                hybrid_collection_cost_dc_bos = dc_outputs['total_collection_cost'].sum().values[1]
                hybrid_collection_cost_bos = self.LandBOSSE_BOS_results['total_collection_cost'] + hybrid_collection_cost_dc_bos
            else:
                outputs = dict()
                hybrid_collection_cost = ArraySystem(input_dict=self.hybrids_input_dict, output_dict=outputs)
                hybrid_collection_cost.run_module()
                hybrid_collection_cost_bos = outputs['total_collection_cost'].sum().values[1]


        else:
            outputs = dict()
            hybrid_collection_cost_bos = (self.LandBOSSE_BOS_results['total_collection_cost'] +
                                      self.SolarBOSSE_results['total_collection_cost'] +
                                      self.StorageBOSSE_results['total_collection_cost'])

        return hybrid_collection_cost_bos

    def inverter_cost(self):
        if self.hybrids_input_dict['project_mode'] == 2 and self.hybrids_input_dict['shared_collection_system']:
            output = dict()
            inverter = InverterTransformerErection(self.hybrids_input_dict, output, "external_inverter")
            inverter.run_module()
            hybrid_inverter_cost = output['total_erection_cost'].sum()
        else:
            hybrid_inverter_cost = 0
        return hybrid_inverter_cost

    def developer_profit_USD(self):
        """

        """
        hybrid_plant_size_MW = self.hybrids_input_dict['hybrid_plant_size_MW']
        wind_plant_size_MW = self.hybrids_input_dict['wind_plant_size_MW']
        solar_system_size_MW_DC = self.hybrids_input_dict['solar_system_size_MW_DC']
        storage_system_size_MW_DC = self.hybrids_input_dict['storage_system_size_MW_DC']

        landbosse_cost_before_mgmt = self.LandBOSSE_BOS_results['total_bos_cost'] - \
                                     self.LandBOSSE_BOS_results['total_management_cost']

        wind_profit_savings = \
            epc_developer_profit_discount(hybrid_plant_size_MW, wind_plant_size_MW) * \
            landbosse_cost_before_mgmt

        self.LandBOSSE_BOS_results['total_bos_cost'] -= wind_profit_savings
        self.LandBOSSE_BOS_results['total_management_cost'] -= wind_profit_savings

        if self.hybrids_input_dict['hybrid_plant_size_MW'] > 15:
            self.LandBOSSE_BOS_results['markup_contingency_usd'] -= wind_profit_savings

        solarbosse_cost_before_mgmt = self.SolarBOSSE_results['total_bos_cost'] - \
                                      self.SolarBOSSE_results['total_management_cost']
        solar_profit_savings = \
            epc_developer_profit_discount(hybrid_plant_size_MW, solar_system_size_MW_DC) * \
            solarbosse_cost_before_mgmt

        self.SolarBOSSE_results['total_bos_cost'] -= solar_profit_savings
        self.SolarBOSSE_results['total_management_cost'] -= solar_profit_savings

        if self.hybrids_input_dict['hybrid_plant_size_MW'] > 15:
            self.SolarBOSSE_results['epc_developer_profit'] -= solar_profit_savings

    def developer_overhead_USD(self):
        """

        """
        hybrid_plant_size_MW = self.hybrids_input_dict['hybrid_plant_size_MW']
        wind_plant_size_MW = self.hybrids_input_dict['wind_plant_size_MW']
        solar_system_size_MW_DC = self.hybrids_input_dict['solar_system_size_MW_DC']

        landbosse_cost_before_mgmt = self.LandBOSSE_BOS_results['total_bos_cost'] - \
                                     self.LandBOSSE_BOS_results['total_management_cost']

        # Calculate overhead savings from going hybrid, and subtract it from wind only
        # BOS cost
        wind_overhead_savings = \
            development_overhead_cost_discount(hybrid_plant_size_MW,
                                               wind_plant_size_MW) * landbosse_cost_before_mgmt

        self.LandBOSSE_BOS_results['total_bos_cost'] -= \
            (wind_overhead_savings + self.LandBOSSE_BOS_results['site_facility_usd'])

        self.LandBOSSE_BOS_results['total_management_cost'] -= \
            (wind_overhead_savings + self.LandBOSSE_BOS_results['site_facility_usd'])

        # Remove site_facility_usd cost from wind's overhead cost (to prevent
        # double counting)
        self.LandBOSSE_BOS_results['site_facility_usd'] = 0

        if self.hybrids_input_dict['hybrid_plant_size_MW'] > 15:
            self.LandBOSSE_BOS_results['markup_contingency_usd'] -= wind_overhead_savings

        solarbosse_cost_before_mgmt = self.SolarBOSSE_results['total_bos_cost'] - \
                                      self.SolarBOSSE_results['total_management_cost']

        # Calculate overhead savings from going hybrid, and subtract it from solar only
        # BOS cost
        solar_overhead_savings = \
            epc_developer_profit_discount(hybrid_plant_size_MW, solar_system_size_MW_DC) * \
            solarbosse_cost_before_mgmt

        solar_system_size_MW_DC = self.hybrids_input_dict['solar_system_size_MW_DC']
        solar_construction_time_months = self.hybrids_input_dict['solar_construction_time_months']
        num_turbines_solar_only = 0
        solar_only_site_cost_usd = site_facility(solar_system_size_MW_DC,
                                                 solar_construction_time_months,
                                                 num_turbines_solar_only)

        self.SolarBOSSE_results['total_bos_cost'] -= (solar_overhead_savings +
                                                      solar_only_site_cost_usd)

        self.SolarBOSSE_results['total_management_cost'] -= (solar_overhead_savings +
                                                             solar_only_site_cost_usd)

        # Remove site_facility_usd cost from solar's overhead cost (to prevent
        # double counting)
        self.SolarBOSSE_results['development_overhead_cost'] -= solar_only_site_cost_usd

        if self.hybrids_input_dict['hybrid_plant_size_MW'] > 15:
            self.SolarBOSSE_results['development_overhead_cost'] -= \
                solar_overhead_savings

    def site_facility_hybrid(self):
        """

        """
        hybrid_plant_size_MW = self.hybrids_input_dict['hybrid_plant_size_MW']
        hybrid_construction_months = self.hybrids_input_dict['hybrid_construction_months']
        num_turbines = self.hybrids_input_dict['num_turbines']

        site_facility_usd = site_facility(hybrid_plant_size_MW,
                                          hybrid_construction_months,
                                          num_turbines)
        return site_facility_usd

    def update_BOS_dict(self, BOS_dict, technology):
        """
        Remove shared cost buckets from the individual BOS detailed outputs
        """
        if technology == 'wind' and BOS_dict['total_bos_cost'] > 0:
            BOS_dict.pop('total_substation_cost')
            BOS_dict.pop('total_gridconnection_cost')
            BOS_dict.pop('total_management_cost')
            BOS_dict.pop('insurance_usd')
            BOS_dict.pop('construction_permitting_usd')
            BOS_dict.pop('project_management_usd')
            BOS_dict.pop('bonding_usd')
            BOS_dict.pop('markup_contingency_usd')
            BOS_dict.pop('engineering_usd')
            BOS_dict.pop('site_facility_usd')
            if self.hybrids_input_dict['shared_collection_system']:
                BOS_dict.pop('total_collection_cost')

        elif technology == 'solar' and BOS_dict['total_bos_cost'] > 0:
            BOS_dict.pop('substation_cost')
            BOS_dict.pop('total_transdist_cost')
            BOS_dict.pop('total_management_cost')
            BOS_dict.pop('epc_developer_profit')
            BOS_dict.pop('bonding_usd')
            BOS_dict.pop('development_overhead_cost')
            BOS_dict.pop('total_sales_tax')
            if self.hybrids_input_dict['shared_collection_system']:
                BOS_dict.pop('total_collection_cost')

        elif technology == 'storage' and BOS_dict['total_bos_cost'] > 0:
            # Remove the appropriate cost buckets for a system involving storage
            # BOS_dict.pop('substation_cost')
            BOS_dict.pop('total_transdist_cost')
            BOS_dict.pop('substation_cost')
            if self.hybrids_input_dict['shared_collection_system']:
                BOS_dict.pop('total_collection_cost')

        return BOS_dict

