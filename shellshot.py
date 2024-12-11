#!/usr/bin/env python3
import re, sys, string, io, argparse, subprocess, urllib.parse
from rich import text
from rich.console import Console, CONSOLE_SVG_FORMAT
from rich.terminal_theme import TerminalTheme

LIBRSVG2 = True # Set to false to use cairosvg instead for png rendering. Requires `pip install cairosvg`.

# Prompt, configure your PS1 here
PROMPT = "\033[1m\033[95mconsultant$ \033[0m"

# Console theme
theme = ['282c34', 'abb2bf', '3f4451', '4f5666', 'e05561', 'ff616e', '8cc265', 'a5e075', 'd18f52', 'f0a45d', '4aa5f0', '4dc4ff', 'c162de', 'de73ff', '42b3c2', '4cd1e0', 'e6e6e6', 'ffffff']
MAX_WIDTH = 200


banned_output = ["", "\n", "\n\x1b[J"]
banned_sequence = []
def extract_cmd_outputs(input_data):
    # Split different commands based on OSC SEQUENCE
    pattern = r'\x1b\]prefix\x07(.*?)\x1b\]suffix\x07'
    outputs = re.findall(pattern, input_data, flags=re.MULTILINE | re.DOTALL)

    # Remove outputs that contains a banned sequence
    for seq in banned_sequence:
        outputs = [output for output in outputs if not seq in output]

    # Remove ASCII non printable characters
    outputs = [ANSI_clean(output) for output in outputs]

    # Remove script header and footer
    if "Script started" in outputs[0]:
        del outputs[0]
    if "Script done" in outputs[-1]:
        del outputs[-1]

    # Remove empty outputs
    outputs = [output for output in outputs if not output in banned_output]
    return outputs


chars_to_remove = ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07', '\x08', '\x0e', '\x0f', '\x10', '\x11', '\x12', '\x13', '\x14', '\x15', '\x16', '\x17', '\x18', '\x19', '\x1a', '\x1a', '\x1b', '\x1c', '\x1d', '\x1e', '\x1f']
def ANSI_clean(input_data):
    result = input_data

    # Remove OSC sequence
    result = re.sub(r'(\x9d|\x1b)(?!\[)(.)(?:.*?)(\x07|\x9c)', '', result).rstrip()

    # Remove ZSH ending '%'
    result = result.replace("\x1B[1m\x1B[7m%\x1B[27m\x1B[1m\x1B[0m", '')

    # Convert CRLF to LF
    result = result.replace("\r\n", "\n")

    # Handle orphan \r
    result = '\n'.join(line.rstrip().split('\r')[-1].rstrip() for line in result.split('\n'))

    # Remove command return \n
    result = result.rsplit('\n', 1)[0]

    return result


def ANSI_to_svg(ansiText, title):
    richText = text.Text.from_ansi(ansiText)
    width = max([len(l.rstrip()) for l in str(richText).split('\n')])+5
    width = min(width, MAX_WIDTH)
    console = Console(record=True, file=io.StringIO(), width=width)
    console.print(richText)
    console.height = len(richText.wrap(console, width=width))
    SVG_FORMAT = CONSOLE_SVG_FORMAT.replace("<svg","<svg xml:space=\"preserve\"")
    result = console.export_svg(title=title, theme=terminalTheme, code_format=SVG_FORMAT)

    # Remove non printable chars from the list ( often not necessary )
    for char in chars_to_remove:
        result = result.replace(char, '')

    return result


# Misc functions
def _hexToRGB(colourCode: str) -> tuple[int, int, int]:
    return tuple(int(colourCode[i : i + 2], base=16) for i in (0, 2, 4))

terminalTheme = TerminalTheme(
    background=_hexToRGB(theme[0]), foreground=_hexToRGB(theme[1]),
    normal=[_hexToRGB(theme[n]) for n in [2, 4, 6, 8, 10, 12, 14, 16]],
    bright=[_hexToRGB(theme[n]) for n in [3, 5, 7, 9, 11, 13, 15, 17]],
)


def copy_image_to_clipboard(image_path):
    try:
        subprocess.run(["xclip", "-selection", "clipboard", "-t", "image/png", "-i", image_path])
        print("Shellshot copied to clipboard.")
    except:
        print("Copying to clipboard failed, check if xclip is installed.")


def main():
    # Do not capture flag
    print("\033]2;donotcapture\a",end="")

    # Parsing CLI
    parser = argparse.ArgumentParser(description='Shellshot Version 1.2 - Parse and export ANSI typescript to svg/png. (https://github.com/fullfox/shellshot)')
    parser.add_argument('typescript', help='Path to the ANSI typescript file')
    parser.add_argument('offset', nargs='?', default="1", help='Number of command outputs to process from the end. Use .n to extract a single command. Use a:b to capture a specific range.')
    parser.add_argument('-o', '--output', help='Path for the output image (default: screenshot.png)', default='screenshot.png')
    parser.add_argument('-c', '--command', help='Command(s) matching stdout. Expects `fc -lIn 0` format.')
    parser.add_argument('-t', '--title', help='Window title rendered in the screenshot (default: Terminal)',default='Terminal')
    parser.add_argument('--head', type=int, help='Crop n lines from the top of the screenshot')
    parser.add_argument('--png', action='store_true', help='Render the screenshot in PNG instead of SVG')
    parser.add_argument('-s', '--scale', type=int, help='Scale of rendered PNGs (default: 2)', default=2)
    parser.add_argument('--list', action='store_true', help='Print all the available outputs and exit')
    parser.add_argument('--print', action='store_true', help='Print the selected command(s) to console instead of rendering.')
    parser.add_argument('--hex', action='store_true', help='With --list or --print specified, print in hexadecimal (for debugging purpose)', default=False)
    parser.add_argument('--flagbypass', action='store_true', help='Ignore the \'donotcapture\' flag. (To capture shellshot itself)')
    parser.add_argument('--open', action='store_true', help='Open the screenshot once rendered')
    parser.add_argument('--clipboard', action='store_true', help='Copy the screenshot to the clipboard using `xclip`', default=False)
    args = parser.parse_args()

    if not args.flagbypass:
        banned_sequence.append("\x1b]2;donotcapture\a")

    # Open typescript
    try:
        with open(args.typescript, 'r', encoding='utf-8', errors='ignore', newline="") as file:
            ANSIdata = file.read()
    except FileNotFoundError:
        print("Could not open file")
        exit(1)

    # Parse typescript outputs and commands input
    stdouts = extract_cmd_outputs(ANSIdata)
    stdins = ['']*len(stdouts) + args.command.split('\n')
    stdins = stdins[-len(stdouts):]
    
    # List all stdin / stdout for debug purpose when --list
    if args.list:
        for i in range(len(stdouts)):
            print(f"Input {i}: {stdins[i]}")
            print(f"Output {i}:\n")
            if args.hex:
                sys.stdout.write(stdouts[i].encode().hex())
            else:
                indented = "\n".join(["    " + line for line in stdouts[i].splitlines()])
                sys.stdout.write(indented)
            print("")
        exit(0)

    # Extract specified range
    # syntaxes  .3 -> get the third last command/output
    #            3  -> get the three last commands/outputs
    #           3:1 -> get the third and the second last commands/outputs
    try:
        if args.offset != None and args.offset.startswith('.'):
            extract_only_one = True
            start_offset = int(args.offset[1:])
        else:
            extract_only_one = False
            
            if ':' in args.offset:
                start_offset = int(args.offset.split(':')[0])
                end_offset = int(args.offset.split(':')[1])
            else:
                start_offset = int(args.offset)
                end_offset = 0
    except:
        print("Invalid offset")
        exit(1)

    if(start_offset > len(stdouts)):
        print("Command's output not found: Out of range for the given typescript.")
        exit(1)

    if extract_only_one:
        selected_stdins = stdins[-int(start_offset)]
        selected_stdouts = stdouts[-int(start_offset)]
    else:
        if end_offset == 0:
            selected_stdins = stdins[-start_offset:]
            selected_stdouts = stdouts[-start_offset:]
        else:
            selected_stdins = stdins[-start_offset:-end_offset]
            selected_stdouts = stdouts[-start_offset:-end_offset]


    # Merge all ( prompts + stdins + stdouts ) into one final string
    ANSI_result = '\n'.join([ f"{PROMPT}{selected_stdins[i]}\n" + selected_stdouts[i] for i in range(len(selected_stdouts))])
    if args.head:
        ANSI_result = '\n'.join(ANSI_result.splitlines()[:args.head])

    # Print the concat stdout for debug purpose
    if args.print:
        if args.hex:
            sys.stdout.write(ANSI_result.encode().hex())
        else:
            sys.stdout.write(ANSI_result)
        sys.stdout.flush()
        exit(0)

    # Export to image
    output_svg = ANSI_to_svg(ANSI_result, args.title)
    svg_fallback = False
    output_file = None
    if args.png:
        try:
            f = f"{args.output}.png"
            if LIBRSVG2:
                    subprocess.run(f"rsvg-convert -o \"{f}\" -z {args.scale}", input=output_svg, check=True, shell=True, text=True)
            else: # SVG to PNG conversion using cairosvg, if librsvg2-bin not available
                import cairosvg
                cairosvg.svg2png(bytestring=output_svg, write_to=f)
            output_file = f
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            svg_fallback = True

    if not args.png or svg_fallback:
        f = args.output + ".svg"
        with open(f, "w") as file:
            output_file = f
            file.write(output_svg)

    if output_file is not None:
        print(f"Shellshot saved at file://{urllib.parse.quote(output_file)}")
        if args.open:
            subprocess.run(f"open \"{output_file}\"", shell=True)
        if args.clipboard:
            copy_image_to_clipboard(output_file)
            

if __name__ == '__main__':
    main()
