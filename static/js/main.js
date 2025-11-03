/**
 * JEWEllUX - Main JavaScript
 * Обработка взаимодействий пользователя
 */

// ========================================
// SMOOTH SCROLLING
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    initSmoothScrolling();
    initInfiniteCarousel();
});

/**
 * Инициализация плавной прокрутки для якорных ссылок
 */
function initSmoothScrolling() {
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
}

// ========================================
// INFINITE CAROUSEL - Бесконечная карусель
// ========================================
function initInfiniteCarousel() {
    const track = document.getElementById('carouselTrack');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    if (!track || !prevBtn || !nextBtn) return;
    
    const originalSlides = Array.from(track.children);
    
    // Проверка: минимум 3 слайда для корректной работы
    if (originalSlides.length < 3) {
        console.warn('Карусель требует минимум 3 изображения для бесконечной прокрутки');
        return;
    }
    
    // Клонируем слайды для бесконечной прокрутки
    // Добавляем копии в конец
    originalSlides.forEach(slide => {
        const clone = slide.cloneNode(true);
        track.appendChild(clone);
    });
    
    // Добавляем копии в начало
    originalSlides.slice().reverse().forEach(slide => {
        const clone = slide.cloneNode(true);
        track.insertBefore(clone, track.firstChild);
    });
    
    const allSlides = Array.from(track.children);
    const slideWidth = allSlides[0].getBoundingClientRect().width + 15; // +15 для gap
    const totalOriginalSlides = originalSlides.length;
    
    let currentIndex = totalOriginalSlides; // Начинаем с первого оригинального слайда
    let isTransitioning = false;
    
    // Устанавливаем начальную позицию
    updateCarouselPosition(false);
    
    // ========================================
    // НАВИГАЦИЯ
    // ========================================
    
    // Следующий слайд
    nextBtn.addEventListener('click', () => {
        if (isTransitioning) return;
        moveToNext();
    });
    
    // Предыдущий слайд
    prevBtn.addEventListener('click', () => {
        if (isTransitioning) return;
        moveToPrev();
    });
    
    function moveToNext() {
        isTransitioning = true;
        currentIndex++;
        updateCarouselPosition(true);
        
        // Если достигли конца клонов, мгновенно перемещаемся к началу оригиналов
        if (currentIndex >= totalOriginalSlides * 2) {
            setTimeout(() => {
                currentIndex = totalOriginalSlides;
                updateCarouselPosition(false);
                isTransitioning = false;
            }, 500); // Совпадает с transition duration
        } else {
            setTimeout(() => {
                isTransitioning = false;
            }, 500);
        }
    }
    
    function moveToPrev() {
        isTransitioning = true;
        currentIndex--;
        updateCarouselPosition(true);
        
        // Если достигли начала клонов, мгновенно перемещаемся к концу оригиналов
        if (currentIndex < totalOriginalSlides) {
            setTimeout(() => {
                currentIndex = totalOriginalSlides * 2 - 1;
                updateCarouselPosition(false);
                isTransitioning = false;
            }, 500);
        } else {
            setTimeout(() => {
                isTransitioning = false;
            }, 500);
        }
    }
    
    // Обновление позиции карусели
    function updateCarouselPosition(animate) {
        const moveDistance = currentIndex * slideWidth;
        
        if (animate) {
            track.style.transition = 'transform 0.5s ease-in-out';
        } else {
            track.style.transition = 'none';
        }
        
        track.style.transform = `translateX(-${moveDistance}px)`;
    }
    
    // ========================================
    // ПОДДЕРЖКА СВАЙПОВ
    // ========================================
    let touchStartX = 0;
    let touchEndX = 0;
    
    track.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });
    
    track.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    }, { passive: true });
    
    function handleSwipe() {
        if (isTransitioning) return;
        
        const swipeDistance = 50;
        
        if (touchEndX < touchStartX - swipeDistance) {
            // Свайп влево - следующий слайд
            moveToNext();
        } else if (touchEndX > touchStartX + swipeDistance) {
            // Свайп вправо - предыдущий слайд
            moveToPrev();
        }
    }
    
    // ========================================
    // АВТОПРОКРУТКА (опционально)
    // ========================================
    
    // Раскомментируй, если хочешь автоматическую прокрутку
    /*
    let autoplayInterval = setInterval(() => {
        if (!isTransitioning) {
            moveToNext();
        }
    }, 3000); // Каждые 3 секунды
    
    // Остановка автопрокрутки при наведении
    track.addEventListener('mouseenter', () => {
        clearInterval(autoplayInterval);
    });
    
    track.addEventListener('mouseleave', () => {
        autoplayInterval = setInterval(() => {
            if (!isTransitioning) {
                moveToNext();
            }
        }, 3000);
    });
    */
}

// ========================================
// HEADER SCROLL EFFECT
// ========================================
window.addEventListener('scroll', function() {
    const header = document.querySelector('.main-header');
    
    if (!header) return;
    
    if (window.scrollY > 50) {
        header.style.background = 'rgba(26, 26, 26, 0.98)';
    } else {
        header.style.background = 'rgba(26, 26, 26, 0.95)';
    }
});
