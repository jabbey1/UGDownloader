<div align="center">
<h1>UGDownloader</h1>
<b>  🎸 Guitar Tab Downloader 🎼 </b><br><br>
    <img src="https://img.shields.io/github/v/release/jabbey1/UGDownloader">
    <img src="https://img.shields.io/github/downloads/jabbey1/UGDownloader/total">
    <img src="https://img.shields.io/github/stars/jabbey1/UGDownloader">
    <img src="https://img.shields.io/github/forks/jabbey1/UGDownloader">
    <img src="https://img.shields.io/github/watchers/jabbey1/UGDownloader">
    
  <br><br>
Use selenium to grab every available user created tablature file from your favorite artists, in the filetype you choose.
  <br><br>
</div>

![Screenshot 2024-10-29 122234](https://github.com/user-attachments/assets/3b3bfea3-de9e-4552-baf2-ec3236b625e2)


## :keyboard: Usage :keyboard:
Entering your **username**, **password**, and an **artist** will open a headless browser to navigate downloading tabs. All available user created tabs for the artist will be downloaded in sequence, letting you do something else.

⚠️ Make sure that you:
- Choose the browser you have installed
- Enter your **user** and **password** exactly ([ultimateguitar](https://www.ultimate-guitar.com/))
- Enter the **artist/search** term with no typos, and with correct capitilization

_If you run into issues with the program getting stuck, try checking/unchecking the "**Bypass**" checkboxes._

Tabs are stored in a folder created next to the .exe, which can be opened via button in the interface. Inside, tabs are stored in folders by Artist name- unless downloaded from a user.

During downloading, extra information is kept to add more info to the filename. Guitar Pro downloads are renamed, while text files are created to the format:
```
Artist - Song name (optional extra title information) - Format (if text) (Version number, Rating score @ Total ratings)
```
**Guitar Pro** example:
```
Adrianne Lenker - My Angel (V1, 4.8@6).gpx
```
**Text** example:
```
Adrianne Lenker - Already Lost - Chords (V1, 4.9@28).txt
```

**Chrome** slightly edges out **Firefox** in terms of speed, but both work well. This moves quicker than a human could, but downloads with large amounts of tabs will need some time to finish.

## 🗄️ Filetypes 🗄️
- **Guitar Pro**
  - **_User created only_** Official files are **not** included.
  - .gp3, .gp4, .gp5, .gpx, .gp
- **Power Tab**
  - .ptb files
- **Text**
  - This includes text **tab**, **chord**, and **bass** tablature.

## :bulb: Other Features :bulb:
> **_search  type 'By'_**

Instead of searching for tabs by Artist, you can download everything created by an individual user by using the `By` dropdown menu. You can also use this menu to download the tabs saved in your account, as 'My Tabs'. You can still select the filetype with either of these methods.

> **_Check for new tabs_**

Using the `Check Artist Tab Count` button will check the number of tabs available online against what you have locally downloaded - allowing you to monitor the arrival of new tabs without doing a full download.

> **_Save a list of artists to download, for later_**

Using the list in the top right corner of the GUI allows you to save artists for later download. You can do this while other downloads are running. Then, copy them from the list for download whenever you want.


## :memo: Config :memo:
You can edit your user info and the `to dl` list inside the `_UGDownloaderFiles` folder.

Entries in the `to dl` list are comma seperated, with no spaces. Here's what the file looks like from the example picture above:
```
,Radiohead,Spectral Wound,Elliott Smith,Big Thief,Boris
```





### Old GUI:

![Untitled picture](https://user-images.githubusercontent.com/9942757/236566975-d5896f6e-6124-44d8-bc4e-4270b584906b.png)
