from zipfile import ZipFile


def find_file_from_zip_regardless_capital(zipfile: ZipFile, filename: str):
    filelist_lower = [x.filename.lower() for x in zipfile.filelist]
    filename_lower = filename.lower()
    idx = filelist_lower.index(filename_lower)

    if idx >= 0:
        return zipfile.filelist[idx].filename
    else:
        return None
