def hybrid_substation(input_dict):
    """
    Function to calculate Substation Cost in USD

    Parameters
    -------
    interconnect_voltage_kV
        (in kV)

    project_size_megawatts
        (in MW)


    Returns:
    -------
    substation_cost
        (in USD)

    """
    output_dict = dict()

    if input_dict['hybrid_substation_rating_MW'] > 15:
        output_dict['substation_cost_usd'] = \
            11652 * (input_dict['interconnect_voltage_kV'] + input_dict['hybrid_substation_rating_MW']) + \
            11795 * (input_dict['hybrid_substation_rating_MW'] ** 0.3549) + 1526800

    else:
        if input_dict['hybrid_substation_rating_MW'] > 10:
            output_dict['substation_cost_usd'] = 1000000
        else:  # that is, < 10 MW_AC
            output_dict['substation_cost_usd'] = 500000

    substation_cost_usd = output_dict['substation_cost_usd']

    return substation_cost_usd
