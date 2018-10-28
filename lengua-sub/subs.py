import html
import json
import os
import re
from .config import dict_languages, BASE_JSON_DIR, BASE_DIR
from .utils import SubDoc, get_encodings, EncodingError



def sublog(text, doc=None):
    if doc:
        doc.log(text)
    print(text)


def makedir(folder):
    if not os.path.exists(os.path.dirname(folder)):
        os.makedirs(os.path.dirname(folder))


class OrderBy:
    def pk(pk, frm, to, text):
        return pk, text

    def frm(pk, frm, to, text):
        return frm, text

    def to(pk, frm, to, text):
        return to, text

    def frmto(pk, frm, to, text):
        return "{}->{}".format(frm, to), text

    def all(pk, frm, to, text):
        return "{}:{}->{}".format(pk, frm, to), text

    def getsort(s):
        s = s.strip()
        if s == '':
            return OrderBy.frmto
        elif s == 'pk':
            return OrderBy.pk
        elif s == 'from':
            return OrderBy.frm
        elif s == 'to':
            return OrderBy.to
        elif s == 'fromto':
            return OrderBy.frmto
        elif s == 'all':
            return OrderBy.all


def get_import_options():
    dirs = []
    for dir in os.listdir(BASE_JSON_DIR):
        errors = 0
        with open("{}/{}/frmto/doc.txt".format(BASE_JSON_DIR, dir), 'r', encoding='utf8') as f:
            errors = f.read().split('\n\n')[1]
            errors = len(errors.split('\n'))
        dirs.append((dir, errors))
    return dirs


def get_options():
    return os.listdir(BASE_DIR)


def validate_encoding(file):
    return True


def get_folder_data(dir, sort, doc=None):
    result = {}
    folder = "{}/{}".format(BASE_DIR, dir)
    sublog("Movie {} \n\n".format(dir), doc)
    if not os.path.isdir(folder):
        sublog("Movie is downloaded yet? or just spelling (Enter to folder name)", doc)
        return None
    directory_files = os.listdir(folder)
    sublog("Possible {} .sub files".format(len(directory_files)), doc)
    for name in directory_files:
        path = "{}/{}".format(folder, name)
        language_code = dict_languages.get(name.split("-")[0].lower(), None)
        # If the extension of the file matches some text followed by ext...
        if not os.path.isfile(path):
            sublog("Movie {} still has folders in it we are missing some data!".format(name), doc)
            sublog("Please fix manually...", doc)
            continue
        encodings = get_encodings(name.split("-")[0].lower())[::-1]
        sublog("{}:{}".format(name.split("-")[0], language_code), doc)
        if not language_code:
            sublog("An Unknown language {} continuing...".format(name.split("-")[0]), doc)
            continue
        else:
            language_code = language_code['code']
        enco = None
        try:
            while encodings:
                enco = encodings.pop()
                with open(path, 'rb') as f:
                    a = f.read().decode(enco)
                    if 'utf8' != enco:
                        sublog("Report on {}:{} by the encoding list ".format(language_code, enco), doc)
                    a = format_subtitle(a)
                    if not validate_encoding(a):
                        raise EncodingError
                    result[language_code] = a
                    continue
        except Exception as e:
            sublog("language {} Exception {} on encoding {}".format(language_code, e, enco), doc)
        except IndexError as e:
            sublog("No known encodings for languge {}.".format(language_code), doc)
    return result


def format_subtitle(raw_str, orderby=OrderBy.frmto, lines_pattern='\n\n',
                    single_pattern=r'(?P<full>(?P<pk>\d+)\n(?P<from>[\d:,]+)[ --> ]+(?P<to>[\d:,]+))', doc=None):
    result = {}
    lines = raw_str.replace('\r', '').split("\n\n")
    for line in lines:
        m = re.match(single_pattern, line)
        if m:
            full, pk, frm, to = m.group('full'), m.group('pk'), m.group('from'), m.group('to')
            line = line.replace(full, "").strip()
            line = html.unescape(line).strip().replace("\n", " ")
            key, value = orderby(pk, frm, to, line)
            result[key] = value
    return result


def sync_keys_to_languages(subtitle_dict, orderby=OrderBy.frmto, doc=None):
    sublog("\n\n", doc)
    sublog("Syncing")
    en = subtitle_dict.get('en', None)
    if not en:
        sublog("No english jsons to work with", doc)
        return
    del subtitle_dict['en']
    strength = {}
    result = {}

    sublog("There are {} Possible languages and {} lines".format(len(subtitle_dict), len(en)), doc)
    for key in en:
        item = {'en': en[key]}
        for lang in subtitle_dict:
            val = subtitle_dict[lang].get(key, None)
            if val:
                item[lang] = val
                strength[lang] = strength.get(lang, 0) + 1
        result[key] = item

    # We got the json we wanted!
    # I just want to sublog the strength of the SortBy
    # they vary in result so try different options
    # (pk, only from, only to, from & to, all)
    total = len(en)

    sublog("Strength of the SortBy: {}".format(orderby.__name__), doc)
    for lang in strength:
        percent = strength[lang] / total * 100
        percent = int(percent / 10)  # Score of 0 - 10
        score = "|{}﴾﴿{}|".format("-" * (percent - 1), "-" * (10 - percent))
        sublog("{:} {:<10}{:>15} match:{}".format(lang, "{} lines".format(len(subtitle_dict[lang])), score,
                                                  strength[lang]), doc)

    sublog("Change SortBy: --sort [fromto(DEFAULT), pk,from,to, all]")
    return result


def unpack_to_csv(result):
    keys = result.keys()
    headers = []
    for key in keys:
        val = result[key]
        headers = headers + list(val.keys())
    headers = set(headers)
    lines = []
    lines.append(','.join(headers))
    for key in keys:
        line = []
        for header in headers:
            line.append(result[key].get(header, ''))
        lines.append(r"'{}'".format(r"','".join(line)))
    return lines


def create_html_page(title, sort, csv, doc, doc_errors):
    pass


def create_json_from_folder(dir, sort):
    doc = SubDoc()
    folder = "{}/{}/{}/".format(BASE_JSON_DIR, dir, sort.__name__)
    data = get_folder_data(dir, sort, doc)
    data = {} if data is None else data
    result = sync_keys_to_languages(data, orderby=sort, doc=doc)
    makedir(folder)
    with open("{}doc.txt".format(folder), 'w', encoding='utf8') as f:
        doc = doc.get()
        f.write(doc)
    if result:
        csv = unpack_to_csv(result)
        # html = create_html_page(dir, sort, csv, doc, doc_errors)
        with open("{}data.csv".format(folder), 'w', encoding='utf8') as f:
            f.write("\n".join(csv))
        with open("{}data.json".format(folder), 'w', encoding='utf8') as f:
            f.write(json.dumps(result))
    return


def insert_lengua_text(dict):
    pass


def get_csv(dir, sort):
    folder = "{}/{}/{}/".format(BASE_JSON_DIR, dir, sort.__name__)
    result = None
    with open("{}data.csv".format(folder), 'r', encoding='utf8') as f:
        result = f.read()
    return result


def get_json(dir, sort=OrderBy.frmto):
    folder = "{}/{}/{}/".format(BASE_JSON_DIR, dir, sort.__name__)
    result = None
    try:
        with open("{}data.json".format(folder), 'r', encoding='utf8') as f:
            result = json.loads(f.read())
    except FileNotFoundError as e:
        sublog("Movie {} FileNotFoundError:json Exception {}".format(dir, e))
    return result


def get_doc(dir, sort=OrderBy.frmto):
    folder = "{}/{}/{}/".format(BASE_JSON_DIR, dir, sort.__name__)
    result = None
    with open("{}doc.txt".format(folder), 'r', encoding='utf8') as f:
        result = f.read()
    return result
