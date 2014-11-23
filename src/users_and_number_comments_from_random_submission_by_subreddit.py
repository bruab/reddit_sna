#!/usr/bin/env python3

import sys
import praw
import collections

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("usage: users_and_number_comments_from_random_submission_by_subreddit.py <subreddit>")
        sys.exit()

    sub= sys.argv[1]

    user_agent = ("reddit_sna scraper v0.1 by /u/sna_bot "
                  "https://github.com/brianreallymany/reddit_sna")
    r = praw.Reddit(user_agent=user_agent)
    submission = r.get_random_submission(subreddit=sub) # this is the only API call
    
    all_redditors = collections.OrderedDict() # dictionary to hold usernames and # comments
    all_redditors[submission.author.name] = 1 # OP counts

    # count comments by user name
    for comment in submission.comments:
        if not comment.author:  # deleted comment
            continue
        author = comment.author.name
        if author not in all_redditors:
            all_redditors[author] = 1
        else:
            all_redditors[author] += 1

    print("## users_and_number_comments_from_random_submission_by_subreddit.py")
    print("## comments by user for " + submission.permalink)
    print("#username\tnum_comments")
    for user, count in all_redditors.items():
        print(user + "\t" + str(count))



############################################################################

if __name__ == '__main__':
    main()

