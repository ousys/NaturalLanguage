== General Notes about this assignment ==

Place your comments or requests here for Min and Ziheng to read.
Discuss your architecture or experiments in general.  A paragraph or
two is usually sufficient.
The overall format for implement the languge model is :
    {
        label1:{key1:probility1,key2:probility2,...keyN:probilityN},
        label2:{key1:probility1,key2:probility2,...keyN:probilityN},
        ...
        labelN:{key1:probility1,key2:probility2,...keyN:probilityN}},
    }
Label = category
key1...keyN= the ngram model (n=5)
probility1....probilityN= the probility for the ngram model.
By using this format , it supports mutiple categories, and it can be 
extended easily.

History:
At the beginning ,I wrote the build_test_LM_first.py for supporting only
the 3 Label: News , Arts, Sports, and I also assumed that the 3 language models
are not the same which means all need 1 smoothing.
Finally , I decided re-code it by using the above structure, which support more
labels and also judge whether LM need oneSmoothing or not and easy to extend or modify.
Very detailed instruction given in build_test_LM.py

Custom Function Brief: (Details included in the source file)
	build_LM: build LM
	nGram: generate Ngram
	updateNGram: update Ngram, this should be called for finalizing the LM to the overall format
	judgeCategory:to judge which category (keys in the Overall format) it belongs to
	test_LM:test the LM by using new testing url collection file
	usage: How to run the python function


== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.
build_test_LM_first.py: Refers to general notes, no use for build_test_LM_first.py
build_test_LM.py: The files to build and test the language model.
eval.py: Evalute the accuracy 
urls.build.txt: The file for buiding the LM
urls.test.txt: The urls collection for testing the LM
urls.correct.txt:The correct output supposed to be for urls.test.txt by using build_test_LM.py
output.txt: My testing result containing Label'\t'url
README: Read me document containing general noted,etc.
essay: Answers to the essay questions


== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>
Python function reference: 	
	http://www.tutorialspoint.com/python/ (Mostly used for dictionary , list , set)
Python efficiency:	 
	http://bayes.colorado.edu/PythonIdioms.html (Help me solved the very slow running speed problem)
NGram generating for a word :	
	http://www.daniweb.com/forums (Help me implement the NGram function for list of urls using dictionary)
Very little reference for NGram model:	 
	http://nltk.googlecode.com, I found there was existing function for NGram , but dunno how to use it. 



