from preprocess import *
import argparse

patterns = {"date": ["(?P<date>(?:(?:[0-3][0-9])|(?:[0-9]))(?:\/|\-|\.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:\/|\-|\.)(?:\d{2}|\d{4})(?:,|) (?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))(?:\:\ |\ \-\ )(?P<user>.+?)(?:\:)(?P<text>.*)"],
            "one" : "(?# get date)(?P<date>(?:(?:[0-3][0-9])|(?:[0-9]))(?:\/|\-|\.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:\/|\-|\.)(?:\d{2}|\d{4})(?:,|) (?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))(?:\:\ |\ \-\ )(?# get user)(?P<user>.+?)(?:\:)(?# get text)(?P<text>(.|\r|\n?|\n)+?(?=(?:(?# next date or end of the doc)(?:(?:[0-3][0-9])|(?:[0-9]))(?:\/|\-|\.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:\/|\-|\.)(?:\d{2}|\d{4})(?:,|) (?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))|(?# end of doc)\Z))",
            'conv':"(?# get conversation date marker)(?P<conv>(?P<fb_date>(?P<_day>\d\d)(?:\s)(?P<_month>(?:[a-z|A_Z]{4,10}))\s(?P<_year>(?:[0-9]{4}))))(?:\n.*\n)(?P<exchange>(?:.*|\r|\n?|\n)+?(?=(?:(?:\d\d)\s(?:(?:[a-z|A_Z]{4,10}))\s(?:(?:[0-9]{4}))|\Z)))",
           'line': '(?# get the actual date)(?P<date>(?P<day>\d\d)\-(?P<month>(?:[0-2][0-9]))\-(?P<year>(?:[0-9]{4}))\s(?P<time>[0-9][0-9]\:[0-9][0-9]))\n(?# username)(?P<user>.*)\n(?# text)(?P<text>(?:.*|\r|\n?|\n)+?(?=(?:(?P<receiver>.*\n){1}(?# next date or end of the doc)(?:(?:[0-3][0-9])|(?:[0-9]))(?:\/|\-|\.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:\/|\-|\.)(?:\d{2}|\d{4})(?:,|) (?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))|(?# end of doc)\Z))'}

if __name__== "__main__":

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--debug", help="get more info and examples from data errors.", action="store_true")
    argparser.add_argument("--data", help="directory of instant messaging conversations")
    argparser.add_argument("--platform", help="type of instant messages: 'fb' / 'wa'")
    args = argparser.parse_args()
    

    if args.platform == 'wa':
        w = whatsApp(patterns['one'],data_dir=args.data,remove_names=False)
        w.run()

    elif args.platform == 'fb':
        w = facebook(patterns,data_dir=args.data,remove_names=False)
        w.run()
    