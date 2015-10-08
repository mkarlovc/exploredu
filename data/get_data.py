import suds
import xmltodict
from json import loads, dumps
from collections import OrderedDict
from tinydb import TinyDB, where
import time
import shutil
import whoosh.index as windex 
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.query import *
import urllib2
import base64
import json
import re
from itertools import islice
from random import randint
from EventRegistry.EventRegistry import *

# Set main data path
path = "/home/luis/data/mario/openedu/"

# Databases
dbSicris = TinyDB(path+'tinydb/sicris.json')
dbVideoLectures = TinyDB(path+'tinydb/videolectures.json')
dbNets = TinyDB(path+'tinydb/nets.json')
dbSicrisConn = TinyDB(path+'tinydb/conn.json')
dbCach = TinyDB(path+'tinydb/cach.json')
dbER = TinyDB(path+'tinydb/er.json')

# Tables
# --- sicris
tblRsr = dbSicris.table("rsr")
tblPrj = dbSicris.table("prj")
tblOrg = dbSicris.table("org")
# --- lec
tblLec = dbVideoLectures.table("lec")
# --- conn
tblRsrPrj = dbSicrisConn.table("rsr_prj")
# --- nets
tblRsrColl = dbNets.table("rsr_colls")
tblRsrPrjColl = dbNets.table("rsr_prj_coll_net")
tblRsrPrjCollW = dbNets.table("rsr_prj_coll_net_w")
# --- cache
tblRsrPrjGraphCache = dbCach.table("rsr_prj_graph")
# --- events
tblEvents = dbER.table("events")

# from sorted dict to dict
def to_dict(input_ordered_dict):
    return loads(dumps(input_ordered_dict))

##################
# Data connections
##################

# create client for sicris
def createClientSicris():
    url = "http://webservice.izum.si/ws-cris/CrisService.asmx?WSDL"
    return suds.client.Client(url)

# create client for videolectures
def createClientVideoLectures(username, password):
    url = "http://videolectures.net/site/stats/lectures.json"
    request = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)   
    return request

def getSessionId(client, username, password):
    return client.service.GetSessionID("si", username, password)
   
def getAllRsr(client, path, sessionId):
    shutil.copyfile(path+'tinydb/sicris.json', path+'tinydb/sicris.json.backup')
    methodCall = "Sicris_app_UI.Researcher.SearchSimple.eng.public.utf-8.mstid.%.1.-1"
    tblRsr.purge()
    result = client.service.Retrieve("si", "RSR", methodCall, "", sessionId)
    res = result.Records
    obj = xmltodict.parse(res)
    for rsr in obj['CRIS_RECORDS']['RSR']:
        tblRsr.insert(to_dict(rsr))

###################
# Data collection
###################

def getAllRsrKeyws(client, path, sessionId, lang, rsrs):
    shutil.copyfile(path+'tinydb/sicris.json', path+'tinydb/sicris.json.backup')
    methodCall = "Sicris_app_UI.Researcher.GetKeywords."+lang+"."
    for rsr in rsrs.all():
        result = client.service.Retrieve("SI", "RSR", methodCall+rsr["@id"], "", sessionId)
        res = result.Records
        obj = {}

        try:
            obj = xmltodict.parse(res)
            obj = to_dict(obj)
        except:
            pass
        
        if obj.has_key('CRIS_RECORDS'):
            rec = obj['CRIS_RECORDS']
            if rec != None:
                # get od record
                old = tblRsr.get(where('@id') == rsr["@id"])
                # update it
                old['keyws_'+lang[0:2]] = rec['RSR']
                # overwrite it
                tblRsr.update(old, where('@id') == rsr["@id"])

def getAllRsrClass(client, sessionId, lang, rsrs):
    methodCall = "Sicris_app_UI.Researcher.GetMSTClassification."+lang+"."
    for rsr in rsrs.all():
        results = client.service.Retrieve("SI", "RSR", methodCall+rsr["@id"], "", sessionId)
        res = result.Records
        obj = {}

        try:
            obj = xmltodict.parse(res)
            obj = to_dict(obj)
        except:
            pass

        if obj.has_key('CRIS_RECORDS'):
            rec = obj['CRIS_RECORDS']
            if rec != None:
                # get od record
                old = tblRsr.get(where('@id') == rsr["@id"])
                # update it
                old['class_'+lang[0:2]] = rec['RSR']
                # overwrite it
                tblRsr.update(old, where('@id') == rsr["@id"])

def getAllRsrPrj(client, path, sessionId, lang, prjs):
    methodCall = "Sicris_app_UI.Project.GetResearchers."+lang+"."
    shutil.copyfile(path+'tinydb/sicris.json', path+'tinydb/sicris.json.backup')
    tblRsrPrj.purge()
    totallen = len(prjs.all())
    print totallen
    for i,prj in enumerate(prjs.all()):
        prjid = prj["@id"]
        results = client.service.Retrieve("SI", "RSR", methodCall+prj["@id"]+".RSR", "mstid", sessionId)
        res = results.Records
        obj = {}

        try:
            obj = xmltodict.parse(res)
            obj = to_dict(obj)
        except:
            pass

        if obj.has_key('CRIS_RECORDS'):
            rec = obj['CRIS_RECORDS']
            if rec != None:
                # get od record
                rsrs = rec['RSR']
                for rsr in rsrs:
                    #if isinstance(rsr, dict):
                    tblRsrPrj.insert({'prjid': prjid, 'rsrmstid': rsr['@mstid'] })
        print i, totallen

def getAllPrjRsr(client, path, sessionId, lang, rsrs):
    methodCall = "Sicris_app_UI.Researcher.GetProjects.PRJ."+lang+"."
    shutil.copyfile(path+'tinydb/sicris.json', path+'tinydb/sicris.json.backup')
    tblRsrPrj.purge()
    totallen = len(rsrs.all())
    print totallen
    for i,rsr in enumerate(rsrs.all()):
        rsrid = rsr["@id"]
        call = methodCall+rsr["@id"]
        print call
        results = client.service.Retrieve("SI", "PRJ", call,"", sessionId)
        res = results.Records
        obj = {}

        try:
            obj = xmltodict.parse(res)
            obj = to_dict(obj)
        except:
            pass

        if obj.has_key('CRIS_RECORDS'):
            rec = obj['CRIS_RECORDS']
            if rec != None:
                # get od record
                prjs = rec['PRJ']
                for prj in prjs:
                    if isinstance(prj, dict):
                        if (prj.has_key('@mstid')):
                            print {'prjmstid': prj['@mstid'], 'rsrid': rsrid, 'prjid:':prj['@id']}
                            tblRsrPrj.insert({'prjmstid': prj['@mstid'], 'prjid:':prj['@id'], 'rsrid': rsrid })
        print i, totallen

# Get all sicris projects
def getAllPrj(client, path, sessionId, lang):
    shutil.copyfile(path+'tinydb/sicris.json', path+'tinydb/sicris.json.backup')
    #tblPrj.purge()
    methodCall = "Sicris_app_UI.Project.SearchSimple.PRJ."+lang+".public.utf-8.mstid.%.1.-1"
    results = client.service.Retrieve("SI", "PRJ", methodCall, "", sessionId)
    res = results.Records
    obj = {}

    try:
        obj = xmltodict.parse(res)
        obj = to_dict(obj)
    except:
        pass

    for i,prj in enumerate(obj['CRIS_RECORDS']['PRJ']):
        print i,len(obj['CRIS_RECORDS']['PRJ'])
        tblPrj.insert(to_dict(prj))

# Gett project abstract and keywords
def getAllPrjDetails(client, path, sessionId, lang, prjs):
    shutil.copyfile(path+'tinydb/sicris.json', path+'tinydb/sicris.json.backup')
    methodCallKeyws = "Sicris_app_UI.Project.GetKeywords."+lang+"."
    methodCallAbst = "Sicris_app_UI.Project.GetAbstract."+lang+"."
    methodCallSign = "Sicris_app_UI.Project.GetSignificance."+lang+"."

    for i,prj in enumerate(prjs.all()):

        # Keywords
        results = client.service.Retrieve("SI", "PRJ", methodCallKeyws+prj["@id"], "", sessionId)
        res = results.Records
        obj = {}

        try:
            obj = xmltodict.parse(res)
            obj = to_dict(obj)
        except:
            pass
       
        keyws = {}
        if obj.has_key('CRIS_RECORDS'):
            rec = obj['CRIS_RECORDS']
            if rec != None:
                if rec['PRJ']['@keyws']:
                    keyws = rec['PRJ']['@keyws']
        
        # Abstract
        results = client.service.Retrieve("SI", "PRJ", methodCallAbst+prj["@id"], "", sessionId)
        res = results.Records
        obj = {}

        try:
            obj = xmltodict.parse(res)
            obj = to_dict(obj)
        except:
            pass

        abst = {}
        if obj.has_key('CRIS_RECORDS'):
            rec = obj['CRIS_RECORDS']
            if rec != None:
                # get od record
                if rec['PRJ'].has_key('@abstr'):
                    abst = rec['PRJ']['@abstr']
         
        # Significance
        results = client.service.Retrieve("SI", "PRJ", methodCallSign+prj["@id"], "", sessionId)
        res = results.Records
        obj = {}

        try:
            obj = xmltodict.parse(res)
            obj = to_dict(obj)
        except:
            pass
        
        sign_dom = {}
        sign_world = {}
        if obj.has_key('CRIS_RECORDS'):
            rec = obj['CRIS_RECORDS']
            if rec != None:
                if rec['PRJ'].has_key('@domestic'):
                    sign_dom = rec['PRJ']['@domestic']
                if rec['PRJ'].has_key('@world'):
                    sign_world = rec['PRJ']['@world']

        # get od record
        old = tblPrj.get(where('@id') == prj["@id"])

        # update it
        if (bool(keyws)):
            old['keyws_'+lang[0:2]] = keyws
        if (bool(abst)):
            old['abstr_'+lang[0:2]] = abst
        if (bool(sign_dom)):
            old['sign_dom_'+lang[0:2]] = sign_dom
        if (bool(sign_world)):
            old['sign_world_'+lang[0:2]] = sign_world
      
        # overwrite it
        if bool(keyws) or bool(abst) or bool(sign_dom) or bool(sign_world):
            tblPrj.update(old, where('@id') == prj["@id"])
        
        print i

# Get all organization using IZUM webcris service and store it into tblOrg table of sicris tinydb database
def getAllOrg(client, path, sessionId, lang):
    shutil.copyfile(path+'tinydb/sicris.json', path+'tinydb/sicris.json.backup')
    methodCall = "Sicris_app_UI.Organization.SearchSimple.@"+lang+".public.utf-8.mstid.%.1.-1"
    results = client.service.Retrieve("SI", "ORG", methodCall, "", sessionId)
    res = results.Records
    obj = {}

    try:
        obj = xmltodict.parse(res)
        obj = to_dict(obj)
    except:
        pass

    for i,org in enumerate(obj['CRIS_RECORDS']['ORG']):
        print i,len(obj['CRIS_RECORDS']['ORG'])
        tblOrg.insert(to_dict(org))

# Get details of organizatipon using IZUM webcris service. Use the existing list of organizations from tblOrg table
# of sicris tinydb database
def getAllOrgDetails(client, path, sessionId, lang, orgs):
    shutil.copyfile(path+'tinydb/sicris.json', path+'tinydb/sicris.json.backup')
    methodCallStatus = "Sicris_app_UI.Organization.GetHeader."+lang+"."
    methodCallClass = "Sicris_app_UI.Organization.GetMSTClassification."+lang+"."

    for i,org in enumerate(orgs.all()):

        # Status
        results = client.service.Retrieve("SI", "ORG", methodCallStatus+org["@id"], "", sessionId)
        res = results.Records
        obj = {}

        try:
            obj = xmltodict.parse(res)
            obj = to_dict(obj)
        except:
            pass

        stat = {}
        if obj.has_key('CRIS_RECORDS'):
            rec = obj['CRIS_RECORDS']
            if rec != None:
               stat = rec['ORG']
        
        # Classification
        results = client.service.Retrieve("SI", "ORG", methodCallClass+org["@id"], "", sessionId)
        res = results.Records
        obj = {}

        try:
            obj = xmltodict.parse(res)
            obj = to_dict(obj)
        except:
            pass
        
        classi = {}
        if obj.has_key('CRIS_RECORDS'):
            rec = obj['CRIS_RECORDS']
            if rec != None:
               classi = rec['ORG']

        # get od record
        old = tblOrg.get(where('@id') == org["@id"])
        
        # update
        if stat.has_key('@org_name'):
            old['name'] = stat['@org_name']
        if stat.has_key('@statfrm'):
            old['statfrm'] = stat['@statfrm']
        if stat.has_key('@status'):
            old['status'] = stat['@status']
        if stat.has_key('@regnum'):
            old['regnum'] = stat['@regnum'] 
        if bool(classi):
            old['classification'] = classi
        # overwrite
        tblOrg.update(old, where('@id') == org["@id"])
        print i

# get all videolecturs
def getAllVideoLectures(client, path):
    shutil.copyfile(path+'tinydb/videolectures.json', path+'tinydb/videolectures.json.backup')
    result = urllib2.urlopen(client)
    lectures = json.loads(result.read())
    length = len(lectures)
    for i,l in enumerate(lectures):
        tblLec.insert(lectures[l])
        if i%10000 == 0:
            print i

# get event registry events with concept Education
def getAllEREducationEvents(path):
    er = EventRegistry(host = "http://eventregistry.org", logging = True)
    q = QueryEvents()
    q.addConcept(er.getConceptUri("Education"))
    q.addRequestedResult(RequestEventsUriList())
    res = er.execQuery(q)
    obj = createStructFromDict(res)
    uris = obj.uriList

    l = len(uris)
    inserts = []
    tblEvents.purge()
    for i,uri in enumerate(uris):
        try:
            q = QueryEvent(uri)
            q.addRequestedResult(RequestEventInfo(["eng"]))   # get event information. concept labels should be in three langauges
            q.addRequestedResult(RequestEventArticles(0, 10))   # get 10 articles describing the event
            q.addRequestedResult(RequestEventKeywordAggr())     # get top keywords describing the event
            eventRes = er.execQuery(q)
            out = {}
            out['info'] =  eventRes[uri][u'info'][u'multiLingInfo']
            out['date'] =  eventRes[uri][u'info'][u'eventDate']
            out['uri'] = uri
            tblEvents.insert(out)
            print i,l
        except:
            pass

####################
# Indexing
####################

# create index of searchable researchers using whoosh index
def createIndexRsr(path, tblRsr):
    schema = Schema(fname=TEXT(stored=True), lname=TEXT(stored=True), id=TEXT(stored=True), mstid=TEXT(stored=True),\
science=TEXT(stored=True), scienceCode=TEXT(stored=True), field=TEXT(stored=True), subfield=TEXT(stored=True), content=TEXT)
    index = create_in(path+"whooshindex/rsr", schema)

    writer = index.writer()
    for rsr in tblRsr.all():
        content = ""
        s = u""
        s_code = u""
        f = u""
        sub = u""
        if rsr.has_key('science'):
            s = rsr['science']['#text']
            s_code = rsr['science']['@code']
            content += " "+rsr['science']['#text']
        if rsr.has_key('field'):
            f = rsr['field']['#text']
            content += " "+rsr['field']['#text']
        if rsr.has_key('subfield'):
            sub = rsr['subfield']['#text']
            content += " "+rsr['subfield']['#text']
        if rsr.has_key('keyws_en'):
            content += " "+rsr['keyws_en']['@keyws']
        if rsr.has_key('keyws_sl'):
            content += " "+rsr['keyws_sl']['@keyws']

        if content != "":
            print rsr["@id"]+": "+content
            writer.add_document(lname=rsr['fname'], fname=rsr['lname'], id=rsr['@id'], mstid=rsr['@mstid'],\
science=s, scienceCode=s_code, field=f, subfield=sub, content=content) 
    
    writer.commit()
    return index

# create index of searchabe projects using whoosh. Index is called prj
def createIndexPrj(path, tblPrj):
    schema = Schema(name=TEXT(stored=True), startdate=TEXT(stored=True), enddate=TEXT(stored=True), mstid=TEXT(stored=True), content=TEXT)
    index = create_in(path+"whooshindex/prj", schema)
    
    writer = index.writer()
    for prj in tblPrj.all():
        content = ""
        if prj.has_key('name'):
            content += " "+prj['name']
        if prj.has_key('keyws_en'):
            content += " "+prj['keyws_en']
        if prj.has_key('abstr_en'):
            content += " "+prj['abstr_en']
        if prj.has_key('sign_dom_en'):
            content += " "+prj['sign_dom_en']
        if prj.has_key('sign_world_en'):
            content += " "+prj['sign_world_en']

        if content != "" and prj.has_key('name'):
            print prj["@id"]+": "+content
            writer.add_document(name=prj['name'], startdate=prj['@startdate'], enddate=prj['@enddate'], mstid=prj['@mstid'], content=content)
 
    writer.commit()
    return index

# create index of searchable organizations using whoosh stored as org
def createIndexOrg(path, tblOrg):
    schema = Schema(name=TEXT(stored=True), city=TEXT(stored=True), science=TEXT(stored=True), mstid=TEXT(stored=True), content=TEXT)
    index = create_in(path+"whooshindex/org", schema)

    writer = index.writer()
    for org in tblOrg.all():
        content = u""
        science = u""
        name = u""
        if org.has_key('name'):
            name = org['name']
            content += " "+org['name']
        if org.has_key('classification'):
            if bool(type(org['classification']) is list):
                for c in org['classification']:
                    if c.has_key('@sci_descr'):
                        content += " "+c['@sci_descr']
                        if c['@weight'] == u'1':
                            science = c['@sci_descr']
        if org.has_key('city'):
            city = org['city']

        if content != "" and org.has_key('name'):
            print org["@id"]+": "+content
            writer.add_document(name=name, city=city, science=science, content=content)

    writer.commit()
    return index

# create index of searchable videolectures using whoosh
def createIndexLec(path, tblLec):
    schema = Schema(title=TEXT(stored=True), url=TEXT(stored=True), desc=TEXT(stored=True), recorded=TEXT(stored=True), content=TEXT)
    index = create_in(path+"whooshindex/lec", schema)

    writer = index.writer()
    content = u""
    for i,lec in enumerate(tblLec.all()):
        title = u""
        type = u""
        lang = u""
        url = u""
        desc = u""
        recorded = u""
        content = u""
        if lec.has_key('title'):
            title = lec['title']
            content += " "+lec['title']
        if lec.has_key('url'):
            url = lec['url']
        if lec.has_key('recorded'):
            recorded = lec['recorded']
            content += " "+lec['recorded']
        if lec.has_key('text'):
            if lec['text'].has_key('desc'):
                desc = lec['text']['desc']
                content += " "+lec['text']['desc']
            if lec['text'].has_key('title'):
                title = lec['text']['title']
                content += " "+lec['text']['title']

        if content != "":
            print lec["url"]+": "+str(i)
            writer.add_document(title=title, type=type, url=url, lang=lang, desc=desc, recorded=recorded, content=content)

    writer.commit()
    return index

# Create index for quick searching of ceonnection between researchers and projects
def createIndexRsrPrj(path, tblRsrPrj):
    schema = Schema(prjmstid=TEXT(stored=True), prjid=TEXT(stored=True), rsrid=TEXT(stored=True), content=TEXT)
    index = create_in(path+"whooshindex/rsrprj", schema)
    writer = index.writer()
    for i,rsrprj in enumerate(tblRsrPrj.all()):
        rsrid = rsrprj['rsrid']
        prjid = rsrprj['prjid:']
        prjmstid = rsrprj['prjmstid']
        writer.add_document(prjmstid=prjmstid, prjid=prjid, rsrid=rsrid, content=rsrid)
    writer.commit()
    return index

# Create index for quick searching of ceonnection between researchers and projects
def createIndexPrjRsr(tblRsrPrj):
    schema = Schema(prjmstid=TEXT(stored=True), prjid=TEXT(stored=True), rsrid=TEXT(stored=True), content=TEXT)
    index = create_in(path+"whooshindex/prjrsr", schema)
    writer = index.writer()
    for i,rsrprj in enumerate(tblRsrPrj.all()):
        rsrid = rsrprj['rsrid']
        prjid = rsrprj['prjid:']
        prjmstid = rsrprj['prjmstid']
        writer.add_document(prjmstid=prjmstid, prjid=prjid, rsrid=rsrid, content=prjid)
    writer.commit()
    return index

def createIndexRsrRsr(tblRsrPrjCollW):
    schema = Schema(rsrid1=TEXT(stored=True), rsrid2=TEXT(stored=True), content=TEXT)
    index = create_in(path+"whooshindex/rsrrsr", schema)
    writer = index.writer()
    for i,edge in enumerate(tblRsrPrjCollW.all()):
        rsrid1 = edge['rsrid1']
        rsrid2 = edge['rsrid2']
        writer.add_document(rsrid1=rsrid1, rsrid2=rsrid2, content=rsrid1+"-"+rsrid2)
    writer.commit()
    return index

# Create connections between researchers and save them into tblRsrPrjColl table of dbNets tinydb database
def createRsrPrjCollNet():
    tblRsrPrjColl.purge()
    tblRsrColl.purge()
    index = loadIndexRsrPrj()
    index1 = loadIndexPrjRsr()
    inserts = []
    inserts1 = []
    for i,rsr in enumerate(tblRsr.all()):
        vals = {}
        rsrid1 = rsr['@id']
        results = searchIndex(index, rsrid1)
        for r in results:
            prjid = r['prjid']
            res = searchIndex(index1, prjid)
            for r1 in res:
                rsrid2 = r1['rsrid']
                if not vals.has_key(rsrid2):
                    vals[rsrid2] = 1
                else:
                    vals[rsrid2] += 1
                inserts.append({'rsrid1': rsrid1, 'rsrid2': rsrid2, 'prjmstid': r['prjmstid'], 'prjid': prjid})
        inserts1.append({'rsrid': rsrid1, 'prjcoll': vals})

    print "insert multiple"
    tblRsrPrjColl.insert_multiple(inserts)
    print "insert multiple 1"
    tblRsrColl.insert_multiple(inserts1)

# Create an undirected one way network of researchers based on project collaboration
# the network is weighted
# saved in tblRrsPrjCollW table of dbNets tinydb 
def createRsrPrjCollNetWeighted():
    pairs = {}
    inserts = []
    print 'counting'
    for i,edge in enumerate(tblRsrPrjColl.all()):
        id1 = edge['rsrid1']
        id2 = edge['rsrid2']
        key = id1+","+id2
        
        if not pairs.has_key(key):
            pairs[key] = 1
        else:
            pairs[key] += 1
    print 'creating inserts'
    for i,key in enumerate(pairs):
        arr = key.split(',')
        id1 = arr[0]
        id2 = arr[1]
        weight = pairs[key]
        inserts.append({'rsrid1': id1, 'rsrid2': id2, 'weight': weight})
    print 'insert multiple'
    tblRsrPrjCollW.insert_multiple(inserts)

########################
# Loading and searching
########################
 
def loadIndexRsr(path):
    return windex.open_dir(path+"whooshindex/rsr")

def loadIndexPrj(path):
    return windex.open_dir(path+"whooshindex/prj")

def loadIndexOrg(path):
    return windex.open_dir(path+"whooshindex/org")

def loadIndexLec(path):
    return windex.open_dir(path+"whooshindex/lec")

def loadIndexRsrPrj(path):
    return windex.open_dir(path+"whooshindex/rsrprj")

def loadIndexPrjRsr(path):
    return windex.open_dir(path+"whooshindex/prjrsr")

def loadIndexRsrRsr(path):
    return windex.open_dir(path+"whooshindex/rsrrsr")

def searchIndex(index, text):
    out = []
    with index.searcher() as searcher:
        parser = QueryParser("content", index.schema)
        myquery = parser.parse(text)
        results = searcher.search(myquery, limit=None)
        for res in results:
            out.append(dict(res))
    return out

# Get value from arbitrary cache table for arbitrary query
def getCache(tbl, text):
    return tbl.search(where('query') == text)

#########################
# Special constructs
########################

# Create graph based on subset of researchers
def graphRsrPrj(path, rsrs):
    index = loadIndexRsrRsr(path)
    ids = []
    nodes = []
    for i,rsr in enumerate(rsrs):
        rsrid = rsr['id']
        ids.append(rsrid)

    edges = []
    print 'length',len(ids)

    l = len(ids)
    degree = {}
    for i in range(0,l-2):
        for j in range(i+1,l-1):
            id1 = ids[i]
            id2 = ids[j]
            res =searchIndex(index,id1+"-"+id2)
            if len(res) > 0:

                # node degres
                if not degree.has_key(id1):
                    degree[id1] = 1
                else:
                    degree[id1] += 1
                if not degree.has_key(id2):
                    degree[id2] = 1
                else:
                    degree[id2] += 1

                # edges
                edges.append({'rsrid1':id1, 'rsrid2': id2})

    for i,rsr in enumerate(rsrs):
        rsrid = rsr['id']
        size = 1
        if degree.has_key(rsrid):
            size = degree[rsrid]

        nodes.append({'id': rsrid, 'name':  rsr['fname']+" "+rsr['lname'],\
'x':randint(0,100), 'y':randint(0,100), 'science': rsr['science'], 'color': rsr['scienceCode'], 'degree':size})

    return {'nodes': nodes, 'edges': edges}

def getPrjHistogram(prjs):
    hist = {}
    for i,prj in enumerate(prjs):
        if prj.has_key('startdate'):
            startdate = prj['startdate']
            year = startdate.split('.')[2]
            if not hist.has_key(year):
                hist[year] = 1
            else:
                hist[year] += 1
    min = 99999
    max = -1 
    for key in hist:
        if int(key) < min:
           min = int(key)
        if int(key) > max:
           max = int(key)
    
    for y in range(min,max):
        if not hist.has_key(str(y)):
            hist[str(y)] = 0

    return hist
