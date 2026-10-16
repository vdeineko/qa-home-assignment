# Sports Betting QA Automation

Automation for the Single Bet Placement feature of
`https://qae-assignment-tau.vercel.app/`.

**Stack:** Python 3.10+ · Selenium WebDriver 4 · Pytest · requests

## Tests Layers
- Api
- UI(e2e)

## Project layout

```
automation/
├── conftest.py            # fixtures: config, API client, balance reset (before/after),
│                          # upcoming match, WebDriver, screenshot-on-failure hook
├── pytest.ini             # markers (api, ui, smoke) and default options
├── requirements.txt       # pinned dependencies
├── .env.example           # template for local settings
├── src/
│   ├── config.py          # settings from environment / .env
│   ├── utils.py           # parse amounts like "Balance: €120.00"
│   ├── api/
│   │   └── betting_api.py # thin requests client; returns requests.Response
│   └── pages/             # Page Object Model
│       ├── base_page.py   # explicit-wait helpers
│       ├── match_list_page.py
│       ├── bet_slip.py
│       └── receipt_modal.py
└── tests/
    ├── api/test_stake_above_balance.py
    └── ui/test_place_bet_e2e.py
```

## Setup

You need Python 3.10+ and desktop Chrome. Selenium Manager (part of Selenium 4)
downloads a matching ChromeDriver automatically.

```bash
cd automation
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Settings

All settings come from environment variables or a local `.env` file (git-ignored):

| Variable | Default | Meaning |
|----------|---------|---------|
| `USER_ID` | — (required) | Issued user id; sent as `x-user-id` and `?user-id=` |
| `BASE_URL` | `https://qae-assignment-tau.vercel.app` | App under test |
| `HEADLESS` | `true` | `false` to watch the browser |
| `TIMEOUT` | `15` | Explicit-wait timeout in seconds |

```bash
cp .env.example .env      # then set USER_ID
```

## Running

```bash
pytest                    # everything
pytest -m api             # API only (no browser)
pytest -m ui              # UI only
pytest -m smoke           # happy path only
```

Headed run: `HEADLESS=false pytest -m ui`.
