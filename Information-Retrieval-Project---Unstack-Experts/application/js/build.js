/** 
 * @projectDescription	Visual Thesaurus
 * @author 	Matt Hobbs
 * @version 	0.1
 *
 * TODO:
 * DONE: Make words square
 * DONE: Try a few settings out,stop the juttering
 * Adjust colour pallete
 * DONE: Ajax loader
 * DONE: Clear canvas on search
 * DONE: Add link to data source + arbor
 * DONE: New API Key
 * DONE: Add cursors
 * DONE: Adjust alpha
 * DONE: Code cleanup
 * DONE: Add resize
 * DONE: Click word re-search
 */
var visThesaurus = function(){
    //Define vars
    var allData, val, sys;
	
	//Particle Colo(u)rs
	var particleColour = [
		'#FF003D',
		'#FC930A',
		'#CCF390',
		'#E0E05A',
		'#F7C41F',
		'#A0C230'
	]
    
    //Bighugelabs settings
    var apiKey = "91afccf5f2469ba63db058a18e4a6c79";
       
    return {
        init:function(){
            //Attach the events
            $("#wordSubmit").click(function(e){
                val = $("#wordInput").val();
                if(val === ""){
                    $("<p>").attr("class", "error").text("Please enter a word!").appendTo("#formWrapper");
                } else {
                    $("p.error").remove();
					$("<img>").attr({class:"loader", src: "images/1.gif"}).appendTo("#formWrapper");
                    visThesaurus.wordRequest(val);
                }
                return false;
            });
            
            //Start the renderer
            sys = arbor.ParticleSystem({friction:1, stiffness:900, repulsion:100, gravity: true, fps: 60, dt: 0.08, precision: 1.0});
            sys.renderer = Renderer();
        },
        wordRequest:function(word){
            //var url = "http://words.bighugelabs.com/api/2/" + apiKey + "/" + word + "/json";
			var url = "http://localhost:1234/";// + "/" + word + "/json";
            
			//Clear all previous particles
			sys.prune(function(node, from, to){return true;});
			
            $.ajax({
				url: url,
				dataType: "json",
				type: 'GET',
				error: visThesaurus.wordError,
                success: visThesaurus.wordSuccess,
				complete: function(){$("img.loader").remove();}
            });
        },
        wordSuccess:function(data){
            //Original word isn't returned in data
            var original = $("#wordInput").val();
            
			//Store all data recieved
            allData = data;
            
            //Define some vars
            var ta_type;
            //Add root node
            sys.addNode('home', {label:original, use:'home', alpha:'1', color: particleColour[0], expanded: true, level: 0, parent: null});
            var color = 1;
			var num = 0;
			var taglist = [];
			for(var key in data){
				var out = 0;
				if(num > 2){
					break;
				}
				if (data.hasOwnProperty(key)) {
					if(data[key].length < 2 )
						continue;
					else{
							//var values = [];
						    var pos = key.indexOf(":");
							var tag = key.substring(pos+1);
							tag = tag.replace(/-/g, ' ');
							var values = tag.split(" ");
							out = 0;
							for(var t = 0;t<taglist.length;t++){
								for(var j = 0 ;j < values.length ; j++){
									if(taglist[t] == values[j]){
										out = 1;
										break;
									}
									
								}
								if(out == 1)
										break;
							}
							if(out == 1)
								continue;
							taglist.push(values[0]);
							taglist.push(values[1]);
							sys.addNode(key, {label:tag, use:'type', alpha:'1', color: particleColour[4], expanded: false, level: 1, parent: 'home'});
							sys.addEdge('home',key,  {length:0.1});
							color++;
							if(color > 5)
								color = 0;
						}
				}
				num++;
			}
			
            /*if('noun' in data){
                sys.addNode('noun', {label:'Nouns', use:'type', alpha:'1', color: particleColour.noun, expanded: false, level: 1, parent: 'home'});
                sys.addEdge('home','noun',  {length:0.1});
            }
            if ('verb' in data) {
                sys.addNode('verb', {label:'Verbs', use:'type', alpha:'1', color: particleColour.verb, expanded: false, level: 1, parent: 'home'});
                sys.addEdge('home','verb', {length: 0.1});
            }
            if('adjective' in data){
                sys.addNode('adjective', {label:'Adjectives', use:'type', alpha:'1', color: particleColour.adjective, expanded: false, level: 1, parent: 'home'});
                sys.addEdge('home','adjective', {length:0.1});
            }*/
            
        },
        wordError: function(error){
            console.warn("There was an error: " + error);
        },
        generateSubs: function(nodeName){
            //Used to generate the sub-sections

            //Select our clicked dataset
            var dataSet;
            switch(nodeName){
                case "noun":
                    dataSet = allData.noun;
                    break;
                case "verb":
                    dataSet = allData.verb;
                    break;
                case "adjective":
                    dataSet = allData.adjective;
                    break;
            }
            
            $.each(dataSet, function(i, set){
                var wordlbl = nodeName + i;
                switch(i){
                    case "syn":
                        ta_type = "Synonymons";
                        break;
                    case "ant":
                        ta_type = "Antonymons";
                        break;
                    case "rel":
                        ta_type = "Related";
                        break;
                    case "sim":
                        ta_type = "Similar";
                        break;
                    case "usr":
                        ta_type = "User Suggested";
                        break;
                }
                sys.addNode(wordlbl, {label:ta_type, use:'sub-type', alpha:'1', color: particleColour.subset, expanded: false, level: 2, parent: nodeName});
                sys.addEdge(nodeName, wordlbl);
            });
        },
        generateWords: function(nodeName){
            var dataSet = allData;
            var full_name = nodeName.split("%");
			
			for(var i = 0 ; i< full_name.length ; i++){
	
				dataSet = dataSet[full_name[i]];
			}
			
			if(dataSet.length != undefined && dataSet != undefined){
				var num = 1;
				for(var j = 0; j<dataSet.length ; j++){
					var lbl = nodeName + "%" + j;
					if (typeof(dataSet[j]) == "string"){
						var word = dataSet[j];
						sys.addNode(lbl, {label:word, wordlength:word.length,  use:'word', alpha:'1', color: particleColour[0], expanded: true, level: 3, parent: nodeName});
						sys.addEdge(nodeName, lbl);
					}
					if (typeof(dataSet[j]) == "object"){
						var tag ;
						for(var key in dataSet[j]){
							tag = lbl + "%" +key;
							var disp_name = key + " " + num;
							sys.addNode(tag, {label:disp_name, wordlength:key.length,  use:'sub-type', alpha:'1', color: particleColour[3], expanded: false, level: 3, parent: nodeName});
							sys.addEdge(nodeName, tag);
							num++;
						}
					}
				}
			}
			if(typeof(dataSet) == "object" && dataSet.length == undefined){
				for(var key in dataSet){
							tag = nodeName + "%" + key;
							sys.addNode(tag, {label:key, wordlength:key.length,  use:'type', alpha:'1', color: particleColour[1], expanded: false, level: 3, parent: nodeName});
							sys.addEdge(nodeName, tag);
						}
				
			}
			
            /*switch(nodeName){
                //Nouns
                case "nounsyn":
                    dataSet = allData.noun.syn;
                    break;
                case "nounant":
                    dataSet = allData.noun.ant;
                    break;
                case "nounrel":
                    dataSet = allData.noun.rel;
                    break;
                case "nounsim":
                    dataSet = allData.noun.sim;
                    break;
                case "nounusr":
                    dataSet = allData.noun.usr;
                    break;
                //Verbs
                case "verbsyn":
                    dataSet = allData.verb.syn;
                    break;
                case "verbant":
                    dataSet = allData.verb.ant;
                    break;
                case "verbrel":
                    dataSet = allData.verb.rel;
                    break;
                case "verbsim":
                    dataSet = allData.verb.sim;
                    break;
                case "verbusr":
                    dataSet = allData.verb.usr;
                    break;
                //Adjective
                case "adjectivesyn":
                    dataSet = allData.adjective.syn;
                    break;
                case "adjectiveant":
                    dataSet = allData.adjective.ant;
                    break;
                case "adjectiverel":
                    dataSet = allData.adjective.rel;
                    break;
                case "adjectivesim":
                    dataSet = allData.adjective.sim;
                    break;
                case "adjectiveusr":
                    dataSet = allData.adjective.usr;
                    break;
            }*/
            dataSet = allData[nodeName]
            //Start word loop
            /*$.each(dataSet, function(i, word){
                var lbl = nodeName + "%" + word;			
                sys.addNode(lbl, {label:word, wordlength:word.length,  use:'word', alpha:'1', color: particleColour.words, expanded: false, level: 3, parent: nodeName});
                sys.addEdge(nodeName, lbl);
            });*/
        },
		newSearch: function(newword){
			$re = $("#re-search");
			//Show
			$re.find("p span").text(newword).end().show();
			
			//Close if no
			$("#re-search .close, #re-search .no").click(function(e){
				$("#re-search").hide();
				return false;
			});
			
			$re.find(".yes").click(function(e){
				$("#re-search").hide();
				
				$("#wordInput").val(newword);
				$("p.error").remove();
				$("<img>").attr({class:"loader", src: "images/1.gif"}).appendTo("#formWrapper");
				
				//Perform new search
				visThesaurus.wordRequest(newword);
				return false;
			});
		},
		removeNodes: function(name, level){
			if(level === 2){
				//Clicked node
				var clicked = sys.getNode(name);
				
				//Clicked parent node
				var parent = sys.getNode(clicked.data.parent);
				
				//Parent is nolonger expanded
				parent.data.expanded = false;
				
				//Remove Children
				sys.prune(function(node, from, to){
					if(node.data.parent === name){
						return true;
					}
				});
				
				//Remove clicked node too
				sys.pruneNode(name);
			}
		}
    }
}();

//The arbor renderer
var Renderer = function(){
    var canvas = document.getElementById("viewport");
	var dom = $("#viewport");
    
    //Screen size
	var cWidth = canvas.width = window.innerWidth;
	var cHeight = canvas.height = window.innerHeight;
    
    var context = canvas.getContext('2d');
    var particleSystem;
    
   var gfx = arbor.Graphics(canvas);
    
    return {
        init:function(system){
            //Define some particle system settings
            particleSystem = system;
            particleSystem.screenSize(cWidth, cHeight);
            particleSystem.screenPadding(100);
            
            //Node dragging
            this.initMouseHandling();
			
			//On window resize
			$(window).resize(this.windowsized);
        },
		windowsized:function(){
			cWidth = window.innerWidth;
			cHeight = window.innerHeight;
			
			particleSystem.screenSize(cWidth, cHeight);
		},
        redraw:function(){
            //Set the canvas styles for every redraw
            context.fillStyle = "white";
            context.fillRect(0,0, cWidth, cHeight);
            
            //The lines between nodes
            particleSystem.eachEdge(function(edge, pt1, pt2){
                // draw a line from pt1 to pt2
                context.strokeStyle = "rgba(0,0,0, .333)";
                context.lineWidth = 1;
                context.beginPath();
                context.moveTo(pt1.x, pt1.y);
                context.lineTo(pt2.x, pt2.y);
                context.stroke();
            });
            
            //The style of each node
            particleSystem.eachNode(function(node, pt){
                var w;
                
                //Create our different types of nodes
                if(node.data.use === 'home'){
                    w = 160;
                    gfx.oval(pt.x-w/2, pt.y-w/2, w, w, {fill:node.data.color, alpha:node.data.alpha});
                    gfx.text(node.data.label, pt.x, pt.y+4, {color:"white", align:"center", font:"Arial", size:24});
                } else if(node.data.use === 'type'){
                    w = 140;
                    gfx.oval(pt.x-w/2, pt.y-w/2, w, w, {fill:node.data.color, alpha:node.data.alpha});
                    gfx.text(node.data.label, pt.x, pt.y+4, {color:"white", align:"center", font:"Arial", size:19});
                } else if(node.data.use === 'sub-type'){
                    w = 100;
                    gfx.oval(pt.x-w/2, (pt.y-w/2)+w/4, w, w/2, {fill:node.data.color, alpha:node.data.alpha});
                    gfx.text(node.data.label, pt.x, pt.y+4, {color:"white", align:"center", font:"Arial", size:18});
                } else if(node.data.use === 'word'){
                    w = parseInt((node.data.wordlength*5.7) + 30, 10);
					gfx.rect(pt.x-w/2, pt.y-10, w, 20, 4, {fill:node.data.color, alpha:node.data.alpha})
                    gfx.text(node.data.label, pt.x, pt.y+5, {color:"white", align:"center", font:"Arial", size:14});
                }
            });
        },
        initMouseHandling:function(){
			var _mouseP, selected;
            var dragged = null;
			var nearest = null;

            var handler = {
				moved:function(e){
					var pos = $(canvas).offset();
					_mouseP = arbor.Point(e.pageX-pos.left, e.pageY-pos.top);
					nearest = particleSystem.nearest(_mouseP);
					
					if(!nearest.node){
						return false;
					}
					
					if(!(nearest.node.data.use === 'home')){
						selected = (nearest.distance < 30) ? nearest : null;
						if(selected){
							dom.addClass('hovered');
						} else {
							dom.removeClass('hovered');
						}
					}
					return false;
				},
                clicked:function(e){
                    var pos = $(canvas).offset();
                    _mouseP = arbor.Point(e.pageX-pos.left, e.pageY-pos.top);
                    dragged = particleSystem.nearest(_mouseP);
                    
                    if (dragged && dragged.node !== null){
                        //Store the clicked node name
						var nName, nLevel;
						
                        if(!dragged.node.data.expanded){
                            dragged.node.data.expanded = true;
                            nName = dragged.node.name;
                            nLevel = dragged.node.data.level;
							visThesaurus.generateWords(nName);
                           /* if(nLevel === 1){
                                //Generate subs below noun, verb etc
                                visThesaurus.generateSubs(nName);
                            } else if(nLevel === 2) {
                                //We are generating the words
                                visThesaurus.generateWords(nName);
							} else if(nLevel === 3) {
								//Clicking on a single word, search it?
								visThesaurus.newSearch(dragged.node.data.label);
                            } else {
                                return false;
                            }*/
                        } else {
							//Node expanded so remove
							nName = dragged.node.name;
							nLevel = dragged.node.data.level;
							visThesaurus.removeNodes(nName, nLevel);
						}
                        dragged.node.fixed = true;
                    }

                    $(canvas).bind('mousemove', handler.dragged);
                    $(window).bind('mouseup', handler.dropped);
                    return false;
                },
                dragged:function(e){
                    var pos = $(canvas).offset();
                    var s = arbor.Point(e.pageX-pos.left, e.pageY-pos.top);
                    
                    if (dragged && dragged.node !== null){
                        var p = particleSystem.fromScreen(s);
                        dragged.node.p = p;
                    }
                    
                    return false;
                },
                dropped:function(e){
                    if (dragged===null || dragged.node===undefined) {
                        return;
                    }
                    if (dragged.node !== null){
                        dragged.node.fixed = false;
                    }
                    dragged.node.tempMass = 1000;
                    dragged = null;
                    $(canvas).unbind('mousemove', handler.dragged);
                    $(window).unbind('mouseup', handler.dropped);
                    _mouseP = null;
                    return false;
                }
            }

            // start listening
            $(canvas).mousedown(handler.clicked);
			$(canvas).mousemove(handler.moved);
        }
    }
}

jQuery(function($){
    visThesaurus.init();
});