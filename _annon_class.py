#%%#
import os
try:
	os.chdir(os.path.join(os.getcwd(), '/home/burtenshaw/code/2019/teen_conv'))
	print(os.getcwd())
except:
	pass

# coding: utf-8
import json
import pandas as pd
from teen_conv.annon import Annon

# Data paths 

output_dir = "/home/burtenshaw/data/teen/beta/combined/annon/"
line = pd.read_csv("/home/burtenshaw/data/teen/beta/combined/combined_line.csv", index_col=0)
conv = pd.read_csv("/home/burtenshaw/data/teen/beta/combined/combined_conv.csv", index_col=0)
user = pd.read_csv("/home/burtenshaw/data/teen/beta/combined/combined_user.csv", index_col=0)

# resources

with open('/home/burtenshaw/data/teen/beta/usable_user_list.json', 'r') as f:
    all_users = json.load(f)

with open('/home/burtenshaw/data/teen/annon_files/gementes_improved.json', 'r') as f:
    gementes = json.load(f) 

with open('/home/burtenshaw/data/teen/annon_files/streets.json', 'r') as f:
    streets = json.load(f)

locations = gementes + streets 

annon = Annon(user, line, conv, all_users, locations)


# run : 
print("Searching for local users in text: ")
df = annon.remove_local_users()
path = output_dir+'lines_df_annon_user_local.csv'
print("Saving :" + path)
df.to_csv(path)

print("Searching for any users in text: ")
df = annon.remove_exterior_users()
path = output_dir + 'lines_df_annon_user_ext.csv'
print("Saving :" + path)
df.to_csv(path)

print("Searching for places in text: ")
df = annon.remove_locations()
path = output_dir+'lines_df_annon_locations.csv'
print("Saving :" + path)
df.to_csv(path)

print("Searching for emails in text: ")
df = annon.remove_emails()
path = output_dir + "lines_annon_emails.csv"
print("Saving :" + path)
df.to_csv(path)