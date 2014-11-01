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

def get_all_redditors_from_a_sub(praw_handle, sub, num_comments):
    """Return a list of users who sumbitted the last num_comments comments to sub"""
    # if num_comments == None, get as many comments as possible
    all_redditors = [] 
    # Get hot submissions for subreddit
    sub = praw_handle.get_subreddit(sub)
    comments = sub.get_comments(limit=num_comments)
    for comment in comments:
        author = str(comment.author)
        if author not in all_redditors:
            all_redditors.append(author)
    return all_redditors

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

    all_redditors = get_all_redditors_from_a_sub(r, subreddit, NUMBER_OF_RESULTS)

    for redditor in all_redditors:
        print(redditor)


############################################################################

if __name__ == '__main__':
    main()

