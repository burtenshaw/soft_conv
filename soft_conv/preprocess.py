import re
import json
import os
from datetime import datetime
from dateutil import parser
from tqdm import tqdm

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
                 school=True,
                 pattern_array=[],
                 in_one = False):
        print('Data Directory: ', data_dir)
        self.dir = data_dir
        self.data = {}
        self.school = school
        self.paths = self.load()
        print('N .txt files: ', len(self.paths))
        self.out_dir = out_dir
        print('Output Location: ', out_dir)
        self.remove_names = remove_names
        self.save_key = save_key

        # process
        self.in_one = in_one
        self.pattern = pattern
        self.pattern_array = pattern_array
        self.errors = []
        self.pattern_distribution = defaultdict(list)
    
    # utility functions
    def load(self):
        if self.school:
            dir_of_schools = os.listdir(self.dir)
            all_files = []
            for school in dir_of_schools:
                school_path = self.dir+'/'+school+'/'
                if os.path.isdir(school_path):
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
        try:
            result = re.match(pattern, filename)
            return result.groupdict()
        except AttributeError:
            print("Filename unrecognised: ", filename)
    
    def anon_filenames(self,filename):
        return filename
    
    def fileIter(self):
        for self.conv_n, f in enumerate(tqdm(self.paths)):
            self.file = f
            self.data[self.conv_n] = self.conversation(f)
            if self.conv_n % 150 == 0:
                for k, i in self.pattern_distribution.items():
                    print(k, ':  ', len(i))
    
    def line(self, line, n_line):
        date, user, text = line['date'], line['user'], line['text']
        try:
            utc = int(parser.parse(date).timestamp())
        except:
            utc = None
        
        try:
            raw_message = line['raw_message']
        except KeyError:
            raw_message = ''

        return {"conv_n":self.conv_n,
                "line_n" : n_line, 
                "utc":utc, 
                "user":user, 
                "text":text, 
                "raw_date":date,
                "raw_message": raw_message,
                "source":self.file
                }

    def regex_file(self, file):
        r = re.compile(self.pattern)
        with open(file, 'r', encoding="utf-8") as f:
            doc = [m.groupdict() for m in r.finditer(f.read())]
        return doc

    def by_date(self, file, patterns=None):
        if patterns == None:
            patterns = self.pattern_array
        with open(file, 'r', encoding="utf-8") as f:
            conv = f.read()
 
        date_split_text = [conv]

        for pat_n, r in enumerate(patterns):
            for n,t in enumerate(date_split_text):
                _split = r.split(t)
                if len(_split) >= 1:
                    split = [c for c in _split if not c.isspace() and len(c) != 0]
                    date_split_text[n:n+len(split)] = split
                    break
        
        raw_lines = []

        for n, line in enumerate(date_split_text):
            if patterns[0].match(line) or n == 0:
                raw_lines.append({'line_n':n,'date':line, 'text':'', 'user': ''})
            elif len(line) > 0 and line.isspace() == False:
                
                while line.startswith(('\n',' ','\t')):
                    line = line[1:]
                while line.endswith(('\n', ' ','\t')):
                    line = line[:-1]
                
                if len(line) > 0 and not line.isspace():
                    try:
                        raw_lines[-1]['raw_message'] = line
                        _line = [x for x in line.split('\n') if x != '\n']
                        try:
                            raw_lines[-1]['user'] = _line[0]
                            raw_lines[-1]['text'] = ' '.join(_line[1:])
                        except:
                            pass

                    except IndexError:
                        pass
        self.file_pattern = 'by_date_' + str(pat_n)        
            
        return raw_lines

    def by_line_break(self, file):
        with open(file, 'r', encoding="utf-8") as f:
            conv = f.read()
            lines = conv.split('\n')
        r = self.pattern_array[0]
        raw_lines = []
        for n, line in enumerate(lines):
            if r.match(line) or n == 0:
                raw_lines.append({'line_n':n,'date':line, 'text':'', 'user': ''})
            elif len(line) > 0 and line.isspace() == False:
                raw_lines[-1].extend({'line_n':n,'date':'', 'text':line, 'user': ''})
        self.file_pattern = 'on_line_break'
        return raw_lines

    def conversation(self, file):
        
        if self.in_one:
            # try to regex the entire file and break the file up into separate coversation exchanges:
            doc = self.regex_file(file)
            self.file_pattern = 'in_one'
        else:
            doc =[]

        # If that fails, use a scale of date detectors to split the file up on date
        if len(doc) == 0 or self.in_one == False:
            doc = self.by_date(file)

        # if all of the patterns fail, use line breaks.
        if len(doc) == 0:
            doc = self.by_line_break(file)
            
        # if line breaks fail, log the empty conv
        if len(doc) == 0:
            self.errors.append(file)
            self.file_pattern = 'no_match'

        self.lines = lines = [self.line(l, n) for n, l in enumerate(doc)]

        users, users_seq = self.users(lines)

        if self.remove_names:
            lines, users_key = self.anon(lines, users)
            users, users_seq = self.users(lines)

        self.pattern_distribution[self.file_pattern].append(self.conv_n)

        # date_range = [lines[0]['utc'], lines[-1]['utc']]
        return {"lines":lines, 
                "user_seq":users_seq, 
                "users":users, 
                # "date_range":date_range,
                "source": file,
                "file_pattern":self.file_pattern
                # "users_key": users_key
                }
    
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
        self.fileIter()
        print("saving data")
        self.save()
        print("empty conversation errors", len(self.errors))

        print("patterns used: ")
        for k, i in self.pattern_distribution.items():
            print(k, ':  ', len(i))
        
    def save(self):
        with open(self.out_dir, 'w') as f:
            json.dump(self.data,f)
        with open('empty_convs.json', 'w') as f:
            json.dump(self.errors,f)
#         self.csv = True
#         if self.csv:
#             self.make_csv()


class whatsApp(instantMessage):
    ''' 
        whatsapp conversation should work using the standard instant message class 
    '''
    pass


class facebook(instantMessage):
    ''' 
        Due to the periodic structuring of facebook conversations, it's useful to handle them in their own way.
        This allows us to also get separate coversations instances, defined by time.
    '''
    
    def regex_file(self, file):
        # print("parsing file: ", file)
        r = re.compile(self.pattern['conv'])
        with open(file, 'r', encoding="utf-8") as f:
            conv = ''.join([m.groupdict()['exchange'] for m in r.finditer(f.read())])
        self.file_pattern = 'conv'
        return conv





