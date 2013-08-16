function render_aggr_graph(selected_name, api_parameters){
    var ajaxGraph = new Rickshaw.Graph.Ajax( {
        element: document.getElementById("chart"),
        height: 300,
        renderer: 'unstackedarea',
        dataURL: '/api?'+ api_parameters,
        onData: function(d) {return d; },
        onComplete: function(transport) {
            var graph = transport.graph;
            var format = function(n) {
                return Math.floor(n/4) + 1996;
            };

            var x_format = function(n){
                var date = new Date(n*1000);
                var month = Math.floor(date.getMonth()/3) ;
                var map = {
                    0: 'Jan-Mar ',
                    1: 'Mar-Jun ',
                    2: 'Jul-Sept ',
                    3: 'Oct-Dec '
                };
                return map[month] + date.getFullYear();
            };

            var y_format = function(y){
                if(query_name.indexOf('has_') === 0){
                    return y.toFixed(2) + " %";
                }
                return y === null ? y : y.toFixed(2);
            }

            var hoverDetail = new Rickshaw.Graph.HoverDetail( {
                graph: graph,
                xFormatter: x_format,
                yFormatter: y_format
            } );

            var x_ticks = new Rickshaw.Graph.Axis.Time( {
                graph: graph,
                orientation: 'bottom',
                element: document.getElementById('x_axis_' + selected_name),
                timeUnit: (new Rickshaw.Fixtures.Time()).unit('year')
            } );
            x_ticks.render();

            var shelving = new Rickshaw.Graph.Behavior.Series.Toggle( {
                graph: graph
            } );
        },
        series:
            [
                {
                    color: "rgba(70,130,180,0.6)",
                    name: "All Sites"
                }
            ]
    } );
    return ajaxGraph;
}

function render_site_graph(selected_name, site_name, api_parameters){
    var ajaxGraph = new Rickshaw.Graph.Ajax( {
        element: document.getElementById("chart"),
        height: 300,
        renderer: 'unstackedarea',
        dataURL: '/api?'+ api_parameters,
        onData: function(d) {return d; },
        onComplete: function(transport) {
            var graph = transport.graph;

            var y_format = function(y){
                if(query_name.indexOf('has_') === 0){
                    return y.toFixed(2) + " %";
                }
                return y === null ? y : y.toFixed(2);
            }
          
            var hoverDetail = new Rickshaw.Graph.HoverDetail( {
                graph: graph,
                yFormatter: y_format
            } );

            var axes = new Rickshaw.Graph.Axis.Time( {
                graph: graph
            } );
            axes.render();

            var legend = new Rickshaw.Graph.Legend( {
                graph: graph,
                element: document.getElementById('legend')

            } );

            var shelving = new Rickshaw.Graph.Behavior.Series.Toggle( {
                graph: graph,
                legend: legend
            } );
        },
        series:
            [
                {
                    color: "rgba(70,130,180,0.6)",
                    name: site_name
                },
                {
                    color: "rgba(200,200,200,0.4)",
                    name: "All Sites"
                }
            ]
    } );
    return ajaxGraph;
}

