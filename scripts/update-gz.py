import os
import shutil
import gzip
import json
import sys
from pathlib import Path
import copy 

parent_folder =  Path(__file__).resolve().parent.parent
gzipped_file = f'{parent_folder}/schema.json.gz'
schema_file = f'{parent_folder}/schema.json'

with open(schema_file, 'r') as f:
    schema_text = f.read()
    schema = json.loads(schema_text)

if not os.path.exists('../locales'):
    os.mkdir('../locales')

# For each item in the 'locales' list of the schema
for locale_name in schema['locales'].keys():
    locale_file_name = f"{locale_name}.json.gz"
    schema_with_one_locale = copy.deepcopy(schema)
    current_locale = schema_with_one_locale['locales'][locale_name]

    # If --sub argument is passed, substitute field names for ones from the corresponding locale
    if len(sys.argv) == 2 and sys.argv[1] == '--sub':
        for item_type in schema_with_one_locale['itemTypes']:
            if item_type['itemType'] in current_locale["itemTypes"]:
                item_type['itemType'] = current_locale["itemTypes"][item_type['itemType']]
            for field in item_type['fields']:
                if field['field'] in current_locale["itemTypes"]:
                    field['field'] = current_locale["itemTypes"][field['field']]
            for creator_type in item_type['creatorTypes']:
                if creator_type['creatorType'] in current_locale["itemTypes"]:
                    creator_type['creatorType'] = current_locale["itemTypes"][creator_type['creatorType']]
        del schema_with_one_locale['locales']
        
    else:
        # otherwise, just keep the relevant locale in the same schema
        schema_with_one_locale['locales'] = {locale_name : current_locale}
        
    # generate a gzip file and save it to the locales subdirectory
    with gzip.open('../locales/' + locale_file_name, 'wb') as f_out:
        json_bytes = json.dumps(schema_with_one_locale, ensure_ascii=False).encode('utf8')
        f_out.write(json_bytes)


# Check if the gzip file exists, create it if not
if not os.path.exists(gzipped_file):
    with open(schema_file, 'rb') as f_in, gzip.open(gzipped_file, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

with gzip.open(gzipped_file, mode='r') as f:
    gzip_schema = f.read()

# # Compare the json of gzip file with the current schema json
if json.dumps(json.loads(gzip_schema)) != json.dumps(json.loads(schema_text)):
    print(f'{gzipped_file} updated')
else:
    print('Schema hasn\'t changed')
