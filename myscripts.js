function testFunction(){

    //document.getElementById('blocker').style.display='block';
    let result= mapModule.calculateVDOP( parseFloat(document.getElementById('latitudeResolutionInput').value),
        parseFloat(document.getElementById('longitudeResolutionInput').value),
        parseFloat(document.getElementById('altitudeInput').value),
        document.getElementById('selectStationList').value,
        !document.getElementById('polygonCheckBox').checked,4)
    if (result!=null) document.getElementById('PanelVDOP').style.display = "block";

}
// onload

function GetMap()
{
    let map = new Microsoft.Maps.Map('#myMap')
    let checkbox = document.getElementById("polygonCheckBox");
    togglePolygon(checkbox);
    mapModule.setMap(map);
    mapModule.setOutputId('VDOPInput');
    mapModule.setClearFunction(restoreVisuals);
    mapModule.setBlockFunction(hideVisuals)
    createGradientDiv();



    //addEventToMap('Vertex');
    //Microsoft.Maps.Events.addHandler(map, 'click', function (e) { addNewStation(e); });
    //Add your post map load code here.
}

function createGradientDiv(){
    var motherDiv = document.getElementById('gradientDiv');
    var min = "00FF00";
    var half = "0000FF";
    var max = "FF0000";
    var colors = generateColor(half,min,15);
    colors = colors.concat(generateColor(max,half,15));
    console.log(colors,'kolory');
    for (let i=0;i<30;++i){
        let innerDiv = document.createElement('div');
        innerDiv.innerHTML = i+1;
        innerDiv.style.backgroundColor='#'+colors[i];
        innerDiv.style.float='left';
        innerDiv.style.width = '3%';
        innerDiv.style.textAlign = 'center';
        motherDiv.appendChild(innerDiv);
    }
    let innerDiv = document.createElement('div');
    //innerDiv.innerHTML = '31<';
    //innerDiv.style.backgroundColor='black';
    //innerDiv.style.color='white';
    //innerDiv.style.float='left';
    //innerDiv.style.width = '2.7%';
    //innerDiv.style.textAlign = 'center';
    //motherDiv.appendChild(innerDiv);
}

// button function

function stopComputation(){
   mapModule.stop();
}


function calculateVDOP(){
    let lat = document.getElementById('latitudeResolutionInput').value;
    let lon =document.getElementById('longitudeResolutionInput').value;
    let alt = document.getElementById('altitudeInput').value

    if (!doesArrayContainOnlyNumbers([lat,lon,alt])){
        alert('The inputs must be numeric');
        return null;
    }

    let result= mapModule.calculateVDOP( parseFloat(lat),
        parseFloat(lon),
        parseFloat(alt),
        document.getElementById('selectStationList').value,
        !document.getElementById('polygonCheckBox').checked,4)
    if (result!=null) document.getElementById('PanelVDOP').style.display = "block";

    //barDiv.style.display='none';

}

function addEventToMap(whichTable){
    //if (typeOfEvent==="Station") Microsoft.Maps.Events.addHandler(mapModule.getMap(), 'click', function (e) { addNewStation(e); });
    //if (typeOfEvent==="Vertex") Microsoft.Maps.Events.addHandler(mapModule.getMap(), 'click', function (e) { addNewVertex(e); });
    if (whichTable==="Station") mapModule.addHandlerMap('click', function (e) { addNewStation(e); });
    if (whichTable==="Vertex") mapModule.addHandlerMap('click', function (e) { addNewVertex(e); });
    if (whichTable==="Circle") mapModule.addHandlerMap('click', function (e) { addNewCircle(e); });
}

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
        if (!doesArrayContainOnlyNumbers([lat,lon])){
            alert('The inputs must be numeric');
            return null;
        }

        loc = new Microsoft.Maps.Location(lat,lon);
        //var alt = document.getElementById('altInputPopUp').value;
        // TO DO: add checking if it is a number
        //alt = parseFloat(alt);

    }
    mapModule.addVertex(loc,function (e) { changeVertexInTable(e); });
    var table = document.getElementById("vertexTable");
    var newRow = table.rows.length;

    var content = [newRow,lat,lon ] ;
    //console.log(content);
    addNewRowToTable("vertexTable",newRow,content,
    '<button type="button" onclick=editRowAndUpdateTable(this,"Vertex") class="buttonSkip fullWidth">Edit</button>',
        '<button type="button" onclick=deleteRowAndUpdateTable(this,"Vertex") class="buttonSkip fullWidth">Delete</button>',null);
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
    mapModule.addCircle(loc,2000,changeCircleInTable);
    var table = document.getElementById("circleOfInterest");
    var newRow = table.rows.length;

    var content = [lat,lon ,2000] ;
    //console.log(content);
    addNewRowToTable("circleOfInterest",newRow,content,
        '<button type="button" onclick=editRowAndUpdateTable(this,"Circle") class="buttonSkip fullWidth">Edit</button>',
        '<button type="button" onclick=deleteRowAndUpdateTable(this,"Circle") class="buttonSkip fullWidth">Delete</button>',null);
    hideMassageWindow('lat_lon_alt');
    if (newRow>2) table.rows[3].parentNode.removeChild(table.rows[2]);
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
        alt = parseFloat(alt);
        if (!doesArrayContainOnlyNumbers([lat,lon,alt])){
            alert('The inputs must be numeric');
            return null;
        }

        loc =new Microsoft.Maps.Location(lat,lon);
        // TO DO: add checking if it is a number



    }
    mapModule.addStation(loc,alt,changeStationInTable)
    var table = document.getElementById("stationTable");
    var newRow = table.rows.length;
    var content = [newRow,lat,lon,alt ,"Station"] ;
    addNewRowToTable("stationTable",newRow,content,
        '<button type="button" onclick=editRowAndUpdateTable(this,"station") class="buttonSkip fullWidth">Edit</button>',
        '<button type="button" onclick=deleteRowAndUpdateTable(this,"station") class="buttonSkip fullWidth">Delete</button>',
        '<input type="checkbox" onchange="changeStateofStation(this)" id="scales" name="scales" checked>');
    hideMassageWindow('lat_lon_alt');
    addStationToList();
}

function changeStateofStation(checker){
    var state = checker.checked;
    var row = checker.parentNode.parentNode;
    var index = row.cells[0].innerHTML-1;
    mapModule.changeStateOfStation(index,state);
    if (state) addStationToList();
    else removeStationFromList();
}

// table support functions

function addNewRowToTable(idOfTable,indexOfRow,content,buttonDescription,buttonDescription2,checkBoxDescription) {
    var table = document.getElementById(idOfTable);
    var row = table.insertRow(indexOfRow);
    var cell;
    for (var i = 0; i < content.length; ++i) {
        cell = row.insertCell(i);
        cell.innerHTML = content[i];
        cell.type = "number";
        if ((i>0)||(idOfTable==='circleOfInterest')) cell.contentEditable = true;
    }
    if (checkBoxDescription==null) {
        cell = row.insertCell(content.length);
        cell.innerHTML = buttonDescription;
        cell = row.insertCell(content.length + 1);
        cell.innerHTML = buttonDescription2;
    } else{
        cell = row.insertCell(content.length);
        cell.innerHTML = checkBoxDescription;
        cell = row.insertCell(content.length+1);
        cell.innerHTML = buttonDescription;
        cell = row.insertCell(content.length + 2);
        cell.innerHTML = buttonDescription2;
    }

}

function changeVertexInTable(e){
    var pin = e.target;
    var loc = pin.getLocation();
    var index = mapModule.getIndexOfVertex(pin);
    var table = document.getElementById("vertexTable");
    var row = table.rows[index+1];
    row.cells[1].innerHTML = loc.latitude;
    row.cells[2].innerHTML = loc.longitude;
}

function changeStationInTable(e){
    var pin = e.target;
    var loc = pin.getLocation();
    var index = mapModule.getIndexOfStation(pin);
    var table = document.getElementById("stationTable");
    var row = table.rows[index+1];
    row.cells[1].innerHTML = loc.latitude;
    row.cells[2].innerHTML = loc.longitude;
}

function changeCircleInTable(e){
    var pin = e.target;
    var loc = pin.getLocation();
    var table = document.getElementById("circleOfInterest");
    var row = table.rows[2];
    row.cells[0].innerHTML = loc.latitude;
    row.cells[1].innerHTML = loc.longitude;
}

function deleteRowAndUpdateTable(cell,where){

    var tableId = cell.parentNode.parentNode.parentNode.parentNode.id
    var table = document.getElementById(tableId);
    //console.log('tutaj')
    //console.log(cell.parentNode.parentNode.parentNode.parentNode)
    var row = cell.parentNode.parentNode
    //console.log(row)
    //console.log(table.rows)
    row.parentNode.removeChild(row);
    if (tableId === "circleOfInterest") {
        deletePin(null,tableId);
        return null;
    }
    // error -> need to find a way to get row and dleete it
    //row_index = table.rows.indexOf(row)
    //table.deleteRow(indexOfRow)
    var numberOfRows = table.rows.length;
    var flag = true;

    for (var i = 1;i<numberOfRows;++i)
    {
        cell = table.rows[i].cells[0];
        if ((flag) && (cell.innerHTML === (i+1))){
            flag = false;
            deletePin(i-1,tableId);
        }
        cell.innerHTML = i;

    }

    if (flag) deletePin(numberOfRows-1,tableId);
    if (where==='station') if (row.cells[5].firstChild.checked) removeStationFromList();
}

function editRowAndUpdateTable(cell){ //To Do

    var tableId = cell.parentNode.parentNode.parentNode.parentNode.id
    //console.log('tutaj')
    //console.log(cell.parentNode.parentNode.parentNode.parentNode)
    var row = cell.parentNode.parentNode;
    if (tableId==="circleOfInterest"){
        var lat = row.cells[0].innerHTML;
        var lon = row.cells[1].innerHTML;
        var radius = row.cells[2].innerHTML;
        if (!doesArrayContainOnlyNumbers([lat,lon,radius])){
            alert('The inputs must be numeric');
            return null;
        }

        var loc = new Microsoft.Maps.Location(parseFloat(lat),parseFloat(lon));
        mapModule.addCircle(loc,radius,changeCircleInTable);
        document.getElementById('PanelVDOP').style.display = "none";
        return null;
    }

    var index = row.cells[0].innerHTML-1;
    var lat = row.cells[1].innerHTML;
    var lon = row.cells[2].innerHTML;
    var alt = row.cells[3].innerHTML;
    if (!doesArrayContainOnlyNumbers([lat,lon,alt])){
        alert('The inputs must be numeric');
        return null;
    }
    var name = row.cells[4].innerHTML;
    //console.log(lat);
    var loc = new Microsoft.Maps.Location(parseFloat(lat),parseFloat(lon));
    editPin(loc,index,tableId,alt,name);


    //console.log(row)
    //console.log(table.rows)
    // error -> need to find a way to get row and dleete it
    //row_index = table.rows.indexOf(row)
    //table.deleteRow(indexOfRow)

}

// List support functions

function addStationToList(){
    var list= document.getElementById("selectStationList");
    var opt = document.createElement('option');
    opt.value = list.length;
    opt.innerHTML = list.length;
    list.appendChild(opt);
    if (list.length === 2) list.value=1;
}

function removeStationFromList(){
    var list= document.getElementById("selectStationList");
    list.remove(list.length-1);
}

// Pin functions

function deletePin(index,tableId){
    if (tableId==="stationTable") mapModule.deleteStation(index);
    if (tableId==="vertexTable") mapModule.deleteVertex(index);
    if (tableId==="circleOfInterest") {document.getElementById('PanelVDOP').style.display = "none";mapModule.deleteCircle();}

}

function editPin(loc,index,tableId,alt,name){
    if (tableId==="stationTable") mapModule.EditStation(loc,parseFloat(alt),index,name,changeStationInTable);
    if (tableId==="vertexTable") mapModule.EditVertex(loc,index,changeVertexInTable);

}

// visuals functions

function restoreVisuals(){
    document.getElementById('blocker').style.display='none';
    document.getElementById('stopButton').style.display='none';
}

function hideVisuals(){
    document.getElementById('blocker').style.display='block';
    document.getElementById('stopButton').style.display='block';
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

    if (whichButtonShow === "Vertex") showDiv("addVertexButton");
    else hideDiv("addVertexButton");
    if (whichButtonShow === "Station") showDiv("addStationButton");
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

function getLocalizationMeasurmentError(){

    var t_measurment_error = parseFloat(document.getElementById('stationMeasurmentErrorInput').value);

    var VDOP = parseFloat(document.getElementById('VDOPInput').value);

    var localization_error = t_measurment_error*VDOP*0.3;
    console.log(t_measurment_error,VDOP,localization_error);
    var out = document.getElementById('localizationMeasurmentErrorInput');
    out.value = localization_error.toString().slice(0,7);

}

function toggle(divId,button){
    //div = document.getElementById(divId);

    //if (div.style.display==="none") div.style.display="block";
    //else div.style.display="none";
    if (button.innerHTML.slice(button.innerHTML.length-4,button.innerHTML.length)==='hide') button.innerHTML = button.innerHTML.slice(0,button.innerHTML.length-4)+'show';
    else button.innerHTML = button.innerHTML.slice(0,button.innerHTML.length-4)+'hide';
    //console.log($('#'+divId).is(':visible'));
    $('#'+divId).slideToggle("slow");

}

function togglePolygon(checkBox){
    console.log(checkBox.checked)
    if (checkBox.checked){
        var button = document.getElementById("polygonShowingTableButton")
        button.innerHTML = button.innerHTML.slice(0,button.innerHTML.length-4)+'show';
        button = document.getElementById("circleShowingTableButton")
        button.innerHTML = button.innerHTML.slice(0,button.innerHTML.length-4)+'show';
        $('#'+"circleOfInterestDiv").slideUp("slow");
        $('#'+"circleOfInterestHideDiv").slideUp("slow");
        //$('#'+"polygonOfInterestDiv").slideDown("slow");
        $('#'+"polygonOfInterestHideButton").slideDown("slow");
        mapModule.vertexPolygonVisibility(true);
        mapModule.circlePolygonVisibility(false);
    } else {
        console.log('qwrerq')
        //$('#'+"circleOfInterestDiv").slideDown("slow");
        $('#'+"circleOfInterestHideDiv").slideDown("slow");
        $('#'+"polygonOfInterestDiv").slideUp("slow");
        $('#'+"polygonOfInterestHideButton").slideUp("slow");
        mapModule.vertexPolygonVisibility(false);
        mapModule.circlePolygonVisibility(true);
    }
}


// math functions

function doesArrayContainOnlyNumbers(arr){
    for (var i=0;i<arr.length;++i) if (isNaN(arr[i])) {console.log(i);return false;}
    console.log('tu');
    return true;
}


