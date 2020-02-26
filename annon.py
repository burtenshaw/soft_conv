import json
import pandas as pd
import argparse

from teen_conv.annon import Annon

if __name__== "__main__":

    argparser = argparse.ArgumentParser()
    
    argparser.add_argument("--data", 
                            help="directory of csv files produced by build.py")
    
    argparser.add_argument("--out_dir",
                            default= None,
                            help="directory of instant messaging conversations")
    
    argparser.add_argument("--users",
                            default='usable_user_list.json',
                            help='a json list of all users')
    
    argparser.add_argument("--gementes", 
                            help="up to date list of all councils within Flanders")
    
    argparser.add_argument("--streets", 
                            help="up to date list of all actual streets within Flanders")
    
    argparser.add_argument("local_users",
                            default=True,
                            help = 'remove names from message text, of the users within a conversation')
    argparser.add_argument("exterior_users",
                            default=True,
                            help = 'aggresively remove any name from message text')
    argparser.add_argument("locations",
                            default=True,
                            help = 'remove names from messages of the users within a conversation')
    argparser.add_argument("contact_info",
                            default=True,
                            help = 'remove names from messages of the users within a conversation')           
    
    args = argparser.parse_args()
    
    # Data paths 

    user = pd.read_csv(args,data + 'user.csv', index_col=0)
    line = pd.read_csv(args,data + 'line.csv', index_col=0)
    conv = pd.read_csv(args,data + 'conv.csv', index_col=0)

    # resources

    with open(args.users, 'r') as f:
        all_users = json.load(f)

    with open(args.gementes, 'r') as f:
        gementes = json.load(f) 

    with open(args.streets, 'r') as f:
        streets = json.load(f)

    locations = gementes + streets 
    annon = Annon(user, line, conv, all_users, locations)

    # run : 

    if args.local_users:
        print("Searching for local users in text: ")
        df = annon.remove_local_users()
        path = args.out_dir+'lines_df_annon_user_local.csv'
        print("Saving :" + path)
        df.to_csv(path)

    if args.exterior_users:
        print("Searching for any users in text: ")
        df = annon.remove_exterior_users()
        path = args.out_dir + 'lines_df_annon_user_ext.csv'
        print("Saving :" + path)
        df.to_csv(path)

    if args.locations:
        print("Searching for places in text: ")
        df = annon.remove_locations()
        path = args.out_dir+'lines_df_annon_locations.csv'
        print("Saving :" + path)
        df.to_csv(path)

    if args.contact_info:
        print("Searching for emails in text: ")
        df = annon.remove_emails()
        path = args.out_dir + "lines_annon_emails.csv"
        print("Saving :" + path)
        df.to_csv(path)