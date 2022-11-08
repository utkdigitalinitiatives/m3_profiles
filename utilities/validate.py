from jsonschema import validate
import json
import yaml


schema = json.load(open('schemas/schema.json'))
test = yaml.safe_load(open('maps/utk.yml'))
validate(test, schema=schema)

