/**
 * Script principal para el Sistema de Gestión de Cotizaciones y Facturas
 */

document.addEventListener('DOMContentLoaded', function() {
    // Habilitar tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-ocultar mensajes flash después de 5 segundos
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Formatear inputs numéricos como moneda chilena
    const currencyInputs = document.querySelectorAll('.currency-input');
    currencyInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            const value = this.value.replace(/\D/g, '');
            if (value) {
                const formattedValue = new Intl.NumberFormat('es-CL').format(value);
                this.value = formattedValue;
            }
        });

        input.addEventListener('focus', function() {
            this.value = this.value.replace(/\D/g, '');
        });
    });

    // Formatear RUT chileno
    const rutInputs = document.querySelectorAll('.rut-input');
    rutInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            let rut = this.value.replace(/\./g, '').replace('-', '');
            if (rut.length > 1) {
                const dv = rut.slice(-1);
                rut = rut.slice(0, -1);
                
                // Formatear número
                rut = rut.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
                
                // Agregar guión y dígito verificador
                this.value = rut + '-' + dv;
            }
        });
    });

    // Validación de formularios
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });

    // Confirmación para acciones de eliminación
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            if (!confirm('¿Está seguro de que desea eliminar este elemento? Esta acción no se puede deshacer.')) {
                event.preventDefault();
            }
        });
    });

    // Inicializar campos de fecha con la fecha actual
    const fechaInputs = document.querySelectorAll('input[type="date"]');
    fechaInputs.forEach(function(input) {
        if (!input.value) {
            const today = new Date();
            const year = today.getFullYear();
            let month = today.getMonth() + 1;
            let day = today.getDate();
            
            month = month < 10 ? '0' + month : month;
            day = day < 10 ? '0' + day : day;
            
            input.value = `${year}-${month}-${day}`;
        }
    });
});