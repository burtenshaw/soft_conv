#%%
import re
import json
import os
from datetime import datetime
from dateutil import parser
import argparse
#%%
class whatsApp:
    """ process whatsapp conversations into a json, maintain conversation and user structure
    use 'remove_names' to remove all the names from lines
    use 'save_key' to store a key in each file to return real users. WARNING: Not anonymous. 
    """
    def __init__(self, data_dir="data/", out_dir="output_file.json", remove_names=True, save_key=False, debug=False):
        self.dir = data_dir
        self.paths = self.load()
        self.out_dir = out_dir
        self.remove_names = remove_names
        self.save_key = save_key
        self.debug = debug

    def load(self):
        return [self.dir + x for x in os.listdir(self.dir) if x[-4:] == ".txt"]

    def users(self, lines):
        users_seq = [l['user'] for l in lines]
        users = list(set(users_seq))
        return [users, users_seq]

    def startsWithDate(self, s):
        pattern = '^[0-9]+(\/|-|\.)(((0)[0-9])|((1)[0-2]))(\/|-|\.)(\d{2}|\d{4}), ([0-9][0-9]):([0-9][0-9])'
        result = re.match(pattern, s)
        return result
    
    def line(self, line):
        date = self.startsWithDate(line)
        if date:
            utc = int(parser.parse(date.group(0)).timestamp())
            user, text = line[len(date.group(0))+1:].split(":", 1)
            print(user)
            return {"utc":utc, "user":user, "text":text}
        else:
            return str(line)

    def conversation(self, f):
        _f = open(f)
        if self.debug:
            [self.lineDebug(l) for l in _f]
        else:
            lines = {}
            for n, l in enumerate(_f):
                _l = self.line(l)
                if type(_l) == dict:
                    lines[n] = _l
                    x = n
                else:
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
                    "source": f,
                    "users_key": users_key}

    def anon(self, lines, users):
        users_key = {u:n for n,u in enumerate(users)}
        for l in lines:
            l['user'] = users_key[l['user']]
        if not self.save_key:
            users_key={}
        return lines, users_key

    def fileIter(self):
        return {n: self.conversation(f) for n, f in enumerate(self.paths)}
    
    def run(self):
        data = self.fileIter()
        with open(self.out_dir, 'w') as f:
            json.dump(data,f)
    
    def lineDebug(self, line):
        try:
            self.startsWithDate(line)
        except:
            print("starts with error \n PRIVATE LINE:  ", line)
        try:
            int(parser.parse(date.group(0)).timestamp())
        except:
            print("date error: \n RIVATE LINE:  ", line)
        try:
            user, text = line[len(date.group(0))+1:].split(":", 1)
        except:
            print("user/text split error \n PRIVATE LINE:  ", line)
    


if __name__== "__main__":

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--debug", help="get more info and examples from data errors.", action="store_true")
    args = argparser.parse_args()

    if args.debug:
        w = whatsApp(debug=True)
    else:
        w = whatsApp()

    w.run()