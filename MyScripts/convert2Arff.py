import arff
import json, os
import itertools
import six

import standard_types as st_types
from distance import ilevenshtein

APP_SERIALIZED_FILE_JSON = 'appSerialized.json'

# Mapping UI elements types to list of standard type (define based on orginal Andriod types provided by Nataniel) by computing string similarity distance, Levenshtein
def refine_types(type_list):
    std_types = st_types.get_standard_type()
    std_types = [tt.lower() for tt in std_types]
    refined_types = [sorted(ilevenshtein(tt.lower(), std_types))[0][1] for tt in type_list]
    return refined_types

# Removing all duplicated items in given list and return a lowercase list
def remove_duplicate_and_to_small(feature_list):

    for idx, features in enumerate(feature_list):
        if isinstance(features, list):
            feature_list[idx] = list(set([feature.lower() for feature in features]))
        elif isinstance(features, six.string_types):
            feature_list[idx] = features.lower()

    return feature_list

# return a stripped string by deleting blank space
def prepare_text(text_feature):
    for idx, txt in enumerate(text_feature):
        if txt is None:
            txt= ''
        text_feature[idx] = txt.strip(' \t\n\r')
    text_feature = [el.lower() for el in text_feature]
    return text_feature

# return type value os element instead of index value for parents and children
def dereference(ids, element_types, ref_ids, serialized_file):
    assert len(ids) == len(element_types) == len(ref_ids)

    deref_element =[]
    grand = []
    for ref_list in ref_ids:
        if not ref_list:
            deref_element.append(ref_list)
            grand.append(ref_list)
        else:
            tmp_list = []
            tmp_grand = []
            for id in ref_list:
                # exclude one exception
                if serialized_file != '/home/srwe/work/project/backstage/apks/menion.android.locus/appSerialized.json' \
                        and id !='0':
                    index = ids.index(id)
                    tmp_list.append(element_types[index])
                    tmp_grand.append(index)
            deref_element.append(tmp_list)
            grand.append(tmp_grand)

    for idx, ll in enumerate(grand):
        if len(ll):
            for jj, index in enumerate(ll):
                grand[idx][jj] = deref_element[index]

    return deref_element, grand

# passes the event of parent to the child if it does not have it
def propagate_parent_event(ids, parent_ids, event_handlers, serialized_file):
    for index, event in enumerate(event_handlers):
        if not event and parent_ids[index]:
            parent_id = parent_ids[index][0]
            if serialized_file != '/home/srwe/work/project/backstage/apks/menion.android.locus/appSerialized.json' \
                and parent_id != '0':
                parent_index = ids.index(parent_id)
                '''
                if event_handlers[parent_index]:
                    print(event_handlers[parent_index])
                    
                '''
                event_handlers[index] = event_handlers[parent_index]
    return event_handlers

# duplicated element if it has more than one event handler
def duplicate(event_handler, feature_lists):
    event_handler_updated = event_handler
    for idx, events in enumerate(event_handler):
        if not events:
            event_handler[idx] = None
        else:
            event_handler[idx] = events[0]
            if len(events) > 1:
                for event in events[1:]:
                    feature_lists = [feat.append(feat[idx]) for feat in feature_lists]
                    event_handler_updated.append(event)

    return event_handler_updated, feature_lists

# convert empty string to None type
def replace_empty_str(*feature_list):
    processed_feature_list = []
    for f_idx, feat in enumerate(feature_list):
        processed_feat = feat
        for index, f in enumerate(feat):
            assert not isinstance(f, list)
            processed_feat[index] = 'None' if f == '' or f is None else f
        processed_feature_list.append(processed_feat)

    return feature_list

# return back extracted data ( the features of all elements) from json file
def get_app_data(app_serialized_file):
    with open(app_serialized_file) as f:
        app_data = json.load(f)

    parent_IDs=[]
    child_IDs=[]
    text=[]
    ui_types=[]
    event_handler=[]
    ids=[]

    for ui_elem in app_data:
        ids.append(ui_elem['id']['text'])
        parent_IDs.append(ui_elem['parentIDs']['sub_feat'])
        child_IDs.append(ui_elem['childIDs']['sub_feat'])
        text.append(ui_elem['text']['text'])
        ui_types.append(ui_elem['kindOfUiElement']['text'])
        event_handler.append(ui_elem['listeners']['sub_feat'])

    # propagate parent events to child if not have any
    event_handler = propagate_parent_event(ids, parent_IDs, event_handler, app_serialized_file)
    # dereference ids
    parents_orig, grand_parents = dereference(ids, ui_types, parent_IDs, app_serialized_file)
    pp_unic = list(set(list(itertools.chain(*parents_orig))))
    children, grand_children = dereference(ids, ui_types, child_IDs, app_serialized_file)
    app_name = os.path.normpath(app_serialized_file).split(os.sep)[-2]
    app_name_list = [app_name] * len(ids)

    # verify that each element has one parent at most and remove nested list
    parents = []
    for pp in parents_orig:
        pp1 = list(filter(lambda a: a != 'include', pp))
        parent_str = None if not pp1 else pp1[0]
        parents.append(parent_str)
        if len(pp1) > 1:
            for idx in range(len(pp1)):
                assert pp[0] == pp[idx]
            parents[-1] = pp[0]

    ids = remove_duplicate_and_to_small(ids)
    parents = remove_duplicate_and_to_small(parents)
    children = remove_duplicate_and_to_small(children)
    text = prepare_text(text)

    refined_ui_types = refine_types(ui_types)

    event_handler = remove_duplicate_and_to_small(event_handler)
    app_name_list = remove_duplicate_and_to_small(app_name_list)

    child1 = [el[0] if len(el) > 0 else None for el in children]
    child2 = [el[1] if len(el) > 1 else None for el in children]

    feat_list = [ids, parents, child1, child2, text, refined_ui_types, app_name_list]
    event_handler, feat_list = duplicate(event_handler, feat_list)
    ids, parents, child1, child2, text, refined_ui_types, app_name_list = feat_list

    # to make sure there is no nested list and replace empty strings with None
    ids, parents, child1, child2, text, refined_ui_types, event_handler, app_name_list = replace_empty_str(
        ids, parents, child1, child2, text, refined_ui_types, event_handler, app_name_list
    )

    return ids, parents, child1, child2, text, refined_ui_types, event_handler, app_name_list

# procees all application to collect data
def get_all_apps_data():
    total_ids = []
    total_parent = []
    total_child1 = []
    total_child2 = []
    total_text = []
    total_ui_types = []
    total_event_handler = []
    total_app_name = []
    app_root_folder = '/home/srwe/work/project/backstage/apks'
    all_folders = os.listdir(app_root_folder)
    for cur_folder in all_folders:
        cur_folder_fp = os.path.join(app_root_folder, cur_folder)
        if os.path.isdir(cur_folder_fp):
            serialized_file = os.path.join(cur_folder_fp, APP_SERIALIZED_FILE_JSON)
            try:
                if os.path.exists(serialized_file) : # and serialized_file != '/home/srwe/work/project/backstage/apks/menion.android.locus/appSerialized.json':
                    ids, parents, child1, child2, text, refined_ui_types, event_handler, app_name_list = get_app_data(serialized_file)
                    total_ids += ids
                    total_parent += parents
                    total_child1 += child1
                    total_child2 += child2
                    total_text += text
                    total_ui_types += refined_ui_types
                    total_event_handler += event_handler
                    total_app_name += app_name_list

            except:
                print('Error processing {}'.format(cur_folder))
                raise

    return total_ids, total_parent, total_child1, total_child2, total_text, total_ui_types,total_event_handler,total_app_name

# create ARFF file from collected data
def data_to_arff(filename, **argvals):

    attributes= []
    data = []
    for key, val in six.iteritems(argvals):
        attributes.append((key, list(set(val))))
        data.append(val)
    data = map(list, zip(*data))

    xor_dataset = {
        'description': 'app Dataset',
        'relation': 'appFeature',
        'attributes': attributes,
        'data': data
    }
    with open(filename, 'w') as fp:
        arff.dump(xor_dataset, fp)
        fp.close()


if __name__ == "__main__":
    get_all_apps_data()
    ids, parents, child1, child2, text, refined_ui_types, event_handler, app_name_list = get_all_apps_data()
    fname = '/home/srwe/work/app.arff'
    data_to_arff(fname, ids=ids, parents=parents, child1=child1, child2=child2, text=text,
                 refined_ui_types=refined_ui_types,
                 event_handler=event_handler, app_name_list=app_name_list)
    #app_serialized = '/home/srwe/work/project/backstage/apks/mobi.infolife.ezweather.widget.figures/appSerialized.json'

    print('Done!')

'''

def load_arff(filename='/home/srwe/Downloads/widget_events_200.arff/widget_events_200.arff'):
    data = arff.load(open(filename, 'rb'))
    for att_name, att_type in data['attributes']:
        print('%s, ' % (att_name))
        if att_name in ['Type']:
            print((att_type))


def get_relative_element_ids(in_element):
    ids = []
    if in_element is not None:
        for tmp_el in in_element:
            ids.append(tmp_el['int']['text'])

    return ids
'''