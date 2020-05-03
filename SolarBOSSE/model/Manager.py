from .RackingSystemInstallation import RackingSystemInstallation

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

    def

    def execute_solarbosse(self):

        racking_system_installation = RackingSystemInstallation(input_dict=self.input_dict,
                                                                output_dict=self.output_dict)
        self.output_dict['racking_assembly_cost'] = racking_system_installation.run_module()
        return self.output_dict['racking_assembly_cost']

