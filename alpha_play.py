# To add a new cell, type '#%%'
# To add a new markdown cell, type '#%% [markdown]'

#%%
%load_ext autoreload
%autoreload 2

from alpha import alphaData
import pandas as pd
import json

from alpha import proposeUsers
#%%
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

#%%
pattern = {'conv':"(?# get conversation date marker)(?P<conv>(?P<fb_date>(?P<_day>\d\d)(?:\s)(?P<_month>(?:[a-z|A_Z]{4,10}))\s(?P<_year>(?:[0-9]{4}))))(?:\n.*\n)(?P<exchange>(?:.*|\r|\n?|\n)+?(?=(?:(?:\d\d)\s(?:(?:[a-z|A_Z]{4,10}))\s(?:(?:[0-9]{4}))|\Z)))",
           'line': '(?# get the actual date)(?P<date>(?P<day>\d\d)\-(?P<month>(?:[0-2][0-9]))\-(?P<year>(?:[0-9]{4}))\s(?P<time>[0-9][0-9]\:[0-9][0-9]))\n(?# username)(?P<user>.*)\n(?# text)(?P<text>(?:.*|\r|\n?|\n)+?(?=(?:(?P<receiver>.*\n){1}(?# next date or end of the doc)(?:(?:[0-3][0-9])|(?:[0-9]))(?:\/|\-|\.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:\/|\-|\.)(?:\d{2}|\d{4})(?:,|) (?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))|(?# end of doc)\Z))',
           'filename':'(?P<path>(?:.*))\/(?P<school>.*)\/(?P<year>\d{4})\_(?P<medium>.+)\_(?P<gender>same|mixed)\_(?P<private>private|group)\_(?P<name>.+)\.txt'}
#%%
file_path = "/home/burtenshaw/data/teen/alpha/lisa_annon.txt"
alpha = alphaData(file_path, names)
alpha.run()
#%%


#%%
user_df = alpha.user_df
#%%
line_df = alpha.line_df
#%%

filename = "/path/to/directory/school/2015_WhatsApp_same_private_kelly.txt"
users = ['Manon Pelli', 'J Verberckmoes']


df = user_df
# df.index = df['chatter_ID']

#%%
with open("/home/burtenshaw/data/teen/alpha/redo/clean_key.json", 'r') as f:
    key = json.load(f)

p = proposeUsers(users, key, filename, pattern['filename'], df)

pos = p.gold_pos

#%
#%%

with open("/home/burtenshaw/data/teen/raw_demo/original.json", 'r') as f:
    convs = json.load(f)


#%%

convs_df = pd.DataFrame.from_dict(convs)

#%%
for k, i in convs.items():
    users = i['users']
    filename = i['source']
    p = proposeUsers(users, key, filename, pattern['filename'], user_df)
    i['pos'] = p.gold_pos


#%%
convs['5']

matching = {}
#%%
for k, conv in convs.items():
    matching[k] = {}
    matching[k]['n_users'] = len(conv['users_key'])
    matching[k]['users_in_conv'] = {user: [] for user in conv['users_key']}
    if conv['pos']:
        pos = conv['pos']
        for user, i in pos.items():
            if len(i['keys']) == 1 and i['keys'][0] == i['record']:
                try:
                    print(i)
                    matching[k]['users_in_conv'][user].append(i['record'])
                except KeyError:
                    print(user)
    else:
        print('no match to alpha:', conv['source'])
#%%
m_df = pd.DataFrame.from_dict(matching['5'])

#%%
