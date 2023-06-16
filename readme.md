
# HemaRatings Discord Bot

Discord bot for https://hemaratings.com


## Invite Bot to your server

To invite bot follow this link:

https://discord.com/api/oauth2/authorize?client_id=1085532549650059264&permissions=2147503104&scope=applications.commands%20bot

Use with command `/hemaratings <Name>`


## Features

- Show embed with fencer stats
- 🤷‍♀️


## Screenshots

![Embed](http://dl.bdcode.eu/hemaratings.png)


## Installation

1. Create new discord application and setup Bot:
https://discord.com/developers/applications

2. Create enviroment and setup application key:

```bash
  cp .env.example .env
```

.env file:
```
  DISCORD_API_KEY= # Discord API key
```

3. Install Hemaratings with python:

```bash
  pip install -r requirments.txt  
  python hemaratings.py
```
    
## License

[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)

