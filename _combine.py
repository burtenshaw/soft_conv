#%%#
import pandas as pd

#%%#
output_dir = "/home/burtenshaw/data/teen/beta/combined/"
wa_dir = "/home/burtenshaw/data/teen/beta/whatsapp/_5/"
fb_dir = "/home/burtenshaw/data/teen/beta/facebook/_5/"

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

w_user = pd.read_csv(w_user, index_col=0)
w_line = pd.read_csv(w_line, index_col=0)
w_conv = pd.read_csv(w_conv, index_col=0)
w_matches = pd.read_csv(w_matches, index_col=0)
w_manual = pd.read_csv(w_manual, index_col=0)

f_user = pd.read_csv(f_user, index_col=0)
f_line = pd.read_csv(f_line, index_col=0)
f_conv = pd.read_csv(f_conv, index_col=0)
f_matches = pd.read_csv(f_matches, index_col=0)
f_manual = pd.read_csv(f_manual, index_col=0)


#%%#
# Line
line = pd.concat([w_line, f_line], axis=0, join='outer', ignore_index=False, keys=None,
          levels=None, names=None, verify_integrity=False, copy=True)
# Conv
conv = pd.concat([w_conv, f_conv], axis=0, join='outer', ignore_index=False, keys=None,
          levels=None, names=None, verify_integrity=False, copy=True)
# User
user = pd.concat([w_user, f_user], axis=0, join='outer', ignore_index=False, keys=None,
          levels=None, names=None, verify_integrity=False, copy=True)

#%%#
# # Matches
matches = pd.concat([w_matches, f_matches], axis=0, join='outer', ignore_index=False, keys=None,
          levels=None, names=None, verify_integrity=False, copy=True)

# # Manual
manual = pd.concat([w_manual, f_manual], axis=0, join='outer', ignore_index=False, keys=None,
          levels=None, names=None, verify_integrity=False, copy=True)

#%%#
# add matches to users
matched_users = pd.concat([user, matches], axis=1, join='outer', ignore_index=False, keys=None,
          levels=None, names=None, verify_integrity=False, copy=True)

#%%#

# save
line.to_csv(output_dir + "combined_line.csv")
conv.to_csv(output_dir + "combined_conv.csv")
user.to_csv(output_dir + "combined_user.csv")
manual.to_csv(output_dir + "combined_manual.csv")
matches.to_csv(output_dir + "combined_matches.csv")
matched_users.to_csv(output_dir + "combined_users_matched.csv")
