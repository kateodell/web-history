new Rickshaw.Graph.Ajax( {

    element: document.getElementById("chart"),
    height: 250,
    renderer: 'area',
    dataURL: '/api?query='+ selected_name,
    onData: function(d) {return d; },
    onComplete: function(transport) {
        var graph = transport.graph;
        var format = function(n) {
            if (n % 4 === 0)
                return Math.floor(n/4) + 1996;
            else
                return "";
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

        var legend = new Rickshaw.Graph.Legend( {
            graph: graph,
            element: document.getElementById('legend')

        } );

        var shelving = new Rickshaw.Graph.Behavior.Series.Toggle( {
            graph: graph,
            legend: legend
        } );

        var axes = new Rickshaw.Graph.Axis.Time( {
            graph: graph
        } );

        // var x_ticks = new Rickshaw.Graph.Axis.X( {
        //     graph: graph,
        //     orientation: 'bottom',
        //     element: document.getElementById('x_axis'),
        //     pixelsPerTick: width/68,
        //     ticks: 68,
        //     tickFormat: format
        // } );

        // var y_axis = new Rickshaw.Graph.Axis.Y( {
        //     graph: graph,
        //     orientation: 'left',
        //     tickFormat: Rickshaw.Fixtures.Number.formatKMBT,
        //     element: document.getElementById('y_axis')
        // } );
    },
    series: [
        {
            color: "rgba(70,130,180,0.5)",
            name: selected_long_name
        }
    ]
} );