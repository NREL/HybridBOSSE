from .RackingSystemInstallation import RackingSystemInstallation
from .SitePreparationCost import SitePreparationCost
from .SubstationCost import SubstationCost
from .ManagementCost import ManagementCost
from .GridConnectionCost import GridConnectionCost


class Manager:
    """
    The Manager class distributes input and output dictionaries among the
    various modules. It maintains the hierarchical dictionary structure.
    """

    def __init__(self, input_dict, output_dict):
        """
        This initializer sets up the instance variables of:

        self.cost_modules: A list of cost module instances. Each of the
            instances must implement the method input_output.

        self.input_dict: A placeholder for the inputs dictionary

        self.output_dict: A placeholder for the output dictionary
        """
        self.input_dict = input_dict
        self.output_dict = output_dict

    def execute_solarbosse(self):

        project_name = 'solar_run'

        # RackingSystemInstallation:
        racking_system_installation = RackingSystemInstallation(input_dict=self.input_dict,
                                                                output_dict=self.output_dict,
                                                                project_name=project_name)
        racking_system_installation.run_module()

        # SitePrepCost:
        siteprep = SitePreparationCost(input_dict=self.input_dict,
                                       output_dict=self.output_dict,
                                       project_name=project_name)
        siteprep.run_module()

        # SubstationCost:
        substationcost = SubstationCost(input_dict=self.input_dict,
                                       output_dict=self.output_dict,
                                       project_name=project_name)
        substationcost.run_module()

        # ManagementCost:
        managementcost = ManagementCost(input_dict=self.input_dict,
                                       output_dict=self.output_dict,
                                       project_name=project_name)
        managementcost.run_module()

        # GridConnectionCost:
        gridconnection = GridConnectionCost(input_dict=self.input_dict,
                                            output_dict=self.output_dict,
                                            project_name=project_name)
        gridconnection.run_module()

        # Sum all costs
        self.output_dict['total_bos_cost'] = self.output_dict['total_racking_cost_USD'] + \
                                             self.output_dict['total_road_cost'] + \
                                             self.output_dict['total_substation_cost'] + \
                                             self.output_dict['total_management_cost'] + \
                                             self.output_dict['total_transdist_cost']

        return self.output_dict
