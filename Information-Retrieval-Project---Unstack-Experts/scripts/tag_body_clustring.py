'''
@author : Ashwini Singh  Date: 04/10/2014
@updated : Chunky Gupta  Date : 04/15/2014

This is create clusters using  the stackoverflow tags  and Virtual tags 
'''

import os
from collections import defaultdict
import cjson
import re
from time import time
import numpy as np
import heapq

from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
import math

from scipy import sparse
#Utility Functions

def log10(x):
    return math.log(x) / math.log(10)
def getIDF(x, totalDocCount):
    return log10(totalDocCount/x)
def getTF(x):
    return 1+log10(x)


#######Global Variables##########
GlobalTagList=defaultdict(int)
GlobalPostUserDict=defaultdict(int)
GlobalParentChildDict=defaultdict(lambda: defaultdict(lambda: defaultdict()))
GlobalTagCount=0
GlobalPostTagsDict=defaultdict()
clusterData=np.zeros(shape=(10,10), dtype=float) #dummy
GlobalUserDict=defaultdict(lambda: defaultdict())

FILTERED_USER_PATH_JSON="/mnt/stackoverflow/data/parseddata/jsonUserDetailsFinal.json"

def parseUserFile():
    filteredData = open(FILTERED_USER_PATH_JSON,'r')
    for line in filteredData: #parsing tweets data file to generate a graph by adding edges
        userData = cjson.decode(line)
        uid = userData["userId"]
        if uid not in GlobalUserDict:
            
            GlobalUserDict[uid]["name"]=userData["displayName"]
            GlobalUserDict[uid]["reputation"]=userData["reputation"]
            GlobalUserDict[uid]["location"]=userData["location"]


def getuser(postId):
    rv =defaultdict()
    userId= GlobalPostUserDict[postId]
    if userId in GlobalUserDict:
        rv =GlobalUserDict[userId]
    return rv


def extractCluster(postIds,KMeanClusterDist):
    clusterDict= defaultdict(lambda: defaultdict(str))
    sample_no=0
    for postId in postIds:
        clusterID="cluster"+str(KMeanClusterDist[sample_no])
        sample_no+=1
        #uid=str(len(clusterDict[clusterID]))
        uid=GlobalPostUserDict[postId]
        clusterDict[clusterID][uid]=getuser(postId)
        clusterDict[clusterID]["tags"]+=str(GlobalPostTagsDict[postId])
    return clusterDict

def getTop2tags(tagsStr):
    if len(tagsStr)==0:
        return ""
    tagDict=defaultdict(int)
    tagList=re.sub(r'[><]',' ', tagsStr).split()
    for tag in tagList:
        tagDict[tag]+=1
        
    heap = [(-value, key) for key,value in tagDict.items()]
    largest = heapq.nsmallest(2, heap)
    largest = [(key, -value) for value, key in largest]
    rv=""
    for doc in largest:
        rv+=str(doc[0])+"-"
    
    return rv;
    
def writeCluterToFile(clusterDict):
    filename="/mnt/stackoverflow/data/parseddata/displayCluster.json"
    f = open (filename, 'w')
    finalContent="{"
    started2=0
    DoneUserDict=defaultdict()
    for clusterID in clusterDict:
        if started2 !=0:
                finalContent+=","
        started2=1
        finalContent += "\"" + clusterID + ":" +getTop2tags(clusterDict[clusterID]["tags"])+"\":"
        usertext=""
        #[{ "Name": ["id","email"]},{"Name2": ["id","email"]}]
        started=0
        for usrs in clusterDict[clusterID]:
            if usrs in DoneUserDict:
                continue
            if usrs=="tags":
                continue
            if started !=0:
                usertext+=","
            started=1
            
            usertext+="{ \"Name\":[\"" +str(clusterDict[clusterID][usrs]["name"].encode('utf8'))+"\",\""+str(clusterDict[clusterID][usrs]["location"].encode('utf8'))+"\"]}"
            DoneUserDict[usrs]="d"
        finalContent+="["+usertext+"]"
    finalContent+="}"

    f.write(finalContent)
    f.close()


##### K Mean Funtions ############33
def bench_k_means(estimator, name, data, sample_size, labels,postIds):
    data=sparse.csr_matrix(data)
    t0 = time()
    print("Performing dimensionality reduction using LSA")
    t0 = time()
    lsa = TruncatedSVD(500)

    data = lsa.fit_transform(data)
    data = Normalizer(copy=False).fit_transform(data)

    print("done in %fs" % (time() - t0))
    print()

    #sData=sparse.csr_matrix(data)
    val=estimator.fit(data)
    print('% 9s   %.2fs    %i   %.3f   %.3f   %.3f   %.3f   %.3f '
          % (name, (time() - t0), estimator.inertia_,
             metrics.homogeneity_score(labels, estimator.labels_),
             metrics.completeness_score(labels, estimator.labels_),
             metrics.v_measure_score(labels, estimator.labels_),
             metrics.adjusted_rand_score(labels, estimator.labels_),
             metrics.adjusted_mutual_info_score(labels,  estimator.labels_)))

    print("Parsing USer File:")
    parseUserFile()
    print("extracting User File:")
    clusterDict=extractCluster(postIds,estimator.labels_)
    print("writing Cluster Data to File")
    writeCluterToFile(clusterDict)

def createKcluster(clusterData,clustersize,samplesize,labels,postIds):
    data = clusterData
    n_samples, n_features = data.shape
    n_digits = clustersize
    print("n_digits: %d, \t n_samples %d, \t n_features %d"  % (n_digits, n_samples, n_features))


    print(79 * '_')
    print('% 9s' % 'init'
          '    time  inertia    homo   compl  v-meas     ARI AMI  silhouette')
    bench_k_means(KMeans(init='k-means++', n_clusters=n_digits, n_init=10),
              name="k-means++", data=data, sample_size=samplesize, labels=labels,postIds=postIds)


def accumulateOriginalTags(tagText):
    global GlobalTagCount
    if len(tagText)==0:
        return

    tagList=re.sub(r'[><]',' ', tagText).split()

    for tag in tagList:
        if tag =="&lt" or tag=="&gt":
            continue
        if tag not in GlobalTagList:
            GlobalTagList[tag]=GlobalTagCount
            GlobalTagCount+=1


def processrecord(data,sampleId):
    global clusterData
    tagText=data["tags"]
    GlobalPostTagsDict[data["postId"]]=data["tags"]
    if len(tagText) !=0:
        tagList=re.sub(r'[><]',' ', tagText).split()
        for tag in tagList:
            tagIndex=GlobalTagList[tag]
            clusterData[sampleId][tagIndex]+=1


######Creating Virtual Tags################

def getTop20results(docScoreDict):
    heap = [(-value, key) for key,value in docScoreDict.items()]
    largest = heapq.nsmallest(10, heap)
    largest = [(key, -value) for value, key in largest]
    return largest;


def getVirtualTags(threadDoc):
    WordDocDictionary = defaultdict(lambda: defaultdict(int))
    documentWordFreqDict = defaultdict(lambda: defaultdict(int))
    total_N_doc=0
    if len(threadDoc)>0:
        title=threadDoc[threadDoc.keys()[0]]["title"]
        for word in re.findall("[a-z0-9]+", title):
            if word:
                WordDocDictionary[word]["doc0"] += 1
                documentWordFreqDict["doc0"][word] += 1
                total_N_doc+=1
    docId=0
    for post in threadDoc:
        if threadDoc[post]["body"]:
            bodyText=threadDoc[post]["body"]
            docId+=1
            for word in re.findall("[a-z0-9]+", bodyText):
                if word:
                    docname="doc"+str(docId)
                    WordDocDictionary[word][docname] += 1
                    documentWordFreqDict[docname][word] += 1
                    total_N_doc+=1


    docTFIDFDict = defaultdict(float)
    for doc in documentWordFreqDict:
        for word in documentWordFreqDict[doc]:
            docTFIDFDict[word] = getTF(documentWordFreqDict[doc][word]) * getIDF(len(WordDocDictionary[word]),total_N_doc)

    toptags=getTop20results(docTFIDFDict)
    rvList=list()
    for doc in toptags:
        rvList.append(doc[0])
    return rvList

def accumulateVirtualTags(tagList):
    global GlobalTagCount
    for tag in tagList:
        if tag in GlobalTagList:
            continue
        else:
            GlobalTagList[tag]=GlobalTagCount
            GlobalTagCount+=1

def processVirtualTags(data,sampleId,virtualTagList):
    bodyText=data["body"]
    for tagword in re.findall("[a-z0-9]+", bodyText):
        if tagword and (tagword in GlobalTagList):
            tagIndex=GlobalTagList[tagword]-1
            clusterData[sampleId][tagIndex]+=1

def getTagCluteringLabels():
    LABEL_DATA_PATH=  "/mnt/stackoverflow/data/parseddata/labels.txt"
    f=open(LABEL_DATA_PATH,'r')
    rv=list()
    for line in f:
         line =line.split(",")
         for l in line:
             if len(l)>0:
                 rv.append(int(l))
    return rv;

#FILTERED_DATA_PATH_JSON = "C:\\Data\\stackoverflow\\sampleJsonTarget.json"
#FILTERED_DATA_PATH_JSON = "/mnt/stackoverflow/data/parseddata/sampleJsonTarget1000.json"
FILTERED_DATA_PATH_JSON = "/mnt/stackoverflow/data/parseddata/targetDocServer2.json"
def main():
    n_sample=0
    filteredData = open(FILTERED_DATA_PATH_JSON,'r')
    print "processing tags"
    for line in filteredData: #parsing tweets data file to generate a graph by adding edges
        data = cjson.decode(line)
        n_sample+=1
        if data["postId"] not in  GlobalPostUserDict:
            GlobalPostUserDict[data["postId"]]=data["ownerUserId"]

        GlobalParentChildDict[data["parentPostID"]][data["postId"]]["title"]=data["title"]
        GlobalParentChildDict[data["parentPostID"]][data["postId"]]["body"]=data["body"]

        accumulateOriginalTags(data["tags"])

    #calculate virtualtags
    print "processing virtual tags"
    virtualTagDict=defaultdict(lambda: list())
    for threadDoc in GlobalParentChildDict:
        virtualTagDict[threadDoc]=getVirtualTags(GlobalParentChildDict[threadDoc])
        if(len(virtualTagDict[threadDoc]) >0):
            accumulateVirtualTags(virtualTagDict[threadDoc])


    n_feature=len(GlobalTagList)

    print "sample=",
    print n_sample,
    print "  feature=",
    print n_feature

    global clusterData
    clusterData=np.zeros(shape=(n_sample,n_feature), dtype=float)

    labels=getTagCluteringLabels()
    print labels
    postIds=[]
    sampleId=0
    filteredData = open(FILTERED_DATA_PATH_JSON,'r')
    for line in filteredData: #parsing tweets data file to generate a graph by adding edges
        data = cjson.decode(line)
        processrecord(data,sampleId)
        postIds.append(data["postId"])
        if data["parentPostID"] in virtualTagDict:
            processVirtualTags(data,sampleId,virtualTagDict[data["parentPostID"]])
        sampleId+=1

    clustersize=100
    createKcluster(clusterData,clustersize,len(postIds),labels,postIds)

if __name__ == '__main__':
    main()
 

