
function testFunction(test){
    var A=[[1,2],[3,4]];
    var B=[[1,2],[3,4]];
    var result=math.multiply(A,B);
    console.log(result);
    alert("This is test box!");
}
function GetMap()
{
    var map = new Microsoft.Maps.Map('#myMap')

    mapModule.setMap(map);
    mapModule.setOutputId('VDOPInput');


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
    if (whichTable==="Station") mapModule.addHandlerMap('click', function (e) { addNewStation(e); });
    if (whichTable==="Vertex") mapModule.addHandlerMap('click', function (e) { addNewVertex(e); });
    if (whichTable==="Circle") mapModule.addHandlerMap('click', function (e) { addNewCircle(e); });
}

//function addEventToInput(whichTable){
    //if (typeOfEvent==="Station") Microsoft.Maps.Events.addHandler(mapModule.getMap(), 'click', function (e) { addNewStation(e); });
    //if (typeOfEvent==="Vertex") Microsoft.Maps.Events.addHandler(mapModule.getMap(), 'click', function (e) { addNewVertex(e); });
//    if (whichTable==="Station") mapModule.addHandler('click', function (e) { addNewStation(e); });
//    if (whichTable==="Vertex") mapModule.addHandler('click', function (e) { addNewVertex(e); });
//    if (whichTable==="Circle") mapModule.addHandler('click', function (e) { addNewCircle(e); });
//}



function addNewVertex(e){
    if (e != null) {
        var point = new Microsoft.Maps.Point(e.getX(), e.getY());
        var loc = e.target.tryPixelToLocation(point);

        //var location = new Microsoft.Maps.Location(loc.latitude, loc.longitude);
        //console.log(loc.latitude.toString().slice(0,7));
        var lat = loc.latitude.toString().slice(0,7);
        var lon = loc.longitude.toString().slice(0,7);
        //mapModule.deleteHandler('click');
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

function addNewCircle(e){
    if (e != null) {
        var point = new Microsoft.Maps.Point(e.getX(), e.getY());
        var loc = e.target.tryPixelToLocation(point);

        //var location = new Microsoft.Maps.Location(loc.latitude, loc.longitude);
        //console.log(loc.latitude.toString().slice(0,7));
        var lat = loc.latitude.toString().slice(0,7);
        var lon = loc.longitude.toString().slice(0,7);
        mapModule.deleteHandler('click');
        document.getElementById('PanelVDOP').style.display = "none";
        //mapModule.deleteHandler('click');
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
    mapModule.addCircle(loc,2000);
    var table = document.getElementById("circleOfInterest");
    var newRow = table.rows.length;

    var content = [lat,lon ,2000] ;
    //console.log(content);
    addNewRowToTable("circleOfInterest",newRow,content,
        '<button type="button" onclick=editRowAndUpdateTable(this) class="fullWidthButton">Edit Vertex clicking</button>',
        '<button type="button" onclick=deleteRowAndUpdateTable(this) class="fullWidthButton">Delete Vertex clicking</button>');
    hideMassageWindow('lat_lon_alt');
    if (newRow>3) table.rows[4].parentNode.removeChild(table.rows[3]);
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
    mapModule.addStation(loc,alt)
    var table = document.getElementById("stationTable");
    var newRow = table.rows.length;
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
    var row = cell.parentNode.parentNode
    //console.log(row)
    //console.log(table.rows)
    row.parentNode.removeChild(row);
    // error -> need to find a way to get row and dleete it
    //row_index = table.rows.indexOf(row)
    //table.deleteRow(indexOfRow)
    var numberOfRows = table.rows.length;
    var flag = true;
    for (var i = 2;i<numberOfRows;++i)
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
    if (tableId=="circleOfInterest"){
        var lat = row.cells[0].innerHTML;
        var lon = row.cells[1].innerHTML;
        var radius = row.cells[2].innerHTML;
        var loc = new Microsoft.Maps.Location(parseFloat(lat),parseFloat(lon));
        mapModule.addCircle(loc,radius);
        document.getElementById('PanelVDOP').style.display = "none";
        return null;
    }

    var index = row.cells[0].innerHTML-1;
    var lat = row.cells[1].innerHTML;
    var lon = row.cells[2].innerHTML;
    var alt = row.cells[3].innerHTML;
    //console.log(lat);
    var loc = new Microsoft.Maps.Location(parseFloat(lat),parseFloat(lon));
    editPin(loc,index,tableId,alt);


    //console.log(row)
    //console.log(table.rows)
    // error -> need to find a way to get row and dleete it
    //row_index = table.rows.indexOf(row)
    //table.deleteRow(indexOfRow)

}

function deletePin(index,tableId){
    if (tableId=="stationTable") mapModule.deleteStation(index);
    if (tableId=="vertexTable") mapModule.deleteVertex(index);
    if (tableId=="circleOfInterest") {document.getElementById('PanelVDOP').style.display = "none";mapModule.deleteCircle();}

}

function editPin(loc,index,tableId,alt){
    if (tableId=="stationTable") mapModule.EditStation(loc,parseFloat(alt),index);
    if (tableId=="vertexTable") mapModule.EditVertex(loc,index);

}

function calculateVDOP(){
    var result=mapModule.calculateVDOP( parseFloat(document.getElementById('latitudeResolutionInput').value),
        parseFloat(document.getElementById('longitudeResolutionInput').value),
            parseFloat(document.getElementById('altitudeInput').value),0,true);
    if (result!=null) document.getElementById('PanelVDOP').style.display = "block";
}

function addNewRowToTable(idOfTable,indexOfRow,content,buttonDescription,buttonDescription2) {
    var table = document.getElementById(idOfTable);
    var row = table.insertRow(indexOfRow);
    for (var i = 0; i < content.length; ++i) {
      var cell = row.insertCell(i);
      cell.innerHTML = content[i];
      if ((i>0)||(idOfTable=='circleOfInterest')) cell.contentEditable = true;
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

function getLocalizationMeasurmentError(cell){

    var t_measurment_error = parseFloat(document.getElementById('stationMeasurmentErrorInput').value);

    var VDOP = parseFloat(document.getElementById('VDOPInput').value);

    var localization_error = t_measurment_error*VDOP*0.3;
    console.log(t_measurment_error,VDOP,localization_error);
    var out = document.getElementById('localizationMeasurmentErrorInput');
    out.value = localization_error;

}