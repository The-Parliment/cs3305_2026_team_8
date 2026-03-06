// Global variables to store the map instance and markers
var map;
var userMarker;
var friendMarkersLayer;
var DEFAULT_FRIENDS_RADIUS_KM = 2; // Default search radius for nearby friends in kilometers
var LIVE_REFRESH_INTERVAL_MS = 5000; // Refresh location every 5 seconds (in milliseconds)
var liveRefreshTimer = null;
var first_time = true;

// Geolocation pattern heavily inspired by https://www.w3schools.com/html/html5_geolocation.asp
// This function initializes the Leaflet map with a tile layer (OpenStreetMap)
// and sets up the friend markers layer as a separate group so we can update it easily
function initMap() {
    // Create a map centered at coordinates [x, y] with zoom level 13
    // The variables x and y are passed from the HTML template
    map = L.map('map').setView([x, y], 13);

    // Add the tile layer (the base map from OpenStreetMap)
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        minZoom: 7,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    // Create a layer group for friend markers - this lets us add/remove friend pins
    // without affecting the user's own marker
    friendMarkersLayer = L.layerGroup().addTo(map);

    // Start getting the user's location from their browser's GPS/network
    getLocation();
}

// Request the browser to get the user's current geolocation
// This calls the success() callback if location is found, or error() if something goes wrong
function getLocation() {
    if (navigator.geolocation) {
        // Pass the success and error callbacks, plus options for timing and accuracy
        navigator.geolocation.getCurrentPosition(success, error, getGeoOptions());
    } else {
        console.error("Geolocation is not supported by this browser");
    }
}

// Called when geolocation is successful - we have the user's latitude and longitude
function success(position) {
    var userLat = position.coords.latitude;
    var userLng = position.coords.longitude;

    // Use the authorized user's name for the label, or "me" if not logged in
    var label = authorizedUser || "me";
    
    // Remove the old user marker if it exists (so we don't stack markers on multiple updates)
    if (userMarker) {
        map.removeLayer(userMarker);
    }

    // Create a new marker at the user's location with a tooltip showing their name
    userMarker = L.marker([userLat, userLng]).addTo(map).bindTooltip(label, {
        permanent: true,
        direction: 'top',
        className: 'user-location-label'
    }).openTooltip();

    // Center the map on the user's location
    if (first_time){
        map.setView([userLat, userLng], 17);
        first_time = false;
    }
    
    // If the user is logged in (authorizedUser exists), send their location to the proximity service
    // and fetch their friends' locations
    if (authorizedUser) {
        // Tell the backend we're at this location (updates Valkey database)
        updateProximityService(authorizedUser, userLat, userLng);
        
        // Fetch and render friend locations from the proximity service
        getFriendsLocations(authorizedUser, userLat, userLng);
        
        // Start the 5-second refresh timer if not already running
        startLiveRefresh();
    }
}

// Start a timer that refreshes the user's location every 5 seconds
// This keeps the map updated as the user moves
function startLiveRefresh() {
    // Only start the timer if it's not already running (prevents multiple timers)
    if (liveRefreshTimer) {
        return;
    }

    // Call getLocation() every 5000 milliseconds (5 seconds)
    liveRefreshTimer = setInterval(function() {
        getLocation();
    }, LIVE_REFRESH_INTERVAL_MS);
}

// Called when geolocation fails (e.g., user denied permission, timeout, etc.)
function error(err) {
    var code = err && err.code ? err.code : "unknown";
    var message = err && err.message ? err.message : "unknown error";
    console.error("Error getting location:", err);
    console.error("Geolocation error code:", code, "message:", message);
}

// Configure geolocation options - mainly timeout and accuracy settings
function getGeoOptions() {
    var isMobile = /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent);
    // Mobile devices use high accuracy (GPS) with longer timeout
    // Desktop browsers use lower accuracy (network-based) with shorter timeout
    return {
        enableHighAccuracy: isMobile,
        timeout: isMobile ? 15000 : 8000,
        maximumAge: isMobile ? 60000 : 300000
    };
}

// Send the user's current location to the proximity service backend
// This updates the Valkey database so other users can find this user's location
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

// Fetch the list of friends (circle members) within a specified radius
// This calls the backend /get_friends endpoint which filters by:
// 1. Who's in this user's accepted circle
// 2. Who's within the search radius (default 2km)
function getFriendsLocations(username, latitude, longitude) {
    // Allow the HTML to override the default radius by setting a global variable
    var radius = (typeof friendsRadiusKm !== 'undefined' && Number(friendsRadiusKm) > 0)
        ? Number(friendsRadiusKm)
        : DEFAULT_FRIENDS_RADIUS_KM;

    // Make a request to the proximity service to get friends
    fetch('/proximity/get_friends', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin', // Include auth cookies
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
        // Once we have the friends data, render their locations on the map
        renderFriendMarkers(data && data.friends ? data.friends : []);
    })
    .catch(function(error) {
        console.error('Error fetching friends locations:', error);
        // If there's an error, render an empty list (no friends shown)
        renderFriendMarkers([]);
    });
}

// Clear the friend markers layer and add new markers for each friend
// This gets called after fetching the friends list
function renderFriendMarkers(friends) {
    // Make sure the layer is initialized before trying to use it
    if (!friendMarkersLayer) {
        return;
    }

    // Remove all existing friend markers from the layer
    friendMarkersLayer.clearLayers();

    // Loop through each friend and add a marker for them
    friends.forEach(function(friend) {
        // Skip invalid friend data (missing lat/lon)
        if (!friend || typeof friend.latitude !== 'number' || typeof friend.longitude !== 'number') {
            return;
        }

        // Create a marker at the friend's location
        var marker = L.marker([friend.latitude, friend.longitude]);
        var label = friend.username || 'friend';
        
        // Add a tooltip with the friend's username (always visible)
        marker.bindTooltip(label, {
            permanent: true,
            direction: 'top'
        }).openTooltip();

        // If we have distance data, add a popup that shows how far away they are
        if (typeof friend.distance === 'number') {
            marker.bindPopup('Distance: ' + friend.distance.toFixed(2) + ' km');
            marker.bindPopup("<a href='/profile/" + friend.username + "'> View Profile </a>")
        }

        // Add the marker to the friend layer (so it appears on the map)
        marker.addTo(friendMarkersLayer);
    });
}

// Wait for Leaflet to be fully loaded before initializing the map
// If L (Leaflet) is already defined, init immediately
// Otherwise, wait for the page to load completely before trying to use Leaflet
if (typeof L !== 'undefined') {
    initMap();
} else {
    window.addEventListener('load', function() {
        initMap();
    });
}
