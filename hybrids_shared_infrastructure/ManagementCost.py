def epc_developer_profit_discount(hybrid_plant_size_MW, technology_size_MW):
    """
    profit is 5% of total cost (before management cost) at 100 MW. And 8 % of TIC at 5
    MW.
    https://www.nrel.gov/docs/fy19osti/72399.pdf
    """
    if technology_size_MW == 0:
        profit_discount_multiplier = 0
    else:
        profit_discount_multiplier = (10.298 * (technology_size_MW ** (-0.157))) - \
                                     (10.298 * (hybrid_plant_size_MW ** (-0.157)))

    return profit_discount_multiplier / 100


def development_overhead_cost_discount(hybrid_plant_size_MW, technology_size_MW):
    """
    Overhead is 2% of total cost (before management cost) at 100 MW. And 12 % of TIC at 5
    MW.
    https://www.nrel.gov/docs/fy19osti/72399.pdf
    """
    if technology_size_MW == 0:
        overhead_discount_multiplier = 0
    else:
        overhead_discount_multiplier = (31.422 * (technology_size_MW ** (-0.598))) - \
                                       (31.422 * (hybrid_plant_size_MW ** (-0.598)))

    return overhead_discount_multiplier / 100
