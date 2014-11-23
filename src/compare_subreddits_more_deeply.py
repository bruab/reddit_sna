#!/usr/bin/env python3

import sys
import praw
from pprint import pprint

def get_all_redditors_from_a_sub(praw_handle, sub, num_comments=None):
    """Return a list of users who submitted the last num_comments comments to sub"""
    # if num_comments == None, get as many comments as possible
    all_redditors = [] 
    # Get hot submissions for subreddit
    sub = praw_handle.get_subreddit(sub)

    # DEBUG SETTING!
    num_comments = 50

    comments = sub.get_comments(limit=num_comments)
    for comment in comments:
        if comment.author not in all_redditors:
            all_redditors.append(comment.author)
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

    # print some stuff about group overlap
    common_users = [u for u in group1 if u in group2]
    denominator = min(len(group1), len(group2))
    numerator = len(common_users)
    O_r = float(numerator) / denominator
    print("users in " + sub1 + ": " + str(len(group1)))
    print("users in " + sub2 + ": " + str(len(group2)))
    print("users in common: " + str(len(common_users)))
    print("O_r is " + str(O_r))

    sys.stderr.write("checking comments for each user now\n\n")
    for user in group1:
        num_user_comments = None
        # DEBUG
        num_user_comments = 50
        sys.stderr.write("checking comments for user " + str(user) + "\n")
        user_comments = user.get_comments(limit=num_user_comments)
        for comment in user_comments:
            sys.stderr.write("\tcurrently inspecting this comment: " + str(comment) + " ...from " + str(comment.subreddit) + "\n")
            # check who replied to it
            sys.stderr.write("\tfound " + str(len(comment.replies)) + " replies...\n")
            for reply in comment.replies:
                sys.stderr.write("\t\tlooking at a reply by " + str(reply.author) + "\n")
                if reply.author in group2:
                    sys.stderr.write("found one!\n")
                    print(str(reply.author) + ", a user in " + str(group1) +
                            ", replied to " + str(user) + ", a user in " + str(group2) +
                            "in this comment: " + str(reply) + " ... in this subreddit: " +
                            str(reply.subreddit))
            # check parent comments
            current_comment = comment
            while not current_comment.is_root:
                sys.stderr.write("\tthis comment has a parent; fetching it now.\n")
                current_comment = r.get_info(thing_id=current_comment.parent_id)
                sys.stderr.write("\tparent comment author is " + str(current_comment.author) + "\n")
                if current_comment.author in group2:
                    sys.stderr.write("found one!\n")
                    print(str(reply.author) + ", a user in " + str(group1) +
                            ", replied to " + str(user) + ", a user in " + str(group2) +
                            "in this comment: " + str(reply) + " ... in this subreddit: " +
                            str(reply.subreddit))

    # for each user, find users responded to and users who responded
    # TODO how to store that info? each user can have 2 dicts -- "users_replied_to" and "users_who_replied"
    # but that seems clunky; prolly whole thing should be in one place. 
    # ultimately what we're after is ... what ... basically if a redpill users replied to or was replied to by
    # a feminism user, we want to know where. and vice versa. so that's it, just a report
    # on where users from sub1 interacted with users from sub2, and maybe what kind of interaction
    # could even just be a table at first -- sub1 username \t sub2 username \t who replied to whom \t where
    # ok this is better, clearer. so for each user, get all their comments
    # for each comment tree (hand wa ving), check upstream. if find opposite sub user,
    # print stuff
    # then check downstream. if find opposite sub user, print stuff
    # so have to figure out how to go from user to thread, and search parents/children on the thread
    # that doesn't sound too bad. oh yeah and also find what subreddit the thread is from, no big deal.
    # something like for comment, if not is_root then parent = r.get_info(thing_id=comment.parent_id)
    # and now we got the parent comment. check if it's opposite sub or not. and keep going




############################################################################

if __name__ == '__main__':
    main()

