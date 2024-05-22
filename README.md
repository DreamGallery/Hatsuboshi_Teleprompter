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
```
Placeholder
```
## How to get the adv files
You can use [DreamGallery/HoshimiToolkit](https://github.com/DreamGallery/HoshimiToolkit) to get them.  
Folked from an Idoly Pride tool [MalitsPlus/HoshimiToolkit](https://github.com/MalitsPlus/HoshimiToolkit)

## Story Video
You can find some game story videos with Chinese subtitles here [学园偶像大师同好会](https://space.bilibili.com/2546078)