import re
import sys
import uuid
from queue import Queue
from threading import Thread
from zipfile import ZipFile, BadZipFile
import os
from shutil import copyfile, rmtree

import requests
from html2text import HTML2Text

from .config import BASE_URL, SUB_RE, BASE_DIR


def get(url):
    '''Retrieve page content and use html2text to convert into readable text.'''
    # get webpage content for this url
    r = requests.get(url)
    # raise exception if status code is not 200
    r.raise_for_status()

    # use html2text to transfer html to readable text
    h = HTML2Text()
    h.ignore_links = False
    text = h.handle(r.text)

    return text


def normalize_filename(title):
    title = title.replace('\\', ' ').replace('/', ' ')
    title = title.replace(',', ' ').replace('.', ' ')
    title = title.replace('<', ' ').replace('>', ' ')
    title = title.replace('*', ' ').replace('?', ' ')
    title = title.replace('"', ' ').replace(':', ' ')
    return title


def search_subtitles(query, limit):
    '''Search subtitle by query in parameter.'''
    text = get('{}/search?q={}'.format(BASE_URL, query))

    # try to find subtitle link in this page
    movies = re.findall(r'(\/movie-imdb\/.+)\)', text)
    movies = list(set(movies))
    threads = []
    results = []
    for m in movies:
        if not limit:
            break
        else:
            limit -= 1
        q = Queue()
        t = Thread(target=get_subtitles_thread, args=('{}{}'.format(BASE_URL, m), q))
        threads.append(t)
        results.append(q)
        t.start()
    for t in threads:
        t.join()

    return [q.queue for q in results]


def search_subtitle(query):
    '''Search subtitle by query in parameter.'''
    text = get('{}/search?q={}'.format(BASE_URL, query))

    # try to find subtitle link in this page
    m = re.search(r'(\/movie-imdb\/.+)\)', text)
    if m:
        # call get_subtitles() to get all available subtitles
        return get_subtitles('{}{}'.format(BASE_URL, m.group(1)))


def get_subtitles(url):
    '''Find all subtitles url for the movie.'''
    # get webpage content for this url
    text = get(url)

    # save english subtitles
    subs = []
    title = re.search(r'## (.+)', text)
    if title:
        title = normalize_filename(title.group(1))
    else:
        title = uuid.uuid4()
    text = text.split('#### All subtitles:')[-1]
    text = text.split('#### Select favourite languages')[0]
    text = text.split('#### Trailer:')[0]
    text = text.split('---|---|---|---|---|---')[1]

    text.replace("\n", " ")
    # find upvote count, subtitle language and subtitle link
    subtitles = re.findall(SUB_RE, text)
    if not subtitles:
        return None
    subs = []
    while subtitles:
        upvote, language, link = subtitles.pop()

        subs.append({
            'up': upvote,
            'link': link.replace('\n', ''),
            'language': language
        })
    # sort list by upvote count
    subs.sort(key=lambda x: int(x['up']), reverse=True)
    langs = []
    # we only want the best
    ctr = 0
    while ctr < len(subs):
        if subs[ctr]['language'] in langs:
            del subs[ctr]
        else:
            langs.append(subs[ctr]['language'])
            ctr += 1
    subs = [(sub, title, Queue()) for sub in subs]
    threads = []
    for sub in subs:
        t = Thread(target=get_subtitle_thread, args=sub)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    # only download subtitle which has the most upvote count
    result = [(sub['language'], queue.get()) for sub, des, queue in subs]
    return result


def get_subtitles_thread(link, t_queue):
    t_queue.put(get_subtitles(link))


def get_subtitle_thread(link, destination, t_queue):
    t_queue.put(get_subtitle(link['link'], destination, link['language']))


def copy_folder_files(root, to):
    directory_files = os.listdir(root)
    for name in directory_files:
        path = "{}/{}".format(root, name)
        # If the extension of the file matches some text followed by ext...
        if os.path.isfile(path):
            if root != to:
                copyfile(path, "{}/{}".format(to, name))
        else:
            copy_folder_files(path, to)


def get_subtitle(url, destination, target):
    '''Download the specific subtitle.'''
    text = get('{}{}'.format(BASE_URL, url))
    text = text.replace('\n', ' ')
    m = re.search(r'\[DOWNLOAD SUBTITLE\]\(([^)]+)\)', text)
    if m:
        # remove all newline
        link = m.group(1).replace('\n', '').replace(' ', '')
        print('Download {}'.format(link))
        uid = uuid.uuid4()

        folder = '{}/{}/{}'.format(BASE_DIR, destination, uid)
        try:
            if not os.path.exists(folder):
                os.makedirs(folder)
        except FileExistsError as e:
            pass
        # use last part of url as file name
        filename = str(uid) + link.split('/')[-1]
        content = requests.get(link)
        if not content.ok:
            return None
        else:
            content = content.content
            # save the file to current directory
        with open('{}/{}'.format(folder, filename), 'wb') as f:
            f.write(content)

        files = []
        # extract subtitles from zip file
        try:
            with ZipFile('{}/{}'.format(folder, filename)) as zf:
                files = zf.filelist
                zf.extractall(folder)
                files = [file for file in files if file.filename.split('.')[-1] in ('srt', 'sub')]
        except BadZipFile as z:
            return []
        data = []
        if files:
            zf_filename = '{}/{}'.format(folder, files[0].filename)
            zf_target = "{}/{}".format(folder.replace('/{}'.format(uid), ''),
                                       normalize_filename("{}-{}".format(target, zf_filename.split('/')[-1])))
            copyfile(zf_filename, zf_target)
            # try:
            #     with open(zf_filename, 'r', encoding='cp1251') as f:
            #         data = f.read()
            # except UnicodeDecodeError as e:
            #     try:
            #         with open(zf_filename, 'r', encoding='utf8') as f:
            #             data = f.read()
            #     except UnicodeDecodeError as e:
            #         pass
            rmtree(folder, ignore_errors=True)
        return data
