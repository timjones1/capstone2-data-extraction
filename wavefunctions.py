from spacy.tokens import Token, Span, Doc
from dateutil import parser
import numpy as np
import re

BASE_DATE = "13th October 2019 "
weekdays = {"monday":1,"tuesday":2,"wednesday":3,"thursday":4,
            "friday":5,"saturday":6,"sunday":7}
number_dict = {"half":0.5,"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,
             "eight":8, "nine":9}

def get_days_per_week(doc):
    
    ents = doc.ents
    days = {"half":0.5,"one":1,"two":2,"three":3,"four":4,"five":5,
            "six":6,"seven":7}

    if "monday to friday" in [e.text.lower() for e in ents]:
        return 5
        
    day_res = [e for e in ents if "days" in e.text]

    if any(day_res):

        num_days = day_res[0].text.replace("days","").lower().strip()
    
        if num_days in ["1","2","3","4","5","6","7"]:
            return int(num_days)

        else: return days.get(num_days)
    
    else: return find_nr_weekdays(doc)


def find_nr_weekdays(doc):


    weekdays = {"monday":1,"tuesday":2,"wednesday":3,"thursday":4,
                "friday":5,"saturday":6,"sunday":7}
    days = set()
    for token in doc:

        head_is_weekday = token.head.text.lower() in weekdays
        is_weekday_range = token.head.pos_ == "PROPN" and token.text == "to"
    
        if head_is_weekday and is_weekday_range:
            day_nr_to = weekdays.get(next(token.children).text.lower())
            day_nr_from = weekdays.get(token.head.text.lower())
            return day_nr_to - day_nr_from + 1
   
        [days.add(w) for w in weekdays if w in token.text]
        
    if any(days):

        return len(days)

    else: return None 

def convert_time(token):
    '''
    converts a token containing time in a string format and returns a datetime
    object using an arbitrary date and the datetime parser, the function also
    strips noisy text from the string to assist with parsing. #
    '''

    time_text = token.text.replace(".", ":")
    time_text = time_text.replace("o", "0").replace("O", "0")
    time_text = time_text.replace("hrs", "").replace("hours", "") 
    if (time_text[0:2].isdigit()):
        if (int(time_text[0:2]) > 12):
            time_text = time_text.replace("pm", "")
    
    match = re.match(r"(\d{1,2})(:|\.)?(\d{2})(?:\d)?(am|pm)?", time_text)

    if match:
        re_text = "".join(filter(None,match.groups()))
        date_time = parser.parse(BASE_DATE+re_text)
        return date_time
    return 0


def calc_hours(time_span):
    '''
    Returns the number of hours in a TIME entity with , converts the start
    and end times to datetime objects and subtracts them to
    provide a timedelta object which can be manipulated to return difference
    in hours. a conditional statement has been added to extract the day
    '''
    
    start_time = convert_time(time_span[0])
    end_time = convert_time(time_span[2])
    delta = end_time - start_time

    return round(delta.seconds / 3600, 2)

    
def get_days_per_week_new(doc):
    
    if doc.text == "None": return None

    # days = {"half":0.5,"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7}

    nr_days = 0
    part_days = 0

    for token in doc:
        if token.lower_ in ["day", "days"]:
            
            for left_tok in token.lefts:
                if left_tok.pos_ == "NUM":
                    if left_tok.is_digit:
                        nr_days = int(left_tok.text)
                    
                    if left_tok.lower_ in number_dict:
                        nr_days = number_dict.get(left_tok.lower_)
                
                if left_tok.pos_ == "ADJ": 
                    if left_tok.lower_ in number_dict:
                        part_days += number_dict.get(left_tok.lower_)
                        
    if nr_days > 0: return nr_days + part_days

    if find_nr_weekdays_new(doc) is not None:
        return find_nr_weekdays_new(doc) - part_days

    else: return None

def extract_specified_times(doc):
    '''
    retrieve specified days and hours from the entities of a doc if present 
    and store values in specified_hours and specified days doc level extensions
    if it is a lunch break store in a lunch_hours document level extension.
    '''
    nr_hours = 0

    def is_lunch(token):
        ''' check if token relates to hour(s) for a lunch break returns a boolean '''
        return (any([True for tok in token.rights for a in tok.children 
                     if a.lower_ in ["lunch","unpaid"]]) 
                or token.head.lower_ in ["lunch","unpaid"])

    def is_staffed(ent):
        ''' check if entity relates to hours that the office is staffed returns a boolean'''
        return any([True for tok in ent[0].head.children if tok.lower_ == "staffed"])


    for ent in doc.ents:
        for idx,token in enumerate(ent):
            if (token.lower_ in ["hour", "hours"] and ent.label_ == "TIME"):
                
                previous_token = ent[idx-1]
                
                if previous_token.pos_ == "NUM":
                        nr_hours = get_number_from_token(previous_token)                        
            
                        if is_lunch(token): ent.doc._.lunch_hours = nr_hours

                        else: ent.doc._.specified_hours = nr_hours 


        if (ent.label_ == "TIME" and len(ent) == 3 and not(is_staffed(ent))
            and ent[1].lower_ in ["to","-"]):
                ent._.saved_hours = calc_hours(ent)

    return nr_hours

        
def get_days_per_week_model(doc):
        
    if doc.text == "None": return 0

    nr_days = 0
    part_days = 0

    for token in doc:
        if token.lower_ in ["day", "days"]:
            
            for tok in token.lefts:
                if tok.pos_ == "NUM":
                    nr_days = get_number_from_token(tok)
                
                if tok.pos_ == "ADJ": 
                    if tok.lower_ in number_dict:
                        part_days += number_dict.get(tok.lower_)
                    
    if nr_days > 0: return nr_days + part_days

    if find_nr_weekdays_model(doc) is not None:
        return find_nr_weekdays_model(doc) - part_days

    else: return None




def find_nr_weekdays_model(doc):
    '''
    returns the number of days worked from the weekdays mentioned in a given doc. 
    adapted for model based approach approach.
    '''

    ents = doc.ents
    
    days = set()
    
    for ent in ents:
        
        days_count = len(days) # used to keep track of changes in nr_days per ent.

        if "monday to friday" in ent.text.lower():
            ent._.saved_days = 5
            return 5
        
        if (ent.label_ == "DATE" and len(ent) == 3):
            if (ent[0].pos_ == "PROPN" and ent[1].lower_ in ["to","-"] and ent[2].pos_ == "PROPN"):
                ent._.saved_days = extract_days(ent)
                return extract_days(ent)
    
        [days.add(w) for w in weekdays for token in ent if w in token.text.lower()]
        ent._.saved_days = len(days) - days_count

    if any(days): 
        return len(days)

    else: return 0

def find_nr_weekdays_new(doc):
    '''
    returns the number of days worked from the weekdays mentioned in a given doc. 
    written for rule based approach using entity ruler.
    '''

    ents = doc.ents
    
    days = set()
    
    for ent in ents:
        if ent.ent_id_ == "days_range":
            return extract_days(ent)
    
        [days.add(w) for w in weekdays for token in ent if w in token.text.lower()]
   
    if any(days):
        return len(days)

    else: return None 

def extract_days(ent):
    
    day_nr_to = weekdays.get(ent[2].lower_)
    day_nr_from = weekdays.get(ent[0].lower_)
    return day_nr_to - day_nr_from + 1

def get_number_from_token(token):
    ''' returns a numeric value from a token from word or number form '''
               
    if token.lower_ in number_dict:
        return number_dict.get(token.lower_)
    
    if token.like_num:
        return float(token.text)

    
    return 0

def get_hours_from_doc_ents(doc):

    running_hours = 0
    current_hours = 0
    current_days = 0
    lunch_adj = 0
    

    if doc._.specified_hours == 0:
        for e in doc.ents:
        
            if e._.saved_hours != 0:
                current_hours = e._.saved_hours
                if current_days != 0:
                    if current_hours < 5.5:
                        lunch_adj = 1
                    running_hours += (current_hours - doc._.lunch_hours + lunch_adj)* current_days
                    current_hours = 0
                    current_days = 0
                    lunch_adj = 0
            
            if e._.saved_days != 0:
                current_days = e._.saved_days
                if current_hours != 0:
                    if current_hours < 5.5:
                        lunch_adj = 1
                    running_hours += (current_hours - doc._.lunch_hours + lunch_adj) * current_days
                    current_hours = 0
                    current_days = 0
                    lunch_adj = 0
                
        if running_hours > 0: doc._.specified_hours = running_hours
    
        else: 
            if current_hours !=0:
                doc._.specified_hours = (current_hours - doc._.lunch_hours) * doc._.specified_days
    
    return running_hours

def get_assumed(specified_time,timeframe="days"):
    '''helper function to calculate assumed hours and days'''
    multiplier = 1
        
    if timeframe == "hours":
        multiplier = 7.5
        
    if specified_time == 0:
        return 5 * multiplier
    else: return 0

def get_blended(specified_time,timeframe="days"):
    '''helper function to calculate blended hours and days'''
    multiplier = 1
        
    if timeframe == "hours":
        multiplier = 7.5
    
    if specified_time == 0:
        return 5 * multiplier
    else: return specified_time

def check_results(preds, actuals):
    '''
    Function to check accuracy the of extracted data to the actual values stored in contract_df
    '''
    cols = preds.columns
    
    for t in ["text","days_holiday","pro_rata","days_entitled","days_phol"]: 
        if t in cols:
            cols = cols.drop(t)
    
    actuals = actuals[cols].fillna(0).reset_index()
    
    rows = len(preds)
    features = len(cols)
    score_matrix = np.zeros((rows,features))
    
    for idx,col in enumerate(cols):
        score_matrix[:,idx] = (preds[col] == actuals[col])
    
    return f"{np.sum(score_matrix) / (rows*features) * 100:.1f}% accuracy"

def get_days_holiday(doc):
    '''
    '''
    for ent in doc.ents:
        if("days" in ent.lower_ and check_nearby_tokens(ent[0],"entitled",[4,0])):
            return get_number_from_token(ent[0])
        
def get_days_entitled(doc):
    
    for ent in doc.ents:
        if("days" in ent.lower_ and check_nearby_tokens(ent[0],"entitlement",[4,0])):
            return get_number_from_token(ent[0])
        
def get_days_phol(doc):
    
    for ent in doc.ents:
        if("days" in ent.lower_ and (check_nearby_tokens(ent[0],"public",[0,4]) or 
           check_nearby_tokens(ent[0],"bank",[0,4]))):
            return get_number_from_token(ent[0])

def check_nearby_tokens(token,search_word,n_range):
    '''
    For a given token, check if a given search_word string is present within
    a given n_range of surrounding tokens, return True if found otherwise False
    
    token: a spacy token object
    search_word: a string object to search for.
    n_range: list of 2 ints, giving the number of tokens before and after to 
             check
    '''
    if token.i < n_range[0]:
        start = 0
    else: start = token.i - n_range[0]
    
    finish = token.i + n_range[1]
    
    return (search_word in token.doc[start:finish].lower_)
