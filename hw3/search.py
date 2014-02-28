#!/usr/bin/python

import sys, getopt, linecache, re
import index
from index import VBDecode

word_dict = {}
ops = ["(", ")", "AND", "OR", "NOT",'"']
all_length=0
postings_file = None
f = None
all_fids = None
# according to page 34 of IIR, skips for intermediate results are not available
# but we may choose to support this by change always_insert_skips to True
always_insert_skips = False 

def reconstruction(terms):
    dic ={}   
    i = 0
    while len(terms)>0:
        f.seek(word_dict[terms[0]][1]),
        f.read(word_dict[terms[0]][2])
        #strs=linecache.getline(postings_file, word_dict[terms[0]][1])
        dic[i]=singleline(strs)
        terms.pop(0)
        i += 1
    return dic

def position(terms,lst):
    #print lst, terms
    res=[]
    lst = [a[0][0] for a in lst]
    if isinstance(terms[0],list):
        dic={}
        for i in range(0,len(terms)):
            dic[i]=terms[i]
    else:
        dic = reconstruction(terms)
    for i in range(0,len(terms)):
        dic[i]=[ele[0] for ele in dic[i]]
        #print "dici",dic[i] 
        others=filter(lambda a: a[0] in lst,dic[i])
        dic[i]=others
    offset = 0
    #print "0 ",dic[0]," 1 ",dic[1]
    #print "length", lst
    for docid in lst:
       print docid
       offset = 1
       term1list = dic[0].pop(0)[1]
       add_to = True
       print "lentgh",len(terms)
       for i in range(1,len(terms)):
           lst2=[(e-offset) for e in dic[i].pop(0)[1]]
           print lst2, term1list
           if len(set(lst2)&set(term1list))>0:
               print lst2, term1list
               term1list =(list)(set(lst2)&set(term1list))
           else:
               add_to = False
               #print "here"
               break   
           offset += 1
       #print "here2"
       if add_to:
           print res
           res.append(docid)     
    res=[[[e10]] for e10 in res]
    return res

def singleline(strs):
    lst=[]
    decodelist=VBDecode(bytearray(strs))
    print decodelist
    i=0
    previousFID = 0
    while i < len(decodelist):
        e=[]
        e.append(decodelist[i]+previousFID)
        previousFID += decodelist[i]
        length = decodelist[i+1]
        if(decodelist[i+2])!=0:
            lst.append([e,decodelist[i+2]])
        else:
            lst.append([e])
        previous_item_id = 0
        ls2=[]
        for item in decodelist[i+3:i+3+length]:
            ls2.extend([item+previous_item_id])
            previous_item_id = item+previous_item_id
        e.append(ls2)
        i = i+3+length
    #print lst
    return lst
            
'''
def singleline(strs):
    lst=[]
    i =0
    byteA=bytearray()
    byteB=bytearray()
    e=[]
    nopointer = True 
    previousFID = 0
    while i < len(strs)-1: #Not end of this line
        if strs[i] == ' ':
            i += 1
            ls1 = VBDecode(byteA)         
            e.append(ls1[0]+previousFID)
            previousFID = ls1[0]+previousFID
            ls1.pop(0)
            previous_item_id=0
            ls2=[]
            for item in ls1:                    
                ls2.extend([item+previous_item_id])
                previous_item_id = item+previous_item_id
            e.append(ls2)
            if len(byteB)>0:
                lst.append([e,VBDecode(byteB)[0]])
            else:
                lst.append([e])
            e=[]
            nopointer = True
            byteA=bytearray()
            byteB=bytearray()
        else:
            if strs[i]!=',':
                if nopointer:
                    byteA.append(strs[i])
                else:
                    byteB.append(strs[i])
            else:
                nopointer = False    
            i+=1
    #print lst
    return lst
  '''          
        
def load_dictionary(input_dict):
    """
    load dictionary into word_dict
    word_dict maps a word to a list [frequency, posting pointer]
    """
    global all_length
    all_length=(int)(linecache.getline(input_dict,1).split()[2])
    fh = open(input_dict)
    for line in fh:
        ws = line.split()
        word_dict[ws[0]] = [int(e) for e in ws[1:]]
    fh.close()

def union_with_skips(p1, p2):
    """
    union two postings lists together
    """
    tmp_dict = {}
    for a in p1:
        tmp_dict[a[0][0]] = 1
    for a in p2:
        tmp_dict[a[0][0]] = 1
    answer = tmp_dict.keys()
    answer.sort()
    answer = index.generate_skip_list(answer, always_insert_skips)
    answer = [[e] for e in answer]
    return answer

def intersect_with_skips(p1, p2):
    """
    algorithm in figure 2.10 of IIR
    intersect two postings lists together
    """
    if p1 == [] or p2 == []: return []
    
    answer = []
    ptr1 = 0
    ptr2 = 0
    #print "here ", p1 ,p2
    while ptr1 != len(p1) and ptr2 != len(p2):
        if p1[ptr1][0][0] == p2[ptr2][0][0]:
            answer.append(p1[ptr1][0][0])
            ptr1 += 1
            ptr2 += 1
        else:
            if p1[ptr1][0][0] < p2[ptr2][0][0]:
                # len(p1[ptr1]) == 2 means hasSkip
                # p1[ptr1][1] is the skip pointer
                if len(p1[ptr1]) == 2 and p1[ p1[ptr1][1] ][0] <= p2[ptr2][0][0]:
                    while len(p1[ptr1]) == 2 and p1[ p1[ptr1][1] ][0] <= p2[ptr2][0][0]:
                        ptr1 = p1[ptr1][1]
                else:
                    ptr1 += 1
            else:
                if len(p2[ptr2]) == 2 and p2[ p2[ptr2][1] ][0] <= p1[ptr1][0][0]:
                    while len(p2[ptr2]) == 2 and p2[ p2[ptr2][1] ][0] <= p1[ptr1][0][0]:
                        ptr2 = p2[ptr2][1]
                else:
                    ptr2 += 1
    if answer == []:
        return []
    else:
        return [[e] for e in index.generate_skip_list(answer, always_insert_skips)]

def process_query_list(qlist):
    # process parentheses
    qlist2 = []
    while len(qlist) != 0:
        if qlist[0] == '"':
            sub_qlist = []
            qlist.pop(0)
            while qlist[0] !='"':
                sub_qlist.append(qlist.pop(0))
            qlist.pop(0)
            firststep = process_AND(sub_qlist)
            #print "firstep ",firststep
            qlist2.append(position(sub_qlist,firststep))
  
        elif qlist[0] == "(":
            sub_qlist = []
            qlist.pop(0)
            while qlist[0] != ")":
                sub_qlist.append(qlist.pop(0))
            qlist.pop(0)
            posting_list = process_query_list(sub_qlist)[0]
            qlist2.append(posting_list)
            
        else:
            qlist2.append(qlist.pop(0))

    # process NOTs
    qlist3 = []
    while len(qlist2) > 0:
        if qlist2[0] == "NOT":
            qlist2.pop(0)
            qlist3.append(process_NOT(qlist2.pop(0)))
        else:
            qlist3.append(qlist2.pop(0))
            
    # process ANDs and ORs
    while len(qlist3) >= 3:
        a  = qlist3.pop(0)
        op = qlist3.pop(0)
        b  = qlist3.pop(0)
        if op == "OR":
            posting_list = process_OR([a, b])
            qlist3.insert(0, posting_list)
        elif op == "AND":
            and_list = []
            and_list.append(a)
            and_list.append(b)
            while len(qlist3) >= 2 and qlist3[0] == "AND":
                qlist3.pop(0)
                and_list.append(qlist3.pop(0))
            posting_list = process_AND(and_list)
            qlist3.insert(0, posting_list)
    return qlist3

    # process parentheses
    qlist2 = []         
    while len(qlist) != 0:
        if qlist[0] == "(":
            sub_qlist = []
            qlist.pop(0)
            while qlist[0] != ")":
                sub_qlist.append(qlist.pop(0))
            qlist.pop(0)
            posting_list = process_query_list(sub_qlist)[0]
            qlist2.append(posting_list)
        else:
            qlist2.append(qlist.pop(0))
    # process NOTs
    qlist3 = []
    while len(qlist2) > 0:
        if qlist2[0] == "NOT":
            qlist2.pop(0)
            qlist3.append(process_NOT(qlist2.pop(0)))
        else:
            qlist3.append(qlist2.pop(0))
            
    # process ANDs and ORs
    while len(qlist3) >= 3:
        a  = qlist3.pop(0)
        op = qlist3.pop(0)
        b  = qlist3.pop(0)
        if op == "OR":
            posting_list = process_OR([a, b])
            qlist3.insert(0, posting_list)
        elif op == "AND":
            and_list = []
            and_list.append(a)
            and_list.append(b)
            while len(qlist3) >= 2 and qlist3[0] == "AND":
                qlist3.pop(0)
                and_list.append(qlist3.pop(0))
            posting_list = process_AND(and_list)
            qlist3.insert(0, posting_list)
    return qlist3

def process_NOT(a):
    # read the postings list for all doc ID's into all_fids when this function is first called
    global all_fids
    if all_fids == None:
        #all_fids = [pair[0] for pair in eval(linecache.getline(postings_file, 1))]
        print all_length
        f.seek(0)
        all_fids = [pair[0][0] for pair in singleline(f.read(all_length))]
        
    if not isinstance(a, list):
        f.seek(word_dict[a][1])
        a_fids = [pair[0][0] for pair in singleline(f.read(word_dict[a][2]))]
    else:
        a_fids = [pair[0][0] for pair in a]
    other_fids = filter(lambda a: a not in a_fids, all_fids)
    return [[e] for e in index.generate_skip_list(other_fids, always_insert_skips)]

def process_OR(pair):
    """
    process a pair of terms/postings that are OR'ed
    """
    if not isinstance(pair[0], list):
        print word_dict[pair[0]]
        f.seek(word_dict[pair[0]][1])
        print len(word_dict[pair[0]])
        p1 = singleline(f.read(word_dict[pair[0]][2]))
    else:
        p1 = pair[0]
    if not isinstance(pair[1], list):
        print word_dict[pair[1]]
        f.seek(word_dict[pair[1]][1])
        p2 = singleline(f.read(word_dict[pair[1]][2]))
    else:
        p2 = pair[1]
    return union_with_skips(p1, p2)

def process_AND(lst):
    """
    process a list of terms/postings that are AND'ed
    """
    for i in range(0, len(lst)):
        if not isinstance(lst[i], list):
            f.seek(word_dict[lst[i]][1])
            lst[i] = singleline(f.read(word_dict[lst[i]][2]))
    # sort the list by frequency so that less frequent terms come first
    lst = sorted(lst, lambda x, y: cmp(len(x), len(y)))
    while len(lst) > 1:
        p1 = lst.pop(0)
        p2 = lst.pop(0)
        lst.insert(0, intersect_with_skips(p1,p2))
    return lst[0]


def search_query(query):
   
    qlist = re.split('([ ()"])', query)
    #print qlist
    qlist = filter(lambda a: a != "" and a != " ", qlist)     # remove " " and ""
    for i in range(0, len(qlist)):
        if qlist[i] not in ops:
            # stem query words
            qlist[i] = index.stemmer.stem_word(qlist[i].lower())   
            if not word_dict.has_key(qlist[i]):
                # assign empty list to words not in dictionary
                qlist[i] = []
    # qlist only contains one query term
    #print qlist
    if len(qlist) == 1:
        if isinstance(qlist[0], list):
            res_list = qlist
        else:
            f.seek(word_dict[qlist[0]][1])
            print(word_dict[qlist[0]][2])
            res_list = [singleline(f.read(word_dict[qlist[0]][2]))]
    else:
        res_list = process_query_list(qlist)
        
    '''print [a[0] for a in res_list[0]]'''
    if len(res_list[0])>0:
        res = [pair[0] for pair in res_list[0]]
        #print res
        if isinstance(res[0],list):
            return " ".join(str(a[0]) for a in res)
        else:
            return " ".join(str(a) for a in res)
    else:
        return "\n"

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
    f = open(postings_file,"rb")
    if dictionary_file == None or postings_file == None or query_file == None or result_file == None:
        usage()
        f.close()
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
                f.close()
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
        f.close()