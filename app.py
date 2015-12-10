from flask import Flask, render_template
from data import get_data
import json

app = Flask(__name__, static_url_path='')
path = "/home/luis/data/mario/openedu/"

##############
# Interface
##############

@app.route('/')
def search():
    #return render_template('search.html')
    return app.send_static_file('index.html')

@app.route('/api')
def api():
    #return render_template('search.html')
    return app.send_static_file('api.html')

@app.route('/search')
def test():
    return app.send_static_file('search.html')

@app.route('/graph')
def graph():
    return render_template('graph.html')

#############
# API
#############

@app.route('/api/all/<text>', methods=['GET'])
def search_all(text):    
    # researchers
    indexrsr = get_data.loadIndexRsr(path)
    rsr = get_data.searchIndex(indexrsr, text)

    # projects
    indexprj = get_data.loadIndexPrj(path)
    prj = get_data.searchIndex(indexprj, text)

    # lectures
    indexlec = get_data.loadIndexLec(path)
    lec = get_data.searchIndex(indexlec, text)
    
    # researchers projects collaboration graph
    graph = []
    cache = get_data.getCache(get_data.tblRsrPrjGraphCache, text)
    if len(cache) > 0:
        graph = cache[0]['res']
    else:
        index = get_data.loadIndexRsr(path)
        rsrs = get_data.searchIndex(index, text)
        res = get_data.graphRsrPrj(path, rsrs)
        get_data.tblRsrPrjGraphCache.insert({'query': text, 'res':res})
        graph = res

    # projects histogram
    hist = get_data.getPrjHistogram(prj)
    
    # legislation
    zakoni = get_data.searchAllZakoni()

    # ods
    indexods = get_data.loadIndexOds(path)
    ods = get_data.searchIndex(indexods, text)

    # sio
    indexsio = get_data.loadIndexSio(path)
    sio = get_data.searchIndex(indexsio, text)
    
    # sio categories
    sio_cat = get_data.getUniqSio()

    # er
    ernews = get_data.getERNewsRelated(text)    
    # ernews = get_data.getERNewsDefault()    

    # oer
    indexoer = get_data.loadIndexOer(path)
    oer = get_data.searchIndex(indexoer, text)

    # keyws
    keyws = get_data.getRelatedKeywsRelRsr(rsr)

    return json.dumps({'keyws': keyws, 'oer': oer, 'ernews': ernews, 'sio': sio, 'sio_cat': sio_cat, 'ods': ods, 'zakoni': zakoni, 'rsr': rsr, 'prj':prj, 'lec':lec, 'graph':graph, 'hist': hist})

@app.route('/api/all/<text>/<limit>', methods=['GET'])
def search_all_limited(text, limit):
    limit = int(limit)

    # researchers
    indexrsr = get_data.loadIndexRsr(path)
    rsr = get_data.searchIndex(indexrsr, text)

    # projects
    indexprj = get_data.loadIndexPrj(path)
    prj = get_data.searchIndexLimited(indexprj, text, limit)

    # lectures
    indexlec = get_data.loadIndexLec(path)
    lec = get_data.searchIndexLimited(indexlec, text, limit)

    # researchers projects collaboration graph
    graph = []
    cache = get_data.getCache(get_data.tblRsrPrjGraphCache, text)
    if len(cache) > 0:
        graph = cache[0]['res']
    else:
        index = get_data.loadIndexRsr(path)
        rsrs = get_data.searchIndex(index, text)
        res = get_data.graphRsrPrj(path, rsrs)
        get_data.tblRsrPrjGraphCache.insert({'query': text, 'res':res})
        graph = res

    # projects histogram
    # hist = get_data.getPrjHistogram(prj)

    # legislation
    zakoni = get_data.searchAllZakoni()

    # ods
    indexods = get_data.loadIndexOds(path)
    ods = get_data.searchIndexLimited(indexods, text, limit)

    # sio
    indexsio = get_data.loadIndexSio(path)
    sio = get_data.searchIndexLimited(indexsio, text, limit)

    # er
    ernews = get_data.getERNewsRelated(text)
    #ernews = get_data.getERNewsDefault()

    # oer
    indexoer = get_data.loadIndexOer(path)
    oer = get_data.searchIndexLimited(indexoer, text, limit)

    # keyws
    keyws = get_data.getRelatedKeywsRelRsr(rsr)

    return json.dumps({'keyws': keyws, 'oer': oer[0], 'oer_count':oer[1], 'ernews': ernews, 'sio': sio[0], 'sio_count':sio[1], 'ods': ods[0], 'ods_count':ods[1], 'zakoni': zakoni, 'rsr': rsr, 'rsr_count': len(rsr), 'prj':prj[0], 'prj_count':prj[1], 'lec':lec[0], 'lec_count':lec[1], 'graph':graph})


@app.route('/api/first/<text>/<limit>', methods=['GET'])
def search_first_limited(text, limit):
    limit = int(limit)

    # researchers
    indexrsr = get_data.loadIndexRsr(path)
    rsr = get_data.searchIndex(indexrsr, text)

    # projects
    indexprj = get_data.loadIndexPrj(path)
    prj = get_data.searchIndexLimited(indexprj, text, limit)

    # lectures
    indexlec = get_data.loadIndexLec(path)
    lec = get_data.searchIndexLimited(indexlec, text, limit)

    # researchers projects collaboration graph
    graph = []
    cache = get_data.getCache(get_data.tblRsrPrjGraphCache, text)
    if len(cache) > 0:
        graph = cache[0]['res']
    else:
        index = get_data.loadIndexRsr(path)
        rsrs = get_data.searchIndex(index, text)
        res = get_data.graphRsrPrj(path, rsrs)
        get_data.tblRsrPrjGraphCache.insert({'query': text, 'res':res})
        graph = res

    # projects histogram
    # hist = get_data.getPrjHistogram(prj)

    # legislation
    zakoni = get_data.searchAllZakoni()

    # ods
    indexods = get_data.loadIndexOds(path)
    ods = get_data.searchIndexLimited(indexods, text, limit)

    # sio
    indexsio = get_data.loadIndexSio(path)
    sio = get_data.searchIndexLimited(indexsio, text, limit)

    # sio categories
    sio_cat = get_data.getUniqSio()

    # er
    ernews = get_data.getERNewsRelated(text)
    #ernews = get_data.getERNewsDefault()

    # er general
    ernews_general = get_data.getERNews()

    # oer
    indexoer = get_data.loadIndexOer(path)
    oer = get_data.searchIndexLimited(indexoer, text, limit)

    # keyws
    keyws = get_data.getRelatedKeywsRelRsr(rsr)

    return json.dumps({'keyws': keyws, 'oer': oer[0], 'oer_count':oer[1], 'ernews': ernews, 'ernews_general': ernews_general, 'sio': sio[0], 'sio_count':sio[1], 'sio_cat': sio_cat, 'ods': ods[0], 'ods_count':ods[1], 'zakoni': zakoni, 'rsr': rsr, 'rsr_count': len(rsr), 'prj':prj[0], 'prj_count':prj[1], 'lec':lec[0], 'lec_count':lec[1], 'graph':graph})

@app.route('/api/zakoni/all', methods=['GET'])
def get_zakoni_all():
    res = get_data.searchAllZakoni()
    return json.dumps(res)

@app.route('/api/ods/<text>', methods=['GET'])
def get_ods(text):
    index = get_data.loadIndexOds(path)
    ods = get_data.searchIndex(index, text)
    return json.dumps(ods)

@app.route('/api/zakoni/<num>', methods=['GET'])
def get_zakoni_num(num):
    res = get_data.searchNumZakoni(num)
    return json.dumps(res)

@app.route('/api/prj/hist/<text>', methods=['GET'])
def get_prj_hist(text):
    indexprj = get_data.loadIndexPrj(path)
    prj = get_data.searchIndex(indexprj, text)
    hist = get_data.getPrjHistogram(prj)
    return json.dumps(hist)

@app.route('/api/graph/<text>', methods=['GET'])
def get_graph(text):
# researchers projects collaboration graph
    graph = []
    cache = get_data.getCache(get_data.tblRsrPrjGraphCache, text)
    if len(cache) > 0:
        graph = cache[0]['res']
    else:
        index = get_data.loadIndexRsr(path)
        rsrs = get_data.searchIndex(index, text)
        res = get_data.graphRsrPrj(path, rsrs)
        get_data.tblRsrPrjGraphCache.insert({'query': text, 'res':res})
        graph = res
    return json.dumps({'graph':graph})

@app.route('/api/rsr/<text>', methods=['GET'])
def search_rsr(text):
    index = get_data.loadIndexRsr(path)
    res = get_data.searchIndex(index, text)
    return json.dumps(res)

@app.route('/api/sio/<text>', methods=['GET'])
def search_sio(text):
    index = get_data.loadIndexSio(path)
    res = get_data.searchIndex(index, text)
    return json.dumps(res)

@app.route('/api/oer/<text>', methods=['GET'])
def serch_oer(text):
    index = get_data.loadIndexOer(path)
    res = get_data.searchIndex(index, text)
    return json.dumps(res)

@app.route('/api/sio/categories', methods=['GET'])
def search_sio_categories():
    res = get_data.getUniqSio()
    return json.dumps(res)

@app.route('/api/sio/adv/<text>', methods=['GET'])
def search_sio_adv(text):
    index = get_data.loadIndexSio(path)
    res = get_data.searchIndexSioAdv(index, text)
    return json.dumps(res)

@app.route('/api/er/news', methods=['GET'])
def search_er_news():
    res = get_data.getERNews()
    #res = get_data.getERNewsDefault()
    return json.dumps(res)

@app.route('/api/er/news/<text>', methods=['GET'])
def search_er_news_related(text):
    res = get_data.getERNewsRelated(text)
    #res = {}
    #res = get_data.getERNewsDefault()
    return json.dumps(res)

@app.route('/api/rsrkeyws/<text>', methods=['GET'])
def search_rsrkeyws(text):
    index = get_data.loadIndexRsrKeyws(path)
    res = get_data.searchIndexRsrKeyws(index, text)
    return json.dumps(res)

@app.route('/api/autocomplete/<text>', methods=['GET'])
def search_autocomplete(text):
    index = get_data.loadIndexRsrKeyws(path)
    res = get_data.searchIndexRsrKeywsAutocomplete(index, text)
    return json.dumps(res)

@app.route('/api/rsrprjgraph/<text>', methods=['GET'])
def rsr_prj_graph(text):
    cache = get_data.getCache(get_data.tblRsrPrjGraphCache, text)
    if len(cache) > 0:
        return json.dumps(cache[0]['res'])
    else:
        index = get_data.loadIndexRsr(path)
        rsrs = get_data.searchIndex(index, text)
        res = get_data.graphRsrPrj(path, rsrs)
        get_data.tblRsrPrjGraphCache.insert({'query': text, 'res':res})
        return json.dumps(res)

@app.route('/api/prj/<text>', methods=['GET'])
def search_prj(text):
    index = get_data.loadIndexPrj(path)
    res = get_data.searchIndex(index, text)
    return json.dumps(res)

@app.route('/api/org/<text>', methods=['GET'])
def search_org(text):
    index = get_data.loadIndexOrg(path)
    res = get_data.searchIndex(index, text)
    return json.dumps(res)

@app.route('/api/lec/<text>', methods=['GET'])
def search_lec(text):
    print path
    index = get_data.loadIndexLec(path)
    res = get_data.searchIndex(index, text)
    return json.dumps(res)

@app.route('/api/keyws/relrsr/<text>', methods=['GET'])
def search_keyws_rel_rsr(text):
    index = get_data.loadIndexRsr(path)
    rsrs = get_data.searchIndex(index, text)
    res = get_data.getRelatedKeywsRelRsr(rsrs)
    return json.dumps(res)

@app.route('/api/class/relrsr/<text>', methods=['GET'])
def search_class_rel_rsr(text):
    index = get_data.loadIndexRsr(path)
    rsrs = get_data.searchIndex(index, text)
    res = get_data.getRelatedClassificationRelRsr(rsrs)
    return json.dumps(res)

####################
# Internal
###################

# Main
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=8888)

