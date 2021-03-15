from hybridbosse.LandBOSSE.landbosse.model import DefaultMasterInputDict


class XlsxReader:
    """
    This class is for reading input data from .xlsx files.

    There are two sets of data to be read from .xlsx files. The first set
    of data is read from the following sheets:

    - components

    - cable_specs

    - equip

    - crane_specs

    - development

    - crew_price

    - crew

    - equip_price

    - material_price

    - construction_estimator

    - site_facility_building_area

    - weather_window

    The second set of data are read from a single sheet as described below.

    The first set of data represent a database used by the various modules. Queries on
    these data allow calculation based on labor, material, crane capacity and so on.
    These data can be shared among different projects. These data are called
    project_data.

    The second set of data represent the parameters specific to each project.
    These parameters include things values like hub height, rotor diameter,
    etc. These data are particular to a single project. These data are
    referred to as the project.

    This class also handles modifications of project data dataframes for
    parametric runs and all the other dataframe manipulations that make that
    possible.
    """

    def create_master_input_dictionary(self,
                                       project_data_dataframes,
                                       project_parameters):
        """
        This method takes a dictionary of dataframes that are the project data
        and unites them with the project parameters as found in the project
        list sheet.

        Parameters
        ----------
        project_data_dataframes : dict
            This is a dictionary for the project data .xlsx file. The keys
            are names of sheets and the values are the dataframe contents of
            the sheets.

        project_parameters : pandas.Series
            Series representing the project data, which is the second set
            of data described in the XlsxReader class docstring. The caller
            of this function is responsible for parsing out the project
            data into a series from which these data can be extracted.
            See the subclasses of XlsxManagerRunner for examples on how this
            project series is read from a spreadsheet.

        Returns
        -------
        dict
            An master input dictionary suitable to pass to an instance
            of Manager to run all the cost module sin LandBOSSE.
        """
        # First, read all inputs that come from .csv or .xlsx files.
        # erection_input_worksheets come from the input data spreadsheet.
        # Their string values are the names of the sheets in the Excel
        # workbook and the keys in the erection_project_data_dict dictionary.

        # Incomplete project dict will hold the input dictionary
        # configurations.
        incomplete_input_dict = dict()
        incomplete_input_dict['error'] = dict()

        # Read all project_data sheets.
        # The erection module takes in a bunch of keys and values under the
        # 'project_data' key in the incomplete_input_dict

        # Apply the labor multipliers
        incomplete_input_dict['labor_cost_multiplier'] = \
            project_parameters['Labor cost multiplier']
        labor_cost_multiplier = incomplete_input_dict['labor_cost_multiplier']
        self.apply_labor_multiplier_to_project_data_dict(project_data_dataframes,
                                                         labor_cost_multiplier)

        # Get the first set of data
        incomplete_input_dict['construction_estimator'] = \
            project_data_dataframes['construction_estimator']

        incomplete_input_dict['hour_day'] = \
            project_parameters['Hours per workday (hours)']

        incomplete_input_dict['solar_BOM'] = \
            project_data_dataframes['balance_of_material_1MW']

        incomplete_input_dict['site_facility_building_area_df'] = \
            project_data_dataframes['site_facility_building_area']

        incomplete_input_dict['material_price'] = \
            project_data_dataframes['material_price']

        incomplete_input_dict['crew'] = project_data_dataframes['crew']
        incomplete_input_dict['crew_cost'] = project_data_dataframes['crew_price']
        incomplete_input_dict['equip_price'] = project_data_dataframes['equip_price']

        incomplete_input_dict['pv_wire_DC_specs'] = \
            project_data_dataframes['pv_wire_DC_specs']

        incomplete_input_dict['power_cable_specs_MV_AC'] = \
            project_data_dataframes['power_cable_specs']

        # Read development tab, if it exists (it is optional since development costs
        # can be placed in the project list):
        if 'development' in project_data_dataframes:
            incomplete_input_dict['development_df'] = \
                project_data_dataframes['development']

        # TODO: Add per diem cost as input to project_list.xlsx spreadsheet
        incomplete_input_dict['construction_estimator_per_diem'] = \
            project_parameters['Labor per diem (USD/day)']

        incomplete_input_dict['fuel_cost'] = 1.5
        # TODO: Add fuel_cost as input to project_list.xlsx spreadsheet
        # incomplete_input_dict['fuel_cost'] = project_parameters['Fuel cost USD per gal']

        incomplete_input_dict['project_id'] = project_parameters['Project ID']

        incomplete_input_dict['project_data_file'] = \
            project_parameters['Project data file']

        incomplete_input_dict['construction_time_months'] = \
            project_parameters['Total project construction time (months)']

        # TODO: Add dc_ac_ratio as user input in project_list.xlsx
        incomplete_input_dict['dc_ac_ratio'] = 1.2

        incomplete_input_dict['system_size_MW_DC'] = \
            project_parameters['System Size (MW_DC)']

        incomplete_input_dict['module_rating_W'] = \
            project_parameters['Module rating (Watts)']

        # TODO: Add module length and width as user inputs in project_list.xlsx
        incomplete_input_dict['module_width_m'] = 1
        incomplete_input_dict['module_length_m'] = 1.98

        # TODO: Add module V_oc to user inputs in project_list.xlsx
        incomplete_input_dict['module_V_oc'] = 52

        # TODO: Add module I_SC to user input in project_list.xlsx
        incomplete_input_dict['module_I_SC_DC'] = 9.3  # Module short circuit current

        incomplete_input_dict['inverter_rating_kW'] = \
            project_parameters['Inverter Rating (kW)']

        # TODO: Add inverter max MPPT DC Voltage to user input in project_list.xlsx
        incomplete_input_dict['inverter_max_mppt_V_DC'] = 820

        incomplete_input_dict['modules_per_string'] = \
            project_parameters['Modules per string']

        incomplete_input_dict['max_strings_combiner_box'] = \
            project_parameters['Maximum strings per combiner box']

        incomplete_input_dict['concrete_pad_length_inches'] = \
            project_parameters['Inverter and LV/MV transformer pad length (inches)']

        incomplete_input_dict['concrete_pad_width_inches'] = \
            project_parameters['Inverter and LV/MV transformer pad width (inches)']

        incomplete_input_dict['concrete_pad_depth_inches'] = \
            project_parameters['Inverter and LV/MV transformer pad depth (inches)']

        incomplete_input_dict['concrete_pad_excavation_depth_inches'] = \
            project_parameters['Inverter and LV/MV transformer pad excavation depth (inches)']

        incomplete_input_dict['foundation_hole_ft'] = \
            project_parameters['Foundation hole length (ft)']

        incomplete_input_dict['line_freq_hz'] = \
            project_parameters['Line Frequency (Hz)']

        incomplete_input_dict['dist_interconnect_mi'] = \
            project_parameters['Distance to interconnect (miles)']

        incomplete_input_dict['interconnect_voltage_kV'] = \
            project_parameters['Interconnect Voltage (kV)']

        incomplete_input_dict['switchyard_y_n'] = \
            project_parameters['New Switchyard (y/n)']

        incomplete_input_dict['site_prep_area_acres_mw_ac'] = \
            project_parameters['Project site prep area (Acres/MW_ac)']

        incomplete_input_dict['fraction_new_roads'] = \
            project_parameters['Percent of roads that will be constructed']

        incomplete_input_dict['road_width_ft'] = \
            project_parameters['Road width (ft)']

        incomplete_input_dict['road_thickness_in'] = \
            project_parameters['Road thickness (in)']

        incomplete_input_dict['crane_width'] = \
            project_parameters['Crane width (m)']

        incomplete_input_dict['num_access_roads'] = \
            project_parameters['Number of access roads']

        incomplete_input_dict['overtime_multiplier'] = \
            project_parameters['Overtime multiplier']

        incomplete_input_dict['markup_contingency'] = \
            project_parameters['Markup contingency']

        incomplete_input_dict['markup_warranty_mgmt'] = \
            project_parameters['Markup warranty management']

        incomplete_input_dict['markup_sales_tax'] = \
            project_parameters['Markup sales and use tax']

        incomplete_input_dict['markup_overhead'] = \
            project_parameters['Markup overhead']
        incomplete_input_dict['markup_profit_margin'] = \
            project_parameters['Markup profit margin']

        incomplete_input_dict['labor_cost_multiplier'] = \
            project_parameters['Labor cost multiplier']


        # For development cost, legacy input data will specify an itemized
        # breakdown in the project data. Newer input data will specify the
        # labor cost in the project list.
        #
        # In the DevelopmentCost module, this change will be detected by the
        # absence of a development_labor_cost_usd key in the master input
        # dictionary. In that case, the development cost will be pulled from
        # the prject data.
        if 'Development labor cost USD' in project_parameters:
            incomplete_input_dict['development_labor_cost_usd'] = \
                project_parameters['Development labor cost USD']

        # These columns come from the columns in the project definition .xlsx
        incomplete_input_dict['project_id'] = project_parameters['Project ID']

        # Now fill any missing values with sensible defaults.
        defaults = DefaultMasterInputDict()
        master_input_dict = defaults.populate_input_dict(incomplete_input_dict=
                                                         incomplete_input_dict)
        return master_input_dict

    def apply_labor_multiplier_to_project_data_dict(self,
                                                    project_data_dict,
                                                    labor_cost_multiplier):
        """
        Applies the labor multiplier to the dataframes that contain the labor
        costs in the project_data_dict. The dataframes are values in the
        dictionary. The keys are "crew_price" and "construction_estimator".

        For the crew_price dataframe, the labor_cost_multiplier is broadcast
        down the "Hourly rate USD per hour" and the "Per diem USD per day" columns.

        For the construction_estimator dataframe, rows that have "Labor" for the
        "Type of cost" column are found and, for those rows, the values in the
        "Rate USD per unit" column is multiplied by the multiplier

        The dataframes are modified in place.

        Parameters
        ----------
        project_data_dict : dict
            The dictionary that has the dataframes as values.

        labor_cost_multiplier : float
            The scalar labor cost multiplier.
        """
        crew_price = project_data_dict['crew_price']
        crew_price_new_hourly_rates = crew_price['Hourly rate USD per hour'] * \
                                      labor_cost_multiplier
        crew_price_new_per_diem_rates = crew_price['Per diem USD per day'] * \
                                        labor_cost_multiplier
        crew_price['Hourly rate USD per hour'] = crew_price_new_hourly_rates
        crew_price['Per diem USD per day'] = crew_price_new_per_diem_rates

        construction_estimator = project_data_dict['construction_estimator']

        # This function maps new labor rates in construction_estimator. Used with an apply()
        # call, it will create a new Series that can be mapped back onto the
        # original dataframe.
        #
        # If the column "Type of cost" is "Labor" then return the current cost
        # times the labor multiplier. If "Type of cost" isn't "Labor" then
        # just return the current cost.
        def map_labor_rates(row):
            if row['Type of cost'] == 'Labor':
                return row['Rate USD per unit'] * labor_cost_multiplier
            else:
                return row['Rate USD per unit']

        construction_estimator_new_labor_rates = \
            construction_estimator.apply(map_labor_rates, axis=1)
        construction_estimator.drop(columns=['Rate USD per unit'],
                                    inplace=True)
        construction_estimator['Rate USD per unit'] = \
            construction_estimator_new_labor_rates
