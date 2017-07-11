from datetime import date
import requests
import gzip
import shutil


INFO_FILE = "last_download.txt"
DOWNLOAD_URL = "http://anidb.net/api/anime-titles.xml.gz"
DOWNLOAD_FILE = "anime-titles.xml.gz"
UNZIPPED_FILE = "anime-titles.xml"


class DownloadList:

    def __init__(self):
        self.need_download = self.need_to_download()

    def need_to_download(self):
        try:
            with open(INFO_FILE, "r") as f:
                data = f.readline()
                if len(data) > 0:
                    last_download = date.fromordinal(int(data))
                    time_delta = date.today() - last_download
                    if time_delta.days > 7:
                        return True
                    else:
                        return False
                else:
                    return True
        except FileNotFoundError:
            return True
        return False

    def write_today_ordinal(self):
        with open(INFO_FILE, "w") as f:
            f.write(str(date.today().toordinal()) + "\n")

    def download_list(self):
        request = requests.get(DOWNLOAD_URL, stream=True)
        with open(DOWNLOAD_FILE, "wb") as f:
            for chunk in request.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    def untar_list(self):
        with gzip.open(DOWNLOAD_FILE, 'rb') as f_in, \
             open(UNZIPPED_FILE, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    def get_file(self):
        if self.need_to_download():
            self.write_today_ordinal()
            self.download_list()
            self.untar_list()


download_list = DownloadList()
