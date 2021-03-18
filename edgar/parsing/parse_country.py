import xml.etree.ElementTree as ET
import json

# with open("edgar/parsing/country_code.html", "r") as code:

#     # Parse the text.
#     root = ET.fromstring(code.read())

#     options = root.findall(path='./option')

#     country_codes = {option.text.replace(" ", "_"): option.attrib.get('value', None) for option in options if option.text}

#     # for option in options:
#     #     print(option.text)
#     #     print(option.attrib.get('value', None))

# print(country_codes)

# with open("edgar/country_codes.jsonc", mode='w+') as country_code_file:
#     json.dump(obj=country_codes, fp=country_code_file, indent=4)

with open("edgar/parsing/state_codes.html", "r") as code:

    # Parse the text.
    root = ET.fromstring(code.read())

    options = root.findall(path='./option')

    country_codes = {option.text.replace(" ", "_"): option.attrib.get('value', None) for option in options}

    # for option in options:
    #     print(option.text)
    #     print(option.attrib.get('value', None))

print(country_codes)

with open("edgar/state_codes.jsonc", mode='w+') as country_code_file:
    json.dump(obj=country_codes, fp=country_code_file, indent=4)