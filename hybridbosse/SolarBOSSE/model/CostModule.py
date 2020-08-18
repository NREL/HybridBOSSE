class CostModule:
    """
    This is a super class for all other cost modules to import
    that provides shared pre-processed data.
    """

    def __init__(self, input_dict, output_dict, project_name):
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.project_name = project_name

        self.input_dict['system_size_MW_AC'] = \
            self.input_dict['system_size_MW_DC'] / self.input_dict['dc_ac_ratio']

        if self.input_dict['switchyard_y_n'] == 'y':
            self.input_dict['new_switchyard'] = True
        else:
            self.input_dict['new_switchyard'] = False

        self.input_dict['site_prep_area_acres_mw_dc'] = \
            self.input_dict['site_prep_area_acres_mw_ac'] * self.input_dict['dc_ac_ratio']

        site_area_in_m2 = \
            (self.input_dict['site_prep_area_acres_mw_dc'] *
             self.input_dict['system_size_MW_DC']) * 4046.86

        self.input_dict['road_length_m'] = 1.5 * ((site_area_in_m2 / 1.5) ** 0.5)

        self.input_dict['site_prep_area_acres'] = \
            self.input_dict['site_prep_area_acres_mw_dc'] * \
            self.input_dict['system_size_MW_DC']

        # 1 acre = 4046.86 m2:
        self.input_dict['site_prep_area_m2'] = \
            self.input_dict['site_prep_area_acres'] * 4046.86
