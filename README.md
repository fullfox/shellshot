# 📷 ShellShot

Generate **screenshots** of **previous commands output**, purely from **commandline** (wrapper only available for zsh for now).

**Shellshot** is a tool made out of two scripts:
- `shellshot.sh`, a wrapper for `shellshot.py` which capture terminal output using the [linux *`script`* command](https://man7.org/linux/man-pages/man1/script.1.html).
- `shellshot.py`, a parser for *`script`* outputs which extract the nth output and render it to SVG or PNG.

## How to install
### Requirements

The tool requires librsvg2-bin. Install it with
```
sudo apt install librsvg2-bin
```
### Installation
Move `shellshot.py` in the $PATH and append

```
source /path/to/shellshot.sh
```
to your `~/.zshrc` config file.

## How to use
While in terminal, run the command of your choice, then run `shot`. A screenshot of the previous command output is saved in your `~/Pictures/shellshot/` directory (configure the directory in `shellshot.sh`).

```bash
$ echo -e "\033[1m\033[31mRED \033[32mGREEN \033[34mBLUE"
RED GREEN BLUE
$ shot
Shellshot saved at ~/Pictures/shellshot/shellshot 2024-01-01 00:00:00.png
```

The rendered png:

![shellshot 2024-01-27 11:29:10 | ee](https://github.com/fullfox/shellshot/assets/31577231/4af2a590-1be5-46c8-be35-1f23e704d243)

If you want to disable automatic outputs recording for security purpose, you can do so by commenting the corresponding line in `shellshot.sh`.
To start recording while in CLI, simply type `record`. Exit the terminal to stop recording outputs.

You can also directly use the `shellshot.py` script which offers many options (save to svg, extract the nth last previous output etc...).

```
$ shellshot.py -h
usage: shellshot.py [-h] [-o OUTPUT] [-c COMMAND] [-t TITLE] [--png]
                    [-s SCALE] [--list] [--hex]
                    typescript

Parse and export ANSI typescript to svg/png

positional arguments:
  typescript            Input file path

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output image path (default: screenshot.png)
  -c COMMAND, --command COMMAND
                        Number of command output to process, starting from the
                        end (default: 1)
  -t TITLE, --title TITLE
                        Window title rendered in the screenshot (default:
                        Terminal)
  --png                 Render the screenshot in PNG instead of SVG
  -s SCALE, --scale SCALE
                        Scale of rendered PNGs (default: 2)
  --list                Print all the available outputs and exit
  --hex                 With --list specified, print in hexadecimal (For debug
                        purpose)
```

If you find any bug, please create an issue.
