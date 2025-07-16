from utils.utils import *
import argparse

import argparse

class addIndentFormatter(argparse.HelpFormatter):
    def __init__(self, *args, **kwargs):
        kwargs['max_help_position'] = 40
        super().__init__(*args, **kwargs)

class metavarOverrideParser(argparse.ArgumentParser):
    def _check_value(self, action, value):
        if action.choices is not None and value not in action.choices:
            metavar = action.metavar
            if metavar == None:
                expected = f"expected {', '.join(map(repr, action.choices))}"
            else: 
                print('sdfsds')
                expected = f"expected {metavar}"

            msg = f"invalid choice: '{value}' ({expected})"
            raise argparse.ArgumentError(action, msg)
        
    def error(self, message):
        for action in self._actions:
            if action.metavar:
                print('**',action.dest)
                mparts = message.split('choice')
                message = mparts[0].replace(action.metavar, action.dest) + 'choice'+ mparts[1]
        super().error(message)


def main():
    parser = metavarOverrideParser(description="Viewer for granular measurement test data.",
                                     formatter_class=addIndentFormatter )
    parser.add_argument("model",type=str,choices=['baidu','deep-seek','doubao','kimi','qwen'],help="selected model")
    parser.add_argument("language",type=str,choices=["EN","SI","TW"],help="selected language")
    parser.add_argument("query_index",type=int,metavar="[0-79]",choices=list(range(0,80)),help="index for the selected query")
    parser.add_argument("sample",default=None,nargs='?',metavar="0-4",choices=[None,'0','1','2','3','4'],help="sample number, if interested in restricting output to a single sample")
    args = parser.parse_args()
    print(args)
    query_mapper = load_query_info()

    model = args.model
    lang = args.language
    query_num = args.query_index
    sample = args.sample

    load_data_(model, lang, query_num,query_mapper,sample=sample)

if __name__ == "__main__":
    main()

