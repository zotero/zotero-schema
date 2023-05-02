import os
import shutil
import gzip
import json
from pathlib import Path
import copy 

parent_folder =  Path(__file__).resolve().parent.parent
gzipped_file = f'{parent_folder}/schema.json.gz'
schema_file = f'{parent_folder}/schema.json'
locales_folder = f'{parent_folder}/locales'

with open(schema_file, 'r') as f:
    schema_text = f.read()
    schema = json.loads(schema_text)

if os.path.exists(locales_folder):
    shutil.rmtree(locales_folder)

os.mkdir(locales_folder)

# String that accumulates the rules to paste into htaccess
htaccess_rules = f"RewriteRule ^schema/({'|'.join(schema['locales'].keys())})$ /zotero-schema/locales/$1.gz [L]"
#Dict to collect country codes with locales to handle multiple locales per country code
htaccess_mapings = {}

# For each item in the 'locales' list of the schema
for locale_name in schema['locales'].keys():
    schema_with_one_locale = copy.deepcopy(schema)
    current_locale = schema_with_one_locale['locales'][locale_name]

    schema_with_one_locale['locales'] = {locale_name : current_locale}

    # Rule to match by country
    if locale_name[:2] in htaccess_mapings:
        htaccess_mapings[locale_name[:2]].append(locale_name)
    else:
        htaccess_mapings[locale_name[:2]] = [locale_name]
  
    # generate a gzip file and save it to the locales subdirectory
    with gzip.open(f'{locales_folder}/{locale_name}.json.gz', 'wb') as f_out:
        json_bytes = json.dumps(schema_with_one_locale, ensure_ascii=False).encode('utf8')
        f_out.write(json_bytes)


def locale_sort_key(a):
    # Prefer en-US
    if a == 'en-US':
        return 'A'
    # Prefer canonical locales
    if a[:2] == a[3:5].lower():
        return 'A'
    return a[3:5]

# For every country code, sort locale candidates and add rule to htacecss
for country_code in htaccess_mapings.keys():
    htaccess_mapings[country_code].sort(key=locale_sort_key)
    htaccess_rules += f'\nRewriteRule ^schema/{country_code} /zotero-schema/locales/{htaccess_mapings[country_code][0]}.gz [L]'  

# Catch all for default schema with all locales
htaccess_rules += f'\nRewriteRule ^schema/* /zotero-schema/schema.json.gz [L]' 

print("--- .htacess rules --- \n" + htaccess_rules + "\n---  ---")


# Create gzip for the main schema
with open(schema_file, 'rb') as f_in, gzip.open(gzipped_file, 'wb') as f_out:
    shutil.copyfileobj(f_in, f_out)
