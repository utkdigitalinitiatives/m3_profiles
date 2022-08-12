import csv
from yaml import dump


class MetadataCSV:
    def __init__(self, path_to_csv):
        self.original_csv = path_to_csv
        self.original_as_dict = self.__read(path_to_csv)
        self.headers = self.__get_headers()

    @staticmethod
    def __read(path_to_file):
        csv_content = []
        with open(path_to_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                csv_content.append(row)
        return csv_content

    def __get_headers(self):
        original_headers = [k for k, v in self.original_as_dict[0].items()]
        return original_headers

    def dump_yaml(self, path="maps/test.yml"):
        test = {
            "properties": {}
        }
        for rdf_property in self.original_as_dict:
            new_property = RDFProperty(rdf_property)
            test['properties'][new_property.name] = new_property.property
        with open(path, 'w') as new_map:
            dump(test, new_map)


class RDFProperty:
    def __init__(self, data):
        self.name = data['Property Name']
        self.property = self.__build(data)

    @staticmethod
    def __return_default(field):
        return {'default': field}

    @staticmethod
    def __determine_required(value):
        if 'N' in value:
            return 'optional'
        else:
            return 'required'

    @staticmethod
    def __get_sample_values(value):
        all_values = value.split('|')

    @staticmethod
    def __get_cardinality(value):
        cardinality = {
        }
        values = value.split('-')
        if len(values) == 1:
            cardinality['minimum'] = 1
            cardinality['maximum'] = 1
        elif values[1] == 'n':
            cardinality['minimum'] = int(values[0])
        else:
            cardinality['minimum'] = int(values[0])
            cardinality['maximum'] = int(values[1])
        return cardinality

    def __build(self, data):
        return {
            'display_label': self.__return_default(data['Display Label']),
            'definition': self.__return_default(data['Description / Usage Guildeline']),
            'usage_guidelines': self.__return_default(data['Description / Usage Guildeline']),
            'requirement': self.__determine_required(data['Required for Migration']),
            'property_uri': data['RDF Property / Predicate'],
            'cardinality': self.__get_cardinality(data['Obligation: Repeatable / Range']),
            'available_on': { 'class': ["Image"]}
        }


if __name__ == "__main__":
    MetadataCSV('csvs/vendor_supplied_map.csv').dump_yaml()
