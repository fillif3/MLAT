function GetMap()
{
    var map = new Microsoft.Maps.Map('#myMap');

        //Add your post map load code here.
}



function addNewVertex(){
    lat = document.getElementById('latInputPopUp').value
    // TO DO: add checking if it is a number
    var lat = parseFloat(lat);
    lon = document.getElementById('longInputPopUp').value
    // TO DO: add checking if it is a number
    var lon = parseFloat(lon);
    var table = document.getElementById("vertexTable");
    newRow = table.rows.length;

    var content = [newRow-1,lat,lon ] ;
    addNewRowToTable("vertexTable",newRow,content,
    '<button type="button" class="fullWidthButton">Delete Vertex clicking</button>');
    hideMassageWindow('lat_lon_alt');
}

function addNewStation(){
    var lat = document.getElementById('latInputPopUp').value
    // TO DO: add checking if it is a number
    lat = parseFloat(lat);
    var lon = document.getElementById('longInputPopUp').value
    // TO DO: add checking if it is a number
    lon = parseFloat(lon);
    var alt = document.getElementById('altInputPopUp').value
    // TO DO: add checking if it is a number
    alt = parseFloat(alt);
    var table = document.getElementById("vertexTable");
    newRow = table.rows.length;

    var content = [newRow-1,lat,lon,alt ] ;
    addNewRowToTable("stationTable",newRow,content,
    '<button type="button" class="fullWidthButton">Delete Staion clicking</button>');
    hideMassageWindow('lat_lon_alt');
}

function deleteRow(idOfTable,indexOfRow,buttonDescriptionPart1,buttonDescriptionPart2){

}


function addNewRowToTable(idOfTable,indexOfRow,content,buttonDescription) {
    var table = document.getElementById(idOfTable);
    var row = table.insertRow(indexOfRow);
    for (i = 0; i < content.length; ++i) {
      var cell = row.insertCell(i);
      cell.innerHTML = content[i];
    }
    var btn = document.createElement('input');
    btn.type = "button";
    btn.className = "btn";
    var cell = row.insertCell(content.length);
    cell.innerHTML = buttonDescription;

}

function hideDiv(divId)
{
    //console.log(divId)
    document.getElementById(divId).style.display = "none";

}

function showDiv(divId)
{

    console.log(divId)
    document.getElementById(divId).style.display = "block";

}

function showMassageWindow(whichControlsShow,whichButtonShow)
{
    console.log(whichControlsShow)

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

    if (whichDivsHide.includes("lat")) hideDiv("latInputPopUppDiv");
    if (whichDivsHide.includes("long")) hideDiv("longInputPopUppDiv");
    if (whichDivsHide.includes("alt")) hideDiv("altInputPopUppDiv");
    hideDiv('popUp');

}