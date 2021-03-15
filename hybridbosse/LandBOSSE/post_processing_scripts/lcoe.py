import pandas as pd

if __name__ == '__main__':
    # Select every row from the AEP and TCC files
    aep = pd.read_csv('aep.csv')
    tcc = pd.read_csv('tcc.csv')

    # Select every row from the LandBOSSE output.
    # Only select the needed columns, convert MW to kW and rename the columns
    # to be consistent with the AEP and TCC data.
    bos = pd.read_excel('landbosse-output.xlsx', 'costs_by_module_type_operation')
    bos = bos[['Number of turbines', 'Turbine rating MW', 'Rotor diameter m', 'Cost per project']]
    bos['Rating [kW]'] = bos['Turbine rating MW'] * 1000
    bos.rename(columns={'Rotor diameter m': 'Rotor Diam [m]', 'Cost per project': 'BOS Capex [USD]'}, inplace=True)
    bos.drop(columns=['Turbine rating MW'], inplace=True)

    # Aggregate and sum BOS costs
    bos_sum = bos.groupby(['Rating [kW]', 'Rotor Diam [m]', 'Number of turbines']).sum().reset_index()

    # Inner join AEP and TCC. Taken together, Rating [kW] and Rotor Diam [m]
    # are the key.
    aep_tcc = aep.merge(tcc, on=['Rating [kW]', 'Rotor Diam [m]'])

    # Then join in the BOS sum data, again using Rating [kW] and
    # Rotor Diam [m] as keys. This dataframe will eventually have the
    # LCOE as a column.
    lcoe = aep_tcc.merge(bos_sum, on=['Rating [kW]', 'Rotor Diam [m]'])

    # Create columns for FCR and Opex USD/kW
    lcoe['FCR'] = 0.079
    lcoe['Opex [USD/kW]'] = 52.0

    # Now calculate LCOE and save the intermediate columns
    lcoe['Total Opex [USD]'] = lcoe['Opex [USD/kW]'] * lcoe['Rating [kW]'] * lcoe['Number of turbines']
    lcoe['Turbine Capex [USD]'] = lcoe['TCC [USD/kW]'] * lcoe['Rating [kW]'] * lcoe['Number of turbines']
    capex_times_fcr = (lcoe['BOS Capex [USD]'] + lcoe['Turbine Capex [USD]']) * lcoe['FCR']
    aep_all_turbines = lcoe['AEP [kWh/yr]'] * lcoe['Number of turbines']
    lcoe['LCOE [USD/kW]'] = (capex_times_fcr + lcoe['Total Opex [USD]']) / aep_all_turbines

    # Output an Excel spreadsheet with the results.
    with pd.ExcelWriter('lcoe_analysis.xlsx', mode='w') as writer:
        lcoe.to_excel(writer, sheet_name='LCOE', index=False)
        bos.to_excel(writer, sheet_name='BOS', index=False)
        aep.to_excel(writer, sheet_name='AEP', index=False)
        tcc.to_excel(writer, sheet_name='TCC', index=False)
