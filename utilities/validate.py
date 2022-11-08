from jsonschema import validate
import json
import yaml
import os


schema = json.load(open('schemas/schema.json'))
for path, directories, files in os.walk('maps'):
    for file in files:
        current_map = yaml.safe_load(open(f'maps/{file}'))
        validate(current_map, schema=schema)
