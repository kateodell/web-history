function render_graph(selected_name, selected_long_name, api_parameters, aggregate){
    var ajaxGraph
    if(aggregate){
        ajaxGraph = new Rickshaw.Graph.Ajax( {

        element: document.getElementById("chart_" + selected_name),
        height: 250,
        width: 700,  //TODO: figure out how to avoid hardcoding the width
        renderer: 'unstackedarea',
        dataURL: '/api?'+ api_parameters,
        onData: function(d) {return d; },
        onComplete: function(transport) {
            var graph = transport.graph;
            var format = function(n) {
                return Math.floor(n/4) + 1996;
                // if (n % 4 === 0)
                //     return Math.floor(n/4) + 1996;
                // else
                //     return "";
            };

            var x_format = function(n){
                var year = Math.floor(n/4) + 1996;
                var months = n % 4 ;
                var map = {
                    0: 'Jan-Mar ',
                    1: 'Mar-Jun ',
                    2: 'Jul-Sept ',
                    3: 'Oct-Dec '
                };
                return map[months] + year;
            };

            var hoverDetail = new Rickshaw.Graph.HoverDetail( {
                graph: graph,
                xFormatter: x_format
            } );

            var x_ticks = new Rickshaw.Graph.Axis.X( {
                graph: graph,
                orientation: 'bottom',
                element: document.getElementById('x_axis_' + selected_name),
                //ticks: 20,
                timeUnit: (new Rickshaw.Fixtures.Time()).unit('year'),
                tickFormat: format
            } );
            x_ticks.render();
           
            var legend = new Rickshaw.Graph.Legend( {
                graph: graph,
                element: document.getElementById('legend_' + selected_name)

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
                    name: selected_long_name
                }
            ]
    } );
    } else {
        ajaxGraph = new Rickshaw.Graph.Ajax( {
            element: document.getElementById("chart_" + selected_name),
            height: 250,
            width: 700,  //TODO: figure out how to avoid hardcoding the width
            renderer: 'unstackedarea',
            dataURL: '/api?'+ api_parameters,
            onData: function(d) {return d; },
            onComplete: function(transport) {
                var graph = transport.graph;
                
                var hoverDetail = new Rickshaw.Graph.HoverDetail( {
                    graph: graph
                } );

                var axes = new Rickshaw.Graph.Axis.Time( {
                    graph: graph
                } );
                axes.render();

                var legend = new Rickshaw.Graph.Legend( {
                    graph: graph,
                    element: document.getElementById('legend_' + selected_name)

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
                        name: selected_long_name
                    },
                    {
                        color: "rgba(100,100,100,0.3)",
                        name: "All Sites"
                    }
                ]
        } );
    }

    return ajaxGraph;
}

