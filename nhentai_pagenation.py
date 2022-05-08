# -*- coding: utf-8 -*-

import requests
import os
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import sys
import re

import pprint

from soupsieve import match

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"
}

base_save_path = 'H:/いろいろ/images/_new/'
base_url = 'https://nhentai.net'


# ページを探索し、imageのurlListと、titleを取得
def scrape_pages(url):
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')

    gallery_list = []
    
    check_txt = soup.find('div', class_='container index-container').get_text()
    if 'No results' in check_txt:
        print('no result')
        return False, gallery_list

    # 画像が入ってるタグだけ引っ張る
    gallery_list_temp = soup.find_all("div", class_="gallery")           # 大枠
    gallery_list_temp = [i.find('a') for i in gallery_list_temp]
    
    for gallery in gallery_list_temp:
        gallery_url = base_url + gallery.get('href')

        judge = gallery.find('div', class_='caption').get_text().lower()
        # print(judge)

        match judge:
            case judge if '[chinese]' in judge:
                print('pass : {}'.format(gallery_url))
            case judge if '[english]' in judge:
                print('pass : {}'.format(gallery_url))
            case judge if '[中国]' in judge:
                print('pass : {}'.format(gallery_url))
            case _:
                if 'search' in url:
                    search_str = url.split('&page=')[0].split('?q=')[-1]
                    search_str = search_str.replace(r'/', ' ', 5)
                    search_str = search_str.replace(r'+', ' ', 5).lower()

                    # print(search_str.replace(r'+', ' '))
                    if search_str in judge:
                        print('append : {}'.format(gallery_url))
                        gallery_list.append(gallery_url)
                    else:
                        print('pass : {}, title: {}'.format(gallery_url, judge))
                else:
                    print('append : {}'.format(gallery_url))
                    gallery_list.append(gallery_url)

        # if all(map(lambda x: x in judge, ("[Chinese]", "[English]"))):
        #    print('pass : {}'.format(gallery_url))
        # else:
        #    print('append : {}'.format(gallery_url))
        #    gallery_list.append(gallery_url)

    # pprint.pprint(gallery_list)

    return True, gallery_list


# プロセス全般
def process(src_url):
    
    # hajime
    print('start script page: {}'.format(src_url))

    gallery_list = []
    pagenation_check = True
    page_num = 1

    # ページを周回
    while pagenation_check:
        if 'search' in src_url:
            url = src_url + '&page=' + str(page_num)
        elif 'artist' in src_url:
            url = src_url + '?page=' + str(page_num)
        print('check_page : {}'.format(url))

        pagenation_check, g_list = scrape_pages(url)
        gallery_list.extend(g_list)

        # print('pagenation : {}'.format(pagenation_check))
        page_num += 1
    
    print('get_gallery_list: \n{}'.format(gallery_list))

    # テキストに保存
    dl_list_dir = 'download_list'
    text_name = url.split('/')[-2]
    text_name = text_name.replace('?q=', '')
    text_name = re.sub(r'[\\/:*?"<>|]+', '', text_name)
    text_name = text_name.replace(r'+', ' ', 5)
    os.makedirs(dl_list_dir, exist_ok=True)

    with open('{}/{}.txt'.format(dl_list_dir, text_name), 'w') as f:
        for gallery in gallery_list:
            f.write('{}\n'.format(gallery))


def main():
    args = sys.argv

    if len(args) >= 2:
        if '.txt' in args[1]:
            print("get from txt")
            
            # テキストの中身を一行づつ取得
            with open(args[1], mode='r', encoding='utf-8') as file:
                key_list = file.readlines()
                key_list = [li.rstrip() for li in key_list]

            for key in key_list:
                # ここでページごとにダウンロード走らせる
                process(key)

        elif 'https' in args[1]:
            print('get one key')
            process(args[1])
        
        else:
            print('pls args url or txt_path')


if __name__ == '__main__':
    main()
