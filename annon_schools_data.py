from preprocess import *
import argparse

# a = re.compile(r'(\d{1,2}(-|\/|\.)\d{1,2}(-|\/|\.)\d{4} )?\d{1,2}:\d{2}')
# b = re.compile(r'((\n)|(\r)|(\\n)|(\\r))\d{1,2} (januari|jan\.|februari|feb\.|maart|maa\.|april|apr\.|mei|mei\.|juni|jun\.|juli|jul\.|augustus|aug\.|september|sep\.|oktober|okt\.|november|nov\.|december|dec\.)( \d{4})?((\n)|(\r)|(\\n)|(\\r))')
# c = re.compile(r'((\n)|(\r)|(\\n)|(\\r))(maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag|Vandaag)(( \d{1,2}:\d{2})|(\n)|(\r)|(\\n)|(\\r))')
# d = re.compile(r'((\n)|(\r)|(\\n)|(\\r))\d{1,2} (uur|minuten|minuut|dag|dagen) geleden((\n)|(\r)|(\\n)|(\\r))')
# e = re.compile(r'\d{1,2}\/\d{1,2}, \d{1,2}:\d{2}(?:am|pm|AM|PM)')
# linebreaks = re.compile(r'(\\r|\\n|\r|\n)+')

patterns = {"line_date": r"(?P<date>(?:(?:[0-3][0-9])|(?:[0-9]))(?:\/|\-|\.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:\/|\-|\.)(?:\d{2}|\d{4})(?:,|) (?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))",
            "multi_date" : [
                           re.compile(r"(?P<date>(?:(?:[0-3][0-9])|(?:[0-9]))(?:.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:.)(?:\d{2}|\d{4})(?:.{0,4})(?:[0-2][0-9]).(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|\w))"),
                           re.compile(r"(?P<date>(?:(?:[0-3][0-9])|(?:[0-9]))(?:\/|\-|\.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:\/|\-|\.)(?:\d{2}|\d{4})(?:,|) (?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))"),
                           re.compile(r"(?P<date>(?:(?:[0-3][0-9])|(?:[0-9]))(?:.)(?:(?:(?:0|)[0-9])|(?:(?:1)[0-2]))(?:.)(?:\d{2}|\d{4})(?:.*))"),
                           re.compile(r"(?P<date>(?:(?:[0-3][0-9])|(?:[0-9]))(?:.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:.)(?:\d{2}|\d{4})(?:.*))"),
                           re.compile(r"(?P<date>(?:(?:[0-3][0-9])|(?:[0-9]))(?:.)(?:(?:[0-3][0-9]))(?:.)(?:\d{2}|\d{4})(?:.{0,4})(?:[0-2][0-9]).*)"),
                           re.compile(r"(.*(?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))"),
                           re.compile(r"(.*(?:[0-2][0-9])\:(?:[0-5][0-9]))")
                           ],
            "one" : "(?# get date)(?P<date>(?:(?:[0-3][0-9])|(?:[0-9]))(?:\/|\-|\.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:\/|\-|\.)(?:\d{2}|\d{4})(?:,|) (?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))(?:\:\ |\ \-\ )(?# get user)(?P<user>.+?)(?:\:)(?# get text)(?P<text>(.|\r|\n?|\n)+?(?=(?:(?# next date or end of the doc)(?:(?:[0-3][0-9])|(?:[0-9]))(?:\/|\-|\.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:\/|\-|\.)(?:\d{2}|\d{4})(?:,|) (?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))|(?# end of doc)\Z))",
            'conv':"(?# get conversation date marker)(?P<conv>(?P<fb_date>(?P<_day>\d\d)(?:\s)(?P<_month>(?:[a-z|A_Z]{4,10}))\s(?P<_year>(?:[0-9]{4}))))(?:\n.*\n)(?P<exchange>(?:.*|\r|\n?|\n)+?(?=(?:(?:\d\d)\s(?:(?:[a-z|A_Z]{4,10}))\s(?:(?:[0-9]{4}))|\Z)))",
           'line': '(?# get the actual date)(?P<date>(?P<day>\d\d)\-(?P<month>(?:[0-2][0-9]))\-(?P<year>(?:[0-9]{4}))\s(?P<time>[0-9][0-9]\:[0-9][0-9]))\n(?# username)(?P<user>.*)\n(?# text)(?P<text>(?:.*|\r|\n?|\n)+?(?=(?:(?P<receiver>.*\n){1}(?# next date or end of the doc)(?:(?:[0-3][0-9])|(?:[0-9]))(?:\/|\-|\.)(?:(?:(?:0)[0-9])|(?:(?:1)[0-2]))(?:\/|\-|\.)(?:\d{2}|\d{4})(?:,|) (?:[0-2][0-9])\:(?:[0-5][0-9])(?:pm|am| pm| am|\:[0-5][0-9]|))|(?# end of doc)\Z))',
        #    'brutal': [a,b,c,d,e],
        #    'linebreaks': linebreaks
           }


if __name__== "__main__":

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--debug", help="get more info and examples from data errors.", action="store_true")
    argparser.add_argument("--data", help="directory of instant messaging conversations")
    argparser.add_argument("--platform", help="type of instant messages: 'fb' / 'wa'")
    args = argparser.parse_args()
    

    if args.platform == 'wa':
        w = whatsApp(patterns['one'],data_dir=args.data,remove_names=False,out_dir="whatsapp.json",)
        w.run()

    elif args.platform == 'fb':
        w = facebook(patterns,data_dir=args.data,remove_names=False, out_dir="facebook.json")
        w.run()
    