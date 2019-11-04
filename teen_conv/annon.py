import pandas as pd
import numpy as np
import json
from collections import defaultdict as dd
from tqdm import tqdm
import nl_core_news_sm
nlp = nl_core_news_sm.load()
import re

class annon:
    def __init__(self, user_df, line_df, all_users, locations, manual_additions=['hoboken']):
        self.user_df = user_df
        self.user_df['user_name_lower'] = self.user_df.us
        self.line_df = line_df
        self.conv_df = conv_df
        self.all_users = all_users
        self.locations = locations
        self.manual_additions = manual_additions
        self.vocab_locations = self.make_vocab_gementes()
        self.fuzzy_names = make_fuzzy_names(all_users)
        self.found_locations = dd(str)
        self._x = 0

    def make_vocab_gementes(self):
        return [x for x in gementes if x in nlp.vocab and x not in self.manual_additions]

    def make_fuzzy_names(self, names):
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

    def get_u_idx(self, real_name):
        ''' beef up this function to handle all the users in the study'''
        try:
            return self.user_df.loc[self.user_df['user_name_lower'] == real_name].user_idx[0]
        except:
            return real_name

    def loc_idx(_x):
        """ give a descrete location reference for places found in text"""
        return 'loc_'+str((_x*_x))

    def check_text_for_user(self, text, c_users):
        doc = nlp(text)
        for c_u in c_users:
            for token in doc:
                if token.pos_ == 'PROPN' and token.text == c_u:
                    text = [t.text for t in doc]
                    text[token.i] = self.get_u_idx(all_fuzzy_names[c_u])
                    text = ' '.join(text)
        return text

    def check_text_for_locations(self, text):
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
    
    def local_users(self):
        df = self.line_df
        df['local_users'] = df.conv_idx.progress_apply(lambda x: self.fuzzy_names(self.conv_df.loc[x].users).keys())
        df['annon_text'] = df.progress_apply(lambda x:check_text_for_user(x.text, x.local_users),axis=1)
        return df

    def exterior_users(self):
        df = self.line_df
        df['annon_text'] = df.progress_apply(lambda x:check_text_for_user(x.annon_text, all_fuzzy_names.keys()),axis=1)
        return df

    def locations(self):
        df = self.line_df
        df['annon_text'] = df.annon_text.progress_apply(self.check_text_for_locations)

    def emails(self):
        df = self.line_df
        p = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
        df['annon_text'] = df.annon_text.progress_apply(lambda txt: re.sub(p, "email@privaat.com", txt))


# resources

with open('/home/burtenshaw/data/teen/beta/usable_user_list.json', 'r') as f:
    all_users = json.load(f)

with open('/home/burtenshaw/data/teen/annon_files/gementes_improved.json', 'r') as f:
    gementes = json.load(f) 

with open('/home/burtenshaw/data/teen/annon_files/streets.json', 'r') as f:
    streets = json.load(f)

gementes.extend(streets)



all_fuzzy_names = fuzzy_names(all_users)

# # annon functions

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
