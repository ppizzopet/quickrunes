try:
    from requests import get
    import os
    import time
    import patoolib

    def download_url(url, save_path, chunk_size=128):
        r = get(url, stream=True)
        with open(save_path, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)


    def checkVersion():
        request = get(url="https://raw.githubusercontent.com/ppizzopet/quickrunes/main/version.txt")
        data = request.json()
        return str(data)


    newestVer = checkVersion()
    updatefilesurl = f"http://www.github.com/ppizzopet/quickrunes/releases/download/{newestVer}/update.rar"

    print("QuickRunes Updater v1")
    print("")
    quickrunesfilespath = input("Enter QuickRunes files path (C:/path/to/files/): ")
    print("Downloading update...")
    download_url(updatefilesurl, f"{quickrunesfilespath}update.rar")
    print("Unpacking file...")
    patoolib.extract_archive(f"{quickrunesfilespath}update.rar", outdir=f"{quickrunesfilespath}")
    print("Removing files...")
    os.remove(f"{quickrunesfilespath}update.rar")
    print("Done!")
    time.sleep(5)
except Exception as e:
    print(e)
    time.sleep(5)
