#!/usr/bin/env python3

import sys
import praw

def get_karma_by_subreddit(username):
    user_agent = ("reddit_sna scraper v0.1 by /u/sna_bot "
                  "https://github.com/brianreallymany/reddit_sna")

    r = praw.Reddit(user_agent=user_agent)


    user_name = username
    user = r.get_redditor(user_name)

    thing_limit = 10
    gen = user.get_submitted(limit=thing_limit)

    karma_by_subreddit = {}
    for thing in gen:
        subreddit = thing.subreddit.display_name
        karma_by_subreddit[subreddit] = (karma_by_subreddit.get(subreddit, 0) + thing.score)
    return(karma_by_subreddit)


def main():
    print(get_karma_by_subreddit(sys.argv[1]))

if __name__ == '__main__':
    main()
