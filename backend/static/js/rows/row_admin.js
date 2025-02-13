document.addEventListener("DOMContentLoaded", function () {
    const placeSelect = $("select[name='place']");
    const sectorSelect = $("select[name='sector']");
    const rowCountField = document.querySelector("input[name='row_count']");

    console.log("Script loaded and DOM fully parsed");

    function setupEventHandlers() {
        if (placeSelect.length && sectorSelect.length) {
            const sectorUrl = `${window.location.origin}/get-sectors-admin/`;

            placeSelect.on("change", function () {
                const placeId = this.value;

                sectorSelect.empty().append("<option value=''>Wybierz sektor</option>");

                if (placeId) {
                    console.log("Fetching sectors for placeId:", placeId, "URL:", sectorUrl);
                    fetch(`${sectorUrl}?place_id=${placeId}`)
                        .then(response => response.json())
                        .then(data => {
                            console.log("Sectors fetched:", data);
                            data.forEach(sector => {
                                const option = new Option(sector.name, sector.id, false, false);
                                sectorSelect.append(option);
                            });
                            sectorSelect.trigger('change');
                        })
                        .catch(error => console.error("Error fetching sectors:", error));
                }
            });
        } else {
            console.error("Place or Sector select element not found");
        }
    }

    if (rowCountField) {
        rowCountField.setAttribute("min", "1");
        rowCountField.setAttribute("placeholder", "Liczba rzędów do dodania");
    }

    if (window.location.href.includes('/admin/rows/row/add/')) {
        setupEventHandlers();
    }
});
