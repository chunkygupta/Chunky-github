'''
@author : Ashwini Singh  Date: 04/10/2014
@updated : Ankit Sighal Date: 04/20/2014

This is create clusters using only the stackoverflow tags . Not using virtual tags for this clustering.
'''
import os
from collections import defaultdict
import cjson
import re
from time import time
import numpy as np

from sklearn.decomposition import PCA
from sklearn.preprocessing import scale
import pylab as pl
from sklearn import metrics
from sklearn.cluster import KMeans
from scipy import sparse

GlobalTagList=defaultdict(int)
GlobalPostUserDict=defaultdict(int)
GlobalTagCount=0
clusterData=np.zeros(shape=(10,10), dtype=float) #dummy

def bench_k_means(estimator, name, data, sample_size, labels):
    t0 = time()
    data=sparse.csr_matrix(data)    
    val=estimator.fit(data)
    LABEL_DATA_PATH=  "/mnt/stackoverflow/data/parseddata/labels.txt"
    f_gt = open(LABEL_DATA_PATH,'w')
    text=""
    for label in estimator.labels_:
        text+=str(label)+","
    f_gt.write(text)
    
def createKcluster(clusterData,clustersize,samplesize,labels):
    data = clusterData
    n_samples, n_features = data.shape
    n_digits = clustersize 
    print("n_digits: %d, \t n_samples %d, \t n_features %d"  % (n_digits, n_samples, n_features))
    
    
    print(79 * '_')
    print('% 9s' % 'init'
          '    time  inertia    homo   compl  v-meas     ARI AMI  silhouette')
    bench_k_means(KMeans(init='k-means++', n_clusters=n_digits, n_init=10),name="k-means++", data=data, sample_size=samplesize, labels=labels)


def accumulateTags(tagText):
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
    
#FILTERED_DATA_PATH_JSON = "C:\\Data\\stackoverflow\\sampleJsonTarget.json"
FILTERED_DATA_PATH_JSON = "/mnt/stackoverflow/data/parseddata/targetDocServer2.json"

def processrecord(data,sampleId):
    global clusterData
    tagText=data["tags"]
    if len(tagText) !=0:
        tagList=re.sub(r'[><]',' ', tagText).split()
        for tag in tagList:
            tagIndex=GlobalTagList[tag]
            clusterData[sampleId][tagIndex]+=1
    
    
def main():
    n_sample=0
    filteredData = open(FILTERED_DATA_PATH_JSON,'r')
    for line in filteredData: #parsing tweets data file to generate a graph by adding edges
        data = cjson.decode(line)
        n_sample+=1
        if data["postId"] not in  GlobalPostUserDict:
            GlobalPostUserDict[data["postId"]]=data["ownerUserId"]
        accumulateTags(data["tags"])
    
    n_feature=len(GlobalTagList)
    
    global clusterData
    clusterData=np.zeros(shape=(n_sample,n_feature), dtype=float)  
        
    labels=[]  
    sampleId=0
    filteredData = open(FILTERED_DATA_PATH_JSON,'r')
    for line in filteredData: #parsing tweets data file to generate a graph by adding edges
        data = cjson.decode(line)
        labels.append(data["postId"])
        processrecord(data,sampleId)
        sampleId+=1
        
    clustersize=100
    createKcluster(clusterData,clustersize,len(labels),labels)    
         
if __name__ == '__main__': 
    main()
