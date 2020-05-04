import os
import pandas as pd
from SolarBOSSE.excelio.create_master_input_dict import XlsxReader
from LandBOSSE.landbosse.excelio.XlsxDataframeCache import XlsxDataframeCache
from SolarBOSSE.model.Manager import Manager
from datetime import datetime, timedelta


def run_solarbosse():
    input_output_path = os.path.dirname(__file__)
    os.environ["LANDBOSSE_INPUT_DIR"] = input_output_path
    os.environ["LANDBOSSE_OUTPUT_DIR"] = input_output_path

    project_data = read_data()
    xlsx_reader = XlsxReader()
    for _, project_parameters in project_data.iterrows():
        project_data_basename = project_parameters['Project data file']
        project_data_sheets = XlsxDataframeCache.read_all_sheets_from_xlsx(
            project_data_basename)

        # make sure you call create_master_input_dictionary() as soon as
        # labor_cost_multiplier's value is changed.
        master_input_dict = xlsx_reader.create_master_input_dictionary(
            project_data_sheets, project_parameters)
        master_input_dict['error'] = dict()

    # master_input_dict = dict()
    output_dict = dict()

    # Manager class (1) manages the distribution of inout data for all modules
    # and (2) executes landbosse
    mc = Manager(input_dict=master_input_dict, output_dict=output_dict)
    mc.execute_solarbosse()

    # results dictionary that gets returned by this function:
    results = dict()
    results['errors'] = []
    if master_input_dict['error']:
        for key, value in master_input_dict['error'].items():
            msg = "Error in " + key + ": " + str(value)
            results['errors'].append(msg)
    else:   # if project runs successfully, return a dictionary with results
        # that are 3 layers deep (but 1-D)
        results['total_bos_cost'] = output_dict['total_bos_cost']
        results['total_racking_cost'] = output_dict['total_racking_cost']
        results['siteprep_cost'] = output_dict['total_road_cost']
        results['substation_cost'] = output_dict['total_substation_cost']
    return results


# This method reads in the two input Excel files (project_list; project_1)
# and stores them as data frames. This method is called internally in
# run_landbosse(), where the data read in is converted to a master input
# dictionary.
def read_data():
    path_to_project_list = os.path.dirname(__file__)
    sheets = XlsxDataframeCache.read_all_sheets_from_xlsx('project_list',
                                                          path_to_project_list
                                                          )

    # If there is one sheet, make an empty dataframe as a placeholder.
    if len(sheets.values()) == 1:
        first_sheet = list(sheets.values())[0]
        project_list = first_sheet

    # If the parametric and project lists exist, read them
    elif 'Project list' in sheets.keys():
        project_list = sheets['Project list']

    # Otherwise, raise an exception
    else:
        raise KeyError(
            "Project list needs to have a single sheet or sheets named "
            "'Project list' and 'Parametric list'."
        )

    return project_list


def read_weather_data(file_path):
    weather_data = pd.read_csv(file_path,
                               sep=",",
                               header=None,
                               skiprows=5,
                               usecols=[0, 1, 2, 3, 4]
                               )
    return weather_data


class Error(Exception):
    """
        Base class for other exceptions
    """
    pass


class SmallTurbineSizeError(Error):
    """
        Raised when user selects a turbine of rating less than 1 MW since
        LandBOSSE provides reasonable results for turbines greater than
        1 MW rating for now.
    """
    pass


class LargeTurbineSizeError(Error):
    """
            Raised when user selects a turbine of rating less than 8 MW
            since LandBOSSE provides reasonable results for turbines greater
            than 1 MW rating for now.
    """
    pass


class TurbineNumberError(Error):
    """
        Raised when number of turbines is less than 10; since LandBOSSE API
        does not currently handle BOS calculations for < 10 turbines.
    """
    pass


class NegativeInputError(Error):
    """
        User entered a negative input. This is an invalid entry.
    """
    pass


# <><><><><><><><> EXAMPLE OF RUNNING THIS SolarBOSSE API <><><><><><><><><><><>

# TODO: Un-comment these out if running this script directly.

BOS_results = run_solarbosse()
print(BOS_results)

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><
