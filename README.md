# 📷 ShellShot

Generate **screenshots** of **commands output**, purely from **commandline** (only available on zsh for now).

**Shellshot** is a tool made out of two scripts:
- `shellshot.sh`, a wrapper for `shellshot.py` which capture terminal output using the [linux *`script`* command](https://man7.org/linux/man-pages/man1/script.1.html).
- `shellshot.py`, a parser for *`script`* outputs which extract the nth output and render it to SVG or PNG.

## How to install
### Requirements

Install the requirements first with:
```
sudo apt install librsvg2-bin xclip uuid-runtime
```

### Installation
1. Clone repo, make `shellshot.py` reachable from the $PATH and make it executable
```bash
git clone git@github.com:fullfox/shellshot.git
cd shellshot
chmod +x shellshot.py
sudo ln -s "$(pwd)/shellshot.py" /usr/local/bin/shellshot.py
```

2. Append this to **the last line** of your `~/.zshrc` config file
```
source /path/to/shellshot.sh
```

That's it.

## How to use
While in terminal, run the command of your choice, then run `shot`. A screenshot of the previous command output is saved in your `~/Pictures/shellshot/` directory (configure the directory in `shellshot.sh`).

```bash
$ echo -e "\033[1m\033[31mRED \033[32mGREEN \033[34mBLUE"
RED GREEN BLUE
$ shot
Shellshot saved at ~/Pictures/shellshot/shellshot 2024-01-01 00:00:00.png
```

The rendered png:

![shellshot 2024-01-27 14:00:12](https://github.com/fullfox/shellshot/assets/31577231/982d125e-9e01-4755-a7ed-4835322aec78)

If you want to disable automatic outputs recording for security purpose, you can do so by commenting the last line in `shellshot.sh`. Type `record` to temporary enable it again.
Exit the terminal to stop recording outputs.

`shellshot.py` offers many options to customize the prompt, the terminal window name, the range of commands to capture.

Use `!n` to capture the output from the last nth command executed.
Use `n` to capture the outputs from the last nth commands executed.
Use `n:m` to capture the output(s) from the last nth to mth command(s) executed.

Explore these options with the `--help` flag.

```
$ shellshot.py -h
usage: shellshot.py [-h] [-o OUTPUT] [-c COMMAND] [-t TITLE] [--png] [-s SCALE] [--list] [--print] [--hex] [--flagbypass] [--open] [--clipboard] typescript offset

Shellshot Version 1.2 - Parse and export ANSI typescript to svg/png. (https://github.com/fullfox/shellshot)

positional arguments:
  typescript            Path to the ANSI typescript file
  offset                Number of command outputs to process from the end. Use !n to extract a single command. Use a:b to capture a specific range.

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Path for the output image (default: screenshot.png)
  -c COMMAND, --command COMMAND
                        Command(s) matching stdout. Expected in `fc -lIn 0` format.
  -t TITLE, --title TITLE
                        Window title rendered in the screenshot (default: Terminal)
  --png                 Render the screenshot in PNG instead of SVG
  -s SCALE, --scale SCALE
                        Scale of rendered PNGs (default: 2)
  --list                Print all the available outputs and exit
  --print               Print the selected command(s) to console instead of rendering.
  --hex                 With --list specified, print in hexadecimal (for debugging purpose)
  --flagbypass          Ignore the 'donotcapture' flag. (To capture shellshot itself)
  --open                Open the screenshot once rendered
  --clipboard           Copy the screenshot to the clipboard using `xclip`
```

If you find any bug, please create an issue.
