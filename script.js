// Mobile menu toggle
const menuBtn = document.querySelector('.mobile-menu-btn');
const nav = document.querySelector('.nav');

if (menuBtn) {
    menuBtn.addEventListener('click', () => {
        nav.classList.toggle('nav-open');
        menuBtn.classList.toggle('active');
    });
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', (e) => {
        const target = document.querySelector(link.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            nav.classList.remove('nav-open');
            menuBtn.classList.remove('active');
        }
    });
});

// Form submission
const form = document.getElementById('contactForm');
if (form) {
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const btn = form.querySelector('button[type="submit"]');
        const originalText = btn.textContent;
        btn.textContent = 'Отправлено!';
        btn.disabled = true;
        btn.style.opacity = '0.7';
        setTimeout(() => {
            btn.textContent = originalText;
            btn.disabled = false;
            btn.style.opacity = '1';
            form.reset();
        }, 3000);
    });
}

// Header shadow on scroll
const header = document.querySelector('.header');
window.addEventListener('scroll', () => {
    if (window.scrollY > 10) {
        header.style.boxShadow = '0 2px 20px rgba(0,0,0,0.08)';
    } else {
        header.style.boxShadow = 'none';
    }
});

// Animate elements on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -40px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = entry.target.dataset.transform || 'translateY(0)';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.querySelectorAll('.service-card-wide, .portfolio-card, .why-card, .process-step').forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = `opacity 0.5s ease ${i * 0.05}s, transform 0.5s ease ${i * 0.05}s`;
    observer.observe(el);
});
