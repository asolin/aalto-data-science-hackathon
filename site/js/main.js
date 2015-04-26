// Generated by CoffeeScript 1.9.2
(function() {
  var activePolylines, addMapLine, clearMap, createIndividualPathTrail, createPathsOnMap, displayNotification, getActivePaths, getPathJobColor, initializeGoogleMaps, map, populateMap, hackAPI;

  hackAPI = "http://dev.hel.fi/aura/v1/snowplow/data";

  activePolylines = [];

  map = null;
  heatmap = new google.maps.visualization.HeatmapLayer({
      dissipating: true,
      //gradient: ,
      //maxIntensity: ,
      opacity: 0.7,
      radius: 20
    });

  initializeGoogleMaps = function(callback, visualization, json_file, index) {
    var helsinkiCenter, mapOptions, styles;
    helsinkiCenter = new google.maps.LatLng(60.21, 24.940338);
    mapOptions = {
      center: helsinkiCenter,
      zoom: 12,
      disableDefaultUI: true,
      zoomControl: true,
      zoomControlOptions: {
        style: google.maps.ZoomControlStyle.SMALL,
        position: google.maps.ControlPosition.RIGHT_BOTTOM
      }
    };
    styles = [
    {
        "featureType": "landscape",
        "stylers": [
            {
                "saturation": -100
            },
            {
                "lightness": 65
            },
            {
                "visibility": "on"
            }
        ]
    },
    {
        "featureType": "poi",
        "stylers": [
            {
                "saturation": -100
            },
            {
                "lightness": 51
            },
            {
                "visibility": "simplified"
            }
        ]
    },
    {
        "featureType": "road.highway",
        "stylers": [
            {
                "saturation": -100
            },
            {
                "visibility": "simplified"
            }
        ]
    },
    {
        "featureType": "road.arterial",
        "stylers": [
            {
                "saturation": -100
            },
            {
                "lightness": 30
            },
            {
                "visibility": "on"
            }
        ]
    },
    {
        "featureType": "road.local",
        "stylers": [
            {
                "saturation": -100
            },
            {
                "lightness": 40
            },
            {
                "visibility": "on"
            }
        ]
    },
    {
        "featureType": "transit",
        "stylers": [
            {
                "saturation": -100
            },
            {
                "visibility": "simplified"
            }
        ]
    },
    {
        "featureType": "administrative.province",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "labels",
        "stylers": [
            {
                "visibility": "on"
            },
            {
                "lightness": -25
            },
            {
                "saturation": -100
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "geometry",
        "stylers": [
            {
                "hue": "#ffff00"
            },
            {
                "lightness": -25
            },
            {
                "saturation": -97
            }
        ]
    }
    ];
    map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);
    map.setOptions({
      styles: styles
    });
    return callback(visualization, json_file, index);
  };

  getColormap = function(v, vmin, vmax) {
    var r=1.0,g=1.0,b=1.0,dv;
    if (v < vmin)
      v = vmin;
    if (v > vmax)
      v = vmax;
    dv = vmax - vmin;
    if (v < (vmin + 0.25 * dv)) {
      r = 0.0;
      g = 4.0 * (v - vmin) / dv;
    } else if (v < (vmin + 0.5 * dv)) {
      r = 0.0;
      b = 1.0 + 4.0 * (vmin + 0.25 * dv - v) / dv;
    } else if (v < (vmin + 0.75 * dv)) {
      r = 4.0 * (v - vmin - 0.5 * dv) / dv;
      b = 0.0;
    } else {
      g = 1.0 + 4.0 * (vmin + 0.75 * dv - v) / dv;
      b = 0.0;
    }
    return("#"+("00"+(Math.floor(255*r)).toString(16)).slice(-2)
              +("00"+(Math.floor(255*g)).toString(16)).slice(-2)
              +("00"+(Math.floor(255*b)).toString(16)).slice(-2));
  }


  addMapLine = function(PathData, value) {
    var PathTrailColor, polyline, polylinePath;
    PathTrailColor = getColormap(value,0,100);
    polylinePath = _.reduce(PathData, (function(accu, x) {
      accu.push(new google.maps.LatLng(x.coords[1], x.coords[0]));
      return accu;
    }), []);
    polyline = new google.maps.Polyline({
      path: polylinePath,
      geodesic: true,
      strokeColor: PathTrailColor,
      strokeWeight: 4,
      strokeOpacity: 0.5
    });
    activePolylines.push(polyline);
    return polyline.setMap(map);
  };

  clearMap = function() {
    heatmap.set('data', null);
    return _.map(activePolylines, function(polyline) {
      return polyline.setMap(null);
    });
  };

  displayNotification = function(notificationText) {
    var $notification;
    $notification = $("#notification");
    return $notification.empty().text(notificationText).slideDown(800).delay(5000).slideUp(800);
  };

  getActivePaths = function(routemap, index, callback) {
    $("#load-spinner").fadeIn(400);
    return $.getJSON(routemap).done(function(json) {
      if (json.length !== 0) {
        callback(index, json);
      } else {
        displayNotification("No routes to show.");
      }
      return $("#load-spinner").fadeOut(800);
    }).fail(function(error) {
      return console.error("Failed to fetch paths: " + (JSON.stringify(error)));
    });
  };

  createIndividualPathTrail = function(value, StopId1, StopId2, historyData) {
    $("#load-spinner").fadeIn(800);
    return $.getJSON("routes/route-"+StopId1+"-"+StopId2+".json").done(function(json) {
      if (json.length !== 0) {
        _.map(json, function(onepath) {
            return addMapLine(onepath, value);
        });
        return $("#load-spinner").fadeOut(800);
      }
    }).fail(function(error) {
      return console.error("Failed to create path " + StopId1 + "-" + StopId2 + ": " + (JSON.stringify(error)));
    });
  };

  createPathsOnMap = function(index, json) {
    return _.each(json, function(x) {
      //console.error("Path: " + x.value[0] + " " + x.id[0] + " " + x.id);
      return createIndividualPathTrail(x.value[index], x.id[0], x.id[1], json);
    });
  };

  populateMap = function(visualization, json_file, index) {
    clearMap();
    if (visualization == "heatmap") {
      console.error("Show heat map for " + json_file + " index " + index);
      return createHeatMap(json_file, index);
    }
    else {
      console.error("Show route map type " + visualization + " " + json_file + " index " + index);
      return getActivePaths(json_file, index, function(index, json) {
        return createPathsOnMap(index, json);
      });
    }
  };

  drawHeatMap = function(data) {
    heatmap.setData(data);
    heatmap.setMap(map);
  }
  

  createHeatMap = function(json_file, index) {

    $("#load-spinner").fadeIn(800);
    var heatMapData = [];
    // Dynamic API:
    //return $.getJSON("" + hackAPI + "?heatmap").done(function(json) {
    // Static API:
    return $.getJSON(json_file).done(function(json) {
      if (json.length !== 0) {
        _.map(json, function(json_data) {
          for (i = 0; i < json_data.length; i++) {
            var lat = json_data[i].coords[0];
            var lng = json_data[i].coords[1];
            var weight = json_data[i].value[index];
            heatMapData.push({location: new google.maps.LatLng(lng, lat),
                              weight: Math.max(0, weight)});
          }
        });
        drawHeatMap(heatMapData);
        return $("#load-spinner").fadeOut(800);
      }
    }).fail(function(error) {
      return console.error("Failed to create heat map: " + (JSON.stringify(error)));
    });

  };


  $(document).ready(function() {
    var clearUI;
    clearUI = function() {
      $("#notification").stop(true, false).slideUp(200);
      return $("#load-spinner").stop(true, false).fadeOut(200);
    };
    if (localStorage["hackathon.userHasClosedInfo"]) {
      $("#info").addClass("off");
    }
    initializeGoogleMaps(populateMap, "heatmap", "stop_1.json", 0);
    $("#time-filters li").on("click", function(e) {
      e.preventDefault();
      clearUI();
      $("#time-filters li").removeClass("active");
      $(e.currentTarget).addClass("active");
      $("#visualization").removeClass("on");
      console.error("" + $(e.currentTarget).data("visualization") +
                         $(e.currentTarget).data("json") +
                    $(e.currentTarget).data("index"))
      return populateMap($(e.currentTarget).data("visualization"),
                         $(e.currentTarget).data("json"),
                         $(e.currentTarget).data("index"));
    });
    $("#info-close, #info-button").on("click", function(e) {
      e.preventDefault();
      $("#info").toggleClass("off");
      return localStorage["hackathon.userHasClosedInfo"] = true;
    });
    return $("#visualization-close, #visualization-button").on("click", function(e) {
      e.preventDefault();
      return $("#visualization").toggleClass("on");
    });
  });


}).call(this);
