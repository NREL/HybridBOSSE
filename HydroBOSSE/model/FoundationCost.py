import traceback
import math
import pandas as pd
import numpy as np
from HydroBOSSE.model.CostModule import CostModule

class FoundationCost(CostModule):
    """
    **FoundationCost.py**

    - Refactored by Parangat Bhaskar on May 10, 2020

    \nCalculates the costs of constructing foundations for utility scale solar projects.
    Here, foundations is referring to the concrete pad that holds the inverter +
    transformer container (only).

    Not considered in this module: Racking systems foundation. Ths is done in
    RackingSystemInstallation module.

    * Get number of turbines
    * Get duration of construction
    * Get daily hours of operation*  # todo: add to process diagram
    * Get season of construction*  # todo: add to process diagram
    * [Get region]
    * Get rotor diameter
    * Get hub height
    * Get turbine rating
    * Get buoyant foundation design flag
    * [Get seismic zone]
    * Get tower technology type
    * Get hourly weather data
    * [Get specific seasonal delays]
    * [Get long-term, site-specific climate data]
    * Get price data
    * Get labor rates
    * Get material prices for steel and concrete
    * [Use region to determine weather data]


    \n\nGiven below is the set of calculations carried out in this module:

    * Calculate the foundation loads using the rotor diameter, hub height, and turbine rating

    * Determine the foundation size based on the foundation loads, buoyant foundation design flag, and type of tower technology

    * Estimate the amount of material needed for foundation construction based on foundation size and number of turbines

    * Estimate the amount of time required to construct foundation based on foundation size, hours of operation, duration of construction, and number of turbines

    * Estimate the additional amount of time for weather delays (currently only assessing wind delays) based on hourly weather data, construction time, hours of operation, and season of construction

    * Estimate the amount of labor required for foundation construction based on foundation size, construction time, and weather delay
        * Calculate number of workers by crew type
        * Calculate man hours by crew type

    * Estimate the amount of equipment needed for foundation construction based on foundation size, construction time, and weather delay
        * Calculate number of equipment by equip type
        * Calculate equipment hours by equip type

    - Calculate the total foundation cost based on amount of equipment, amount of labor, amount of material, and price data.


    **Keys in the input dictionary are the following:**

    depth
        (int) depth of foundation [in m]


    component_data
        (pd.DataFrame) data frame with wind turbine component data

    def __init__(self, input_dict, output_dict, project_name):
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.project_name = project_name


    num_turbines
        (int) total number of turbines in wind farm

    duration_construction
        (int) estimated construction time in months

    num_delays
        (int) Number of delay events

    avg_hours_per_delay
        (float) Average hours per delay event

    std_dev_hours_per_delay
        (float) Standard deviation from average hours per delay event

    delay_speed_m_per_s
        (float) wind speed above which weather delays kick in

    start_delay_hours
        (int)

    mission_time_hours
        (int)

    gust_wind_speed_m_per_s
        (float)

    wind_height_of_interest_m
        (int)

    wind_shear_exponent
        (float)

    season_construct
        list of seasons (like ['spring', 'summer']) for the construction.

    time_construct
        list of time windows for constructions. Use ['normal'] for a
        0800 to 1800 schedule 10 hour schedule. Use ['long'] for an
        overnight 1800 to 2359, 0000 to 0759 overnight schedule. Use
        ['normal', 'long'] for a 24-hour schedule.

    operational_hrs_per_day
        (float)


    material_price
        (pd.DataFrame) dataframe containing foundation cost related material prices

    construction_estimator
        (pd.DataFrame) TODO: Formal definition for construction_estimator?


    **Keys in the output dictionary are the following:**

    F_dead_kN_per_turbine
        (float) foundation dead load [in kN]

    F_horiz_kN_per_turbine
        (float) total lateral load [kN]

    M_tot_kN_m_per_turbine
        (float) Moment [kN.m]

    Radius_o_m
        (float) foundation radius based on overturning moment [in m]

    Radius_g_m
        (float) foundation radius based on gapping [in m]

    Radius_b_m
        (float) foundation radius based on bearing pressure [in m]

    Radius_m
        (float) largest foundation radius based on all three foundation design criteria: moment, gapping, bearing [in m]

    foundation_volume_concrete_m3_per_pad
        (float) volume of a round, raft foundation [in m^3]

    steel_mass_short_ton
        (float) short tons of reinforcing steel

    material_needs_per_pad
        (pd.DataFrame) table containing material needs info for -> Steel - rebar, Concrete 5000 psi, Excavated dirt, Backfill.

    operation_data
        (pd.DataFrame) TODO: What's the best one line definition for this?


    **TODO: Weather delay set of outputs -> ask Alicia for formal definitions of these keys.**

    total_foundation_cost
        (pd.DataFrame) summary of foundation costs (in USD) broken down into 4 main categories:
        1. Equipment Rental
        2. Labor
        3. Materials
        4. Mobilization
    """

    def __init__(self, input_dict, output_dict, project_name):
        """
        Parameters
        ----------
        input_dict : dict
            The input dictionary with key value pairs described in the
            class documentation

        output_dict : dict
            The output dictionary with key value pairs as found on the
            output documentation.
        """
        super(FoundationCost, self).__init__(input_dict, output_dict, project_name)
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.project_name = project_name



        #Constants used in FoundationCost class. Making this data private (hidden
        # from outside of this class):
        self._kg_per_tonne = 1000
        self._cubicm_per_cubicft = 0.0283168
        self._steel_density = 9490  # kg / m^3
        self._cubicyd_per_cubicm = 1.30795
        self._ton_per_tonne = 0.907185
        self.inches_per_meter = 0.0254

    def calculate_foundation_cost(self):
        """
        This is a BOS cost comming out of ICC
        """

        usacost = self.input_dict['usacost']        # this is assumed to be a dataframe

        usacost["pct_foundation"] = usacost["%ICC(inFC)"] * usacost["Foundation"]

        total_cost_percent = usacost.sum(axis=0)["pct_foundation"]/100

        self.output_dict['foundation_cost'] = total_cost_percent * self.output_dict['total_initial_capital_cost']

        return self.output_dict


    def run_module(self):
        """
        Runs the FoundationCost module and populates the IO dictionaries with calculated values.

        Parameters
        ----------
        <None>

        Returns
        -------
        tuple
            First element of tuple contains a 0 or 1. 0 means no errors happened and
            1 means an error happened and the module failed to run. The second element
            either returns a 0 if the module ran successfully, or it returns the error
            raised that caused the failure.

        """
        try:
            # Returns foundation volume
            self.output_dict['Foundation_cost'] = self.calculate_foundation_cost()

            return 0, 0   # module ran successfully

        except Exception as error:
            traceback.print_exc()
            print(f"Fail {self.project_name} FoundationCost")
            self.input_dict['error']['FoundationCost'] = error
            return 1, error    # module did not run successfully
