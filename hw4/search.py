#!/usr/bin/python

import sys, getopt, linecache, re
import math
import index
from heapq import heappushpop,heappush,heappop

word_dict = {}
N = None
postings_file = None
all_fids = None
# according to page 34 of IIR, skips for intermediate results are not available
# but we may choose to support this by change always_insert_skips to True
always_insert_skips = False 

def load_dictionary(input_dict):
    """
    load dictionary into word_dict
    word_dict maps a word to a list [frequency, posting pointer]
    """
    fh = open(input_dict)
    for line in fh:
        ws = line.split()
        word_dict[ws[0]] = [int(e) for e in ws[1:]]
    fh.close()  
    

def process_query_list(qlist):
    scores = []
    docs={}
    N = len(eval(linecache.getline(postings_file, 1)))
    qset=(set)(qlist)
    for e in qset:
        if e in word_dict.keys():
            df = word_dict[e][0]
            posts =eval(linecache.getline(postings_file, word_dict[e][1]))
            idf= math.log((float)(N)/df,10)
            tf = qlist.count(e)
            print "tf for ",e," : ",tf
            print "df for ",e," : ",df
            wtq =(1+math.log(tf,10)) * idf
            print "wtq for ",e," : ",wtq
            for pair in posts:
                if pair[0] in docs.keys():
                    docs[pair[0]]+=(1+math.log(pair[1],10))*wtq
                else:
                    docs[pair[0]] =(1+math.log(pair[1],10))*wtq
    for mykey in docs:
        if len(scores)<10:
            #because the below heappushpop always pop minimum id, so 70000 is for 
            #converting large id to small number, in order to allow lowest id with same score top
            heappush(scores,(docs[mykey],70000-mykey))
        else:
            heappushpop(scores,(docs[mykey],70000-mykey))
    return [heappop(scores) for i in range(len(scores))]

def search_query(query):
    qlist = re.split("([ ()])", query)
    qlist = filter(lambda a: a != "" and a != " ", qlist)     # remove " " and ""

    for i in range(0, len(qlist)):
        # stem query words
        qlist[i] = index.stemmer.stem_word(qlist[i].lower())
    
    res_list = process_query_list(qlist)
    print str(res_list)
    res_list.reverse()
    res=[(70000-a[1]) for a in res_list]
    return " ".join(str(a) for a in res)

def usage():
    print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"
    print "    or " + sys.argv[0] + " -d dictionary-file -p postings-file -i"

if __name__ == "__main__":
    dictionary_file = query_file = result_file = None
    interactive = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:i')
    except getopt.GetoptError, err:
        usage()
        sys.exit(2)
    for o, a in opts:
        if o == '-d':
            dictionary_file = a
        elif o == '-p':
            postings_file = a
        elif o == '-q':
            query_file = a
        elif o == '-o':
            result_file = a
        elif o == '-i':
            interactive = True
            query_file = ""
            result_file = ""
        else:
            assert False, "unhandled option"
    if dictionary_file == None or postings_file == None or query_file == None or result_file == None:
        usage()
        sys.exit(2)

    load_dictionary(dictionary_file)

    # interactive mode: you can key in your query one at a time at the command prompt
    if interactive:
        print "Interactive search. Ctrl-C to exit."
        while True:
            try:
                query = raw_input("Search: ")
                res_str = search_query(query.strip())
                print "Results: " + res_str + "\n"
            except KeyboardInterrupt:
                print "\nBye"
                sys.exit()
    else:
        fh = open(query_file, "r")
        fh2 = open(result_file, "w")
        for query in fh:
            query = query.strip()
            #print "Search: " + query
            res_str = search_query(query)
            #print "Results: " + res_str + "\n"
            fh2.write(res_str+"\n")
        fh.close()
        fh2.close()
