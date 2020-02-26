import pandas as pd
import numpy as np
import json
from collections import defaultdict as dd
from tqdm import tqdm
import nl_core_news_sm
nlp = nl_core_news_sm.load()
import re


# resources

with open('/home/burtenshaw/data/teen/beta/usable_user_list.json', 'r') as f:
    all_users = json.load(f)

with open('/home/burtenshaw/data/teen/annon_files/gementes_improved.json', 'r') as f:
    gementes = json.load(f) 

with open('/home/burtenshaw/data/teen/annon_files/streets.json', 'r') as f:
    streets = json.load(f)


manual_additions = ['hoboken']
vocab_gementes = [x for x in gementes if x in nlp.vocab and x not in manual_additions]

gementes.extend(streets)
vocab_gementes.extend([x for x in streets if x in nlp.vocab])

def fuzzy_names(names):
    _ = {}
    for n in names:
        try:
            int(n[-1])
        except ValueError :
            _n = n.split(' ')
            x = _n[0].lower()
            y = ' '.join(_n[1:]).lower()
            
            if len(x) > 2:
                _[x] = n
            if len(y) > 2:
                _[y] = n
    return _

all_fuzzy_names = fuzzy_names(all_users)

# # annon functions

def get_u_idx(real_name):
    ''' beef up this function to handle all the users in the study'''
    try:
        return user_df.loc[user_df['user_name_lower'] == real_name].user_idx[0]
    except:
        return real_name

def check_text_for_user(text, c_users):
    doc = nlp(text)
    for c_u in c_users:
        for token in doc:
            if token.pos_ == 'PROPN' and token.text == c_u:
                text = [t.text for t in doc]
                text[token.i] = get_u_idx(all_fuzzy_names[c_u])
                text = ' '.join(text)
    return text

locations = dd(str)
_x = 0

def check_text_for_locations(text):
    doc = nlp(text)
    for t in doc:
        txt = t.lower_
        if txt in gementes:
            if txt not in vocab_gementes:
                locations[txt] = locations.get(txt, loc_idx(_x))
                text = text.replace(t.text,locations[txt])
                _x += 1
            elif t.ent_type_ == 'LOC':
                locations[txt] = locations.get(txt, loc_idx(_x))
                text = text.replace(t.text,locations[txt])
                _x += 1
            elif t.pos_ == 'NOUN' and t.pos_ != nlp(txt)[0].pos_:
                locations[txt] = locations.get(txt, '_'+loc_idx(_x))
                text = text.replace(t.text,locations[txt])
                _x += 1

    return text

def loc_idx(_x):
    """ give a descrete location reference for places found in text"""
    return 'loc_'+str((_x*_x))

# tidying functions

def extra_words(a, b, s='\n'):
    return list(set(a.split(s)) - set(b.split(s)))

def tidy_users(users):
    _ = [u.replace('\n', '') for u in users if len(u) > 1 and u.isspace() == False]
    _ = list(dict.fromkeys(_))
    return _

def split(delimiters, string, maxsplit=0):
    import re
    regexPattern = '(?:'+'|'.join(map(re.escape, delimiters))+')'
    return re.split(regexPattern, string, maxsplit)
    
# def check_on_all_patterns(t, patterns=patterns['multi_date']):
#     conv = []
#     for dp in patterns:
#         date_split_text = dp.split(t)
#         if len(date_split_text) > 1:
#             t = date_split_text[0]
#             conv = date_split_text[1:]
#             break
#     return t, conv, dp

def get_user(raw, users):
    t = raw
    user = 'unfound'
    for u in users:
        if raw.startswith(u):
            user = u
            t = raw.replace(u,'')
            break
    return t, user

def wrap_line(t, users, dp, conv_n):
    if dp.match(t):
        raw_date = t
    else:
        raw_date = 'unfound'
    raw, conv, dp = check_on_all_patterns(t)
    t, user = get_user(t, users)
    if t != raw_date and t.isspace() == False and len(raw) > 0 and len(t) > 0:
        return {'conv_n' :conv_n, 'line_n':'_','raw_date':raw_date, 'raw_message':raw, 'text':t, 'user': user}
    else:
        return {}
