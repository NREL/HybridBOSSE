
class RackingSystemInstallation:
    """
    Class for simulating installation of utility scale ground-mount
    racking system and panel installation. This portion of the project
    will take ~60% of project time. The following activities are
    considered in this class:
    1. Pile driven anchor placement
    2. Racking system assembly
    3. Solar module installation
    4. Rack wiring
    5. String testing

    """
    def __init__(self, input_dict, output_dict):
        self.input_dict = input_dict
        self.output_dict = output_dict

    def run_module(self):
        self.output_dict['total_racking_cost'] = 0
        return self.output_dict
