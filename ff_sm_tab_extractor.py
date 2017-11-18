#!/usr/bin/python

'''
The MIT License (MIT)

Copyright (c) 2017 Alex Tereschenko <https://github.com/alex-ter>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import json
import webbrowser
import argparse
import time

# Global constants
OUTPUT_FORMAT_PRETTY = 'pretty'
OUTPUT_FORMAT_PLAIN = 'plain'

def main():
    ''' Main function'''
    # Arguments
    arg_parser = argparse.ArgumentParser(description='Extract Firefox URL information from Firefox Session Manager file')
    arg_parser.add_argument('-i', '--input-file', type=argparse.FileType(encoding='utf-8'), default='backup.session',
                            help='Path to Session Manager file, (default is "backup.session" in current dir)')
    arg_parser.add_argument('-f', '--output-format',
                            choices=[OUTPUT_FORMAT_PLAIN, OUTPUT_FORMAT_PRETTY], default=OUTPUT_FORMAT_PLAIN,
                            help=('Format of the output, "%s" (default) is one (latest) URL per line, '
                                  '"%s" adds delimiters and tab history') %(OUTPUT_FORMAT_PLAIN, OUTPUT_FORMAT_PRETTY))
    arg_parser.add_argument('-n', '--no-history', action='store_const', default=False, const=True,
                            help='Do not print out tab history in pretty mode (default is to print)')
    arg_parser.add_argument('-o', '--open-in-browser', action='store_const', default=False, const=True,
                            help=('Open each saved URL in default browser, with split into windows and tabs, '
                                  'according to the Session Manager file (no tab history injected)'))

    try:
        args = arg_parser.parse_args()
    except FileNotFoundError:
        print('Input file not found, please check and try again')
        exit(1)

    # Extract data.
    # Pick just the last line in a file - that's JSON we need.
    json_string = args.input_file.readlines()[-1]
    session_data = json.loads(json_string)

    # Act upon data
    for window in session_data['windows']:
        new_browser_window = True
        print_window_header(args.output_format)
        for tab in window['tabs']:
            # Print
            print_tab(tab, args)
            # ...and open, if requested
            if args.open_in_browser:
                open_tab_in_browser(tab, new_browser_window)
                new_browser_window = False
        print_window_footer(args.output_format)

def print_window_header(output_format):
    '''Prints out window header in pretty mode, does nothing for plain'''
    if output_format == OUTPUT_FORMAT_PRETTY:
        print('======= WINDOW BEGIN =======')

def print_window_footer(output_format):
    '''Prints out window footer in pretty mode, does nothing for plain'''
    if output_format == OUTPUT_FORMAT_PRETTY:
        print('======= WINDOW END =======')

def print_tab(tab, args):
    '''Prints out tab information according to mode selected'''
    if args.output_format == OUTPUT_FORMAT_PRETTY:
        print_tab_formatted(tab, args.no_history)
    elif args.output_format == OUTPUT_FORMAT_PLAIN:
        print_tab_plain(tab)

def print_tab_formatted(tab, no_history):
    '''Prints tab information in pretty mode'''
    print('------- TAB BEGIN -------')
    print('TAB URL: %s' %(get_tab_url(tab),))
    if len(tab['entries']) > 1 and not no_history:
        print('TAB HISTORY (oldest to newest):')
        for entry in tab['entries']:
            print('\t%s - "%s"' %(entry['url'], entry['title']))
    print('------- TAB END -------')

def print_tab_plain(tab):
    '''Prints tab information in plain text mode, only the current URL (no history)'''
    print(get_tab_url(tab))

def open_tab_in_browser(tab, new_browser_window):
    '''Opens the latest URL from a given tab in a default browser'''
    url = get_tab_url(tab)

    if new_browser_window:
        webbrowser.open_new(url)
        # Wait to make sure the window opens and successive tabs are created in it.
        # If not done causes each URL to be opened in separate window.
        time.sleep(5)

    webbrowser.open_new_tab(url)
    # Small delay to prevent host overload or UI freezes
    time.sleep(0.1)

def get_tab_url(tab):
    '''Helper function, returns the newest URL from tab object'''
    return tab['entries'][-1]['url']

if __name__ == '__main__':
    main()
