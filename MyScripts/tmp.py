import json

with open('/home/srwe/work/project/backstage/apks/animaonline.android.wikiexplorer_v1.5.5/appSerialized.json') as jsonfile:
    parsed = json.load(jsonfile)
for i in parsed:
    if i['drawableNames']['sub_feat'] != None :
        print i['drawableNames']['sub_feat']
        print i['id']['text']
print json.dumps(parsed, indent=2, sort_keys=True)
