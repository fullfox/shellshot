# 📷 ShellShot

Take **screenshots** of the **terminal**, from the **terminal**.

## How to install

1. Install the requirements first with:
```
sudo apt install librsvg2-bin xclip uuid-runtime bat
```
2. Put `shellshot.py` in the $PATH and make it executable.
3. Append this at the end of your `~/.zshrc` config file
```
source /path/to/shell-integration.zsh
source /path/to/shellshot.sh
```

## How to use:
While in terminal, run the command of your choice, then run `shot`. That's it.

**Example:**

```bash
$ echo -e "\033[1m\033[31mRED \033[32mGREEN \033[34mBLUE"
RED GREEN BLUE
$ shot
Shellshot saved at ~/Pictures/shellshot/echo.png
Shellshot copied to clipboard.
```

The rendered png:

![shellshot 2024-01-27 14:00:12](https://github.com/fullfox/shellshot/assets/31577231/982d125e-9e01-4755-a7ed-4835322aec78)

**Syntax:**
- `shot` captures the last command
- `shot N..` captures the last N commands (range)
- `shot N` captures the Nth command back in history

By default, screenshots are saved in `~/Pictures/shellshot/`. Set the env var $SHELLSHOT_EXPORT_DIR to specify another directory.

The generated screenshots can be configured. Check `shellshot.py --help` for more infos.

## How it works ?

Three scripts are used:
- `shell-integration.zsh`, a custom OSC 133 compatible shell integration
- `shellshot.sh`, which captures terminal input/output using [ `script`](https://man7.org/linux/man-pages/man1/script.1.html) and exposes a command `shot` feeding `shellshot.py`.
- And `shellshot.py`, a parser for the generated typescripts, extracting command's inputs/outputs and rendering it to SVG or PNG.


`shellshot.sh` saves all your terminal session inputs/outputs in a file under `~/.shellshot`. This file is deleted when you exit the terminal.

If you want to disable automatic recording of your terminal for security purpose, you can do so by commenting the last line in `shellshot.sh`. Type `record` to temporary enable it again, and `exit` to stop and delete the recording.

## Scripting with `pipeshot.py`

For usage in scripts, `pipeshot.py` can be used as follows:
```bash
cat myfile | pipeshot.py
```

If you want to keep stdout visible for interactivity, use:
```bash
nmap 127.1 2>&1 | tee >(pipeshot.py)
```

(`2>&1` to capture stderr as well)

Check `pipeshot.py --help` for more infos.

## Screenshot files with `fileshot`

To display the content of a file with syntax highlighting, use:
```
fileshot myscript.py
```
It's a `pipeshot.py` wrapper, meaning you can use the same args.