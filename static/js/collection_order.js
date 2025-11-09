/**
 * COLLECTION_ORDER.JS - Скрипты для страницы заказа из коллекции
 * ================================================================
 */

document.addEventListener('DOMContentLoaded', function() {
    
    const form = document.getElementById('collectionOrderForm');
    const sizeSelect = document.getElementById('id_ring_size');
    const commentField = document.querySelector('textarea[name="comment"]');
    
    // Валидация формы перед отправкой
    if (form) {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            // Проверка размера
            if (!sizeSelect.value) {
                e.preventDefault();
                showError(sizeSelect, 'Пожалуйста, выберите размер');
                isValid = false;
            } else {
                clearError(sizeSelect);
            }
            
            // Если выбран индивидуальный размер, проверяем комментарий
            if (sizeSelect.value === 'custom' && !commentField.value.trim()) {
                e.preventDefault();
                showError(commentField, 'Пожалуйста, укажите индивидуальный размер в комментарии');
                isValid = false;
            } else if (sizeSelect.value === 'custom') {
                clearError(commentField);
            }
            
            if (!isValid) {
                // Прокрутка к первой ошибке
                const firstError = form.querySelector('.error-message');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            } else {
                // Показываем индикатор загрузки
                const submitBtn = form.querySelector('.btn-submit');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Оформление...';
                }
            }
        });
    }
    
    // Автоматическая очистка ошибок при изменении
    if (sizeSelect) {
        sizeSelect.addEventListener('change', function() {
            clearError(this);
            
            // Показываем подсказку для индивидуального размера
            if (this.value === 'custom') {
                commentField.focus();
                showHint(commentField, 'Пожалуйста, укажите желаемый размер');
            }
        });
    }
    
    if (commentField) {
        commentField.addEventListener('input', function() {
            if (sizeSelect.value === 'custom') {
                clearError(this);
            }
        });
    }
    
    // Функция показа ошибки
    function showError(element, message) {
        clearError(element);
        
        element.style.borderColor = '#ff6b6b';
        element.style.boxShadow = '0 0 0 3px rgba(255, 107, 107, 0.1)';
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `<i class="bi bi-exclamation-circle"></i> ${message}`;
        
        element.parentNode.appendChild(errorDiv);
        
        // Анимация тряски
        element.style.animation = 'shake 0.5s';
        setTimeout(() => {
            element.style.animation = '';
        }, 500);
    }
    
    // Функция очистки ошибки
    function clearError(element) {
        element.style.borderColor = 'rgba(212, 175, 55, 0.3)';
        element.style.boxShadow = 'none';
        
        const existingError = element.parentNode.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
    }
    
    // Функция показа подсказки
    function showHint(element, message) {
        const existingHint = element.parentNode.querySelector('.custom-hint');
        if (existingHint) {
            existingHint.remove();
        }
        
        const hintDiv = document.createElement('div');
        hintDiv.className = 'form-hint custom-hint';
        hintDiv.innerHTML = `<i class="bi bi-arrow-down"></i> ${message}`;
        hintDiv.style.color = '#d4af37';
        hintDiv.style.fontWeight = '500';
        
        element.parentNode.insertBefore(hintDiv, element);
        
        setTimeout(() => {
            hintDiv.remove();
        }, 3000);
    }
    
    // Анимация появления элементов
    const animatedElements = document.querySelectorAll(
        '.product-summary-card, .order-form-card'
    );
    
    animatedElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 150);
    });
    
    console.log('✨ Collection order page loaded successfully');
});
