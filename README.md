# Cozoomus

Cozoomus assigns/removes ZOOM licenses to users in your organization depending on scheduled meetings.

## Configuration

Configuration is made using environment variables:

| envar                  | required | default value | description                                                                                                                 |
|------------------------|----------|---------------|-----------------------------------------------------------------------------------------------------------------------------|
| ZOOM_API_KEY           |    yes   |               | API KEY from your JWT app. [More info](https://marketplace.zoom.us/docs/guides/getting-started/app-types/create-jwt-app)    |
| ZOOM_API_SECRET        |    yes   |               | API SECRET from your JWT app. [More info](https://marketplace.zoom.us/docs/guides/getting-started/app-types/create-jwt-app) |
| ZOOM_TIME_DELTA        |     -    | 4             | Hours before/after start time of a meeting                                                                                  |
| ZOOM_LICENSES          |     -    | 20            | Total license number                                                                                                        |
| ZOOM_WHITELISTED_USERS |     -    |               | Licensed users (always)                                                                                                     |