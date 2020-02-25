import pandas as pd
from ast import literal_eval

DATA_DIR = '/home/burtenshaw/data/teen/beta/whatsapp/_6/'
ALPHA_DIR = '/home/burtenshaw/data/teen/alpha/redo/'
KEY_PATH = '/home/burtenshaw/data/teen/beta/combined/combined_matches.csv'
OUTPUT_DIR = '/home/burtenshaw/data/teen/beta/combined/'

user = pd.read_csv(DATA_DIR + 'combined_user.csv', index_col=0)
line = pd.read_csv(DATA_DIR + 'combined_line.csv', index_col=0)
conv = pd.read_csv(DATA_DIR + 'combined_conv.csv', index_col=0)

a_user = pd.read_csv(ALPHA_DIR + 'alpha_users.csv', index_col=0)
a_line = pd.read_csv(ALPHA_DIR + 'alpha_lines.csv', index_col=0)

# Encorporate validated matches
key = pd.read_csv(KEY_PATH, index_col=0)

print('conv')               
# %%
# fields from conv
_c = conv[['line_idxs','users']]
_c['line_idxs'] = _c.line_idxs.apply(literal_eval)
_c = _c.explode('line_idxs')
_c['conv_idx'] = _c.index
_c.index = _c.line_idxs

print('user')
# %%
# fields from user
# LOAD ALPHA DATA - Where Possible\
_u = user[['line_idxs','AS_ALPHA_chatter_id']]
_u['chatter_id'] = key.matched_chatter_id


# %%
_u = pd.merge(left=_u,right=a_user,left_on='chatter_id', right_index=True, how='left')


# %%
_u['line_idxs'] = _u.line_idxs.apply(literal_eval)
_u = _u.explode('line_idxs')
_u['user_idx'] = _u.index
_u.index = _u.line_idxs

print('source')
# %%
_s = pd.DataFrame(list(line.source.apply(lambda x: x.split('/')[-1].split('_')[:4])),columns=['year','medium','conv_sex','conv_size'])

print('combining')
# %%
all_on_line = pd.concat([_u,_c,_s], axis=1)
all_on_line = pd.merge(left= all_on_line, right=line, left_index=True, right_index=True)

all_on_line.drop(columns=['line_idxs','line_n'], inplace=True)

print('saving')
# %%
all_on_line.to_csv(OUTPUT_DIR + 'combined_all_on_line.csv')
# %%



