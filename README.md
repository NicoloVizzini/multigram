# Multigram

Run and automate multiple Telegram instances simultaneously, with support for mini-app automation (Blum, Yescoin, Moneydogs, and more).

<video src="demo.mp4" controls width="600"></video>

## Requirements

- Linux with X11
- Telegram desktop installed at `/opt/Telegram/Telegram`
- Python 3 with dependencies listed in `requirements.txt`
- `wmctrl`, `xdotool`, `Xephyr` (for virtual displays)

```bash
pip install -r requirements.txt
```

## Usage

```bash
./multigram.sh <command> [options]
```

### Options

| Option | Description |
|---|---|
| `-a, --account=NAME` | Name of the account to use |
| `-c, --create` | Create a new account if it doesn't exist |
| `-n, --number=N` | Account number to launch |
| `-f, --folder=DIR` | Folder containing accounts |
| `--no-redirect` | Don't redirect stdout/stderr |
| `--video` | Use a video file instead of screen capture |
| `--dont-click` | Don't click on the screen |
| `--record=FILE` | Record a video while playing |
| `--step` | Step through video frame by frame |

### Commands

| Command | Description |
|---|---|
| `list` | List all available accounts |
| `start` | Launch a new Telegram instance |
| `screenshot` | Take a screenshot of the Telegram window |
| `screen_record` | Record the mini-app window |
| `blum` | Play Blum on one account |
| `blum_all` | Play Blum on all accounts |
| `blum_from_acc` | Play Blum starting from a specific account |
| `check` | Check in on one account |
| `check_all` | Check in on all accounts |
| `farm` | Farm on one account |
| `farm_all` | Farm on all accounts |
| `set_yescoin` | Set up Yescoin on one account |
| `set_yescoin_all` | Set up Yescoin on all accounts |
| `ysetup` | Yescoin full setup on one account |
| `ysetup_all` | Yescoin full setup on all accounts |
| `money_setup` | Moneydogs setup on one account |
| `money_setup_all` | Moneydogs setup on all accounts |
| `rectsel` | Select a rectangle on screen |

### Examples

```bash
# List all accounts
./multigram.sh list

# Start Telegram for account "alice"
./multigram.sh start -a alice

# Play Blum on all accounts
./multigram.sh blum_all

# Check in on all accounts
./multigram.sh check_all
```

## Account Management

Accounts are stored in the `accounts/` directory. Each account has its own Telegram data folder, allowing independent sessions.

Create a new account:
```bash
./multigram.sh start -a myaccount --create
```

## Project Structure

```
multigram/
├── multigram/
│   ├── __main__.py      # Entry point and command dispatch
│   ├── blum.py          # Blum mini-app automation
│   ├── yescoin.py       # Yescoin mini-app automation
│   ├── screen_record.py # Screen capture utilities
│   └── utils.py         # Shared helpers (image matching, clicking)
├── multigram.sh          # Shell launcher
├── Xephyr.sh            # Virtual display helper
└── requirements.txt
```
