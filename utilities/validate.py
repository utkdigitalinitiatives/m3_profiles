from jsonschema import validate
import json
import yaml
import os


class AdditionalChecks:
    def __init__(self, m3):
        self.path = m3
        self.m3 = yaml.safe_load(open(m3))
        self.unique_classes = self.find_unique_classes()
        self.all_exceptions = []
        self.validate_available_on()
        self.raise_exceptions()

    def find_unique_classes(self):
        return [work_type for work_type in self.m3['classes']]

    def validate_available_on(self):
        for property in self.m3['properties']:
            for work_type in self.m3['properties'][property]['available_on']['class']:
                if work_type not in self.unique_classes:
                    self.all_exceptions.append(f'Unknown worktype {work_type} in {property} in {self.path}.')

    def raise_exceptions(self):
        separator = '\n'
        if len(self.all_exceptions) > 0:
            raise Exception(f'{self.path} not valid. Has at least {len(self.all_exceptions)} errors including:\n\n{separator.join(self.all_exceptions)}')
        else:
            pass


schema = json.load(open('schemas/flex_schema.json'))
for path, directories, files in os.walk('maps'):
    for file in files:
        current_map = yaml.safe_load(open(f'maps/{file}'))
        validate(current_map, schema=schema)
        check = AdditionalChecks(f'maps/{file}')
