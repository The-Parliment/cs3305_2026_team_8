// Global variables to store the map instance and markers
var map;// 1. Try to get saved state, or use defaults
var savedCenter = localStorage.getItem('mapCenter');
var savedZoom = localStorage.getItem('mapZoom');

var center = savedCenter ? JSON.parse(savedCenter) : [51.8925, -8.4925]; // Default coords
var zoom = savedZoom ? parseInt(savedZoom) : 13; // Default zoom
function initMap() {
    // Create a map centered at coordinates [x, y] with zoom level 17
    // The variables x and y are passed from the HTML template
    map = L.map('map').setView(center, zoom);

    // Add the tile layer (the base map from OpenStreetMap)
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        minZoom: 7,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
}

if (typeof L !== 'undefined') {
    initMap();
} else {
    window.addEventListener('load', function() {
        initMap();
    });
}
map.on('moveend', function() {
    var center = map.getCenter();
    var zoom = map.getZoom();
    
    // Save as JSON string
    localStorage.setItem('mapCenter', JSON.stringify([center.lat, center.lng]));
    localStorage.setItem('mapZoom', zoom);
});
