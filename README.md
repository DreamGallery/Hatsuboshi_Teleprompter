# Hatsuboshi_Teleprompter
Subtitle tool for「学園アイドルマスター」  
1. Convert `adv_xxx_..._xxx.txt` to Aegisub subtile file.
2. Genarated text image based on the adv files, use `OpenCV` to match them with game screen and correct the subtitle timeline.  
(developing)

## Usage

### Simply convert
Put your adv file in the `adv/txt` folder and run with
```
python generate.py
```
You can put a batch of files at the same time and it will convert them at once.  

**Notice:**  
The subtitle converted from adv file may need you to move them in sections according to the situation.  
And the game also have some choices that you will need to check them and the diffenence scenarios that due to your choices. 

### Frame convert
Only for `初星コミュ`, edit the `config.ini` first.<br />
Put recorded video in `video` folder and the recommended resolution is `[1920x1080]`, or you can change the `[Font Config]` in `config.ini` to fit your video (compare in PS is a good idea).<br />
If your resolution ratio is not `16:9`, you may also have to modify the cutting area of frames [here](frame_convert/src/frame_process.py).
#### Install requirements
```
pip install -r requirements.txt
```
**Check and edit adv file**

Extract subtitle line from `adv` file.
```
python adv_extract.py
```
Go to check the file and delete choices (if so) those you didn't select in your video. <br />

**Start match**
```
python main.py
```

Adjust the appropriate threshold is very helpful to the running of this tool.<br />
Maybe sometimes you need to increase the threshold instead of decreasing it.<br />

## How to get the adv files
You can get them from here [Campus-adv-txts](https://github.com/DreamGallery/Campus-adv-txts).  
Or just use the auto generated subtitles here [Campus-adv-ass](https://github.com/DreamGallery/Campus-adv-ass).

## Some translated video
You can find some game story videos with Chinese subtitles here [学园偶像大师同好会](https://space.bilibili.com/2546078)