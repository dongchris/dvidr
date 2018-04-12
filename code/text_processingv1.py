import re

def simple_process(text):
    text_list = text.split('\n')

    pattern = r'^\d+\s[\d|\D]+'
    result = {}
    for index, item in enumerate(text_list):
        if re.findall(pattern, str(item)):
            result[item] = index
    num_items = len(result.keys())
    for key in result.keys():
        result[key] = "$" + str(text_list[(result[key] + num_items)])
    return result

