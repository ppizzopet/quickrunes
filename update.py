try:
    from requests import get
    import os
    import time
    from zipfile import ZipFile

    def download_url(url, save_path, chunk_size=200000000):
        r = get(url, stream=True)
        with open(save_path, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)


    def checkVersion():
        request = get(url="https://raw.githubusercontent.com/ppizzopet/quickrunes/main/version.txt")
        data = request.json()
        return str(data)

    newestVer = checkVersion()
    updatefilesurl = f"http://www.github.com/ppizzopet/quickrunes/releases/download/{newestVer}/update.zip"

    print("QuickRunes Updater v1.1")
    print("")
    quickrunesfilespath = input("Enter QuickRunes files path (C:/path/to/files/): ")
    os.chmod(quickrunesfilespath, 777)
    print("Downloading update...")
    download_url(updatefilesurl, f"{quickrunesfilespath}update.zip")
    print("Unpacking file...")
    with ZipFile(f"{quickrunesfilespath}update.zip", 'r') as zipObj:
        zipObj.extractall(path=quickrunesfilespath)
    print("Removing files...")
    os.remove(f"{quickrunesfilespath}update.zip")
    print("Done!")
    time.sleep(5)
except Exception as e:
    print(e)
    time.sleep(5)
