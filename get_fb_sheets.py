import pandas as pd
import json
import numpy as np
import itertools
from tqdm import tqdm

from beta import fb_beta
from beta import betaData
from alpha import alphaData
from alpha import proposeUsers, matchDataSets


output_dir = '/home/burtenshaw/data/teen/beta/facebook/play/'

with open('/home/burtenshaw/data/teen/raw/facebook.json', 'r') as f:
    facebook_json = json.load(f)
# conversation_json = "/home/burtenshaw/data/teen/raw/whatsapp.json"
with open('/home/burtenshaw/data/teen/alpha/redo/key.json') as f:
    alpha_key = json.load(f)

file_path = "/home/burtenshaw/data/teen/alpha/lisa_annon.txt"
alpha = alphaData(file_path, alpha_key=alpha_key)
alpha.run()

latest_csv = '/home/burtenshaw/data/teen/beta/facebook/cleaning/facebook_lines_clean_2.csv'
latest_csv = pd.read_csv(latest_csv)

beta = fb_beta(conversation_json=facebook_json, line_csv=latest_csv[:100], alpha_object=alpha)

beta.line_df.to_csv(output_dir + 'fb_line_df.csv')
beta.conv_df.to_csv(output_dir + 'fb_conv_df.csv')
beta.user_df.to_csv(output_dir + 'fb_user_df.csv')

proposal_df = pd.DataFrame(columns=['contact_name','proposed_chatter_ids', 'proposed_names'])

# In[ ]:
for contact_idx, row in beta.user_df.iterrows():
    p = proposeUsers(row['user_name'], alpha)
    proposal_df = proposal_df.astype('object')
    proposal_df.at[contact_idx, 'contact_name'] = row['user_name']
    proposal_df.at[contact_idx, 'proposed_chatter_ids'] = list(itertools.chain.from_iterable([x[1] for x in p.validated_names.items()]))
    proposal_df.at[contact_idx, 'proposed_names'] = list(p.validated_names.keys())
    if row.AS_ALPHA_chatter_id in list(alpha.user_df.index) and row.AS_ALPHA_chatter_id not in proposal_df.proposed_chatter_ids[contact_idx]:
        proposal_df.proposed_chatter_ids[contact_idx].append(row.AS_ALPHA_chatter_id)

proposal_df.to_csv(output_dir + 'fb_proposal_df.csv')


beta.contact_df = beta.user_df
m = matchDataSets(alpha, beta, proposal_df, params={'sample':10,'intersection':0.7})
m.run()

m.contact_df.to_csv(output_dir+'fb_matches.csv')
m.manual_df.to_csv(output_dir+'fb_manual.csv')