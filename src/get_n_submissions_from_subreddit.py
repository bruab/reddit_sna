#!/usr/bin/env python3

import sys
import praw

def get_n_submissions_from_subreddit(n, subreddit):
    user_agent = ("reddit_sna scraper v0.1 by /u/sna_bot "
                  "https://github.com/brianreallymany/reddit_sna")
    r = praw.Reddit(user_agent=user_agent)

    submissions = r.get_subreddit(subreddit).get_hot(limit=n)
    return submissions

def main():
    if len(sys.argv) != 3:
        sys.stderr.write("usage: python3 get_n_submissions_from_subreddit.py <number of submissions> <subreddit>\n")
        sys.exit()
    n = int(sys.argv[1])
    subreddit = sys.argv[2]
    submissions = get_n_submissions_from_subreddit(n, subreddit)
    print([str(x) for x in submissions])

if __name__ == '__main__':
    main()
