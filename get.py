from flask import Flask
from data import get_data
import json
import time
import pprint

path = "/home/luis/data/mario/openedu/"

# Start session
t1 = time.time()
print "Start session... " + str(t1)

# Loading credentials
print "Loading credentials"
pwd = {}
with open('pwd.json') as data_file:    
    pwd = json.load(data_file)
    #pprint pwd

print 'pass',pwd['sicris']['pass']

# Creating sicris client
print "Creating sicris client..."
client = get_data.createClientSicris()
sessionId = get_data.getSessionId(client, pwd['sicris']['user'], pwd['sicris']['pass'])
'''
# Get all researchers and store them in Tinydb
t2 = time.time()
print "Get all researchers and store them in Tinydb... "+str((t2-t1)/3600)
get_data.getAllRsr(client, path, sessionId)
 
# Get all resercher keywords
t3 = time.time()
print "Get all resercher keywords... "+str((t3-t1)/3600)
get_data.getAllRsrKeyws(client, path, sessionId, get_data.tblRsr,"eng")
# Create index rsr
t4 = time.time()
print "Create index rsr... "+str((t4-t1)/3600)
index = get_data.createIndexRsr(path, get_data.tblRsr)
# Get al projects
t5 = time.time()
print "Get all projects... "+str((t5-t1)/3600)
get_data.getAllPrj(client, path, sessionId, "eng")
'''
index = get_data.createIndexPrj(path, get_data.tblPrj)
'''
get_data.getAllPrjDetails(client, path, sessionId, "eng", get_data.tblPrj)
t5 = time.time()
print (t5 - t1)/(60*60)
get_data.getAllOrgDetails(client, path, sessionId, "eng", get_data.tblOrg)
t6 = time.time()
print (t6 - t1)/(60*60)
client_vl = get_data.createClientVideoLectures(pwd['videolectures'].user, pwd['videolectures'].pass)
get_data.getAllVideoLectures(client_vl)
t7 = time.time()
print (t7 - t1)/(60*60)
#get_data.getAllRsrPrj(client, sessionId, "eng", get_data.tblPrj)
print len(get_data.tblRsr.all())
print len(get_data.tblLec.all())
print len(get_data.tblRsrPrj.all())
get_data.getAllPrjRsr(client, sessionId, "eng", get_data.tblRsr)
t8 = time.time()
print (t8 - t1)/(60*60)
print len(get_data.tblRsr.all())
print len(get_data.tblLec.all())
print len(get_data.tblRsrPrj.all())
get_data.getAllEREducationEvents(path)
get_data.getAllSIO()
index = get_data.createIndexRsrKeyws(path, get_data.tblRsr)
t8 = time.time()
print (t8 - t1)/(60*60)
get_data.getAllSioFile()
get_data.createIndexSio(path, get_data.tblEduMaterials)
print 'done'
'''
