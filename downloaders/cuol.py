import os
import logging
import re
import subprocess

import requests

from bs4 import BeautifulSoup

CUOL_PAT = re.compile("https://vfs-dcp.cuol.ca/([0-9]+)/(.*)/(.*).mp4\+([0-9]+).ts")

def getLength(filename):
    try:
        result = subprocess.Popen(["ffprobe", filename],
                                stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        
        ffprobeOutput = [x for x in result.stdout.readlines() if "Duration" in str(x)][0].decode("utf-8")
    except:
        print("Errored out at file:", filename)
    return float(re.findall(r"Duration: 00:00:([0-9\.]+)", ffprobeOutput)[0])

def _increment_link(link, increment):
    return re.sub(CUOL_PAT, r"https://vfs-dcp.cuol.ca/\1/\2/\3.mp4+%i.ts" % (increment,), link)

def download(link, fname, **passedArgs):
    logging.info("Received link of '%s' from '%s" % (link, link,))
    increment = 0
    finished = False
    fLength = 0

    tempName = "%s.ts.tmp" % (fname,)
    switch = True
    with open(tempName, 'wb') as f:
        while True:
            increment += fLength
            switch = not switch
            newLink = _increment_link(link, increment)
            currentDownloadFileName = tempName + ".current.ts"
            tmpFile = open(currentDownloadFileName, "wb")
            while True:
                try:
                    download = requests.get(newLink, stream=True, timeout=10)
                    break
                except Exception as e:
                    logging.error(
                        "Connection timed out while downloading block %i. With error %s"
                        % (increment, str(e),)
                    )
            if download.status_code == 200:
                if int(download.headers["content-length"]) > 10000:
                    tmpFile.write(download.content)
                    tmpFile.close()
                    fLength = int(getLength(currentDownloadFileName) * 1000 + 2)
                    os.remove(currentDownloadFileName)
                    f.write(download.content)
                    logging.info("Finished writing increment #%i" % (increment))
                    finished = True
                else:
                    break
            else:
                logging.error("FAILED to download increment #%i" % (increment))
                break

    if finished:
        if 'convert' in passedArgs and passedArgs['convert']:
            try:
                subprocess.run(['ffmpeg', '-i', tempName, '%s' % (fname,)])
            except:
                print("Please install FFMPEG")
                return False
            os.remove(tempName)
        else:
            os.rename(tempName, fname)
            return True

matching_urls = [
    {
        'urls': [
            r"https://vfs-dcp.cuol.ca/([0-9]+)/(.*)/(.*).([0-9]+).mp4\+([0-9]+).ts",
        ],
        'function': download,
    }
]