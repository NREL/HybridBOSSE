import numpy as np


class CostModule:
    """
    This is a super class for all other cost modules to import
    that provides shared methods for outputs from results and
    mobilization cost calculations.
    """
    def __init__(self, input_dict, output_dict, project_name):
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.project_name = project_name

        self.input_dict['inverter_rating_MW'] = self.input_dict['hybrid_substation_rating_MW']
        self.input_dict['system_size_MW_AC'] = \
            self.input_dict['hybrid_substation_rating_MW'] / self.input_dict['dc_ac_ratio']

        # self.input_dict['site_prep_area_acres_mw_dc'] = \
        #     self.input_dict['site_prep_area_acres_mw_ac'] * self.input_dict['dc_ac_ratio']

        # site_area_in_m2 = \
        #     (self.input_dict['site_prep_area_acres_mw_dc'] *
        #      self.input_dict['system_size_MW_DC']) * 4046.86
        #
        # self.input_dict['road_length_m'] = 1.5 * ((site_area_in_m2 / 1.5) ** 0.5)
        #
        # self.input_dict['site_prep_area_acres'] = \
        #     self.input_dict['site_prep_area_acres_mw_dc'] * \
        #     self.input_dict['system_size_MW_DC']
        #
        # # 1 acre = 4046.86 m2:
        # self.input_dict['site_prep_area_m2'] = \
        #     self.input_dict['site_prep_area_acres'] * 4046.86

    def layout_length(self):
        """ In manual mode, calculates the total length between nodes in the plant, which is the road length, and cable
        length from substation to all nodes [km]."""
        self.output_dict['layout_length_km'] = 0
        self.collection_layout = self.input_dict['collection_layout'].values
        self.L = self.collection_layout[:, :2]  # location of nodes [m]
        self.A = self.collection_layout[:, 2:]  # adjacency matrix for collection system. Zeroth element is substation
        dim = self.A.shape
        self.n_segments = dim[1] - 1  # #turbines
        remains = np.ones(self.n_segments + 1)  # nodes still to have cables defined around
        for i in range(0, self.n_segments):
            for j in np.where(self.A[i, :] * remains == 1)[0]:
                self.output_dict['layout_length_km'] += ((self.L[i, 0] - self.L[j, 0]) ** 2 + (
                        self.L[i, 1] - self.L[j, 1]) ** 2) ** (1 / 2)
                # calculates cable length with distance formula
            remains[i] = False  # prevent duplicate cables
