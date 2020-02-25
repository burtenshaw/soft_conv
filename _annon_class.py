import json
import pandas as pd
from teen_conv.annon import Annon

# Data paths 

ALL_USERS_PATH = '/home/burtenshaw/data/teen/beta/usable_user_list.json'
GEMENTES_PATH = '/home/burtenshaw/data/teen/annon_files/gementes_improved.json'
STREETS_PATH = '/home/burtenshaw/data/teen/annon_files/streets.json'

output_dir = "/home/burtenshaw/data/teen/beta/combined/annon/"
DATA_DIR = '/home/burtenshaw/data/teen/beta/whatsapp/_6/'
KEY_PATH = '/home/burtenshaw/data/teen/beta/combined/combined_matches.csv'
OUTPUT_DIR = '/home/burtenshaw/data/teen/beta/combined/'

user = pd.read_csv(DATA_DIR + 'combined_user.csv', index_col=0)
line = pd.read_csv(DATA_DIR + 'combined_line.csv', index_col=0)
conv = pd.read_csv(DATA_DIR + 'combined_conv.csv', index_col=0)

# resources

with open(ALL_USERS_PATH, 'r') as f:
    all_users = json.load(f)

with open(GEMENTES_PATH, 'r') as f:
    gementes = json.load(f) 

with open(STREETS_PATH, 'r') as f:
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