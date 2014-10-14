#!/usr/bin/env python3

from get_n_submissions_from_subreddit import get_n_submissions_from_subreddit
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
    all_redditors = {} # maps username to number of comments
    if len(sys.argv) < 2:
        sys.stderr.write("usage: all_user_info_by_subreddit.py <subreddit> [number of submissions ('0' for no limit)]\n")
        sys.exit()

    if len(sys.argv) == 3:
        if sys.argv[2] == '0':
            NUMBER_OF_RESULTS = None
        else:
            NUMBER_OF_RESULTS = int(sys.argv[2])

    subreddit = sys.argv[1]

    # Get hot submissions for subreddit
    submissions = get_n_submissions_from_subreddit(NUMBER_OF_RESULTS, subreddit)
    for i, sub in enumerate(submissions):
        sys.stderr.write("parsing submission #" + str(i))
        # Add submission author to dict
        update_dict(str(sub.author), all_redditors)
        sub.replace_more_comments(limit=None, threshold=0)
        flat_comments = praw.helpers.flatten_tree(sub.comments)
        # Add all commentors to dict
        for comment in flat_comments:
            update_dict(str(comment.author), all_redditors)

    # Behold:
    for redditor in sorted(all_redditors.keys()):
        sys.stdout.write(redditor + "\t" + str(all_redditors[redditor]) + "\n")


if __name__ == '__main__':
    main()
