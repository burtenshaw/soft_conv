#%%#
import pandas as pd

emails = pd.read_csv("/home/burtenshaw/data/teen/beta/combined/annon/lines_annon_emails.csv", index_col=0)
locations = pd.read_csv("/home/burtenshaw/data/teen/beta/combined/annon/lines_df_annon_locations.csv", index_col=0)
user_ext = pd.read_csv("/home/burtenshaw/data/teen/beta/combined/annon/lines_df_annon_user_ext.csv", index_col=0)
user_local = pd.read_csv("/home/burtenshaw/data/teen/beta/combined/annon/lines_df_annon_user_local.csv", index_col=0)

# %%
