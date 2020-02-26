# import pandas as pd
import json
import argparse

if __name__== "__main__":

    argparser = argparse.ArgumentParser()
    
    argparser.add_argument("--line_csv", 
                            help="path to any beta line_csv")
    argparser.add_argument("--out_csv", 
                            help="path to output validation csv for annotation")
    argparser.add_argument("--size",
                            default= 100,
                            help="number of samples per error type")
    args = argparser.parse_args()


    df = pd.read_csv(args.line_csv, index_col=0)
    df.dropna(subset=['raw_message','text'], inplace=True)


    _columns = df.columns

    for col in df.columns:
        df[col+'_len'] = [len(str(x)) for x in df[col]]

    

    # 100 random examples
    rand = df.sample(n = args.size)

    # 50 longest user
    long_user = pd.DataFrame(df.sort_values(['user_len'], ascending=False)[:args.size][_columns])
    
    # 50 shortest user
    shortest_user = pd.DataFrame(df.sort_values(['user_len'])[:args.size][_columns]) 

    # 50 longest text
    long_text = pd.DataFrame(df.sort_values(['text_len'], ascending=False)[:args.size][_columns])
    
    # 50 shortest text
    shortest_text = pd.DataFrame(df.sort_values(['text_len'])[:args.size][_columns])

    # 50 longest date
    long_date = pd.DataFrame(df.sort_values(['raw_date_len'], ascending=False)[:args.size][_columns])
    
    # 50 shortest date
    shortest_date = pd.DataFrame(df.sort_values(['raw_date_len'])[:args.size][_columns])

    # unfound users
    unfound_users = pd.DataFrame(df.loc[df['user'] == 'unfound'][:args.size][_columns])
    
    # unfound dates
    unfound_dates = pd.DataFrame(df.loc[df['raw_date'] == 'unfound'][:args.size][_columns])


    # In[8]:

    frames = [
        rand,
        long_user,
        shortest_user,
        long_text,
        shortest_text,
        long_date,
        shortest_date,
        unfound_users,
        unfound_dates,]

    names = [
        'rand_hundred',
        'long_user',
        'shortest_user',
        'long_text',
        'shortes_text',
        'long_date',
        'shortes_date',
        'unfound_users',
        'unfound_dates',]

    result = pd.concat(frames, keys=names)

    result['validity'] = [1 for x in result.index]

    result.to_csv(args.out_csv)
