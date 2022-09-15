
# Line Bot

My personal LINE Messenger bot

## Features

- Fetch next schedule from Binusmaya
- Get random image from specified subreddit
- Trakt new episode notification


## Environment Variables

To run this project with all of its features, you will need to add the following environment variables to your .env file

`LINE_HOST`

`LINE_CHANNEL_ACCESS_TOKEN`

`LINE_CHANNEL_SECRET`

`BIMAY_TOKEN`

`REDDIT_CLIENT_ID`

`REDDIT_CLIENT_SECRET`

`TMDB_API_KEY`

`SECRET_KEY` (for receiving External Flex requests)

`MONGO_URI`

## Run Locally

Clone the project

```bash
  git clone https://github.com/radityaharya/line-bot
```

Go to the project directory

```bash
  cd line bot
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the server

```bash
  gunicorn --bind '0.0.0.0:8011' app:run
```


## Run Using Docker Compose

To deploy this project run

```bash
  docker compose up -d --build 
```

