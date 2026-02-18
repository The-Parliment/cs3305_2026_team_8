events.forEach(element => {
    var marker = L.marker([element.latitude, element.longitude]).addTo(map);
    marker.bindPopup("<b>" + element.title + "</b><br>" + 
        element.description + "<br>" + "<a href='/eventinfo/" + element.id + "'>View Event</a>");
});