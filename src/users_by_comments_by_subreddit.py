#!/usr/bin/env python3

import sys
import praw
from pprint import pprint

NUMBER_OF_RESULTS = 10 # set to None for the real deal ...

def update_dict(username, dictionary):
    if username not in dictionary:
        dictionary[username] = 1
    else:
        dictionary[username] += 1

def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: users_by_comments_by_subreddit.py <subreddit> [number of submissions ('0' for no limit)]\n")
        sys.exit()

    if len(sys.argv) == 3:
        if sys.argv[2] == '0':
            NUMBER_OF_RESULTS = None
        else:
            NUMBER_OF_RESULTS = int(sys.argv[2])

    subreddit = sys.argv[1]

    user_agent = ("reddit_sna scraper v0.1 by /u/sna_bot "
                  "https://github.com/brianreallymany/reddit_sna")
    r = praw.Reddit(user_agent=user_agent)

    all_redditors = {} # maps username to number of comments
    # Get hot submissions for subreddit
    sub = r.get_subreddit(subreddit)
    comments = sub.get_comments(limit=None)
    count = 0
    for comment in comments:
        count += 1
        update_dict(str(comment.author), all_redditors)

    pprint(all_redditors)
    print("count is " + str(count))


if __name__ == '__main__':
    main()
