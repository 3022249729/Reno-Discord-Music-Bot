# Reno Music Bot
A Python Discord bot that plays music in your voice channel.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
  
## Installation
### Step 1: Install Python
  1. Download the lastest Python installer from the [official website](https://www.python.org/downloads/).
  2. Run the installer and install Python.

### Step 2: Install required libraries
  1. Open Windows cmd/Terminal.
  2. Right click onto the folder and copy the path to folder.
  3. Run the following command, replace `path` with the actual path to the folder.
```bash
pip install -r /path/requirements.txt
```
  4. If you're having trouble finding the path, you can run the following command instead.
 ```bash
pip install discord.py PyNaCl yt-dlp
```

### Step 3: Install FFmpeg
#### Windows
  1. Download the latest build of FFmpeg from the [official website](https://ffmpeg.org/download.html).
  2. Extract the downloaded file at the root of C drive or any folder of your choice.
  3. Rename the extracted folder to "ffmpeg".
  4. Open the Windows search bar, type in system variables, then hit enter.
  5. Click on the `Edit the system environment variables`.
  6. Go to `User variables`, select `Path` and click the `Edit`" button.
  7. Click `New` on the side menu.
  8. Add the path to the extracted ffmpeg folder, then add \bin at the back of the path. For example:
```bash
C:\ffmpeg\bin
```

#### macOS
  1. Open Terminal.
  2. Install Brew by running the following command. If you have Brew on your device already, skip this step.
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
  3. Install FFmpeg via Brew by running the following command.
```bash
brew install ffmpeg
```

#### Linux
  1. Run the following commands one-by-one.
```bash
sudo apt update && sudo apt upgrade
sudo apt install ffmpeg
```

### Step 4: Install Opus
  This step should be for Mac users only. If you're on non-Mac systems and are experiencing issue with Opus, try the steps below.
  1. Download the latest stable release of Opus from the [official website](https://opus-codec.org/downloads/).
  2. Extract the downloaded file.
  3. Open cmd/Terminal.
  4. Run `cd path` to the extracted folder, replace the `path` with the actual path of the folder.
  5. Run the following commands one-by-one. Commands might take a while to run.
```bash
./configure
make
make install
```
  6. If `make install` generates error, try running the following.
```
sudo make install
```

## Usage
**IMPORTANT:** Host the bot first before inviting the bot to any servers!
### Launching the Bot
  1. Open `.env` file and replace `YOUR_TOKEN` with your bot token.
  2. Open cmd/Terminal.
  3. Run the bot with the command:
```bash
python main.py
```

### Commands
The default command prefix for the bot is `.`, [argument] are optional, &lt;argument&gt; are required.

Below is the list of all the commands for the bot:
| Command               | Aliases             | Description                                                                                       |
|-----------------------|---------------------|---------------------------------------------------------------------------------------------------|
| .play [URL/keyword]   | `.p`                | Play audio from the provided URL/keyword.                                                         |
| .skip                 | `.s` `.next`        | Skip the current song.                                                                            |
| .pause                |                     | Pause the music.                                                                                  |
| .resume               |                     | Resume the music.                                                                                 |
| .queue [page]         | `.q`                | Show the list of queued songs.                                                                    |
| .shuffle              |                     | Shuffle the queue.                                                                                |
| .remove &lt;index&gt; | `.rm` `.dl`         | Remove a song from the queue at the specified index. Use -1 to remove the last song in the queue. |
| .jump &lt;index&gt;   | `.j`                | Jump to the song at the specified index. Use -1 to jump to the last song in the queue.            |
| .nowplaying           | `.np`               | Show the information about the song currently playing.                                            |
| .lyrics               |                     | Show the lyrics of the song currently playing.                                                    |
| .loopsong             | `.ls`               | Enable/disable loop song.                                                                         |
| .loopqueue            | `.lq`               | Enable/disable loop queue.                                                                        |
| .leave                |  `.dc`              | Disconnect from the current voice channel.                                                        |
| .ping                 |                     | Show the latency of the bot.                                                                      |
