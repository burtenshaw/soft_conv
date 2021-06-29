import pandas as pd
import numpy as np
import json
from collections import defaultdict as dd
from tqdm import tqdm
import nl_core_news_sm
import re
from ast import literal_eval
nlp = nl_core_news_sm.load()
tqdm.pandas()

with open('/home/burtenshaw/data/vocab/nl_vocab.json') as f:
    nl_vocab = json.load(f)

class Annon:
    
    def __init__(self, user_df, line_df, conv_df, all_users, locations, nl_vocab=nl_vocab, manual_additions=['hoboken']):
        self.user_df = user_df
        self.user_df['user_name_lower'] = self.user_df.user_name.str.lower()
        self.line_df = line_df
        self.conv_df = conv_df
        self.line_df['annon_text'] = line_df.text
        self.all_users = all_users
        self.nl_vocab = set(nl_vocab)
        self.locations = locations
        self.locations_set = set(locations)
        self.manual_additions = manual_additions
        self.vocab_locations = self.make_vocab_locations()
        # self.fuzzy_names = self.make_fuzzy_names(all_users)
        self.found_locations = dd(str)
        self._x = 0

    def make_vocab_locations(self):
        return self.nl_vocab.intersection(self.locations_set)

    def make_fuzzy_names(self, names):
        _ = {}
        names = literal_eval(names)
        for n in names:
            n = n.lower()
            _n = n.split(' ')
            x = _n[0].lower()
            y = ' '.join(_n[1:]).lower()
            _[x] = n
            _[y] = n
        return _

    def get_u_idx(self, real_name, token):
        ''' beef up this function to handle all the users in the study'''
        try:
            return self.user_df.loc[self.user_df['user_name_lower'] == real_name].index[0]
        except:
            return token

    def loc_idx(self, _x):
        """ give a descrete location reference for places found in text"""
        return 'loc_'+str((_x*_x))

    def check_text_for_user(self, text, c_users):

        for c_u in c_users.keys():
            if c_u in text:
                doc = nlp(text)
                l = len(text)
                for token in doc:
                    if token.pos_ == 'PROPN' and token.text == c_u:
                        text = ''.join((text[:token.idx-l],self.get_u_idx(c_users[c_u], token.text), text[(token.idx-l)+len(token):]))
        return text

    def check_text_for_locations(self, text):
        if len(set([t.text for t in nlp.tokenizer(text)]).intersection(self.locations_set)):
            doc = nlp(text)
            l = len(text)
            # alpino tagging
            # monoise
            for token in doc:
                txt = token.lower_
                if txt in self.locations:
                    if txt not in self.vocab_locations and token.ent_type_ == 'LOC':
                        self.found_locations[txt] = self.found_locations.get(txt, self.loc_idx(self._x))
                        start = token.idx-l
                        end = start+len(token)
                        new_text = [text[:start],self.found_locations[txt]]
                        if end:
                            new_text.append(text[end:])
                        text = ''.join(tuple(new_text))
                        self._x += 1
                    # elif :
                    #     self.found_locations[txt] = self.found_locations.get(txt, self.loc_idx(self._x))
                    #     text = ''.join((text[:token.idx-l],self.found_locations[txt], text[(token.idx-l)+len(token):]))
                    #     self._x += 1
                    # elif token.pos_ == 'NOUN' and token.pos_ != nlp(txt)[0].pos_:
                    #     self.found_locations[txt] = self.found_locations.get(txt, self.loc_idx(self._x))
                    #     text = ''.join((text[:token.idx-l],self.found_locations[txt], text[(token.idx-l)+len(token):]))
                    #     self._x += 1

        return text
    
    def remove_local_users(self):
        df = self.line_df
        df['local_users'] = df.conv_idx.progress_apply(lambda x: self.make_fuzzy_names(self.conv_df.loc[x].users))
        df['annon_text'] = df.progress_apply(lambda x:self.check_text_for_user(x.annon_text, x.local_users),axis=1)
        return df

    def remove_exterior_users(self):
        df = self.line_df
        _all_users = dict(zip(self.all_users, self.all_users))
        df['annon_text'] = df.progress_apply(lambda x:self.check_text_for_user(x.annon_text, _all_users),axis=1)
        return df

    def remove_locations(self):
        df = self.line_df
        df['annon_text'] = df.annon_text.progress_apply(self.check_text_for_locations)
        return df

    def remove_emails(self):
        df = self.line_df
        p = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
        df['annon_text'] = df.annon_text.progress_apply(lambda txt: re.sub(p, "email@privaat.com", txt))
        return df
