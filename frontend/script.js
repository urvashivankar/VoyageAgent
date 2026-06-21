// 1. Mobile Menu Toggle
const menuBtn = document.getElementById('menu-btn');
const mobileMenu = document.getElementById('mobile-menu');

menuBtn.addEventListener('click', () => {
    mobileMenu.classList.toggle('active');
});

// Close mobile menu when a link is clicked
document.querySelectorAll('.mobile-menu a').forEach(link => {
    link.addEventListener('click', () => {
        mobileMenu.classList.remove('active');
    });
});

// 2. Sticky Navbar & Active Link Highlighting
const navbar = document.getElementById('navbar');
const sections = document.querySelectorAll('section');
const navLinks = document.querySelectorAll('.nav-link');

window.addEventListener('scroll', () => {
    // Sticky Navbar
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }

    // Active Link Highlighting
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (scrollY >= (sectionTop - sectionHeight / 3)) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href').includes(current)) {
            link.classList.add('active');
        }
    });
});

// 3. Scroll Reveal Animation (Intersection Observer)
const revealElements = document.querySelectorAll('.reveal');

const revealOptions = {
    threshold: 0.15,
    rootMargin: "0px 0px -50px 0px"
};

const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        
        entry.target.classList.add('active');
        
        // If it's the stats section, trigger counters
        if (entry.target.querySelector('.stat-number')) {
            startCounters();
        }
        
        observer.unobserve(entry.target);
    });
}, revealOptions);

revealElements.forEach(el => {
    revealObserver.observe(el);
});

// 4. Animated Counters
let countersStarted = false;

function startCounters() {
    if (countersStarted) return;
    countersStarted = true;

    const counters = document.querySelectorAll('.stat-number');
    const speed = 200; // The lower the slower

    counters.forEach(counter => {
        const target = +counter.getAttribute('data-target');
        const suffix = counter.getAttribute('data-suffix') || '';
        const inc = target / speed;
        let count = 0;

        const updateCount = () => {
            count += inc;
            if (count < target) {
                counter.innerText = Math.ceil(count) + suffix;
                setTimeout(updateCount, 10);
            } else {
                counter.innerText = target + suffix;
            }
        };

        updateCount();
    });
}

// 5. FAQ Accordion Toggle
const faqItems = document.querySelectorAll('.faq-item');

faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    
    question.addEventListener('click', () => {
        // Close currently active items (optional - makes it an accordion)
        const currentlyActive = document.querySelector('.faq-item.active');
        if (currentlyActive && currentlyActive !== item) {
            currentlyActive.classList.remove('active');
            currentlyActive.querySelector('.faq-answer').style.maxHeight = null;
        }

        // Toggle clicked item
        item.classList.toggle('active');
        const answer = item.querySelector('.faq-answer');
        
        if (item.classList.contains('active')) {
            answer.style.maxHeight = answer.scrollHeight + "px";
        } else {
            answer.style.maxHeight = null;
        }
    });
});

// 6. Fetch Seasonal Destinations
document.addEventListener('DOMContentLoaded', async () => {
    const grid = document.getElementById('trending-destinations-grid');
    if (!grid) return;

    try {
        const API_BASE_URL = 'http://localhost:8000'; // Make sure backend is running
        const response = await fetch(`${API_BASE_URL}/destinations/seasonal`);
        
        if (!response.ok) throw new Error('API Error');
        
        const destinations = await response.json();
        
        grid.innerHTML = destinations.map(dest => `
            <div class="dest-card" onclick="window.location.href='login.html?dest=${dest.id}'">
                <div class="dest-img" style="background-image: url('${dest.hero_image}');"></div>
                <div class="dest-info">
                    <h3>${dest.name}, ${dest.state}</h3>
                    <div class="dest-meta">
                        <span>Budget: ₹${dest.avg_budget.toLocaleString()}</span>
                        <span>${dest.days} Days</span>
                    </div>
                    <p style="font-size: 0.85rem; color: #aaa; margin-top: 0.5rem; line-height: 1.4;">${dest.description}</p>
                </div>
            </div>
        `).join('');
    } catch (err) {
        console.error('Failed to load seasonal destinations:', err);
        grid.innerHTML = `
            <div class="col-span-full text-center py-10">
                <p class="text-red-400">Could not load seasonal destinations. Ensure backend is running.</p>
            </div>
        `;
    }
});
