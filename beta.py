import pandas as pd
import json
import ast 
from tqdm import tqdm
import numpy as np

from alpha import alphaData

class betaData:
    def __init__(self, conversation_json, alpha_key=None):
        with open(conversation_json, 'r') as f:
            self.conv_data = json.load(f)
        self.line_df = self.make_lines_df()
        self.conv_df = self.make_conv_df()
        if alpha_key:
            self.a = alphaData(alpha_key=alpha_key)
            self.contact_df = self.make_contact_df()
            
    # utility functions

    def clean_up_submitter(self, source):
        raw_submitter = source.split('_')[-1].split('.')[0]
        if len(raw_submitter) > 1:
            try:
                int(raw_submitter[-1])
                try:
                    int(raw_submitter[-2])
                    clean = raw_submitter[:-2]
                except ValueError:
                    clean = raw_submitter[:-1]
            except ValueError:
                clean = raw_submitter
        else:
            clean = raw_submitter
        return clean

    #build dataframes
    
    def make_lines_df(self):
        lines = {}
        for conv_idx, conv in self.conv_data.items():
            lines_n = []
            for line in conv['lines']:
                line_idx = str(conv_idx) + '_' + str(line['line_n'])
                line['text'] = line['text'].strip('\n')[1:]
                lines[line_idx] = line
                lines_n.append(line_idx)
            self.conv_data[conv_idx]['lines_n'] = lines_n
                
        return pd.DataFrame.from_dict(lines, orient='index')
        
    def make_conv_df(self):
        df = pd.DataFrame.from_dict(self.conv_data, orient='index')
        df.drop(columns=['lines', 'user_seq', 'users_key'], inplace=True)
        return df
    
    def make_contact_df(self):
        
        # build a base contact df for every conversation
        contacts = {}
        for k, item in self.conv_data.items():
            for n, u in enumerate(item['users']):
                user_idx = str(k) + '_' + str(n)
                line_idxs = [str(k) + '_' + str(l['line_n']) for l in item['lines'] if l['user'] == u]
                school = item['source'].split('/')[1]
                submitter = item['source'].split('/')[2].split('_')[-1][:-4]

                # mimic flawed alpha process by storing the first found chatter_ID
                # rather than proceeding to resolve duplicates
                chatter_id = self.a.search(u)[0]
                
                # clean up inconsistencies in the submitter field
                clean_submitter = self.clean_up_submitter(item['source'])
                
                contacts[user_idx] = {'contact_name':u,
                                    'AS_ALPHA_chatter_id':chatter_id,
                                    'line_idxs':line_idxs,
                                    'source':item['source'],
                                    'school':school,
                                    'submitter':submitter,
                                    'clean_submitter': clean_submitter}
                
        df = pd.DataFrame.from_dict(contacts, orient='index')
        
        # refine down contacts to only keep individual per submitter
        submitters = df.groupby(['clean_submitter'])        
        _ref = {}
        for _, subm in submitters:
            _conts = subm.groupby(['contact_name'])
            for _, c in _conts:
                s_c = ()
                for idx, row in c.iterrows():
                    s_c = s_c + (idx,)
                _ref[s_c[0]] = s_c

        submitter_contacts = {}
        
        for key, item in _ref.items():
            data = contacts[key]
            line_idxs = []
            for idx in item:
                line_idxs.extend(contacts[idx]['line_idxs'])
            data['line_idxs'] = line_idxs
            submitter_contacts[key] = data
        
        return pd.DataFrame.from_dict(submitter_contacts, orient='index')


    def get_contact_lines(self, beta_contact_idx):
        return list(self.line_df.loc[self.contact_df.loc[beta_contact_idx]['line_idxs']]['text'])