import re
import json
import os
from datetime import datetime
from dateutil import parser
import argparse

import pandas as pd
from collections import defaultdict
import itertools
import difflib

class instantMessage:
    """ process whatsapp conversations into a json, maintain conversation and user structure
    use 'remove_names' to remove all the names from lines
    use 'save_key' to store a key in each file to return real users. WARNING: Not anonymous. 
    """
    def __init__(self,
                 pattern=dict(),
                 data_dir="data/", 
                 out_dir="output_file.json", 
                 remove_names=True, 
                 save_key=False, 
                 debug=True):
        self.dir = data_dir
        self.paths = self.load()
        self.out_dir = out_dir
        self.remove_names = remove_names
        self.save_key = save_key
        self.pattern = pattern
    
    # utility functions
    def load(self):
        return [self.dir + x for x in os.listdir(self.dir) if x[-4:] == ".txt"]

    def users(self, lines):
        # TODO rewrite to encorporte alpha user key
        users_seq = [l['user'] for l in lines]
        users = list(set(users_seq))
        return [users, users_seq]

    def anon(self, lines, users):
        users_key = {u:n for n,u in enumerate(users)}
        for l in lines:
            l['user'] = users_key[l['user']]
        if not self.save_key:
            users_key={}
        return lines, users_key

    def grab_filename(self, filename, pattern):
        result = re.match(pattern, filename)
        return result.groupdict()
    
    def anon_filenames(self,filename):
        return filename
    
    def fileIter(self):
        return {self.conv_n: self.conversation(f) for self.conv_n, f in enumerate(self.paths)}
    
    def line(self, line, n_line):
        date, user, text = line['date'], line['user'], line['text']
        try:
            utc = int(parser.parse(date).timestamp())
        except:
            utc: None
        return {"conv_n":self.conv_n,
                "line_n" : n_line, 
                "utc":utc, 
                "user":user, 
                "text":text, 
                "raw_date":date}

    # single regex
    def conversation(self, file):
        """Approach using a single regex"""
        print("parsing file: ", file)
        r = re.compile(self.pattern)
        with open(file, 'r', encoding="utf-8") as f:
            doc = [m.groupdict() for m in r.finditer(f.read())]
        lines = [self.line(l, n) for n, l in enumerate(doc)]
        users, users_seq = self.users(lines)
        if self.remove_names:
            lines, users_key = self.anon(lines, users)
            users, users_seq = self.users(lines)
        
        # date_range = [lines[0]['utc'], lines[-1]['utc']]
        return {"lines":lines, 
                "user_seq":users_seq, 
                "users":users, 
                # "date_range":date_range,
                "source": file,
                "users_key": users_key}  
    
    def user_data(self):
        return {user:{'lines': [[line['conv_n'], line['line_n'], line['utc']] 
                       for line in self.lines_d]} 
                       for user in self.users(self.lines_d)[0]}
    
    def line_data(self):
        return [line for _, conv in self.data.items() for line in conv['lines']]
    
    def conversations_data(self):
        return [[l['line_n'] for l in conv['lines']] for _, conv in self.data.items()]
    
    def separate_data(self):
        self.lines_d = self.line_data()
        self.conversations_d = self.conversations_data()
        self.user_d = self.user_data()
        for d in [['lines',self.lines_d], 
                  ['conversations',self.conversations_d], 
                  ['users',self.user_d]]:
            self.out_dir = d[0] + ".json"
            self.data = d[1]
            self.save()
            
    def run(self):
        print("iterating over files")
        self.data = self.fileIter()
        print("saving data")
        self.save()
        
    def save(self):
        with open(self.out_dir, 'w') as f:
            json.dump(self.data,f)
#         self.csv = True
#         if self.csv:
#             self.make_csv()

class lineByline(instantMessage):

    def validate_date_pattern(self, line):
        for p in self.patterns['date']:
            try:
                date, user, text = self.reg_line(line, p)
                print("Regex pattern validated: ", 
                      "\n date ",date,
                      "\n user ", user,
                      "\n text ", text)
                utc = int(parser.parse(date).timestamp())
                print("Date parse validated: ", utc)
                self.pattern = p
                break
            except:
                print("Broken pattern")
                pass

    def conversation(self, file):
        print("parsing file: ", file)
        doc = list(open(file, 'r', encoding="utf-8"))
        self.validate_date_pattern(doc[0])
        
        lines = {}
        for n, l in enumerate(doc):
            try:
                self.line(re.match(self.pattern, line).groupdict(), n)
                lines[n] = _l
                x = n
            except:
                lines[x]['text'] += _l
                
        lines = [l[1] for l in lines.items()]  
        users, users_seq = self.users(lines)
        if self.remove_names:
            lines, users_key = self.anon(lines, users)
            users, users_seq = self.users(lines)

        date_range = [lines[0]['utc'], lines[-1]['utc']]
        return {"lines":lines, 
                "user_seq":users_seq, 
                "users":users, 
                "date_range":date_range,
                "source": file,
                "users_key": users_key}    


class whatsApp(instantMessage):
    pass

class facebook(instantMessage):    
    def regex_file(self, file):
        print("parsing file: ", file)
        r = re.compile(self.pattern['conv'])
        with open(file, 'r', encoding="utf-8") as f:
            return ''.join([m.groupdict()['exchange'] for m in r.finditer(f.read())])

    def conversation(self, file):
        f = self.regex_file(file)
        r = re.compile(self.pattern['line'])
        doc = [m.groupdict() for m in r.finditer(f)]
        lines = [self.line(l, n) for n, l in enumerate(doc)]
        self.lines = lines    
        users, users_seq = self.users(lines)
        if self.remove_names:
            lines, users_key = self.anon(lines, users)
            users, users_seq = self.users(lines)

        date_range = [lines[0]['utc'], lines[-1]['utc']]
        return {"lines":lines, 
                "user_seq":users_seq, 
                "users":users, 
                "date_range":date_range,
                "source": file,
                "users_key": users_key}  

class alphaData:
    def __init__(self, src_path, names):
        self.src = src_path
        self.names = names
        self.load()

    def load(self):
        self.df = pd.read_csv(file_path, delimiter='\t', names=names['all'])
        
    def make_user_df(self):
        user_df = self.df[names['user_fields']]
        user_df = user_df.drop_duplicates(subset='chatter_ID', keep='first')
        user_df = user_df.set_index('chatter_ID')
        
        gp = self.df.groupby('chatter_ID', sort=False)
        user_df['lines_n'] = pd.Series(dict(gp.groups))
        
        self.user_df = user_df

    def make_line_df(self):
        self.line_df = self.df[names['line_fields']]
    
    def run(self):
        self.make_line_df()
        self.make_user_df()
    
    def save(self, output_dir):
        self.line_df.to_csv(output_dir+"alpha_lines.csv")
        self.user_df.to_csv(output_dir+"alpha_users.csv")

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

class proposeUsers:
    def __init__(self, users, users_list, filename, pattern, users_df, look_up=True):
        self.pattern, self.users_list , self.users, self.df, self.look_up = pattern, users_list, users, users_df, look_up
        self.f_data = self.grab_filename(filename)
        self.pos = self.possible_names()
        self.gold_pos = self.check_key()
        
    def grab_filename(self, filename):
        result = re.match(self.pattern, filename).groupdict()
        try:
            self.users.append(result['name'])
        except AttributeError:
            print("no name found in filename: ", filename)
        return result

    def possible_names(self):
        return {u : difflib.get_close_matches(u, self.users_list, n=3, cutoff=0.8) for u in self.users}
    
    def check_df(self, pos, df):
        for k, i in pos.items():
            for idx in i['keys']:
                try:
                    g = df.loc[idx].chatter_ID
                    pos[k]['record'] = g
                except KeyError:
                    pass
        return pos

    def check_key(self):
        gold_pos = {}
        for k, i in self.pos.items():
            gold_pos[k] = {'pos':i, 'keys' :list(itertools.chain.from_iterable([self.users_list[_n] for _n in i]))}
        if self.look_up:
            gold_pos = self.check_df(gold_pos, self.df)
        return gold_pos
    
patterns = {"date": ["(?P<date>(?:(?:[0-3][0-9])|(?:[0-9]))(?:\/|\-|\.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:\/|\-|\.)(?:\d{2}|\d{4})(?:,|) (?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))(?:\:\ |\ \-\ )(?P<user>.+?)(?:\:)(?P<text>.*)"],
            "one" : "(?# get date)(?P<date>(?:(?:[0-3][0-9])|(?:[0-9]))(?:\/|\-|\.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:\/|\-|\.)(?:\d{2}|\d{4})(?:,|) (?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))(?:\:\ |\ \-\ )(?# get user)(?P<user>.+?)(?:\:)(?# get text)(?P<text>(.|\r|\n?|\n)+?(?=(?:(?# next date or end of the doc)(?:(?:[0-3][0-9])|(?:[0-9]))(?:\/|\-|\.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:\/|\-|\.)(?:\d{2}|\d{4})(?:,|) (?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))|(?# end of doc)\Z))",
            'conv':"(?# get conversation date marker)(?P<conv>(?P<fb_date>(?P<_day>\d\d)(?:\s)(?P<_month>(?:[a-z|A_Z]{4,10}))\s(?P<_year>(?:[0-9]{4}))))(?:\n.*\n)(?P<exchange>(?:.*|\r|\n?|\n)+?(?=(?:(?:\d\d)\s(?:(?:[a-z|A_Z]{4,10}))\s(?:(?:[0-9]{4}))|\Z)))",
           'line': '(?# get the actual date)(?P<date>(?P<day>\d\d)\-(?P<month>(?:[0-2][0-9]))\-(?P<year>(?:[0-9]{4}))\s(?P<time>[0-9][0-9]\:[0-9][0-9]))\n(?# username)(?P<user>.*)\n(?# text)(?P<text>(?:.*|\r|\n?|\n)+?(?=(?:(?P<receiver>.*\n){1}(?# next date or end of the doc)(?:(?:[0-3][0-9])|(?:[0-9]))(?:\/|\-|\.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:\/|\-|\.)(?:\d{2}|\d{4})(?:,|) (?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))|(?# end of doc)\Z))'}

if __name__== "__main__":

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--debug", help="get more info and examples from data errors.", action="store_true")
    argparser.add_argument("--line", help="process the doc line by line", action="store_true")
    args = argparser.parse_args()

    if args.line:
        w = lineByline(pattern=patterns)
    else:
        w = whatsApp(patterns['one'])
    
    w.run()