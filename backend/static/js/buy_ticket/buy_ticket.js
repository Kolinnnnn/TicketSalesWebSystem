function calculatePrice() {
    const sectorSelect = document.getElementById('sector');
    const categorySelect = document.getElementById('ticket_category');
    const priceDisplay = document.getElementById('price-display');
    const calculatedPriceDiv = document.getElementById('calculated-price');
    const calculatedPriceField = document.getElementById('calculated_price_field');

    const selectedSector = sectorSelect.options[sectorSelect.selectedIndex];
    const basePrice = parseFloat(selectedSector.getAttribute('data-price')) || 0;
    const category = categorySelect.value;
    let finalPrice = basePrice;

    if (category === 'discount') {
        finalPrice *= 0.5;
    }

    priceDisplay.innerText = `${finalPrice.toFixed(2)} zł`;
    calculatedPriceDiv.style.display = 'block';
    calculatedPriceField.value = finalPrice.toFixed(2);
}

document.getElementById('sector').addEventListener('change', calculatePrice);
document.getElementById('ticket_category').addEventListener('change', calculatePrice);

document.getElementById('sector').addEventListener('change', function() {
    const sectorId = this.value;
    const rowSelect = document.getElementById('row');
    const seatSelect = document.getElementById('seat');

    rowSelect.innerHTML = '<option value="">Select row</option>';
    seatSelect.innerHTML = '<option value="">Select seat</option>';

    if (sectorId) {
        fetch(`/get-rows/?sector_id=${sectorId}`)
            .then(response => response.json())
            .then(data => {
                if (data.rows.length > 0) {
                    data.rows.forEach(function(row) {
                        const option = document.createElement('option');
                        option.value = row.id;
                        option.text = row.name;
                        if (!row.has_seats) {
                            option.disabled = true;
                            option.text += " (No seats available)";
                        }
                        rowSelect.appendChild(option);
                    });
                } else {
                    const option = document.createElement('option');
                    option.value = '';
                    option.text = 'No available rows in this sector';
                    option.disabled = true;
                    rowSelect.appendChild(option);
                }
            });
    }
});

document.getElementById('row').addEventListener('change', function() {
    const rowId = this.value;
    const seatSelect = document.getElementById('seat');

    seatSelect.innerHTML = '<option value="">Select seat</option>';

    if (rowId) {
        fetch(`/get-seats/?row_id=${rowId}`)
            .then(response => response.json())
            .then(data => {
                if (data.seats.length > 0) {
                    data.seats.forEach(function(seat) {
                        const option = document.createElement('option');
                        option.value = seat.id;
                        option.text = seat.name;
                        seatSelect.appendChild(option);
                    });
                } else {
                    const option = document.createElement('option');
                    option.value = '';
                    option.text = 'No available seats in this row';
                    option.disabled = true;
                    seatSelect.appendChild(option);
                }
            })
            .catch(error => {
                console.error("Błąd w pobieraniu miejsc:", error);
                alert("Wystąpił błąd podczas ładowania dostępnych miejsc. Spróbuj ponownie.");
            });
    }
});

document.getElementById('ticket-form').addEventListener('submit', function(event) {
    const ticketCategory = document.getElementById('ticket_category').value;
    const sector = document.getElementById('sector').value;
    const row = document.getElementById('row').value;
    const seat = document.getElementById('seat').value;

    if (!ticketCategory || !sector || !row || !seat) {
        alert('Please select a ticket category, sector, row, and seat before proceeding.');
        event.preventDefault();
    }
});