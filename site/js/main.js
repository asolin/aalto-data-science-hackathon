// Generated by CoffeeScript 1.9.2
(function() {
  var activePolylines, addMapLine, clearMap, createIndividualPathTrail, createPathsOnMap, displayNotification, getActivePaths, getPathJobColor, initializeGoogleMaps, map, populateMap, hackAPI;

  hackAPI = "http://dev.hel.fi/aura/v1/snowplow/data";

  activePolylines = [];

  map = null;

  initializeGoogleMaps = function(callback, time) {
    var helsinkiCenter, mapOptions, styles;
    helsinkiCenter = new google.maps.LatLng(60.193084, 24.940338);
    mapOptions = {
      center: helsinkiCenter,
      zoom: 13,
      disableDefaultUI: true,
      zoomControl: true,
      zoomControlOptions: {
        style: google.maps.ZoomControlStyle.SMALL,
        position: google.maps.ControlPosition.RIGHT_BOTTOM
      }
    };
    map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);
    map.setOptions({
      styles: styles
    });
    return callback(time);
  };

  getPathColor = function(value) {

    return "#" + ("00" + Math.floor(parseInt('00',16) + value / 100 * parseInt('ff',16)).toString(16)).slice(-2) + "00ff";

//    if (value > 50) {
//      return "#84ff00";
//    } else {
//      return "#d93425";
//    }
  };

  addMapLine = function(PathData, value) {
    var PathTrailColor, polyline, polylinePath;
    PathTrailColor = getPathColor(value);
    polylinePath = _.reduce(PathData, (function(accu, x) {
      accu.push(new google.maps.LatLng(x.coords[1], x.coords[0]));
      return accu;
    }), []);
    polyline = new google.maps.Polyline({
      path: polylinePath,
      geodesic: true,
      strokeColor: PathTrailColor,
      strokeWeight: 2,
      strokeOpacity: 0.8
    });
    activePolylines.push(polyline);
    return polyline.setMap(map);
  };

  clearMap = function() {
    return _.map(activePolylines, function(polyline) {
      return polyline.setMap(null);
    });
  };

  displayNotification = function(notificationText) {
    var $notification;
    $notification = $("#notification");
    return $notification.empty().text(notificationText).slideDown(800).delay(5000).slideUp(800);
  };

  getActivePaths = function(time, callback) {
    $("#load-spinner").fadeIn(400);
    return $.getJSON("routes.json").done(function(json) {
      if (json.length !== 0) {
        callback(time, json);
      } else {
        displayNotification("No routes to show.");
      }
      return $("#load-spinner").fadeOut(800);
    }).fail(function(error) {
      return console.error("Failed to fetch paths: " + (JSON.stringify(error)));
    });
  };

  createIndividualPathTrail = function(value, PathId, historyData) {
    $("#load-spinner").fadeIn(800);
    return $.getJSON("route-"+PathId+".json").done(function(json) {
      if (json.length !== 0) {
        _.map(json, function(onepath) {
            return addMapLine(onepath, value);
        });
        return $("#load-spinner").fadeOut(800);
      }
    }).fail(function(error) {
      return console.error("Failed to create path " + PathId + ": " + (JSON.stringify(error)));
    });
  };

  createPathsOnMap = function(time, json) {
    return _.each(json, function(x) {
      return createIndividualPathTrail(x.value, x.id, json);
    });
  };

  populateMap = function(time) {
    clearMap();
    return getActivePaths(time + "hours+ago", function(time, json) {
      return createPathsOnMap(time, json);
    });
  };

  $(document).ready(function() {
    var clearUI;
    clearUI = function() {
      $("#notification").stop(true, false).slideUp(200);
      return $("#load-spinner").stop(true, false).fadeOut(200);
    };
    if (localStorage["auratkartalla.userHasClosedInfo"]) {
      $("#info").addClass("off");
    }
    initializeGoogleMaps(populateMap, 8);
    $("#time-filters li").on("click", function(e) {
      e.preventDefault();
      clearUI();
      $("#time-filters li").removeClass("active");
      $(e.currentTarget).addClass("active");
      $("#visualization").removeClass("on");
      return populateMap($(e.currentTarget).data("hours"));
    });
    $("#info-close, #info-button").on("click", function(e) {
      e.preventDefault();
      $("#info").toggleClass("off");
      return localStorage["auratkartalla.userHasClosedInfo"] = true;
    });
    return $("#visualization-close, #visualization-button").on("click", function(e) {
      e.preventDefault();
      return $("#visualization").toggleClass("on");
    });
  });


}).call(this);
