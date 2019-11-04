import pandas as pd
import json
import numpy as np
import itertools
from tqdm import tqdm

from teen_conv.beta import fb_beta
from teen_conv.beta import betaData
from teen_conv.alpha import alphaData
from teen_conv.alpha import matchDataSets

# Paths

input_dir = '/home/burtenshaw/data/teen/'
fb_latest = 'beta/facebook/cleaning/facebook_lines_clean_2.csv'
wa_latest = 'beta/whatsapp/whatsapp_clean_lines_1.csv'
version = '_5'

with open(input_dir + 'raw/facebook.json', 'r') as f:
    facebook_json = json.load(f)

with open(input_dir + 'raw/whatsapp.json', 'r') as f:
    whatsapp_json = json.load(f)
# conversation_json = input_dir + "raw/whatsapp.json"
with open(input_dir + 'alpha/redo/key.json') as f:
    alpha_key = json.load(f)

# Alpha Data

file_path = input_dir + "alpha/lisa_annon.txt"
alpha = alphaData(file_path, alpha_key=alpha_key)
alpha.run()

# BUILDING

## whatsapp

wa_output_dir = input_dir + 'beta/whatsapp/%s/' % version
 
wa_latest_csv = pd.read_csv(input_dir + wa_latest)

wa_beta = fb_beta(conversation_json=whatsapp_json, line_csv=wa_latest_csv, alpha_object=alpha, data_prefix='wa')

wa_beta.line_df.to_csv(wa_output_dir + 'wa_line_df.csv')
wa_beta.conv_df.to_csv(wa_output_dir + 'wa_conv_df.csv')
wa_beta.user_df.to_csv(wa_output_dir + 'wa_user_df.csv')

## facebook

fb_output_dir = input_dir + 'beta/facebook/%s/' % version

fb_latest_csv = pd.read_csv(input_dir + fb_latest)

fb_beta = fb_beta(conversation_json=facebook_json, line_csv=fb_latest_csv, alpha_object=alpha, data_prefix='fb')

fb_beta.line_df.to_csv(fb_output_dir + 'fb_line_df.csv')
fb_beta.conv_df.to_csv(fb_output_dir + 'fb_conv_df.csv')
fb_beta.user_df.to_csv(fb_output_dir + 'fb_user_df.csv')

# MATCHING

## WA

m = matchDataSets(alpha, wa_beta, params={'sample':10,'intersection':0.5})
m.run()

m.contact_df.to_csv(wa_output_dir+'wa_matches.csv')
m.manual_df.to_csv(wa_output_dir+'wa_manual.csv')

## FB

m = matchDataSets(alpha, fb_beta, params={'sample':10,'intersection':0.5})
m.run()

m.contact_df.to_csv(fb_output_dir+'fb_matches.csv')
m.manual_df.to_csv(fb_output_dir+'fb_manual.csv')
