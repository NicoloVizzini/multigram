"""
Multigram - multiple telegram instances

usage:
    multigram.py <command> [options]

options:
    -h, --help                  shows the help
    -a, --account=NAME          name of the account to launch [default: main]
    -c, --create                create a new account if it doesn't exist

Available commands:
    list                        list all available acconuts
    start                       launch a new telegram instance
"""

import sys
import os
import time
import shlex
from pathlib import Path
from docopt import docopt
from wmctrl import Window

TELEGRAM = '/opt/Telegram/Telegram'
ROOT = Path(__file__).parent
ACCOUNTS = ROOT.joinpath('accounts')
ACCOUNTS.mkdir(exist_ok=True)

def launch_command(*args, bg=False, redirect_null=False):
    cmdline = [shlex.quote(arg) for arg in args]
    cmdline = ' '.join(cmdline)
    if redirect_null:
        cmdline += ' > /dev/null 2>&1'
    if bg:
        cmdline += ' &'
    print(f'EXEC: {cmdline}')
    return os.system(cmdline)

def main():
    options = docopt(__doc__)
    command = options.pop('<command>')
    if command == 'list':
        cmd_list(options)
    elif command == 'start':
        cmd_start(options)
    elif command == 'dev':
        cmd_dev(options)
    else:
        print(f'Invalid command: {command}')
        print(__doc__)
        sys.exit(1)

def cmd_list(options):
    accounts = []
    not_accounts = []
    for child in ACCOUNTS.iterdir():
        is_account = child.joinpath('tdata').exists()
        if is_account:
            accounts.append(child.name)
        else:
            not_accounts.append(child.name)

    accounts.sort()
    not_accounts.sort()
    for name in accounts:
        print(name)

    if not_accounts:
        print('The following seems to be invalid accounts:')
        for name in not_accounts:
            print(name)

def cmd_start(options):
    account = options['--account']
    workdir = ACCOUNTS.joinpath(account)
    if not workdir.exists():
        print(f'Account {account} does not exist')
        if options['--create']:
            print('Creating a new one...')
        else:
            print('Please use --create to automatically create a new one')
            sys.exit(1)
    launch_command(TELEGRAM, '-workdir', str(workdir), bg=True,
                   redirect_null=True)
    reposition_telegram()


def reposition_telegram():
    """
    Wait until the active window is a telegram one, then reposition it to a
    top-left corner.
    """
    def find_window():
        for i in range(10):
            w = Window.get_active()
            print(f'[WINDOW] active window is {w.wm_name} - {w.wm_class}')
            if w.wm_class == 'Telegram.TelegramDesktop':
                print('[WINDOW] found!')
                return w
            else:
                time.sleep(0.5)
        else:
            print('[WINDOW] telegram not found, aborting')
            sys.exit(1)

    w = find_window()
    w.resize_and_move(x=64, y=0, w=1000, h=1500)


if __name__ == '__main__':
    main()
