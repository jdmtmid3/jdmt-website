/* =========================
   MOBILE MENU TOGGLE
========================= */
const menuBtn = document.getElementById("menuBtn");
const mobilePanel = document.getElementById("mobilePanel");

if (menuBtn && mobilePanel) {
    menuBtn.addEventListener("click", () => {
        mobilePanel.classList.toggle("show");
    });
}

/* =========================
   HERO SLIDER
========================= */
const slides = document.querySelectorAll(".slide");
const dots = document.querySelectorAll(".dot");

let current = 0;

function showSlide(index) {
    if (!slides.length) return;

    slides.forEach((slide, i) => {
        slide.classList.toggle("active", i === index);
    });

    dots.forEach((dot, i) => {
        dot.classList.toggle("active", i === index);
    });

    current = index;
}

if (dots.length) {
    dots.forEach((dot, i) => {
        dot.addEventListener("click", () => showSlide(i));
    });
}

if (slides.length > 0) {
    setInterval(() => {
        showSlide((current + 1) % slides.length);
    }, 6000);
}

/* =========================
   PARTNER SLIDER
========================= */
const partnerSlides = document.querySelectorAll(".partner-slide");
const partnerDots = document.querySelectorAll(".partner-dots .dot");

let partnerIndex = 0;

function showPartner(index) {
    if (!partnerSlides.length) return;

    partnerSlides.forEach((slide, i) => {
        slide.classList.toggle("active", i === index);
    });

    partnerDots.forEach((dot, i) => {
        dot.classList.toggle("active", i === index);
    });

    partnerIndex = index;
}

if (partnerDots.length) {
    partnerDots.forEach((dot, i) => {
        dot.addEventListener("click", () => showPartner(i));
    });
}

if (partnerSlides.length > 0) {
    setInterval(() => {
        partnerIndex = (partnerIndex + 1) % partnerSlides.length;
        showPartner(partnerIndex);
    }, 4000);
}

/* =========================
   REVEAL ON SCROLL
========================= */
const revealEls = document.querySelectorAll(".reveal");

if (revealEls.length) {
    const io = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("show");
                    io.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.14 },
    );

    revealEls.forEach((el) => io.observe(el));
}

/* =========================
   TEAM SLIDER
========================= */
function scrollTeam(direction) {
    const teamScroll = document.getElementById("teamScroll");
    if (!teamScroll) return;

    const scrollAmount = 300; // Adjust based on card width + gap
    teamScroll.scrollBy({
        left: direction * scrollAmount,
        behavior: "smooth",
    });
}

/* =========================
   CONTACT FORM
========================= */
const contactForm = document.getElementById("contactForm");

if (contactForm) {
    contactForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const formData = new FormData(contactForm);
        const data = {
            name: formData.get("name"),
            email: formData.get("email"),
            project: formData.get("project"),
            message: formData.get("message"),
        };

        const submitBtn = contactForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = "Sending...";
        submitBtn.disabled = true;

        try {
            const response = await fetch("/contact", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (response.ok && result.success) {
                alert("Message sent successfully!");
                contactForm.reset();
            } else {
                alert(
                    result.error || "Failed to send message. Please try again.",
                );
            }
        } catch (error) {
            alert("Error sending message. Please try again.");
            console.error("Error:", error);
        } finally {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    });
}

/* =========================
   COOKIE & EMBED CONSENT
========================= */
const consentKey = "jdmt_cookie_consent_v1";
const cookieBanner = document.getElementById("cookieBanner");
const acceptCookies = document.getElementById("acceptCookies");
const rejectCookies = document.getElementById("rejectCookies");
const contactMap = document.getElementById("contactMap");
const mapConsent = document.getElementById("mapConsent");
const allowMapBtn = document.getElementById("allowMapBtn");

function loadOptionalContent() {
    if (contactMap && !contactMap.src) {
        contactMap.src = contactMap.dataset.src;
    }
    if (mapConsent) mapConsent.hidden = true;
}

function saveConsent(value) {
    localStorage.setItem(consentKey, value);
    if (cookieBanner) cookieBanner.hidden = true;
    if (value === "optional-allowed") loadOptionalContent();
}

const savedConsent = localStorage.getItem(consentKey);
if (!savedConsent && cookieBanner) cookieBanner.hidden = false;
if (savedConsent === "optional-allowed") loadOptionalContent();

acceptCookies?.addEventListener("click", () => saveConsent("optional-allowed"));
rejectCookies?.addEventListener("click", () => saveConsent("necessary-only"));
allowMapBtn?.addEventListener("click", () => saveConsent("optional-allowed"));
