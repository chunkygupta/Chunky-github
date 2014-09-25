'''
@author : Chunky Gupta / Ankit Singhal  Date: 04/5/2014
@updated : Ashwini Singh Date: 04/16/2014
@updated : Ankit Singhal Date : 04/20/2014


This is to extract user details from the stack overflow data file.
'''
import sys
import os
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
import cjson


#GlobalUserDict= defaultdict(lambda: defaultdict())
#FILTERED_DATA_PATH_JSON = "C:\Users\chunkygupta\Dropbox\Project_ir\data\small_data\jsonUserDetailsFinal.json"
FILTERED_DATA_PATH_JSON = "/mnt/stackoverflow/data/parseddata/targetDocServer2.json"
USER_DETAILS_DATA_PATH = '/mnt/stackoverflow/data/users/stackoverflow.com-Users.xml'
#USER_DATA_PATH = '/mnt/stackoverflow/data/users/stackoverflow.com-Users.xml'
#FILTERED_USER_DATA_PATH = 'C:\Users\chunkygupta\Dropbox\Project_ir\data\small_data\jsonUserDetails.json'
FINAL_USER_DATA_PATH = "/mnt/stackoverflow/data/parseddata/jsonUserDetailsFinal.json"


def extractUserDetails(userTree, filteredPostsUserSet):
    userDocRoot = userTree.getroot()
    for child in userDocRoot:
        if child.attrib["Id"] in filteredPostsUserSet:
            try:
                uidText = "\"userId\" : \"" + child.attrib["Id"] + "\" ,"
                reputationText = "\"reputation\" : \"" + child.attrib["Reputation"] + "\" ,"
                displayNameText = "\"displayName\" : \"" + str(child.attrib["DisplayName"].encode('utf8'))+ "\" ,"
                locationText = "\"location\" : \"" + str(child.attrib["Location"].encode('utf8')) + "\" ," 
                websiteURLText = "\"websiteURLName\" : \"" + str(child.attrib["WebsiteUrl"].encode('utf8')) + "\" "
            except:
                uidText = "\"userId\" : \"" + child.attrib["Id"] + "\" ,"
                reputationText = "\"reputation\" : \"" + child.attrib["Reputation"] + "\" ,"
                displayNameText = "\"displayName\" : \"" + str(child.attrib["DisplayName"].encode('utf8')) + "\" ,"
                locationText = "\"location\" : \"" + "" + "\" ,"
                websiteURLText = "\"websiteURLName\" : \"" + "" + "\" " 
            jsonString = "{ " + uidText + displayNameText + reputationText + locationText + websiteURLText + " } \n"
            f = open (FINAL_USER_DATA_PATH, 'a')
            f.write(jsonString)
            f.close()

def parseFilteredPost(filteredPostData):
    filteredPostsUserSet = set()
    for singlePost in filteredPostData: #parsing filtered post to extract user id
        singlePostJson = cjson.decode(singlePost)
        userId = singlePostJson["ownerUserId"]   
        filteredPostsUserSet.add(userId)
    return filteredPostsUserSet


def main():
    filteredPostData = open(FILTERED_DATA_PATH_JSON,'r')
    userTree = ET.parse(USER_DETAILS_DATA_PATH)
    filteredPostsUserSet = parseFilteredPost(filteredPostData)
    print filteredPostsUserSet
    extractUserDetails(userTree, filteredPostsUserSet)
    
    

if __name__ == '__main__': 
    main()
