import traceback
import math
import numpy as np
import pandas as pd
from CostModule import CostModule


class CollectionCost(CostModule):
    """
    Assumptions:
    1. System contains central inverters of 1 MW rating each. The inverter being
    considered is a containerized solution which includes a co-located LV/MV
    transformer.
    2. PV array is rectangular in design, with an aspect ratio of 1.5:1::L:W
    3. Trench for buried cables from each string inverter runs along the perimeter
     of the system, and up till the combiner box placed at one of the 4 corners of the
     array.

     Shown below is a crude visualization of solar farm floor-plan considered in
     SolarBOSSE. As mentioned above, the aspect ratio of this solar farm is assumed
     to be 1.5:1::L:W. This is a simple, over-generalization of-course, given that it
     is the 1st version of SolarBOSSE (v.1.0.0). This model is being designed in such
     a way that any future interest to allow the user design project layout will be
     possible.

     Key:
     ||| - 3 phase HV power cables (gen-tie)

     ||  - main project road; assumed to have 20+ ton bearing capacity. Also contains
           trench along both sides of the road for output circuit cables (DC), as well
           as MV power cables from each inverter station going all the way to the
           substation.

     === - horizontal road running across the width of project land. Assumed to be of
           lower quality than the main project road, and not meant to support cranes.
           Smaller maintenance vehicles (like Ford F-150 permissible).



             [gen-tie to utility substation/point of interconnection]
                              |||
                              |||
                              |||
                              |||
                   ________   |||
     _____________|inverter|__|||____
    |            ||-------|          |
    |            ||       |substation|
    |            ||       |          |
    |            ||       |__________|
    |            ||                  |
    |            ||                  |
    |            ||________          |
    |            ||inverter|         |
    |============||==================|
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||________          |
    |            ||inverter|         |
    |============||==================|
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||________          |
    |            ||inverter|         |
    |============||==================|
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |____________||__________________|

    Module to calculate:
    1. Wiring requirements of system. This includes:
        a. Source circuit cabling (from string to combiner box located at end of each
         row). The combiner box capacity (number of strings per box) is a user input.
        b. Output circuit; from each combiner box to that string's inverter station.
        c. Power cable home run; from inverter/transformer station (where it is
        transformed to MV) to the plant's substation which is located at the long end
        of the plant.
    """

    def __init__(self, input_dict, output_dict, project_name):
        super(CollectionCost, self).__init__(input_dict, output_dict, project_name)
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.project_name = project_name
        self.m2_per_acre = 4046.86
        self.inch_to_m = 0.0254
        self.m_to_lf = 3.28084
        self._km_to_LF = 3.28084 * 1000

        # Max allowable voltage drop (VD%) in circuits
        self.allowable_vd_percent = 3 / 100

        # Specific resistivity of copper between 25 and 50 deg C:
        self.Cu_specific_resistivity = 11

    def land_dimensions(self):
        """
        Given user defined project area, and assumed aspect ratio of 1.5:1, calculate
        solar farm's length and width (in m)
        """
        land_area_acres = self.input_dict['site_prep_area_acres']
        land_area_m2 = land_area_acres * self.m2_per_acre

        # Determine width & length of project land respectively:
        land_width_m = (land_area_m2 / 1.5) ** 0.5
        self.output_dict['land_width_m'] = land_width_m
        land_length_m = 1.5 * land_width_m

        return land_length_m, land_width_m

    def calculate_collection_cost(self):
        """
        This is a BOS cost comming out of ICC
        """

        usacost = self.input_dict['usacost']        # this is assumed to be a dataframe

        usacost["pct_collection"] = usacost["%ICC(inFC)"] * usacost["Collection"]

        total_cost_percent = usacost.sum(axis=0)["pct_collection"]/100

        self.output_dict['collection_cost'] = total_cost_percent * self.output_dict['total_initial_capital_cost']

        return self.output_dict



    def run_module(self):
        """

        """
        try:
            # original_site_prep_area_acres = self.input_dict['site_prep_area_acres']
            #
            # self.input_dict['site_prep_area_acres'] = original_site_prep_area_acres
            self.output_dict['total_collection_cost'] = self.calculate_collection_cost()

            return 0, 0  # module ran successfully

        except Exception as error:
            traceback.print_exc()
            print(f"Fail {self.project_name} CollectionCost")
            self.input_dict['error']['CollectionCost'] = error
            return 1, error  # module did not run successfully


