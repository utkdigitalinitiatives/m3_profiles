import csv
from yaml import dump
import arrow


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
            "m3_version": "1.0.beta1",
            "profile": {
                "responsibility": "https://www.lib.utk.edu",
                "responsibility_statement": "University of Tennessee Libraries",
                "date_modified": str(arrow.utcnow().format("YYYY-MM-DD")),
                "type": "base",
                "version": 0.1
            },
            "contexts": {
                "flexible_context": {
                    "display_label": "Flexible Metadata Example"
                }
            },
            "mappings": {
                "blacklight": {
                    "name": "Additional Blacklight Solr Mappings"
                },
                "metatags": {
                    "name": "Metatags"
                },
                "simple_dc_pmh": {
                    "name": "Simple DC OAI PMH"
                },
                "qualified_dc_pmh": {
                    "name": "Qualified DC OAI PMH"
                },
                "mods_oai_pmh": {
                    "name": "MODS OAI PMH"
                },
            },
            "classes": {
                "GenericWork": {
                    "display_label": "Generic Work"
                },
                "Image": {
                    "display_label": "Image"
                },
                "Video": {
                    "display_label": "Video"
                },
                "Audio": {
                    "display_label": "Audio"
                },
                "Pdf": {
                    "display_label": "PDF"
                },
                "Book": {
                    "display_label": "Book"
                },
                "CompoundObject": {
                    "display_label": "Compound Object"
                },
                "Newspaper": {
                    "display_label": "Newspaper"
                },
            },
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
        sample_values = value.split('|')
        return [value.strip() for value in sample_values if value != '']

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

    @staticmethod
    def __get_classes(data):
        types = ("GenericWork", "Image", "Video", "Collection", "Audio", "PDF", "Book", "CompoundObject", "Newspaper")
        available_on = []
        for value in data.split(','):
            if value == "All":
                for work_type in types:
                    available_on.append(work_type)
            else:
                available_on.append(value.strip())
        return {'class': available_on}

    @staticmethod
    def __get_controlled_values(data, range):
        controlled_values = []
        for value in data.split(','):
            if value.lower() == "n/a" or value.lower().strip() == "none":
                controlled_values.append('null')
            else:
                controlled_values.append(value.strip())
        return {
            "format": range.strip(),
            "sources": controlled_values
        }

    @staticmethod
    def __get_solr_specific_things(solr_fields, facets):
        values = []
        for value in solr_fields.split(','):
            if value != "":
                values.append(value.strip())
        for value in facets.split(','):
            if value != "":
                values.append(value.strip())
        return values

    @staticmethod
    def __get_indexing(data):
        return [field.strip() for field in data.split(',')]

    def __build(self, data):
        final_property = {
            'display_label': self.__return_default(data['Display Label']),
            'requirement': self.__determine_required(data['Required for Migration']),
            'controlled_values': self.__get_controlled_values(data['Vocab'], data['M3: Range']),
            'property_uri': data['RDF Property / Predicate'].strip(),
            'available_on': self.__get_classes(data['Work Type']),
            'cardinality': self.__get_cardinality(data['Obligation: Repeatable / Range']),
            'mappings': PropertyMapping(data).build(),
            'indexing': self.__get_indexing(data['indexing'])
        }
        sample_values = self.__get_sample_values(data['Example'])
        if len(sample_values) > 0:
            final_property['sample_values'] = sample_values
        if data['Definition'] != "":
            final_property['definition'] = self.__return_default(data['Definition'])
        if data['Usage Guidelines'] != "":
            final_property['usage_guidelines'] = self.__return_default(data['Usage Guidelines'])
        if data['M3: Range'] != '':
            final_property['range'] = data['M3: Range']
        if data['M3: Syntax'] != '':
            final_property['syntax'] = data['M3: Syntax']
        if data['M3: Validations'] != '':
            final_property['validations'] = {"match_regex": data['M3: Validations']}
        if data['index_documentation'] != '':
            final_property['index_documentation'] = data['index_documentation']
        return final_property


class PropertyMapping:
    def __init__(self, data):
        self.data = data

    def __get_blacklight(self):
        return self.data['Additional Blacklight / Solr Field Expecations']

    def __get_simple_oai_pmh(self):
        return self.data['OAI_PMH Simple DC']

    def __get_qualified_oai_pmh(self):
        return self.data['OAI_PMH Qualified DC']

    def __get_oai_pmh_mods(self):
        return self.data['OAI_PMH MODS']

    def __get_metatags(self):
        return self.data['Metatags']

    def build(self):
        mappings = {}
        if self.__get_blacklight() != '':
            mappings['blacklight'] = self.__get_blacklight()
        if self.__get_oai_pmh_mods().lower() != 'n/a' and self.__get_oai_pmh_mods() != '':
            mappings['mods_oai_pmh'] = self.__get_oai_pmh_mods()
        if self.__get_simple_oai_pmh().lower() != 'n/a' and self.__get_simple_oai_pmh() != '':
            mappings['simple_dc_pmh'] = self.__get_simple_oai_pmh()
        if self.__get_qualified_oai_pmh().lower() != 'n/a' and self.__get_qualified_oai_pmh() != '':
            mappings['qualified_dc_pmh'] = self.__get_qualified_oai_pmh()
        if self.__get_metatags().lower() != 'n/a' and self.__get_metatags() != '':
            mappings['metatags'] = self.__get_metatags()
        return mappings


if __name__ == "__main__":
    MetadataCSV('csvs/testing_indexing2.csv').dump_yaml('maps/utk_test_files.yml')
