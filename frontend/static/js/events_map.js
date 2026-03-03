var centerMarker = L.marker([x, y]).addTo(map)

function setLocation(){
    document.getElementById("latitude").value = map.getCenter().lat;
    document.getElementById("longitude").value = map.getCenter().lng;
}

document.getElementById("latitude").value = map.getCenter().lat;
document.getElementById("longitude").value = map.getCenter().lng;

const radiusSlider = document.getElementById("radius");
console.log("Radius Slider: " + radiusSlider.value);

var tempRad = (parseFloat(radiusSlider.value) || 1) * 250;

var circle = L.circle(map.getCenter(), {radius: tempRad}).addTo(map);
var bounds = circle.getBounds();
map.removeLayer(circle); 

var square = L.rectangle(bounds, {
    color: "blue",
    weight: 1
}).addTo(map);
square.setBounds(bounds);

radiusSlider.addEventListener('input', function() {
    var radius = this.value;
    console.log("Radius: " + radius);
    radius = radius * 250;

    var tempCircle = L.circle(map.getCenter(), {radius: (radius)}).addTo(map);
    var newBounds = tempCircle.getBounds();
    
    square.setBounds(newBounds);
    map.removeLayer(tempCircle); 
});

function onDrag(e){
    var center = map.getCenter();
    centerMarker.setLatLng(center);

    var radius = (parseFloat(radiusSlider.value) || 1) * 250;

    var tempCircle = L.circle(centerMarker.getLatLng(), {radius: radius}).addTo(map);
    square.setBounds(tempCircle.getBounds());
    map.removeLayer(tempCircle);

    document.getElementById("latitude").value = map.getCenter().lat;
    document.getElementById("longitude").value = map.getCenter().lng;
}

map.on("move", onDrag);

events.forEach(element => {
    var marker = L.marker([element.latitude, element.longitude]).addTo(map);
    marker.bindPopup("<b>" + element.title + "</b><br>" + 
        element.description + "<br>" + "<a href='/eventinfo/" + element.id + "'>View Event</a>");
});

