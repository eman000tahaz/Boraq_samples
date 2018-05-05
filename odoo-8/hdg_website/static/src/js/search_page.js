function initialize() {
    var s = new openerp.Session();
    var project_model = new openerp.Model(s ,'project.project');
    project_model.call('get_address',[]).then(function (project) {
        var map;
        var geocoder;
        var marker;
        var latitude;
        var longitude;
        var mylat = [];
        var mylong = [];
        var mapProp = {
            mapTypeId:google.maps.MapTypeId.ROADMAP,
            center:new google.maps.LatLng(26.820553,30.802498),
            zoom:6,
            minZoom: 4,
             };
        map = new google.maps.Map(document.getElementById('map'), mapProp);
        var geocoder = new google.maps.Geocoder();
        var i = 0;
    var currentWindow = null;
    for(indx in project){
        var contentString = project[indx].name;
        geocoder.geocode({'address': project[indx].address} ,function(results, status) {
            if(status == google.maps.GeocoderStatus.OK) {
                var contentString = "<div><p class='text-center'>"+project[i].name+"</p><br/><img src='data:image/gif;base64,"+project[i].image+"' style='width:100px; height:70px;' class='center-block'/></div>";
                var infowindow = new google.maps.InfoWindow({
                    content : contentString,
                });
                marker = new google.maps.Marker({
                    position: results[0].geometry.location,
                    map: map
                 });
                marker.addListener('click', function() {
                    if (currentWindow != null){
                        currentWindow.close();
                    }
                    infowindow.open(map, this);
                    currentWindow = infowindow;
                });
                infowindow.addListener('closeclick', function(){
                    currentWindow = null;
                });
                console.log(project);
                console.log(project[i]);
                i+=1;
                }
            else {
                alert('Geocode was not successful for the following reason: ' + status);
                }
            });
        }
    });
}
google.maps.event.addDomListener(window, 'load', initialize);

/* show map view */
function map_view(){
    var list_view = document.getElementById("list_view");
    list_view.style.display = 'none';
    var map_view = document.getElementById("map_view");
    map_view.style.display = 'block';
    }
/* show list view */
function list_view(){
    var map_view = document.getElementById("map_view");
    map_view.style.display = 'none';
    var list_view = document.getElementById("list_view");
    list_view.style.display = 'block';
    }
/* Pagination */
/* Note : look  at saved page to get html code */

var paginationHandler = function(){
    // store pagination container so we only select it once
    var $paginationContainer = $(".pagination-container"),
        $pagination = $paginationContainer.find('.pagination ul');
    // click event
    $pagination.find("li a").on('click.pageChange',function(e){
        e.preventDefault();

        // get parent li's data-page attribute and current page
        var parentLiPage = $(this).parent('li').data("page"),
            currentPage = parseInt( $(".pagination-container div[data-page]:visible").data('page') ),
            numPages = $paginationContainer.find("div[data-page]").length;

        // make sure they aren't clicking the current page
        if ( parseInt(parentLiPage) !== parseInt(currentPage) ) {
            // hide the current page
            $paginationContainer.find("div[data-page]:visible").hide();

            if ( parentLiPage === '+' ) {
                // next page
                $paginationContainer.find("div[data-page="+( currentPage+1>numPages ? numPages : currentPage+1 )+"]").show();
            } else if ( parentLiPage === '-' ) {
                // previous page
                $paginationContainer.find("div[data-page="+( currentPage-1<1 ? 1 : currentPage-1 )+"]").show();
            } else {
                // specific page
                $paginationContainer.find("div[data-page="+parseInt(parentLiPage)+"]").show();
            }

        }
    });
};
$( document ).ready( paginationHandler );


