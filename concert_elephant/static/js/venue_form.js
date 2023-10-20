function toggleStateField() {
    const countryField = document.getElementById('id_country');
    countryField.addEventListener('change', function() {
        const stateFieldDiv = document.getElementById('state-field');
        if (countryField.value === 'US') {
            stateFieldDiv.style.display = 'block';
        } else {
            stateFieldDiv.style.display = 'none';
        }
    });
    countryField.dispatchEvent(new Event('change'));  // Trigger the change event on page load
}

document.addEventListener('DOMContentLoaded', toggleStateField);
