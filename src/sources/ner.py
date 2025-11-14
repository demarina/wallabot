import copy
import json
import os
import random
import re


class Ner:
    ENTITIES_FILE_NAME = 'entities.json'
    NER_PHRASES_FILE_NAME = 'ner_phrases.json'
    ANNOTATIONS_FILE_NAME = 'annotations.json'

    REGEX_PATTERN = r'\[ent\.[^\]]+\]'

    def __init__(self):
        pass

    def annotated_data(self):
        entities_file = os.path.join(os.path.dirname(__file__), '..', 'data', self.ENTITIES_FILE_NAME)
        if os.path.exists(entities_file):
            entities = json.load(open(entities_file))
        else:
            print(f'Entities file {entities_file} not found.')
            raise

        ner_phrases_file = os.path.join(os.path.dirname(__file__), '..', 'data', self.NER_PHRASES_FILE_NAME)
        if os.path.exists(ner_phrases_file):
            phrases = json.load(open(ner_phrases_file))
        else:
            print(f'Ner phrases file {ner_phrases_file} not found.')
            raise

        annotated_data = []
        for phrase in phrases:
            entities_info = []
            new_phrase = phrase
            matches = re.finditer(self.REGEX_PATTERN, phrase)
            for m in matches:
                e_type = m.group(0)
                start = int(m.start(0))
                end = int(m.end(0))

                e_type_key = e_type.replace('[', '').replace(']', '')
                entity_value = random.choice(entities[e_type_key])

                entities_info.append([start, end, entity_value])
                new_phrase = new_phrase.replace(e_type, entity_value, 1)

            annotated_data.append(
                {
                    'text': new_phrase,
                    'entities': entities_info
                }
            )

        annotated_data_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', self.ANNOTATIONS_FILE_NAME)
        with open(annotated_data_file_path, 'w') as f:
            f.write(json.dumps(annotated_data, indent=4))

        print(f'File {annotated_data_file_path} created.')


Ner().annotated_data()
