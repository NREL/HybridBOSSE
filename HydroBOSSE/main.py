import os
import pandas as pd
from HydroBOSSE.excelio.create_master_input_dict import XlsxReader
from LandBOSSE.landbosse.excelio.XlsxDataframeCache import XlsxDataframeCache
from HydroBOSSE.model.Manager import Manager
from HydroBOSSE.model.SitePreparationCost import SitePreparationCost


def run_hydrobosse(input_dictionary):
    input_output_path = os.path.dirname(__file__)
    # HydroBOSSE uses LandBOSSE's Excel I/O library for reading in data from Excel
    # files. Accordingly, the environment variables used in HydroBOSSE are called
    # LANDBOSSE_INPUT_DIR & LANDBOSSE_OUTPUT_DIR:
    os.environ["LANDBOSSE_INPUT_DIR"] = input_output_path
    os.environ["LANDBOSSE_OUTPUT_DIR"] = input_output_path

    project_data = read_data(input_dictionary['project_list'])
    xlsx_reader = XlsxReader()
    for _, project_parameters in project_data.iterrows():
        project_data_basename = project_parameters['Project data file']

     # print(project_data_basename)

        project_path = os.path.join(input_output_path, project_data_basename)

        # project_data_sheets = \
        #     XlsxDataframeCache.read_all_sheets_from_xlsx(project_data_basename)
        project_data_sheets = \
             XlsxDataframeCache.read_all_sheets_from_xlsx(project_path)

    # make sure you call create_master_input_dictionary() as soon as
    # labor_cost_multiplier's value is changed.
    #   Take out data_sheets with
    #    for each_sheet,_ in  project_data_sheets.endswith('_df')
    #        input_dictionary[each_sheet] = XlsxDataframeCache.copy_dataframes()


        master_input_dict = xlsx_reader.create_master_input_dictionary(
                                            project_data_sheets['metadata'], project_data_sheets['usacost_df'],
                                            project_data_sheets['lcmcosts_df'], project_parameters)

        master_input_dict['error'] = dict()

    # master_input_dict = dict()
    output_dict = dict()

    for key, _ in input_dictionary.items():
        master_input_dict[key] = input_dictionary[key]

    if 'grid_system_size_MW_DC' not in master_input_dict:
        master_input_dict['grid_system_size_MW_DC'] = master_input_dict['system_size_MW_DC']

    if 'grid_size_MW_AC' not in master_input_dict:
        master_input_dict['grid_size_MW_AC'] = \
            master_input_dict['system_size_MW_DC'] / master_input_dict['dc_ac_ratio']
    if 'Labor cost multiplier' not in master_input_dict:
        master_input_dict['Labor cost multiplier'] = 1


    # Manager class (1) manages the distribution of inout data for all modules
    # and (2) executes hydrobosse
    mc_hydro = Manager(input_dict=master_input_dict, output_dict=output_dict)
    mc_hydro.execute_hydrobosse()

    # results dictionary that gets returned by this function:
    results = dict()
    results['errors'] = []
    if master_input_dict['error']:
        for key, value in master_input_dict['error'].items():
            msg = "Error in " + key + ": " + str(value)
            results['errors'].append(msg)
    else:   # if project runs successfully, return a dictionary with results
        print("This feature temporarily disabled")
        # that are 3 layers deep (but 1-D)
        results['total_bos_cost'] = output_dict['total_bos_cost']
        results['site_preparation_cost'] = output_dict['site_preparation_cost']
        results['total_substation_cost'] = output_dict['total_substation_cost']
        results['grid_connection_cost'] = output_dict['grid_connection_cost']
        results['total_management_cost'] = output_dict['total_management_cost']
        results['total_foundation_cost'] = output_dict['total_foundation_cost']
        results['total_erection_cost'] = output_dict['total_erection_cost']
        results['total_collection_cost'] = output_dict['total_collection_cost']
        results['total_initial_capital_cost'] = output_dict['total_initial_capital_cost']

    return results, output_dict


# This method reads in the two input Excel files (project_list; project_1)
# and stores them as data frames. This method is called internally in
# run_hydrobosse(), where the data read in is converted to a master input
# dictionary.
def read_data(file_name):
    path_to_project_list = os.path.dirname(__file__)
    sheets = XlsxDataframeCache.read_all_sheets_from_xlsx(file_name,
                                                          path_to_project_list)

    # If there is one sheet, make an empty data frame as a placeholder.
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


class NegativeInputError(Error):
    """
        User entered a negative input. This is an invalid entry.
    """
    pass

# <><><><><><><><> EXAMPLE OF RUNNING THIS HydroBOSSE API <><><><><><><><><><><>
# TODO: uncomment these lines to run HydroBOSSE as a standalone model.

results_dict = dict()
results_dict['Project_Size_MW'] = list()
results_dict['Project_Head_Height'] = list()
results_dict['Total_Initial_Capital_Cost'] = list()
results_dict['Site_Peparation_Cost'] = list()
results_dict['Foundation_Cost'] = list()
results_dict['Erection_Cost'] = list()
results_dict['Total_Collection_Cost'] = list()
results_dict['Substation_Cost'] = list()
results_dict['Grid_Connection_Cost'] = list()
results_dict['Management_Cost'] = list()


project_types = ['Non-powered Dam', 'New Stream-reach Development',
                 'Canal/Conduit Project', 'Pumped Storage Hydropower Project', 'Unit Addition Project',
                 'Generator Rewind Project']

project_sizes = [1, 10, 30, 100]  # MW
head_heights = [20, 90, 250]  # feet

for size in project_sizes:
    for head_height in head_heights:
        # Create input and output dictionaries
        input_dict = dict()
        output_dict = dict()
        BOS_results = dict()
        BOS_results.update({str(size)+' MW scenario': ' '})

        # Set input parameters
        # input_dict['project_list'] = 'project_list_' + str(size) + 'MW'
        input_dict['project_list'] = 'project_list'  # .xlsx
        # Go to the closest roundup value [1 10 30 100]
        input_dict['system_size_MW_DC'] = size
        input_dict['grid_system_size_MW_DC'] = size
        input_dict['grid_size_MW_AC'] = size
        input_dict['head_height_ft'] = head_height
        input_dict['greenfield_or_existing'] = 'greenfield'

        # SitePreparationCost.calculate_siteprep_cost()       # this is giving a output dictionry
        # spc = output_dict['site_preparation_cost']
        # print('Site prep cost:', spc)

        # cobb_npd, case = HydroBOSCost.cobb_cost_model(input_dict('lcmcost'), npd)
        #
        # print('Cobb Douglas value:', cobb_npd)

        for project_type in project_types:
            input_dict['project_type'] = project_type  # Non-powered Dam, New Stream-reach Development,\
            # Canal/Conduit Project, Pumped Storage Hydropower Project, Unit Addition Project, Generator Rewind Project

            # Run HydroBOSSE
            BOS_results, detailed_results = run_hydrobosse(input_dict)

            results_dict['Project_Size_MW'].append(size)
            results_dict['Project_Head_Height'].append(head_height)
            results_dict['Total_Initial_Capital_Cost'].append(BOS_results['total_initial_capital_cost'])
            results_dict['Site_Peparation_Cost'].append(BOS_results['site_preparation_cost'])
            results_dict['Foundation_Cost'].append(BOS_results['total_foundation_cost'])
            results_dict['Erection_Cost'].append(BOS_results['total_erection_cost'])
            results_dict['Total_Collection_Cost'].append(BOS_results['total_collection_cost'])
            results_dict['Substation_Cost'].append(BOS_results['total_substation_cost'])
            results_dict['Grid_Connection_Cost'].append(BOS_results['grid_connection_cost'])
            results_dict['Management_Cost'].append(BOS_results['total_management_cost'])

            results_df = pd.DataFrame(results_dict)

            # Print Results
        #    print(BOS_results)
            bos_capex_total = BOS_results['total_initial_capital_cost']
            management_cost = BOS_results['total_management_cost']
            collection_cost = detailed_results['collection_cost']       # because it was on output dictionary
            foundation_cost = detailed_results['foundation_cost']
            grid_connection_cost = detailed_results['grid_connection_cost']
            # erection_cost = detailed_results['invertertransformer_erection_cost']   # whether module o/p is dictionary
            erection_cost = detailed_results['total_erection_cost']             # this is comming from run_module.
            substation_cost = detailed_results['total_substation_cost']

            bos_capex = bos_capex_total / (size * 1e6)
            management_capex = management_cost / (size * 1e6)
            print(str(size) + ' MW CAPEX (USD/Watt) = ' + str(round(bos_capex, 2)))
            print(str(size) + ' MW Management (USD/Watt)  = ' + str(round(management_capex, 2)))
            print(str(size) + ' MW Collection USD  = ' + str(round(collection_cost, 2)))
            print(str(size) + ' MW Foundation USD  = ' + str(round(foundation_cost, 2)))
            print(str(size) + ' MW Grid Connection USD  = ' + str(round(grid_connection_cost, 2)))
            print(str(size) + ' MW Inv Trans Erection USD  = ' + str(round(erection_cost, 2)))
            print(str(size) + ' MW Substation USD  = ' + str(round(substation_cost, 2)))

        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><
print(results_df)
results_df.to_csv()
