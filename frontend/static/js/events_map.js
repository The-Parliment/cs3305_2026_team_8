var marker = L.marker([x, y], {color : 'red'}).addTo(map)

function setLocation(){
    document.getElementById("latitude").value = map.getCenter().lat;
    document.getElementById("longitude").value = map.getCenter().lng;
}

document.getElementById("latitude").value = map.getCenter().lat;
document.getElementById("longitude").value = map.getCenter().lng;

const radiusSlider = document.getElementById("radius");
console.log("Radius Slider: " + radiusSlider.value);

var circle = L.circle(map.getCenter(), {radius: 1}).addTo(map);
var bounds = circle.getBounds();
map.removeLayer(circle); 

var square = L.rectangle(bounds, {
    color: "blue",
    weight: 1
}).addTo(map);

radiusSlider.addEventListener('input', function() {
    var radius = this.value;
    console.log("Radius: " + radius);
    radius = radius * 1000; // Convert km to meters

    var tempCircle = L.circle(map.getCenter(), {radius: (radius)}).addTo(map);
    var newBounds = tempCircle.getBounds();
    
    square.setBounds(newBounds);
    map.removeLayer(tempCircle); 
});

function onDrag(e){
    marker.setLatLng(map.getCenter());
    document.getElementById("latitude").value = map.getCenter().lat;
    document.getElementById("longitude").value = map.getCenter().lng;
}

map.on("move", onDrag);

events.forEach(element => {
    var marker = L.marker([element.latitude, element.longitude]).addTo(map);
    marker.bindPopup("<b>" + element.title + "</b><br>" + 
        element.description + "<br>" + "<a href='/eventinfo/" + element.id + "'>View Event</a>");
});

