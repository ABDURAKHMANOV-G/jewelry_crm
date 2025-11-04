// ==========================================
// AUTH.JS - Валидация форм входа и регистрации
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('form[action*="login"]');
    const registerForm = document.querySelector('form[method="POST"]:not([action*="login"])');
    
    // ==========================================
    // LOGIN FORM VALIDATION
    // ==========================================
    if (loginForm) {
        const username = loginForm.querySelector('input[name="username"]');
        const password = loginForm.querySelector('input[name="password"]');
        
        loginForm.addEventListener('submit', function(e) {
            let isValid = true;
            
            // Валидация имени пользователя
            if (!username.value || username.value.trim() === '') {
                showError(username, 'Введите имя пользователя');
                isValid = false;
            } else {
                clearError(username);
            }
            
            // Валидация пароля
            if (!password.value || password.value.trim() === '') {
                showError(password, 'Введите пароль');
                isValid = false;
            } else {
                clearError(password);
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
        
        // Очистка ошибок при вводе
        [username, password].forEach(field => {
            field.addEventListener('input', function() {
                clearError(this);
            });
        });
    }
    
    // ==========================================
    // REGISTER FORM VALIDATION
    // ==========================================
    if (registerForm) {
        const username = registerForm.querySelector('input[name="username"]');
        const firstName = registerForm.querySelector('input[name="first_name"]');
        const lastName = registerForm.querySelector('input[name="last_name"]');
        const email = registerForm.querySelector('input[name="email"]');
        const phone = registerForm.querySelector('input[name="phone"]');
        const password1 = registerForm.querySelector('input[name="password1"]');
        const password2 = registerForm.querySelector('input[name="password2"]');
        
        registerForm.addEventListener('submit', function(e) {
            let isValid = true;
            const errors = [];
            
            // Имя пользователя
            if (!username || !username.value || username.value.trim() === '') {
                showError(username, 'Введите имя пользователя');
                errors.push('Имя пользователя обязательно');
                isValid = false;
            } else if (username.value.length < 3) {
                showError(username, 'Минимум 3 символа');
                errors.push('Имя пользователя должно быть минимум 3 символа');
                isValid = false;
            } else {
                clearError(username);
            }
            
            // Имя
            if (!firstName || !firstName.value || firstName.value.trim() === '') {
                showError(firstName, 'Введите имя');
                errors.push('Имя обязательно');
                isValid = false;
            } else {
                clearError(firstName);
            }
            
            // Фамилия
            if (!lastName || !lastName.value || lastName.value.trim() === '') {
                showError(lastName, 'Введите фамилию');
                errors.push('Фамилия обязательна');
                isValid = false;
            } else {
                clearError(lastName);
            }
            
            // Email
            if (!email || !email.value || email.value.trim() === '') {
                showError(email, 'Введите email');
                errors.push('Email обязателен');
                isValid = false;
            } else if (!isValidEmail(email.value)) {
                showError(email, 'Неверный формат email');
                errors.push('Введите корректный email');
                isValid = false;
            } else {
                clearError(email);
            }
            
            // Пароль
            if (!password1 || !password1.value || password1.value.trim() === '') {
                showError(password1, 'Введите пароль');
                errors.push('Пароль обязателен');
                isValid = false;
            } else if (password1.value.length < 8) {
                showError(password1, 'Минимум 8 символов');
                errors.push('Пароль должен быть минимум 8 символов');
                isValid = false;
            } else {
                clearError(password1);
            }
            
            // Подтверждение пароля
            if (!password2 || !password2.value || password2.value.trim() === '') {
                showError(password2, 'Подтвердите пароль');
                errors.push('Подтверждение пароля обязательно');
                isValid = false;
            } else if (password1 && password1.value !== password2.value) {
                showError(password2, 'Пароли не совпадают');
                errors.push('Пароли должны совпадать');
                isValid = false;
            } else {
                clearError(password2);
            }
            
            if (!isValid) {
                e.preventDefault();
                alert('Пожалуйста, исправьте ошибки в форме:\n\n' + errors.join('\n'));
            }
        });
        
        // Очистка ошибок при вводе
        [username, firstName, lastName, email, phone, password1, password2].forEach(field => {
            if (field) {
                field.addEventListener('input', function() {
                    clearError(this);
                });
            }
        });
    }
});

// ==========================================
// HELPER FUNCTIONS
// ==========================================

function showError(field, message) {
    if (!field) return;
    
    // Красная подсветка
    field.style.borderColor = '#ff5459';
    field.style.background = 'rgba(255, 84, 89, 0.1)';
    
    // Добавляем сообщение об ошибке
    const parent = field.closest('.auth-field');
    if (parent) {
        // Удаляем старую ошибку если есть
        const oldError = parent.querySelector('.auth-error');
        if (oldError) oldError.remove();
        
        // Создаём новую ошибку
        const errorDiv = document.createElement('span');
        errorDiv.className = 'auth-error';
        errorDiv.textContent = message;
        parent.appendChild(errorDiv);
    }
}

function clearError(field) {
    if (!field) return;
    
    // Убираем красную подсветку
    field.style.borderColor = '';
    field.style.background = '';
    
    // Удаляем сообщение об ошибке
    const parent = field.closest('.auth-field');
    if (parent) {
        const error = parent.querySelector('.auth-error');
        if (error) error.remove();
    }
}

function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}
