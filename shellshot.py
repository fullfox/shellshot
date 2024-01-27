#!/usr/bin/env python3
import re, sys, string, io, argparse, subprocess
from rich import text
from rich.console import Console, CONSOLE_SVG_FORMAT
from rich.terminal_theme import TerminalTheme

LIBRSVG2 = True # Set to false to use cairosvg instead for png rendering. Requires `pip install cairosvg`.

chars_to_remove = ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07', '\x08', '\x0e', '\x0f', '\x10', '\x11', '\x12', '\x13', '\x14', '\x15', '\x16', '\x17', '\x18', '\x19', '\x1a', '\x1a', '\x1c', '\x1d', '\x1e', '\x1f']

# Console theme
theme = ["282c34", "3f4451", "4f5666", "545862", "9196a1", "abb2bf", "e6e6e6", "ffffff", "e05561", "d18f52", "e6b965", "8cc265", "42b3c2", "4aa5f0", "c162de", "bf4034", "21252b", "181a1f", "ff616e", "f0a45d", "a5e075", "4cd1e0", "4dc4ff", "de73ff"]


def extract_cmd_outputs(input_data):
    # Split different commands based on OSC SEQUENCE
    outputs = re.split(r'(?:\x1b\]\d+;[^\x07]*\x07)+', input_data)

    # Remove ASCII non printable characters
    outputs = [ANSI_clean(output) for output in outputs]

    # Remove script header and footer
    if "Script started" in outputs[0]:
        del outputs[0]
    if "Script done" in outputs[-1]:
        del outputs[-1]

    # Remove empty outputs
    outputs = [output for output in outputs if output != ""]
    return outputs


def ANSI_clean(input_data):
    result = input_data

    # Remove ZSH ending '%'
    result = result.replace("\x1B[1m\x1B[7m%\x1B[27m\x1B[1m\x1B[0m", '')

    # Convert CRLF to LF
    result = result.replace("\r\n", "\n")

    # Remove non printable chars from the list
    for char in chars_to_remove:
        result = result.replace(char, '')

    # Handle orphan \r
    result = '\n'.join(line.split('\r')[-1] for line in result.split('\n'))

    return result.rstrip()


def ANTI_to_svg(ansiText, title):
    width = min(max([len(get_printable(line.rstrip())) for line in ansiText.split('\n')]), 120)

    console = Console(width=width, record=True, file=io.StringIO())
    richText = text.Text.from_ansi(ansiText)
    console.print(richText)
    console.height = len(richText.wrap(console, width=width))
    SVG_FORMAT = CONSOLE_SVG_FORMAT.replace("<svg","<svg xml:space=\"preserve\"")
    return console.export_svg(title=title, theme=terminalTheme, code_format=SVG_FORMAT)



def remove_header(input_data):
    if input_data.count('\n') == 0:
        return input_data
    header, body = input_data.split('\n', 1)
    if header.startswith("Script started"):
        return body
    return input_data

def remove_footer(input_data):
    body, footer = input_data.rsplit('\n', 1)
    if footer.startswith("Script done"):
        return body
    return input_data

# Misc functions
def get_printable(input_str):
    return ''.join(char for char in input_str if char in string.printable)

def _hexToRGB(colourCode: str) -> tuple[int, int, int]:
	return tuple(int(colourCode[i : i + 2], base=16) for i in (0, 2, 4))

terminalTheme = TerminalTheme(
	background=_hexToRGB(theme[0]), foreground=_hexToRGB(theme[5]),
	normal=[_hexToRGB(theme[n]) for n in [1, 8, 11, 9, 13, 14, 12, 6]],
	bright=[_hexToRGB(theme[n]) for n in [2, 18, 20, 19, 22, 23, 21, 7]],
)

def main():
    # Parsing CLI
    parser = argparse.ArgumentParser(description='Parse and export ANSI typescript to svg/png')
    parser.add_argument('typescript', help='Input file path')
    parser.add_argument('-o', '--output', help='Output image path (default: screenshot.png)', default='screenshot.png')
    parser.add_argument('-c', '--command', type=int, help='Number of command output to process, starting from the end (default: 1)', default=1)
    parser.add_argument('-t', '--title', help='Window title rendered in the screenshot (default: Terminal)',default='Terminal')
    parser.add_argument('--png', action='store_true', help='Render the screenshot in PNG instead of SVG')
    parser.add_argument('-s', '--scale', type=int, help='Scale of rendered PNGs (default: 2)', default=2)
    parser.add_argument('--list', action='store_true', help='Print all the available outputs and exit')
    parser.add_argument('--hex', action='store_true', help='With --list specified, print in hexadecimal (For debug purpose)', default=False)
    args = parser.parse_args()

    # Open typescript
    try:
        with open(args.typescript, 'r', newline="") as file:
            ANSIdata = file.read()
    except FileNotFoundError:
        print("Could not open file")
        exit(1)

    # Parse typescript
    outputs = extract_cmd_outputs(ANSIdata)
    if(int(args.command) > len(outputs)):
        print("Command's output not found: Out of range for the given typescript.")
        exit(1)

    if args.list:
        i = len(outputs)+1
        for o in outputs:
            i -= 1
            print(f"Output {i}:\n")
            if args.hex:
                sys.stdout.write(o.encode().hex())
            else:
                indented = "\n".join(["    " + line for line in o.splitlines()])
                sys.stdout.write(indented)
            print("")
        exit(1)

    output = outputs[-int(args.command)]

    # Export to image
    output_svg = ANTI_to_svg(output, args.title)
    if args.png:
        if LIBRSVG2:
            try:
                subprocess.run(f"rsvg-convert -o \"{args.output}\" -z {args.scale}", input=output_svg, check=True, shell=True, text=True)
            except subprocess.CalledProcessError as e:
                print(f"Error: {e}")
        else: # SVG to PNG conversion using cairosvg, if librsvg2-bin not available
            import cairosvg
            cairosvg.svg2png(bytestring=output_svg, write_to=args.output)
    else:
        with open(args.output, "w") as file:
            file.write(output_svg)
    print("Shellshot saved at", args.output)

if __name__ == '__main__':
    main()
