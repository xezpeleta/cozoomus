# Cozoomus

Cozoomus handles dynamic license assignations, depending on the scheduled meetings.


```
$ python cozoomus.py

###############################################
#                 COZOOMUS                    #
###############################################
# Wed Apr  1 16:27:07 UTC 2020
[user1@domain.com] Meetings scheduled. License assigned
[user2@domain.com] Meetings scheduled. Nothing to do, already licensed
[user3@domain.com] User whitelisted. License assigned.

~ SUMMARY ~
Users: 30
Whitelisted users: 1
Users with scheduled meetings: 2
Assigned licenses: 3/5
Available licenses: 2/5
```

## Configuration

Configuration is made using environment variables:

| envar                  | required | default value | description                                                                                                                 |
|------------------------|----------|---------------|-----------------------------------------------------------------------------------------------------------------------------|
| ZOOM_API_KEY           |    yes   |               | API KEY from your JWT app. [More info](https://marketplace.zoom.us/docs/guides/getting-started/app-types/create-jwt-app)    |
| ZOOM_API_SECRET        |    yes   |               | API SECRET from your JWT app. [More info](https://marketplace.zoom.us/docs/guides/getting-started/app-types/create-jwt-app) |
| ZOOM_TIME_DELTA        |     -    | 4             | Hours before/after start time of a meeting                                                                                  |
| ZOOM_LICENSES          |     -    | 20            | Total license number                                                                                                        |
| ZOOM_WHITELISTED_USERS |     -    |               | Will keep these users always licensed, regardless their meetings (email addresses separated with whitespaces)               |
| IGNORE_RECURRENT_WITHOUT_TIME | - | True          | Ignore recurrent meetings without time: do not assign licenses if the meeting is a recurrent meeting without time           |
| IGNORE_RECURRENT_WITH_TIME |      | False         | Ignore recurrent meetings with time: do not assign licenses if the meeting is a recurrent meeting with time                 |                                                                                      |

## How to use it

### Running the python script

Install the required packages:

```
pip install -r requirements.txt
```

Set your environment variables:
```
export ZOOM_API_KEY=xxx
export ZOOM_API_SECRET=yyy
```

Run the script:

```
python cozoomus.py
```

### Using Docker

I recommend you to use a file to set your environment variables. For instance, you can create your `.env` file. You can use the template `.env.dist` from this repo:

```sh
mv .env.dist .env
```

Customize the environment variables inside the file:

```
ZOOM_API_KEY=xxx
ZOOM_API_SECRET=yyy
```

Run the script with Docker:

```
docker run --env-file .env --rm -it xezpeleta/cozoomus
```

Or using Docker-Compose:

```
version: '3'

services:
    cozoomus:
        image: xezpeleta/cozoomus
        env_file: .env
        restart: unless-stopped
```

## Daemon mode

You probably need to call this script every 20 minutes (for instance), to keep your user type updated (licensed or basic).

If you are running the Python script directly, you could use CRON:

```
# crontab -e
*/20 * * * python /opt/cozoomus/cozoomus.py >> /var/log/cozoomus.py
```

If you are using **Docker**, you can set the environment variable `DAEMON=true`. Use `SLEEP=600`to specify the time we should wait between the calls (in seconds):

```
# filename: .env
DAEMON=true
SLEEP=600
ZOOM_API_KEY=xxx
ZOOM_API_SECRET=yyy
```
