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

// Form submission: opens Telegram with the request pre-filled (no backend on this site)
const form = document.getElementById('contactForm');
if (form) {
    const formMsg = {
        ru: 'Открываем Telegram — нажмите «Отправить»',
        en: 'Opening Telegram — press Send',
        es: 'Abriendo Telegram — pulse Enviar',
        fr: 'Ouverture de Telegram — appuyez sur Envoyer'
    };
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const val = (sel) => { const el = form.querySelector(sel); return el ? el.value.trim() : ''; };
        const lines = ['Заявка с aikrok.com', 'Имя: ' + val('input[type="text"]'), 'Контакт: ' + val('input[type="tel"]')];
        if (val('input[type="email"]')) lines.push('Email: ' + val('input[type="email"]'));
        if (val('textarea')) lines.push('Задача: ' + val('textarea'));
        const url = 'https://t.me/yuri_admin?text=' + encodeURIComponent(lines.join('\n'));
        const win = window.open(url, '_blank');
        if (!win) window.location.href = url;

        const btn = form.querySelector('button[type="submit"]');
        const originalText = btn.textContent;
        btn.textContent = formMsg[document.documentElement.lang] || formMsg.ru;
        btn.disabled = true;
        btn.style.opacity = '0.7';
        setTimeout(() => {
            btn.textContent = originalText;
            btn.disabled = false;
            btn.style.opacity = '1';
        }, 6000);
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

// 3D parallax on hero preview
const heroPreview = document.querySelector('.hero-services-preview');
const heroImage = document.querySelector('.hero-image');
if (heroPreview && heroImage && window.matchMedia('(pointer: fine)').matches && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    heroImage.addEventListener('mousemove', (e) => {
        const r = heroImage.getBoundingClientRect();
        const dx = (e.clientX - r.left) / r.width - 0.5;
        const dy = (e.clientY - r.top) / r.height - 0.5;
        heroPreview.style.transform = `rotateX(${12 - dy * 16}deg) rotateY(${-10 + dx * 18}deg)`;
    });
    heroImage.addEventListener('mouseleave', () => {
        heroPreview.style.transform = '';
    });
}

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

// Portfolio promo video: autoplay (muted) while in view, sound toggle
const promoVideo = document.querySelector('.portfolio-video-el');
if (promoVideo) {
    const soundBtn = promoVideo.parentElement.querySelector('.portfolio-video-sound');
    const videoObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                promoVideo.play().catch(() => {});
            } else {
                promoVideo.pause();
            }
        });
    }, { threshold: 0.4 });
    videoObserver.observe(promoVideo);

    if (soundBtn) {
        soundBtn.addEventListener('click', () => {
            promoVideo.muted = !promoVideo.muted;
            soundBtn.classList.toggle('is-on', !promoVideo.muted);
            const t = (typeof translations !== 'undefined') && translations[document.documentElement.lang];
            if (t) soundBtn.setAttribute('aria-label', promoVideo.muted ? t.p6_sound_on : t.p6_sound_off);
            if (!promoVideo.muted && promoVideo.paused) promoVideo.play().catch(() => {});
        });
    }
}
