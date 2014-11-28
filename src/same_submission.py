#!/usr/bin/env python3

import sys
import praw
import collections
import networkx as nx

def parse_command_line_args():
    debug, verbose = False, False
    if len(sys.argv) < 3:
        sys.stderr.write("usage: same_sumission.py <subreddit1> <subreddit2> [-d] -[v]\n")
        sys.stderr.write("(enter -d for debug mode, -v for verbose mode\n)")
        sys.exit()

    sub1 = sys.argv[1]
    sub2 = sys.argv[2]
    if "-d" in sys.argv:
        debug = True
    if "-v" in sys.argv:
        verbose = True

    return sub1, sub2, debug, verbose


def print_graph_summary(graph):
    for node in graph.nodes():
        if ',' in graph.node[node]['user_of']:
            print("\n\n\n**********\n\n\n*********")
            print("user of more than one: " + graph.node[node]['user_of'])
            print("\n\n\n**********\n\n\n*********")
        print("node " + node + " has " + str(len(graph.neighbors(node))) + " neighbors")
        print("they are:")
        for neighbor in graph.neighbors(node):
            print("\t" + neighbor + "\t" + graph.node[neighbor]['user_of'])

def get_top_N_from_month(subreddit, N, r, DEBUG=False, VERBOSE=False):
    if DEBUG:
        if subreddit == '100pushups':
            url = "http://www.reddit.com/r/100pushups/comments/1v1wvy/i_just_finished_the_initial_test_and_am_ready_to/"
            debug_submission = r.get_submission(url)
            return [debug_submission]
        elif subreddit == 'MakeupAddiction':
            url = "http://www.reddit.com/r/MakeupAddiction/comments/1jwg3o/159_including_shipping_for_12_assorted_eye_liners/"
            debug_submission = r.get_submission(url)
            return [debug_submission]
    else:
        return r.get_subreddit(subreddit).get_top_from_month(limit=N)

def update_graph_with_comment(graph, submission, comment, already_added, r, DEBUG=False, VERBOSE=False):
    """Creates/modifies nodes and edges based on an "in_group" comment.
    * Each node is tagged as "user of" subreddit.
    * Edges between comment author and users in 'already_added' are created
      or modified by adding the submission's permalink to the "in_group_subs"
      property of the edge
    * Returns graph unmodified if comment.author is Deleted or if this
      comment is a MoreComments object

    Arguments:
        graph: a NetworkX Graph object
        submission: a praw.reddit.Submission object
        comment: a praw.Reddit.Comment object
        already_added: a list of usernames/nodes already added to the graph
                       from this submission
        r: a praw.Reddit object
        DEBUG: a boolean
        VERBOSE: a boolean

    Returns:
        the updated Graph object
    """
    if  isinstance(comment, praw.objects.MoreComments):
        return graph
    if comment.author == None:
        return graph

    this_author = comment.author.name

    # create a node for this_author if necessary
    if this_author in graph.nodes():
        if VERBOSE:
            print("author already in the graph: " + this_author + " (user_of: " + graph.node[this_author]['user_of'])
    else:
        graph.add_node(this_author, 
                       user_of=submission.subreddit.display_name)
        if VERBOSE:
            print("added new author: " + this_author + " (user_of: " + graph.node[this_author]['user_of'])


    # Add this subreddit to node's 'user_of' list if necessary
    already_user_of = graph.node[this_author]['user_of']
    if submission.subreddit.display_name not in already_user_of:
        user_of_list = already_user_of.split(',')
        user_of_list.append(submission.subreddit.display_name)
        user_of_list = sorted(user_of_list)
        graph.node[this_author]['user_of'] = ','.join(seen_list)

    # connect this node to all others in the graph from this submission
    for author in already_added:
        graph.add_edge(author, this_author, in_group_subs=submission.permalink) 

    already_added.append(this_author)

def update_graph_with_in_group_submission(graph, submission, r, DEBUG=False, VERBOSE=False):
    """Creates/modifies nodes and edges based on an "in_group" submission.
    * Each node is tagged as "user of" subreddit.
    * Edges between users are created/modified when they appear in the same submission.
    * The submission's permalink is added to the "in_group_subs" property
      of the edge.
    * Returns graph unmodified if submission.author is Deleted

    Arguments:
        graph: a NetworkX Graph object
        submission: a praw.reddit.Submission object
        r: a praw.Reddit object
        DEBUG: a boolean
        VERBOSE: a boolean

    Returns:
        the updated Graph object
    """

    if submission.author == None:
        return graph

    if VERBOSE:
        print("Working on this submission: " + submission.permalink)
        print("  author is " + str(submission.author))

    if not DEBUG:
        pass # TODO
        # Deal with MoreComments 
        if VERBOSE:
            pass
            #print("Fetching MoreComments")
        #X = 5 # TODO limit=None
        #submission.replace_more_comments(limit=X, threshold=0)

    flat_comments = praw.helpers.flatten_tree(submission.comments)

    if DEBUG: # fewer comments, faster runtime, smaller graph
        flat_comments = flat_comments[:40]
    if VERBOSE:
        print("It has " + str(len(flat_comments)) + " comments")

    # Add node for Submission author (if necessary)
    if submission.author not in graph.nodes():
        graph.add_node(submission.author.name, user_of=submission.subreddit.display_name) 
    
    already_added = [submission.author.name]
    for comment in flat_comments:
        update_graph_with_comment(graph, submission, comment, already_added, r, DEBUG, VERBOSE)
    return graph

def update_graph_with_subreddit_of_interest(graph, N, sub, r, DEBUG=False, VERBOSE=False):
    """Gets top N submissions from given subreddit, updates graph.
    * Each node is tagged as "user of" subreddit.
    * Edges between users are created/modified when they appear in the same submission.
    * The submission's permalink is added to the "in_group_subs" property
      of the edge.

    Arguments:
        graph: a NetworkX Graph object
        N: an integer for how many top submissions from month to fetch
        sub: a string representingi the subreddit name
        r: a praw.Reddit object

    Returns:
        the updated Graph object
    """
    top_submissions = get_top_N_from_month(sub, N, r, DEBUG, VERBOSE)

    if VERBOSE:
        print("Got " + str(N) + " submission(s) from " + sub)
    
    # loop through submissions, adding each submitter and each commenter to the graph
    for submission in top_submissions:
        graph = update_graph_with_in_group_submission(graph, submission, r, DEBUG, VERBOSE)
    return graph

def main():
    sub1, sub2, DEBUG, VERBOSE = parse_command_line_args()

    if DEBUG:
        sub1, sub2 = '100pushups', 'MakeupAddiction'

    user_agent = ("reddit_sna scraper v0.1 by /u/sna_bot "
                  "https://github.com/brianreallymany/reddit_sna")
    r = praw.Reddit(user_agent=user_agent)

    graph = nx.Graph()

    submissions_per_subreddit = 1 # TODO command line arg

    graph = update_graph_with_subreddit_of_interest(graph, 
            submissions_per_subreddit, sub1, r, DEBUG, VERBOSE)

    graph = update_graph_with_subreddit_of_interest(graph,
            submissions_per_subreddit, sub2, r, DEBUG, VERBOSE)

    # Summarize graph
    if VERBOSE:
        print_graph_summary(graph)
        print("writing gexf...")

    nx.write_gexf(graph, 'foo.gexf')

    if VERBOSE:
        print("wrote gexf...")

############################################################################

if __name__ == '__main__':
    main()

