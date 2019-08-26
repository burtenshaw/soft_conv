import re
import json
import os
from datetime import datetime
from dateutil import parser
import argparse


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

    def fileIter(self):
        return {n: self.conversation(f) for n, f in enumerate(self.paths)}
    
    def line(self, line, n_line):
        date, user, text = line['date'], line['user'], line['text']
        try:
            utc = int(parser.parse(date).timestamp())
        except:
            utc: None
        return {"line" : n_line, 
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
    
    def run(self):
        """ define approach and run """
        data = self.fileIter()
        with open(self.out_dir, 'w') as f:
            json.dump(data,f)

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
    
    def line(self, line, n_line):
        try:
            line = re.match(self.pattern, line).groupdict()
            self.make_line(line, n_line)
        except:
            return str(line)

    def conversation(self, file):
        print("parsing file: ", file)
        doc = list(open(file, 'r', encoding="utf-8"))
        self.validate_date_pattern(doc[0])
        lines = {}
        for n, l in enumerate(doc):
            _l = self.line(l, n)
            if type(_l) == dict:
                lines[n] = _l
                x = n
            elif type(_l) == str:
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
    pass

patterns = {"date": ["(?P<date>(?:(?:[0-3][0-9])|(?:[0-9]))(?:\/|\-|\.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:\/|\-|\.)(?:\d{2}|\d{4})(?:,|) (?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))(?:\:\ |\ \-\ )(?P<user>.+?)(?:\:)(?P<text>.*)"],
            "one" : "(?# get date)(?P<date>(?:(?:[0-3][0-9])|(?:[0-9]))(?:\/|\-|\.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:\/|\-|\.)(?:\d{2}|\d{4})(?:,|) (?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))(?:\:\ |\ \-\ )(?# get user)(?P<user>.+?)(?:\:)(?# get text)(?P<text>(.|\r|\n?|\n)+?(?=(?:(?# next date or end of the doc)(?:(?:[0-3][0-9])|(?:[0-9]))(?:\/|\-|\.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:\/|\-|\.)(?:\d{2}|\d{4})(?:,|) (?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))|(?# end of doc)\Z))"
}

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