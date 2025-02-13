document.addEventListener("DOMContentLoaded", function () {
    const placeSelect = $("select[name='place']");
    const sectorSelect = $("select[name='sector']");
    const rowSelect = $("select[name='row']");
    const seatCountField = document.querySelector("input[name='seat_count']");

    console.log("Script loaded and DOM fully parsed");

    function setupEventHandlers() {
        if (placeSelect.length && sectorSelect.length && rowSelect.length) {
            const sectorUrl = `${window.location.origin}/get-sectors-admin/`;
            const rowUrl = `${window.location.origin}/get-rows-admin/`;

            placeSelect.on("change", function () {
                const placeId = this.value;

                sectorSelect.empty().append("<option value=''>Wybierz sektor</option>");
                rowSelect.empty().append("<option value=''>Wybierz rząd</option>").prop("disabled", true);

                if (placeId) {
                    fetch(`${sectorUrl}?place_id=${placeId}`)
                        .then(response => response.json())
                        .then(data => {
                            data.forEach(sector => {
                                const option = new Option(sector.name, sector.id, false, false);
                                sectorSelect.append(option);
                            });
                            sectorSelect.trigger('change');
                        })
                        .catch(error => console.error("Error fetching sectors:", error));
                }
            });

            sectorSelect.on("change", function () {
                const sectorId = this.value;

                rowSelect.empty().append("<option value=''>Wybierz rząd</option>");

                if (sectorId) {
                    fetch(`${rowUrl}?sector_id=${sectorId}`)
                        .then(response => response.json())
                        .then(data => {
                            data.forEach(row => {
                                const option = new Option(row.name, row.id, false, false);
                                rowSelect.append(option);
                            });
                            rowSelect.prop("disabled", false);
                        })
                        .catch(error => console.error("Error fetching rows:", error));
                }
            });
        } else {
            console.error("Place, Sector, or Row select element not found");
        }
    }

    if (seatCountField) {
        seatCountField.setAttribute("min", "1");
        seatCountField.setAttribute("placeholder", "Liczba miejsc do dodania");
    }

    if (window.location.href.includes('/admin/seats/seat/add/')) {
        setupEventHandlers();
    }
});
