import argparse
from enum import Enum

from src.sources.ner import Ner


class TasksEnum(str, Enum):
    GENERATE = 'generate'
    TRAIN = 'train'
    PREDICT = 'predict'


parser = argparse.ArgumentParser(description='NER client')

parser.add_argument('--task', type=str, required=True, help='generate, train or predict')

args = parser.parse_args()

if args.task == TasksEnum.GENERATE:
    Ner().generate_training_data()
elif args.task == TasksEnum.TRAIN:
    Ner().train()
elif args.task == TasksEnum.PREDICT:
    while True:
        q = input('Insert query: ')
        result = Ner().predict(query=q)
        for e in result:
            print(e)
