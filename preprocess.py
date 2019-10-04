import re
import json
import os
from datetime import datetime
from dateutil import parser

# import pandas as pd
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
                 debug=True,
                 school=True):
        print('Data Directory: ', data_dir)
        self.dir = data_dir
        self.school = school
        self.paths = self.load()
        print('N .txt files: ', len(self.paths))
        self.out_dir = out_dir
        print('Output Location: ', out_dir)
        self.remove_names = remove_names
        self.save_key = save_key
        self.pattern = pattern
        
    
    # utility functions
    def load(self):
        if self.school:
            dir_of_schools = os.listdir(self.dir)
            all_files = []
            for school in dir_of_schools:
                school_path = self_dir+'/'+school+'/'
                all_files.extend([school_path + x for x in os.listdir(school_path) if x[-4:] == ".txt"])
        else:
            all_files =  [self.dir + x for x in os.listdir(self.dir) if x[-4:] == ".txt"]
        return all_files

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
            utc = None

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
        else:
            users_key = users
            users, users_seq = self.users(lines)
        
        # date_range = [lines[0]['utc'], lines[-1]['utc']]
        return {"lines":lines, 
                "user_seq":users_seq, 
                "users":users, 
                # "date_range":date_range,
                "source": file,
                "users_key": users}  
    
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

    ''' 
    Slower class that iterates over text files per line.
    Requires seperate date, line, and conversation patterns
    '''

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
    ''' 
        whatsapp conversation should work using the standard instant message class 
    '''
    pass

class facebook(instantMessage):
    ''' 
        Due to the periodic structuring of facebook conversations, it's useful to handle them in their own way.
        This allows us to also get seperate coversations instances, defined by time.
    '''
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
