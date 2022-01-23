# DRIB: Discord Reddit Integrator Bot

## <div align=right> [Video demo over here!](https://youtu.be/knVU6Ff3YDg)

# Meet Drib!

Do you ever just have those occasions when your friends are talking about the trending Reddit posts, but you have no idea about it and don't feel like leaving the confines of your Discord server? This is where DRIB comes into action: designed to help link Reddit and Discord through a few simple, but powerful commands, DRIB allows you to pull posts from Reddit and post them in your Discord server.


# Setup

The code provided over here won't actually work on its own, as you'll need API tokens from both Discord and Reddit. Provided alongside is ``.env`` file that has spaces open for you to insert your own API tokens. 

- `DISCORD_TOKEN` is the only one that requires a token from Discord, provided over [here](https://discord.com/developers/applications). You'll need to register an application and then check the Bot tab, where a Bot token will be provided.
  
- The fields `CLIENT_ID`, `CLIENT_SECRET` can be obtained from [here](https://www.reddit.com/prefs/apps), after you create a new app. `USER_AGENT` has to be provided in the format:
    >```'platform':'appname':vx.x.x (by u/'Username')```

After you type these values in the `.env` file, that's it! The program should be good to go.

# Files

Before we get into the meat of the app, here's a quick overview of what each file does:

- [.env](.env), as mentioned above, stores 'environment' values. This helps increase the security of the app; your auth tokens shouldn't actually be visible to anyone, since they allow anyone to abuse your application and incur charges on it. Using `python-dotenv`, we can load the values in the .env folder instead of having to hard-code it into `bot.py`. 
  
- [requirements.txt](requirements.txt) is a simple requirements file that lists out all the top-level dependencies required for the program to work. Any subdependencies *should* be automatically installed by pip. If you have pip installed, run this in a terminal window:

    > `pip -r requirements.txt` 

- [runtime.txt](runtime.txt) simply states the Python version being used. (3.8.8 at time of writing.) You should try running the program with the same version to avoid any undefined errors.

- [subinfo.db](subinfo.db) is probably one of the most important files. It has two tables defined: `flairlist` and `interval_list` (amazing names, I'm aware). 
    >`flairlist` is designed to help speed up DRIB significantly when using [flrlist](##flrlist). 

    >`interval_list` is used when [link](##link) has been set up with a channel. It's what stores the various subreddits and the channels they have to be sent to.

- [bot.py](bot.py) is the python program written to implement DRIB!
  
Now that you have a brief idea of the workings of each file, let's jump right into the main part! 

# Commands

You opened the file and probably went: *woah, that's a lot of ugly code.* I know, but I'm trying my best!

DRIB's commands have been separated into two categories, which can be seen in the file through the form of `cogs` (classes):
> Reddit Subreddit Searching (`Reddit_Srch`), which defines the functions `srch`, `srchflr`, `rand` and `trending`.

> Reddit Subreddit Functionality (`Reddit_Subs`), which defines the functions `flrlist`, `link`, `unlink` and `list`.

DRIB uses `.` as its command prefix by default, but feel free to change it to whatever you want!

## ***Reddit Subreddit Searching***

## srch

The most generic function! `srch` returns a specified number of posts from a specified subreddit, under a chosen criteria (such as hot, top, rising, etc.)

Usage:
> `.srch <subreddit> <number_of_posts> <criteria>`

## srchflr 

A modified version of the `srch`. `srchflr` takes an additional argument `flair` that can be found using `flrlist`. As can be inferred, it allows you to search for posts but this time, filtering by flair.

Usage:
> `.srch <subreddit> <number_of_posts> <criteria> <flair>`

## r

Bored and up for playing some Russian Roulette? The `r` command forgoes the `criteria` argument in `srch` and instead returns (a) completely random post(s) from your chosen subreddit. *According to the PRAW documentation, not all subreddits support this. I have no idea which ones do and don't, but as a general rule of thumb if DRIB doesn't respond in five business days (lmao) it's probably not supported.*

~~*no, there's no issue with my code i swear*~~

Usage:
>`.r <subreddit> <number_of_posts>`

## trending

Basically the r/all page, brought to your server. Too lazy to check Reddit but want to know what's trending right now? Just run this command, and it's done.

Usage:
>`.trending <number_of_posts>`
 
 ## ***Reddit Subreddit Functionality***

 ## flrlist

 This command is used in conjunction with `srchflr`. There's a bit more to this than one might expect; in fact, it was the reason `subinfo.db` was created. [AsyncPRAW](asyncpraw.readthedocs.io), the library I used to interact with the Reddit API, offered no easy way of obtaining the list of flairs available in a subreddit without being a moderator. As a result, this command checks for unique flairs in the top 100 posts of the chosen subreddit. This takes quite some time, so I decided to optimise it by introducing `flairlist` in `subinfo.db`, which stores the flairs once queried, so if it's required again the process doesn't have to be repeated.

 Usage:
 >`.flrlist <subreddit>`

 ## link *and* unlink

 These two commands are basically interrelated so there'll be one specific entry for them.

 `link` is designed to keep you up to date with any subreddit of your choice, while attempting to ensure that you don't get repeated posts. It links the channel you run the command in with the subreddit, randomly posting posts from 'rising' every half hour. Unfortunately, there's no way (as of now) to redefine this interval, you'll have to change the code yourself.

`unlink` terminates this connection. You'll have to be in the channel where you linked it, though.

Usage:

*link*
>`.link <subreddit> <number_of_posts>`

*unlink*
>`.unlink <subreddit>`

## list

Just when you need a quick refresher on what subreddits are linked to the channel you're in.

Usage:

>`.list`


# Acknowledgements

My man Sangee has to be on top of this list for all the testing and the suggestions.

In regards to the libraries I used, literally would've been impossible without [discord.py](https://discordpy.readthedocs.io/en/stable/) and [AsyncPRAW](https://asyncpraw.readthedocs.io/en/stable/). This [article](https://realpython.com/how-to-make-a-discord-bot-python/#connecting-a-bot) was a massive help as well. Finally, major shoutout to [discord-pretty-help](https://github.com/stroupbslayen/discord-pretty-help) for making the bot's menu look actually good.

And of course, the folks over at CS50. This was an amazing course.
