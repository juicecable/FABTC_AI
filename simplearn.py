#Copyright Derek Frombach
import json
import os
import operator
import statistics
import time

#VAULT STORAGE
words={} #This is the storage of the word data
catinfo={} #This is where the category totals are stored for the dependant filter
msgdata={} #This is where the dependant filter data is stored
catslist=[] #category list (only for savefile)

def buildvault(catlist): #Initalises the vault from the start (category list)
    global msgdata
    global catinfo
    global words
    global catslist

    try:
        if len(msgdata)>0:
            for x in list(msgdata.keys()):
                msgdata[x].clear()
                del msgdata[x]
        del msgdata
    except:
        pass
    try:
        del catinfo
    except:
        pass
    try:
        if len(words)>0:
            for x in list(words.keys()):
                words[x].clear()
                del words[x]
        del words
    except:
        pass
    words={}
    catinfo={}
    msgdata={}
    catslist=catlist.copy()
    for x in catlist:
        catinfo[x]=0
        msgdata[x]={}

def uniquefilter(word): #Apply the unique filter to a word and return the uniqueness (word)
    global words
    
    #if not word in words: #assert
    #    raise Exception('Word Does Not Exist!')
    a={}
    for x in words[word]:
        a[x]=words[word][x]
    a['u']-=sum([a[x] for x in a if x != 'u']) #Accounting for different storage format of u
    b=max(a.items(), key=operator.itemgetter(1))[0]
    bv=a[b]
    del a[b]
    c=max(a.items(), key=operator.itemgetter(1))[0]
    cv=a[c]
    del a
    return (bv-cv)/bv

def dependantfilter(word,cat): #Apply the dependant filter to a word and the return the dependancy (word, category)
    global msgdata

    #if not cat in msgdata: #assert
    #    raise Exception('Category Does Not Exist!')
    a=catinfo[cat]

    #if not word in msgdata[cat]: #assert
    #    raise Exception('Word Does Not Exist!')
    if not word in msgdata[cat]:
        b=0
    else:
        b=msgdata[cat][word]
    if a==0:
        return 0
    return b/a

def msgparse(msg): #Parses the messages into the words and phrases (message)
    nmsg=msg.replace('\u0097',' ').replace('\u00b4',"'").replace('\u00e9',"e").replace('\u0096'," ").replace('\u00ea',"e").replace('\u00f5',"o").replace('\u2019',"'").replace('\u2013',"-").replace('\u201c','"').replace('\u201d','"').replace('\u2018',"'").replace('\u2026',"...").replace('\u00ef',"i").replace('\u00e0',"a").replace('\u00bd',"1/2").replace('\u00e8',"e").replace('\u00f1',"n").replace('\u00a3',"$").replace('\u00a8'," ").replace('\u0091',"'").replace('\u00e5',"a").replace('\u00f6',"o").replace('\u00f3',"o").replace('\u0095'," ").replace('\u00fc',"u").replace('\u00ae',"r").replace('\u00a7',"ss")
    nmsg=nmsg.replace('`',"'").replace('...',' ... ').replace(',',' , ').replace('!',' ! ').replace('.',' . ').replace('?',' ? ').replace(':',' : ').replace(';',' ; ').replace('(',' ( ').replace(')',' ) ').replace('[',' [ ').replace(']',' ] ').replace('{',' { ').replace('}',' } ').replace('"',' " ').replace('--',' -- ').replace(' -',' - ').replace('- ',' - ').replace('/',' / ').replace('"',' " ').replace(' *',' * ').replace('* ',' * ').replace(" '"," ' ").replace("' "," ' ").replace('<',' < ').replace('>',' > ')
    msglist=nmsg.split(' ')
    for n in range(0,len(msglist)):
        msglist[n]=msglist[n].rstrip().lstrip().replace(' ','')
    return list(filter(None,msglist))

def upperbound(u): #Upper bound saftey function (unknown)
    return (u-1)/u

def lowerbound(u): #Lower bound safety function (unknown)
    return 1/u

def confidenceboost(u,p): #Minimum confidence requirement function (unknown, probability)
    if u<3: return 0.5
    return p

def wordgetmax(word): #Gets the max value category from a word (word)
    global words
    #if not word in words: #assert
    #    raise Exception('Word Does Not Exist!')
    a={}
    for x in words[word]:
        a[x]=words[word][x]
    a['u']-=sum([a[x] for x in a if x != 'u']) #Accounting for different storage format of u
    b=max(a.items(), key=operator.itemgetter(1))[0]
    del a
    return b

def weight(word,cat=None,bias=0): #Applies weighting to the word (word, category, bias)
    global words
    global msgdata

    dependantfilterenable=False          #Default is False
    uniquefilterenable=False             #Default is False
    rangesafetyfunctionsenable=True     #Default is True
    confidenceboostenable=True          #Default is True

    #if not word in words: #assert
    #    raise Exception('Word Does Not Exist!')

    if cat==None: #making it easier to use this function as starting point
        cat=wordgetmax(word)

    #if not cat in msgdata: #assert
    #    raise Exception('Category Does Not Exist!')

    u=words[word]['u']
    if cat!='u': #Accounting for difference type of storage in u
        p=min([words[word][cat]+bias,u])/u
    else:
        q=sum([words[word][x] for x in msgdata if x != 'u'])
        p=min([(words[word][cat]-q)+bias,u])/u
    if(confidenceboostenable):
        p=confidenceboost(u,p)
    if p!=0.5:
        if dependantfilterenable or uniquefilterenable:
            l=[]
            if uniquefilterenable:
                l.append(uniquefilter(word))
            if dependantfilterenable:
                l.append(dependantfilter(word,cat))
            w=max(l)
            p=(p*((0.5+(w/2))-(0.5-(w/2))))+(0.5-(w/2))
    if rangesafetyfunctionsenable:
        if p>=1.0:
            p=upperbound(u)
        if p<=0.0:
            p=lowerbound(u)
    return p

def addword(word): #Adds a word to the vault (word)
    global words
    global msgdata
    
    if True:
    #if not word in words: #assert
        words[word]={}
        for x in msgdata:
            words[word][x]=0

def addcat(cat): #Adds a category to the vault (category)
    global words
    global msgdata
    global catinfo
    global catslist

    if True:
    #if not cat in msgdata: #assert
        catinfo[cat]=0
        msgdata[cat]={}
        for x in words:
            words[x][cat]=0
        catslist.append(cat)

def remword(word): #Removes a word from the vault (word)
    global words
    global catinfo
    global msgdata
    
    if True:
    #if word in words: #assert
        for x in msgdata:
            del words[word][x]
            n=msgdata[x][word]
            del msgdata[x][word]
            catinfo[x]-=n
        del words[word]

def remcat(cat): #Removes a category from the vault (category)
    global words
    global catinfo
    global msgdata
    global catslist
    
    if cat!='u':
    #if cat in msgdata and cat!='u': #assert
        for x in words:
            n=words[x][cat]
            words[x]['u']-=n
            del words[x][cat]
        del catinfo[cat]
        msgdata[cat].clear()
        del msgdata[cat]
        catslist.remove(cat)

def classify(wordlist): #Classifies the message from the given word list (word list)
    global words
    
    reqcert=1 #Default 1, Better of Required Certainty 1-3

    c=[{},{},{}]
    cc=['','','']
    for bias in range(-1,2):
        for cat in msgdata:
            a=1.0
            b=1.0
            for word in wordlist:
                if word in words: #assert
                    n=weight(word,cat,bias)
                    a*=n
                    b*=1.0-n
            if a==0.0 and b==0.0:
                c[bias+1][cat]=0.0
            else:
                c[bias+1][cat]=a/(a+b)
        a=max(c[bias+1].items(), key=operator.itemgetter(1))[0]
        a=[a,c[bias+1][a]]
        cc[bias+1]=a
        b=c[bias+1]
        c[bias+1]=a
        del b
    if cc.count(cc[1]) >= reqcert:
        a=len(cc)-1-cc[::-1].index(cc[1])
        return c[a]
    elif cc.count(cc[0]) >= reqcert:
        a=len(cc)-1-cc[::-1].index(cc[0])
        return c[a]
    elif cc.count(cc[2]) >= reqcert:
        a=len(cc)-1-cc[::-1].index(cc[2])
        return c[a]
    else:
        a=1.0
        b=1.0
        for word in wordlist:
            if word in words: #assert
                n=weight(word,'u',1)
                a*=n
                b*=1.0-n
        return ['u', a/(a+b)]

def update(wordlist,cat,rep=False): #Single round of training for single message (word list, category, if second or higher round)
    global words
    global catinfo
    global msgdata

    if not cat in msgdata: #assert
        raise Exception('Category Does Not Exist!')

    wordset=list(set(wordlist)) #For dependant filter

    for word in wordlist:
        if not word in words:
            addword(word)
        if cat!='u':
            words[word][cat]+=1
        words[word]['u']+=1
    
    if not rep: #Make sure that dependant filter doesn't get repeat messages
        for word in wordset:
            if not word in msgdata[cat]:
                msgdata[cat][word]=0
            msgdata[cat][word]+=1
            catinfo[cat]+=1

def save(path='FABTCdata.txt'): #Saves the vault data (file path)
    global words
    global catinfo
    global msgdata
    global catslist

    f=open(path,'w')
    f.write(json.dumps([catslist,words,catinfo,msgdata]))
    f.close()

def load(path='FABTCdata.txt'): #Loads the vault data (file path)
    global words
    global catinfo
    global msgdata
    global catslist

    f=open(path,'r')
    d=json.loads(f.read())
    f.close()
    buildvault(d[0]) #Reinitalise everything
    words=d[1]
    catinfo=d[2]
    msgdata=d[3]

def categorise(wordlist,conf=0.5): #Categorises a message, is a wrapper for classify (word list, minimum confidence)
    global words

    a=classify(wordlist)
    b=a[0] #The classifcation
    c=a[1] #The confidence

    if b!='u':
        if c<=conf: #The confidence threshold required, default is 0.5
            b='u'
            e=1.0
            f=1.0
            for word in wordlist:
                if word in words: #assert
                    n=weight(word,'u',1)
                    e*=n
                    f*=1.0-n
            c=a/(a+b)
    return [b,c]

def train(msgs): #Trains the program (messages dictionary)
    global msgdata
    global words

    debug=False #Default is True

    #First Time Training
    save('~FABTCbeforetrain.tmp') #Backup before making major modifications
    #Updating
    for cat in msgs:
        for msg in msgs[cat]:
            wordlist=msgparse(msg)
            update(wordlist,cat,False)
    
    #Verifying Accuracy
    caa={} #Average accuracy
    nff={} #Percent of failed messages
    for cat in msgs:
        acc=0
        n=0
        nf=0
        for msg in msgs[cat]:
            wordlist=msgparse(msg)
            c=categorise(wordlist)
            a=c[0] #Category
            b=c[1] #Confidence
            n+=1
            if a!=cat:
                msgs[cat][msg]=0.0-b
                nf+=1
            else:
                msgs[cat][msg]=b
                acc+=b
        if n!=0:
            caa[cat]=acc/n
            nff[cat]=nf/n

    oa=sum([caa[x] for x in caa if x!='u'])/len(caa) #Overall average accuracy
    off=sum([nff[x] for x in caa if x!='u'])/len(nff) #Overall average percentage failed

    if debug:
        print()
        print('End Single Training')
        print('Overall Accuracy: '+str(oa))
        print('Percentage Failed: '+str(off))
        for cat in caa:
            print('Category: '+cat)
            print('Accuracy: '+str(caa[cat]))
            print('Failed: '+str(nff[cat]))
        print()

    oldmsgs={} #Deepcopy the messages to allow for the system to auto-determine when to stop training
    for cat in msgs:
        oldmsgs[cat]={}
        for msg in msgs[cat]:
            oldmsgs[cat][msg]=msgs[cat][msg]
    oldcaa={}
    for x in caa:
        oldcaa[x]=caa[x]
    oldnff={}
    for x in nff:
        oldnff[x]=nff[x]
    oldoa=oa
    oldoff=off


    #Repetition Training
    didbreak=False #Ended the bad way
    for i in range(0,max([len(words),4])): #To prevent an infinite loop, one should never need to train more times than there are words
        save('~FABTCbeforerep.tmp') #Backup before starting a repetition

        #Updating Undertrained Messages
        for cat in msgs:
            for msg in msgs[cat]:
                if msgs[cat][msg]<=0.0: #If the message is undertrained
                    wordlist=msgparse(msg)
                    update(wordlist,cat,True)

        #Verifying Accuracy
        del caa
        del nff
        caa={} #Average accuracy
        nff={} #Percent of failed messages
        for cat in msgs:
            acc=0
            n=0
            nf=0
            for msg in msgs[cat]:
                wordlist=msgparse(msg)
                c=categorise(wordlist)
                a=c[0] #Category
                b=c[1] #Confidence
                n+=1
                if a!=cat:
                    msgs[cat][msg]=0.0-b
                    nf+=1
                else:
                    msgs[cat][msg]=b
                    acc+=b
            if n!=0:
                caa[cat]=acc/n
                nff[cat]=nf/n

        oa=sum([caa[x] for x in caa if x!='u'])/len(caa) #Overall average accuracy
        off=sum([nff[x] for x in caa if x!='u'])/len(nff) #Overall average percentage failed

        #Checking if another round needs to be done
        oadiff=oa-oldoa #Difference in overall accuracy between rounds
        offdiff=off-oldoff #Difference in messages failed between rounds

        difflist=[] #Accuracy difference list
        for cat in msgs: #Generating the difference list
            if cat!='u':
                for msg in msgs[cat]:
                    difflist.append(msgs[cat][msg]-oldmsgs[cat][msg])
        
        diff=sum(difflist)/len(difflist) #The difference score
        if diff<=0.0: #If the last iteration made the training worse
            load('~FABTCbeforerep.tmp') #Revert to backup
            didbreak=True #Ended the good way
            break

        #As it seems the training is improving past this point, the old data may now be overridden
        if debug:
            print()
            print('End Repetition Training Iteration: '+str(i+1))
            print('Overall Accuracy: '+str(oa))
            print('Overall Accuracy Difference: '+str(oadiff))
            print('Percentage Failed: '+str(off))
            print('Percentage Failed Difference: '+str(offdiff))
            print('Difference Score: '+str(diff))
            print('Max Difference Score: '+str(max(difflist)))
            print('Min Difference Score: '+str(min(difflist)))
            print('Mode Difference Score: '+str(statistics.mode(difflist)))
            print('Variance Difference Score: '+str(statistics.variance(difflist)))
            print('Stdev Difference Score: '+str(statistics.stdev(difflist)))
            for cat in caa:
                print('Category: '+cat)
                print('Accuracy: '+str(caa[cat]))
                print('Accuracy Difference: '+str(caa[cat]-oldcaa[cat]))
                print('Failed: '+str(nff[cat]))
                print('Failed Difference: '+str(nff[cat]-oldnff[cat]))
            print()

        for cat in msgs:
            for msg in msgs[cat]:
                oldmsgs[cat][msg]=msgs[cat][msg]
        for x in caa:
            oldcaa[x]=caa[x]
        for x in nff:
            oldnff[x]=nff[x]
        oldoa=oa
        oldoff=off
    
    #The training is done, now report the results and cleanup
    if not debug:
        os.remove('~FABTCbeforerep.tmp') #cleanup unessicary files
    else:
        if didbreak:
            print('Ended the Good Way')
        else:
            print('Ended the Bad Way!')
        print()
        print('Training Done!')
        print('Overall Accuracy: '+str(oldoa))
        print('Percentage Failed: '+str(oldoff))
        for cat in oldcaa:
            print('Category: '+cat)
            print('Accuracy: '+str(oldcaa[cat]))
            print('Failed: '+str(oldnff[cat]))
        print()
    save('~FABTCposttrain.tmp') #Backup the good progress
    #Cleanup the trash
    del caa
    del nff
    del oldcaa
    del oldnff
    for cat in oldmsgs:
        oldmsgs[cat].clear()
    del oldmsgs

    return [oldoa,oldoff]

def manualtrain(): #Manually train the program using the interactive command line
    global msgdata

    if len(msgdata)<=1: #No classes exist
        while True: #Initial Category Creation Loop
            b=input('Do you want to create a new category? (y/n): ').lower().rstrip().lstrip()
            if b.lower()=='y':
                a=input('Enter the new category name: ').lower().rstrip().lstrip()
                b=input('Is this your category name: '+a+' ? (y/n): ').lower().rstrip().lstrip()
                if b=='y':
                    addcat(a)
                    print('Category Added Sucessfully')
            elif b=='n':
                print('')
                break

    tempclass={}
    classmsgs={}
    for x in msgdata:
        tempclass[x]={}
        classmsgs[x]=0
    save=True
    qquit=False
    while True: #Menu Outer Loop
        while True: #Entry Loop
            msg=input('Enter the message (or m to enter the menu): ').lower().rstrip().lstrip()
            if msg=='m': #Enter the Menu
                break
            while True: #Categorisation Loop
                print('What Category is this: ').lower().rstrip().lstrip()
                print('')
                a=input(', '.join(list(msgdata.keys()))+': ').lower().rstrip().lstrip()
                if a in tempclass:
                    if not msg in tempclass[a]: #assert
                        tempclass[a][msg]=1.0
                        classmsgs[a]+=1
                    else:
                        print('Duplicate messages are not allowed in the same category!')
                    break
                print('Press n if the word is unknown, press c to cancel')
                b=input('Do you want to create a new category? (y/n/c): ').lower().rstrip().lstrip()
                if b=='y':
                    addcat(a)
                    tempclass[a]={}
                    classmsgs[a]=0
                    tempclass[a][msg]=1.0
                    classmsgs[a]+=1
                    break
                elif b=='n':
                    if not msg in tempclass['u']: #assert
                        tempclass['u'][msg]=1.0
                        classmsgs['u']+=1
                    break
                elif b=='c':
                    break
                print('')
        #Beginning of Menu Inner Loop
        while True:
            a=input('Do you want to continue (c), quit (q), or save and quit (s): ').lower().rstrip().lstrip()
            if a=='c':
                save=False
                qquit=False
                break
            elif a=='q':
                a=input('Are you sure you want to quit without saving? (y/n): ').lower().rstrip().lstrip()
                if a=='y':
                    save=False
                    qquit=True
                    del classmsgs
                    for x in tempclass:
                        tempclass[x].clear()
                    del tempclass
                    break
            elif a=='s':
                print('Are you sure you want to save and quit,')
                b={}
                for x in classmsgs:
                    b[x]=classmsgs[x]
                a=max(classmsgs.items(), key=operator.itemgetter(1))[0]
                del b[a]
                a=input('The data is biased towards category '+max(classmsgs.items(), key=operator.itemgetter(1))[0]+' by '+classmsgs[a]-max(b.items(), key=operator.itemgetter(1))[1]+' messages? (y/n): ').lower().rstrip().lstrip()
                del b
                if a=='y':
                    save=True
                    qquit=True
                    break
        #End of All Prompts
        if save:
            a=train(tempclass)
            print('')
            print('Trained and Saved')
            print('Accuracy: '+str(a[0]))
            print('Failed: '+str(a[1]))
            del classmsgs
            for x in tempclass:
                tempclass[x].clear()
            del tempclass
        if qquit:
            break

def autotrain(msgsdict): #Automatically train the program by inputting the contents in a dictionary ({'catA':['first message','second message'],'catB':['third message','fourth message']})
    global msgdata

    tempclass={}
    classwords={}
    wdict={}
    for x in msgdata:
        tempclass[x]={}
        classwords[x]=0
    
    for cat in msgsdict:
        if not cat in msgdata:
            addcat(cat)
            tempclass[cat]={}
            classwords[cat]=0
            wdict[cat]=[]
        for msg in msgsdict[cat]:
            if len(msg)>1:
                word=msgparse(msg)
                for x in word:
                    if not x in wdict[cat]:
                        wdict[cat].append(x)
                    classwords[cat]+=1
                tempclass[cat][msg]=1.0

    c={}
    for x in classwords:
        c[x]=classwords[x]
    cab=max(classwords.items(), key=operator.itemgetter(1))[0]
    b=c[cab]
    del c[cab]
    a=max(c.items(), key=operator.itemgetter(1))[1]
    del c
    c=(b-a)/a

    d=train(tempclass)
    del classwords
    del wdict
    for x in tempclass:
        tempclass[x].clear()
    del tempclass
    d.append(c)
    return d

def check(msgs): #Determines the accuracy of test data (messages)
    global msgdata

    #Verifying Accuracy
    caa={} #Average accuracy
    nff={} #Percent of failed messages
    for cat in msgs:
        acc=0
        n=0
        nf=0
        for msg in msgs[cat]:
            wordlist=msgparse(msg)
            c=categorise(wordlist)
            a=c[0] #Category
            b=c[1] #Confidence
            n+=1
            if a!=cat:
                msgs[cat][msg]=0.0-b
                nf+=1
            else:
                msgs[cat][msg]=b
                acc+=b
        if n!=0:
            caa[cat]=acc/n
            nff[cat]=nf/n

    oa=sum([caa[x] for x in caa if x!='u'])/len(caa) #Overall average accuracy
    off=sum([nff[x] for x in caa if x!='u'])/len(off) #Overall average percentage failed

    del caa
    del nff
    return [oa,off]

def verify(msgsdict): #Automatically verify the accuracy of the program by inputting the contents in a dictionary ({'catA':['first message','second message'],'catB':['third message','fourth message']})
    global msgdata

    tempclass={}
    for x in msgdata:
        tempclass[x]={}
    
    for cat in msgsdict:
        if cat in msgdata:
            for msg in msgsdict[cat]:
                tempclass[cat][msg]=1.0

    d=check(tempclass)
    for x in tempclass:
        tempclass[x].clear()
    del tempclass
    return d

#Init
buildvault(['u']) #Do not modify this line

#Everything below is temporary

q={'p':[],'n':[]}

f=open('pos.txt','rb')
d=f.read().decode('utf-8','ignore')
f.close()
q['p']=d.rstrip().lstrip().lower().splitlines()

f=open('neg.txt','rb')
d=f.read().decode('utf-8','ignore')
f.close()
q['n']=d.rstrip().lstrip().lower().splitlines()

aaa=time.perf_counter()
a=autotrain(q)
del q
bbb=time.perf_counter()
print(bbb-aaa)

print(a)

save()