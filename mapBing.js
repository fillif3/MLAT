
var mapModule = (function() {
    'use strict';

    const _semimajor_axis = 6378137.0;
    const _semiminor_axis = 6356752.31424518
    //const _flattening = (_semimajor_axis - _semiminor_axis) / _semimajor_axis;
    //const _thirdflattening = (_semimajor_axis - _semiminor_axis) / (_semimajor_axis + _semiminor_axis);
    //const _eccentricity = Math.sqrt(2 * _flattening - _flattening **2);
    const _meter_per_lat = 111320;


    var _MAP_REFERENCE = '';
    var _handlers = new Map();
    var _stationArray =[];
    var _stationAltitudeArray=[];
    var _ifStationActive=[]
    var _vertexArray=[];
    var _vertexPolygon = null;
    var _VDOPPixels = [];
    var _VDOPValues = [];
    var _circleRadius=0;
    var _circlePin=null;
    var _circlePolygon=null;
    var _outputId='';

    function setOutputId(val){

        _outputId=val;
        //console.log(_outputId);
        //throw 'qweqwe';
    }

    // Geometry transformations between coordiates - Start

    function _geodetic2ecef(latitude,longitude,alt){
        if (Math.abs(latitude)>90) return [null,null,null];
        var latitudeRadians = _degrees_to_radians(latitude);
        var longitudeRadians = _degrees_to_radians(longitude);
        // radius of curvature of the prime vertical section
        var N = _semimajor_axis ** 2 / Math.sqrt(
            _semimajor_axis ** 2 * Math.cos(latitudeRadians) ** 2 + _semiminor_axis ** 2 * Math.sin(latitudeRadians) ** 2
        );
        // Compute cartesian (geocentric) coordinates given  (curvilinear) geodetic
        // coordinates.
        var x = (N + alt) * Math.cos(latitudeRadians) * Math.cos(longitudeRadians);
        var y = (N + alt) * Math.cos(latitudeRadians) * Math.sin(longitudeRadians);
        var z = (N * (_semiminor_axis / _semimajor_axis) ** 2 + alt) * Math.sin(latitudeRadians)
        return [x,y,z];
    }

    function _uvw2enu(u, v, w, lat0, lon0){
        if (Math.abs(lat0)>90) return [null,null,null];
        lat0 = _degrees_to_radians(lat0);
        lon0 = _degrees_to_radians(lon0);
        var t = Math.cos(lon0) * u + Math.sin(lon0) * v;
        var East = -Math.sin(lon0) * u + Math.cos(lon0) * v;
        var Up = Math.cos(lat0) * t + Math.sin(lat0) * w
        var North = -Math.sin(lat0) * t + Math.cos(lat0) * w
        return [East,North,Up];
    }

    function _geodetic2enu(lat, lon, h, lat0, lon0, h0){
        var [x1, y1, z1] = _geodetic2ecef(lat, lon, h);
        var [x2, y2, z2] = _geodetic2ecef(lat0, lon0, h0);
        var [east,north,up] = _uvw2enu(x1-x2, y1-y2, z1-z2, lat0, lon0);
        return [east,north,up];
    }

    function _degrees_to_radians(degrees)
    {
        var pi = Math.PI;
        return degrees * (pi/180);
    }

    // Jacobian functions

    function _compute_Q(size){
        return math.add(math.identity(size),math.ones(size,size));
    }

    function _create_array2D(size1,size2){
        var arr=[];
        //console.log(arr);
        //throw "koniec";
        //console.log('-------');
        for (var i=0;i<size1;++i){
            //console.log(arr);
            var arrHelper=[];
            for (var j=0;j<size2;++j){
                arrHelper.push(0);

            }
            arr.push(arrHelper);

        }
        return arr;
    }

    function _computeJacobian2dot5D(anchors,position){

        var jacobian = _create_array2D(anchors.length-1,2);
        //console.log('-------');
        //console.log(anchors,'anchors');
        //console.log(jacobian);
        //console.log(position,'position');
        //console.log(math.subset(anchors,math.index(0, [0, 1,2])))
        //console.log(math.subtract(position,math.subset(anchors,math.index(0, [0, 1,2]))[0]))
        var distToReference = math.norm(math.subtract(position,math.subset(anchors,math.index(0, [0, 1,2]))[0]));
        //console.log(distToReference,'distToReference');
        //refence_derievative = (position[0:2] - anchors[-1][0:2]) / dist_to_refernce
        //console.log(math.subset(position,math.index([0, 1])));
        //console.log(math.subset(anchors,math.index(0, [0, 1]))[0]);
        var refence_derievative = math.multiply(math.subtract(math.subset(position,math.index([0, 1])),
            math.subset(anchors,math.index(0, [0, 1]))[0]),1/distToReference);
        //console.log(refence_derievative,'refence_derievative');
        //console.log(refence_derievative);
        for (var i=0;i<(anchors.length-1);++i){
            //console.log(i);

            var distToCurrent = math.norm(math.subtract(position,math.subset(anchors,math.index(i+1, [0, 1,2]))[0]));
            //console.log();
            //console.log()
            var gradient = math.multiply(math.subtract(math.subset(position,math.index([0, 1])),
                math.subset(anchors,math.index(i+1, [0, 1]))[0]),1/distToCurrent);
            //console.log(JSON.parse(JSON.stringify(distToCurrent)),'distToCurrent');
            //console.log(JSON.parse(JSON.stringify(gradient)),'gradient');
            jacobian[i][0]=gradient[0]-refence_derievative[0];
            jacobian[i][1]=gradient[1]-refence_derievative[1];
            //console.log(jacobian);
            //console.log(gradient);
            //throw "koniec";

        }
        //console.log(anchors,position);
        //console.log(jacobian);
        //throw "koniec";
        return jacobian;
    }

    // Computing VDOP

    function _computeSingleVDOP(anchors,position,base){
        if (base===-1){
            var new_bases = [];
            for (let i=0;i<anchors.length;i++){
                new_bases.push(i);
            }

        } else {var new_bases = [base];}

        var minVDOP = Number.MAX_VALUE;

        for (let i=0;i<new_bases.length;i++) {

            var helper = JSON.parse(JSON.stringify(anchors[new_bases[i]]));
            anchors[new_bases[i]]=JSON.parse(JSON.stringify(anchors[0]));
            anchors[0]=helper;

            //console.log(new_bases);
            //console.log(anchors);
            //throw 'koniec';
            //console.log(anchors);
            //console.log(position);
            var Jacobian = _computeJacobian2dot5D(anchors, position);
            //console.log(Jacobian);
            var Q = _compute_Q(anchors.length - 1);
            //console.log(Q,'Q');
            //try{
            //console.log(anchors)
            //console.log(position)
            try {
                var transposed_Jacobian = math.transpose(Jacobian);
                //console.log(JSON.parse(JSON.stringify(transposed_Jacobian)),'transposed_Jacobian');
                var equation = math.multiply(transposed_Jacobian, Jacobian);//np.dot(tran_J,J)
                //console.log(JSON.parse(JSON.stringify(equation)),'eq2');
                equation = math.inv(equation);//np.linalg.inv(equation)
                //console.log(JSON.parse(JSON.stringify(equation)),'eq3');
                equation = math.multiply(equation, transposed_Jacobian);//np.dot(equation,tran_J)
                //console.log(JSON.parse(JSON.stringify(equation)),'eq4');
                equation = math.multiply(equation, Q);//np.dot(equation, Q)
                //console.log(JSON.parse(JSON.stringify(equation)),'eq5');
                equation = math.multiply(equation, Jacobian);//np.dot(equation, J)
                //console.log(JSON.parse(JSON.stringify(equation)),'eq6');
                equation = math.multiply(equation, math.inv(math.multiply(transposed_Jacobian, Jacobian)));//np.dot(equation, np.linalg.inv(np.dot(tran_J,J)))
                //console.log(JSON.parse(JSON.stringify(equation)),'eq7');
                //throw "koniec";
                //equation = Math.sqrt(equation._data[0][0]+equation._data[1][1]);
                //console.log(JSON.parse(JSON.stringify(equation)),'eq7');
                //throw "koniec";
                let out = Math.sqrt(equation._data[0][0] + equation._data[1][1]);
                if (out < minVDOP) minVDOP = out;

            }
                //}
            catch (e) {
                //continue;
            }
        }
        return minVDOP;
    }


    function _computeColorBasedOnVDOP(currentLatitude,currentLongitude,altitude,base_station,newStationArray){
        var position = [0,0,0];
        var anchors=[];
        for (var i=0;i<newStationArray.length;++i){
            var loc = newStationArray[i].getLocation();
            //throw 'Parameter is not a number!';
            anchors.push(_geodetic2enu(loc.latitude,loc.longitude,_stationAltitudeArray[i],currentLatitude,currentLongitude,altitude));
        }

        var VDOP = _computeSingleVDOP(anchors,position,base_station);
        _VDOPValues.push(VDOP);
        return _getColor(VDOP);

    }

    function calculateVDOP(lat_res,lon_res,altitude,base_station,isCircle){
        _clearVDOP();


        base_station--;
        var newStationArray = [];
        if (_ifStationActive!=null){
            for (var i=0;i<_ifStationActive.length;++i){
                if (_ifStationActive[i]) newStationArray.push(_stationArray[i]);
            }
        } else newStationArray = _stationArray;
        //alert(newStationArray.length)



        if (newStationArray.length<3) return null;
        if ((_vertexArray.length<3)&&(!isCircle)) return null;
        if ((_circlePolygon==null)&&(isCircle)) return null;
        console.log(isCircle);
        var edges = _getPolygonEdgeValues(isCircle);
        //console.log(edges);
        var latitudePrecision = (edges.get('max_latitude') - edges.get('min_latitude'))/lat_res;
        var longitudePrecision = (edges.get('max_longitude') - edges.get('min_longitude'))/lon_res;
        var currentLatitude= edges.get('min_latitude');
        var n = performance.now();
        while (currentLatitude<edges.get('max_latitude')){
            var currentLongitude= edges.get('min_longitude');
            while (currentLongitude<edges.get('max_longitude')){
                var locationArray = _getPixelLocationArray(currentLatitude,currentLongitude,latitudePrecision,longitudePrecision);

                if (_checkIfPointInsidePolygon(currentLatitude,currentLongitude,isCircle)){
                    //console.log('tutaj');
                    //console.log('jestem tu');
                    var color = _computeColorBasedOnVDOP(currentLatitude,currentLongitude,altitude,base_station,newStationArray);
                    //console.log(color);
                    //throw 'kniec';
                    //console.log('jestem tu2');
                    var pixel = new Microsoft.Maps.Polygon(locationArray,{strokeThickness:0,fillColor:color});
                    Microsoft.Maps.Events.addHandler(pixel,"mouseover", function (e) { _showVDOP(e); } );
                    _MAP_REFERENCE.entities.push(pixel);
                    _VDOPPixels.push(pixel);
                }
                currentLongitude+=longitudePrecision;
            }
            currentLatitude+=latitudePrecision;
        }

        var n2 = performance.now();
        console.log(n2-n,'czas');
        console.log(n,'czas');
        console.log(n2,'czas');
        if (_vertexPolygon!=null) _vertexPolygon.setOptions({visible:false});
        if (_circlePolygon!=null) _circlePolygon.setOptions({visible:false});
        return 0;
    }

    function _showVDOP(e){
        //console.log(e);
        var pixel = e.target;
        for (var i=0;i<_VDOPPixels.length;++i){
            if (_VDOPPixels[i]===pixel){
                break;
            }
        }
        //console.log(pixel);
        console.log(_VDOPValues);
        console.log(i);
        console.log(_outputId);
        if (_outputId!=='') document.getElementById(_outputId).value = _VDOPValues[i-1];
        getLocalizationMeasurmentError();
    }

    function _clearVDOP(){

        for (var i=0;i<_VDOPPixels.length;++i){
            _MAP_REFERENCE.entities.remove(_VDOPPixels[i]);
        }
        _VDOPPixels=[];
        _VDOPValues=[];
    }


    // Color functions

    function _getColor(val){
        //console.log(value);
        var value = val*4;
        var bins = 60;
        if (value>(bins*2+1)) {return 'black';}
        var min = "00FF00";
        var half = "0000FF";
        var max = "FF0000";

        value= Math.floor(value);
        //console.log(value);

        if (value >bins){
            value-=bins;
            value--;

            var tmp = generateColor(max,half,bins);
            //console.log(tmp[value]);
            //throw 'kniec';
            return '#'+tmp[value];
        } else{
            value--;
            var tmp = generateColor(half,min,bins);
            //console.log(tmp[value]);
            //throw 'kniec';
            return '#'+tmp[value];
        }


    }


    // Polygon functions

    function _checkIfPointInsidePolygon(latitude,longitude,isCircle){
        if (isCircle){
            const meter_per_lon = 40075000*Math.cos(3.14*latitude/180)/360;
            var loc = _circlePin.getLocation();
            var x = (loc.latitude-latitude)*_meter_per_lat;
            var y = (loc.longitude-longitude)*meter_per_lon;
            return _circleRadius>Math.sqrt(x**2+y**2);
        }
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
        return numberOfIntersections%2===1;
    }


    function _getPolygonEdgeValues(isCircle){
        if ((_vertexPolygon == null)&&(!isCircle)) return null;
        if ((_circlePolygon==null)&&(isCircle)) return null;
        if (isCircle){
            _circleRadius;

            var loc =_circlePin.getLocation();
            const meter_per_lon = 40075000*Math.cos(3.14*loc.latitude/180)/360;
            var edges = new Map();
            edges.set('min_latitude',loc.latitude -_circleRadius/_meter_per_lat );
            edges.set('max_latitude',loc.latitude +_circleRadius/_meter_per_lat );
            edges.set('min_longitude',loc.longitude -_circleRadius/meter_per_lon );
            edges.set('max_longitude',loc.longitude +_circleRadius/meter_per_lon );
            return  edges;
        }
        var locations = _vertexPolygon.getLocations();

        //await sleep(2000);
        var edges = new Map();
        edges.set('min_latitude',locations[0].latitude);
        edges.set('max_latitude',locations[0].latitude);
        edges.set('min_longitude',locations[0].longitude);
        edges.set('max_longitude',locations[0].longitude);
        for (var i=1;i<(locations.length-1);++i){
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
            var polygon = new Microsoft.Maps.Polygon(locationArray,{fillColor:'white',visible:true});
            _MAP_REFERENCE.entities.push(polygon);
            _vertexPolygon = polygon
        } else _vertexPolygon=null;

    }

    // Pin functions

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

    function getLocationArrayFromPinArray(pinArray){
        var retArr = [];
        for (var i=0;i<pinArray.length;++i)
        {
            var pin = pinArray[i];
            retArr.push(pin.getLocation());
        }
        return retArr;

    }

    // station functions

    function changeStateOfStation(index,state){
        if (index>=_ifStationActive.length) return null;
        _ifStationActive[index] = state;
        if (state) _stationArray[index].setOptions({color:'green'});
        else _stationArray[index].setOptions({color:'red'});
    }

    function EditStation(loc,alt,index,name){
        if (_ifStationActive[index]) var color='green';
        else color = 'red';
        var newPin = new Microsoft.Maps.Pushpin(loc, {
            title: name, color:color
            // subTitle: number.toString()
        });
        _MAP_REFERENCE.entities.push(newPin);
        var oldPin = _stationArray[index];

        _MAP_REFERENCE.entities.remove(oldPin);
        _stationArray.splice(index,1,newPin);
        _stationAltitudeArray.splice(index,1,alt);
        console.log(_stationAltitudeArray);

    }

    function addStation(loc,alt){
        //var number = _vertexArray.length+1
        var pin = new Microsoft.Maps.Pushpin(loc, {
            title: 'Station',color: 'green',
            // subTitle: number.toString()
        });
        _MAP_REFERENCE.entities.push(pin);
        _stationArray.push(pin);
        _ifStationActive.push(true);
        //console.log(alt);
        _stationAltitudeArray.push(alt);
    }

    function deleteStation(index){
        var pin = _stationArray[index];
        _stationArray.splice(index,1);
        _stationAltitudeArray.splice(index,1);
        _MAP_REFERENCE.entities.remove(pin);
    }

    //  Vertexes functions

    function vertexPolygonVisibility(flag){
        if (_vertexPolygon!=null) _vertexPolygon.setOptions({visible:flag});
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

    // Circle functions

    function circlePolygonVisibility(flag){
        if (_circlePolygon!=null) _circlePolygon.setOptions({visible:flag});
    }

    function _calculateVertexesOfCircle(lat,lon,radius){
        var angle = 0
        var vertexes=[]
        const meter_per_lon = 40075000*Math.cos(3.14*lat/180)/360;
        _MAP_REFERENCE.entities.remove(_circlePolygon);

        for (var i=0;i<30;++i){
            var x = radius*Math.cos(angle)/_meter_per_lat;
            var y = radius*Math.sin(angle)/meter_per_lon;
            var loc = new Microsoft.Maps.Location(lat+x,lon+y);
            vertexes.push(loc);
            angle+= 6.28/30;
        }
        //console.log(vertexes);
        if (_circlePolygon !=null) _MAP_REFERENCE.entities.remove(_circlePolygon);
        _circlePolygon = new Microsoft.Maps.Polygon(vertexes,{fillColor:'white',visible:true});
        _MAP_REFERENCE.entities.push(_circlePolygon);
    }


    function addCircle(loc,radius){
        _clearVDOP();
        //console.log('tutaj');
        //var number = _vertexArray.length+1
        var pin = new Microsoft.Maps.Pushpin(loc, {
            title: 'Cricle',
            // subTitle: number.toString()
        });
        if (_circlePin !=null) _MAP_REFERENCE.entities.remove(_circlePin);
        _MAP_REFERENCE.entities.push(pin);
        _circleRadius=radius;
        _circlePin=pin;
        _calculateVertexesOfCircle(loc.latitude,loc.longitude,radius);
        //console.log(_vertexArray);
        //_updateVertexPolygon();
    }

    function deleteCircle(){
        _clearVDOP();
        _MAP_REFERENCE.entities.remove(_circlePin);
        _circlePin = null
        _MAP_REFERENCE.entities.remove(_circlePolygon);
        _circlePolygon = null;
    }

    //  Map functions

    function setMap(reference) {
        //console.log(reference);
        _MAP_REFERENCE = reference;
    }

    function addHandlerMap(typeOfEvent,func) {
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


    //function getMap() {
    //    //console.log(reference);
    //    return _MAP_REFERENCE;
    //}

    return {
        addVertex:addVertex,
        setMap: setMap,
        //getMap: getMap,
        EditStation:EditStation,
        EditVertex:EditVertex,
        addStation:addStation,
        deleteStation:deleteStation,
        deleteVertex:deleteVertex,
        addHandlerMap: addHandlerMap,
        deleteHandler:deleteHandler,
        calculateVDOP:calculateVDOP,
        addCircle:addCircle,
        deleteCircle:deleteCircle,
        setOutputId:setOutputId,
        vertexPolygonVisibility:vertexPolygonVisibility,
        circlePolygonVisibility:circlePolygonVisibility,
        changeStateOfStation:changeStateOfStation,
    };
})();