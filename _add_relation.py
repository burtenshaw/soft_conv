from preprocess import instantMessage
import argparse

class relation_only(instantMessage):
        def conversation(self,path):
            try:
                _path = path.split('/')
                filename = path[2].split('_')
                return {
                    'source_file':path,
                    'school': _path[1],
                    'year': filename[0],
                    'platform':filename[1],
                    'genders':filename[2],
                    'privacy':filename[3],
                    'name':filename[4]}
            except IndexError:
                print('Filename Error: ', path)
                return path

if __name__== "__main__":

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--data", help="directory of instant messaging conversations")
    args = argparser.parse_args()
          
    r = relation_only(data_dir=args.data, out_dir='conversation_paths.json',)
    r.run()