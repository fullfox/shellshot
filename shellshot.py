#!/usr/bin/env python3
import re, io, argparse, subprocess, urllib.parse
from rich import text
from rich.console import Console, CONSOLE_SVG_FORMAT
from rich.terminal_theme import TerminalTheme

LIBRSVG2 = True # Set to false to use cairosvg instead for png rendering. Requires `pip install cairosvg`.

# Prompt, configure your PS1 here
PROMPT = "\033[1m\033[95mconsultant$ \033[0m"

# Console theme
theme = ['282c34', 'abb2bf', '3f4451', '4f5666', 'e05561', 'ff616e', '8cc265', 'a5e075', 'd18f52', 'f0a45d', '4aa5f0', '4dc4ff', 'c162de', 'de73ff', '42b3c2', '4cd1e0', 'e6e6e6', 'ffffff']
MAX_WIDTH = 130


def _decode_c_payload(payload):
    # New form: key=value options, command percent-encoded in cmd=.
    # Old form: raw command -> fallback.
    if "cmd=" in payload:
        for opt in payload.split(";"):
            if opt.startswith("cmd="):
                return urllib.parse.unquote(opt[4:])
    return payload


def extract_commands_osc133(input_data):
    """
    Parse typescript using OSC 133 shell integration sequences.
    
    OSC 133 sequence flow:
    - A: Prompt start (with aid=process_id)
    - B: Prompt end / command input start
    - C: Command execution start (contains the actual command!)
    - D: Command finished (with exit code and aid)
    
    The command is embedded in OSC 133;C;cmd=<percent-encoded command>
    (older typescripts carry the raw command instead)
    Between C and D: command output
    """
    commands = []
    
    # Pattern: C;command ... output ... D
    # The command is now embedded in the C sequence itself
    pattern = r'\x1b\]133;C;([^\x07]*)\x07(.*?)\x1b\]133;D[^\x07]*\x07'
    
    matches = re.findall(pattern, input_data, flags=re.DOTALL)
    
    for cmd, output in matches:
        cmd = _decode_c_payload(cmd)
        # Clean the output
        output_clean = ANSI_clean(output)
        
        # Skip empty commands
        if not cmd.strip():
            continue
            
        # Skip script header/footer
        if "Script started" in output_clean or "Script done" in output_clean:
            continue
            
        commands.append({
            'command': cmd.strip(),
            'output': output_clean
        })
    
    return commands


def ANSI_clean(input_data):
    result = input_data
    # Remove OSC sequences
    result = re.sub(r'(\x9d|\x1b)(?!\[)(.)(?:.*?)(\x07|\x9c|\x1b\\)', '', result)
    # Remove ZSH ending '%'
    result = result.replace("\x1B[1m\x1B[7m%\x1B[27m\x1B[1m\x1B[0m", '')
    # Normalize line endings and handle carriage returns
    result = result.replace("\r\n", "\n")
    result = '\n'.join(line.split('\r')[-1].rstrip() for line in result.split('\n'))
    # Remove trailing newline (if any)
    return result.rstrip('\n')


def ANSI_to_svg(ansiText, title):
    richText = text.Text.from_ansi(ansiText)
    width = min(max(len(l.rstrip()) for l in str(richText).split('\n')) + 5, MAX_WIDTH)
    console = Console(record=True, file=io.StringIO(), width=width)
    console.print(richText)
    console.height = len(richText.wrap(console, width=width))
    svg_format = CONSOLE_SVG_FORMAT.replace("<svg", '<svg xml:space="preserve"')
    result = console.export_svg(title=title, theme=TERMINAL_THEME, code_format=svg_format)
    # Remove non-printable control characters
    return re.sub(r'[\x00-\x08\x0e-\x1f]', '', result)


def _hex_to_rgb(code: str) -> tuple[int, int, int]:
    return tuple(int(code[i:i+2], 16) for i in (0, 2, 4))

TERMINAL_THEME = TerminalTheme(
    background=_hex_to_rgb(theme[0]), foreground=_hex_to_rgb(theme[1]),
    normal=[_hex_to_rgb(theme[n]) for n in [2, 4, 6, 8, 10, 12, 14, 16]],
    bright=[_hex_to_rgb(theme[n]) for n in [3, 5, 7, 9, 11, 13, 15, 17]],
)


def copy_image_to_clipboard(image_path):
    try:
        subprocess.run(["xclip", "-selection", "clipboard", "-t", "image/png", "-i", image_path])
        print("Shellshot copied to clipboard.")
    except:
        print("Copying to clipboard failed, check if xclip is installed.")


def main():
    # Parsing CLI
    parser = argparse.ArgumentParser(description='Shellshot Version 2.0 - Parse and export ANSI typescript to svg/png using OSC 133 shell integration. (https://github.com/fullfox/shellshot)')
    parser.add_argument('typescript', help='Path to the ANSI typescript file')
    parser.add_argument('offset', nargs='?', default="1", help='Number of command outputs to process from the end. Use n to extract a single command. Use a..b to capture a specific range.')
    parser.add_argument('-o', '--output', help='Path for the output image (default: screenshot)', default='screenshot')
    parser.add_argument('-t', '--title', help='Window title rendered in the screenshot (default: Terminal)',default='Terminal')
    parser.add_argument('--head', type=int, help='Crop n lines from the top of the screenshot')
    parser.add_argument('--svg', action='store_true', help='Render the screenshot in SVG instead of PNG')
    parser.add_argument('-s', '--scale', type=int, help='Scale of rendered PNGs (default: 2)', default=2)
    parser.add_argument('--list', action='store_true', help='Print all the available commands and outputs and exit')
    parser.add_argument('--print', action='store_true', help='Print the selected command(s) to console instead of rendering.')
    parser.add_argument('--open', action='store_true', help='Open the screenshot once rendered')
    parser.add_argument('--clipboard', action='store_true', help='Copy the screenshot to the clipboard using `xclip`', default=False)
    args = parser.parse_args()

    # Open typescript
    try:
        with open(args.typescript, 'r', encoding='utf-8', errors='ignore', newline="") as file:
            ANSIdata = file.read()
    except FileNotFoundError:
        print("Could not open file")
        exit(1)

    ANSI_result = process_typescript(ANSIdata, args)

    if args.head: # crop
        ANSI_result = '\n'.join(ANSI_result.splitlines()[:args.head])

    if args.print:
        print(ANSI_result, end='')
        exit(0)

    args.png = not args.svg  # Convert --svg flag to png boolean for save_image
    save_image(ANSI_result, args)


def process_typescript(ANSIdata, args):
    commands = extract_commands_osc133(ANSIdata)
    
    if not commands:
        print("No commands found in typescript. Make sure OSC 133 shell integration is enabled.")
        exit(1)
    
    # List all commands when --list
    if args.list:
        for i, cmd in enumerate(commands):
            print(f"Command {i}: {cmd['command']}")
            print(f"Output {i}:")
            print("\n".join("    " + line for line in cmd['output'].splitlines()))
            print()
        exit(0)

    # Offset Syntaxes:
    #   3       -> Get the third last command/output
    #   3..     -> Get commands/outputs from the third last to the most recent
    #   3..1    -> Get commands/outputs from the third last to the second last
    try:
        if ".." in args.offset:
            offsets = args.offset.split("..")
            start_offset = int(offsets[0]) if offsets[0] else None
            end_offset = int(offsets[1]) if len(offsets) > 1 and offsets[1] else 0

            # Validate the range
            if start_offset is None or start_offset <= end_offset:
                print("Invalid range: start_offset must be specified and greater than end_offset")
                raise ValueError("Invalid range")
        else:
            start_offset = int(args.offset)
            end_offset = start_offset - 1  # Single command: slice of 1
    except:
        print("Invalid offset")
        exit(1)

    if start_offset > len(commands):
        print("Command's output not found: Out of range for the given typescript.")
        exit(1)

    selected_commands = commands[-start_offset:] if end_offset == 0 else commands[-start_offset:-end_offset]

    # Merge all ( prompts + commands + outputs ) into one final string
    ANSI_result = '\n\n'.join([
        f"{PROMPT}{cmd['command']}\n{cmd['output']}" 
        for cmd in selected_commands
    ])
    return ANSI_result


def save_image(ANSI_result, args=None, output='screenshot', title='Terminal', png=False, scale=2, open_file=False, clipboard=False):
    # Support both args object and individual parameters
    if args:
        output = args.output
        title = args.title
        png = args.png
        scale = args.scale
        open_file = getattr(args, 'open', False)
        clipboard = getattr(args, 'clipboard', False)
    
    output_svg = ANSI_to_svg(ANSI_result, title)
    
    if png:
        output_file = f"{output}.png"
        try:
            if LIBRSVG2:
                subprocess.run(f'rsvg-convert -o "{output_file}" -z {scale}', input=output_svg, check=True, shell=True, text=True)
            else:
                import cairosvg
                cairosvg.svg2png(bytestring=output_svg, write_to=output_file)
        except subprocess.CalledProcessError as e:
            print(f"PNG conversion failed: {e}, falling back to SVG")
            png = False
    
    if not png:
        output_file = f"{output}.svg"
        with open(output_file, "w") as f:
            f.write(output_svg)

    print(f"Saved at file://{urllib.parse.quote(output_file)}")
    if open_file:
        subprocess.run(f'open "{output_file}"', shell=True)
    if clipboard:
        copy_image_to_clipboard(output_file)
            

if __name__ == '__main__':
    main()
