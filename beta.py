import pandas as pd
import json
import ast 
from tqdm import tqdm
import numpy as np
import re

from alpha import alphaData

class betaData:
    def __init__(self, conversation_json=None, alpha_key=None, line_csv=None, alpha_object=None):

        if type(conversation_json) == str:
            with open(conversation_json, 'r') as f:
                self.conv_data = json.load(f)
        elif type(conversation_json) == dict:
            self.conv_data = conversation_json

        if type(line_csv) == str:
            self.line_df = pd.read_csv(line_csv)
        else:
            self.line_df = line_csv
        
        if alpha_object:
            self.a = alpha_object
        elif alpha_key:
            self.a = alphaData(alpha_key=alpha_key)

        self.run()
    # utility functions

    #build dataframes
    
    def make_line_df(self):
        self.line_df.dropna(inplace=True)
        # self.line_df.dropna(subset=['raw_message','text'], inplace=True)
        self.line_df['line_idx'] = self.line_df.index
        self.line_df['line_idx'] = self.line_df.line_idx.apply(lambda n: 'l_' + str(n))
        self.line_df['source'] = self.line_df.conv_n.apply(lambda conv_n: self.conv_data[str(conv_n)]['source'])
        self.line_df['conv_idx'] = self.line_df.conv_n.apply(lambda conv_n: 'c_'+str(conv_n))
        self.line_df['school'] = self.line_df.source.apply(lambda source: source.split('/')[1])
        self.line_df['submitter'] = self.line_df.source.apply(lambda source: source.split('/')[2].split('_')[-1][:-4])
        self.line_df['clean_submitter'] = self.line_df.source.apply(lambda x: re.sub('\d','',x))
        
        self.line_df.index = self.line_df['line_idx']

    def make_conv_df(self):
        convs = self.line_df.groupby(['conv_idx'])
        self.conv_df = convs.first()
        self.conv_df['line_idxs'] = convs.line_idx.apply(list)
        self.conv_df['users'] = convs.user.apply(lambda x:list(dict.fromkeys(list(x))))
        self.conv_df['user_idxs'] = [[] for x in self.conv_df.index]

    def make_user_df(self):
        users = self.line_df.groupby(['user'], as_index=False)
        self.user_df = users.first()
        self.user_df['user_name'] = self.user_df.user
        self.user_df['line_idxs'] = users.line_idx.apply(list)
        self.user_df['conv_idxs'] = users.conv_idx.apply(lambda x:list(dict.fromkeys(list(x))))

        self.user_df['user_idx'] = self.user_df.index
        self.user_df.index = self.user_df['user_idx'] = self.user_df.user_idx.apply(lambda idx: 'u_' + str(idx))
        
        self.user_df['AS_ALPHA_chatter_id'] = self.user_df.user_name.apply(lambda x: self.a.search(x))

        # # add user fields to other frames
        # for idx in self.user_df.index:
        #     row = self.user_df.loc[idx]
        #     u_idx = row.user_idx
        #     for line_idx in row.line_idxs:
        #         self.line_df.at[line_idx, 'user_idx'] = u_idx
        #     for c_idx in row.conv_idxs:
        #         self.conv_df.loc[c_idx]['user_idxs'].append(u_idx)

    def run(self):
        print("Building Line Frame")
        self.make_line_df()
        print("Building Conv Frame")
        self.make_conv_df()
        print("Building User Frame")
        self.make_user_df()

    
class wa_beta(betaData):

    def deal_with_contacts():
        """ Whatsapp uses contact names rathe than true users, this means that there can overlaps and errors depending on how entered that contact """
        """ To deal with that, we handle users as 'submitter_username' for whatsapp """
        self.line_df['user'] = self.line_df[['clean_submitter','contact_name']].apply(lambda x: '_'.join(x), axis=1)

    def run(self):
        self.line_df = self.make_lines_df()
        self.deal_with_contacts()
        self.conv_df = self.make_conv_df()
        self.contact_df = self.make_contact_df()
        
class fb_beta(betaData):
    pass