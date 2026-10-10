const fill = document.getElementById('progress-fill');
const links = [...document.querySelectorAll('.section-nav a')];
const sections = [...document.querySelectorAll('.poem-section')];

function updateProgress() {
  const total = document.documentElement.scrollHeight - window.innerHeight;
  fill.style.width = `${total > 0 ? Math.min(100, window.scrollY / total * 100) : 0}%`;
}
window.addEventListener('scroll', updateProgress, { passive: true });
window.addEventListener('resize', updateProgress);
updateProgress();

const observer = new IntersectionObserver((entries) => {
  const visible = entries.filter((entry) => entry.isIntersecting);
  if (!visible.length) return;
  visible.sort((a, b) => b.intersectionRatio - a.intersectionRatio);
  const id = visible[0].target.id;
  links.forEach((link) => {
    const active = link.getAttribute('href') === `#${id}`;
    link.classList.toggle('active', active);
    if (active) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
}, { rootMargin: '-10% 0px -65% 0px', threshold: 0 });
sections.forEach((section) => observer.observe(section));
