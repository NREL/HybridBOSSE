import pandas as pd
import math


# power = 20      # 20 MW
# head_m  = 27.4  # 90 ft

ft_to_meter = 0.3048

# head_ft = head_m/ft_to_meter

# pd.read_csv('examples/ex2.csv', names=['key', 'description', 'A', 'B', 'C'])

metadata = pd.read_excel('project_list_30mw.xlsx', sheet_name='Metadata',index_col=0)
usacost = pd.read_excel('project_list_30MW.xlsx', sheet_name='USACost')
lcmcost = pd.read_excel('project_list_30MW.xlsx', sheet_name='LCMCosts')


usacost["product08"] = usacost["%ICC(inFC)"] * usacost["08"]

total_cost = usacost.sum(axis=0)[17]
# total_cost = usacost.sum(axis=0)[17] * self.output_dict['total_initial_capital_cost']
# print(usacost)
print('Total BOS Site Prep:', total_cost)
# No need to change to dictionary if we need only ABC - dataframe is fine
# Write a function to generate cost from the lcmcost_dic



def cobb_cost_model(lcmcost, uid_case):
    """

    """
    # get the row for the uid_case and extract that particular row - based on key
    # how we confirm the variables used are right one

    a_cobb = lcmcost.at['uid_case', 'A']
    b_cobb = lcmcost.at['uid_case', 'B']
    c_cobb = lcmcost.at['uid_case', 'C']

    cost_cobb = a_cobb * (power ** b_cobb) * (head_ft ** c_cobb)


    # output_dict['site_access_cost'] = per_ICC * factor * self.output_dict['total_initial_capital_cost']

    return cost_cobb, uid_case


def cost_escalation_factor(lcmcost, uid_case):
    """

    """
    model_year = lcmcost.at['uid_case', 'CostModelYear']
    current_year = 2020     # Hard coded for now - make dynamic later

    # Use some logic here based on Construction Cost Escalation
    # Here I am using default value as a placeholder
    ce_factor_default = lcmcost.at['uid_case', 'CostEscalationFactor']
    ce_factor = (current_year - model_year)/(current_year - model_year) * ce_factor_default


    return ce_factor, uid_case


metadata_dic = metadata.to_dict()


# for index in metadata
#   metadat_dic[] = metadata.at[index, 'value']


print(metadata)

power = metadata_dic['Value']['Capacity']       # Nested Dictionaries https://www.w3schools.com/python/python_dictionaries.asp
head_ft = metadata_dic['Value']['Head']/ft_to_meter

abc = pd.read_excel('project_list_30MW.xlsx', sheet_name='LCMCosts', index_col=0)

#nsd_a = abc.loc['nsd',['A']]

nsd_a = abc.at['nsd','A']
nsd_b = abc.at['nsd','B']
nsd_c = abc.at['nsd','C']

cost_cd = nsd_a * (power**nsd_b) * (head_ft**nsd_c)
cost_kw = cost_cd/(power*1000)

print("Total cost is:", cost_cd)
print("Cost per kW is:", cost_kw)


print(nsd_b)
print(nsd_a)

### write generalized function based on key pass..

#def calculate_cobbdouglas(self, string_name):

# key = string name - what cost needs to be computed - there could be a better way to do this.
# hope that self can have project parameters eg. P, H, turbine etc.
# read the keybased array
# parce out A B C
# Calculate cost and retur cost only
#    return cost_cd, cost_kw

