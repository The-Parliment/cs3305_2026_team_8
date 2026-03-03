var marker = L.marker([x, y], {color : 'red'}).addTo(map)

function onDrag(e){
    marker.setLatLng(map.getCenter());
    document.getElementById("latitude").value = map.getCenter().lat;
    document.getElementById("longitude").value = map.getCenter().lng;
}

map.on("move", onDrag);

function setLocation(){
    document.getElementById("latitude").value = map.getCenter().lat;
    document.getElementById("longitude").value = map.getCenter().lng;
}

document.getElementById("latitude").value = map.getCenter().lat;
document.getElementById("longitude").value = map.getCenter().lng;