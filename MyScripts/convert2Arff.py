import arff
import json, os
import itertools
import six
import copy

import standard_types as st_types
from distance import ilevenshtein
import unicodedata
from imageListParser import ImageListParser
from balance_data import balance_data as bd


APP_SERIALIZED_FILE_JSON = 'appSerialized.json'
AZURE_FILE_LEMMATIZE = 'lemmetizied_image_text.txt'

def refine_types(type_list):
    # Mapping UI elements types to list of standard type (define based on orginal Andriod types provided by Nataniel)
    # by computing string similarity distance, Levenshtein

    std_types = st_types.get_standard_type()
    std_types = [tt.lower() for tt in std_types]
    refined_types = [sorted(ilevenshtein(tt.lower(), std_types))[0][1] for tt in type_list]
    return refined_types

def remove_duplicate_and_to_small(feature_list):
    # Removing all duplicated items in given list and return a lowercase list

    for idx, features in enumerate(feature_list):
        if isinstance(features, list):
            feature_list[idx] = list(set([feature.lower() for feature in features]))
        elif isinstance(features, six.string_types):
            feature_list[idx] = features.lower()

    return feature_list


def prepare_text(text_feature):
    # return a stripped string by deleting blank space

    for idx, txt in enumerate(text_feature):
        if txt is None:
            txt= ''
        text_feature[idx] = txt.strip(' \t\n\r')
    text_feature = [el.lower() for el in text_feature]
    return text_feature


def dereference(ids, element_types, ref_ids, serialized_file):
    # return type value of element instead of index value for parents and children

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


def propagate_parent_event(ids, parent_ids, event_handlers, serialized_file):
    # passes the event of parent to the child if it does not have it

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


def duplicate(event_handler, feature_lists):
    # duplicated element if it has more than one event handler

    event_handler_updated = copy.deepcopy(event_handler)
    for idx, events in enumerate(event_handler):
        if not events:
            event_handler_updated[idx] = 'None'
        else:
            assert isinstance(events, list)
            event_handler_updated[idx] = events[0]
            if len(events) > 1:
                for event in events[1:]:
                    feature_lists = [feat + [feat[idx]] for feat in feature_lists]
                    event_handler_updated.append(event)

    return event_handler_updated, feature_lists


def replace_empty_str(*feature_list):
    # convert empty string to None type

    processed_feature_list = []
    for f_idx, feat in enumerate(feature_list):
        processed_feat = feat
        for index, f in enumerate(feat):
            assert not isinstance(f, list)
            if f == '' or f is None:
              processed_feat[index] = 'None'
            else:
                if type(f) == type('str'):
                    correct_unicode_string = f
                else:
                    correct_unicode_string = unicodedata.normalize('NFKD', f).encode('ascii', 'ignore')

                #correct_unicode_string = unidecode(unicode(f, encoding="utf-8"))
                #unicode_string = f.decode('latin1')
                #correct_unicode_string = unicode_string.encode('latin1').decode('utf8')
                processed_feat[index] = correct_unicode_string

        processed_feature_list.append(processed_feat)

    return feature_list


def split_string(str, separator=',', max_element=3):
    elements = ['empty'] * max_element

    sub_str = str.rstrip().split(separator)
    for idx in range(min(max_element, len(sub_str))):
        elements[idx] = sub_str[idx]

    return elements


def get_azure_text(filename, drawable_name):
    emp = 'empty'
    azure_lemm_fname = filename.replace('appSerialized.json', 'lemmetizied_image_text.txt')
    ilp = ImageListParser()
    is_loaded = ilp.load(azure_lemm_fname)
    assert is_loaded

    cap1, cap2, cap3 = [], [], []
    tag1 = []; tag2 = []; tag3 = []; tag4 = []; tag5 = []
    name1 = []; name2 = []; name3 = []

    for img in drawable_name:
        if img != 'empty' and img in ilp.image_list:
            cap, tags, name = ilp.get_caption_tag_name(img)
            c1, c2, c3 = split_string(cap)
            t1, t2, t3, t4, t5 = split_string(tags, max_element=5)
            n1, n2, n3 = split_string(name)
            cap1.append(c1), cap2.append(c2), cap3.append(c3)
            tag1.append(t1), tag2.append(t2), tag3.append(t3), tag4.append(t4), tag5.append(t5)
            name1.append(n1), name2.append(n2), name3.append(n3)
        else:
            cap1.append(emp), cap2.append(emp), cap3.append(emp)
            tag1.append(emp), tag2.append(emp), tag3.append(emp), tag4.append(emp), tag5.append(emp)
            name1.append(emp), name2.append(emp), name3.append(emp)

    return cap1, cap2, cap3, tag1, tag2, tag3, tag4, tag5, name1, name2, name3


def get_app_data(app_serialized_file):
    # return back extracted data ( the features of all elements) from json file

    with open(app_serialized_file) as f:
        app_data = json.load(f)

    parent_IDs=[]
    child_IDs=[]
    text=[]
    ui_types=[]
    event_handler=[]
    ids=[]
    drawable_name = []
    has_event = []
    txt_azure = []

    for ui_elem in app_data:
        ids.append(ui_elem['id']['text'])
        parent_IDs.append(ui_elem['parentIDs']['sub_feat'])
        child_IDs.append(ui_elem['childIDs']['sub_feat'])
        text.append(ui_elem['text']['text'])
        ui_types.append(ui_elem['kindOfUiElement']['text'])
        event_handler.append(ui_elem['listeners']['sub_feat'])
        try:
            drawable_name.append(ui_elem['drawableNames']['sub_feat']['string']['text'])
            #print(ui_elem['drawableNames']['sub_feat']['string']['text'])
        except:
            drawable_name.append('empty')

    # propagate parent events to child if not have any
    cap1, cap2, cap3, tag1, tag2 , tag3, tag4, tag5, name1, name2, name3 = get_azure_text(app_serialized_file, drawable_name)
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

    feat_list = [ids, parents, child1, child2, text, ui_types, refined_ui_types, app_name_list,
                 cap1, cap2, cap3, tag1, tag2 , tag3, tag4, tag5, name1, name2, name3]
    event_handler, feat_list = duplicate(event_handler, feat_list)
    ids, parents, child1, child2, text, ui_types, refined_ui_types, app_name_list,\
    cap1, cap2, cap3, tag1, tag2 , tag3, tag4, tag5, name1, name2, name3 = feat_list

    # to make sure there is no nested list and replace empty strings with None
    ids, parents, child1, child2, text, ui_types, refined_ui_types, event_handler, app_name_list = replace_empty_str(
        ids, parents, child1, child2, text, ui_types, refined_ui_types, event_handler, app_name_list)

    # check that UI element has event handler
    has_event = [ 'False' if el == 'None' else 'True' for el in event_handler]

    return ids, parents, child1, child2, text, ui_types, refined_ui_types, event_handler, has_event, app_name_list, \
           cap1, cap2, cap3, tag1, tag2 ,tag3, tag4, tag5, name1, name2, name3


def get_all_apps_data():
    # procees all application to collect data

    total_ids = []
    total_parent = []
    total_child1 = []
    total_child2 = []
    total_text = []
    total_refined_types = []
    total_event_handler = []
    total_app_name = []
    total_type = []
    total_has_event = []
    total_cap1 = []
    total_cap2 = []
    total_cap3 = []
    total_tag1 = []
    total_tag2 = []
    total_tag3 = []
    total_tag4 = []
    total_tag5 = []
    total_name1 = []
    total_name2 = []
    total_name3 = []


    app_root_folder = '/home/srwe/work/project/backstage/apks'
    all_folders = os.listdir(app_root_folder)
    for cur_folder in all_folders:
        cur_folder_fp = os.path.join(app_root_folder, cur_folder)
        if os.path.isdir(cur_folder_fp):
            print(cur_folder_fp)
            serialized_file = os.path.join(cur_folder_fp, APP_SERIALIZED_FILE_JSON)
            try:
                if os.path.exists(serialized_file) : # and serialized_file != '/home/srwe/work/project/backstage/apks/menion.android.locus/appSerialized.json':
                    ids, parents, child1, child2, text, ui_type, refined_ui_types, event_handler, has_event, app_name_list, \
                    cap1, cap2, cap3, tag1, tag2 ,tag3, tag4, tag5, name1, name2, name3 = get_app_data(serialized_file)
                    total_ids += ids
                    total_parent += parents
                    total_child1 += child1
                    total_child2 += child2
                    total_text += text
                    total_refined_types += refined_ui_types
                    total_event_handler += event_handler
                    total_app_name += app_name_list
                    total_type += ui_type
                    total_has_event += has_event
                    total_cap1 += cap1
                    total_cap2 += cap2
                    total_cap3 += cap3
                    total_tag1 += tag1
                    total_tag2 += tag2
                    total_tag3 += tag3
                    total_tag4 += tag4
                    total_tag5 += tag5
                    total_name1 += name1
                    total_name2 += name2
                    total_name3 += name3

            except:
                print('Error processing {}'.format(cur_folder))
                raise

    return total_ids, total_parent, total_child1, total_child2, total_text, total_type, total_refined_types, \
           total_event_handler, total_has_event, total_app_name, total_cap1, total_cap2, total_cap3, total_tag1, \
           total_tag2, total_tag3, total_tag4, total_tag5, total_name1, total_name2, total_name3


def data_to_arff(filename, **argvals):
    # create ARFF file from collected data

    attributes = []
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


def main(balance_data):
    #tmp = '/home/srwe/work/project/backstage/apks/air.com.demute.TaoMix_v1.1.13/appSerialized.json'
    #ids, parents, child1, child2, text, ui_type, refined_types, event_handler, has_event, app_name_list, cap1, cap2, cap3, tag1, tag2 ,tag3, tag4, tag5, name1, name2, name3 = get_app_data(tmp)

    ids, parents, child1, child2, text, ui_type, refined_types, event_handler, has_event, app_name_list, cap1, cap2, cap3, tag1, tag2 ,tag3, tag4, tag5, name1, name2, name3 = get_all_apps_data()

    if balance_data:
        has_event, ids, parents, child1, child2, text, ui_type, refined_types, event_handler, app_name_list, cap1, cap2, cap3, tag1, tag2, tag3, tag4, tag5, name1, name2, name3 = \
            bd(has_event, ids, parents, child1, child2, text, ui_type, refined_types, event_handler, app_name_list, cap1, cap2, cap3, tag1, tag2 ,tag3, tag4, tag5, name1, name2, name3)

    if balance_data:
        fname = '/home/srwe/work/allApp_balanced.arff'
    else:
        fname = '/home/srwe/work/allApp.arff'

    data_to_arff(fname, Text=text, Type=ui_type, RefinedType=refined_types, Parent=parents,
                 Child1=child1, Child2=child2, HasEvent=has_event, Listener=event_handler, AppName=app_name_list,
                 Cap1=cap1, Cap2=cap2, Cap3=cap3, Tag1=tag1, Tag2=tag2, Tag3=tag3, Tag4=tag4, Tag5=tag5, Name1=name1,
                 Name2=name2, Name3=name3)

    print('Done!')


if __name__ == "__main__":
    balance_data = False
    main(balance_data)




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