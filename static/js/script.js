// Общие функции JavaScript для приложения

// Подтверждение удаления автомобиля
function confirmDelete(carId, carName) {
    if (confirm(`Вы уверены, что хотите удалить автомобиль "${carName}"?`)) {
        document.getElementById(`delete-form-${carId}`).submit();
    }
}

// Инициализация всплывающих подсказок Bootstrap
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Предварительный просмотр изображения перед загрузкой
function previewImage(event) {
    const reader = new FileReader();
    reader.onload = function() {
        const output = document.getElementById('image-preview');
        output.src = reader.result;
        output.classList.remove('d-none');
        document.querySelector('.image-preview-container').classList.remove('d-none');
    };
    reader.readAsDataURL(event.target.files[0]);
}