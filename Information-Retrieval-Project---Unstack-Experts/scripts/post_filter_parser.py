'''
@author : Chunky Gupta  Date: 03/25/2014
@updated : Chunky gupta Date: 04/10/2014
@updated : Ankit singhal/ Ashwini Singh 04/17/2014 (some modification in the filter rules)

This is used to extract post from stack overflow data. This provides the filtered post used for final clustering.

'''
import sys
import os
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from nltk.corpus import stopwords
import datetime



PARENT_ID="ParentId"
NUMBER_OF_DAYS_USER_IS_OLD = 120 # In number of days
GlobalQuesDict= defaultdict(lambda: defaultdict())
GlobalUserDict= defaultdict(lambda: defaultdict())
GlobalUserCountDict = defaultdict(lambda: 0)
stopWords = set(stopwords.words('english'))
CURRENT_DATE = datetime.date.today()
POSTS_PATH = "/mnt/stackoverflow/data/posts/Splited_Files/temp"
TAGS_SET = set(line.strip() for line in open('/mnt/stackoverflow/data/Top_500_Tags_List.txt'))
GlobalRowDoc= defaultdict()    


def filterBody(oldBody):
    newBody = ' '.join([word for word in oldBody.split() if word not in (stopWords)])
    #filteredBody = re.sub(r'[\W_]+',' ', newBody)
    filteredBody = re.sub (r'[&;@$%{}^*<_>()\\=`"/]+',' ', newBody )
    return filteredBody

def filterTitle(oldTitle):
    newTitle = ' '.join([word for word in oldTitle.split() if word not in (stopWords)])
    #filteredTitle = re.sub(r'[\W_]+',' ', newTitle)
    filteredTitle = re.sub (r'[&;@$%{}^*<_>()\\=`"/]+',' ', newTitle )
    return filteredTitle

def filterFunctionRules(xmlDoc):
    reputedUser = 0
    frequentTag = 1
    udRatio = 0
    userViews = 0
    parentId = xmlDoc.attrib[PARENT_ID]
    if parentId in GlobalQuesDict:
        try:
	    tagsSplit = re.sub(r'[><]',' ', GlobalQuesDict[parentId]["Tags"]).split()
	    for tag in tagsSplit:
		if tag not in TAGS_SET:
			frequentTag = 0
            userID = xmlDoc.attrib["OwnerUserId"]
	    GlobalUserCountDict[userID] += 1
	    if (GlobalUserCountDict[userID] > 1000):
		return 0
            userCreationDateString = GlobalUserDict[userID]["CreationDate"]
            userCreationDate = datetime.datetime.strptime(userCreationDateString, '%Y-%m-%d').date()
            daysDifference = (CURRENT_DATE - userCreationDate).days
            if ( daysDifference > NUMBER_OF_DAYS_USER_IS_OLD):
                if (GlobalUserDict[userID]["Rep"] > 30000):
                    reputedUser = 1 
            else:
                if (GlobalUserDict[userID]["Rep"] > 10000):
                    reputedUser = 1
            if (GlobalUserDict[userID]["Views"] > 10000):
    		userViews = 1
            if (GlobalUserDict[userID]["UDRatio"] > 5000):
                udRatio = 1
        except:
            reputedUser = 0
            udRatio = 0
	    frequentTag = 0
	    userViews = 0
    return ((reputedUser or udRatio) and frequentTag and userViews)
        
        
def processChild(xmlDoc):
    parentId=xmlDoc.attrib[PARENT_ID]
    filterBooleanValue = filterFunctionRules(xmlDoc)
    if filterBooleanValue:
	try:
	    ownerUserId = "\"ownerUserId\" : \"" + xmlDoc.attrib["OwnerUserId"] + "\" ,"
	except:
	    ownerUserId = "\"ownerUserId\" : \"" + "0" + "\" ,"
        newBody = filterBody((xmlDoc.attrib["Body"].encode('utf8')).lower())
	newTitle = filterTitle(GlobalQuesDict[parentId]["Title"])
        idText =  "\"postId\" : \"" + parentId + "\" ,"
        parendID = "\"parentPostID\" : \"" + parentId + "\" ,"
        tagText = "\"tags\" : \"" + GlobalQuesDict[parentId]["Tags"] + "\" ," 
        titleText = "\"title\" : \"" + newTitle + "\" ," 
        bodyText = "\"body\" : \"" + newBody + "\" " 
        jsonString = "{ " + idText + ownerUserId + parendID + tagText  + titleText + bodyText + " } \n"
        f = open ('/mnt/stackoverflow/data/output/targetDocServer.txt', 'a')
        f.write(jsonString)
        f.close()
        
def processUserFile(userTree):
    userDocRoot = userTree.getroot()
    print "Inside User Processing Dictionary"
    for child in userDocRoot:
        if ET.iselement(child):
            GlobalUserDict[child.attrib["Id"]]["Rep"] = int(child.attrib["Reputation"])
            GlobalUserDict[child.attrib["Id"]]["Views"] = int(child.attrib["Views"])
            GlobalUserDict[child.attrib["Id"]]["CreationDate"] = child.attrib["CreationDate"][0:10]
            if (float(child.attrib["DownVotes"]) == 0):
                GlobalUserDict[child.attrib["Id"]]["UDRatio"] = int(child.attrib["UpVotes"])
            else:
                GlobalUserDict[child.attrib["Id"]]["UDRatio"] = int(float(child.attrib["UpVotes"]) / float(child.attrib["DownVotes"]) )
    
def populatePostDictionary(fileName, root):
    postTree = ET.parse(os.path.join(root,fileName))
    postDocRoot= postTree.getroot()
    print fileName
    for child in postDocRoot:
        if ET.iselement(child):
            if PARENT_ID not in child.attrib:
		try:
                    GlobalQuesDict[child.attrib["Id"]]["Tags"] = child.attrib["Tags"].encode('utf8')
                    GlobalQuesDict[child.attrib["Id"]]["Title"] = child.attrib["Title"].encode('utf8')
		except:
		    GlobalQuesDict[child.attrib["Id"]]["Tags"] = "None"
		    GlobalQuesDict[child.attrib["Id"]]["Title"] = "None"
            
def main():
    print "Before Post Parse ETree"
    for root, dirs, files in os.walk(POSTS_PATH):
        for one_file in files:
	    populatePostDictionary(one_file, root)
            
    print "Before User Parse ETree"
    userTree = ET.parse('/mnt/stackoverflow/data/users/stackoverflow.com-Users.xml')
    print "Before User Processing Dictionary"
   
    processUserFile(userTree)

    f2 = open ('/mnt/stackoverflow/data/output/targetDocUserDataDone.txt', 'a')
    f2.write("UserDataDictionaryDone")
    f2.close()

    #done all processing of parents
    for root, dirs, files in os.walk(POSTS_PATH):
        for one_file in files:
            postTree = ET.parse(os.path.join(root,one_file))
            postDocRoot= postTree.getroot()
            for child in postDocRoot:
                if ET.iselement(child):
                    if PARENT_ID in child.attrib:
                        processChild(child)

if __name__ == '__main__': 
    main()
