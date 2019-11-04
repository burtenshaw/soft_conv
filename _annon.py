#%%#
import os
try:
	os.chdir(os.path.join(os.getcwd(), '/home/burtenshaw/code/2019/teen_conv'))
	print(os.getcwd())
except:
	pass

# coding: utf-8
import pandas as pd
import numpy as np
import json
from collections import defaultdict as dd
from tqdm import tqdm
tqdm.pandas()
import nl_core_news_sm
nlp = nl_core_news_sm.load()
import re
from utils import fuzzy_names, get_u_idx, check_text_for_user, check_text_for_locations, loc_idx
# Data paths 

output_dir = "/home/burtenshaw/data/teen/beta/combined/annon/"
line = "/home/burtenshaw/data/teen/beta/combined/combined_line.csv"
conv = "/home/burtenshaw/data/teen/beta/combined/combined_conv.csv"
user = "/home/burtenshaw/data/teen/beta/combined/combined_user.csv"
# resources

with open('/home/burtenshaw/data/teen/beta/usable_user_list.json', 'r') as f:
    all_users = json.load(f)

with open('/home/burtenshaw/data/teen/annon_files/gementes_improved.json', 'r') as f:
    gementes = json.load(f) 

with open('/home/burtenshaw/data/teen/annon_files/streets.json', 'r') as f:
    streets = json.load(f)


all_fuzzy_names = fuzzy_names(all_users)

manual_additions = ['hoboken']
vocab_gementes = [x for x in gementes if x in nlp.vocab and x not in manual_additions]

gementes.extend(streets)
vocab_gementes.extend([x for x in streets if x in nlp.vocab])

# get dataframes

df = pd.read_csv(line, index_col=0)
conv_df = pd.read_csv(conv, index_col=0)
user_df = pd.read_csv(user, index_col=0)

df = df.dropna(how='all')
df = df.dropna(subset=['text','raw_message'])
conv_df = conv_df.dropna(subset=['line_idxs'])

# annon : 
#%%#
print("Searching for local users in text ... ")
df['local_users'] = df.conv_idx.progress_apply(lambda x: fuzzy_names(conv_df.loc[x].users).keys())
df['annon_text'] = df.progress_apply(lambda x:check_text_for_user(x.text, x.local_users),axis=1)
#%%#

print("Saving...")
df.to_csv(output_dir+'lines_df_annon_user_local.csv')
#%%#
# ## External participants to the conversation
print("Searching for exterior users in text ... ")
df['annon_text'] = df.progress_apply(lambda x:check_text_for_user(x.annon_text, all_fuzzy_names.keys()),axis=1)
#%%#
print("Saving...")
df.to_csv(output_dir + 'lines_df_annon_user_ext.csv')



## Locations in the text
print("Searching for locations in text ... ")

df['annon_text'] = df.annon_text.progress_apply(check_text_for_locations)

print("Saving lines without locations: ")
df.to_csv(output_dir+'lines_df_annon_locations.csv')



print("Searching for emails in text: ")
p = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
df['annon_text'] = df.annon_text.progress_apply(lambda txt: re.sub(p, "email@privaat.com", txt))

print("Saving lines without emails: ")
df.to_csv(output_dir + "lines_annon_emails.csv")