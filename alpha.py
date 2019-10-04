import re
import difflib
import itertools
import pandas as pd
import json

class alphaData:
    def __init__(self, src_path, names):
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
        
        self.user_df = user_df

    def make_line_df(self):
        self.line_df = self.df[self.names['line_fields']]
    
    def run(self):
        self.make_line_df()
        self.make_user_df()
    
    def save(self, output_dir):
        self.line_df.to_csv(output_dir+"alpha_lines.csv")
        self.user_df.to_csv(output_dir+"alpha_users.csv")

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
    def __init__(self, alpha_df, beta_df, alpha_key, conv_df):
        self.alpha_df, self.beta_df, self.conv_df = alpha_df, beta_df, conv_df
        self.alpha_key_reversed, self.alpha_key = self._reverse_key(), alpha_key
        self.manual_df = pd.DataFrame()

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

    # matching instances

    def match_none(self, conv_idx, beta_contact_name, beta_contact_int):
        conv_lines = [line['text'] for line in self.beta_df[int(conv_idx)] if type(line) == dict and line['user'] == beta_contact_name]
        if len(conv_lines) > 3:
            conv_lines.sort(key=len, reverse=True)
            beta_examples = conv_lines[:3]
        else:
            beta_examples = conv_lines

        matches = []

        for alpha_idx, row in self.alpha_df.iterrows():
            if row['post'] in beta_examples:
                matches.append(row['chatter_ID'])
        
        self.match_many(conv_idx, beta_contact_name, matches, beta_contact_int)
        
    def match_one(self, conv_idx, beta_contact_name, chatter_id):
        conv_lines = [line['text'] for line in self.beta_df[int(conv_idx)] if type(line) == dict and line['user'] == beta_contact_name]
        if len(conv_lines) > 3:
            conv_lines.sort(key=len, reverse=True)
            beta_examples = conv_lines[:3]
        else:
            beta_examples = conv_lines
        # get line form alpha
        try:
            alpha_examples = list(self.alpha_df.loc[chatter_id]['post'])
        except KeyError:
            return 0
        if(all(x in alpha_examples for x in beta_examples)):
            return str(chatter_id)
        else:
            return 0
    
    def match_many(self, conv_idx, beta_contact_name, proposed_chatter_ids, beta_contact_int):
        self.manual_df.at[conv_idx, 'conv_id'] = conv_idx
        self.manual_df.at[conv_idx, 'source'] = self.beta_df[int(conv_idx)]['source']
        self.manual_df.at[conv_idx, 'contact name'] = beta_contact_name
        
        matches = []

        for n, chatter_id in enumerate(proposed_chatter_ids):
            self.manual_df.at[conv_idx, 'user_%s_proposed_chatter_id_%s' % (beta_contact_int, n)] = str(chatter_id)
            self.manual_df.at[conv_idx, 'user_%s_proposed_alpha_name_%s' % (beta_contact_int, n)] = self.alpha_key_reversed[chatter_id]
#                 manual_df.at[idx, 'proposed_examples_%s' % _n] = str(alpha_line_df.loc[k]['post'])
            match = self.match_one(conv_idx,beta_contact_name,chatter_id)
            matches.append(match)
        
        for n, chatter_id in enumerate(matches):
            self.manual_df.at[conv_idx, 'user_%s_match_%s_chatter_id' % (beta_contact_int, n)] = chatter_id
            self.manual_df.at[conv_idx, 'user_%s_match_%s_alpha_name' % (beta_contact_int, n)] = self.alpha_key_reversed[chatter_id]