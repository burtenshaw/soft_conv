import re
import difflib
import itertools
import pandas as pd
import numpy as np
import json
import ast 
from tqdm import tqdm

names = {
        'all': ["post", "chatter_ID", "medium", "year", "conv_sex", "conv_size", "gender", "age", "region", "education", "language", "prof", "prof_cat", "permission", "permission_parents", "school", "in_gesprek"],
        'line_fields' : [
        "post",
        "chatter_ID",
        "medium",
        "year",
        "conv_sex",
        "conv_size"
                ],
         'user_fields' : [
        "chatter_ID",
        "gender",
        "age",
        "region",
        "education",
        "language",
        "prof",
        "prof_cat",
        "permission",
        "permission_parents",
        "school",
        "in_gesprek"
         ]
        }

class alphaData:
    def __init__(self, src_path=None, alpha_key=None, website_encoding=None, manual_encoding=None, names=names):
        self.key = alpha_key
        self.encodings = [website_encoding, manual_encoding]
        self.src = src_path
        self.names = names
        if src_path:
            self.load()

    def build_key(self, keys_output=None):
        key_dict = {}

        web = pd.read_csv(self.encodings[0], delimiter=';')
        web.columns = web.iloc[1]
        web = web.drop([0,1,2,3,4,5])
        for _, row in web.iterrows():
            key_dict['website ' + str(row.Serial)] = str(row.Voornaam) + ' ' + str(row.Familienaam)

        manual= pd.read_csv(self.encodings[1], delimiter=';')
        for _, row in manual.iterrows():
            key_dict[str(row['ID Chatter'])] = str(row[1])
        
        self.key = key_dict

    def load(self):
        self.df = pd.read_csv(self.src, delimiter='\t', names=self.names['all'])
        
    def make_user_df(self):
        user_df = self.df[self.names['user_fields']]
        user_df = user_df.drop_duplicates(subset='chatter_ID', keep='first')
        user_df = user_df.set_index('chatter_ID')
        
        gp = self.df.groupby('chatter_ID', sort=False)
        user_df['lines_n'] = pd.Series(dict(gp.groups))
        user_df['lines_n'] = [list(n) for n in user_df['lines_n']]

        self.user_df = user_df

    def make_line_df(self):
        self.line_df = self.df[self.names['line_fields']]
    
    def run(self):
        self.make_line_df()
        self.make_user_df()
    
    def save(self, output_dir):
        self.line_df.to_csv(output_dir+"alpha_lines.csv")
        self.user_df.to_csv(output_dir+"alpha_users.csv")
        
    def search(self, contact):
        chatter_ID = []
        for field_ID, field_name in self.key.items():
            if field_name.lower() == contact.lower():
                chatter_ID.append(field_ID)
        if len(chatter_ID) == 0:
            chatter_ID = [None]
        return chatter_ID

    def get_user_lines(self, chatter_id):
        try:
            return [str(x).lower() for x in list(self.line_df.loc[chatter_id]['post'])]
        except KeyError:
            return []


# class betaData:
#     def __init__(self, conversation_json):
#         with open(conversation_json, 'r') as f:
#             self.conv_data = json.load(f)
#         self.line_df = self.make_lines_df()
#         self.conv_df = self.make_conv_df()
    
#     def make_lines_df(self):
#         df = pd.DataFrame.from_dict(self.conv_data, orient='index')['lines']
#         df = pd.DataFrame(data=df)
#         df = df.lines.apply(pd.Series)
#         return df
        
#     def make_conv_df(self):
#         df = pd.DataFrame.from_dict(self.conv_data, orient='index')
#         df.drop(columns=['lines', 'user_seq', 'users_key'], inplace=True)
#         return df

class matchDataSets:
    def __init__(self, alpha, beta,     params = {'sample':10,'intersection':0.7}, check_alpha = True):
        alpha.line_df.index = alpha.line_df['chatter_ID']
        self.alpha = alpha
        self.beta = beta
        self.alpha_key = alpha.key
        self.manual_df = pd.DataFrame()
        self.contact_df = pd.DataFrame()
        self.log = []
        self.params = params
        self.check_alpha = check_alpha
        self.proposal_df = self.build_proposal_df()

    # utility functions
    
    def clean_beta_examples(self, contact_name):
        beta_examples = list(self.beta.line_df.loc[self.beta.line_df.user.str.contains(contact_name)].text.dropna().str.lower())
        beta_examples.sort(key=lambda x: len(str(x)), reverse=True)
        return beta_examples
                                                                                                                                   
    def clean_alpha_examples(self, chatter_id):
        alpha_examples = list(self.alpha.line_df.loc[self.alpha.line_df.chatter_ID.str.contains(chatter_id)].post.dropna().str.lower())
        alpha_examples.sort(key=lambda x: len(str(x)), reverse=True)
        return alpha_examples
    
    def match_intersection(self, a, b):
        return len(list(set(a) & set(b)))
    
    def write_df(self,chatter_id,beta_contact_idx,_inter):
        self.contact_df = self.contact_df.astype('object')
        self.contact_df.at[beta_contact_idx, 'matched_chatter_id'] = chatter_id
        self.contact_df.at[beta_contact_idx, 'match_intersection'] = _inter
        self.contact_df.at[beta_contact_idx, 'AS_ALPHA_chatter_id'] = self.beta.user_df.AS_ALPHA_chatter_id[beta_contact_idx]
        self.contact_df.at[beta_contact_idx, 'proposed_chatter_ids'] = str(self.proposal_df.proposed_chatter_ids[beta_contact_idx])
    # proposal df

    def build_proposal_df(self):
        print('Making Proposals')
        proposal = self.beta.user_df
        all_names = list(dict.fromkeys(self.alpha_key.values()))
        alpha_chatter_ids = list(self.alpha.user_df.index)
        proposal['possible_names'] = proposal.user.apply(lambda x: difflib.get_close_matches(x, all_names, n=3, cutoff=0.75))
        proposal['proposed_chatter_ids'] = proposal.possible_names.apply(lambda pos: list(itertools.chain.from_iterable([self.alpha.search(p) for p in pos])))
        return proposal

    # Matching scenarios
    
    def match_none(self, conv_idx, beta_contact_name, beta_contact_idx):
        beta_examples = self.clean_beta_examples(beta_contact_idx)
        beta_examples.sort(key=len, reverse=True)
        beta_examples = beta_examples[:3]

        matches = []

        for alpha_idx, row in self.alpha.line_df.iterrows():
            if str(row['post']).lower() in beta_examples:
                matches.append(row['chatter_ID'])

        if len(matches) > 0:
            matches = list(dict.fromkeys(matches))
            self.match_many(conv_idx, beta_contact_name, matches, beta_contact_idx)
        
    def match_one(self, conv_idx, beta_contact_name, chatter_id, beta_contact_idx):
        # get beta examples
        beta_examples = self.clean_beta_examples(beta_contact_idx)
        alpha_examples = self.clean_alpha_examples(chatter_id)
        _inter = self.match_intersection(alpha_examples, beta_examples)
        t = len(beta_examples) * self.params['intersection']
        if _inter >= t:
            match = True
        else:
            chatter_id = np.nan
            match = False
        self.write_df(chatter_id,beta_contact_idx,_inter)
        return [match,_inter]

    
    def match_many(self, conv_idx, beta_contact_name, proposed_chatter_ids, beta_contact_idx):
        self.manual_df.at[beta_contact_idx, '_'] = 0
        for n, chatter_id in enumerate(proposed_chatter_ids):
            match = self.match_one(conv_idx,beta_contact_name,chatter_id,beta_contact_idx)
            if match[0]:
                self.manual_df.drop([beta_contact_idx], inplace=True)
                break
            else:
                self.manual_df.at[beta_contact_idx, 'conv_id'] = conv_idx
                self.manual_df.at[beta_contact_idx, 'source'] = self.beta.conv_df.loc[conv_idx]['source']
                self.manual_df.at[beta_contact_idx, 'contact name'] = beta_contact_name
                self.manual_df.at[beta_contact_idx, 'submitter'] = self.beta.user_df.loc[beta_contact_idx]['submitter']
                self.manual_df.at[beta_contact_idx, 'proposed_chatter_id_%s' % n] = str(chatter_id)
                self.manual_df.at[beta_contact_idx, 'proposed_alpha_name_%s' % n] = self.alpha_key[chatter_id]
                self.manual_df.at[beta_contact_idx, 'proposed_chatter_id_%s_match_intersection' % n] = match[1]
    
    def run(self):
        with tqdm(total=self.proposal_df.shape[0]) as pbar:
            for beta_contact_idx, row in self.proposal_df.iterrows():
                self.log.append(beta_contact_idx)
                beta_contact_name = row['user']
                self.contact_df.at[beta_contact_idx, 'beta_contact_name'] = beta_contact_name

                conv_idx = self.beta.user_df.loc[beta_contact_idx]['conv_idxs'][0]
                proposed_chatter_ids = row['proposed_chatter_ids']

                if len(proposed_chatter_ids) > 0:
                    self.match_many(conv_idx, beta_contact_name, proposed_chatter_ids, beta_contact_idx)
                    
                pbar.update(1)
