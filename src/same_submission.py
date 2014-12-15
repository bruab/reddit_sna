#!/usr/bin/env python3

import sys
import time
import datetime
import praw
import collections
import networkx as nx

def parse_command_line_args():
    debug, verbose = False, False
    if len(sys.argv) < 3:
        sys.stderr.write("usage: same_sumission.py <subreddit1> <subreddit2>"+\
                         "[-d] -[v] [-l limit]\n")
        sys.stderr.write("(enter -d for debug mode, -v for verbose mode)\n")
        sys.stderr.write("(enter -l 10 for a submission fetch limit of 10)\n")
        sys.stderr.write("(enter -l None for as many as possible)\n")
        sys.exit()

    sub1 = sys.argv[1]
    sub2 = sys.argv[2]
    limit = 1 # default
    if len(sys.argv) > 3:
        for i, arg in enumerate(sys.argv[3:]):
            if "-d" in arg:
                debug = True
            elif "-v" in arg:
                verbose = True
            elif "l" in arg:
                limit_string = sys.argv[i+4] # b/c for loop starts at the 4th
                if limit_string == "None":
                    limit = None
                else:
                    limit = int(limit_string)

    return sub1, sub2, debug, verbose, limit


def print_graph_summary(graph):
    for node in graph.nodes():
        if ',' in graph.node[node]['user_of']:
            print("\n\n\n**********\n\n\n*********")
            print("user of more than one: " + graph.node[node]['user_of'])
            print("\n\n\n**********\n\n\n*********")
        print("node " + node + " has " + str(len(graph.neighbors(node)))+\
              " neighbors")
        print("they are:")
        for neighbor in graph.neighbors(node):
            print("\t" + neighbor + "\t" + graph.node[neighbor]['user_of'])
    for node, neighbors in graph.adjacency_iter():
        for neighbor, eattr in neighbors.items():
            if 'out_group_submissions' in eattr:
                print("Found an out_group_submission link between users " +
                        node + " and " + neighbor + ".")
                print("The link is from: " +\
                      graph[node][neighbor]['out_group_submissions'])

def get_top_N_from_month(subreddit, N, r, DEBUG=False, VERBOSE=False):
    if DEBUG:
        if subreddit == '100pushups':
            url = "http://www.reddit.com/r/100pushups/comments/1v1wvy/i_just_finished_the_initial_test_and_am_ready_to/"
            debug_submission = r.get_submission(url) # has_fetched = True
            return [debug_submission]
        elif subreddit == 'MakeupAddiction':
            url = "http://www.reddit.com/r/MakeupAddiction/comments/1jwg3o/159_including_shipping_for_12_assorted_eye_liners/"
            debug_submission = r.get_submission(url)
            return [debug_submission]
    else:
        # Return a generator object (has_fetched = False)
        return r.get_subreddit(subreddit).get_top_from_month(limit=N)

def update_graph_with_comment(graph, submission, comment, 
           already_added, r, DEBUG=False, VERBOSE=False):
    """Creates/modifies nodes and edges based on an "in_group" comment.
    * Each node is tagged as "user of" subreddit.
    * Edges between comment author and users in 'already_added' are created
      or modified by adding the submission's permalink to the "in_group_submissions"
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
            print("\t\t\tauthor already in the graph: " + this_author +
                    " (user_of: " + graph.node[this_author]['user_of'] + ")")
    else:
        graph.add_node(this_author, 
                       user_of=submission.subreddit.display_name)
        if VERBOSE:
            print("\t\t\tadded new author: " + this_author + " (user_of: " +
                    graph.node[this_author]['user_of'] + ")")


    # Add this subreddit to node's 'user_of' list if necessary
    already_user_of = graph.node[this_author]['user_of']
    if submission.subreddit.display_name not in already_user_of:
        user_of_list = already_user_of.split(',')
        user_of_list.append(submission.subreddit.display_name)
        user_of_list = sorted(user_of_list)
        graph.node[this_author]['user_of'] = ','.join(seen_list)

    # connect this node to all others in the graph from this submission
    for author in already_added:
        graph.add_edge(author, this_author, 
                in_group_submissions=submission.permalink) 

    # modifies passed-in list, doesn't return, ick
    if this_author not in already_added:
        already_added.append(this_author)

def update_graph_with_in_group_submission(graph, submission, r, 
                                    DEBUG=False, VERBOSE=False):
    """Creates/modifies nodes and edges based on an "in_group" submission.
    * Each node is tagged as "user of" subreddit.
    * Edges between users are created/modified when they appear in 
      the same submission.
    * The submission's permalink is added to the "in_group_submissions" property
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
        print("\tWorking on this submission: " + submission.permalink)
        print("\t\tauthor is " + str(submission.author))

    # Fetch MoreComments (unless in DEBUG mode)
    if not DEBUG:
        X = 5 # TODO limit=None
        try:
            submission.replace_more_comments(limit=X)
        except Exception as e:
            sys.stderr.write("replace_more_comments "+\
                    " caught an Exception: " + str(e) + "\n")
        if VERBOSE:
            print("Fetching MoreComments")

    flat_comments = praw.helpers.flatten_tree(submission.comments)

    if DEBUG: # fewer comments, faster runtime, smaller graph
        flat_comments = flat_comments[:40]
    if VERBOSE:
        print("\t\tIt has " + str(len(flat_comments)) + " comments")

    # Add node for Submission author (if necessary)
    if submission.author not in graph.nodes():
        graph.add_node(submission.author.name, 
                user_of=submission.subreddit.display_name) 
    
    already_added = [submission.author.name]
    for comment in flat_comments:
        update_graph_with_comment(graph, submission, comment, 
                already_added, r, DEBUG, VERBOSE)
    return graph

def update_graph_with_subreddit_of_interest(graph, N, sub, r, 
                                    DEBUG=False, VERBOSE=False):
    """Gets top N submissions from given subreddit, updates graph.
    * Each node is tagged as "user of" subreddit.
    * Edges between users are created/modified when they appear in the same submission.
    * The submission's permalink is added to the "in_group_submissions" property
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
    # has_fetched = False
    # unless DEBUG

    if VERBOSE:
        print("\tGot " + str(N) + " submission(s) from " + sub)
    
    # loop through submissions, 
    # adding each submitter and each commenter to the graph
    for submission in top_submissions:
        try:
            graph = update_graph_with_in_group_submission(graph, submission, 
                                                            r, DEBUG, VERBOSE)
        except Exception as e: 
            sys.stderr.write("Error fetching top submissions for subreddit " +\
                             str(sub) + ".\n")
    return graph

def update_graph_with_user_comments(graph, username, r, in_groups, 
                            DEBUG=False, VERBOSE=False, LIMIT=1):
    """Fetches user submissions and comments and adds edges to graph.
    * No new nodes are created.
    * Edges between users are created/modified when they appear in 
      the same submission.
    * If user is a "user_of" a submission's subreddit, the submission 
      is not considered.
    * The submission's permalink is added to the "out_group_submissions" 
      property of the edge.

    Arguments:
        graph: a NetworkX Graph object
        username: a string representing a praw.Redditor.name
        r: a praw.Reddit object
        in_groups: a tuple containing the names of the two 'reference'
                   subreddits for this experiment

    Returns:
        the updated Graph object
    """
    fetch_limit = LIMIT

    # make in group subreddit names lowercase for easier string comparison
    # (in case the display_name is MakeupAddiction but command line 
    # arg was 'makeupaddiction')
    in_groups = ( in_groups[0].lower(), in_groups[1].lower() )

    try:
        user = r.get_redditor(username) # has_fetched = True
    except Exception as e: 
        sys.stderr.write("Exception when fetching redditor " +
                         username + ". Skipping ...\n")
        sys.stderr.write(str(e) + "\n")
        time.sleep(120)
        return graph

    all_submissions = []
    # Fetch user submissions and add to list
    if VERBOSE:
        print("\tFetching " + str(fetch_limit) + " submissions and " +
                str(fetch_limit) + " comments' submissions for user " +
                username)
    subs = user.get_submitted(limit=fetch_limit) # a generator
    try:
        [all_submissions.append(sub) for sub in subs] # has_fetched = True
    except Exception as e:
        sys.stderr.write("Exception when fetching submissions for redditor " +
                         username + ". Skipping ...\n")
        sys.stderr.write(str(e) + "\n")
        time.sleep(120)
        return graph

    # Fetch user comments
    comms = user.get_comments(limit=fetch_limit) # a generator
    for comm in comms:
        # Discard if it's from an 'in_group' subreddit
        subreddit = comm.subreddit.display_name
        if subreddit in graph.node[username]['user_of']:
            if VERBOSE:
                print("\t\tDisregarding comment and its containing "+\
                        "submission; user " + username + " is a 'user_of' "\
                        + subreddit)
            continue
        else:
            # Add the comment's containing submission to all_submissions
            #   if it's not already in there
            # TODO can we possibly save some API calls here?
            try:
                comment_submission = comm.submission
                if comment_submission not in all_submissions:
                    all_submissions.append(comment_submission)
            except Exception as e:
                sys.stderr.write("Error fetching submission for " + str(comm))
                sys.stderr.write("Skipping ...")
                continue

    # Filter submissions, discarding those from 'in_group' subreddits;
    #   at this point we're only interested in chance meetings
    #   Note that we're comparing the lower() versions of the subreddit names
    all_submissions = [s for s in all_submissions 
            if s.subreddit.display_name.lower() not in in_groups]

    if VERBOSE:
        print("\t\tAfter filtering in_group submissions and duplicates, " +
                "found " + str(len(all_submissions)) +
                " submissions for user " + username)

    if DEBUG:
        if username == "I_love_pugs_dammit":
            print("\t\tAdding out group link submission for debugging...")
            all_submissions.append(r.get_submission("http://www.reddit.com/r/pugs/comments/zjna4/after_years_of_lurking_i_created_an_account/"))

    # For each submission, update graph by creating/modifying edges
    #   with an "out_group_submissions" tag. Edges are added between
    #   users regardless of which subreddit they are each a "user_of".
    for submission in all_submissions:
        if VERBOSE:
            print("\t\t\tLooking at submission " + submission.permalink)
        try:
            for comment in submission.comments:
                if  isinstance(comment, praw.objects.MoreComments):
                    continue
                if comment.author == None:
                    continue
                comment_author = comment.author.name
                if VERBOSE:
                    print("\t\t\t\tFound a comment by " + comment_author)
                if comment_author in graph.nodes() and \
                        comment_author != username:
                    if VERBOSE:
                        print("\n\t\t\t\t\tComment author is already"+\
                              " in the graph, but this is an out_group"+\
                              " submission! Jackpot!\n")
                    graph.add_edge(username, comment_author, 
                            out_group_submissions=submission.permalink) 
        except Exception as e:
            sys.stderr.write("\nException occurred in "+\
                             " update_graph_with_user_comments(): ")
            sys.stderr.write(str(e) + "\n")
            sys.stderr.write("Not all comments parsed from submission "+\
                    submission.permalink + "\n")

    return graph

def main():
    sub1, sub2, DEBUG, VERBOSE, LIMIT = parse_command_line_args()

    if DEBUG:
        sub1, sub2 = '100pushups', 'MakeupAddiction'

    user_agent = ("reddit_sna scraper v0.1 by /u/sna_bot "
                  "https://github.com/brianreallymany/reddit_sna")
    r = praw.Reddit(user_agent=user_agent)

    graph = nx.Graph()

    submissions_per_subreddit = LIMIT

    # Add nodes and edges for users of first subreddit
    if VERBOSE:
        print("\nAdding nodes and in_group_submissions edges for first "+\
                " subreddit, " + sub1)
    graph = update_graph_with_subreddit_of_interest(graph, 
            submissions_per_subreddit, sub1, r, DEBUG, VERBOSE)

    # Add nodes and edges for users of second subreddit
    #   If the two subreddits have any  users in common,
    #   edges between them will be annotated with the 
    #   "in_group_submissions" field and the name of the submission
    if VERBOSE:
        print("Adding nodes and in_group_submissions edges for second "+\
                "subreddit, " + sub2)
    graph = update_graph_with_subreddit_of_interest(graph,
            submissions_per_subreddit, sub2, r, DEBUG, VERBOSE)

    # For each user in the graph, explore previous comments
    #   made outside of the user's "user_of" subreddit(s).
    #   If other users from the graph are present in the same
    #   submission, add an edge with "out_group_submissions"
    #   and the submission permalink.
    if VERBOSE:
        print("\nNow updating graph with submissions and comments from "+\
                "all users.\n")
    for user in graph.nodes():
        update_graph_with_user_comments(graph, user, r, (sub1, sub2), 
                                        DEBUG, VERBOSE, LIMIT)


    # Summarize graph
    if VERBOSE:
        print_graph_summary(graph)
        print("writing gexf...")

    # Write .gexf file
    timestamp = datetime.datetime.now().isoformat()
    filename = sub1 + "." + sub2 + "."
    filename += "limit_" + str(LIMIT) + "."
    filename += timestamp + ".gexf"
    nx.write_gexf(graph, filename)

    if VERBOSE:
        print("wrote gexf...")

############################################################################

if __name__ == '__main__':
    main()

