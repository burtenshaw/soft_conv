#%%#
import pandas as pd

#%%#
wa_dir = "/home/burtenshaw/data/teen/beta/whatsapp/_4/"
fb_dir = "/home/burtenshaw/data/teen/beta/facebook/_4/"

w_user= wa_dir + "wa_user_df.csv"
w_line= wa_dir + "wa_line_df.csv"
w_conv= wa_dir + "wa_conv_df.csv"
w_matches= wa_dir + "wa_matches.csv"
w_manual= wa_dir + "wa_manual.csv"

f_user= fb_dir + "fb_user_df.csv"
f_line= fb_dir + "fb_line_df.csv"
f_conv= fb_dir + "fb_conv_df.csv"
f_matches= fb_dir + "fb_matches.csv"
f_manual= fb_dir + "fb_manual.csv"

#%%#

w_user = pd.read_csv(w_user, index_col=0)
w_line = pd.read_csv(w_line, index_col=0)
w_conv = pd.read_csv(w_conv, index_col=0)
# w_matches = pd.read_csv(w_matches, index_col=0)
# w_manual = pd.read_csv(w_manual, index_col=0)

f_user = pd.read_csv(f_user, index_col=0)
f_line = pd.read_csv(f_line, index_col=0)
f_conv = pd.read_csv(f_conv, index_col=0)
# f_matches = pd.read_csv(f_matches, index_col=0)
# f_manual = pd.read_csv(f_manual, index_col=0)

#%%#
# Line
line = pd.concat([w_line, f_line], axis=0, join='outer', ignore_index=False, keys=None,
          levels=None, names=None, verify_integrity=False, copy=True)
#%%#
# Conv


#%%#
# User

#%%#
# Matches

#%%#
# Manual
