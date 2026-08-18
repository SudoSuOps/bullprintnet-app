/* The only client JS on the page. Sections start hidden and fade up once, then
   stop being watched. Nothing else moves except the Edge status dot, which is
   pure CSS.

   Under prefers-reduced-motion this does not run at all — the stylesheet
   already leaves .reveal fully visible, so the page is complete without it. */
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var items = document.querySelectorAll('.reveal');

  // No IntersectionObserver, or motion is unwanted: show everything and stop.
  if (reduce || !('IntersectionObserver' in window)) {
    for (var i = 0; i < items.length; i++) items[i].classList.add('is-in');
    return;
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add('is-in');
      io.unobserve(e.target);
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -6% 0px' });

  items.forEach(function (el) { io.observe(el); });
})();
