import os
try:
	os.chdir(os.path.join(os.getcwd(), '/home/burtenshaw/code/2019/teen_conv'))
	print(os.getcwd())
except:
	pass

from beta import betaData
import json
from collections import defaultdict
import pandas as pd


conversation_json = "/home/burtenshaw/data/teen/raw/whatsapp.json"
alpha_key = '/home/burtenshaw/data/teen/alpha/redo/key.json'



with open(alpha_key) as f:
    alpha_key = json.load(f)

beta = betaData(conversation_json, alpha_key=alpha_key)

with open(conversation_json, 'r') as f:
    whatsapp_raw = json.load(f)


_df = pd.DataFrame.from_dict(whatsapp_raw, orient="index")

_lines = pd.concat(list(_df.lines.apply(pd.DataFrame)))
_lines['source'] = _lines.conv_n.apply(lambda conv_n: whatsapp_raw[str(conv_n)]['source'])

_lines['text'] = _lines.text.apply(lambda x: x[:-1] )



_lines.to_csv('/home/burtenshaw/data/teen/beta/whatsapp/whatsapp_clean_lines_1.csv')