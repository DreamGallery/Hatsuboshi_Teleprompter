# Hatsuboshi_Teleprompter
Subtitle tool for「学園アイドルマスター」  
Convert `adv_xxx_..._xxx.txt` to Aegisub subtile file and CSV file for [imas_tools](https://github.com/imas-tools)'s localization project.

## Installation

1. Clone this repository
2. Install the required dependencies:
```
pip install -r requirements.txt
```

## Usage

### Command Line Interface (CLI)

This tool provides a convenient command line interface for all operations:
```
python main.py --help
```

```bash
Usage: main.py [OPTIONS] COMMAND [ARGS]...

  Convert game txt files to subtitles or CSV with AI translation.

Options:
  --help  Show this message and exit.

Commands:
  ass          Convert txt files to ASS format
  clone        Clone text files from a remote repository to the adv/txt
  convert-all  Convert all TXT files to CSV and ASS format at the same time
  count        Count the number of files
  csv          Convert txt files to CSV format
```
You can get more Commands usage by `python main.py [Commands] --help`.  

If you want to use the AI translator in `csv` commands, don't forget to put your api keys in `.env` file under the folder:
```
OPENAI_API_BASE=your_base_url_here
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=specify_model_to_use
```

**Notice:**  
The subtitle converted from adv file may need you to move them in sections according to the situation.  
And the game also have some choices that you will need to check them and the difference scenarios that due to your choices. 

## Term list
There are some terms used for AI translation in `src/terms.py`.  
```
    {
        "src": "Original",
        "dst": "Translated",
        "info": "Notes",
        "enable": Bool, # Whether to use this term
        "always_include": Bool # Whether to keep this term in prompts. If set to False, it will be added only when appearing in the text.
    },
```
Suggestions for revisions are welcome!

## Processed files
You can get the auto processed ASS and CSV files here [Campus-Story](https://github.com/DreamGallery/Campus-Story) and welcome to proofread the translation file using the provided method here [gakuen-adapted-stories](https://github.com/imas-tools/gakuen-adapted-stories).

## Some translated video
You can find some game story videos with Chinese subtitles here [学园偶像大师同好会](https://space.bilibili.com/2546078)