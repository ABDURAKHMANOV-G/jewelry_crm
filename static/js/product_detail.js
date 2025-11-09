/**
 * PRODUCT_DETAIL.JS - Скрипты для детальной страницы товара
 * ===========================================================
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Галерея - переключение главного изображения
    const thumbnails = document.querySelectorAll('.thumbnail');
    const mainImage = document.querySelector('.main-image');
    
    thumbnails.forEach((thumb, index) => {
        thumb.addEventListener('click', function() {
            // Убираем активный класс со всех миниатюр
            thumbnails.forEach(t => t.classList.remove('active'));
            // Добавляем активный класс на текущую
            this.classList.add('active');
            
            // Анимация смены изображения
            mainImage.style.opacity = '0.7';
            setTimeout(() => {
                mainImage.style.opacity = '1';
            }, 200);
        });
    });

    // Плавная прокрутка к секциям
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Анимация появления элементов при скролле
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Наблюдаем за блоками
    const animatedElements = document.querySelectorAll(
        '.story-block, .craftsmanship-block, .specs-card, .care-item, .cta-card'
    );
    
    animatedElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(element);
    });

    // Кнопка "Записаться на просмотр" - модальное окно (placeholder)
    const appointmentBtn = document.querySelector('.btn-secondary');
    if (appointmentBtn) {
        appointmentBtn.addEventListener('click', function(e) {
            e.preventDefault();
            alert('Функция записи на просмотр в разработке.\nПожалуйста, позвоните нам: +7 (999) 999-99-99');
        });
    }

    // Parallax эффект для главного изображения
    let ticking = false;
    window.addEventListener('scroll', function() {
        if (!ticking) {
            window.requestAnimationFrame(function() {
                const scrolled = window.pageYOffset;
                const gallery = document.querySelector('.product-gallery');
                
                if (gallery && window.innerWidth > 1024) {
                    const parallax = scrolled * 0.15;
                    mainImage.style.transform = `translateY(${parallax}px)`;
                }
                
                ticking = false;
            });
            ticking = true;
        }
    });

    // Добавление товара в избранное (placeholder)
    const favoriteBtn = document.createElement('button');
    favoriteBtn.className = 'btn-favorite';
    favoriteBtn.innerHTML = '<i class="bi bi-heart"></i>';
    favoriteBtn.title = 'Добавить в избранное';
    
    const productInfo = document.querySelector('.product-info');
    if (productInfo) {
        favoriteBtn.style.cssText = `
            position: absolute;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: rgba(212, 175, 55, 0.1);
            border: 1px solid rgba(212, 175, 55, 0.3);
            color: #d4af37;
            font-size: 20px;
            cursor: pointer;
            transition: all 0.3s;
        `;
        
        favoriteBtn.addEventListener('click', function() {
            this.classList.toggle('active');
            if (this.classList.contains('active')) {
                this.innerHTML = '<i class="bi bi-heart-fill"></i>';
                this.style.background = '#d4af37';
                this.style.color = '#1a1a1a';
            } else {
                this.innerHTML = '<i class="bi bi-heart"></i>';
                this.style.background = 'rgba(212, 175, 55, 0.1)';
                this.style.color = '#d4af37';
            }
        });
        
        productInfo.style.position = 'relative';
        productInfo.appendChild(favoriteBtn);
    }

    // Копирование ссылки на товар
    const shareBtn = document.createElement('button');
    shareBtn.className = 'btn-share';
    shareBtn.innerHTML = '<i class="bi bi-share"></i>';
    shareBtn.title = 'Поделиться';
    shareBtn.style.cssText = favoriteBtn.style.cssText.replace('right: 20px', 'right: 80px');
    
    shareBtn.addEventListener('click', function() {
        const url = window.location.href;
        navigator.clipboard.writeText(url).then(() => {
            const originalHTML = this.innerHTML;
            this.innerHTML = '<i class="bi bi-check"></i>';
            setTimeout(() => {
                this.innerHTML = originalHTML;
            }, 2000);
        });
    });
    
    if (productInfo) {
        productInfo.appendChild(shareBtn);
    }

    console.log('✨ Product detail page loaded successfully');
});
