function drawGraph(graph) {
    nodes = graph.nodes;
    edges = graph.edges;

    var s = new sigma('graph');
    
    for (var i=0; i<nodes.length; i++) {
        s.graph.addNode({id: nodes[i].id,
            label: nodes[i].name,
            size: 1,
            color: '#f00',
            x: nodes[i].x,
            y: nodes[i].y
        })
    }
   
    for (var i=0; i<edges.length; i++) {
        s.graph.addEdge({id: i.toString(),
            source: edges[i].rsrid1,
            target: edges[i].rsrid2,
            type: 'curve'
        });
    }

   var edges = s.graph.edges(); 

   s.startForceAtlas2();
   setTimeout(function () {
       s.stopForceAtlas2();
   }, 1000);
}


function drawGraph1(graph) {
	var c = new Array();
	c['-1'] = "#9B9B9B";
	c['N'] = "#0E53A7"
	c['M'] = "#A64300"
	c['B'] = "#FF6700"
	c['T'] = "#0ACF00"
	c['S'] = "#FBB917"
	c['H'] = "#FBB917"
	c['I'] = "#FF0000"
    var nodes = graph.nodes;
    var edges = graph.edges;

    var minNodeSizeVar = 2;
    if (nodes.length < 10 || nodes.length < 20)
        minNodeSizeVar = 4;

    $('#graph').empty();
    var sigRoot = document.getElementById('graph');
    var sigInst = sigma.init(sigRoot).drawingProperties({
        defaultLabelColor: 'black',
        font: 'Arial',
        edgeColor: 'source',
        defaultEdgeType: 'curve'
    }).graphProperties({
        minNodeSize: minNodeSizeVar,
        maxNodeSize: 10
    });

    for (var i = 0; i < nodes.length; i++) {
        sigInst.addNode(nodes[i].id, { label: nodes[i].name, 'x': nodes[i].x, 'y': nodes[i].y, color: c[nodes[i].color], size: nodes[i].degree})
    }

    for (var i = 0; i < edges.length; i++) {
        sigInst.addEdge(i.toString(), edges[i].rsrid1, edges[i].rsrid2);
    }

    var duration = 2000 + (nodes.length * 20.0)
    console.log(duration);
    sigInst.draw();
    sigInst.startForceAtlas2();
    setTimeout(function () {
        sigInst.stopForceAtlas2();
        sigInst.refresh();
    }, duration);
};
