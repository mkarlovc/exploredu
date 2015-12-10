from flask import Flask
from data import get_data
import json
import time

t1 = time.time()
client = get_data.createClientSicris()
sessionId = get_data.getSessionId(client)
'''
#get_data.getAllRsr(client, sessionId)
t2 = time.time()
print t2 - t1
#get_data.getAllRsrKeyws(client, sessionId, get_data.tblRsr,"slv")
t3 = time.time()
print t3 - t2
index = get_data.createIndexRsr(get_data.tblRsr)
get_data.getAllPrj(client, sessionId, "eng")
t4 = time.time()
print (t4 - t1)/(60*60)
get_data.getAllPrjDetails(client, sessionId, "eng", get_data.tblPrj)
t5 = time.time()
print (t5 - t1)/(60*60)
index1 = get_data.createIndexRsr(get_data.tblRsr)
index2 = get_data.createIndexPrj(get_data.tblPrj)
index3 = get_data.createIndexOrg(get_data.tblOrg)
index4 = get_data.createIndexLec(get_data.tblLec)
get_data.getAllRsrPrj(client, sessionId, "eng", get_data.tblPrj)
index5 = get_data.createIndexRsrPrj(get_data.tblRsrPrj)
index6 = get_data.createIndexPrjRsr(get_data.tblRsrPrj) 
get_data.createRsrPrjCollNet()
get_data.createRsrPrjCollNetWeighted()
index7 = get_data.createIndexRsrRsr(get_data.tblRsrPrjCollW)
'''
index1 = get_data.createIndexRsr(get_data.tblRsr)
