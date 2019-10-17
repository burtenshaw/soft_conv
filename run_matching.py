import pandas as pd
import json
import ast 
from tqdm import tqdm
import numpy as np

from alpha import alphaData
from alpha import proposeUsers
from alpha import matchDataSets
from alpha import betaData


# In[ ]:

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


file_path = "/home/burtenshaw/data/teen/alpha/lisa_annon.txt"
alpha = alphaData(file_path, names)
alpha.run()


# # Load key
# 
# There may be short comings in this key.

# In[ ]:

with open("/home/burtenshaw/data/teen/alpha/redo/clean_key.json", 'r') as f:
    alpha_user_key = json.load(f)
# In[ ]:

conversation_json = "/home/burtenshaw/data/teen/raw/whatsapp.json"
beta = betaData(conversation_json)
# In[ ]:

proposal_df = beta.conv_df.astype('object')
for idx, row in beta.conv_df.iterrows():
    users = [str(u) for u in row['users']]
    p = proposeUsers(users, alpha_user_key, row['source'], pattern['filename'], alpha.user_df)
    proposal_df.at[idx,'n_users'] = len(row['users'])
    for n, u in enumerate(users):
        proposal_df = proposal_df.astype('object')
        proposal_df.at[idx, 'user_%s' % (n)] = str(u)
        proposal_df.at[idx,'user_%s_keys' % (n)] = str(p.validated_names[u]['keys'])
        proposal_df.at[idx, 'user_%s_proposed' % (n)] = str(p.proposed_names[u])
    if p.f_data:
        proposal_df.at[idx, 'path'] = p.f_data['path']
        proposal_df.at[idx, 'school'] = p.f_data['school']
        proposal_df.at[idx, 'year'] = p.f_data['year']
        proposal_df.at[idx, 'medium'] = p.f_data['medium']
        proposal_df.at[idx, 'privacy'] = p.f_data['private']
        proposal_df.at[idx, 'source_user'] = p.f_data['name']


# In[ ]:


m = matchDataSets(alpha, beta, alpha_user_key, proposal_df)
m.run()

m.user_df.to_csv('/home/burtenshaw/data/teen/beta/matching/beta_user.csv')
m.manual_df.to_csv('/home/burtenshaw/data/teen/beta/matching/beta_manual.csv')