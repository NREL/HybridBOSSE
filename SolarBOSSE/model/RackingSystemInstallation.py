
class RackingSystemInstallation:
    """
    Class for simulating installation of utility scale ground-mount
    racking system and panel installation. The following activities
    are considered in this class:
    1. Pile driven anchor placement
    2. Racking system assembly
    3.

    """
    def __init__(self, input_dict, output_dict):
        self.input_dict = input_dict
        self.output_dict = output_dict

    def run_module(self):
        self.output_dict['racking_installation_cost_USD'] = 0
        return self.output_dict
