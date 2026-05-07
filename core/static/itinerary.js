    const YANDEX_API_KEY = "7af13a42-8ae5-4930-8b11-50aa988d021a";

    function getCookie(name) {
        const v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
        return v ? v[2] : null;
    }

    let mapInstances = {}; 
    let geocodedItineraryItems = {}; 
    let rawItineraries = [];

    const countryRank = {
        "Kazakhstan": 1,
        "Kyrgyzstan": 2,
        "Uzbekistan": 3,
        "Turkmenistan": 4,
        "Tajikistan": 5,
    };
    async function removeItem(itemId) {
        if (!confirm("Remove this place from your trip?")) return;
        try {
            const response = await fetch(`/itinerary/remove-item/${itemId}/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') }
            });
            if (response.ok) window.location.reload();
        } catch (e) {
            console.error("Removal error:", e);
        }
    }

    async function deleteEntireTrip(itinId) {
        if (!confirm("Are you sure? This trip will be permanently deleted.")) return;
        try {
            const response = await fetch(`/itinerary/delete/${itinId}/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') }
            });
            if (response.ok) window.location.reload();
        } catch (e) {
            console.error("Delete error:", e);
        }
    }

    // --- Initial Map Loading and Geocoding ---
    ymaps.ready(async () => {
        rawItineraries = JSON.parse(document.getElementById('itineraries-data').textContent);

        rawItineraries.forEach(async (itin) => {
            const mapDiv = document.getElementById(`map-${itin.id}`);
            if (!mapDiv || itin.items.length === 0) return;

            const map = new ymaps.Map(mapDiv, {
                center: [itin.items[0].lat, itin.items[0].lng],
                zoom: 9,
                controls: ['zoomControl', 'fullscreenControl', 'rulerControl']
            });
            mapInstances[itin.id] = map;

            const geocodePromises = itin.items.map(async (item) => {
                let coords = [item.lat, item.lng]; // Fallback to DB coords
                try {
                    const query = `${item.name}, ${item.city}, ${item.country}`;
                    const res = await ymaps.geocode(query, { results: 1 });
                    const firstGeoObject = res.geoObjects.get(0);
                    if (firstGeoObject) {
                        coords = firstGeoObject.geometry.getCoordinates();
                        item.lat = coords[0];
                        item.lng = coords[1];
                    }
                } catch (e) {
                    console.error("Geocoder failed for " + item.name + ":", e);
                }
                
                // Always add a marker to the map, using best available coordinates
                map.geoObjects.add(new ymaps.Placemark(coords, {
                    balloonContent: `<strong>${item.name}</strong><br>${item.city}`,
                    iconContent: item.name.substring(0, 1)
                }, { preset: 'islands#darkGreenIcon' }));

                return item;
            });

            geocodedItineraryItems[itin.id] = await Promise.all(geocodePromises);
            if (map.geoObjects.getLength() > 0) map.setBounds(map.geoObjects.getBounds(), { checkZoomRange: true, zoomMargin: 30 });
        });
    });

    let currentItinId = null;
    let currentItems = [];

    function startGenerator(id) {
        currentItinId = id;
        // Try to get geocoded items first, fallback to raw data if not yet processed
        if (geocodedItineraryItems[id]) {
            currentItems = geocodedItineraryItems[id];
        } else {
            const found = rawItineraries.find(it => it.id === id);
            currentItems = found ? found.items : [];
        }
        document.getElementById('gen-overlay').style.display = 'flex';
    }

    async function runOptimization() {
        document.getElementById('gen-overlay').style.display = 'none';
        const map = mapInstances[currentItinId];
        if (!map) return;

        map.geoObjects.removeAll();

        const scheduleDiv = document.getElementById(`schedule-${currentItinId}`);
        scheduleDiv.innerHTML = '<h3>Calculating logically...</h3>';
        const startTimeStr = document.getElementById('gen-start').value;

        // --- GEOGRAPHIC & LOGICAL SORTING ENGINE ---
        const sortedItems = [...currentItems].sort((a, b) => {
            const rankA = countryRank[a.country] || 99;
            const rankB = countryRank[b.country] || 99;
            if (rankA !== rankB) return rankA - rankB; // 1. Regional North-to-South Flow
            if (a.city !== b.city) return a.city.localeCompare(b.city); // 2. Group by City
            // 3. Hotels at the start of city visit
            if (a.type === 'hotel' && b.type !== 'hotel') return -1; // 3. Hotels at the start of city visit
            return 0;
        });

        // Re-add markers to the map using the sorted order with sequence numbers
        sortedItems.forEach((item, idx) => {
            if (!isNaN(item.lat) && !isNaN(item.lng)) {
                map.geoObjects.add(new ymaps.Placemark([item.lat, item.lng], {
                    balloonContent: `<strong>${item.name}</strong><br>${item.city}`,
                    iconContent: (idx + 1).toString()
                }, { preset: 'islands#darkGreenIcon' }));
            }
        });

        const randomColor = '#' + Math.floor(Math.random() * 16777215).toString(16);

        // Generate schedule HTML independently of routing success
        let scheduleHtml = `<h3 style="color:${randomColor}">Logical Journey Plan:</h3>`;
        let currentTime = new Date();
        const [h, m] = startTimeStr.split(':').map(Number);
        currentTime.setHours(h, m, 0);

        let lastLoc = null;
        let dayCounter = 1;

        sortedItems.forEach((item) => {
            if (currentTime.getHours() >= 22) {
                dayCounter++;
                currentTime.setHours(h, m, 0);
                scheduleHtml += `<h4 class="item-tag">Day ${dayCounter}</h4>`;
            }

            if (lastLoc && (lastLoc.city !== item.city || lastLoc.country !== item.country)) {
                scheduleHtml += `
                    <div class="schedule-grid" style="opacity: 0.7">
                        <div class="time-slot">${currentTime.getHours().toString().padStart(2, '0')}:00</div>
                        <div><i class="bi bi-airplane"></i> Travel to ${item.city}, ${item.country}</div>
                    </div>`;
                currentTime.setHours(currentTime.getHours() + 3);
            }

            scheduleHtml += `
                <div class="schedule-grid" style="border-left: 4px solid ${randomColor}; padding-left: 10px;">
                    <div class="time-slot">${currentTime.getHours().toString().padStart(2, '0')}:00</div>
                    <div><strong>${item.name}</strong> <span class="badge">${item.type.toUpperCase()}</span></div>
                </div>`;

            currentTime.setHours(currentTime.getHours() + 2);
            lastLoc = item;
        });
        scheduleDiv.innerHTML = scheduleHtml;

        // Filter out invalid coords and remove consecutive duplicates (which can crash the Route API)
        const waypoints = [];
        sortedItems.forEach(i => {
            if (!isNaN(i.lat) && !isNaN(i.lng)) {
                if (waypoints.length === 0 || 
                    (waypoints[waypoints.length - 1][0] !== i.lat || waypoints[waypoints.length - 1][1] !== i.lng)) {
                    waypoints.push([i.lat, i.lng]);
                }
            }
        });

        if (waypoints.length < 2) return;

        try {
            const route = await ymaps.route(waypoints, { 
                mapStateAutoApply: true, 
                routingMode: 'auto' 
            }, { 
                routeStrokeColor: randomColor, 
                routeStrokeWidth: 5 
            });
            map.geoObjects.add(route);
            map.setBounds(route.getBounds());
        } catch (e) {
            console.error("Yandex Route Error:", e);
            // Fallback: draw direct lines between locations if road routing fails across borders
            const fallbackLine = new ymaps.Polyline(waypoints, {}, {
                strokeColor: randomColor,
                strokeWidth: 4,
                strokeOpacity: 0.6
            });
            map.geoObjects.add(fallbackLine);
            map.setBounds(fallbackLine.geometry.getBounds(), { checkZoomRange: true, zoomMargin: 30 });
            scheduleDiv.innerHTML += `<p style="font-size: 12px; color: #ff9999; margin-top: 10px;">Note: Direct lines shown on map because cross-border driving routes are unavailable in this region.</p>`;
        }
    }
