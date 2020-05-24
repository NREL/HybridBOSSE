from .GridConnectionCost import hybrid_gridconnection


class PostSimulationProcessing:
    """
    Parse through detailed BOS outputs and 'smart' combine the outputs of the BOS
    models into a single, Hybrid BOS detailed output.
    """
    def __init__(self, hybrids_input_dict, LandBOSSE_BOS_results, SolarBOSSE_results):
        self.hybrids_input_dict = hybrids_input_dict
        self.LandBOSSE_BOS_results = LandBOSSE_BOS_results
        self.SolarBOSSE_results = SolarBOSSE_results
        self.total_hybrids_BOS_USD = self.hybrid_BOS_usd()
        self.total_hybrids_BOS_USD_Watt = self.hybrid_BOS_usd_watt()

    def hybrid_BOS_usd(self):
        """
        Hybrid BOS Results on a total project basis (USD)
        """

        total_hybrids_BOS_USD = self.LandBOSSE_BOS_results['total_bos_cost'] + \
                                self.SolarBOSSE_results['total_bos_cost']

        if self.hybrids_input_dict['shared_interconnection']:

            self.hybrids_input_dict['dist_interconnect_mi'] = \
                self.hybrids_input_dict['distance_to_interconnect_mi']

            self.hybrids_input_dict['system_size_MW'] = \
                self.hybrids_input_dict['grid_interconnection_rating_MW']

            # Shared hybrids Grid Interconnection Cost (USD):
            hybrid_gridconnection_usd = hybrid_gridconnection(self.hybrids_input_dict)

            total_hybrids_BOS_USD = total_hybrids_BOS_USD + \
                                    hybrid_gridconnection_usd - \
                                    self.LandBOSSE_BOS_results['total_gridconnection_cost'] - \
                                    self.SolarBOSSE_results['total_transdist_cost']

        return total_hybrids_BOS_USD

    def hybrid_BOS_usd_watt(self):
        if self.SolarBOSSE_results['total_bos_cost'] == 0:
            total_hybrids_BOS_USD_Watt = (self.LandBOSSE_BOS_results['total_bos_cost'] /
                                          (self.hybrids_input_dict['wind_plant_size_MW'] * 1e6))

        elif self.LandBOSSE_BOS_results['total_bos_cost'] == 0:
            total_hybrids_BOS_USD_Watt = (self.SolarBOSSE_results['total_bos_cost'] /
                                          (self.hybrids_input_dict['solar_system_size_MW_DC'] * 1e6))

        else:
            total_hybrids_BOS_USD = self.hybrid_BOS_usd()
            total_hybrids_BOS_USD_Watt = total_hybrids_BOS_USD / \
                                         ((self.hybrids_input_dict['wind_plant_size_MW'] * 1e6) +
                                          (self.hybrids_input_dict['solar_system_size_MW_DC'] * 1e6))

        return total_hybrids_BOS_USD_Watt


