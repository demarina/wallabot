import copy
import json
import os
import random
import re


class Ner:
    ENT_MODEL = 'ent.model'
    ENT_MODELS = 'ent.models'
    ENT_BRAND = 'ent.brand'
    ENTITIES_FILE_NAME = 'entities.json'
    NER_PHRASES_FILE_NAME = 'ner_phrases.json'
    TRAINING_SET_FILE_NAME = 'training_set.json'

    REGEX_PATTERN = r'\[ent\.[^\]]+\]'

    def __init__(self):
        pass

    def annotated_data(self):
        entities_file = os.path.join(os.path.dirname(__file__), '..', 'data', self.ENTITIES_FILE_NAME)
        if os.path.exists(entities_file):
            entities = json.load(open(entities_file))
        else:
            print(f'Entities file "{entities_file}" not found.')
            raise

        ner_phrases_file = os.path.join(os.path.dirname(__file__), '..', 'data', self.NER_PHRASES_FILE_NAME)
        if os.path.exists(ner_phrases_file):
            phrases = json.load(open(ner_phrases_file))
        else:
            print(f'Ner phrases file "{ner_phrases_file}" not found.')
            raise

        annotated_data = []
        for phrase in phrases:
            entities_info = []
            new_phrase = phrase
            matches = re.finditer(self.REGEX_PATTERN, phrase)

            e_brand_value = None

            for m in matches:
                e_type = m.group(0)
                start = new_phrase.find(e_type)

                e_type_key = e_type.replace('[', '').replace(']', '')

                if e_type_key == self.ENT_BRAND:
                    entity_value = random.choice(entities[e_type_key])
                    e_brand_value = entity_value
                else:
                    if e_brand_value is not None and e_type_key == self.ENT_MODEL:
                        entity_value = random.choice(entities[self.ENT_MODELS].get(e_brand_value, entities[e_type_key]))
                    else:
                        entity_value = random.choice(entities[e_type_key])

                entities_info.append([start, (start + len(entity_value)), entity_value])
                new_phrase = new_phrase.replace(e_type, entity_value, 1)

            annotated_data.append(
                {
                    'text': new_phrase,
                    'entities': entities_info
                }
            )

        annotated_data_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', self.TRAINING_SET_FILE_NAME)
        with open(annotated_data_file_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(annotated_data, indent=4, ensure_ascii=False))

        print(f'File "{annotated_data_file_path}" created.')


Ner().annotated_data()
