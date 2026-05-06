
    const YANDEX_API_KEY = "7af13a42-8ae5-4930-8b11-50aa988d021a"; // Define your API key here
    
    // Global storage for map instances and geocoded items
    let mapInstances = {}; // Stores Yandex Map objects
    let geocodedItineraryItems = {}; // Stores items with their accurate geocoded coordinates

    // --- Delete Functions ---
    async function removeItem(itemId) {
        if(!confirm("Remove this place from your trip?")) return;
        try {
            const response = await fetch(`/itinerary/remove-item/${itemId}/`, { 
                method: 'POST', 
                headers: { 'X-CSRFToken': '{{ csrf_token }}' } 
            });
            if (response.ok) {
                window.location.reload(); // Reload to reflect changes
            } else {
                const errorData = await response.json();
                alert(`Error removing item: ${errorData.message || 'Something went wrong.'}`);
            }
        } catch (e) {
            alert("Network error during item removal.");
            console.error("Remove item network error:", e);
        }
    }

    async function deleteEntireTrip(itinId) {
        if(!confirm("Are you sure? This trip will be permanently deleted.")) return;
        try {
            const response = await fetch(`/itinerary/delete/${itinId}/`, { 
                method: 'POST', 
                headers: { 'X-CSRFToken': '{{ csrf_token }}' } 
            });
            if (response.ok) {
                window.location.reload(); // Reload to reflect changes
            } else {
                const errorData = await response.json();
                alert(`Error deleting trip: ${errorData.message || 'Something went wrong.'}`);
            }
        } catch (e) {
            alert("Network error during trip deletion.");
            console.error("Delete trip network error:", e);
        }
    }

    // --- Initial Map Loading and Geocoding ---
    ymaps.ready(() => {
        const itineraries = {{ itineraries|safe }};

        itineraries.forEach(async (itin) => {
            const mapDiv = document.getElementById(`map-${itin.id}`);
            if (!mapDiv || itin.items.length === 0) return;

            // Initialize map with a placeholder center (first item's approximate location)
            const map = new ymaps.Map(mapDiv, {
                center: [itin.items[0].lat, itin.items[0].lng],
                zoom: 9,
                controls: ['zoomControl', 'fullscreenControl', 'rulerControl']
            });
            mapInstances[itin.id] = map;
            geocodedItineraryItems[itin.id] = [];

            // Geocode all items for this specific map concurrently
            const geocodePromises = itin.items.map(async (item) => {
                try {
                    const query = `${item.name}, ${item.city}, ${item.country}`;
                    const res = await ymaps.geocode(query, { results: 1 });
                    const firstGeoObject = res.geoObjects.get(0);

                    if (firstGeoObject) {
                        const coords = firstGeoObject.geometry.getCoordinates();
                        item.geocoded_lat = coords[0];
                        item.geocoded_lng = coords[1];

                        const placemark = new ymaps.Placemark(coords, {
                            balloonContent: `<strong>${item.name}</strong><br>${item.city}<br><small>Verified by Yandex</small>`,
                            iconContent: item.name.substring(0, 1)
                        }, { preset: 'islands#darkGreenIcon' });
                        map.geoObjects.add(placemark);
                    } else {
                        item.geocoded_lat = item.lat;
                        item.geocoded_lng = item.lng;
                        map.geoObjects.add(new ymaps.Placemark([item.lat, item.lng], {
                            balloonContent: `<strong>${item.name}</strong><br>${item.city}<br><small>Approximate Location</small>`,
                            iconContent: '?'
                        }, { preset: 'islands#redDotIcon' }));
                    }
                } catch (e) {
                    console.error("Geocoding error:", e);
                }
            });

            await Promise.all(geocodePromises);
            geocodedItineraryItems[itin.id] = itin.items;
            if (map.geoObjects.getLength() > 0) {
                map.setBounds(map.geoObjects.getBounds(), {
                    checkZoomRange: true,
                    zoomMargin: 30
                });
            }
            // if (map.geoObjects.getCount() > 0) map.setBounds(map.geoObjects.getBounds(), { checkZoomRange: true });
        });
    });

    let currentItinId = null;
    let currentItems = [];

    // Function to start the generator modal
    function startGenerator(id, items) {
        currentItinId = id;
        // Prioritize geocoded coordinates stored in memory
        currentItems = geocodedItineraryItems[id] || items.map(i => ({
            ...i, geocoded_lat: i.lat, geocoded_lng: i.lng
        }));
        document.getElementById('gen-overlay').style.display = 'flex';
    }

    // Function to run the optimization and display the route/schedule
    async function runOptimization() {
        const days = parseInt(document.getElementById('gen-days').value);
        const startTimeStr = document.getElementById('gen-start').value;
        
        document.getElementById('gen-overlay').style.display = 'none';
        
        const map = mapInstances[currentItinId]; 
        if (!map) {
            alert("Map for this trip is still loading. Please wait a second!");
            return;
        }

        map.geoObjects.removeAll();

        const scheduleDiv = document.getElementById(`schedule-${currentItinId}`);
        scheduleDiv.innerHTML = '<h3>Generating Optimized Plan...</h3><p>This might take a moment.</p>';

        currentItems.forEach(item => {
            const placemark = new ymaps.Placemark([item.geocoded_lat || item.lat, item.geocoded_lng || item.lng], {
                balloonContent: `<strong>${item.name}</strong><br>${item.city}<br>${item.description}`,
                iconContent: item.name.substring(0, 1)
            }, { preset: 'islands#darkGreenIcon' });
            map.geoObjects.add(placemark);
        });

        ymaps.ready(async () => { 
            const waypointsForRoute = currentItems.map(item => [item.geocoded_lat || item.lat, item.geocoded_lng || item.lng]);
            const randomColor = '#' + Math.floor(Math.random()*16777215).toString(16);
            
            if (waypointsForRoute.length < 2) {
                scheduleDiv.innerHTML = '<h3>Your Itinerary:</h3><p>Add more items to generate a route!</p>';
                return;
            }

            try {
                const route = await ymaps.route(waypointsForRoute, {
                    mapStateAutoApply: true,
                    multiRoute: true, 
                    routingMode: 'auto'
                }, {
                    routeStrokeColor: randomColor,
                    routeStrokeWidth: 5
                });
                map.geoObjects.add(route); 
                
                const optimizedRoutePoints = route.getWayPoints();
                let scheduleHtml = `<h3 style="color:${randomColor}">Optimized Roadmap:</h3>`;
                let currentTime = new Date();
                const [startHour, startMinute] = startTimeStr.split(':').map(Number);
                currentTime.setHours(startHour, startMinute, 0);

                let lastLocation = null;
                let lunchAdded = false;
                let dinnerAdded = false;
                let dayCounter = 1;

                optimizedRoutePoints.each((point, idx) => {
                    const pointCoords = point.geometry.getCoordinates();
                    const originalItem = currentItems.find(i => 
                        Math.abs((i.geocoded_lat || i.lat) - pointCoords[0]) < 0.0001 && 
                        Math.abs((i.geocoded_lng || i.lng) - pointCoords[1]) < 0.0001
                    ) || currentItems[idx];
                    
                    // --- Multi-Day Logic ---
                    if (currentTime.getHours() >= 22) {
                        dayCounter++;
                        currentTime.setHours(startHour, startMinute, 0);
                        lunchAdded = false;
                        dinnerAdded = false;
                        scheduleHtml += `<h4 style="margin-top:25px; color: #ffe176; border-bottom: 1px solid #ffe176; padding-bottom: 5px;">Day ${dayCounter}</h4>`;
                    }

                    // --- Travel Logic (Inter-city/Country) ---
                    if (lastLocation && (lastLocation.city !== originalItem.city || lastLocation.country !== originalItem.country)) {
                        scheduleHtml += `
                            <div class="schedule-grid" style="border-left: 4px solid #ffffff66; padding-left: 15px; opacity: 0.7; margin-bottom: 10px;">
                                <div class="time-slot">${currentTime.getHours().toString().padStart(2,'0')}:${currentTime.getMinutes().toString().padStart(2,'0')}</div>
                                <div><i class="bi bi-train-front"></i> <em>Travel to ${originalItem.city} (Train/Flight)</em></div>
                            </div>`;
                        currentTime.setHours(currentTime.getHours() + 3); // Allocate 3 hours for travel
                    }

                    // --- Intelligent Meal Allocation ---
                    if (originalItem.type === 'restaurant') {
                        if (currentTime.getHours() < 15) lunchAdded = true;
                        else dinnerAdded = true;
                    } else {
                        if (!lunchAdded && currentTime.getHours() >= 12 && currentTime.getHours() <= 14) {
                            scheduleHtml += `
                                <div class="schedule-grid" style="border-left: 4px solid #ffe176; padding-left: 15px; margin-bottom: 10px;">
                                    <div class="time-slot">${currentTime.getHours().toString().padStart(2,'0')}:${currentTime.getMinutes().toString().padStart(2,'0')}</div>
                                    <div><i class="bi bi-egg-fried"></i> <strong>Lunch Break</strong></div>
                                </div>`;
                            currentTime.setHours(currentTime.getHours() + 1);
                            lunchAdded = true;
                        }

                        if (!dinnerAdded && currentTime.getHours() >= 18) {
                            scheduleHtml += `
                                <div class="schedule-grid" style="border-left: 4px solid #ffe176; padding-left: 15px; margin-bottom: 10px;">
                                    <div class="time-slot">${currentTime.getHours().toString().padStart(2,'0')}:${currentTime.getMinutes().toString().padStart(2,'0')}</div>
                                    <div><i class="bi bi-cup-hot"></i> <strong>Dinner Break</strong></div>
                                </div>`;
                            currentTime.setHours(currentTime.getHours() + 1);
                            dinnerAdded = true;
                        }
                    }

                    // --- Activity Slot ---
                    scheduleHtml += `
                        <div class="schedule-grid" style="border-left: 4px solid ${randomColor}; padding-left: 15px; margin-bottom: 10px;">
                            <div class="time-slot">${currentTime.getHours().toString().padStart(2,'0')}:${currentTime.getMinutes().toString().padStart(2,'0')}</div>
                            <div><strong>${originalItem.name}</strong> <small style="opacity:0.6">(${originalItem.city})</small></div>
                        </div>`;
                    
                    currentTime.setHours(currentTime.getHours() + 2); // Standard 2-hour duration
                    lastLocation = { city: originalItem.city, country: originalItem.country };
                });
                scheduleDiv.innerHTML = scheduleHtml;
                map.setBounds(route.getBounds());

            } catch (error) {
                scheduleDiv.innerHTML = `<h3>Error generating route:</h3><p>${error.message || 'Could not calculate route.'}</p>`;
                console.error("Route generation failed:", error);
            }
        });
    }
