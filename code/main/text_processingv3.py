import re

# def desc_coord(texts):
#     """
#     Extract description and coordinates. Remove everything below `Total`.
#     Return (description, coordinates)
#     """
#     desc_res = []
#     vertices_res = []
#     for text in texts[1:]:  # 0th bounding box is whole picture
#         desc = text.description.encode('ascii', 'ignore').decode('ascii')
#         if desc.lower() == 'total':
#             break  # remove everything below `Total`
#         desc_res.append(desc)
#         # get coordinates
#         vertices = [(vertex.x, vertex.y)
#                     for vertex in text.bounding_poly.vertices]
#         vertices_res.append(vertices)
#     return desc_res, vertices_res


def desc_coord(texts):
    """
    Extract description and coordinates. Remove everything below `Total`
    Return (description, coordinates)
    """
    desc_res = []
    vertices_res = []
    for text in texts[1:]:  # 0th bounding box is whole picture
        desc = text.description.encode('utf-8', 'ignore').decode('utf-8')
        if desc.lower() == 'total' or desc.lower() == 'tip' or \
           desc.lower() == 'guide':
            break  # remove everything below `Total` and `Tip`
        desc_res.append(desc)
        # get coordinates
        vertices = [(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices]
        vertices_res.append(vertices)
    return desc_res, vertices_res


def pre_proc(text_list):
    """
    Pre-process text: find digits matching the money pattern on the receipts.
    Return index of matching text
    """
    # assume money has 2 decimal places, which is very common.
    # e.g., $.50, .50, $1.50, 1.50, S1.50
    money_pattern = re.compile(r'^[$|S]?(\d*\.\d{2})$')
    index_list = []
    for index, money in enumerate(text_list):
        if re.findall(money_pattern, str(money)):
            text_list[index] = re.sub('^S', '$', money)  # convert S to $
            index_list.append(index)

    return index_list


def judge_neighbor(i, j, vertices):
    """
    Judge whether the item align with the money.
    Return 1 if aligned, 0 if not aligned.
    """
    vi = vertices[i]
    vj = vertices[j]
    # use the height of money box as threshold
    threshold = abs(vi[1][1] - vi[2][1])
    flag = 1
    for a, b in zip(vi, vj):               # check threshold for 4 corners
        if abs(a[1] - b[1]) > threshold:
            flag = 0
            break
    return flag


def find_neighbor(desc, vertices, m_idx):
    """
    Find aligned items for money.
    Return a dictionary: {money_idx: item_idx list}
    """
    item_idx = [i for i in range(len(desc)) if i not in set(m_idx)]
    neighbors = {i: [] for i in m_idx}

    for i in m_idx:
        for j in item_idx:
            if judge_neighbor(i, j, vertices):
                neighbors[i].append(j)
    return neighbors


def idx2text(desc, neighbors):
    """
    Convert index to text.
    Return a dictionary {item: money}
    """
    item_m = {}
    for m, item in neighbors.items():
        item = sorted(item)
        item = [desc[i] for i in item]
        item = ' '.join(item)
        m = desc[m]
        item_m[item] = m
    return item_m


# def filter_item(res):
#     """
#     Filter out not useful items.
#     Return a filtered dictionary.
#     """
#     res_clean = {}
#     pattern = re.compile(r'( \
#                  change|credit\s?card|subtotal|visa|total|x{2,}|^$)')
#     for i in res.keys():
#         if pattern.search(i.lower()) is None and \
#            re.search(r'^\$?0.00$', res[i]) is None:
#             res_clean[i] = res[i]
#
#     return res_clean


def filter_item(res):
    """
    Filter out not useful items.
    Return a filtered dictionary.
    """
    res_clean = {}
    pattern = re.compile('|'.join([r'change',
                                   r'credit\s?card',
                                   r'subtotal',
                                   r'visa',
                                   r'total',
                                   r'x{2,}',
                                   r'^$',
                                   r':',
                                   r'amount']))
    for i in res.keys():
        if (pattern.search(i.lower()) is None or 'tax' in i.lower()) and \
             re.search(r'^\$?0.00$', res[i]) is None:
            res_clean[i] = res[i]

    return res_clean


def simple_process(texts):
    # get description and coordinate for each detected component
    desc, vertices = desc_coord(texts)
    # get index for money
    m_idx = pre_proc(desc)
    # get index for corresponding items
    neighbors = find_neighbor(desc, vertices, m_idx)
    # convert index to text
    res = idx2text(desc, neighbors)
    # clena items
    res_clean = filter_item(res)
    return res_clean
