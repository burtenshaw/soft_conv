import pandas as pd
import json
import ast 
from tqdm import tqdm
import numpy as np

from alpha import alphaData
from alpha import proposeUsers
from alpha import matchDataSets
from alpha import betaData

file_path = "/home/burtenshaw/data/teen/alpha/lisa_annon.txt"
alpha = alphaData(file_path)
alpha.run()

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


# In[ ]:


m = matchDataSets(alpha, beta, proposal_df)
m.run()

m.user_df.to_csv('/home/burtenshaw/data/teen/beta/matching/beta_contact.csv')
m.manual_df.to_csv('/home/burtenshaw/data/teen/beta/matching/beta_manual.csv')