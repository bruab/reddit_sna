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
    N = 2 # TODO command line arg
    top_submissions = r.get_subreddit(sub).get_top_from_month(limit=N)

    print("Got " + str(N) + " submission(s) from " + sub)
    
    # loop through submi ssions, adding each submitter and each commenter to the graph
    for submission in top_submissions:
        print("Working on this submission: " + submission.permalink)
        print("  author is " + str(submission.author))

        # TODO deal with MoreComments
        #print("Fetching MoreComments")
        #X = 5 # TODO limit=None
        #submission.replace_more_comments(limit=X, threshold=0)
        #print("Now it has " + str(len(submission.comments)) + " comments")

        flat_comments = praw.helpers.flatten_tree(submission.comments)
        # DEBUG!
        flat_comments = flat_comments[:40]
        print("It has " + str(len(flat_comments)) + " comments")

        if submission.author == None:
            continue

        graph.add_node(submission.author.name, seen=submission.permalink) 
        # TODO think long and hard about what to store

        already_added = [submission.author.name]
        for comment in flat_comments:
            if  isinstance(comment, praw.objects.MoreComments):
                continue
            if comment.author == None:
                continue

            this_author = comment.author.name

            # create a node for this_author if necessary
            if this_author not in graph.nodes():
                graph.add_node(this_author, seen=submission.permalink)
                print("added new author: " + this_author + " (seen: " + graph.node[this_author]['seen'])
            else:
                print("author already in the graph: " + this_author + " (seen: " + graph.node[this_author]['seen'])
                print("and submission.permalink is " + submission.permalink)
                already_seen = graph.node[this_author]['seen']
                if submission.permalink not in already_seen:
                    seen_list = already_seen.split(',')
                    seen_list.append(submission.permalink)
                    seen_list = sorted(seen_list)
                    graph.node[this_author]['seen'] = ','.join(seen_list)
                seen_string = submission.permalink
            # connect this node to all others in the graph from this submission
            for author in already_added:
                graph.add_edge(author, this_author) 

            already_added.append(this_author)



    for node in graph.nodes():
        print("node " + node + " has " + str(len(graph.neighbors(node))) + " neighbors")
        print("they are:")
        for neighbor in graph.neighbors(node):
            print(neighbor + "\t" + graph.node[neighbor]['seen'])
    print("writing gexf?")
    nx.write_gexf(graph, 'foo.gexf')
    print("wrote gexf?")

############################################################################

if __name__ == '__main__':
    main()

