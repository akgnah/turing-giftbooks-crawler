# -*- coding: utf-8 -*-
import sys
import json
import time
import redis
import jieba
import requests
from functools import reduce
from bs4 import BeautifulSoup

db = redis.Redis()
proxy = False   # if you want to use proxy, change it True
sleep_time = 0.5


def urlopen(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.108 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,und;q=0.2',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Connection': 'keep-alive',
        'X-Requested-With': 'XMLHttpRequest',
    }

    if proxy:
        proxies = {
            'http': 'your proxy',  # if you want to use proxy
            'https': 'your proxy',
        }
    else:
        proxies = None

    return requests.get(url, headers=headers, proxies=proxies)


def yield_ids(bsobj):
    for book in bsobj.find('div', {'class': 'g-main'}).findAll('li'):
        yield book.find('div', {'class': 'book-info'}).find(lambda tag: tag.attrs.get('title')).get('href').split('/')[-1]


def parse_book(book_id):
    resp = urlopen('http://www.ituring.com.cn/book/details/%s' % book_id)
    bsobj = BeautifulSoup(resp.text, 'html.parser')

    title = bsobj.find('div', {'class': 'book-title'}).find('h2').get_text()
    img = bsobj.find('img', {'class': 'lazy'}).attrs['src'].split('/')[-1]
    gift = bsobj.findAll('div', {'class': 'buy-btns'})[-1].find(lambda tag: 'addtogiftcart' in tag.attrs['href']) and True
    price = bsobj.find('div', {'class': 'book-approaches'}).find('dt', text='纸质版定价')
    price = int(float(price.findNextSibling().get_text()[1:])) if price else 0
    date = bsobj.find('ul', {'class': 'publish-info'}).find('strong', text='出版日期')
    date = date.findParent().contents[1] if date else '1970-01-01'

    dump_books({'id': book_id, 'title': title, 'gift': gift, 'img': img, 'price': price, 'date': date})
    print('dump', book_id)
    time.sleep(sleep_time)


def fetch_book():
    resp = urlopen("http://www.ituring.com.cn/book?tab=book&sort=new&page=0")
    bsobj = BeautifulSoup(resp.text, 'html.parser')
    page_end = int(bsobj.find('li', {'class': 'PagedList-skipToLast'}).find('a').get_text()) - 1
    for book_id in yield_ids(bsobj):
        parse_book(book_id)
    time.sleep(sleep_time * 20)

    for page in range(1, page_end):
        resp = urlopen("http://www.ituring.com.cn/book?tab=book&sort=new&page=%s" % page)
        bsobj = BeautifulSoup(resp.text, 'html.parser')
        for book_id in yield_ids(bsobj):
            parse_book(book_id)
        time.sleep(sleep_time * 20)


def cut_for_search(text):
    ignore = set(['你', '是', '的', '与', '及', '第', '版', '用', '学', '和',
                  '式', '个', '从', '到', '上', '手', '卷', '道', '看', '集',
                  '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                  '：', '—', ',', '!', '！', '、', '“', '”', '[', ']',
                  '（', '）', '《', '》', '-', '.', '·', '•', '|', '"',
                  'ⅱ', '(', ')', '@', ':', '?', '【', '】', '&', '+', '/', ''])
    seg_list = jieba.lcut_for_search(text)
    seg_list = [seg.lower() for seg in seg_list if seg.strip() not in ignore]
    return set(seg_list)


def load_books():
    books = db.get('turing_books') or b'{}'
    return json.loads(books.decode())


def load_index():
    index = db.get('turing_index') or b'{}'
    return json.loads(index.decode())


def dump_books(book):
    books = load_books()
    books[book['id']] = book
    db.set('turing_books', json.dumps(books))


def dump_index(seg, book_id):
    index = load_index()
    index_list = index.get(seg, [])
    index_list.append(book_id)
    index[seg] = list(set(index_list))
    db.set('turing_index', json.dumps(index))


def update_books(mode='new', count=100):
    books = load_books()
    if not books or mode == 'all':
        fetch_book()
    else:
        sort_books = sorted(books.values(), key=lambda x: x['date'], reverse=True)
        for book in sort_books[:count]:
            parse_book(book['id'])


def update_index():
    books = load_books()
    for book in (book for book in books.values() if book['gift']):
        for seg in cut_for_search(book['title']):
            dump_index(seg, book['id'])


def search(text, page=0, count=20, sort='date'):
    tmp = []
    index = load_index()
    books = load_books()

    for seg in cut_for_search(text):
        tmp.append(set(index.get(seg, [])))
    if not tmp:
        tmp.append(set())

    books = {_id: books.get(_id) for _id in reduce(lambda a, b: a & b, tmp)}
    gift_books = [book for book in books.values() if book['gift']]  # filter books, because update_index don't auto clean invalid indexes.
    sort_books = sorted(gift_books, key=lambda x: x[sort], reverse=True)
    return sort_books[page * count: page * count + count], len(sort_books)


def get_books(page=0, count=20, sort='date'):
    books = load_books()
    gift_books = [book for book in books.values() if book['gift']]
    sort_books = sorted(gift_books, key=lambda x: x[sort], reverse=True)
    return sort_books[page * count: page * count + count], len(sort_books)


if __name__ == '__main__':
    argv = sys.argv
    if len(argv) > 1 and argv[1] == 'all':
        update_books('all')
    elif len(argv) > 1 and argv[1] == 'new':
        update_books('new')
    elif len(argv) > 1 and argv[1] == 'get':
        parse_book(argv[2])
    else:
        print('Usage: python turing.py all|new|get book_id\n')
        exit(1)
    update_index()
