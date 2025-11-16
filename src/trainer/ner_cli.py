import argparse
from enum import Enum

from ner import Ner


class TasksEnum(str, Enum):
    GENERATE = 'generate'
    TRAIN = 'train'
    PREDICT = 'predict'


parser = argparse.ArgumentParser(description='NER client')

parser.add_argument('--task', type=str, required=True, help='generate, train or predict')
parser.add_argument('--data-folder-path', dest='data_folder_path', type=str, required=False,
                    help='data folder path')
parser.add_argument('--nlp-model-path', dest='nlp_model_path', type=str, required=False,
                    help='NLP model path')

args = parser.parse_args()

if args.task == TasksEnum.GENERATE:
    Ner().generate_training_data(data_folder_path=args.data_folder_path)
elif args.task == TasksEnum.TRAIN:
    Ner().train(data_folder_path=args.data_folder_path, nlp_model_path=args.nlp_model_path)
elif args.task == TasksEnum.PREDICT:
    ner_obj = Ner(nlp_model_path=args.nlp_model_path)
    while True:
        q = input('Insert query: ')
        result = ner_obj.predict(query=q)
        for e in result:
            print(e)
