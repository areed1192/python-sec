import xml.etree.ElementTree as ET
import pprint
import csv

'''
    When parsing an SEC Filing that contains XBLR files, it's curucial that you know how the files are structured
    and what each file contains. If you skip this portion it's very easy to get lost in the process and lose sight
    of how to get the data.

        CALCULATION FILE: TradingSymbol_EndDate_cal.xml
        This contains links to different calculations in the file this will be useful when trying to 
        reference how certain calculations were made.

        DEFINITION FILE: TradingSymbol_EndDate_def.xml
        This contains links to different definitions used in the 10K/Q and also external resources 
        that define those definitions, this would be entities like FASB.

        LABEL FILE: TradingSymbol_EndDate_lab.xml
        This contains a section for each label in the document along with their corresponding ID used 
        in the XML structuring. Additionally each one these labels also has a locator that will provide 
        a hyperlink to that label in the file.

        PRESENTATION FILE: TradingSymbol_EndDate_pre.xml
        This provides more links to different presentations that contain information regarding different 
        sections of the filing.

    The general strategy is as follows:

        1. Parse the labels file.
        2. Parse the definitions file, and match the information to the labels file.
        3. Parse the calculations file, and match the information to the labels file.
        4. Parse the maind HTML file.
'''


# Define the file path.
file_htm = r'C:\Users\Alex\OneDrive\Growth - Tutorial Videos\Lessons - SEC\0001326801-19-000069-xbrl\fb-09302019x10q.htm'
file_cal = r'C:\Users\Alex\OneDrive\Growth - Tutorial Videos\Lessons - SEC\0001326801-19-000069-xbrl\fb-20190930_cal.xml'
file_lab = r'C:\Users\Alex\OneDrive\Growth - Tutorial Videos\Lessons - SEC\0001326801-19-000069-xbrl\fb-20190930_lab.xml'
file_def = r'C:\Users\Alex\OneDrive\Growth - Tutorial Videos\Lessons - SEC\0001326801-19-000069-xbrl\fb-20190930_def.xml'

# # Initalize my master dictionary list, this will store the content as I parse it.
# dict_list = []

# '''
#     STEP 1: PARSE THE LABELS FILE.
# '''

# # Load the file into the `ElementTree.Parse` function.
# tree = ET.parse(file_lab)

# # Every `ElementTree` has a Root Node. This is the starting point of our tree.
# root_node = tree.getroot().tag

# # I use the root node, extract the namespace. The namespace will exist in every node we have, this can make parsing a little challenging.
# # I rather not have it at all and just remove it from the content as I'm parsing it.
# root_node_name_space =  root_node.split('}')[0] + '}'

# # Labels come in two forms, those I want and those I don't want.
# avoids = ['linkbase','roleRef']
# parse = ['label','labelLink','labelArc','loc','definitionLink','definitionArc','calculationArc']


# # Grab all the definition links.
# label_links = tree.findall(r'{http://www.xbrl.org/2003/linkbase}labelLink')

# # loop through each label in the tree.
# for label_link in label_links:
#     for label_element in label_link.iter():

#         # split the label to remove the namespace component, we now have a list.
#         split_label = label_element.tag.split('}')

#         # The first element is the namespace, and the second element is a label.
#         namespace = split_label[0]
#         label = split_label[1]

#         # Grab the label value and check if it's in the parse list.
#         if label in parse:

#             # create a dictionary for to store the values
#             dict_storage = {}
#             dict_storage['item_type'] = 'label_' + label

#             # grab the attribute keys
#             label_keys = label_element.keys()

#             # for each key.
#             for key in label_keys:
                
#                 # parse if needed.
#                 if '}' in key:

#                     # add the new key to the dictionary and grab the old value.
#                     new_key = key.split('}')[1]
#                     dict_storage[new_key] = link_label.attrib[key]
#                 else:
#                     # grabe the value.
#                     dict_storage[key] = link_label.attrib[key]

#             # add to the dictionary
#             dict_list.append(dict_storage)

# '''
#     STEP 2: PARSE THE DEFINITIONS FILE.
# '''

# # Parse the tree.
# tree = ET.parse(file_def)

# # Grab all the definition links.
# definition_links = tree.findall(r'{http://www.xbrl.org/2003/linkbase}definitionLink')

# # Loop through the definition links
# for definition_link in definition_links:

#     # each definition link can have it's own children, so loop through those.
#     for definition in definition_link.iter():

#         # split the label to remove the namespace component, we now have a list.
#         split_label = definition.tag.split('}')

#         # The first element is the namespace, and the second element is a label.
#         namespace = split_label[0]
#         label = split_label[1]

#         if label in parse:

#             # create a dictionary for to store the values
#             dict_storage = {}
#             dict_storage['item_type'] = 'definition_' + split_label[1]

#             # grab the attribute keys
#             def_keys = definition.keys()

#             # for each key.
#             for key in def_keys:

#                  # parse if needed.
#                 if '}' in key:

#                     # add the new key to the dictionary and grab the old value.
#                     new_key = key.split('}')[1]
#                     dict_storage[new_key] = definition.attrib[key]

#                 else:
#                     # grabe the value.
#                     dict_storage[key] = definition.attrib[key]

#             # add to dictionary.
#             dict_list.append(dict_storage)

# '''
#     STEP 3: PARSE THE CALCULATIONS FILE.
# '''

# # Parse the tree.
# tree = ET.parse(file_cal)

# # Grab all the calculation links.
# calculation_links = tree.findall(r'{http://www.xbrl.org/2003/linkbase}calculationLink')

# # Loop throught the calculation links
# for calculation_link in calculation_links:

#     # each calculation link can have their own children, so loop through those.
#     for calculation in calculation_link.iter():

#         # split the label to remove the namespace component, we now have a list.
#         split_label = calculation_link.tag.split('}')

#         # The first element is the namespace, and the second element is a label.
#         namespace = split_label[0]
#         label = split_label[1]

#         if label in parse:

#             dict_storage = {}
#             dict_storage['item_type'] = 'calculation_' + split_label[1]

#             # grab the attribute keys
#             cal_keys = calculation.keys()

#             # for each key.
#             for key in cal_keys:

#                  # parse if needed.
#                 if '}' in key:

#                     # add the new key to the dictionary and grab the old value.
#                     new_key = key.split('}')[1]
#                     dict_storage[new_key] = calculation.attrib[key]

#                 else:
#                     # grabe the value.
#                     dict_storage[key] = calculation.attrib[key]

#             # add to dictionary.
#             dict_list.append(dict_storage)

# Initalize some dictionaries to store some values.
storage_values = {}
storage_gaap = {}

# Initalize my master dictionary list, this will store the content as I parse it.
dict_list = []

# Initalize my list of files I plan to parse.
files_list = [
    (file_cal, r'{http://www.xbrl.org/2003/linkbase}calculationLink', 'calculation'), 
    (file_def, r'{http://www.xbrl.org/2003/linkbase}definitionLink','definition'), 
    (file_lab, r'{http://www.xbrl.org/2003/linkbase}labelLink','label')
    ]

# Labels come in two forms, those I want and those I don't want.
avoids = ['linkbase','roleRef']
parse = ['label','labelLink','labelArc','loc','definitionLink','definitionArc','calculationArc']

# part of the process is matching up keys, to do that we will store some keys as we parse them.
lab_list = set()
cal_list = set()

# loop through each file.
for file in files_list:

    # Parse the tree by passing through the file.
    tree = ET.parse(file[0])

    # Grab all the calculation links.
    links = tree.findall(file[1])

    # Loop throught the calculation links
    for link in links:

        # each calculation link can have their own children, so loop through those.
        for link_element in link.iter():

            # split the label to remove the namespace component, we now have a list.
            split_label = link_element.tag.split('}')

            # The first element is the namespace, and the second element is a label.
            namespace = split_label[0]
            label = split_label[1]

            # if it's a label we want then continue.
            if label in parse:

                # define the item type label
                item_type_label = file[2] + '_' + split_label[1]
                
                # initalize a smaller dictionary that will house all the content from that element.
                dict_storage = {}
                dict_storage['item_type'] = item_type_label

                # grab the attribute keys
                cal_keys = link_element.keys()

                # for each key.
                for key in cal_keys:

                    # parse if needed.
                    if '}' in key:

                        # add the new key to the dictionary and grab the old value.
                        new_key = key.split('}')[1]
                        dict_storage[new_key] = link_element.attrib[key]

                    else:
                        # grabe the value.
                        dict_storage[key] = link_element.attrib[key]

                # add important values to the set list.
                if item_type_label == 'label_label':

                    key_store = dict_storage['label']
                    master_key = key_store.replace('lab_','')

                    label_split = master_key.split('_')
                    label_split_joined = label_split[0] + ':' + label_split[1]
                    storage_values[master_key] = {}
                    storage_values[master_key][label_split[0]] = label_split_joined
                    storage_values[master_key]['label_id'] = key_store
                    storage_values[master_key]['location_id'] = key_store.replace('lab_','loc_')
                    storage_values[master_key]['us_gaap_id'] = label_split_joined
                    storage_values[master_key]['us_gaap_value'] = None
                    storage_values[master_key][item_type_label] = dict_storage 

                    storage_gaap[label_split_joined] = {}
                    storage_gaap[label_split_joined]['id'] = label_split_joined
                    storage_gaap[label_split_joined]['master_id'] = master_key


                # add to dictionary.
                dict_list.append([file[2], dict_storage])

'''
    PARSE THE HTML FILE.
'''

# Load the HTML file.
tree = ET.parse(file_htm)

# create a new dictionary to store context info.
context_dictionary = {}

# loop through all the elements in the HTML file.
for element in list(tree.iter()):
    
    # for nonNumber the content is different.
    if 'nonNumeric' in element.tag:
        storage_gaap[element.attrib['name']]['context_ref'] = element.attrib['contextRef']
        storage_gaap[element.attrib['name']]['context_id'] = element.attrib['id']
        storage_gaap[element.attrib['name']]['continued_at'] = element.attrib.get('continuedAt','null')
        storage_gaap[element.attrib['name']]['escape'] = element.attrib.get('escape','null')
        storage_gaap[element.attrib['name']]['escape'] = element.attrib.get('format','null')
        if storage_gaap[element.attrib['name']]['master_id'] in storage_values:
            storage_values[storage_gaap[element.attrib['name']]['master_id']]['us_gaap_value'] = storage_gaap[element.attrib['name']]  

    # same for nonFraction tags.
    if 'nonFraction' in element.tag:
        storage_gaap[element.attrib['name']]['context_ref'] = element.attrib['contextRef']
        storage_gaap[element.attrib['name']]['fraction_id'] = element.attrib['id']
        storage_gaap[element.attrib['name']]['unit_ref'] = element.attrib.get('unitRef','null')
        storage_gaap[element.attrib['name']]['decimals'] = element.attrib.get('decimals','null')
        storage_gaap[element.attrib['name']]['scale'] = element.attrib.get('scale','null')
        storage_gaap[element.attrib['name']]['format'] = element.attrib.get('format','null')
        storage_gaap[element.attrib['name']]['value'] = element.text.strip() if element.text else 'Null'
        if storage_gaap[element.attrib['name']]['master_id'] in storage_values:
            storage_values[storage_gaap[element.attrib['name']]['master_id']]['us_gaap_value'] = storage_gaap[element.attrib['name']]    

    
    # context is very different.
    if 'context' in element.tag:
        context_dictionary[element.attrib['id']] = {}
        for cnx_item in element.iter():
            for att in cnx_item.attrib:
                if att:
                    context_dictionary[element.attrib['id']][att] = cnx_item.attrib[att]
                    if cnx_item.text.strip() != '':
                        context_dictionary[element.attrib['id']]['text'] = cnx_item.text.strip()
                    else:
                        context_dictionary[element.attrib['id']]['text'] = 'Null'
    

# pprint.pprint(storage_values.keys())
# pprint.pprint(dict_list)
# for key in storage_gaap:
#     if storage_gaap[key]['master_id'] in storage_values:
#         storage_values[storage_gaap[key]['master_id']]['us_gaap_value'] = storage_gaap[key]



# pprint.pprint(context_dictionary)              

# INTERSTING DIRECTORIES - SEC
# country
# naics
# invest
# exch
# dei
# stpr
# sic
# currency

# INTERSTING DIRECTORIES - FASB
# us-gaap

# https://xbrl.sec.gov/invest/
# https://xbrl.sec.gov/sic/2020
# https://xbrl.sec.gov/country/2020/country-lab-2020-01-31.xml
# https://xbrl.sec.gov/naics/2017/naics-doc-2017-01-31.xml
# https://xbrl.sec.gov/currency/2020/currency-lab-2020-01-31.xml
# https://xbrl.sec.gov/exch/2020/
# https://xbrl.sec.gov/dei
# https://xbrl.sec.gov/stpr
# http://xbrl.fasb.org/us-gaap/

# https://www.sec.gov/data.json



# first write the xbrl_content.
file_name = 'sec_xbrl_content.csv'

# open the file.
with open(file_name, mode='w', newline='') as sec_file:

    # create the writer.
    writer = csv.writer(sec_file)

    # write the header.
    writer.writerow(['FILE','LABEL','VALUE'])

    # dump the dict to the csv file.
    for dict_cont in dict_list:
        for item in dict_cont[1].items():
            writer.writerow([dict_cont[0]] + list(item))


# second write the filing_values.
file_name = 'sec_xbrl_values.csv'

# open the file.
with open(file_name, mode='w', newline='') as sec_file:

    # create the writer.
    writer = csv.writer(sec_file)

    # write the header.
    writer.writerow(['ID','CATEGORY','LABEL','VALUE'])

    # start at level 1
    for storage_1 in storage_values:

        # level two is grab the items.
        for storage_2 in storage_values[storage_1].items():

            # if the value is a dictionary, we have one more possible level.
            if isinstance(storage_2[1], dict):

                # level three grab the items.
                for storage_3 in storage_2[1].items():

                    # Write the values to the csv.
                    writer.writerow([storage_1] + [storage_2[0]] + list(storage_3))

            # else just write it to the CSV.
            else:
                if storage_2[1] != None:
                    writer.writerow([storage_1] + list(storage_2) + ['None'])  