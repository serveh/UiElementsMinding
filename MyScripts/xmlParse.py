import six
import xml.etree.ElementTree as ET
import json


def print_child(child):
    tail = 'NEWLINE' if child.tail == '\n' else child.tail
    text = 'NONE' if not child.text else child.text
    if 'UIElement' in child.tag:
        found =True
    str = 'tag {}, text {}, tail {}, Attributes: '.format(child.tag, text, tail)
    str = str.replace('\n', 'NEWLINE')
    for key, val in six.iteritems(child.attrib):
        str += '{}:{} '.format(key, val)
    print(str)


ui_element_feature = ['parentIDs', 'childIDs', 'parentIDsDyn', 'childIDsDyn', 'idVar', 'id', 'textVar', 'text',
                      'kindOfUiElement', 'listeners', 'drawableNames', 'styles', 'logger']
UIELEMENTS_TAG = 'UIElement'
SUB_FEAT_TAG = 'sub_feat'
#ui_element_list = []
IDENTIFIER_TAG = 'kindOfUiElement'


def has_all_common_tags(element, verbose=False):
    _children_tags = [ch.tag for ch in element.getchildren()]
    for tt in ui_element_feature:
        if tt not in _children_tags:
            if verbose:
                print('Common UI element feature "{}" is missing. The tag list includes {}'.format(tt, _children_tags))
            return False
    return True


def traverse_children(children, ui_element_list, unknown_tag_list):
    if len(children) == 0:
        return None
    else:
        child_dict = {}
        for ch in children:
            if has_all_common_tags(ch): # UIELEMENTS_TAG in ch.tag:
                elem = ui_element_to_dic(ch, ui_element_list, unknown_tag_list)
                ui_element_list.append(elem)
                child_dict[ch.tag] = elem
            else:
                child_dict[ch.tag] =  {'text': ch.text, 'attributes': ch.attrib}
                child_dict[ch.tag][SUB_FEAT_TAG] = traverse_children(ch.getchildren(),
                                                                     ui_element_list, unknown_tag_list)
                if ch.tag not in unknown_tag_list:
                    unknown_tag_list.append(ch.tag)
        return child_dict


def ui_element_to_dic(element, ui_element_list, unknown_tag_list):
    ui_element = {}

    for child in element.getchildren():
        ui_element[child.tag] = {'text':child.text, 'attributes': child.attrib}
        if 'child' in child.tag or 'parent' in child.tag:
            ids = []
            child_list = child.getchildren()
            for idx in range(len(child_list)):
                ids.append(child_list[idx].text)
            ui_element[child.tag][SUB_FEAT_TAG] = ids
        elif 'listeners' in child.tag:
            listeners = []
            child_list = child.getchildren()
            for ch_tmp in child_list:
                actionWaitingFor = ch_tmp.find('actionWaitingFor').text
                if actionWaitingFor not in listeners:
                    listeners.append(actionWaitingFor)

            if len(listeners) > 1:
                print(listeners)
            ui_element[child.tag][SUB_FEAT_TAG] = listeners
        else:
            ui_element[child.tag][SUB_FEAT_TAG] = traverse_children(child.getchildren(), ui_element_list, unknown_tag_list)

    return ui_element


def parse_xml(file_name):
    tree = ET.parse(file_name)
    root = tree.getroot()
    ui_element_list = []
    unknown_tag_list = []
    for child in root.getchildren():
        traverse_children(child, ui_element_list, unknown_tag_list)

    return ui_element_list


def main():
    file_name = '/home/srwe/work/project/backstage/apks/mobi.infolife.ezweather.widget.figures/appSerialized.txt'
    # ''/home/srwe/work/project/backstage/apks/ru.tubin.bp_v1.43/appSerialized.txt'
    ui_element_list = parse_xml(file_name)
    '''
    tree = ET.parse('/home/srwe/work/project/backstage/apks/ru.tubin.bp_v1.43/appSerialized.txt')
    root = tree.getroot()
    for child in root.getchildren():       # .findall("uiElementOfApp")
        traverse_children(child)
    '''

    with open(file_name[:-4]+'.json', 'w') as fp:
        json.dump(ui_element_list, fp)
    print('DONE')


if __name__ == "__main__":
    main()
