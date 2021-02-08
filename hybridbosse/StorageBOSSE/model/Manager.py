from .SitePreparationCost import SitePreparationCost
from .SubstationCost import SubstationCost
from .ManagementCost import ManagementCost
from .GridConnectionCost import GridConnectionCost
from .FoundationCost import FoundationCost
from .ContainerErection import ContainerErection
from .CollectionCost import CollectionCost
from .LayoutOptimizer import LayoutOptimizer
import numpy as np


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

        self.input_dict['system_size_MW_AC'] = \
            self.input_dict['system_size_MW_DC'] / self.input_dict['dc_ac_ratio']

        # calculate number of containers based on desired system sizes
        self.output_dict['num_containers'] = np.ceil(max(self.input_dict['system_size_MW_DC'] / self.input_dict['battery_power_MW'], \
                                                         self.input_dict['system_size_MWh'] / self.input_dict['battery_capacity_MWh']))

        # check to see if enough containers are included in custom layout
        if self.input_dict['layout'] == 'custom':
            num_layout = self.input_dict['num_full_row']*self.input_dict['pad_per_row'] + self.input_dict['num_left']
            if num_layout < self.output_dict['num_containers']:
                print('need at least ' +str(self.output_dict['num_containers']) + ' containers to satisfy system'
                      'requirements. Only ' + str(num_layout) + ' containers specified in custom layout.')
                exit(1)

        # Battery CAPEX  (USD)
        self.output_dict['total_container_cost'] = self.output_dict['num_containers'] * self.input_dict['container_cost']

    def execute_storagebosse(self):

        project_name = 'storage_run'

        layout_optimizer = LayoutOptimizer(input_dict=self.input_dict,
                                       output_dict=self.output_dict)
        layout_optimizer.run_module()

        siteprep = SitePreparationCost(input_dict=self.input_dict,
                                       output_dict=self.output_dict,
                                       project_name=project_name)
        siteprep.run_module()

        collection_system = CollectionCost(input_dict=self.input_dict,
                                           output_dict=self.output_dict,
                                           project_name=project_name)
        collection_system.run_module()

        foundation_cost = FoundationCost(input_dict=self.input_dict,
                                         output_dict=self.output_dict,
                                         project_name=project_name)
        foundation_cost.run_module()

        container_erection = ContainerErection(input_dict=self.input_dict,
                                               output_dict=self.output_dict,
                                               project_name=project_name)
        container_erection.run_module()

        substationcost = SubstationCost(input_dict=self.input_dict,
                                        output_dict=self.output_dict,
                                        project_name=project_name)
        substationcost.run_module()

        gridconnection = GridConnectionCost(input_dict=self.input_dict,
                                            output_dict=self.output_dict,
                                            project_name=project_name)
        gridconnection.run_module()

        # Sum all costs
        # print('Manager Output Dict:')
        # print(self.output_dict)
        # self.output_dict['total_road_cost'] = 0
        self.output_dict['total_bos_cost_before_mgmt'] = \
            self.output_dict['total_road_cost'] + \
            self.output_dict['total_collection_cost'] + \
            self.output_dict['total_substation_cost'] + \
            self.output_dict['total_transdist_cost'] + \
            self.output_dict['total_foundation_cost'] + \
            self.output_dict['total_erection_cost']


        # ManagementCost:
        managementcost = ManagementCost(input_dict=self.input_dict,
                                        output_dict=self.output_dict,
                                        project_name=project_name)
        managementcost.run_module()
        if 'management_cost_multiplier' in self.input_dict:
            self.output_dict['total_management_cost'] *= self.input_dict['management_cost_multiplier']

        self.output_dict['total_bos_cost'] = \
            self.output_dict['total_bos_cost_before_mgmt'] + \
            self.output_dict['total_management_cost']
        self.output_dict['total_cost'] = self.output_dict['total_container_cost'] + self.output_dict['total_bos_cost']

        return self.output_dict
