from preprocess import instantMessage
import argparse

pattern = '(?P<path>(?:.*))\/(?P<school>.*)\/(?P<year>\d{4})\_(?P<medium>.+)\_(?P<gender>same|mixed)\_(?P<private>private|group)\_(?P<relationship>.+)\_(?P<name>.+)\.txt'
class relation_only(instantMessage):
        def conversation(self,file):
            path = self.grab_filename(file,self.pattern)
            path['source_file'] = file
            return path

if __name__== "__main__":

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--data", help="directory of instant messaging conversations")
    args = argparser.parse_args()
          
    r = relation_only(pattern=pattern, data_dir=args.data, out_dir='conversation_paths.csv',)
    r.run()