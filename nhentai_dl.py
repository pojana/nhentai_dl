# -*- coding: utf-8 -*-

import requests
import os
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import sys
import re
import pathlib

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"
}

base_save_path = 'H:/いろいろ/images/_new/'
already_download_dir = 'already_download'


# マルチスレッドでダウンロードする
def save_image_multithread(url_list, save_path):
    data_list = [[]]

    # マルチスレッドで送るデータを整形する
    for i, url in enumerate(url_list):
        data_list.append([save_path + url.split('/')[-1], url])

    data_list.remove([])

    # print('save multies')
    # pprint.pprint(data_list)

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(save_image, data_list)


# urlから画像をダウそして、保存する
# data[0] -> saveするフルパス
# data[1] -> url
def save_image(data):
    img = requests.get(data[1], headers=headers)

    if img.status_code == 200:
        print('response: {}, filename: {}, url: {}'.format(
            str(img.status_code), data[0], data[1]
        ))

        with open(data[0], 'wb') as file:
            file.write(img.content)

    else:
        print('!Failed! response: {}, filename: {}, url: {}'.format(
            str(img.status_code), data[0], data[1]
        ))


# ページを探索し、imageのurlListと、titleを取得
def scrape_pages(url):
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')

    # フォルダ名を引っ張る
    temp = soup.find("div", id="info")
    if temp.find("h2", class_="title") is None:
        temp = temp.find("h1", class_="title")
    else:
        temp = temp.find("h2", class_="title")
    title = temp.find("span", class_="pretty").get_text()
    title = '{}  ({})'.format(title, url.split('/')[-2])
    title = re.sub(r'[\\/:*?"<>|]+', '', title)
    print(title)

    # 画像が入ってるタグだけ引っ張る
    image_tag = soup.find("div", class_="thumbs")              # 大枠
    image_list = [i.get('src') for i in image_tag.find_all('img')]  # imgタグ
    image_list = dict.fromkeys(image_list)                          # url重複削除

    # urlじゃあない子を消す & t.jpg, t.pngをリプレース
    image_list = [i for i in image_list if 'https' in i]
    image_list = [i.replace('t.jpg', '.jpg') for i in image_list]
    image_list = [i.replace('t.png', '.png') for i in image_list]
    image_list = [i.replace('t.webp', '.webp') for i in image_list]
    image_list = [i.replace('https://t', 'https://i') for i in image_list]

    # タイトルの画像を引っ張る
    # title_img = image_tag.find("a", class_='image').get('href')
    # image_list.insert(0, title_img)

    # /revision で分割し、前半だけぶち取る
    # image_list = [i.split('/revision')[0] for i in image_list]

    print('title: {}'.format(title))
    print('len: {}'.format(len(image_list)))

    # pprint.pprint(image_list)

    return title, image_list


# プロセス全般
def process(base_url, save_path):
    
    # hajime
    # print('start script page: {}'.format(base_url))

    # ページからimageのリストと、titleを取得
    title, url_list = scrape_pages(base_url)

    # 保存するフォルダを作成
    save_path = save_path + title + '/'
    os.makedirs(save_path, exist_ok=True)

    # マルチスレッドでダウンロード
    save_image_multithread(url_list=url_list, save_path=save_path)

    # owari
    print('complete script page: {}'.format(base_url))


def check_already_download(check_dir):
    posts_list = []
    file_list = list(pathlib.Path(check_dir).glob('*'))

    for f in file_list:

        tag = str(f.name).split('  (')[-1].replace(')', '')

        try:
            posts_list.append(tag)
        except ValueError:
            print(tag)
                
    # print(posts_list)
    return posts_list


def check_already_download_frm_txt(check_dir):
    posts_list = []
    txt_list = list(pathlib.Path(check_dir).glob('*.txt'))

    for txt in txt_list:
        key_list = []

        with open(txt, mode='r', encoding='utf-8') as file:
            key_list = file.readlines()
            key_list = [li.rstrip() for li in key_list]

        try:
            posts_list.extend(key_list)
        except ValueError:
            print('adderror')
                
    # print(posts_list)
    return posts_list


def dl_from_txt(txt_name):
    # テキストの中身を一行づつ取得
    with open(txt_name, mode='r', encoding='utf-8') as file:
        key_list = file.readlines()
        key_list = [li.rstrip() for li in key_list]

    # テキストの名前（著者名）
    txt_name = txt_name.split('\\')[-1].replace('.txt', '')
    save_path = base_save_path + txt_name + '/'
    os.makedirs(save_path, exist_ok=True)

    aleady_dl_list = check_already_download(save_path)

    aleady_dl_list.extend(check_already_download_frm_txt(already_download_dir))

    for i, key in enumerate(key_list):
                
        check_key = key.split('/')[-2]
        # print('key: {}'.format(check_key))
        # print(aleady_dl_list)

        if [i for i in aleady_dl_list if check_key in i]:
            print('already download :{}/{}: {}'.format(i, len(key_list), key))
        else:
            # ここでページごとにダウンロード走らせる
            print('{}/{}: {}'.format(i, len(key_list), key))
            process(key, save_path)


def main():
    args = sys.argv

    if len(args) >= 2:
        if '.txt' in args[1]:
            print("get from txt")

            dl_from_txt(args[1])

        elif 'https' in args[1]:
            print('get one key')
            process(args[1], base_save_path)
        
        else:
            print('please one url or txt path')
    
    else:
        txt_list = list(pathlib.Path('download_list').glob('*.*'))

        for txt in txt_list:
            dl_from_txt(str(txt))


if __name__ == '__main__':
    main()
    # list_len = 66
    # book_list = ['https://nhentai.net/g/243807/']

    # for book in book_list:
    #     process(book)

    # os.makedirs(file_name, exist_ok=True)

    # for i in range(63, list_len):
    #     print(i)
    #     download_img(base_url + str(i) + '.jpg', file_name + '/' + str(i) + '.jpg')

