#!/usr/bin/env python3

import sys
import praw
from pprint import pprint

def get_all_redditors_from_a_sub(praw_handle, sub, num_comments=None):
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
    if len(sys.argv) != 3:
        sys.stderr.write("usage: compare_subreddits.py <subreddit_1> <subreddit_2>\n")
        sys.exit()

    sub1 = sys.argv[1]
    sub2 = sys.argv[2]

    user_agent = ("reddit_sna scraper v0.1 by /u/sna_bot "
                  "https://github.com/brianreallymany/reddit_sna")
    r = praw.Reddit(user_agent=user_agent)

    group1 = get_all_redditors_from_a_sub(r, sub1) 
    group2 = get_all_redditors_from_a_sub(r, sub2)

    common_users = [u for u in group1 if u in group2]
    #print("group1 is " + str(group1))
    #print("group2 is " + str(group2))
    #print("common_users is " + str(common_users))
    denominator = min(len(group1), len(group2))
    numerator = len(common_users)
    O_r = float(numerator) / denominator
    print("users in " + sub1 + ": " + str(len(group1)))
    print("users in " + sub2 + ": " + str(len(group2)))
    print("users in common: " + str(len(common_users)))
    print("O_r is " + str(O_r))


############################################################################

if __name__ == '__main__':
    main()

