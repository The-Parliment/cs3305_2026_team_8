// Global variables to store the map instance and markers
var map;
function initMap() {
    // Create a map centered at coordinates [x, y] with zoom level 17
    // The variables x and y are passed from the HTML template
    map = L.map('map').setView([x, y], 17);

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
