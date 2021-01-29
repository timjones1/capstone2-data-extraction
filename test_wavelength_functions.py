import unittest

import spacy
from spacy.matcher import Matcher
from spacy.pipeline import EntityRuler
from spacy.tokens import Token, Span, Doc
from openpyxl import load_workbook
import numpy as np
import pandas as pd
from dateutil import parser
import wavefunctions as wf

nlp = spacy.load('en_core_web_sm')

patterns = [{"label" : "TIMES", 
             "pattern" : [{"LOWER" : {"IN" : ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]}, 
                           "OP" : "?"},
                          {"IS_PUNCT" : True, "OP" : "?"},            
                          {"SHAPE" : {"IN" :["dddd","ddd","d:dd","d:ddxx","dd:dx","dd:dd","dd:ddxx",
                                             "dd:ddxxx","d.dd","d.ddxx","dd.dx","dd.dd","dd.ddxx",
                                             "dd.ddxxx"]}},
                          {"LOWER" : {"IN" : ["to", "-"]}},
                          {"SHAPE" : {"IN" :["dddd,""ddd", "d:dd","d:ddxx","dd:dx","dd:dd","dd:ddxx",
                                             "dd:ddxxx","d.dd","d.ddxx","dd.dx","dd.dd","dd.ddxx",
                                             "dd.ddxxx"]}}]},
            {"label" : "DATE", 
             "pattern" : [{"LOWER" : {"IN" : ["monday", "tuesday", "wednesday","thursday","friday",
                                              "saturday","sunday"]}},
                          {"LOWER" : {"IN" : ["to", "-"]}},
                          {"LOWER" : {"IN" : ["monday", "tuesday", "wednesday","thursday","friday",
                                              "saturday","sunday"]}}],
             "id" : "days_range"},
            {"label" : "DATE",
             "pattern" : [{"LIKE_NUM" : True},
                          {"LOWER" : {"IN" : ["hour","hours"]}},
                          {"IS_ALPHA" : True, "OP" : "?"},
                          {"LOWER" : "lunch"}],
             "id" : "lunch_break"},
            {"label" : "DATE",
             "pattern" : [{"LIKE_NUM" : True},
                          {"LOWER" : {"IN" : ["day","days"]}}],
             "id" : "days_worked"}
           ]

ruler = EntityRuler(nlp)
ruler.add_patterns(patterns)
nlp.add_pipe(ruler,before='ner')


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
            self.assertEqual(wf.get_days_per_week_new(doc), test_results[idx], f"should return {test_results[idx]} from test string {idx} \n {test_list[idx]}")

if __name__ == '__main__':
    unittest.main()
