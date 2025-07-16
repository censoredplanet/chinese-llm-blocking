import json
import os
import textwrap
import shutil
import string

QUERY_SET_PATH = "utils/query_mapping_ref.json"

def print_indent(s, columns):
    s =  textwrap.wrap(s,width=columns,initial_indent="    ",subsequent_indent="    ")
    print('\n'.join(s))

def load_query_info():
    """
    Builds index to query mapping.

    Returns:
        dict: Index to query mapping.
    """
    with open(QUERY_SET_PATH, 'r') as f:
        qnum = json.load(f)
    
    queries_by_idx_lang = {}
    for k,v in qnum.items(): queries_by_idx_lang[v] = k
    return queries_by_idx_lang


def test():
    print('test')


def truncation_msg(s,tr_len):
    """
    Builds truncation notice clarifying how much of a response has been printed.

    Args:
        s (str): The response string.
        tr_len (str): The deisgnated truncation length for viewing response data.

    Returns:
        str: Truncation notice. 
    """
    if len(s) < tr_len:
        return f"(all {len(s)} chars shown)"
    else:
        return f"... ({tr_len} of {len(s)} chars shown)"

def load_data(model, lang, query_num, sample, queries_by_idx_lang, wrap_width=100, tr_len=250):
    """
    Load the raw measurement data and analysis info for a given model, language, sample, and query index.

    Args:
        model (str): The specified model, one of 'baidu', 'deep-seek', 'doubao', 'kimi', 'qwen'.
        lang (str): The specified language, one of 'EN', 'SI', 'TW'.
        sample (int): The specified sample, in the range 0-4.
        query_num (int): An index corresponding to a spcecified query, in the range 0-79.
        queries_by_idx_lang (dict): The pre-computed dictionary containing the index to query mappings.
    
    Optional keyword args:
        wrap_width (int): The character wrapping width for viewing response data; defaults to 100.
        tr_len (int): The truncation length in characters for printing response data; defaults to 250.
    """
    query = queries_by_idx_lang[f"{query_num}_{lang}"]
    print('Query:', query)
    print()

    path = os.path.join('data',model)
    fpath = os.path.join(path,f"Q{query_num}_{lang}_{sample}_info.json")
    hpath = os.path.join(path,f"Q{query_num}_{lang}_{sample}.http")

    with open(fpath, 'r') as f:
        x = json.load(f)

    tvis = x['traffic_visible_response']
    uvis = x['UI_visible_response']

    print('Traffic visible response:', textwrap.fill(tvis[:250],width=wrap_width),truncation_msg(tvis, tr_len))
    print('----------')
    print('UI visible response:', textwrap.fill(uvis[:250],width=wrap_width),truncation_msg(uvis, tr_len))
    print('----------')
    print('Block type:',x['block_type'])
    print('Indicators:',x['indicators'])

    return fpath, hpath

def load_data_(model, lang, query_num, queries_by_idx_lang, sample=None, tr_len=250):
    """
    Load the raw measurement data and analysis info for a given model, language, sample, and query index.

    Args:
        model (str): The specified model, one of 'baidu', 'deep-seek', 'doubao', 'kimi', 'qwen'.
        lang (str): The specified language, one of 'EN', 'SI', 'TW'.
        query_num (int): An index corresponding to a spcecified query, in the range 0-79.
        queries_by_idx_lang (dict): The pre-computed dictionary containing the index to query mappings.
    
    Optional keyword args:
        sample (int): The specified sample, in the range 0-4 if set; restricts printed output to this sample. 
        tr_len (int): The truncation length in characters for printing response data; defaults to 250.
    """
    columns = shutil.get_terminal_size().columns
    slen = len("**** Sample: 0 ****")
    half_dash_len = (columns - slen) // 2

    query = queries_by_idx_lang[f"{query_num}_{lang}"]
    query_eng =  queries_by_idx_lang[f"{query_num}_EN"]

    print()
    if lang != 'EN': start_up_str = f"Collecting test data for {model}, query number {query_num} and language {lang}: {query} ({query_eng})"
    else: start_up_str = f"Collecting test data for {model}, query number {query_num} and language {lang}: {query}"

    if sample == None: srange = range(0,5)
    else: 
        srange = [sample]
        start_up_str += f" --> fetching individual sample {sample}"

    print("="*columns)
    print(start_up_str)
    print("="*columns+'\n')

    outcomes = []

    path = os.path.join('data',model)
    for sample in srange:
        fpath = os.path.join(path,f"Q{query_num}_{lang}_{sample}_info.json")
        hpath = os.path.join(path,f"Q{query_num}_{lang}_{sample}.http")

        with open(fpath, 'r') as f:
            x = json.load(f)

        tvis = x['traffic_visible_response']
        uvis = x['UI_visible_response']
        width = columns
        if '\x20' in tvis or '\x20' in uvis:
            width = columns // 2
            tvis = ' '.join(tvis.split())
            uvis = ' '.join(uvis.split())
            
        tvis = tvis.replace('\n','')
        uvis = uvis.replace('\n','')

        print(f'{'-'*half_dash_len}**** Sample: {sample} ****{'-'*half_dash_len}'.center(columns))
        print('Traffic visible response:')
        print_indent(f"{tvis[:tr_len]} {truncation_msg(tvis, tr_len)}",width)
        print()
        print('UI visible response:')
        print_indent(f"{uvis[:tr_len]} {truncation_msg(uvis, tr_len)}",width)
        print()
        print('Blocking outcome:',x['block_type'])
        print('Indicators:',x['indicators'])
        outcomes.append(x['block_type'])

        print('Raw data:',hpath, '  Meta info:', fpath)
        print(f'{'-'*columns}')

    print()
    if lang != 'EN': end_str = f"Collected test data for {model}, query number {query_num} and language {lang}: {query} ({query_eng}) | Outcomes: {outcomes}"
    else: end_str = f"Collected test data for {model}, query number {query_num} and language {lang}: {query} | Outcomes: {outcomes}"
    if len(srange) == 1:
        end_str += f" --> fetched individual sample {sample}"

    print("="*columns)
    print(end_str)
    print("="*columns+'\n')


    return fpath, hpath
