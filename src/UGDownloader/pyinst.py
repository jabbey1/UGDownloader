# flake8: noqa: E501
# import PyInstaller.__main__
# pysimplegui
# PyInstaller.__main__.run([
#     '--windowed',
#     '--noconsole',
#     '--clean',
#     '-F',
#     '--add-data=_UGDownloaderFiles/extension_3_4_6_0.crx;_UGDownloaderFiles/',
#     'UGDownloader.pyw'
# ])
# customtkinter not working
# PyInstaller.__main__.run([
#     '--noconfirm',
#     '--windowed',
#     '--noconsole',
#     '--clean',
#     '--onedir',
#     '--add-data=_UGDownloaderFiles/extension_3_4_6_0.crx;_UGDownloaderFiles/',
#     'UGDownloader.pyw'
# ])

# pyinstaller --noconfirm --onefile --windowed --icon "C:/Users/jake/AppData/Roaming/JetBrains/PyCharmCE2023.1/scratches/icons8-python-64.ico" --clean --add-data "C:/Users/jake/PycharmProjects/UGDownloader/venv/Lib/site-packages/customtkinter;customtkinter/" --add-data "C:/Users/jake/PycharmProjects/UGDownloader/UGDownloader/_UGDownloaderFiles/extension_3_4_6_0.crx;_UGDownloaderFiles/"  "C:/Users/jake/PycharmProjects/UGDownloader/UGDownloader/UGDownloader.pyw"


## --windowed
# pyinstaller --noconfirm --onefile  --clean  --log-level=DEBUG --paths "C:/Users/user/Downloads/UGDownloader/src/UGDownloader" --paths "C:/Users/user/Downloads/UGDownloader/src/UGDownloader/_UGDownloaderFiles" --add-data "C:/Users/user/Downloads/UGDownloader/src/UGDownloader/_UGDownloaderFiles/config.ini;_UGDownloaderFiles/" --add-data "C:/Users/user/anaconda3/envs/myenv/Lib/site-packages/customtkinter;customtkinter/" --add-data "C:/Users/user/Downloads/UGDownloader/src/UGDownloader/_UGDownloaderFiles/extension_3_4_6_0.crx;_UGDownloaderFiles/" "C:/Users/user/Downloads/UGDownloader/src/UGDownloader/UGDownloader.pyw"