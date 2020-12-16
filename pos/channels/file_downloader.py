import os
import json
import requests
import platform
from zipfile import ZipFile
from io import BytesIO, StringIO
from clint.textui import progress
from urllib.request import urlopen


# os.system('cd static/')

class Downloader(object):

    store_files = None
    store_img = None
    content = None
    files_data = None
    zip_files = None
    video_files = None
    audio_files = None
    m4v_files = None
    mp4_files = None
    mp3_files = None
    wav_files = None
    pdf_files = None
    wrong_extension = None
    localUrl = ""
    

    current_dir = os.getcwd()
    # print('old current_dir', current_dir)
    new_current_dir = os.path.join(current_dir, 'static')
    # print('after join', new_current_dir)
    os.chdir(new_current_dir)
    new_current_dir = os.getcwd()
    # print("new dir is", new_current_dir)

    headers = {
        'cache-control': "no-cache",
        'content-type': "application/json",
        "Accept": "application/json"
    }

    def createdir(self, AppName):
        # time.sleep(15)
        self.store_files = os.path.join(self.new_current_dir, 'storage')
        # print('sf', store_files)
        if not os.path.exists(self.store_files):
            os.makedirs(self.store_files)
        else:
            pass

        self.store_files = os.path.join(self.store_files, AppName)
        # print('sf', store_files)
        if not os.path.exists(self.store_files):
            os.makedirs(self.store_files)
        else:
            pass

        # images folder
        self.store_img = os.path.join(self.store_files, 'images')
        # print('simg', store_img)
        if not os.path.exists(self.store_img):
            os.makedirs(self.store_img)
        else:
            pass

        # content (videos and zips)
        self.content = os.path.join(self.store_files, 'content')
        # print('content', content)
        if not os.path.exists(self.content):
            os.makedirs(self.content)
        else:
            pass

        self.zip_files = os.path.join(self.content, 'zips')
        # print('content', content)
        if not os.path.exists(self.zip_files):
            os.makedirs(self.zip_files)
        else:
            pass

        self.audio_files = os.path.join(self.content, 'audios')
        # print('content', content)
        if not os.path.exists(self.audio_files):
            os.makedirs(self.audio_files)
        else:
            pass

        self.mp3_files = os.path.join(self.audio_files, 'mp3')
        # print('content', content)
        if not os.path.exists(self.mp3_files):
            os.makedirs(self.mp3_files)
        else:
            pass

        self.wav_files = os.path.join(self.audio_files, 'wav')
        # print('content', content)
        if not os.path.exists(self.wav_files):
            os.makedirs(self.wav_files)
        else:
            pass

        self.video_files = os.path.join(self.content, 'videos')
        # print('content', content)
        if not os.path.exists(self.video_files):
            os.makedirs(self.video_files)
        else:
            pass

        self.mp4_files = os.path.join(self.video_files, 'mp4')
        # print('content', content)
        if not os.path.exists(self.mp4_files):
            os.makedirs(self.mp4_files)
        else:
            pass

        self.m4v_files = os.path.join(self.video_files, 'm4v')
        # print('content', content)
        if not os.path.exists(self.m4v_files):
            os.makedirs(self.m4v_files)
        else:
            pass

        self.pdf_files = os.path.join(self.content, 'docs')
        # print('content', content)
        if not os.path.exists(self.pdf_files):
            os.makedirs(self.pdf_files)
        else:
            pass

        self.wrong_extension = os.path.join(self.content, 'wrong_extensions')
        # print('content', content)
        if not os.path.exists(self.wrong_extension):
            os.makedirs(self.wrong_extension)
        else:
            pass


    def download_files_with_qs(self, download_url, querystring, AppName):
        # print("url is ", download_url)
    
        self.createdir(AppName)
        response = requests.get(download_url, params=querystring, headers=self.headers)
        # print(response)
        result = json.loads(response.content.decode('utf-8'))
        # print(result, type(result))

        for detail in result:
            for key, value in detail.items():
                if key == 'LstFileList':
                    self.files_data = value

        try:
            for data in self.files_data:
                file_url = data["FileUrl"]
                if data["FileType"] == "Thumbnail":
                    path_to_put = os.path.join(
                        self.store_img, str(os.path.basename(file_url)))
                elif data["FileType"] == "Content" and file_url.endswith('.mp4'):
                    path_to_put = os.path.join(
                        self.mp4_files, str(os.path.basename(file_url)))
                elif data["FileType"] == "Content" and file_url.endswith('.MP4'):
                    file_url = file_url.replace('.MP4', '.mp4')
                    path_to_put = os.path.join(
                        self.mp4_files, str(os.path.basename(file_url)))
                elif data["FileType"] == "Content" and file_url.endswith('.m4v'):
                    path_to_put = os.path.join(
                        self.m4v_files, str(os.path.basename(file_url)))
                elif data["FileType"] == "Content" and file_url.endswith('.mp3'):
                    path_to_put = os.path.join(
                        self.mp3_files, str(os.path.basename(file_url)))
                elif data["FileType"] == "Content" and file_url.endswith('.MP3'):
                    file_url = file_url.replace('.MP3', '.mp3')
                    path_to_put = os.path.join(
                        self.mp3_files, str(os.path.basename(file_url)))
                elif data["FileType"] == "Content" and file_url.endswith('.wav'):
                    path_to_put = os.path.join(
                        self.wav_files, str(os.path.basename(file_url)))
                elif data["FileType"] == "Content" and file_url.endswith('.zip'):
                    path_to_put = os.path.join(
                        self.zip_files, str(os.path.basename(file_url)))
                elif data["FileType"] == "Content" and file_url.endswith('.pdf' or '.doc'):
                    path_to_put = os.path.join(
                        self.pdf_files, str(os.path.basename(file_url)))
                elif data["FileType"] == "Content" and file_url.endswith('.png' or '.mpeg' or '.jpg' or '.jpeg'):
                    path_to_put = os.path.join(
                        self.wrong_extension, str(os.path.basename(file_url)))
                try:
                    if file_url == '':
                        continue
                    else:
                        self.localUrl = path_to_put
                        # print("local path is ", self.localUrl)
                        file_to_get = requests.get(
                            file_url, stream=True, timeout=10)
                        with open(path_to_put, "wb") as target:
                            total_length = int(
                                file_to_get.headers.get('content-length'))
                            for chunk in progress.bar(file_to_get.iter_content(chunk_size=1024),
                                                        expected_size=(total_length/1024) + 1):
                                if chunk:
                                    target.write(chunk)
                                    target.flush()

                except requests.exceptions.ConnectionError as ierror:
                    print(" no internet ", ierror)
                    return False

        except requests.exceptions.ConnectionError as e_error:
            print("e_error ", e_error)
            return False

        # print("with qs local ", self.localUrl)
        # return localUrl


    # download("http://devposapi.prathamopenschool.org/Api/AppNodeDetailListByNode", {"id": "1"})


    def download_files_without_qs(self, download_url, AppName):
        self.createdir(AppName)
        response = requests.get(download_url, headers=self.headers)
        print(response)
        result = json.loads(response.content.decode('utf-8'))
        # print(result, type(result))

        try:
            for detail in result:
                file_url = detail['ThumbUrl']
                if file_url.endswith('.png'):
                    path_to_put = os.path.join(
                            self.store_img, str(os.path.basename(detail['ThumbUrl'])))
                    # print(path_to_put)
                    # print(detail, type(detail))
                file_to_get = requests.get(
                            file_url, stream=True, timeout=10)
                with open(path_to_put, "wb") as target:
                        total_length = int(
                            file_to_get.headers.get('content-length'))
                        for chunk in progress.bar(file_to_get.iter_content(chunk_size=1024),
                                                    expected_size=(total_length/1024) + 1):
                            if chunk:
                                target.write(chunk)
                                target.flush()
                        self.localUrl = path_to_put
            # return True
        except requests.exceptions.ConnectionError:
            return False
        
        # print("this is ", self.localUrl)

# download = Downloader()
# download.download_files_with_qs("http://devposapi.prathamopenschool.org/Api/AppNodeDetailListByNode",
#                         {"id": "ee486417-0216-47ec-a493-56622a800503"})
# download.download_files_without_qs("http://devposapi.prathamopenschool.org/api/AppList")
