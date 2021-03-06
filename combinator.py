import json
from itertools import product

import xlsxwriter

# input data
# permanent loads
g = ['G', ]

# variable loads
v = ['V', 'S', 'Rez', ['Wx', 'Wy', ], ['T_plus', 'T_minus'], 'T']
# Load cases that can not combine with each other must be list in the main list
# !!MAXIMUM 2 not combine inner arrays allowed!

# combinations coefficients for load cases
psi = {
    'V': 1,
    'S': 0.5,
    'Rez': 1,
    'Wx': 0.6,
    'Wy': 0.6,
    'T_plus': 0.6,
    'T_minus': 0.6,
    'T': 1,
    'W-x': .8,
}

gamma_f_g = 1.35
gamma_f_v = 1.5
# end of input data

base_combos = []
result_combos = {}

# generate base combos
for permanent_load in g:
    permanent_load = str(gamma_f_g) + '*' + permanent_load
    for variable_load in v:
        if isinstance(variable_load, list):
            for single_load in variable_load:
                single_load = str(gamma_f_v) + "*" + single_load
                base_combo = '+'.join([permanent_load, single_load])
                base_combos.append(base_combo)
        else:
            variable_load = str(gamma_f_v) + "*" + variable_load
            base_combo = '+'.join([permanent_load, variable_load])
            base_combos.append(base_combo)

# generate all combos
index = 0
list_check = False
combos = base_combos.copy()
current_pass = 1
for base_combo in base_combos:
    remaining = v.copy()
    removed_element = remaining.pop(index)

    if not isinstance(removed_element, list):
        index += 1
    else:
        list_len = len(removed_element)
        if current_pass == list_len:
            current_pass = 1
            index += 1
        else:
            current_pass += 1
    generated_combo = base_combo
    print(generated_combo)
    list_items = []
    generated_combo_without_no_combination = None
    while len(remaining) != 0:
        removed_remaining_item = remaining.pop(0)
        if not isinstance(removed_remaining_item, list):
            temp_gamma = str(round((psi[removed_remaining_item] * gamma_f_v), 2)) + '*'
            generated_combo += "+" + temp_gamma + removed_remaining_item
            print(generated_combo)
            combos.append(generated_combo)
        else:
            if generated_combo_without_no_combination is None:
                generated_combo_without_no_combination = generated_combo
            for single_item in removed_remaining_item:
                if not removed_remaining_item in list_items:
                    list_items.append(removed_remaining_item)
                temp_combo = generated_combo
                temp_gamma = str(round((psi[single_item] * gamma_f_v), 2)) + '*'
                temp_combo += "+" + temp_gamma + single_item
                print(temp_combo)
                combos.append(temp_combo)
    # add missing combos
    if len(list_items) == 2:
        combinated = list(product(list_items[0], list_items[1]))
        for first, last in combinated:
            temp_gamma_first = str(round((psi[first] * gamma_f_v), 2)) + '*'
            temp_gamma_last = str(round((psi[last] * gamma_f_v), 2)) + '*'
            temp_combo = generated_combo_without_no_combination + "+" + temp_gamma_first + first + \
                         "+" + temp_gamma_last + last
            print(temp_combo)
            combos.append(temp_combo)

    elif len(list_items) == 1:
        for item in list_items[0]:
            temp_gamma = str(round((psi[item] * gamma_f_v), 2)) + '*'
            temp_combo = generated_combo_without_no_combination + "+" + temp_gamma + item
            print(temp_combo)
            combos.append(temp_combo)

# generate final dict
index = 1
for item in combos:
    formatted_item = f'[{index}]' + item
    split_list = item.split('+')
    result_combos[formatted_item] = {}
    for single_item in split_list:
        single_item_split = single_item.split('*')
        result_combos[formatted_item][single_item_split[1]] = float(single_item_split[0])
    index += 1

# RESULTS
# write json
with open('combinator_result.json', 'w') as fp:
    json.dump(result_combos, fp)
# create excel
workbook = xlsxwriter.Workbook('combinator_result.xlsx')
worksheet = workbook.add_worksheet()
row = 0
for item in result_combos:
    comb_name = item
    # initial_row
    worksheet.write(row, 1, 'Linear Add')
    worksheet.write(row, 2, 'No')
    worksheet.write(row, 4, '')
    for none_cols in range(6, 10):
        worksheet.write(row, none_cols, 'None')
    worksheet.write(row, 10, '420cc500-2e93-4eac-8805-d020a7124d2f')
    # load cases
    for single_item in result_combos[item]:
        worksheet.write(row, 0, item)
        worksheet.write(row, 3, single_item)
        worksheet.write(row, 5, result_combos[item][single_item])
        row += 1
workbook.close()
