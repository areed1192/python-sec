import xml.etree.ElementTree as ET
import pprint
import csv

# Define the file path.
file_htm = r'C:\Users\Alex\OneDrive\Growth - Tutorial Videos\Lessons - SEC\0001326801-19-000069-xbrl\fb-09302019x10q.htm'
file_cal = r'C:\Users\Alex\OneDrive\Growth - Tutorial Videos\Lessons - SEC\0001326801-19-000069-xbrl\fb-20190930_cal.xml'
file_lab = r'C:\Users\Alex\OneDrive\Growth - Tutorial Videos\Lessons - SEC\0001326801-19-000069-xbrl\fb-20190930_lab.xml'
file_def = r'C:\Users\Alex\OneDrive\Growth - Tutorial Videos\Lessons - SEC\0001326801-19-000069-xbrl\fb-20190930_def.xml'

# Initalize my master dictionary list, this will store the content as I parse it.
dict_list = []

'''
    STEP 1: PARSE THE LABELS FILE.
'''

# Load the file into the `ElementTree.Parse` function.
tree = ET.parse(file_lab)

# Every `ElementTree` has a Root Node. This is the starting point of our tree.
root_node = tree.getroot().tag

# I use the root node, extract the namespace. The namespace will exist in every node we have, this can make parsing a little challenging.
# I rather not have it at all and just remove it from the content as I'm parsing it.
root_node_name_space =  root_node.split('}')[0] + '}'

# Labels come in two forms, those I want and those I don't want.
avoids = ['linkbase','roleRef']
parse = ['label','labelLink','labelArc','loc','definitionLink','definitionArc','calculationArc']


# Grab all the definition links.
label_links = tree.findall(r'{http://www.xbrl.org/2003/linkbase}labelLink')

# loop through each label in the tree.
for label_link in label_links:
    for label_element in label_link.iter():

        # split the label to remove the namespace component, we now have a list.
        split_label = label_element.tag.split('}')

        # The first element is the namespace, and the second element is a label.
        namespace = split_label[0]
        label = split_label[1]

        # Grab the label value and check if it's in the parse list.
        if label in parse:

            # create a dictionary for to store the values
            dict_storage = {}
            dict_storage['item_type'] = 'label_' + label

            # grab the attribute keys
            label_keys = label_element.keys()

            # for each key.
            for key in label_keys:
                
                # parse if needed.
                if '}' in key:

                    # add the new key to the dictionary and grab the old value.
                    new_key = key.split('}')[1]
                    dict_storage[new_key] = link_label.attrib[key]
                else:
                    # grabe the value.
                    dict_storage[key] = link_label.attrib[key]

            # add to the dictionary
            dict_list.append(dict_storage)

'''
    STEP 2: PARSE THE DEFINITIONS FILE.
'''

# Parse the tree.
tree = ET.parse(file_def)

# Grab all the definition links.
definition_links = tree.findall(r'{http://www.xbrl.org/2003/linkbase}definitionLink')

# Loop through the definition links
for definition_link in definition_links:

    # each definition link can have it's own children, so loop through those.
    for definition in definition_link.iter():

        # split the label to remove the namespace component, we now have a list.
        split_label = definition.tag.split('}')

        # The first element is the namespace, and the second element is a label.
        namespace = split_label[0]
        label = split_label[1]

        if label in parse:

            # create a dictionary for to store the values
            dict_storage = {}
            dict_storage['item_type'] = 'definition_' + split_label[1]

            # grab the attribute keys
            def_keys = definition.keys()

            # for each key.
            for key in def_keys:

                 # parse if needed.
                if '}' in key:

                    # add the new key to the dictionary and grab the old value.
                    new_key = key.split('}')[1]
                    dict_storage[new_key] = definition.attrib[key]

                else:
                    # grabe the value.
                    dict_storage[key] = definition.attrib[key]

            # add to dictionary.
            dict_list.append(dict_storage)

'''
    STEP 3: PARSE THE CALCULATIONS FILE.
'''

# Parse the tree.
tree = ET.parse(file_cal)

# Grab all the calculation links.
calculation_links = tree.findall(r'{http://www.xbrl.org/2003/linkbase}calculationLink')

# Loop throught the calculation links
for calculation_link in calculation_links:

    # each calculation link can have their own children, so loop through those.
    for calculation in calculation_link.iter():

        # split the label to remove the namespace component, we now have a list.
        split_label = calculation_link.tag.split('}')

        # The first element is the namespace, and the second element is a label.
        namespace = split_label[0]
        label = split_label[1]

        if label in parse:

            dict_storage = {}
            dict_storage['item_type'] = 'calculation_' + split_label[1]

            # grab the attribute keys
            cal_keys = calculation.keys()

            # for each key.
            for key in cal_keys:

                 # parse if needed.
                if '}' in key:

                    # add the new key to the dictionary and grab the old value.
                    new_key = key.split('}')[1]
                    dict_storage[new_key] = calculation.attrib[key]

                else:
                    # grabe the value.
                    dict_storage[key] = calculation.attrib[key]

            # add to dictionary.
            dict_list.append(dict_storage)