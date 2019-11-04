
# coding: utf-8
import pandas as pd
import numpy as np
import json
from collections import defaultdict as dd
from tqdm import tqdm
import nl_core_news_sm
nlp = nl_core_news_sm.load()
import re
from utils import *
# resources

output_dir = "/home/burtenshaw/data/teen/beta/facebook/annon/"

# latest_csv = '/home/burtenshaw/data/teen/beta/facebook_lines_clean_1.csv'

# with open(output_dir+'usable_user_list.json', 'r') as f:
#     all_users = json.load(f)

# with open('/home/burtenshaw/data/teen/annon_files/gementes_improved.json', 'r') as f:
#     gementes = json.load(f) 

# with open('/home/burtenshaw/data/teen/annon_files/streets.json', 'r') as f:
#     streets = json.load(f)




# all_fuzzy_names = fuzzy_names(all_users)

# manual_additions = ['hoboken']
# vocab_gementes = [x for x in gementes if x in nlp.vocab and x not in manual_additions]

# gementes.extend(streets)
# vocab_gementes.extend([x for x in streets if x in nlp.vocab])

# # # build prelim dataframes

df = pd.read_csv('/home/burtenshaw/data/teen/beta/facebook/annon/ines_df_annon_locations.csv')

# df = pd.read_csv(latest_csv, index_col=0)
# df.dropna(inplace=True)
# df.dropna(subset=['raw_message','text'], inplace=True)
# df['line_idx'] = ['l_' + str(x) for x in df.index]
# df.index = df['line_idx']
# df['conv_idx'] = ['c_' + str(x) for x in df.conv_n]


# convs = df.groupby(['conv_idx'])
# _convs = []
# for cdf in convs:
#     _convs.append({
#     'conv_idx': cdf[0],
#     'users': list(dict.fromkeys(list(cdf[1].user))),
#     'line_idxs': cdf[1].index})
# conv_df = pd.DataFrame(_convs)
# conv_df.index = conv_df['conv_idx']


# users = df.groupby(['user'])
# _users = []
# for udf in users:
#     _users.append({
#     'user_name': udf[0],
#     'conv_idx': list(udf[1].conv_n),
#     'line_idxs': udf[1].index})
# user_df = pd.DataFrame(_users)
# user_df['user_idx'] = ['u_' + str(x) for x in user_df.index]
# user_df['user_name_lower'] = [str(x).lower() for x in user_df.user_name]
# user_df.index = user_df['user_idx']

# # annon : 

# print("Searching for local users in text ... ")

# _annon_lines = []
# for idx in tqdm(conv_df.index):
#     text_lines = df.loc[conv_df.loc[idx].line_idxs].index
#     conv_users = fuzzy_names(conv_df.loc[idx].users)
#     for idx in text_lines:
#         idx=df.loc[idx]['line_idx']
#         text=df.loc[idx]['text']
#         for c_u in conv_users.keys():
#             if c_u in text:
#                 text = check_text_for_user(text, c_u)
#         _annon_lines.append({'line_idx':idx, 'text':text})

# print("Saving...")
# df = pd.DataFrame(_annon_lines)
# df.to_csv(output_dir+'lines_df_annon_user_local.csv')

# # ## External participants to the conversation
# print("Searching for exterior users in text ... ")
# _annon_lines = []
# for _idx in tqdm(df.index):
#     idx = df.loc[_idx]['line_idx']
#     text = df.loc[_idx]['text']
#     for c_u in all_fuzzy_names.keys():
#         if c_u in text:
#             text = check_text_for_user(text, c_u)
#     _annon_lines.append({'line_idx':idx, 'text':text})

# print("Saving...")
# df = pd.DataFrame(_annon_lines)
# df.to_csv(output_dir + 'lines_df_annon_user_ext.csv')

# ## Locations in the text

# _annon_lines = []
# locations = dd(str)
# _x = 0

# print("Searching for locations in text ... ")

# for _idx in tqdm(df.index):
#     idx = df.loc[_idx]['line_idx']
#     text = df.loc[_idx]['text']
#     doc = nlp(text)
#     for t in doc:
#         txt = t.lower_
#         if txt in gementes:
#             if txt not in vocab_gementes:
#                 locations[txt] = locations.get(txt, loc_idx(_x))
#                 text = text.replace(t.text,locations[txt])
#                 _x += 1
#             elif t.ent_type_ == 'LOC':
#                 locations[txt] = locations.get(txt, loc_idx(_x))
#                 text = text.replace(t.text,locations[txt])
#                 _x += 1
#             elif t.pos_ == 'NOUN' and t.pos_ != nlp(txt)[0].pos_:
#                 locations[txt] = locations.get(txt, '_'+loc_idx(_x))
#                 text = text.replace(t.text,locations[txt])
#                 _x += 1
            
#     _annon_lines.append({'text':text,'line_idx':idx})

# print("Saving lines without locations: ")
# df = pd.DataFrame(_annon_lines)
# df.to_csv(output_dir+'ines_df_annon_locations.csv')

p = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
df['text'] = df.text.apply(lambda txt: re.sub(p, "email@privaat.com", txt))
df.to_csv(output_dir + "lines_annon_emails.csv")