#!/usr/bin/python
import re
import nltk
import sys
import getopt

'''
This support that mutiple categories build up.
'''
def build_LM(in_file):
    """
	
    build language models for each label
    each line in in_file contains a label and an URL separated by a tab(\t)
    """
    print 'building language models...'    
    # Pls implement your code in below
    ''' 
    
    This method is to build the language model, after executing this method, you 
    can get the model like the following format:
    OVERALL FORMAT 
    {
        label1:{key1:probility1,key2:probility2,...keyN:probilityN},
        label2:{key1:probility1,key2:probility2,...keyN:probilityN},
        ...
        labelN:{key1:probility1,key2:probility2,...keyN:probilityN}},
    }
    
    parameter: 
        in_file:String = the path for the input file to build the LM.
    return:
        modeldic: Dictionary = LM = The OVERALL FORMAT
    '''
    #N is for Ngram model; By changing the value N , you can get unigram, bigram,trigram...Ngram
    global N 
    N=5 
    modeldic = {}
    lines = open(in_file,'r')
    for line in lines:
        # re will get the things like 'News   http://', '.....url'
        cat_url = re.split("\t*://",line);
        #spliting by tab can get the label for category
        category = cat_url[0].split("\t")[0];
        url = cat_url[1].lower();
        #Build seperate NGram model for different categories.
        if category in modeldic.keys():
            modeldic[category] = nGram(N,url,modeldic[category]);
        else:
            modeldic[category]={};
            modeldic[category] = nGram(N,url,modeldic[category]);
    i = len(modeldic)-1;
    keyslist=modeldic.keys()
    #oneSmoothing dictionary to keep track that whether need oneSmoothing or not
    #Though most of time, we need one smoothing ,because it is really difficult that two LM are identical.
    oneSmoothing=modeldic.fromkeys(keyslist,False);
    #The following loop together to made the three language model has same Ngram...
    #Refers to the OVERALL FORMAT above, Ngram model here presents keys.
    while i>0:
        ii=i-1;
        while ii>-1:
            #complement of the Ngrams
            for key in (set(modeldic[keyslist[i]].keys())-set(modeldic[keyslist[ii]].keys())):
                oneSmoothing[keyslist[ii]]=True;
                #because one smoothing true,later list will +1 together, so here don't use 1.0 but 0.0
                modeldic[keyslist[ii]][key]=0.0
            for key in (set(modeldic[keyslist[ii]].keys())-set(modeldic[keyslist[i]].keys())):
                 oneSmoothing[keyslist[i]]=True;
                 modeldic[keyslist[i]][key]=0.0
            ii=ii-1;
        i=i-1
    #update the models 
    #counts of Ngram(Actual count if oneSmoothing=false, count+1 if onesmoothing=true) to probility
    for category in modeldic.keys():
        updateNGram(modeldic[category],oneSmoothing[category]);
    return modeldic		
    
def nGram(N,txt,NDic):
    '''
    
    It is to build ngram for given txt, and return 
    res=NDic which append keys:count for new key or update count for existing key.
    parameter:
        N: int value for N(this N)gram model
        txt:String need to interpreted as Ngram model
        NDic: The dictionary is either{} or {key1:count1,key2:count2,...keyN:countN}
    return:
        NDic: The dictionary = {key1:count1,key2:count2,...keyN:countN}
    '''
    if N> 1:
        space = "?" * (N-1)         # add N - 1 '?'
        txt = space + txt + space   # add both in front and back 

    # append the slices [i:i+N] to NDic
    for i in range( len(txt) - (N - 1) ):
        if txt[i:i+N] in NDic:
            NDic[txt[i:i+N]] += 1;
        else:
             NDic[txt[i:i+N]] = 1      
    return NDic                   # return the dictionary 

#import add operating for sum cacul.
from operator import add
def updateNGram(NDic,oneSmoothing):
    '''
    update the Ngram model by dealing with count accoring to oneSmoothing==true|false,
    and converting count to probility .
    parameter:
        NDic: The dictionary which has the structure {key1:count1,key2:count2,...keyN:countN}
        oneSmoothing: Bool value which means count+1 if this=true 
    return:
        NDic: The dictionary which has the structure {key1:prob1,key2:prob2,...keyN:probN}
    '''
    sum = 0;
    if oneSmoothing:
        for key in NDic.keys():        
            NDic[key] = NDic[key]+1;
    #sum=total count
    sum=reduce(add,NDic.values())
    #cacul the probility
    for key in NDic.keys():
        NDic[key] = float(NDic[key])/float(sum)        
    return NDic;


def judgeCategory(txt,dic):
    '''
    
    The method is to judge the category of given txt according to the LM dic
    parameter:
        txt: String
        dic:Dictionary of LM has the same format as OVERALL FORMAT introduced above
    return;
        String: Cate1(the maxvalue is from one category)
        String: Cate1\tCate2... (if probility of maxvalue=cate1=cate2=..cateN which is the max value)
    '''
    txtModel = {}
    txtModel = nGram(N,txt,txtModel)
    mycate="";
    probDic = dic.fromkeys(dic.keys(),1.0);
    for category in dic.keys():
        #intersection of the ngrams
        for key in (set(txtModel.keys()) & (set(dic[category].keys()))):
            probDic[category] *= (float(dic[category][key]))
        #Only when a typical new Ngram model will produce that probDic[category]=1.0
        if probDic[category]==1.0:
            probDic[category]=0.0
    maxvalue=max(probDic.values());
    #From the maxvalue to find the corresponding category
    for key in probDic.keys():
        if maxvalue == probDic[key]:
            mycate=mycate+key+"\t"
    return mycate
        
def test_LM(in_file, out_file, LM):
    """
    test the language models on new URLs
    each line of in_file contains an URL
    you should print the most probable label for each URL into out_file
    """
    print "testing language models..."
    # Pls implement your code in below
    '''
    
    This method is to test the LM according to new url file.
    parameter:
        in_file:string = input file path to testing the LM.
        out_file: string = the new created file path to save your testing results.
        LM:The language model, here this is typeof(dictionary)
    '''
   
    lines=open(in_file,'r');
    f=open(out_file,"w");
    for line in lines:
        f.write(judgeCategory(line,LM)+line)
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
