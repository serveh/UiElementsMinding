

import json, bson
#from bson import json_util

file_name = '/home/srwe/work/project/backstage/apks/ru.tubin.bp_v1.43/appSerialized.json'
'''with open(file_name, "r") as read_file:
    data = json.load(read_file)

collection.insert(data)
'''

json_data=open(file_name).read()
data = bson.loads(json_data)
#data = json.loads(json_data)

with open('output.bson', 'w') as outfile:
    bson.dumps(data, outfile)
    #json_util.dump(data, outfile)


'''    
reading = (input_file.read()).encode() #reading = (input_file.read()+'\0').encode()
    datas = bson.BSON.decode(reading)
    json.dump(datas, output_file)



#dumps(file_name)   #, json_options=RELAXED_JSON_OPTIONS)
'''