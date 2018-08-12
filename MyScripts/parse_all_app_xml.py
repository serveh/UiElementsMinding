import glob, os
import xmlParse
import json

APP_SERIALIZED_FILE = 'appSerialized.txt'

def main():
    app_root_folder = '/home/srwe/work/project/backstage/apks'
    skipped_folders = os.path.join(app_root_folder, 'skipped_folders.txt')
    log_skipped_folder = open(skipped_folders, 'w')
    all_folders = os.listdir(app_root_folder)
    for cur_folder in all_folders:
        cur_folder_fp = os.path.join(app_root_folder, cur_folder)
        if os.path.isdir(cur_folder_fp):
            serialized_file = os.path.join(cur_folder_fp, APP_SERIALIZED_FILE)
            if os.path.exists(serialized_file):
                try:
                    ui_element_list = xmlParse.parse_xml(serialized_file)
                except:
                    print('Error processing {}'.format(cur_folder))
                    raise
                with open(os.path.join(cur_folder_fp, APP_SERIALIZED_FILE[:-3] + 'json'), 'w') as fp:
                    json.dump(ui_element_list, fp)
                #print('{} DONE'.format(cur_folder))
            else:
                log_skipped_folder.write('{}  at {} \n'.format(cur_folder, cur_folder_fp))
                #print('The serialized file does not exist for this app {} '.format(cur_folder_fp))

    log_skipped_folder.close()


if __name__ == "__main__":
    main()