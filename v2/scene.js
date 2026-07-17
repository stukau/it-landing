import * as THREE from 'three';

// «Живой рой»: тысячи частиц пересобираются из фигуры в фигуру —
// лестница step-by-step → растущий график → чат-пузырь → глобус.
const canvas = document.getElementById('hero3d');
const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (canvas && !reduced) {
    initScene();
} else if (canvas) {
    canvas.remove();
}

function initScene() {
    let renderer;
    try {
        renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    } catch (e) {
        canvas.remove();
        return;
    }

    const isMobile = window.matchMedia('(max-width: 900px)').matches;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 50);
    camera.position.set(0, 0, 5.4);

    const N = isMobile ? 2600 : 5200;
    const NY = Math.floor(N * 0.14); // первые NY частиц — жёлтые: в фигурах они собираются в акцентные зоны

    // ---------- Генераторы фигур (каждая — N точек) ----------

    // 1. Дашборд-аналитика: столбики разной высоты + линия тренда с узлами
    function sampleBars() {
        const a = new Float32Array(N * 3);
        const heights = [0.75, 1.35, 0.95, 1.8, 1.25];
        const tops = heights.map((h, b) => new THREE.Vector2(-1.44 + b * 0.72, -1.3 + h + 0.25));
        const lens = [];
        let total = 0;
        for (let s = 0; s < tops.length - 1; s++) {
            const l = tops[s].distanceTo(tops[s + 1]);
            lens.push(l);
            total += l;
        }
        for (let i = 0; i < N; i++) {
            const r = Math.random();
            if (r < 0.72) {
                // столбики
                const b = Math.floor(Math.random() * 5);
                a[i * 3] = -1.44 + b * 0.72 + (Math.random() - 0.5) * 0.5;
                a[i * 3 + 1] = -1.3 + Math.random() * heights[b];
            } else if (r < 0.92) {
                // линия тренда над столбиками
                let d = Math.random() * total;
                let s = 0;
                while (d > lens[s]) { d -= lens[s]; s++; }
                const p = tops[s].clone().lerp(tops[s + 1], d / lens[s]);
                a[i * 3] = p.x + (Math.random() - 0.5) * 0.09;
                a[i * 3 + 1] = p.y + (Math.random() - 0.5) * 0.09;
            } else {
                // узлы на линии
                const p = tops[Math.floor(Math.random() * tops.length)];
                const t = Math.random() * Math.PI * 2;
                const rr = Math.sqrt(Math.random()) * 0.13;
                a[i * 3] = p.x + Math.cos(t) * rr;
                a[i * 3 + 1] = p.y + Math.sin(t) * rr;
            }
            a[i * 3 + 2] = (Math.random() - 0.5) * 0.25;
        }
        return a;
    }

    // 2. Голова робота — AI-агенты
    function sampleRobot() {
        const a = new Float32Array(N * 3);
        const hw = 1.05, hh = 0.82, cr = 0.28; // корпус головы
        const straightW = (hw - cr) * 2, straightH = (hh - cr) * 2;
        const per = straightW * 2 + straightH * 2 + Math.PI * 2 * cr;
        for (let i = 0; i < N; i++) {
            let x, y;
            if (i < NY) {
                // жёлтые: глаза и шарик антенны
                const pick = Math.random();
                if (pick < 0.75) {
                    const side = Math.random() < 0.5 ? -1 : 1;
                    const t = Math.random() * Math.PI * 2;
                    const rr = Math.sqrt(Math.random()) * 0.2;
                    x = side * 0.48 + Math.cos(t) * rr;
                    y = -0.12 + Math.sin(t) * rr;
                } else {
                    const t = Math.random() * Math.PI * 2;
                    const rr = Math.sqrt(Math.random()) * 0.14;
                    x = Math.cos(t) * rr;
                    y = 1.12 + Math.sin(t) * rr;
                }
                a[i * 3] = x;
                a[i * 3 + 1] = y;
                a[i * 3 + 2] = (Math.random() - 0.5) * 0.18;
                continue;
            }
            const r = Math.random();
            if (r < 0.5) {
                // контур головы со скруглёнными углами
                let d = Math.random() * per;
                if (d < straightW) { x = -hw + cr + d; y = hh; }
                else if ((d -= straightW) < straightH) { x = hw; y = hh - cr - d; }
                else if ((d -= straightH) < straightW) { x = hw - cr - d; y = -hh; }
                else if ((d -= straightW) < straightH) { x = -hw; y = -hh + cr + d; }
                else {
                    d -= straightH;
                    const t = d / cr;
                    const corner = Math.floor(t / (Math.PI / 2));
                    const ct = t % (Math.PI / 2);
                    const cx = corner === 0 ? hw - cr : corner === 1 ? -hw + cr : corner === 2 ? -hw + cr : hw - cr;
                    const cy = corner === 0 ? hh - cr : corner === 1 ? hh - cr : corner === 2 ? -hh + cr : -hh + cr;
                    const a0 = corner * Math.PI / 2;
                    x = cx + Math.cos(a0 + ct) * cr;
                    y = cy + Math.sin(a0 + ct) * cr;
                }
                x += (Math.random() - 0.5) * 0.07;
                y += (Math.random() - 0.5) * 0.07;
                y -= 0.25;
            } else if (r < 0.72) {
                // рот-улыбка (дуга)
                const t = Math.PI * 1.15 + Math.random() * Math.PI * 0.7;
                x = Math.cos(t) * 0.42;
                y = -0.32 + Math.sin(t) * 0.3;
            } else if (r < 0.88) {
                // ножка антенны (шарик — жёлтый)
                x = (Math.random() - 0.5) * 0.05;
                y = 0.57 + Math.random() * 0.42;
            } else {
                // уши-датчики по бокам
                const side = Math.random() < 0.5 ? -1 : 1;
                x = side * (1.12 + Math.random() * 0.12);
                y = -0.25 + (Math.random() - 0.5) * 0.5;
            }
            a[i * 3] = x;
            a[i * 3 + 1] = y;
            a[i * 3 + 2] = (Math.random() - 0.5) * 0.18;
        }
        return a;
    }

    // 2. Растущий график со стрелкой
    function sampleChart() {
        const a = new Float32Array(N * 3);
        const pts = [
            new THREE.Vector2(-1.85, -1.25),
            new THREE.Vector2(-0.65, -0.05),
            new THREE.Vector2(0.15, -0.6),
            new THREE.Vector2(1.45, 0.85),
        ];
        // длины сегментов для равномерного распределения
        const lens = [];
        let total = 0;
        for (let s = 0; s < pts.length - 1; s++) {
            const l = pts[s].distanceTo(pts[s + 1]);
            lens.push(l);
            total += l;
        }
        const dir = new THREE.Vector2(1.9, 1.25).sub(pts[3]).normalize();
        const perp = new THREE.Vector2(-dir.y, dir.x);
        for (let i = 0; i < N; i++) {
            if (i >= NY) {
                // линия
                let d = Math.random() * total;
                let s = 0;
                while (d > lens[s]) { d -= lens[s]; s++; }
                const p = pts[s].clone().lerp(pts[s + 1], d / lens[s]);
                a[i * 3] = p.x + (Math.random() - 0.5) * 0.14;
                a[i * 3 + 1] = p.y + (Math.random() - 0.5) * 0.14;
            } else {
                // наконечник стрелки — жёлтый
                const u = Math.random();               // вдоль конуса
                const w = (Math.random() - 0.5) * (1 - u) * 0.5;
                const base = pts[3].clone().addScaledVector(dir, u * 0.62).addScaledVector(perp, w);
                a[i * 3] = base.x;
                a[i * 3 + 1] = base.y;
            }
            a[i * 3 + 2] = (Math.random() - 0.5) * 0.2;
        }
        return a;
    }

    // 4. Мишень — три кольца, жёлтое яблочко
    function sampleTarget() {
        const a = new Float32Array(N * 3);
        for (let i = 0; i < N; i++) {
            const r = Math.random();
            let rad;
            if (i < NY) {
                // яблочко — все жёлтые частицы
                rad = Math.sqrt(Math.random()) * 0.28;
            } else if (r < 0.36) {
                rad = 0.62 + (Math.random() - 0.5) * 0.13;
            } else if (r < 0.75) {
                rad = 1.05 + (Math.random() - 0.5) * 0.13;
            } else {
                rad = 1.48 + (Math.random() - 0.5) * 0.13;
            }
            const t = Math.random() * Math.PI * 2;
            a[i * 3] = Math.cos(t) * rad;
            a[i * 3 + 1] = Math.sin(t) * rad;
            a[i * 3 + 2] = (Math.random() - 0.5) * 0.16;
        }
        return a;
    }

    // 5. Ракета на взлёте — запуск продукта; пламя из жёлтых частиц
    function sampleRocket() {
        const a = new Float32Array(N * 3);
        for (let i = 0; i < N; i++) {
            let x, y;
            if (i < NY) {
                // пламя — капля под соплом, сужается вниз
                const u = Math.random();                 // 0 у сопла, 1 внизу
                const w = (1 - u) * 0.3 + 0.04;
                x = (Math.random() - 0.5) * 2 * w;
                y = -0.72 - u * (0.85 + Math.random() * 0.25);
            } else {
                const r = Math.random();
                if (r < 0.42) {
                    // корпус: контур капсулы с носом
                    const t = Math.random();
                    const side = Math.random() < 0.5 ? -1 : 1;
                    if (t < 0.62) {
                        // борта
                        x = side * 0.42;
                        y = -0.62 + t / 0.62 * 1.35;
                    } else {
                        // нос — дуга к вершине
                        const u = (t - 0.62) / 0.38;
                        x = side * 0.42 * Math.cos(u * Math.PI / 2);
                        y = 0.73 + Math.sin(u * Math.PI / 2) * 0.75;
                    }
                    x += (Math.random() - 0.5) * 0.06;
                    y += (Math.random() - 0.5) * 0.06;
                } else if (r < 0.54) {
                    // иллюминатор — кольцо
                    const t = Math.random() * Math.PI * 2;
                    const rr = 0.24 + (Math.random() - 0.5) * 0.07;
                    x = Math.cos(t) * rr;
                    y = 0.42 + Math.sin(t) * rr;
                } else if (r < 0.78) {
                    // стабилизаторы — треугольники по бокам
                    const side = Math.random() < 0.5 ? -1 : 1;
                    const u = Math.random(), v = Math.random() * (1 - u);
                    x = side * (0.42 + u * 0.42);
                    y = -0.62 + v * 0.75 - u * 0.25;
                } else if (r < 0.9) {
                    // низ корпуса и сопло
                    x = (Math.random() - 0.5) * 0.7;
                    y = -0.62 + (Math.random() - 0.5) * 0.1;
                } else {
                    // редкое заполнение корпуса
                    x = (Math.random() - 0.5) * 0.74;
                    y = -0.5 + Math.random() * 1.2;
                }
            }
            a[i * 3] = x;
            a[i * 3 + 1] = y + 0.25; // приподнять композицию
            a[i * 3 + 2] = (Math.random() - 0.5) * 0.2;
        }
        return a;
    }

    // 6. Чат-пузырь с «печатает…» — боты и AI-ассистенты
    function sampleBubble() {
        const a = new Float32Array(N * 3);
        for (let i = 0; i < N; i++) {
            const r = Math.random();
            let x, y;
            if (r < 0.62) {
                const t = Math.random() * Math.PI * 2;
                const f = 0.9 + Math.random() * 0.1;
                x = Math.cos(t) * 1.5 * f;
                y = 0.25 + Math.sin(t) * 1.0 * f;
            } else if (r < 0.74) {
                const u = Math.random(), v = Math.random() * (1 - u);
                x = -0.55 - u * 0.55 + v * 0.35;
                y = -0.72 - u * 0.75 + v * 0.25;
            } else {
                const c = [-0.55, 0, 0.55][Math.floor(Math.random() * 3)];
                const t = Math.random() * Math.PI * 2;
                const rr = Math.sqrt(Math.random()) * 0.17;
                x = c + Math.cos(t) * rr;
                y = 0.25 + Math.sin(t) * rr;
            }
            a[i * 3] = x;
            a[i * 3 + 1] = y;
            a[i * 3 + 2] = (Math.random() - 0.5) * 0.16;
        }
        return a;
    }

    // 7. Смартфон — мобильные приложения
    function samplePhone() {
        const a = new Float32Array(N * 3);
        const hw = 0.62, hh = 1.15, cr = 0.2; // полуширина, полувысота, радиус угла
        const straightW = (hw - cr) * 2, straightH = (hh - cr) * 2;
        const per = straightW * 2 + straightH * 2 + Math.PI * 2 * cr;
        for (let i = 0; i < N; i++) {
            const r = Math.random();
            let x, y;
            if (r < 0.66) {
                // контур корпуса со скруглёнными углами
                let d = Math.random() * per;
                if (d < straightW) { x = -hw + cr + d; y = hh; }
                else if ((d -= straightW) < straightH) { x = hw; y = hh - cr - d; }
                else if ((d -= straightH) < straightW) { x = hw - cr - d; y = -hh; }
                else if ((d -= straightW) < straightH) { x = -hw; y = -hh + cr + d; }
                else {
                    d -= straightH;
                    const t = d / cr; // 0..2π по четырём углам
                    const corner = Math.floor(t / (Math.PI / 2));
                    const ct = t % (Math.PI / 2);
                    const cx = corner === 0 ? hw - cr : corner === 1 ? -hw + cr : corner === 2 ? -hw + cr : hw - cr;
                    const cy = corner === 0 ? hh - cr : corner === 1 ? hh - cr : corner === 2 ? -hh + cr : -hh + cr;
                    const a0 = corner * Math.PI / 2;
                    x = cx + Math.cos(a0 + ct) * cr;
                    y = cy + Math.sin(a0 + ct) * cr;
                }
                x += (Math.random() - 0.5) * 0.07;
                y += (Math.random() - 0.5) * 0.07;
            } else if (r < 0.74) {
                // «чёлка»-динамик
                x = (Math.random() - 0.5) * 0.5;
                y = 0.92 + (Math.random() - 0.5) * 0.05;
            } else if (r < 0.82) {
                // кнопка-точка внизу
                const t = Math.random() * Math.PI * 2;
                const rr = Math.sqrt(Math.random()) * 0.11;
                x = Math.cos(t) * rr;
                y = -0.88 + Math.sin(t) * rr;
            } else {
                // разреженный «экран»
                x = (Math.random() - 0.5) * 1.0;
                y = (Math.random() - 0.5) * 1.5 + 0.05;
            }
            a[i * 3] = x;
            a[i * 3 + 1] = y;
            a[i * 3 + 2] = (Math.random() - 0.5) * 0.16;
        }
        return a;
    }

    // 8. Шестерёнка — CRM и автоматизация
    function sampleGear() {
        const a = new Float32Array(N * 3);
        const TEETH = 8;
        for (let i = 0; i < N; i++) {
            const r = Math.random();
            let rad, t;
            if (r < 0.55) {
                // тело-кольцо
                t = Math.random() * Math.PI * 2;
                rad = 0.95 + (Math.random() - 0.5) * 0.28;
            } else if (r < 0.85) {
                // зубья
                const tooth = Math.floor(Math.random() * TEETH);
                t = tooth / TEETH * Math.PI * 2 + (Math.random() - 0.5) * 0.3;
                rad = 1.12 + Math.random() * 0.34;
            } else {
                // втулка
                t = Math.random() * Math.PI * 2;
                rad = 0.4 + (Math.random() - 0.5) * 0.12;
            }
            a[i * 3] = Math.cos(t) * rad;
            a[i * 3 + 1] = Math.sin(t) * rad;
            a[i * 3 + 2] = (Math.random() - 0.5) * 0.18;
        }
        return a;
    }

    // 9. Глобус с параллелями — сайты, выход в онлайн
    function sampleGlobe() {
        const a = new Float32Array(N * 3);
        const R = 1.42;
        for (let i = 0; i < N; i++) {
            let z, t;
            if (Math.random() < 0.3) {
                const lat = [-0.6, 0, 0.6][Math.floor(Math.random() * 3)];
                z = lat + (Math.random() - 0.5) * 0.04;
                t = Math.random() * Math.PI * 2;
            } else {
                z = Math.random() * 2 - 1;
                t = Math.random() * Math.PI * 2;
            }
            const rr = Math.sqrt(Math.max(0, 1 - z * z));
            a[i * 3] = Math.cos(t) * rr * R;
            a[i * 3 + 1] = z * R;
            a[i * 3 + 2] = Math.sin(t) * rr * R;
        }
        return a;
    }

    // 10. Галочка в кольце — цель достигнута; галочка из жёлтых частиц
    function sampleCheck() {
        const a = new Float32Array(N * 3);
        // ломаная галочки
        const p0 = new THREE.Vector2(-0.62, 0.02);
        const p1 = new THREE.Vector2(-0.16, -0.44);
        const p2 = new THREE.Vector2(0.72, 0.5);
        const l1 = p0.distanceTo(p1), l2 = p1.distanceTo(p2);
        for (let i = 0; i < N; i++) {
            let x, y;
            if (i < NY) {
                // галочка
                let d = Math.random() * (l1 + l2);
                const p = d < l1
                    ? p0.clone().lerp(p1, d / l1)
                    : p1.clone().lerp(p2, (d - l1) / l2);
                x = p.x + (Math.random() - 0.5) * 0.13;
                y = p.y + (Math.random() - 0.5) * 0.13;
            } else if (Math.random() < 0.85) {
                // кольцо
                const t = Math.random() * Math.PI * 2;
                const rr = 1.3 + (Math.random() - 0.5) * 0.15;
                x = Math.cos(t) * rr;
                y = Math.sin(t) * rr;
            } else {
                // редкое сияние вокруг кольца
                const t = Math.random() * Math.PI * 2;
                const rr = 1.55 + Math.random() * 0.45;
                x = Math.cos(t) * rr;
                y = Math.sin(t) * rr;
            }
            a[i * 3] = x;
            a[i * 3 + 1] = y;
            a[i * 3 + 2] = (Math.random() - 0.5) * 0.16;
        }
        return a;
    }

    // История: наши решения → к чему они приводят
    // глобус (сайты) → бот → смартфон → шестерёнка (CRM) → дашборд → робот (AI) →
    // → рост → мишень → ракета → галочка «готово»
    const shapes = [
        sampleGlobe(), sampleBubble(), samplePhone(), sampleGear(), sampleBars(), sampleRobot(),
        sampleChart(), sampleTarget(), sampleRocket(), sampleCheck(),
    ];
    const GLOBE_IDX = 0;

    // ---------- Частицы ----------
    const positions = new Float32Array(N * 3);
    positions.set(shapes[0]);
    const colors = new Float32Array(N * 3);
    const cA = new THREE.Color(0x8fe0ff);
    const cB = new THREE.Color(0x2ea8d4);
    const cY = new THREE.Color(0xffdf2e);
    const tmp = new THREE.Color();
    for (let i = 0; i < N; i++) {
        if (i < NY) {
            tmp.copy(cY);
        } else {
            tmp.copy(cA).lerp(cB, Math.random());
        }
        colors[i * 3] = tmp.r;
        colors[i * 3 + 1] = tmp.g;
        colors[i * 3 + 2] = tmp.b;
    }

    // случайные параметры каждой частицы: задержка морфа, вектор вихря, фаза дыхания
    const delay = new Float32Array(N);
    const swirl = new Float32Array(N * 3);
    const phase = new Float32Array(N);
    for (let i = 0; i < N; i++) {
        delay[i] = Math.random() * 0.35;
        swirl[i * 3] = (Math.random() - 0.5) * 1.4;
        swirl[i * 3 + 1] = (Math.random() - 0.5) * 1.4;
        swirl[i * 3 + 2] = (Math.random() - 0.5) * 1.4;
        phase[i] = Math.random() * Math.PI * 2;
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    // круглая мягкая точка
    const spriteCanvas = document.createElement('canvas');
    spriteCanvas.width = spriteCanvas.height = 64;
    const ctx = spriteCanvas.getContext('2d');
    const grad = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
    grad.addColorStop(0, 'rgba(255,255,255,1)');
    grad.addColorStop(0.55, 'rgba(255,255,255,0.85)');
    grad.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 64, 64);
    const sprite = new THREE.CanvasTexture(spriteCanvas);

    const points = new THREE.Points(geo, new THREE.PointsMaterial({
        size: 0.055,
        map: sprite,
        vertexColors: true,
        transparent: true,
        opacity: 0.95,
        depthWrite: false,
        sizeAttenuation: true,
        blending: THREE.AdditiveBlending, // свечение на тёмном фоне
    }));
    const group = new THREE.Group();
    group.add(points);
    scene.add(group);

    // ---------- Тайминг ----------
    const HOLD = 2.3;    // фигура держится
    const MORPH = 1.5;   // перестроение
    const PER = HOLD + MORPH;
    const CYCLE = PER * shapes.length;

    function smoothstep(x) {
        x = Math.min(1, Math.max(0, x));
        return x * x * (3 - 2 * x);
    }

    // Размер под контейнер
    function resize() {
        const w = canvas.clientWidth || canvas.parentElement.clientWidth;
        const h = canvas.clientHeight || w;
        renderer.setSize(w, h, false);
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
    }
    resize();
    window.addEventListener('resize', resize);

    // Лёгкий отклик на мышь
    const mouse = { x: 0, y: 0 };
    if (window.matchMedia('(pointer: fine)').matches) {
        window.addEventListener('mousemove', (e) => {
            mouse.x = (e.clientX / window.innerWidth - 0.5) * 2;
            mouse.y = (e.clientY / window.innerHeight - 0.5) * 2;
        }, { passive: true });
    }

    // Рендерим только пока hero на экране
    let inView = true;
    new IntersectionObserver((entries) => {
        inView = entries[0].isIntersecting;
    }).observe(canvas);

    const clock = new THREE.Clock();
    const pos = geo.attributes.position.array;

    function animate() {
        requestAnimationFrame(animate);
        if (!inView || document.hidden) return;

        const T = clock.getElapsedTime();
        const t = T % CYCLE;
        const idx = Math.floor(t / PER);
        const tt = t - idx * PER;
        const from = shapes[idx];
        const to = shapes[(idx + 1) % shapes.length];
        const raw = tt < HOLD ? 0 : (tt - HOLD) / MORPH;

        for (let i = 0; i < N; i++) {
            const j = i * 3;
            // индивидуальная задержка — рой перестраивается волной
            const u = raw === 0 ? 0 : smoothstep((raw * 1.35 - delay[i]) / 1.0);
            const arc = Math.sin(Math.PI * u);

            // дыхание фигуры
            const b = Math.sin(T * 1.3 + phase[i]) * 0.018;

            pos[j]     = from[j]     + (to[j]     - from[j])     * u + swirl[j]     * 0.5 * arc + b;
            pos[j + 1] = from[j + 1] + (to[j + 1] - from[j + 1]) * u + swirl[j + 1] * 0.5 * arc + b;
            pos[j + 2] = from[j + 2] + (to[j + 2] - from[j + 2]) * u + swirl[j + 2] * 0.5 * arc;
        }
        geo.attributes.position.needsUpdate = true;

        // глобус медленно вращается, у остальных фигур поворот плавно возвращается
        const isGlobe = idx === GLOBE_IDX && raw < 0.5;
        if (isGlobe) group.rotation.y += 0.004;
        else group.rotation.y *= 0.97;
        group.rotation.y += mouse.x * 0.0015;
        group.rotation.x = mouse.y * 0.08 + Math.sin(T * 0.3) * 0.02;

        renderer.render(scene, camera);
    }
    animate();
}
