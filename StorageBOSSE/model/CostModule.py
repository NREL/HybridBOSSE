class CostModule:
    """
    This is a super class for all other cost modules to import
    that provides shared pre-processed data.
    """

    def __init__(self, input_dict, output_dict, project_name):
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.project_name = project_name

        if self.input_dict['switchyard_y_n'] == 'y':
            self.input_dict['new_switchyard'] = True
        else:
            self.input_dict['new_switchyard'] = False


