import argparse
import pandas as pd
import json

from teen_conv.alpha import alphaData
from teen_conv.alpha import matchDataSets
from teen_conv.beta import fb_beta
from teen_conv.beta import wa_beta

if __name__== "__main__":

    argparser = argparse.ArgumentParser()
    
    argparser.add_argument("--data", 
                            help="directory of preprocessed json")
    
    argparser.add_argument("--append", 
                            help="directory of previously build dataset")
    
    argparser.add_argument("--out_dir",
                            default= None,
                            help="directory of instant messaging conversations")
    
    argparser.add_argument("--version",
                            default='_',
                            help='filename addition for versions')
    
    argparser.add_argument("--alpha", 
                            help="alpha data file")
    
    argparser.add_argument("--key", 
                            help="FOREIGN KEY : json file with dictionary of alpha usernames to chatter_ids for legacy matching")
    
    argparser.add_argument("--whatsapp", 
                            default=True, 
                            help="medium specific build")
    
    argparser.add_argument("--facebook", 
                            default=True, 
                            help="medium specific build")
    
    argparser.add_argument("--user_matching", 
                            default=False, 
                            help="perform validated matching on user names with alpha chatter id")
    
    argparser.add_argument("--manual_annotation", 
                            default=False, 
                            help="write manual annotation csv where user_matching fails or queries alpha assumptions")
    
    argparser.add_argument("--combine",
                            default=False,
                            help="combine IM mediums into one dataframe ")
    
    args = argparser.parse_args()


    # Alpha Data
    with open(args.key) as f:
        alpha_key = json.load(f)

    alpha = alphaData(args.alpha, alpha_key=alpha_key)
    alpha.run()

    # BUILDING

    ## whatsapp

    if args.whatsapp:
        with open(args.data + 'whatsapp.json', 'r') as f:
            whatsapp_json = json.load(f)
    
        wa_output_dir = args.out_dir + 'whatsapp/%s/' % args.version

        if args.append:
            wa_latest_csv = pd.read_csv(args.append)
        else:
`   `       wa_latest_csv = None
    
        wa_beta = fb_beta(conversation_json=whatsapp_json, 
                            line_csv=wa_latest_csv, 
                            alpha_object=alpha, 
                            data_prefix='wa')

        wa_beta.line_df.to_csv(wa_output_dir + 'line.csv')
        wa_beta.conv_df.to_csv(wa_output_dir + 'conv.csv')
        wa_beta.user_df.to_csv(wa_output_dir + 'user.csv')

        if args.user_matching:
            wa_m = matchDataSets(alpha, wa_beta, params={'sample':10,'intersection':0.5})
            wa_m.run()
            wa_m.contact_df.to_csv(wa_output_dir+'matched_users.csv')
            wa_m.manual_df.to_csv(wa_output_dir+'manual_annotation.csv')

    ## facebook

    if args.facebook:
        with open(args.data + 'facebook.json', 'r') as f:
            facebook_json = json.load(f)

        fb_output_dir = args.out_dir + 'facebook/%s/' % args.version


        if args.append and wa_latest_csv == None:
            fb_latest_csv = pd.read_csv(args.append)
        else:
`   `       fb_latest_csv = None

        fb_beta = fb_beta(conversation_json=facebook_json, 
                            line_csv=fb_latest_csv, 
                            alpha_object=alpha, 
                            data_prefix='fb')

        fb_beta.line_df.to_csv(fb_output_dir + 'line.csv')
        fb_beta.conv_df.to_csv(fb_output_dir + 'conv.csv')
        fb_beta.user_df.to_csv(fb_output_dir + 'user.csv')

        if args.user_matching:
            fb_m = matchDataSets(alpha, fb_beta, params={'sample':10,'intersection':0.5})
            fb_m.run()
            fb_m.contact_df.to_csv(fb_output_dir+'matches.csv')
            fb_m.manual_df.to_csv(fb_output_dir+'manual.csv')

    if args.combine and args.whatsapp and args.facebook:

        # Line
        line = pd.concat([wa_beta.line_df, fb_beta.line_df], axis=0, join='outer', ignore_index=False, keys=None,
                levels=None, names=None, verify_integrity=False, copy=True)
        # Conv
        conv = pd.concat([wa_beta.conv_df, fb_beta.conv_df], axis=0, join='outer', ignore_index=False, keys=None,
                levels=None, names=None, verify_integrity=False, copy=True)
        # User
        user = pd.concat([wa_beta.user_df, fb_beta.user_df], axis=0, join='outer', ignore_index=False, keys=None,
                levels=None, names=None, verify_integrity=False, copy=True)

        if args.matching:
            matches = pd.concat([wa_m.contact_df, fb_m.contact_df], axis=0, join='outer', ignore_index=False, keys=None,
                    levels=None, names=None, verify_integrity=False, copy=True)

            # # Manual
            manual = pd.concat([wa_m.manual_df, fb_m.manual_df], axis=0, join='outer', ignore_index=False, keys=None,
                    levels=None, names=None, verify_integrity=False, copy=True)

            #%%#
            # add matches to users
            matched_users = pd.concat([user, matches], axis=1, join='outer', ignore_index=False, keys=None,
                    levels=None, names=None, verify_integrity=False, copy=True)

        # save
        line.to_csv(args.out_dir + '/combined/' + "line.csv")
        conv.to_csv(args.out_dir + '/combined/' + "conv.csv")
        user.to_csv(args.out_dir + '/combined/' + "user.csv")
        manual.to_csv(args.out_dir + '/combined/' + "manual.csv")
        matches.to_csv(args.out_dir + '/combined/' + "matches.csv")
        matched_users.to_csv(args.out_dir + '/combined/'+ "users_matched.csv")