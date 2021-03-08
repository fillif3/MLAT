//MAP_REFERENCE = '';

var mapModule = (function() {
    'use strict';

    var _MAP_REFERENCE = '';
    var _handlers = new Map();
    var _stationArray =[];
    var _vertexArray=[];
    var _vertexPolygon = null;
    var _VDOPPixels = []

    function calculateVDOP(latitudePrecision,longitudePrecision,altitude,base_station){
        _clearVDOP();
        //if (_stationArray.length<3) return null;
        if (_vertexArray.length<3) return null;
        var edges = _getPolygonEdgeValues();
        var currentLatitude= edges.get('min_latitude');
        while (currentLatitude<edges.get('max_latitude')){
            var currentLongitude= edges.get('min_longitude');
            while (currentLongitude<edges.get('max_longitude')){
                var locationArray = _getPixelLocationArray(currentLatitude,currentLongitude,latitudePrecision,longitudePrecision);

                if (_checkIfPointInsidePolygon(currentLatitude,currentLongitude,locationArray)){

                    var pixel = new Microsoft.Maps.Polygon(locationArray,{strokeThickness:0});
                    _MAP_REFERENCE.entities.push(pixel);
                    _VDOPPixels.push(pixel);
                }
                currentLongitude+=longitudePrecision;
            }
            currentLatitude+=latitudePrecision;
        }
    }

    function _clearVDOP(){

        for (var i=0;i<_VDOPPixels.length;++i){
            _MAP_REFERENCE.entities.remove(_VDOPPixels[i]);
        }
        _VDOPPixels=[];
    }

    function _getPixelLocationArray(latitude,longitude,latitudePrecision,longitudePrecision){
        var locationsArray=[]
        var loc = new Microsoft.Maps.Location(latitude-0.5*latitudePrecision,longitude-0.5*longitudePrecision);
        locationsArray.push(loc);
        loc = new Microsoft.Maps.Location(latitude+0.5*latitudePrecision,longitude-0.5*longitudePrecision);
        locationsArray.push(loc);
        loc = new Microsoft.Maps.Location(latitude+0.5*latitudePrecision,longitude+0.5*longitudePrecision);
        locationsArray.push(loc);
        loc = new Microsoft.Maps.Location(latitude-0.5*latitudePrecision,longitude+0.5*longitudePrecision);
        locationsArray.push(loc);

        //console.log(locationsArray);
        return locationsArray;
    }

    function _checkIfPointInsidePolygon(latitude,longitude){
        var locationArray = _vertexPolygon.getLocations();
        //console.log(locationArray);
        var numberOfIntersections=0;
        for (var i=1;i<locationArray.length;++i){
            var maxY = Math.max(locationArray[i-1].longitude,locationArray[i].longitude)
            var minY = Math.min(locationArray[i-1].longitude,locationArray[i].longitude)
            if ((longitude>minY)&&(longitude<maxY)){
                //console.log('---------');
                //console.log(longitude);
                //console.log(locationArray[i-1].longitude);
                //console.log(locationArray[i].longitude);
                var firstPartOfLine = Math.abs(locationArray[i-1].longitude-longitude)
                var secondPartOfLine = Math.abs(locationArray[i].longitude-longitude)
                var division = firstPartOfLine/(firstPartOfLine+secondPartOfLine);
                var xPoint = locationArray[i-1].latitude+division*(locationArray[i].latitude- locationArray[i-1].latitude);
                if (xPoint<latitude) numberOfIntersections++;
            }
        }
        if (numberOfIntersections>0) {
            //console.log(numberOfIntersections);
            //console.log(numberOfIntersections % 2 == 1)
        }
        return numberOfIntersections%2==1;
    }

    function _getPolygonEdgeValues(){
        if (_vertexPolygon == null) return null;

        var locations = _vertexPolygon.getLocations();

        //await sleep(2000);
        var edges = new Map();
        edges.set('min_latitude',locations[0].latitude);
        edges.set('max_latitude',locations[0].latitude);
        edges.set('min_longitude',locations[0].longitude);
        edges.set('max_longitude',locations[0].longitude);
        for (i=1;i<(locations.length-1);++i){
            if (edges.get('min_latitude')>locations[i].latitude) edges.set('min_latitude',locations[i].latitude);
            if (edges.get('max_latitude')<locations[i].latitude) edges.set('max_latitude',locations[i].latitude);
            if (edges.get('min_longitude')>locations[i].longitude) edges.set('min_longitude',locations[i].longitude);
            if (edges.get('max_longitude')<locations[i].longitude) edges.set('max_longitude',locations[i].longitude);
        }
        return edges;
    }

    function _updateVertexPolygon(){
        if (_vertexPolygon!=null) _MAP_REFERENCE.entities.remove(_vertexPolygon);
        if (_vertexArray.length>2) {
            var locationArray = getLocationArrayFromPinArray(_vertexArray);
            var polygon = new Microsoft.Maps.Polygon(locationArray,{fillColor:'white'});
            _MAP_REFERENCE.entities.push(polygon);
            _vertexPolygon = polygon
        } else _vertexPolygon=null;

    }

    function getLocationArrayFromPinArray(pinArray){
        var retArr = [];
        for (i=0;i<pinArray.length;++i)
        {
            var pin = pinArray[i];
            retArr.push(pin.getLocation());
        }
        return retArr;

    }

    function EditStation(loc,index){
        var newPin = new Microsoft.Maps.Pushpin(loc, {
            title: 'Station',
            // subTitle: number.toString()
        });
        _MAP_REFERENCE.entities.push(newPin);
        var oldPin = _stationArray[index];
        _MAP_REFERENCE.entities.remove(oldPin);
        _stationArray.splice(index,1,newPin);

    }

    function addStation(loc){
        //var number = _vertexArray.length+1
        var pin = new Microsoft.Maps.Pushpin(loc, {
            title: 'Station',
           // subTitle: number.toString()
        });
        _MAP_REFERENCE.entities.push(pin);
        _stationArray.push(pin);
    }

    function deleteStation(index){
        var pin = _stationArray[index];
        _stationArray.splice(index,1)
        _MAP_REFERENCE.entities.remove(pin);
    }

    function EditVertex(loc,index){
        var newPin = new Microsoft.Maps.Pushpin(loc, {
            title: 'Vertex',
            // subTitle: number.toString()
        });
        _MAP_REFERENCE.entities.push(newPin);
        var oldPin = _vertexArray[index];
        _MAP_REFERENCE.entities.remove(oldPin);
        _vertexArray.splice(index,1,newPin);
        _updateVertexPolygon();
    }

    function addVertex(loc){
        //var number = _vertexArray.length+1
        var pin = new Microsoft.Maps.Pushpin(loc, {
            title: 'Vertex',
            // subTitle: number.toString()
        });
        _MAP_REFERENCE.entities.push(pin);
        _vertexArray.push(pin);
        //console.log(_vertexArray);
        _updateVertexPolygon();
    }

    function deleteVertex(index){
        var pin = _vertexArray[index];
        _vertexArray.splice(index,1)
        _MAP_REFERENCE.entities.remove(pin);
        _updateVertexPolygon();
    }

    function setMap(reference) {
        //console.log(reference);
        _MAP_REFERENCE = reference;
    }

    function addHandler(typeOfEvent,func) {
        deleteHandler(typeOfEvent);
        var referenceToHandler = Microsoft.Maps.Events.addHandler(_MAP_REFERENCE,typeOfEvent, func );
        //console.log(reference);
        _handlers.set(typeOfEvent,referenceToHandler);
    }

    function deleteHandler(typeOfEvent){
        if (_handlers.get(typeOfEvent)!=null){
            Microsoft.Maps.Events.removeHandler(_handlers.get(typeOfEvent));
            _handlers.delete(typeOfEvent);
        }
    }


    function getMap() {
        //console.log(reference);
        return _MAP_REFERENCE;
    }

    return {
        addVertex:addVertex,
        setMap: setMap,
        getMap: getMap,
        EditStation:EditStation,
        EditVertex:EditVertex,
        addStation:addStation,
        deleteStation:deleteStation,
        deleteVertex:deleteVertex,
        addHandler: addHandler,
        deleteHandler:deleteHandler,
        calculateVDOP:calculateVDOP
    };
})();


function GetMap()
{
    map = new Microsoft.Maps.Map('#myMap')

    mapModule.setMap(map);


    //addEventToMap('Vertex');
    //Microsoft.Maps.Events.addHandler(map, 'click', function (e) { addNewStation(e); });
        //Add your post map load code here.
}

/*if (!Array.prototype.indexOf)
{
  Array.prototype.indexOf = function(elt /*, from*//*)
  {
    var len = this.length;

    var from = Number(arguments[1]) || 0;
    from = (from < 0)
         ? Math.ceil(from)
         : Math.floor(from);
    if (from < 0)
      from += len;

    for (; from < len; from++)
    {
      if (from in this &&
          this[from] === elt)
        return from;
    }
    return -1;
  };
}*/

//function calculateVDOP(latitudePrecision,longitudePrecision,altitude,base_station){
//    mapModule.calculateVDOP(latitudePrecision,longitudePrecision,altitude,base_station);
//}

function addEventToMap(whichTable){
    //if (typeOfEvent==="Station") Microsoft.Maps.Events.addHandler(mapModule.getMap(), 'click', function (e) { addNewStation(e); });
    //if (typeOfEvent==="Vertex") Microsoft.Maps.Events.addHandler(mapModule.getMap(), 'click', function (e) { addNewVertex(e); });
    if (whichTable==="Station") mapModule.addHandler('click', function (e) { addNewStation(e); });
    if (whichTable==="Vertex") mapModule.addHandler('click', function (e) { addNewVertex(e); });
}



function addNewVertex(e){
    if (e != null) {
        var point = new Microsoft.Maps.Point(e.getX(), e.getY());
        var loc = e.target.tryPixelToLocation(point);

        //var location = new Microsoft.Maps.Location(loc.latitude, loc.longitude);
        console.log(loc.latitude.toString().slice(0,7));
        var lat = loc.latitude.toString().slice(0,7);
        var lon = loc.longitude.toString().slice(0,7);
        mapModule.deleteHandler('click');
        //var alt = document.getElementById('altInputPopUp').value;
    }
    else {
        var lat = document.getElementById('latInputPopUp').value;
        // TO DO: add checking if it is a number
        lat = parseFloat(lat);
        var lon = document.getElementById('longInputPopUp').value;
        // TO DO: add checking if it is a number
        lon = parseFloat(lon);
        loc = new Microsoft.Maps.Location(lat,lon);
        //var alt = document.getElementById('altInputPopUp').value;
        // TO DO: add checking if it is a number
        //alt = parseFloat(alt);

    }
    mapModule.addVertex(loc);
    var table = document.getElementById("vertexTable");
    var newRow = table.rows.length;

    var content = [newRow-1,lat,lon ] ;
    //console.log(content);
    addNewRowToTable("vertexTable",newRow,content,
    '<button type="button" onclick=editRowAndUpdateTable(this) class="fullWidthButton">Edit Vertex clicking</button>',
        '<button type="button" onclick=deleteRowAndUpdateTable(this) class="fullWidthButton">Delete Vertex clicking</button>');
    hideMassageWindow('lat_lon_alt');
}

function addNewStation(e){
    if (e != null) {
        var point = new Microsoft.Maps.Point(e.getX(), e.getY());
        var loc = e.target.tryPixelToLocation(point);

        //var location = new Microsoft.Maps.Location(loc.latitude, loc.longitude);
        //console.log(loc.latitude.toString().slice(0,7));
        var lat = loc.latitude.toString().slice(0,7);
        var lon = loc.longitude.toString().slice(0,7);

        var alt = 0;//document.getElementById('altInputPopUp').value;
        mapModule.deleteHandler('click');
    }
    else {
        var lat = document.getElementById('latInputPopUp').value;
        // TO DO: add checking if it is a number
        lat = parseFloat(lat);
        var lon = document.getElementById('longInputPopUp').value;
        // TO DO: add checking if it is a number
        lon = parseFloat(lon);
        var alt = document.getElementById('altInputPopUp').value;
        loc =new Microsoft.Maps.Location(lat,lon);
        // TO DO: add checking if it is a number
        alt = parseFloat(alt);

    }
    mapModule.addStation(loc)
    var table = document.getElementById("stationTable");
    newRow = table.rows.length;
    var content = [newRow-1,lat,lon,alt ] ;
    addNewRowToTable("stationTable",newRow,content,
    '<button type="button" onclick=editRowAndUpdateTable(this) class="fullWidthButton">Edit Station clicking</button>',
        '<button type="button" onclick=deleteRowAndUpdateTable(this) class="fullWidthButton">Delete Station clicking</button>');
    hideMassageWindow('lat_lon_alt');
}

function deleteRowAndUpdateTable(cell){

    var tableId = cell.parentNode.parentNode.parentNode.parentNode.id
    var table = document.getElementById(tableId);
    //console.log('tutaj')
    //console.log(cell.parentNode.parentNode.parentNode.parentNode)
    row = cell.parentNode.parentNode
    //console.log(row)
    //console.log(table.rows)
    row.parentNode.removeChild(row);
    // error -> need to find a way to get row and dleete it
    //row_index = table.rows.indexOf(row)
    //table.deleteRow(indexOfRow)
    var numberOfRows = table.rows.length;
    var flag = true;
    for (i = 2;i<numberOfRows;++i)
    {
        var cell = table.rows[i].cells[0];
        if ((flag) && (cell.innerHTML == (i))){
            flag = false;
            deletePin(i-2,tableId);
        }
        cell.innerHTML = i-1;

    }

    if (flag) deletePin(numberOfRows-2,tableId);
}

function editRowAndUpdateTable(cell){ //To Do

    var tableId = cell.parentNode.parentNode.parentNode.parentNode.id
    //console.log('tutaj')
    //console.log(cell.parentNode.parentNode.parentNode.parentNode)
    var row = cell.parentNode.parentNode;
    var index = row.cells[0].innerHTML-1;
    var lat = row.cells[1].innerHTML;
    var lon = row.cells[2].innerHTML;
    console.log(lat);
    var loc = new Microsoft.Maps.Location(parseFloat(lat),parseFloat(lon));
    editPin(loc,index,tableId);


    //console.log(row)
    //console.log(table.rows)
    // error -> need to find a way to get row and dleete it
    //row_index = table.rows.indexOf(row)
    //table.deleteRow(indexOfRow)

}

function deletePin(index,tableId){
    if (tableId=="stationTable") mapModule.deleteStation(index);
    if (tableId=="vertexTable") mapModule.deleteVertex(index);

}

function editPin(loc,index,tableId){
    if (tableId=="stationTable") mapModule.EditStation(loc,index);
    if (tableId=="vertexTable") mapModule.EditVertex(loc,index);

}



function addNewRowToTable(idOfTable,indexOfRow,content,buttonDescription,buttonDescription2) {
    var table = document.getElementById(idOfTable);
    var row = table.insertRow(indexOfRow);
    for (i = 0; i < content.length; ++i) {
      var cell = row.insertCell(i);
      cell.innerHTML = content[i];
      if (i>0) cell.contentEditable = true;
    }
    var cell = row.insertCell(content.length);
    cell.innerHTML = buttonDescription;
    cell = row.insertCell(content.length+1);
    cell.innerHTML = buttonDescription2;

}

function hideDiv(divId)
{
    //console.log(divId)
    document.getElementById(divId).style.display = "none";

}

function showDiv(divId)
{

    //console.log(divId)
    document.getElementById(divId).style.display = "block";

}

function showMassageWindow(whichControlsShow,whichButtonShow)
{
    //console.log(whichControlsShow)

    if (whichButtonShow == "Vertex") showDiv("addVertexButton");
    else hideDiv("addVertexButton");
    if (whichButtonShow == "Station") showDiv("addStationButton");
    else hideDiv("addStationButton");

    if (whichControlsShow.includes("lat")) showDiv("latInputPopUpDiv");
    else hideDiv("latInputPopUpDiv");
    if (whichControlsShow.includes("long")) showDiv("longInputPopUpDiv");
    else hideDiv("longInputPopUpDiv");
    if (whichControlsShow.includes("alt")) showDiv("altInputPopUpDiv");
    else hideDiv("altInputPopUpDiv");
    showDiv('popUp');

}

function hideMassageWindow(whichDivsHide)
{
    //console.log('1')

    if (whichDivsHide.includes("lat")) hideDiv("latInputPopUpDiv");
    if (whichDivsHide.includes("long")) hideDiv("longInputPopUpDiv");
    if (whichDivsHide.includes("alt")) hideDiv("altInputPopUpDiv");
    hideDiv('popUp');

}