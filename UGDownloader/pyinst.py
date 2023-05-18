import PyInstaller.__main__

PyInstaller.__main__.run([
    '--windowed',
    '--noconsole',
    '--clean',
    '-F',
    '--add-data=_UGDownloaderFiles/extension_3_4_6_0.crx;_UGDownloaderFiles/',
    'UGDownloader.py'
])
