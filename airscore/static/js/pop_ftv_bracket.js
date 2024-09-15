function populate_ftv_brackets(json){
    $('#comp_name').text('Loading Results ...');
    var taskNum = json.stats.valid_tasks
    console.log('taskNum='+taskNum);
    var columns = [];
    // rankings
    json.rankings.forEach( function(item, index) {
        columns.push({data: 'rankings.'+item.rank_id.toString(), title: '#', name: item.rank_id.toString(), className: "text-right", defaultContent: '', visible: (index === 0) ? true : false});
    });
    columns.push({data: 'ID', title:'ID', className: "text-right", defaultContent: ''});
    columns.push({data: 'fai_id', title:'FAI', className: "text-right", defaultContent: '', visible: false});
    columns.push({data: 'civl_id', title:'CIVL', className: "text-right", defaultContent: '', visible: false});
    columns.push({data: 'name', title:'Name'});
    columns.push({data: 'nat', title:'NAT', name:'NAT', defaultContent: ''});
    columns.push({data: 'sex', title:'Sex', defaultContent: '', visible: false});
    columns.push({data: 'glider', title:'Equip', defaultContent: '', visible: false});
    columns.push({data: 'glider_cert', title:'Class', defaultContent: '', visible: false});
    columns.push({data: 'sponsor', title:'Sponsor', defaultContent: '', visible: false});
    columns.push({data: 'max_score', title:'Max Score', className: "text-right"});
    columns.push({data: 'min_score', title:'Min Score', className: "text-right"});
    $('#results_table').DataTable( {
        data: json.results,
        paging: false,
        searching: true,
        saveState: true,
        info: false,
        dom: 'lrtip',
        columns: columns,
        rowId: function(data) {
            return 'id_' + data.par_id;
        },
        initComplete: function(settings) {
            var table = $('#results_table');
            var rows = $("tr", table).length-1;
            // Get number of all columns
            var numCols = table.DataTable().columns().nodes().length;
            console.log('numCols='+numCols);

            // comp info
            $('#comp_name').text(json.info.comp_name);
            $('#comp_date').text(json.info.date_from + ' - ' + json.info.date_to);
            if (json.info.comp_class != "PG") {
                update_classes(json.info.comp_class);
            }
            // description text
            let text = document.createTextNode('Score bracket applying FTV parameters to the overall results after a new fully valid task');
            $('#comp_header').append(text);

            // some GAP parameters
            $('#formula tbody').append(
                        "<tr><td>Director</td><td>" + json.info.MD_name + '</td></tr>' +
                        "<tr><td>Location</td><td>" + json.info.comp_site + '</td></tr>' +
                        "<tr><td>Formula</td><td>" + json.formula.formula_name + '</td></tr>' +
                        "<tr><td>Overall Scoring</td><td>" + json.formula.overall_validity + ' (' + json.formula.validity_param + ')</td></tr>');
            if (json.formula.overall_validity.toLowerCase() == 'ftv') {
                $('#formula tbody').append(
                        "<tr><td>Assumed Total Validity</td><td>" + json.stats.total_validity + ' (FTV validity ' + json.stats.avail_validity + ')</td></tr>');
            }
            // remove empty cols and NAT if all pilots are from a single country
            var natId = table.DataTable().column('NAT:name').index();
            var natRef = table.DataTable().column(natId).data()[0];
            for ( var col=1; col<numCols; col++ ) {
                var empty = true;
                table.DataTable().column(col).data().each( val => {
                    if (col == natId) {
                        if (val != natRef) {
                            empty = false;
                        }
                    }
                    else {
                        if (val != "") {
                            empty = false;
                        }
                    }
                    if (!empty) {
                        return false;
                    }
                } );

                if (empty) {
                    table.DataTable().column( col ).visible( false );
                }
            }

            // class picker
            $("#dhv option").remove(); // Remove all <option> child tags.
            // at the moment we provide the highest EN rating for a class and the overall_class_filter.js uses this.
            // if we want to be more specific and pass a list of all EN ratings inside a class we can do something like this: https://stackoverflow.com/questions/15759863/get-array-values-from-an-option-select-with-javascript-to-populate-text-fields
            console.log(json.rankings);
            $.each(json.rankings, function(index, item) {
                $("#dhv").append(
                    $("<option></option>")
                        .text(item.rank_name)
                        .val(item.rank_id)
                );
            });
        }
    });
}