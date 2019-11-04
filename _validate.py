
# coding: utf-8

# In[ ]:




# In[2]:

# Change directory to VSCode workspace root so that relative path loads work correctly. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
import os
try:
	os.chdir(os.path.join(os.getcwd(), '../../../teen_conv'))
	print(os.getcwd())
except:
	pass


get_ipython().magic('load_ext autoreload')
get_ipython().magic('autoreload 2')


# In[3]:

import pandas as pd
import json


# In[4]:

with open("/home/burtenshaw/data/teen/raw/facebook.json", 'r') as f:
    data = json.load(f)


# In[5]:

# cleaning
df = pd.read_csv('/home/burtenshaw/data/teen/beta/facebook_lines_clean_1.csv', index_col=0)
df.dropna(inplace=True)
df.dropna(subset=['raw_message','text'], inplace=True)


# In[ ]:




# In[6]:

for col in df.columns:
    df[col+'_len'] = [len(str(x)) for x in df[col]]


# In[7]:

# 100 random examples
rand_hundred = df.sample(n = 100)

# 50 shortest user
long_user = pd.DataFrame(df.sort_values(['user_len'], ascending=False)[:50][['conv_n','file_pattern','found_in','line_n','raw_date','raw_message','text','user']])
# 50 shortest user
shortest_user = pd.DataFrame(df.sort_values(['user_len'])[:50][['conv_n','file_pattern','found_in','line_n','raw_date','raw_message','text','user']])

# 50 longest text
long_text = pd.DataFrame(df.sort_values(['text_len'], ascending=False)[:50][['conv_n','file_pattern','found_in','line_n','raw_date','raw_message','text','user']])
# 50 shortest text
shortes_text = pd.DataFrame(df.sort_values(['text_len'])[:50][['conv_n','file_pattern','found_in','line_n','raw_date','raw_message','text','user']])

# 50 longest date
long_date = pd.DataFrame(df.sort_values(['raw_date_len'], ascending=False)[:50][['conv_n','file_pattern','found_in','line_n','raw_date','raw_message','text','user']])
# 50 shortest date
shortest_date = pd.DataFrame(df.sort_values(['raw_date_len'])[:50][['conv_n','file_pattern','found_in','line_n','raw_date','raw_message','text','user']])

# unfound users
unfound_users = pd.DataFrame(df.loc[df['user'] == 'unfound'][:50][['conv_n','file_pattern','found_in','line_n','raw_date','raw_message','text','user']])
# unfound dates
unfound_dates = pd.DataFrame(df.loc[df['raw_date'] == 'unfound'][:50][['conv_n','file_pattern','found_in','line_n','raw_date','raw_message','text','user']])


# In[8]:

frames = [
    rand_hundred,
    long_user,
    shortest_user,
    long_text,
    shortes_text,
    long_date,
    shortest_date,
    unfound_users,
    unfound_dates,]


# In[9]:

names = [
    'rand_hundred',
    'long_user',
    'shortest_user',
    'long_text',
    'shortes_text',
    'long_date',
    'shortes_date',
    'unfound_users',
    'unfound_dates',]

result = pd.concat(frames, keys=names)


# In[11]:

result['source'] = [data[str(result.loc[idx]['conv_n'])]['source'] for idx in result.index]


# In[13]:

result['validity'] = [1 for x in result.index]


# In[ ]:

# Long text is very hard to validate.
# user fields should be limited to one appearance of that user


# In[18]:

# In[14]:

# rand_hundred.to_excel("/home/burtenshaw/data/teen/validation/rand_hundred.xlsx")

# long_user.to_excel("/home/burtenshaw/data/teen/validation/long_user.xlsx")
# shortest_user.to_excel("/home/burtenshaw/data/teen/validation/shortest_users.xlsx")

# long_text.to_excel("/home/burtenshaw/data/teen/validation/long_text.xlsx")
# shortest_text.to_excel("/home/burtenshaw/data/teen/validation/shortest_text.xlsx")

# long_date.to_excel("/home/burtenshaw/data/teen/validation/long_date.xlsx")
# shortest_date.to_excel("/home/burtenshaw/data/teen/validation/shortest_date.xlsx")

# no_users.to_excel("/home/burtenshaw/data/teen/validation/no_users.xlsx")
# no_date.to_excel("/home/burtenshaw/data/teen/validation/no_date.xlsx")

result.to_excel("/home/burtenshaw/data/teen/validation/COMBINED.xlsx")


# In[ ]:



