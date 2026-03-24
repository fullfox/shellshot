#!/usr/bin/env python3
"""Pipeshot - Capture piped command output as svg/png. Usage: cmd | pipeshot -c 'cmd'"""
import sys, argparse, os
from shellshot import PROMPT, ANSI_clean, save_image


def main():
    parser = argparse.ArgumentParser(description='Pipeshot - Capture piped command output as svg/png')
    parser.add_argument('-c', '--command', help='Command to display in the screenshot', default='')
    parser.add_argument('-o', '--output', help='Output file path (default: screenshot)', default='screenshot')
    parser.add_argument('-t', '--title', help='Window title (default: Terminal)', default='Terminal')
    parser.add_argument('--svg', action='store_true', help='Render as SVG instead of PNG')
    parser.add_argument('-s', '--scale', type=int, help='PNG scale (default: 2)', default=2)
    parser.add_argument('--open', action='store_true', help='Open the screenshot once rendered')
    args = parser.parse_args()

    # Read from stdin
    output = ANSI_clean(sys.stdin.read().rstrip('\n'))
    
    # Build result with prompt + command + output
    ANSI_result = f"{PROMPT}{args.command}\n{output}" if args.command else output

    save_image(ANSI_result, output=os.path.abspath(args.output), title=args.title, png=not args.svg, scale=args.scale, open_file=args.open)


if __name__ == '__main__':
    main()
