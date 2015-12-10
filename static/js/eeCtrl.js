var app = angular.module('eeApp', []);
app.controller('eeCtrl', ['$scope', '$http', function($scope, $http) {
	
	var response = ''
	
	$scope.searchString = "mathematics"
	$scope.sections = [ "events", "experts", "videos", "materials", "projects" ]
	$scope.counter = []
	resetCounters()
	$scope.keywords = { researchers: [], related: [] }
	$scope.histogram = []
	
	$scope.sources = [
		{ name: "SAExperts", url: "rsr/", limit: 10, section: "experts", count: true }, // researchers indexed by keywords
		{ name: "SAExpertsCollaborationGraph", url: "graph/", limit: 0, section: "experts", count: false },
		{ name: "SAProjects", url: "prj/", limit: 10, section: "projects", count: true }, // projects indexed by keywords, abstract, world and domestic significance
		{ name: "SAProjectsHistogram", url: "prj/hist/", limit: 0, section: "projects", count: false },
		{ name: "VideoLectures", url: "lec/", limit: 10, section: "videos", count: true }, // videolectures indexed by descriptions
		{ name: "EventRegistry", url: "er/news/", limit: 5, section: "events", count: true }, // news from EventRegistry
		{ name: "EventRegistryEducation", url: "er/news", limit: 10, section: "general", count: false }, // news from EventRegistry
		{ name: "SIO", url: "sio/", limit: 7, section: "materials", count: true },
		{ name: "ODS", url: "ods/", limit: 7, section: "materials", count: true },
		{ name: "OER", url: "oer/", limit: 7, section: "materials", count: true },
		{ name: "Zakoni", url: "zakoni/10", limit: 0, section: "general", count: false },
		{ name: "KeywordsResearchers", url: "rsrkeyws/", limit: 10, section: "keywords", count: false }, // keywords assigned to researchers
		{ name: "KeywordsRelated", url: "keyws/relrsr/", limit: 10, section: "keywords", count: false }, // keywords are related if they are related to a common researcher
		{ name: "KeywordsAll", url: "class/relrsr/", limit: 10, section: "keywords", count: false }
	]

	$scope.counterSum = function() {
		var sum = 0
		$scope.counter.forEach(function(c) { sum += c.counter })
		return sum
	}
	$scope.fontSize = function(f) {
		return Math.round(2*Math.log(f)+10) + "px";
	}
	$scope.levelText = function(level) {
		switch(level) {
			case "gimnazija": return "gimnazija"; break;
			case "strokovne": return "strokovna šola"; break;
			case "osnovnasola": return "osnovna šola"; break;
			case "poklicna": return "poklicna šola"; break;
			case "visjesolska": return "višja šola"; break;
			case "vrtec": return "vrtec"; break;
		}
	}
	$scope.eeMore = function(name) {
		moreResults(name)
		if (name == "experts") updateSearchResults('SAExpertsCollaborationGraph', drawGraph, ['graphBig'])
		var areaName = name.charAt(0).toUpperCase() + name.slice(1);
		$('.overviewSearchResults').hide()
		$('.narrowSearchResults').hide()
		$('#only' + areaName).show()
		$('#btn' + areaName).attr('checked', 'checked');
		if (name == 'materials') $("#advancedSearchMaterials").show()
		else $("#advancedSearchMaterials").hide()
	}
	$scope.eeAllSearch = function() {
		$('.narrowSearchResults').hide()
		$("#advancedSearchMaterials").hide()
		$('.overviewSearchResults').show()
		fetchData()
	}
	$scope.updateSearchResults = function(event) {
		if (event.type == 'click' && event.target.id == "searchButton" || event.type == 'keypress' && event.charCode == 13) {
			resetCounters()
			var sq = $('#searchQuery').val()
			$('#searchQuery').attr("placeholder", sq)
			$scope.searchString = sq
			var checked = []
			$('.togglesMaterials input:checked').each(function(i, v) {
				value = $(this).val();
				if (value != "on") checked.push(value);
			});
			if (checked.length > 0) { // if Materials
				response = '{' + checked.join();
				if ($scope.searchString.length > 0) response += ',"text":"' + $scope.searchString + '"}'
				else response += '}'
				console.log(response)
				moreResults('materials')
				$('.overviewSearchResults').hide()
				$('.narrowSearchResults').hide()
				$('#onlyMaterials').show()
			}
			else fetchData($('#searchQuery').val());
		}
	}
	$scope.setLectureBackground = function(elementId) {
		$.ajax({
			url:"http://videolectures.net/" + elementId + "/screenshot.jpg",
			type:'HEAD',
			error:
				function(){
					console.log(elementId)
				},
			success:
				function(){
					console.log("not image")
				}
		});
	}
	
	function resetCounters() {
		$scope.counter = []
		$scope.sections.forEach(function(section) { $scope.counter.push({label: section, counter: 0}) })
	}
	function sourceObject(source) {
		var result = $.grep($scope.sources, function(s){ return s.name === source })
		if (result.length == 1) return result[0]
		else return ''
	}
	function updateCounter(label, value) {
		var result = $.grep($scope.counter, function(c){ return c.label === label })
		if (value == 0) result[0].counter = 0 // if value equals 0, reset counter
		else result[0].counter += value
	}
	function updateSearchResults(source, updateCallback, args) {
		var r = ''
		var s = sourceObject(source)
		if (s.section != 'general')  r = $scope.searchString
		if (s.name == 'SIO' && response != '') r = response
		$http.get("/api/" + s.url + r, 'json').success(function(data, status, headers, config) {
			args.push(s)
			args.push(data)
			updateCallback.apply(this, args)
		}).error(function(data, status, headers, config) {});
	}
	function updateSource(source, input) {
		var data = input
		if ((source.name).includes('EventRegistry')) data = input.articles.results
		if (source.count == true && data.length != 0) updateCounter(source.section, data.length)
		$scope[source.name] = sliceResults(data, source.limit)
	}
	function allFromSource(source, input) {
		var data = input
		if ((source.name).includes('EventRegistry')) data = input.articles.results
		$scope[source.name] = data
	}
	function drawGraph(elementId, source, data) {
		drawRsrPrjColl(data.graph, elementId);
	}
	function keywordsAll(source, data) {
		$scope[source.name] = []
		$.each( ['science', 'field', 'subfield'], function( key, level ) {
			$.each (data[level+'s'], function(i, v) { $scope[source.name].push({category: level, name: v[level], freq: v.freq}) })
		})
	}
	function keywordsRelated(source, data) {
		$scope[source.name] = data.slice(0, Math.min(data.length-1, 15));
		d3.layout.cloud().size([cloudElement.width, cloudElement.height]).words($scope[source.name]).padding(2).text(getWord).spiral("archimedean").fontSize(wordSize).on("end", draw).start();
	}
	function keywordsResearchers(source, data) {
		console.log(source.name)
	}
	function moreResults(section) {
		var sources = $.grep($scope.sources, function(c){ return c.section === section })
		sources.forEach(function(source) { updateSearchResults(source.name, allFromSource, []) })
	}
	function sliceResults(data, limit) {
		if (limit > 0 && limit < data.length) return data.slice(0, limit)
		else return data
	}
	function fetchGeneralData() {
		updateSearchResults('Zakoni', updateSource, [])
		updateSearchResults('EventRegistryEducation', updateSource, [])
		$http.get("/api/sio/categories").success(function(data, status, headers, config) {
			$scope["categoriesMaterials"] = data
			$scope.categoriesMaterials.grades = Array(1, 2, 3, 4, 5, 6, 7, 8, 9)
			$scope.categoriesMaterials.levels = Array("gimnazija", "strokovne", "osnovnasola", "poklicna", "visjesolska", "vrtec")
		}).error(function(data, status, headers, config) {});
	}
	function fetchData(searchString) {
		resetCounters()
		$('#wordCloud').empty()
		if (typeof searchString == 'undefined' || searchString.length == 0) searchString = $scope.searchString
		$scope.sources.forEach(function(source) { if (source.count == true) updateSearchResults(source.name, updateSource, []) })
		updateSearchResults('KeywordsAll', keywordsAll, [])
		updateSearchResults('KeywordsRelated', keywordsRelated, [])
		updateSearchResults('KeywordsResearchers', keywordsResearchers, [])
		updateSearchResults('SAExpertsCollaborationGraph', drawGraph, ['graph'])
	}
	function drawHistogram(histogram, elementSelector) {
		console.log(histogram)
		var histogramContainer = d3.select(elementSelector);
		var margin = {top: 20, right: 20, bottom: 30, left: 40},
			width = histogramContainer.node().getBoundingClientRect().width - margin.left - margin.right,
			height = 300 - margin.top - margin.bottom;
		var x = d3.scale.ordinal().rangeRoundBands([0, width], .1);
		var y = d3.scale.linear().range([height, 0]);
		var xAxis = d3.svg.axis().scale(x).orient("bottom");
		var yAxis = d3.svg.axis().scale(y).orient("left").ticks(10, '');
		var svg = histogramContainer.append("svg").attr("width", width + margin.left + margin.right).attr("height", height + margin.top + margin.bottom).append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
		x.domain(histogram.map(function(d) { return d.year; }));
		y.domain([0, d3.max(histogram, function(d) { return d.value; })]);
		svg.append("g").attr("class", "x axis").attr("transform", "translate(0," + height + ")").call(xAxis);
		svg.append("g").attr("class", "y axis").call(yAxis).append("text").attr("transform", "rotate(-90)").attr("y", 6).attr("dy", ".71em").style("text-anchor", "end").text("Frequency");
		svg.selectAll(".bar").data(histogram).enter().append("rect").attr("class", "bar").attr("x", function(d) { return x(d.letter); }).attr("width", x.rangeBand())
			.attr("y", function(d) { return y(d.value); })
			.attr("height", function(d) { return height - y(d.value); });
	}
	
	// keyword wordcloud
	var cloudElement = {width: $("#wordCloud").width(), height: 200, translate: "translate(" + [$("#wordCloud").width()/2, 100] + ")"};
	var wordSize = function(d) { return (2*Math.log(d.freq)+10); }
	var wordSizePX = function(d) { return (2*Math.log(d.freq)+10) + "px"; }
	var getWord = function(d) { return d.keyws; }
	var color = d3.scale.linear().domain([0, 40, 70, 80, 90, 100]).range(["#fff", "#987", "#756", "#654", "#423", "#422"]);
	function draw(words) {
		d3.select("#wordCloud").append("svg").attr("width", cloudElement.width).attr("height", cloudElement.height).attr("class", "wordcloud").append("g").attr("transform", cloudElement.translate).selectAll("text").data(words).enter()
			.append("text").style("font-size", wordSizePX).style("fill", function(d, i) { return color(i); }).attr("text-anchor", "middle")
			.attr("transform", function(d) { return "translate(" + [d.x, d.y] + ") rotate(" + d.rotate + ")"; }).text(getWord);
	}
	
	fetchGeneralData()
	fetchData($scope.searchString)

	// slider stuff
	
	var eltWidth = 300;
	var eltNum = Math.floor($('.hNewsBox').width()/eltWidth)
	var minMarginLeft = (eltNum-10)*eltWidth;
	
	function sliderMoveRight(slider) {
		if (slider.marginLeft <= minMarginLeft) slider.marginLeft = eltWidth;
		slider.marginLeft -= eltWidth;
		slider['margin-left'] = slider.marginLeft + 'px';
		$('#infoMargin').html = slider.marginLeft;
		return slider['margin-left'];
	}
	function sliderMoveLeft(slider) {
		if (slider.marginLeft >= 0) slider.marginLeft = minMarginLeft;
		slider.marginLeft += eltWidth;
		slider['margin-left'] = slider.marginLeft + 'px';
		$('#infoMargin').html = slider.marginLeft;
		return slider['margin-left'];
	}
  
	$scope.eeNews = {
		marginLeft: 0,
		eeHNews: { 'margin-left': '0px' },
		menuItems: 10,
		moveRight: function() { return sliderMoveRight($scope.eeNews); },
		moveLeft: function() { return sliderMoveLeft($scope.eeNews); }
	}
	$scope.eePolicies = {
		marginLeft: 0,
		eeHPolicies: { 'margin-left': '0px' },
		menuItems: 10,
		moveRight: function() { return sliderMoveRight($scope.eePolicies); },
		moveLeft: function() { return sliderMoveLeft($scope.eePolicies); }
	}

}]);
