import json
import pandas as pd
import re
from tqdm import tqdm

facebook_json = '/home/burtenshaw/data/teen/raw/facebook.json'
clean_csv = '/home/burtenshaw/data/teen/raw/clean_facebook_2.csv'

with open(facebook_json, 'r') as f:
    data = json.load(f)


# In[ ]:




# In[5]:

df = pd.DataFrame.from_dict(data, orient='index')


# In[6]:

patterns = df.groupby(['file_pattern'])


# In[7]:

list_of_df = [[n,x[0],x[1]] for n,x in enumerate(patterns)]


# In[9]:

date_pattern = re.compile(r"(?P<date>(?:(?:[0-3][0-9])|(?:[0-9]))(?:\/|\-|\.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:\/|\-|\.)(?:\d{2}|\d{4})(?:,|) (?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))")


patterns = {"line_date": r"(?P<date>(?:(?:[0-3][0-9])|(?:[0-9]))(?:\/|\-|\.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:\/|\-|\.)(?:\d{2}|\d{4})(?:,|) (?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))",
            "multi_date" : [
                re.compile(r"(?P<date>(?:(?:[0-3][0-9])|(?:[0-9]))(?:\/|\-|\.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:\/|\-|\.)(?:\d{2}|\d{4})(?:,|) (?:[0-9]|[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am| |\:[0-5][0-9]|))"),
                           re.compile(r"(?P<date>(?:(?:[0-3][0-9])|(?:[0-9]))(?:.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:.)(?:\d{2}|\d{4})(?:.{0,4})(?:[0-2][0-9]).(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|\w))"),
                           re.compile(r"(?P<date>(?:(?:[0-3][0-9])|(?:[0-9]))(?:\/|\-|\.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:\/|\-|\.)(?:\d{2}|\d{4})(?:,|) (?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))"),
                           re.compile(r"(?P<date>(?:(?:[0-3][0-9])|(?:[0-9]))(?:.)(?:(?:(?:0|)[0-9])|(?:(?:1)[0-2]))(?:.)(?:\d{2}|\d{4})(?:.*))"),
                           re.compile(r"(?P<date>(?:(?:[0-3][0-9])|(?:[0-9]))(?:.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:.)(?:\d{2}|\d{4})(?:.*))"),
                           re.compile(r"(?P<date>(?:(?:[0-3][0-9])|(?:[0-9]))(?:.)(?:(?:[0-3][0-9]))(?:.)(?:\d{2}|\d{4})(?:.{0,4})(?:[0-2][0-9]).*)"),
                           re.compile(r"(.*(?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))"),
                           re.compile(r"(.*(?:[0-2][0-9])\:(?:[0-5][0-9]))")
                           ]}


# In[21]:
def extra_words(a, b, s='\n'):
    return list(set(a.split(s)) - set(b.split(s)))

def tidy_users(users):
    _ = [u.replace('\n', '') for u in users if len(u) > 1 and u.isspace() == False]
    _ = list(dict.fromkeys(_))
    return _

def split(delimiters, string, maxsplit=0):
    import re
    regexPattern = '(?:'+'|'.join(map(re.escape, delimiters))+')'
    return re.split(regexPattern, string, maxsplit)
    
def check_on_all_patterns(t, patterns=patterns['multi_date']):
    conv = []
    for dp in patterns:
        date_split_text = dp.split(t)
        if len(date_split_text) > 1:
            t = date_split_text[0]
            conv = date_split_text[1:]
            break
    return t, conv, dp

def get_user(raw, users):
    t = raw
    user = 'unfound'
    for u in users:
        if raw.startswith(u):
            user = u
            t = raw.replace(u,'')
            break
    return t, user

def wrap_line(t, users, dp, conv_n):
    if dp.match(t):
        raw_date = t
    else:
        raw_date = 'unfound'
    raw, conv, dp = check_on_all_patterns(t)
    t, user = get_user(t, users)
    if t != raw_date and t.isspace() == False and len(raw) > 0 and len(t) > 0:
        return {'conv_n' :conv_n, 'line_n':'_','raw_date':raw_date, 'raw_message':raw, 'text':t, 'user': user}
    else:
        return {}

_lines = []
_convs = []
nousers = 0
for p_df in list_of_df  :
    pattern_name = p_df[1]
    _df = p_df[2]
    print(pattern_name)
#     if pattern_name == 'multi_line0':
    for conv_n in tqdm(_df.index):
#         print(idx)
        lines = data[conv_n]['lines']
        users = tidy_users(data[conv_n]['users'])
        for l in lines:
            _l = {}
            t = l['text']
            raw = l['raw_message']
            conv_n = l['conv_n']
            try:
                user = l['user']
            except KeyError:
                user = 'unfound'
            if len(t) == 0:
                if set(l['raw_message'].split('\n')).issubset(users) == False:
                    for u in users:
                        raw = str(raw).replace(u,'')
                    if raw.isspace() == False:
                        t = raw
                        while t.startswith('\n'):
                            t = t[1:]
                        if raw.isspace() == False and len(raw) > 0: 
                            _l.update(l)
                            _l['text'] = t
                            _lines.append(_l)
            elif len(t) > 1 and t.isspace() == False:
                t, conv, dp = check_on_all_patterns(t)
                l['text'] = t
                _lines.append(l)
                if len(conv) > 1:
                    for t in conv:
                        _lines.append(wrap_line(t, users, dp, conv_n))
                        if len(conv) > 1:
                            for t in conv:
                                _lines.append(wrap_line(t, users, dp, conv_n))
                        elif len(conv) == 1:
                            t = conv[0]
                            _lines.append(wrap_line(t, users, dp, conv_n))
                elif len(conv) == 1:
                    t = conv[0]
                    _lines.append(wrap_line(t, users, dp, conv_n))
                                    
line_df = pd.DataFrame(_lines)
line_df = pd.DataFrame(_lines)
line_df.to_csv(clean_csv)
