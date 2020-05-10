

class CollectionCost:
    """
    Assumptions:
    1. System contains central inverters of 1 MW rating each. The inverter being
    considered is a containerized solution which includes a co-located LV/MV
    transformer.
    2. PV array is rectangular in design, with an aspect ratio of 1.5:1::L:W
    3. Trench for buried cables from each string inverter runs along the perimeter
     of the system, and up till the combiner box placed at one of the 4 corners of the
     array.

     Shown below is a crude visualization of solar farm floor-plan considered in
     SolarBOSSE. As mentioned above, the aspect ratio of this solar farm is assumed
     to be 1.5:1::L:W. This is a simple, over-generalization of-course, given that it
     is the 1st version of SolarBOSSE (v.1.0.0). This model is being designed in such
     a way that any future interest to allow the user design project layout will be
     possible.

     Key:
     ||| - 3 phase HV power cables (gen-tie)
     ||  - main project road; assumed to have 20+ ton bearing capacity
     === - horizontal road running across the width of project land. Assumed to be same
           quality as the main project road (i.e. 20+ ton bearing capacity).


             [gen-tie to utility substation/point of interconnection]
                              |||
                              |||
                              |||
                              |||
                   ________   |||
     _____________|inverter|__|||____
    |            ||-------|          |
    |            ||       |substation|
    |            ||       |          |
    |            ||       |__________|
    |            ||                  |
    |            ||                  |
    |            ||________          |
    |            ||inverter|         |
    |============||==================|
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||________          |
    |            ||inverter|         |
    |============||==================|
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||________          |
    |            ||inverter|         |
    |============||==================|
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |            ||                  |
    |____________||__________________|

    Module to calculate:
    1. Wiring requirements of system. This includes:
        a. Source circuit cabling (from string to combiner box located at end of each
         row). The combiner box capacity (number of strings per box) is a user input.
        b. Output circuit; from each combiner box to that string's inverter station.
        c. Power cable home run; from inverter/transformer station (where it is
        transformed to MV) to the plant's substation which is located at the long end
        of the plant.
    """
    pass
