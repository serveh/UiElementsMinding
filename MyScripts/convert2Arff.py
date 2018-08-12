import arff
import pprint
import json


def load_arff(filename='/home/srwe/Downloads/widget_events_200.arff/widget_events_200.arff'):
    data = arff.load(open(filename, 'rb'))
    for att_name, att_type in data['attributes']:
        print('%s, ' % (att_name))
        if att_name in ['Type']:
            print((att_type))


def get_ralative_element_ids(in_element):
    ids = []
    if in_element is not None:
        for tmp_el in in_element:
            ids.append(tmp_el['int']['text'])

    return ids


def get_app_data(app_serialized_file='/home/srwe/work/project/backstage/apks/mobi.infolife.ezweather.widget.figures/appSerialized.json'):
    with open(app_serialized_file) as f:
        app_data = json.load(f)

    parent_IDs=[]
    child_IDS=[]
    text=[]
    ui_types=[]
    event_handler=[]
    ids=[]
    for ui_elem in app_data:
        ids.append(ui_elem['id']['text'])
        parent_IDs.append(ui_elem['parentIDs']['sub_feat'])
        child_IDS.append(ui_elem['childIDs']['sub_feat'])
        text.append(ui_elem['text']['text'])
        ui_types.append(ui_elem['kindOfUiElement']['text'])
        event_handler.append(kindOfUiElement['listeners']['sub_feat'])

    found = 0
    cur_list = child_IDS
    for el in cur_list:
        try:
            idx = ids.index(el)
            found += 1
            parent_IDs[im][el] = ui_types[idx]
        except ValueError:
            print('Not found element {} index is {}'.format(el, cur_list.index(el)))

    print('found {} out of {}'.format(found, len(cur_list)))

    print (app_data)


if __name__ == "__main__":
    get_app_data()

    # do it for all app
    # remove number ids and transfer properties remeber to add appName
    #  add to the total list of all apps
    # extract unique valueList for each feature
    # generate arff file