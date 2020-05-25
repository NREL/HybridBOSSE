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


def site_facility(hybrid_plant_size_MW, hybrid_construction_months, num_turbines):
    """
    Uses empirical data to estimate cost of site facilities and security, including


    Site facilities:

    Building design and construction

    Drilling and installing a water well, including piping

    Electric power for a water well

    Septic tank and drain field


    Site security:

    Constructing and reinstating the compound

    Constructing and reinstating the batch plant site

    Setting up and removing the site offices for the contractor, turbine supplier, and owner

    Restroom facilities

    Electrical and telephone hook-up

    Monthly office costs

    Signage for project information, safety and directions

    Cattle guards and gates

    Number of access roads



    In main.py, a csv is loaded into a Pandas dataframe. The columns of the
    dataframe must be:

    Size Min (MW)
        Minimum power output for a plant that needs a certain size of
        building.

    Size Max (MW)
        Maximum power output of a plant that need a certain size of
        building.

    Building Area (sq. ft.)
        The area of the building needed to provide O & M support to plants
        with power output between "Size Min (MW)" and "Size Max (MW)".

    Returns
    -------
    float
        Building area in square feet
    """

    if hybrid_plant_size_MW > 15:
        building_area_sq_ft = float(4000)

        construction_building_cost = building_area_sq_ft * 125 + 176125

        ps = hybrid_plant_size_MW
        ct = hybrid_construction_months
        nt = num_turbines
        if nt < 30:
            nr = 1
            acs = 30000
        elif nt < 100:
            nr = round(0.05 * nt)
            acs = 240000
        else:
            nr = round(0.05 * nt)
            acs = 390000
        compound_security_cost = 9825 * nr + 29850 * ct + acs + 60 * ps + 62400

        site_facility_cost = construction_building_cost + compound_security_cost

    else:
        site_facility_cost = 0

    return site_facility_cost
