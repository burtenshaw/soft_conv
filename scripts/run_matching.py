import os
try:
	os.chdir(os.path.join(os.getcwd(), '../'))
	print(os.getcwd())
except:
	pass

import pandas as pd
import json
import itertools
import numpy as np

from alpha import alphaData
from alpha import proposeUsers
from alpha import matchDataSets
from beta import betaData


# prepare alpha_data

alpha = alphaData(src_path="/home/burtenshaw/data/teen/alpha/lisa_annon.txt")
alpha.run()

with open('/home/burtenshaw/data/teen/alpha/redo/key.json') as f:
    alpha.key = json.load(f)

alpha.make_user_df()

# prepare beta_data

conversation_json = "/home/burtenshaw/data/teen/raw/whatsapp.json"
beta = betaData(conversation_json, alpha_key=alpha.key)


proposal_df = pd.DataFrame(columns=['contact_name','proposed_chatter_ids', 'proposed_names'])

for contact_idx, row in beta.contact_df.iterrows():
    p = proposeUsers(row['contact_name'], alpha)
    proposal_df = proposal_df.astype('object')
    proposal_df.at[contact_idx, 'contact_name'] = row['contact_name']
    proposal_df.at[contact_idx, 'proposed_chatter_ids'] = list(itertools.chain.from_iterable([x[1] for x in p.validated_names.items()]))
    proposal_df.at[contact_idx, 'proposed_names'] = list(p.validated_names.keys())
    if row.AS_ALPHA_chatter_id in list(alpha.user_df.index) and row.AS_ALPHA_chatter_id not in proposal_df.proposed_chatter_ids[contact_idx]:
        proposal_df.proposed_chatter_ids[contact_idx].append(row.AS_ALPHA_chatter_id)

m = matchDataSets(alpha, beta, proposal_df, params={'sample':10,'intersection':0.7})
m.run()

m.contact_df.to_csv('/home/burtenshaw/data/teen/beta/matching/beta_contact.csv')
m.manual_df.to_csv('/home/burtenshaw/data/teen/beta/matching/beta_manual.csv')