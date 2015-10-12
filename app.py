from flask import Flask, render_template
from data import get_data
import json

app = Flask(__name__)
path = "/home/luis/data/mario/openedu/"

###########
# Interface
###########

@app.route('/')
def search():
    return render_template('search.html')

@app.route('/graph')
def graph():
    return render_template('graph.html')

###########
# API
###########

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

    return json.dumps({'rsr': rsr, 'prj':prj, 'lec':lec, 'graph':graph, 'hist': hist})

@app.route('/api/rsr/<text>', methods=['GET'])
def search_rsr(text):
    index = get_data.loadIndexRsr(path)
    res = get_data.searchIndex(index, text)
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

####################
# Internal
###################


# Main
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=8888)

