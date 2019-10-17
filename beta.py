import pandas as pd
import json
import ast 
from tqdm import tqdm
import numpy as np


class betaData:
    def __init__(self, conversation_json):
        with open(conversation_json, 'r') as f:
            self.conv_data = json.load(f)
        self.line_df = self.make_lines_df()
        self.conv_df = self.make_conv_df()
    
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
                
        df = pd.DataFrame.from_dict(lines, orient='index')
        return df
        
    def make_conv_df(self):
        df = pd.DataFrame.from_dict(self.conv_data, orient='index')
        df.drop(columns=['lines', 'user_seq', 'users_key'], inplace=True)
        return df

    def make_user_df(self):
        user_df = df[self.names['user_fields']]
        user_df = user_df.drop_duplicates(subset='chatter_ID', keep='first')
        user_df = user_df.set_index('chatter_ID')
        
        gp = self.df.groupby('chatter_ID', sort=False)
        user_df['lines_n'] = pd.Series(dict(gp.groups))
        user_df['lines_n'] = [list(n) for n in user_df['lines_n']]
        
        self.user_df = user_df