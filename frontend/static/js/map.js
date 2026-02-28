var map;
var userMarker;
var friendMarkersLayer;
var DEFAULT_FRIENDS_RADIUS_KM = 2;
var LIVE_REFRESH_INTERVAL_MS = 5000;
var liveRefreshTimer = null;

// Geolocation pattern heavily inspired by https://www.w3schools.com/html/html5_geolocation.asp
function initMap() {
    map = L.map('map').setView([x, y], 17);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        minZoom: 7,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    friendMarkersLayer = L.layerGroup().addTo(map);

    getLocation();
}

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(success, error, getGeoOptions());
    } else {
        console.error("Geolocation is not supported by this browser");
    }
}

function success(position) {
    var userLat = position.coords.latitude;
    var userLng = position.coords.longitude;

    var label = authorizedUser || "me";
    if (userMarker) {
        map.removeLayer(userMarker);
    }

    userMarker = L.marker([userLat, userLng]).addTo(map).bindTooltip(label, {
        permanent: true,
        direction: 'top',
        className: 'user-location-label'
    }).openTooltip();

    map.setView([userLat, userLng], 17);
    
    // Send location update to proximity service
    if (authorizedUser) {
        updateProximityService(authorizedUser, userLat, userLng);
        getFriendsLocations(authorizedUser, userLat, userLng);
        startLiveRefresh();
    }
}

function startLiveRefresh() {
    if (liveRefreshTimer) {
        return;
    }

    liveRefreshTimer = setInterval(function() {
        getLocation();
    }, LIVE_REFRESH_INTERVAL_MS);
}

function error(err) {
    var code = err && err.code ? err.code : "unknown";
    var message = err && err.message ? err.message : "unknown error";
    console.error("Error getting location:", err);
    console.error("Geolocation error code:", code, "message:", message);
}

function getGeoOptions() {
    var isMobile = /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent);
    return {
        enableHighAccuracy: isMobile,
        timeout: isMobile ? 15000 : 8000,
        maximumAge: isMobile ? 60000 : 300000
    };
}

function updateProximityService(username, latitude, longitude) {
    fetch('/proximity/update_location', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            latitude: latitude,
            longitude: longitude
        })
    })
    .then(function(response) {
        if (response.ok) {
            console.log("Location updated in proximity service");
        } else {
            console.error("Failed to update proximity service:", response.status);
        }
    })
    .catch(function(error) {
        console.error("Error updating proximity service:", error);
    });
}

function getFriendsLocations(username, latitude, longitude) {
    var radius = (typeof friendsRadiusKm !== 'undefined' && Number(friendsRadiusKm) > 0)
        ? Number(friendsRadiusKm)
        : DEFAULT_FRIENDS_RADIUS_KM;

    fetch('/proximity/get_friends', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin',
        body: JSON.stringify({
            username: username,
            latitude: latitude,
            longitude: longitude,
            radius: radius
        })
    })
    .then(function(response) {
        if (!response.ok) {
            throw new Error('Failed to get friends list: ' + response.status);
        }
        return response.json();
    })
    .then(function(data) {
        renderFriendMarkers(data && data.friends ? data.friends : []);
    })
    .catch(function(error) {
        console.error('Error fetching friends locations:', error);
        renderFriendMarkers([]);
    });
}

function renderFriendMarkers(friends) {
    if (!friendMarkersLayer) {
        return;
    }

    friendMarkersLayer.clearLayers();

    friends.forEach(function(friend) {
        if (!friend || typeof friend.latitude !== 'number' || typeof friend.longitude !== 'number') {
            return;
        }

        var marker = L.marker([friend.latitude, friend.longitude]);
        var label = friend.username || 'friend';
        marker.bindTooltip(label, {
            permanent: true,
            direction: 'top'
        }).openTooltip();

        if (typeof friend.distance === 'number') {
            marker.bindPopup('Distance: ' + friend.distance.toFixed(2) + ' km');
        }

        marker.addTo(friendMarkersLayer);
    });
}

// Wait for Leaflet to be fully loaded before initializing
if (typeof L !== 'undefined') {
    initMap();
} else {
    window.addEventListener('load', function() {
        initMap();
    });
}
