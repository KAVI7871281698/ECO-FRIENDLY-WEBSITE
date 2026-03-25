document.addEventListener('DOMContentLoaded', () => {
    const calcForm = document.getElementById('carbonCalcForm');
    
    if (calcForm) {
        calcForm.addEventListener('submit', (e) => {
            let isValid = true;
            
            // Clear previous errors
            document.querySelectorAll('.error-msg').forEach(el => el.style.display = 'none');
            
            // Distance Validation
            const distance = document.getElementById('distance');
            if (distance.value <= 0 || isNaN(distance.value)) {
                showError(distance, "Distance must be greater than 0");
                isValid = false;
            }
            
            // Electricity Validation
            const electricity = document.getElementById('electricity');
            if (electricity.value <= 0 || isNaN(electricity.value)) {
                showError(electricity, "Electricity must be greater than 0");
                isValid = false;
            }
            
            // Plastic Validation
            const plastic = document.getElementById('plastic');
            if (plastic.value < 0 || isNaN(plastic.value)) {
                showError(plastic, "Plastic used cannot be negative");
                isValid = false;
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    }
    
    function showError(input, message) {
        const errorMsg = input.parentElement.querySelector('.error-msg');
        if (errorMsg) {
            errorMsg.innerText = message;
            errorMsg.style.display = 'block';
        }
        input.focus();
    }
});
