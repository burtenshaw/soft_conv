import pandas as pd
import json
import numpy as np
import itertools
from tqdm import tqdm

from beta import fb_beta
from beta import betaData
from alpha import alphaData
from alpha import matchDataSets




# whatsapp




output_dir = '/home/burtenshaw/data/teen/beta/whatsapp/_2/'

with open('/home/burtenshaw/data/teen/raw/whatsapp.json', 'r') as f:
    facebook_json = json.load(f)
# conversation_json = "/home/burtenshaw/data/teen/raw/whatsapp.json"
with open('/home/burtenshaw/data/teen/alpha/redo/key.json') as f:
    alpha_key = json.load(f)

file_path = "/home/burtenshaw/data/teen/alpha/lisa_annon.txt"
alpha = alphaData(file_path, alpha_key=alpha_key)
alpha.run()

latest_csv = '/home/burtenshaw/data/teen/beta/whatsapp/whatsapp_clean_lines_1.csv'
latest_csv = pd.read_csv(latest_csv)

beta = fb_beta(conversation_json=facebook_json, line_csv=latest_csv, alpha_object=alpha)

beta.line_df.to_csv(output_dir + 'wa_line_df.csv')
beta.conv_df.to_csv(output_dir + 'wa_conv_df.csv')
beta.user_df.to_csv(output_dir + 'wa_user_df.csv')

beta.contact_df = beta.user_df
m = matchDataSets(alpha, beta, params={'sample':10,'intersection':0.5})
m.run()

m.contact_df.to_csv(output_dir+'wa_matches.csv')
m.manual_df.to_csv(output_dir+'wa_manual.csv')




