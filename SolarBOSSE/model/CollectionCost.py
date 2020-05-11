import traceback
import math


class CollectionCost:
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
           trench along one side of the road for output circuit cables (DC), as well as
           MV power cables from each inverter station going all the way to the
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
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.project_name = project_name
        self.m2_per_acre = 4046.86
        self.inch_to_m = 0.0254

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

    def get_quadrant_dimensions(self):
        """
        1 inverter for every 1 MW_DC worth of panels. Super imposing the project layout
        on a cartesian plane, the main project road (along the long edge of the land)
        is at x = 0. And the souther most part of the project land is at y = 0. The
        area covering each unit MW_DC worth of land will be referred to as a quadrant.

               y
               |
               |
    (-x) ------|----- x
               |
               |
              (-y)
        """
        # Get length and width of each quadrant:
        land_area_acres = self.input_dict['site_prep_area_acres_mw_dc']
        land_area_per_inverter_acres = land_area_acres * \
                                       (self.input_dict['inverter_rating_kW'] / 1000)

        land_area_m2 = land_area_per_inverter_acres * self.m2_per_acre

        # Determine width & length of project land respectively:
        land_width_m = self.output_dict['land_width_m']
        subarray_width_m = land_width_m / 2
        self.output_dict['subarray_width_m'] = subarray_width_m
        land_length_m = land_area_m2 / land_width_m

        return land_length_m, land_width_m

    def inverter_list(self):
        """
        Return a tuple of inverters in the project
        """
        # Get number of inverters in the project
        number_of_inverters = self.input_dict['system_size_MW_DC']
        inverter_list = [n for n in range(number_of_inverters)]
        self.output_dict['inverter_list'] = inverter_list
        return inverter_list

    def number_panels_along_x(self):
        """
        Assuming portrait orientation of modules, with 2 modules stacked end-to-end.
        """
        subarray_width_m = self.output_dict['subarray_width_m']

        # Adding 1 inch for mid clamp:
        panel_width_m = self.input_dict['module_width_m'] + self.inch_to_m

        number_panels_along_x = math.floor(subarray_width_m / panel_width_m)
        return number_panels_along_x

    def number_rows_per_subquadrant(self):
        """
        2 sub-quadrants per quadrant; one sub-quadrant on either side of the main
        project road. 2 sub arrays per quadrant; accordingly, 1 sub-array per
        sub-quadrant. And each sub-quadrant is rated for half of quadrant's DC
        rating.
        """
        module_rating_W = self.input_dict['module_rating_W']

        # multiplied by 2 since 2 modules end-to-end in portrait orientation
        single_row_rating_W = 2 * self.number_panels_along_x() * module_rating_W

        # Since each quadrant is size according to inverter rating (DC)
        inverter_rating_W = self.input_dict['inverter_rating_kW'] * 1000
        num_rows_sub_quadrant = math.floor((inverter_rating_W / 2) / single_row_rating_W)
        return num_rows_sub_quadrant

    def run_module(self):
        """
        Runs the CollectionCost module and populates the IO dictionaries with
        calculated values.

        Parameters
        ----------
        <None>

        Returns
        -------
        tuple
            First element of tuple contains a 0 or 1. 0 means no errors happened
            and 1 means an error happened and the module failed to run. The second
            element either returns a 0 if the module ran successfully, or it returns
            the error raised that caused the failure.

        """
        try:
            project_l, project_w = self.land_dimensions()
            l, w = self.get_quadrant_dimensions()
            self.inverter_list()
            # self.number_panels_along_x()
            self.number_rows_per_subquadrant()
            return 0, 0   # module ran successfully

        except Exception as error:
            traceback.print_exc()
            print(f"Fail {self.project_name} CollectionCost")
            self.input_dict['error']['CollectionCost'] = error
            return 1, error    # module did not run successfully

