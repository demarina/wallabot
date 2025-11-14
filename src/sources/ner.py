import json
import os
import random
import re
from typing import List, Dict

import spacy
from spacy.training import Example


class Ner:
    ENT_MODEL = 'ent.model'
    ENT_MODELS = 'ent.models'
    ENT_BRAND = 'ent.brand'
    ENTITIES_FILE_NAME = 'entities.json'
    NER_PHRASES_FILE_NAME = 'ner_phrases.json'
    TRAINING_SET_FILE_NAME = 'training_set.json'

    MODEL_SPACY = 'es_core_news_sm'
    WALLABOT_MODEL_NAME = 'wallabot_model'

    REGEX_PATTERN = r'\[ent\.[^\]]+\]'

    def __init__(self):
        pass

    def generate_training_data(self) -> None:
        print('Start generating dataset...')
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
        for i in range(5):
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
                            entity_value = random.choice(
                                entities[self.ENT_MODELS].get(e_brand_value, entities[e_type_key]))
                        else:
                            entity_value = random.choice(entities[e_type_key])

                    entities_info.append([start, (start + len(entity_value)), e_type_key])
                    new_phrase = new_phrase.replace(e_type, entity_value, 1)

                annotated_data.append(
                    {
                        'text': new_phrase.lower(),
                        'entities': entities_info
                    }
                )

        training_data_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', self.TRAINING_SET_FILE_NAME)
        with open(training_data_file_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(annotated_data, indent=4, ensure_ascii=False))

        print(f'File "{training_data_file_path}" created.')

    def train(self) -> None:
        print('Start training...')

        training_data_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', self.TRAINING_SET_FILE_NAME)
        if not os.path.exists(training_data_file_path):
            print(f'File "{training_data_file_path}" not found.')
            raise

        with open(training_data_file_path, 'r') as f:
            training_data = json.load(f)

        nlp = spacy.blank('es')
        nlp.add_pipe('lemmatizer', config={'mode': 'rule'})

        ner = nlp.add_pipe('ner')

        for item in training_data:
            for ent in item['entities']:
                ner.add_label(ent[2])

        n_iter = 30
        optimizer = nlp.initialize()

        for _ in range(n_iter):
            random.shuffle(training_data)
            losses = {}

            for entry in training_data:
                text = entry['text']
                ents = entry['entities']
                doc = nlp.make_doc(text)

                example = Example.from_dict(doc, {'entities': ents})

                nlp.update([example], losses=losses, drop=0.2, sgd=optimizer)

        nlp.to_disk(self.WALLABOT_MODEL_NAME)
        print(f'Finish training. Model save in {self.WALLABOT_MODEL_NAME}.')

    def predict(self, query: str) -> List[Dict]:
        nlp_model = spacy.load(self.WALLABOT_MODEL_NAME)
        predict = nlp_model(query.lower())
        result = []
        for ent in predict.ents:
            result.append({
                'e_type': ent.label_,
                'e_value': ent.text
            })

        return result
