# yt2tg

Small script to send videos or audio from a YouTube channel(s) feed to a Telegram chat.

## Installation

System requirements:
- python >3.5 with pip and virtualenv installed
- youtube-dl
- ffmpeg

```shell script
sudo pip install -r requirements.txt
```

## Usage

First, you need to fill the fields in `config.sample.py` and 
rename the file to `config.py`. 
Then put the script in a crontab and enjoy.

A plausible crontab can be:

`*/5 * * * * /path/to/python /path/to/yt2tg/yt2tg.py`
