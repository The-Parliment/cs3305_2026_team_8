var marker = L.marker([x, y]).addTo(map)

function onDrag(e){
    marker.setLatLng(map.getCenter());
    document.getElementById("latitude").value = map.getCenter().lat;
    document.getElementById("longitude").value = map.getCenter().lng;
}

map.on("move", onDrag);

function setLocation(){
    document.getElementById("location").value = map.getCenter().lat + ", " + map.getCenter().lng;
}

document.getElementById("location").value = map.getCenter().lat + ", " + map.getCenter().lng;