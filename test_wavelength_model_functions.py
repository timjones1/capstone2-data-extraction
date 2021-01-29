import unittest
import spacy
from spacy.tokens import Token, Span, Doc
import numpy as np
import pandas as pd
from dateutil import parser
import wavefunctions as wf
import re
import random

nlp = spacy.load('en_core_web_sm')



def create_entity_tags(labels_list):
    entity_dict = {} 
    entity_dict["entities"] = tuple(labels_list)
    
    return entity_dict

TRAIN_IMPORT = pd.read_json("file.json1",orient="records",lines=True)
TRAIN_IMPORT['entities'] = TRAIN_IMPORT['labels'].apply(create_entity_tags)
TRAINING_DATA = []
BASE_DATE = "13th October 2019 "

for _, row in TRAIN_IMPORT[['text','entities']].iterrows():
    training_example = (row['text'], row['entities'])
    TRAINING_DATA.append(training_example)

ner = nlp.create_pipe("ner")

nlp.begin_training()

for itn in range(10):
    random.shuffle(TRAINING_DATA)
    for batch in spacy.util.minibatch(TRAINING_DATA, size=2):
        texts = [text for text,annotation in batch]
        annotations = [annotation for text, annotation in batch]
        nlp.update(texts, annotations)

class TestDays(unittest.TestCase):

    def test_get_days_per_week(self):
        test_list = [
            "None",
            "6.1 Your normal working hours are 08.45 to 17.45 with breaks, and a one hour lunch break 4 days a week.", 
            "6.1 Your normal working hours are 08.45 to 17.45 on three days a week with breaks and a one hour lunch.",
            "• The normal working hours are 8.45am to 5.3opm), Tuesday to Wednesday, with breaks, and a one hour lunch.",
            "• The normal working hours are 8.45am to 5.3opm), Monday to Friday, with breaks, and a one hour lunch.",
            "Your normal working hours are 08.45 to 17.45, Monday, Wednesday and Thursday with breaks, and a one hour lunch break. You work 08.45 to 12.45 or a half day equivalent on Friday",
            "Your normal working hours are 08.45 to 17.45 four days a week with breaks and a one hour lunch. You will work a half day on the fifth day of the week",
            "6.1 Your normal working hours are 15 hours each week, working on Monday, Tuesday, Wednesday, Thursday and Friday.",
            "Your normal working hours are 21 hours each week, working on Tuesday, Wednesday and Thursday. Your department is generally required to be staffed 08:00 - 18:00hrs, and specific working hours within this will be instructed by your line manager with a one hour lunch break",
        ]
        test_results = [None,4,3,2,5,3.5,4.5,5,3]
        
        for idx, test_string in enumerate(test_list):
            doc = nlp(test_string)
            self.assertEqual(wf.get_days_per_week_model(doc), test_results[idx], f"should return {test_results[idx]} from test string {idx} \n {test_list[idx]}")

if __name__ == '__main__':
    unittest.main()