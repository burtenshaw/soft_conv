import re
import difflib
import itertools
import pandas as pd
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
    def __init__(self, src_path, website_encoding, manual_encoding, names=names):
        self.encodings = [website_encoding, manual_encoding]
        self.src = src_path
        self.names = names
        self.load()

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
        
    def search(self, name):
        ID = None
        for n, e in enumerate(self.encodings):           
            codings_file = open(e,'rt', encoding = 'latin-1').read()
            codings_names = codings_file.split("\n")

            # we look for the correct coding
            if n == 0: 
                for item in codings_names:
                    fields = item.split(';')
                    # if the length of the line is valid, the fields contain the necessary info
                    if len(fields)>=23:
                        field_ID = fields[0]
                        field_first_name = fields[9]
                        field_last_name = fields[10]
                        field_name = str(field_first_name)+' '+str(field_last_name)
                        # we search for the name
                        if name.lower() == field_name.lower():
                            # we strip away whitespace for the ID
                            if (field_ID[0] == '\n') or (field_ID[0] == '\r'):
                                field_ID = field_ID[1:]
                            ID = 'website '+str(field_ID)
                            break
            else:
                for item in codings_names:
                    fields = item.split(';')
                    if len(fields)>1:
                        # if the line contains more than one field, it holds an ID and a name
                        field_ID = fields[0]
                        field_name = fields[1]
                        # we search for the name in the coding file
                        if name.lower() == field_name.lower():
                            # we do not take whitespace into account for the ID
                            if (field_ID[0] == '\n') or (field_ID[0] == '\r'):
                                field_ID = field_ID[1:]
                            ID = field_ID
                            break
        return ID



class betaData:
    def __init__(self, conversation_json):
        with open(conversation_json, 'r') as f:
            self.conv_data = json.load(f)
        self.line_df = self.make_lines_df()
        self.conv_df = self.make_conv_df()
    
    def make_lines_df(self):
        df = pd.DataFrame.from_dict(self.conv_data, orient='index')['lines']
        df = pd.DataFrame(data=df)
        df = df.lines.apply(pd.Series)
        return df
        
    def make_conv_df(self):
        df = pd.DataFrame.from_dict(self.conv_data, orient='index')
        df.drop(columns=['lines', 'user_seq', 'users_key'], inplace=True)
        return df


class proposeUsers:
    def __init__(self, users, users_list, filename, pattern, users_df, look_up=True):
        '''
            Given a conversation instance from instant messaging, attempt to match users with alpha data.
        '''
        self.pattern, self.users_list , self.users, self.df, self.look_up = pattern, users_list, users, users_df, look_up
        self.f_data = self.grab_filename(filename)
        self.proposed_names = self.possible_names()
        self.validated_names = self.check_key()
        
    def grab_filename(self, filename):
        try:
            # filename = filename.split('/')[1]
            result = re.match(self.pattern, filename).groupdict()
            self.source_user = result['name']
            return result
        except AttributeError:
            print("Unexpected structure in filename: ", filename)
        
    def possible_names(self):
        return {u : difflib.get_close_matches(u, self.users_list, n=3, cutoff=0.8) for u in self.users}
    
    def check_df(self, pos, df):
        for k, i in pos.items():
            for idx in i['keys']:
                try:
                    df.loc[idx]
                    pos[k]['record'] = idx
                except KeyError:
                    pass
        return pos

    def check_key(self):
        validated = {}
        for k, i in self.proposed_names.items():
            validated[k] = {'name':i, 'keys' :list(itertools.chain.from_iterable([self.users_list[_n] for _n in i]))}
        if self.look_up:
            validated = self.check_df(validated, self.df)
        return validated
    

class matchDataSets:
    def __init__(self, alpha, beta, alpha_key, proposal_df):
        alpha.line_df.index = alpha.line_df['chatter_ID']
        self.alpha = alpha
        self.beta = beta
        self.proposal_df = proposal_df
        self.alpha_key = alpha_key
        self.alpha_key_reversed = self._reverse_key()
        
        self.manual_df = pd.DataFrame()
        self.user_df = pd.DataFrame()

    # utility functions

    def _reverse_key(self):
        alpha_key_reversed = {}
        for name, l in self.alpha_key.items():
            for k in l:
                alpha_key_reversed[k] = name 
        return alpha_key_reversed

    def match_meta_data(self, conv_idx, proposed_chatter_id):
        school = self.conv_df.at[conv_idx, 'school']
        # get more meta info from beta, and use it to match
        pass
    
    def get_beta_lines(self, conv_idx, beta_contact_name):
        beta_lines = []
        for line in self.beta.line_df.loc[conv_idx]:
            if type(line) == dict:
#                 print(conv_idx, ' ::', line)
#                 print(line['user'], ':', beta_contact_name)
                if line['user'] == beta_contact_name:  
                    beta_lines.append(str(line['text']).lower().strip('\n')[1:])
#         conv_lines = [line['text'] for line in self.beta.line_df[int(conv_idx)] if type(line) == dict and line['user'] == beta_contact_name]
        return beta_lines

    def get_alpha_lines(self, chatter_id):
        try:
            return [str(x).lower() for x in list(self.alpha.line_df.loc[chatter_id]['post'])]
        except KeyError:
            return []


    def match_none(self, conv_idx, beta_contact_name, beta_contact_int):
        beta_examples = self.get_beta_lines(conv_idx, beta_contact_name)
        if len(beta_examples) > 3:
            beta_examples.sort(key=len, reverse=True)
            beta_examples = beta_examples[:3]

            matches = []

            for alpha_idx, row in self.alpha.line_df.iterrows():
                if str(row['post']).lower() in beta_examples:
                    matches.append(row['chatter_ID'])
                    
            if len(matches) > 0:
                self.match_many(conv_idx, beta_contact_name, matches, beta_contact_int)
        
    def match_one(self, conv_idx, beta_contact_name, chatter_id, beta_contact_int):
        # get beta examples
        beta_examples = self.get_beta_lines(conv_idx, beta_contact_name)
        beta_user_idx = str(conv_idx) + '_' + str(beta_contact_int)
#         print('len examples: ',len(beta_examples))
        if len(beta_examples) > 3:
#             print(conv_idx)
#             print(beta_contact_name)
#             print(self.alpha_key_reversed[chatter_id])
#             print(chatter_id)
            beta_examples.sort(key=len, reverse=True)
            beta_examples = beta_examples[:3]
            # get alpha examples      
            alpha_examples = self.get_alpha_lines(chatter_id)
#             print('a ----', alpha_examples)
#             print('b ----', beta_examples)      
            # match the two
            if(all(x in alpha_examples for x in beta_examples)):
#                 print(chatter_id)
#                 print('a ----', alpha_examples[0])
#                 print('b ----', beta_examples[0])
                self.user_df = self.user_df.astype('object')
                self.user_df.at[beta_user_idx, 'alpha_chatter_id'] = chatter_id
                return True

    
    def match_many(self, conv_idx, beta_contact_name, proposed_chatter_ids, beta_contact_int):
        beta_user_idx = str(conv_idx) + '_' + str(beta_contact_int)
        self.manual_df.at[beta_user_idx, '_'] = 0
        for n, chatter_id in enumerate(proposed_chatter_ids):
            match = self.match_one(conv_idx,beta_contact_name,chatter_id,beta_contact_int)
            if match:
                self.manual_df.drop([beta_user_idx], inplace=True)
                break
            else:
                self.manual_df.at[beta_user_idx, 'conv_id'] = conv_idx
                # self.manual_df.at[conv_idx, 'source'] = self.conv_df[conv_idx]['source']
                self.manual_df.at[beta_user_idx, 'contact name'] = beta_contact_name

                self.manual_df.at[beta_user_idx, 'user_%s_proposed_chatter_id_%s' % (beta_contact_int, n)] = str(chatter_id)
                self.manual_df.at[beta_user_idx, 'user_%s_proposed_alpha_name_%s' % (beta_contact_int, n)] = self.alpha_key_reversed[chatter_id]
    #                 self.manual_df.at[idx, 'proposed_examples_%s' % _n] = str(self.alpha_df.loc[chatter_id]['post'])
    
    def run(self):
        with tqdm(total=self.proposal_df.shape[0]) as pbar:
            for conv_idx, row in tqdm(self.proposal_df.iterrows()):
                for n, beta_contact_name in enumerate(row['users']):
                    beta_user_idx = str(conv_idx) + '_' + str(n)

                    self.user_df.at[beta_user_idx, 'beta_contact_name'] = beta_contact_name

                    proposed_chatter_ids = ast.literal_eval(row['user_%s_keys' % n])

                    # instance with no matches in key
                    if len(proposed_chatter_ids) == 0:
                        self.match_none(conv_idx, beta_contact_name, n)

                    # instances with only one match
                    if len(proposed_chatter_ids) == 1:
                        self.match_one(conv_idx,beta_contact_name, proposed_chatter_ids[0], n)

                    # instances with multiple matches
                    if len(proposed_chatter_ids) > 1:
                        self.match_many(conv_idx, beta_contact_name, proposed_chatter_ids, n)
                    
                    pbar.update(1/len(row['users']))


