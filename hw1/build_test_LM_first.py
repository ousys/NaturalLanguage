#!/usr/bin/python
import re
import nltk
import sys
import getopt

def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and an URL separated by a tab(\t)
    """
    print 'building language models...'
    # This is an empty method
    # Pls implement your code in below    
    lines=open(in_file).readlines();
    arts=[];
    sports=[];
    news=[];
    global artsModel
    global newsModel
    global sportsModel    
    for line in lines:
        mycat=line.split("\thttp://");
        if mycat[0]=='Arts':
            arts.append(mycat[1]);
        elif mycat[0]=='Sports':
            sports.append(mycat[1]);
        elif mycat[0]=="News":
            news.append(mycat[1]);
    # Arts Language Model
    artsModel={}
    for artUrl in arts:
        artsModel=nGram(5,artUrl,artsModel)
    # News Language Model
    newsModel={}
    for newsUrl in news:
        newsModel=nGram(5,newsUrl,newsModel)  
    #Sports Language Model
    sportsModel={}
    for sportsUrl in sports:
        sportsModel=nGram(5,sportsUrl,sportsModel)
    for key in (set(sportsModel.keys())- set(newsModel.keys())):
        newsModel[key]=0.0
    for key in (set(artsModel.keys()) -set( newsModel.keys())):
        newsModel[key]=0.0
    for key in (set(newsModel.keys()) -set(sportsModel.keys())):
        sportsModel[key]=0.0
    for key in (set(artsModel.keys()) - set(sportsModel.keys())):
        sportsModel[key]=0.0
    for key in (set(sportsModel.keys()) -set( artsModel.keys())):
        artsModel[key]=0.0
    for key in (set(newsModel.keys()) - set(artsModel.keys())):
        artsModel[key]=0.0       
    updateNGram(artsModel)
    updateNGram(sportsModel)
    updateNGram(newsModel)
    print newsModel['la.ab'];
    return [artsModel,newsModel,sportsModel]
    
def nGram(N,txt,NDic):
    if N> 1:
        space = "?" * (N-1)         # add N - 1 '?'
        txt = space + txt + space   # add both in front and back 

    # append the slices [i:i+N] to NList
    for i in range( len(txt) - (N - 1) ):
        if NDic.has_key(txt[i:i+N]):
            NDic[txt[i:i+N]]+=1;
        else:
             NDic[txt[i:i+N]]=1      
    return NDic                   # return the list  

    
def updateNGram(NDic):
    sum=0;
    for key in NDic.keys():
        NDic[key]=NDic[key]+1;
    for value in NDic.values():
        sum+=value
    for key in NDic.keys():
        NDic[key]=float(NDic[key])/float(sum);
    return NDic;

def judgeCategory(txt):
    txtModel={}
    artsprob=1.0
    newsprob=1.0
    sportsprob=1.0
    category=""
    txtModel=nGram(5,txt,txtModel)
    for key in txtModel.keys():
        if artsModel.has_key(key):
            artsprob*=(float(artsModel[key]))
        if newsModel.has_key(key):
            newsprob*=(float(newsModel[key]))
        if sportsModel.has_key(key):
            sportsprob*=(float(sportsModel[key]))
    maxvalue=max(artsprob,newsprob,sportsprob)
    if maxvalue==artsprob:
        category+="Arts"
    if maxvalue==newsprob:
        category+="News"
    if maxvalue==sportsprob:
        category+="Sports"
    return category+"\t"
        
def test_LM(in_file, out_file, LM):
    """
    test the language models on new URLs
    each line of in_file contains an URL
    you should print the most probable label for each URL into out_file
    """
    print "testing language models..."
    # This is an empty method
    # Pls implement your code in below
    lines=open(in_file).readlines();
    f=open(out_file,"w");
    for line in lines:
        f.write(judgeCategory(line)+line)
    f.close()
def usage():
    print "usage: " + sys.argv[0] + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file"

input_file_b = input_file_t = output_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'b:t:o:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-b':
        input_file_b = a
    elif o == '-t':
        input_file_t = a
    elif o == '-o':
        output_file = a
    else:
        assert False, "unhandled option"
if input_file_b == None or input_file_t == None or output_file == None:
    usage()
    sys.exit(2)

LM = build_LM(input_file_b)
test_LM(input_file_t, output_file, LM)
