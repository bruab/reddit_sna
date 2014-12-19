#!/usr/bin/env python3

import sys
import praw
import networkx
import datetime

def get_all_redditors_from_a_sub(praw_handle, sub, num_comments):
    """Return a list of users who submitted the last num_comments comments to sub"""
    # if num_comments == None, get as many comments as possible
    all_redditors = []  # a list of Redditor objects
    sub = praw_handle.get_subreddit(sub)
    comments = sub.get_comments(limit=num_comments)
    for comment in comments:
        try:
            if comment.author not in all_redditors:
                all_redditors.append(comment.author)
        except Exception as e:
            sys.stderr.write("get_all_redditors_from_a_sub: "
                    "error fetching comment, skipping. " + str(e) + "\n")
            continue
    return all_redditors

def get_subreddits_visited_for_redditor(redditor, limit):
    all_subreddits = []
    # get submissions first
    submissions = redditor.get_submitted(limit=limit)
    for submission in submissions:
        try:
            if submission.subreddit.display_name not in all_subreddits:
                all_subreddits.append(submission.subreddit.display_name)
        except Exception as e:
            sys.stderr.write("get_subreddits_visited_for_redditor: error\n"
                    "skipping a submission..." + str(e))
            continue
    # get comments next
    comments = redditor.get_comments(limit=limit)
    for comment in comments:
        try:
            if comment.subreddit.display_name not in all_subreddits:
                all_subreddits.append(comment.subreddit.display_name)
        except Exception as e:
            sys.stderr.write("get_subreddits_visited_for_redditor: error\n"
                    "skipping a submission..." + str(e))
            continue
    return all_subreddits

def main():
    ## PARSE COMMAND LINE ARGS ##
    if len(sys.argv) < 2:
        sys.stderr.write("usage: compare_subreddits.py <subreddit_1> [-d] [-v] [-l limit]\n")
        sys.stderr.write("-d is for debug mode, -v for verbose mode, limit is number of comments to get\n")
        sys.stderr.write("for each subreddit, then submissions and comments to get for each user.\n")
        sys.exit()

    sub1 = sys.argv[1]
    DEBUG = False
    VERBOSE = False
    LIMIT = None

    if len(sys.argv) >= 4:
        for i, arg in enumerate(sys.argv[2:]):
            if arg == "-d":
                DEBUG = True
            if arg == "-v":
                VERBOSE = True
            if arg == "-l":
                LIMIT = int(sys.argv[i+1+2]) # because looping through [3:]

    ## SETUP PRAW ##
    user_agent = ("/u/sna_bot graph_two_subreddits algorithm "
                  "https://github.com/brianreallymany/reddit_sna")
    r = praw.Reddit(user_agent=user_agent)

    ## COLLECT DATA FROM REDDIT ##
    # Get a list of users from the last LIMIT comments
    all_redditors = get_all_redditors_from_a_sub(r, sub1, LIMIT) 

    # Get list of subreddits visited for each redditor
    # Add nodes to graph for each subreddit, and add edges between
    # subreddits when a single user users them
    graph = networkx.Graph()
    for redditor in all_redditors:
        print("working on " + str(redditor))
        subs_visited = get_subreddits_visited_for_redditor(redditor, LIMIT)
        print("\tvisited: " + str(subs_visited))
        for sub in subs_visited:
            if sub not in graph.nodes():
                graph.add_node(sub, users=1)
            else:
                graph.node[sub]['users'] += 1 # TODO verify this works
        # TODO add edges
        # ok if got 'pics', 'funny', 'gifs' need edges from pics to funny
        # (create with weight=1 if not there, weight += 1 if already there)
        # from pics to gifs and from funny to gifs
        # how do i do it. [pics, funny, gifs]
        # from [0] to [1:]
        # from [1] to [2:]
        # while i+1 < len(list)
        for i in range(len(subs_visited)):
            this_sub = subs_visited[i]
            for target in subs_visited[i+1:]:
                if target not in graph[this_sub]:
                    graph.add_edge(this_sub, target, weight=1)
                else:
                    graph[this_sub][target]['weight'] += 1

    # Summarize results
    print("looked at a total of " + str(len(all_redditors)) + " redditors.")
    print("found a total of " + str(len(graph.nodes())) + " subreddits.")
    print("here are the edges with weight > 1:")
    for n,nbrs in graph.adjacency_iter():
        for nbr,eattr in nbrs.items():
            data=eattr['weight']
            if data > 1:
                print(n, nbr, data)

    # Write .gexf file
    timestamp = datetime.datetime.now().isoformat()
    filename = sub1 + "." 
    filename += "linked_by_common_users."
    filename += "limit_" + str(LIMIT) + "."
    filename += timestamp + ".gexf"
    networkx.write_gexf(graph, filename)



############################################################################

if __name__ == '__main__':
    main()

