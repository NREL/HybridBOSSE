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
    if 'hybrid_substation' not in input_dict:
        mode = input_dict['project_mode']
        power = input_dict['hybrid_substation_rating_MW']
        if mode == 1 or mode == 3 or mode == 4:
            if power > 15:
                output_dict['substation_cost_usd'] = \
                    11652 * (input_dict['interconnect_voltage_kV'] + input_dict['hybrid_substation_rating_MW']) + \
                    11795 * (power ** 0.3549) + 1526800

            else:
                if power > 10:
                    output_dict['substation_cost_usd'] = 1000000
                else:  # that is, < 10 MW_AC
                    output_dict['substation_cost_usd'] = 500000
        else:
            if power > 600:
                output_dict['substation_cost_usd'] = power*119000 + 88000000
            else:
                output_dict['substation_cost_usd'] = power*17350 * 1.19
            #DC substation

        substation_cost_usd = output_dict['substation_cost_usd']

    return substation_cost_usd
