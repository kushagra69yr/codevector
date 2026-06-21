// Premium Dynamic UI Engine: Random Curation Themes & Click Particles
(function() {
    // 1. Curated Premium Color Schemes
    const themes = [
        {
            name: "Cyberpunk Neon",
            primary: "#6366f1", // Indigo
            secondary: "#10b981", // Emerald
            accent: "#a855f7", // Purple
            bgGlow: "rgba(99, 102, 241, 0.3)",
            secGlow: "rgba(16, 185, 129, 0.2)"
        },
        {
            name: "Vibrant Synthwave",
            primary: "#ec4899", // Neon Pink
            secondary: "#06b6d4", // Cyan
            accent: "#8b5cf6", // Violet
            bgGlow: "rgba(236, 72, 153, 0.3)",
            secGlow: "rgba(6, 182, 212, 0.2)"
        },
        {
            name: "Solar Flare",
            primary: "#f97316", // Warm Orange
            secondary: "#facc15", // Amber Gold
            accent: "#ef4444", // Red
            bgGlow: "rgba(249, 115, 22, 0.3)",
            secGlow: "rgba(250, 204, 21, 0.2)"
        },
        {
            name: "Emerald Forest",
            primary: "#14b8a6", // Teal
            secondary: "#84cc16", // Lime Green
            accent: "#10b981", // Emerald
            bgGlow: "rgba(20, 184, 166, 0.3)",
            secGlow: "rgba(132, 204, 22, 0.2)"
        },
        {
            name: "Deep Cosmos",
            primary: "#3b82f6", // Royal Blue
            secondary: "#d946ef", // Fuchsia
            accent: "#6366f1", // Indigo
            bgGlow: "rgba(59, 130, 246, 0.3)",
            secGlow: "rgba(217, 70, 239, 0.2)"
        }
    ];

    // Pick a random theme on page load
    const activeTheme = themes[Math.floor(Math.random() * themes.length)];

    // Inject styles dynamically to document variables
    const root = document.documentElement;
    root.style.setProperty('--primary', activeTheme.primary);
    root.style.setProperty('--secondary', activeTheme.secondary);
    root.style.setProperty('--primary-glow', activeTheme.bgGlow);
    root.style.setProperty('--secondary-glow', activeTheme.secGlow);

    // Apply color to CSS blur blobs dynamically
    const styleEl = document.createElement("style");
    styleEl.innerHTML = `
        .blob-1 { background: radial-gradient(circle, ${activeTheme.primary} 0%, transparent 70%) !important; }
        .blob-2 { background: radial-gradient(circle, ${activeTheme.secondary} 0%, transparent 70%) !important; }
        .blob-3 { background: radial-gradient(circle, ${activeTheme.accent} 0%, transparent 70%) !important; }
    `;
    document.head.appendChild(styleEl);

    // 2. Inject Active Theme Name pill in the header
    document.addEventListener("DOMContentLoaded", () => {
        const brand = document.querySelector(".brand");
        if (brand) {
            const themeBadge = document.createElement("span");
            themeBadge.className = "theme-badge";
            themeBadge.innerHTML = `🎨 ${activeTheme.name}`;
            themeBadge.style.fontSize = "0.75rem";
            themeBadge.style.background = "rgba(255, 255, 255, 0.05)";
            themeBadge.style.border = "1px solid var(--panel-border)";
            themeBadge.style.color = "var(--secondary)";
            themeBadge.style.padding = "0.25rem 0.65rem";
            themeBadge.style.borderRadius = "50px";
            themeBadge.style.marginLeft = "1rem";
            themeBadge.style.fontWeight = "600";
            themeBadge.style.whiteSpace = "nowrap";
            themeBadge.style.textShadow = "0 0 10px var(--secondary-glow)";
            themeBadge.style.animation = "fadeIn 0.5s ease-out";
            brand.appendChild(themeBadge);
        }
    });

    // 3. Canvas Constellation & Click Ripple Engine
    const canvas = document.createElement('canvas');
    canvas.id = 'bg-canvas';
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100vw';
    canvas.style.height = '100vh';
    canvas.style.zIndex = '-1';
    canvas.style.pointerEvents = 'none';
    document.body.appendChild(canvas);

    const ctx = canvas.getContext('2d');
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    const particles = [];
    const particleCount = 80;
    const connectionDistance = 110;
    const mouse = { x: null, y: null, radius: 180 };

    window.addEventListener('mousemove', (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });

    window.addEventListener('mouseout', () => {
        mouse.x = null;
        mouse.y = null;
    });

    // Constellation Particle Class
    class Particle {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.vx = (Math.random() - 0.5) * 0.45;
            this.vy = (Math.random() - 0.5) * 0.45;
            this.radius = Math.random() * 2 + 0.8;
            this.alpha = Math.random() * 0.45 + 0.15;
            this.baseAlpha = this.alpha;
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;

            if (this.x < 0 || this.x > width) this.vx *= -1;
            if (this.y < 0 || this.y > height) this.vy *= -1;

            if (mouse.x !== null) {
                const dx = this.x - mouse.x;
                const dy = this.y - mouse.y;
                const dist = Math.hypot(dx, dy);
                if (dist < mouse.radius) {
                    const force = (mouse.radius - dist) / mouse.radius;
                    const angle = Math.atan2(dy, dx);
                    this.x += Math.cos(angle) * force * 1.6;
                    this.y += Math.sin(angle) * force * 1.6;
                    this.alpha = Math.min(0.85, this.baseAlpha + force * 0.45);
                } else {
                    if (this.alpha > this.baseAlpha) this.alpha -= 0.02;
                }
            } else {
                if (this.alpha > this.baseAlpha) this.alpha -= 0.02;
            }
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(165, 180, 252, ${this.alpha})`;
            ctx.fill();
        }
    }

    // Initialize background particles
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }

    // 4. Click Particle Burst (Click Ripple)
    const bursts = [];

    class BurstParticle {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            const angle = Math.random() * Math.PI * 2;
            const speed = Math.random() * 3 + 1;
            this.vx = Math.cos(angle) * speed;
            this.vy = Math.sin(angle) * speed;
            this.radius = Math.random() * 4 + 2;
            this.life = 1.0;
            this.decay = Math.random() * 0.03 + 0.015;
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;
            this.vx *= 0.98; // Friction
            this.vy *= 0.98;
            this.life -= this.decay;
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius * this.life, 0, Math.PI * 2);
            ctx.fillStyle = hexToRgba(activeTheme.secondary, this.life * 0.7);
            ctx.fill();
        }
    }

    // Helper to convert hex to RGBA
    function hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    // Capture User Clicks anywhere to trigger burst
    window.addEventListener('click', (e) => {
        // Spawn 12 particles per click
        for (let i = 0; i < 12; i++) {
            bursts.push(new BurstParticle(e.clientX, e.clientY));
        }
    });

    // Main Canvas Render loop
    function animate() {
        ctx.clearRect(0, 0, width, height);

        // Render Constellation Background
        for (let i = 0; i < particles.length; i++) {
            const p1 = particles[i];
            p1.update();
            p1.draw();

            for (let j = i + 1; j < particles.length; j++) {
                const p2 = particles[j];
                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const dist = Math.hypot(dx, dy);

                if (dist < connectionDistance) {
                    const alpha = (1 - dist / connectionDistance) * 0.14;
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = hexToRgba(activeTheme.primary, alpha);
                    ctx.lineWidth = 0.75;
                    ctx.stroke();
                }
            }
        }

        // Render Burst Particles
        for (let i = bursts.length - 1; i >= 0; i--) {
            const bp = bursts[i];
            bp.update();
            if (bp.life <= 0) {
                bursts.splice(i, 1);
            } else {
                bp.draw();
            }
        }

        requestAnimationFrame(animate);
    }

    animate();
})();
