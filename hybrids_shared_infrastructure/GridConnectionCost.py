def hybrid_gridconnection(input_dict):
    """
    Function to calculate total costs for transmission and distribution.

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
    output_dict = dict()
    # Switch between utility scale model and distributed model
    # Run utility version of GridConnectionCost for project size > 10 MW:
    if input_dict['system_size_MW'] > 15:
        if input_dict['dist_interconnect_mi'] == 0:
            output_dict['trans_dist_usd'] = 0
        else:
            if input_dict['new_switchyard'] is True:
                output_dict['interconnect_adder_USD'] = \
                    18115 * input_dict['interconnect_voltage_kV'] + 165944
            else:
                output_dict['interconnect_adder_USD'] = 0

            output_dict['trans_dist_usd'] = \
                ((1176 * input_dict['interconnect_voltage_kV'] + 218257) *
                 (input_dict['dist_interconnect_mi'] ** (-0.1063)) *
                 input_dict['dist_interconnect_mi']
                 ) + output_dict['interconnect_adder_USD']

    # Run distributed wind version of GridConnectionCost for project size < 15 MW:
    else:
        # Code below is for newer version of LandBOSSE which incorporates
        # distributed wind into the model. Here POI refers to point of
        # interconnection.
        output_dict['substation_to_POI_usd_per_kw'] = \
            1736.7 * ((input_dict['system_size_MW'] * 1000) ** (-0.272))

        output_dict['trans_dist_usd'] = \
            input_dict['system_size_MW'] * 1000 * output_dict['substation_to_POI_usd_per_kw']

    return output_dict['trans_dist_usd']
