import re
import difflib
import itertools
import pandas as pd

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
            filename = filename.split('/')[1]
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
