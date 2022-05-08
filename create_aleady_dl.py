import sys
import pathlib

already_dl_save_path = "already_download"


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


def process(check_dir):
    already_dl_list = check_already_download(check_dir=check_dir)
    text_name = 'already_dl'

    with open('{}/{}.txt'.format(already_dl_save_path, text_name), 'a') as f:
        for gallery in already_dl_list:
            f.write('{}\n'.format(gallery))


def main():
    args = sys.argv

    if len(args) >= 2:
        print('get one key')
        args_dir = args[1].replace('\\', '/') + '/'
        process(args_dir)
        
    else:
        print('pls args url or txt_path')


if __name__ == '__main__':
    main()