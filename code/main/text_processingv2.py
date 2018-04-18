import re


def simple_process(text, n):
    text_list = text.split('\n')

    # find digits matching the money pattern on the receipts
    money_pattern = re.compile('|'.join([
        r'^\$?(\d*\.\d{1,2})$',  # e.g., $.50, .50, $1.50, $.5, .5
        r'^\$?(\d+)$',  # e.g., $500, $5, 500, 5
        r'^\$(\d+\.?)$',  # e.g., $5.
    ]))
    index_list = []
    for index, money in enumerate(text_list):
        if re.findall(money_pattern, str(money)):
            index_list.append(index)

    # group the index with one jump together
    stack = []
    sub_group = [index_list[0]]
    for i in range(1, (len(index_list))):
        if index_list[i] - sub_group[-1] == 1:
            sub_group.append(index_list[i])
            continue
        else:
            stack.append(sub_group)
            sub_group = [index_list[i]]
    stack.append(sub_group)

    result = {}
    for sub_group in stack:
        if len(sub_group) < n: continue
        for j in sub_group[:n]:
            result[text_list[j - n]] = text_list[j]

    return result
