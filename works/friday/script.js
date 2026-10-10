const progressFill = document.getElementById('progress-fill');
const links = [...document.querySelectorAll('.chapter-nav a')];
const chapters = [...document.querySelectorAll('.chapter')];

function updateProgress() {
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const value = scrollable > 0 ? Math.min(100, (window.scrollY / scrollable) * 100) : 0;
  progressFill.style.width = `${value}%`;
}

window.addEventListener('scroll', updateProgress, { passive: true });
window.addEventListener('resize', updateProgress);
updateProgress();

const observer = new IntersectionObserver((entries) => {
  const visible = entries.filter((entry) => entry.isIntersecting);
  if (!visible.length) return;
  visible.sort((a, b) => b.intersectionRatio - a.intersectionRatio);
  const activeId = visible[0].target.id;
  links.forEach((link) => {
    const active = link.getAttribute('href') === `#${activeId}`;
    link.classList.toggle('active', active);
    if (active) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
}, { rootMargin: '-10% 0px -65% 0px', threshold: 0 });
chapters.forEach((chapter) => observer.observe(chapter));
