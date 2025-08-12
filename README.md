## insta-AI-automation

AI-powered Instagram automation that:
- Fetches the latest tech/AI news from email (e.g., TLDR newsletter)
- Extracts links and scrapes article text
- Generates an Instagram-ready caption (with hashtags) using OpenAI
- Creates a DALL·E 3 image and overlays branding/text
- Publishes the post to Instagram
- Logs each run to `logs.csv`

### Features
- **Email ingestion**: IMAP login, find latest email from a sender, extract URLs
- **Content extraction**: Requests-HTML + Selenium fallback
- **AI captioning**: Structured JSON output with title, subtitle, caption, hashtags
- **Image generation**: DALL·E 3 (or Stability API alternative), PIL-based edits
- **Instagram posting**: via `instagrapi`
- **Run modes**: `main/main_ai.py` (with compliance check) and `main/main_general.py`

### Project structure
```text
.
├── config/                # whitelists/blacklists, logs
├── database/db.py         # append run logs to logs.csv
├── emails/fetch.py        # IMAP + HTML parsing helpers
├── images/functions.py    # image prompt + generation + overlay
├── instagram/functions.py # post uploader (instagrapi)
├── main/
│   ├── main_ai.py         # full pipeline with compliance check
│   └── main_general.py    # full pipeline without compliance check
├── text/functions.py      # article scraping + caption generation/check
├── utilities/cost_calculation.py
├── requirements.txt
├── Dockerfile
└── README.md
```

### Prerequisites
- Python 3.11+
- An OpenAI API key with access to `gpt-4o` and `dall-e-3`
- Instagram credentials for `instagrapi`
- Gmail IMAP access (or compatible IMAP provider)

### Quickstart
```bash
git clone <your-fork-or-repo-url>
cd insta-AI-automation
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp example.env .env  # then edit values
python scripts/init_logs.py  # creates logs.csv with headers if missing
python main/main_ai.py
```

### Environment variables
Create a `.env` at repository root:
```env
OPENAI_API_KEY=...
# Optional if using Stable Diffusion API
STABLE_DIFFUSION_KEY=...

# Gmail IMAP
GMAIL_USERNAME=...
GMAIL_PASSWORD=...

# Instagram (instagrapi)
INSTAGRAM_USERNAME=...
INSTAGRAM_PASSWORD=...
```

### Usage
- Run full AI pipeline with compliance check:
```bash
python main/main_ai.py
```
- Run general pipeline:
```bash
python main/main_general.py
```

Results:
- Generated images: `images/generated/`
- Final post images: `images/posts/`
- Run logs: `logs.csv`

### Docker
Build and run:
```bash
docker build -t insta-ai .
docker run --rm \
  --env-file .env \
  -v "$PWD/images":/app/images \
  -v "$PWD/logs.csv":/app/logs.csv \
  insta-ai python main/main_ai.py
```

### Scheduling (cron)
Examples in `main/cronjob_ai.sh` and `main/cronjob_general.sh`. Example crontab:
```cron
0 9 * * * /bin/bash -lc 'cd /path/to/insta-AI-automation && source .venv/bin/activate && python main/main_ai.py >> cron.log 2>&1'
```

### Notes and caveats
- `instagrapi` may require challenge solving the first time; consider storing a session file.
- Gmail IMAP may require an app password.
- The first run must create `logs.csv` with the expected columns (the code appends). You can initialize it by creating an empty CSV with headers:
```csv
main_title,subtitle,post_caption,hashtags,json,date,edited_img_path,published,image_prompt
```
 - The Docker image does not include a browser. The Selenium fallback in `text/functions.py` will not work unless you extend the image with Chrome/Chromedriver.

### Contributing
See `CONTRIBUTING.md`.

### License
MIT. See `LICENSE`.