#!/usr/bin/env python3

import sys
import praw
import collections
import networkx as nx

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("usage: build_graph_for_one_subreddit.py <subreddit>\n")
        sys.exit()

    sub= sys.argv[1]

    user_agent = ("reddit_sna scraper v0.1 by /u/sna_bot "
                  "https://github.com/brianreallymany/reddit_sna")
    r = praw.Reddit(user_agent=user_agent)

    graph = nx.Graph()

    # get N top submissions from chosen subreddit
    N = 1 # TODO command line arg
    top_submissions = r.get_subreddit(sub).get_top_from_month(limit=N)

    print("Got " + str(N) + " submission(s) from " + sub)
    
    # loop through submi ssions, adding each submitter and each commenter to the graph
    for submission in top_submissions:
        print("Working on this submission: " + submission.permalink)

        # TODO deal with MoreComments
        #print("Fetching MoreComments")
        #X = 5 # TODO limit=None
        #submission.replace_more_comments(limit=X, threshold=0)
        #print("Now it has " + str(len(submission.comments)) + " comments")

        flat_comments = praw.helpers.flatten_tree(submission.comments)
        print("It has " + str(len(flat_comments)) + " comments")

        if submission.author == None:
            continue

        graph.add_node(submission.author.name, seen=submission.permalink) 
        # TODO think long and hard about what to store

        for comment in flat_comments:
            if  isinstance(comment, praw.objects.MoreComments):
                continue
            if comment.author == None:
                continue

            graph.add_node(comment.author.name, seen=submission.permalink)
            # TODO add edges


    print(graph.nodes())
    print("writing gexf?")
    nx.write_gexf(graph, 'foo.gexf')
    print("wrote gexf?")

############################################################################

if __name__ == '__main__':
    main()

