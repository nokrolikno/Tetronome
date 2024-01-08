import gdown
import os
import time


def main():
    folder_path = './images/'

    test = os.listdir(folder_path)

    for images in test:
        if images.endswith(".png"):
            os.remove(os.path.join(folder_path, images))

    url = 'https://drive.google.com/drive/folders/1Xgj_iqSfKlOmSCnVBMeH_4Z2keZJjoGE?usp=drive_link'
    if url.split('/')[-1] == '?usp=sharing':
        url = url.replace('?usp=sharing', '')

    flag = 0
    finish_try = 5

    while flag != finish_try:
        try:
            time.sleep(10)
            gdown.download_folder(url, quiet=False, use_cookies=True)
            break
        except:
            pass
        flag += 1


if __name__ == '__main__':
    main()
