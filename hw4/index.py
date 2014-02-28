#!/usr/bin/python

import sys, os, re, math, getopt, glob
import nltk
from nltk.stem.porter import PorterStemmer

stemmer = PorterStemmer()

def read_process_text(fn):
    """
    tokenize and stem words in a file
    """
    fh = open(fn, 'r')
    text = fh.read()
    text = re.sub('\n', ' ', text) 
    text = re.sub(' +', ' ', text) 
    fh.close()
    #my_words = {}
    words_list=[]
    # the reason for doing sentence tokenization before word tokenization is that
    # word tokenizer may need sentence boundary information to tokenize words at
    # the begin and end of a sentence
    for sent in nltk.sent_tokenize(text):
        for w in nltk.word_tokenize(sent):
            #for w2 in re.split("\.\.+|[-/]", w):
            words_list.append(stemmer.stem_word(w.lower()))
    #return sorted(my_words.keys())
    return words_list

def generate_skip_list(posting_list, insert_skips=True):
    """
    the format for a postings list with skips is (for example):
    [[w1,skip1], [w2], [w3], [w4,skip2], ...]
    """
    p = len(posting_list)
    skip_list = [[e] for e in posting_list]
    if p <= 2:
        return skip_list 

    if insert_skips:
        num_skips = int(math.floor(math.sqrt(p)))
        step = int(math.floor(p / num_skips))
        i = 0
        while num_skips > 0:
            next_i = i + step
            if num_skips == 1:
                next_i = p - 1
            skip_list[i] = [skip_list[i][0], next_i]
            i = next_i
            num_skips -= 1
    return skip_list

def index_documents(input_dir, output_dict, output_post):
    words = {}
    # sort the documents to be indexed
    sorted_files = sorted(glob.glob(input_dir+'/*'), 
            lambda x, y: cmp(int(os.path.basename(x)), int(os.path.basename(y))))

    # intermediate results will be written to fh1
    fh1 = open('intermediate.txt', 'w')

    all_fids = {}
    for fn in sorted_files:
        print fn
        fid = os.path.basename(fn)
        all_fids[fid] = 1
        my_words = read_process_text(fn)
        # each line in the intermediate file contains doc ID followed by all unique terms appear in this doc
        fh1.write(fid+' '+' '.join(my_words)+'\n')
        for w in my_words:
            words[w] = 1
    if words.has_key(''): del words['']
    words = sorted(words.keys())
    fh1.close()

    # store file/doc IDs
    all_fids = [int(a) for a in all_fids.keys()]
    all_fids.sort()

    fh2 = open(output_dict, 'w')
    fh3 = open(output_post, 'w')
    # first line of postings.txt stores the postings list for all documents for
    # the purpose of processing NOT query
    fh3.write(generate_skip_list(all_fids).__str__()+"\n")
    lineno = 2
    for w in words:
        print w
        fh1 = open('intermediate.txt', 'r')
        posting_list = []
        for line in fh1:
            my_words = line.split()
            fid = int(my_words.pop(0))
            if w in my_words:
                posting_list.append([fid,my_words.count(w)])
        #posting_list = generate_skip_list(posting_list)
        fh1.close()
        fh2.write(w+" "+str(len(posting_list))+" "+str(lineno)+"\n")
        fh3.write(posting_list.__str__()+"\n")
        lineno += 1
    fh2.close()
    fh3.close()

def usage():
    print "usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file"

if __name__ == "__main__":
    input_dir = output_dict = output_post = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
    except getopt.GetoptError, err:
        usage()
        sys.exit(2)
    for o, a in opts:
        if o == '-i':
            input_dir = a
        elif o == '-d':
            output_dict = a
        elif o == '-p':
            output_post = a
        else:
            assert False, "unhandled option"
    if input_dir == None or output_dict == None or output_post == None:
        usage()
        sys.exit(2)

    index_documents(input_dir, output_dict, output_post)
