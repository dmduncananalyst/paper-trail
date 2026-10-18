/* Geographic projection: d3-geo. Natural Earth geometry: world-atlas. */
(() => {
  const figure = document.querySelector('.nationwide-globe');
  if (!figure || !window.d3 || !window.paperTrailGlobeData) return;
  const svg = figure.querySelector('svg');
  const control = figure.querySelector('.globe-toggle');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const projection = d3.geoOrthographic().scale(244).translate([300, 280]).clipAngle(90);
  const path = d3.geoPath(projection);
  const graticule = d3.geoGraticule10();
  const data = window.paperTrailGlobeData;
  const land = svg.querySelector('.globe-land');
  const us = svg.querySelector('.globe-us');
  const grid = svg.querySelector('.globe-grid');
  const pin = svg.querySelector('.globe-pin');
  let paused = reduced.matches, visible = true, frame = 0, last = 0, elapsed = 0;
  function draw() {
    projection.rotate([100 + Math.sin(elapsed / 9000) * 18, -30, 0]);
    land.setAttribute('d', path(data.land));
    us.setAttribute('d', path(data.us));
    grid.setAttribute('d', path(graticule));
    const [x, y] = projection([-118.2437, 34.0522]);
    pin.setAttribute('transform', `translate(${x.toFixed(2)} ${y.toFixed(2)})`);
  }
  function animate(now) {
    frame = 0;
    if (paused || !visible || document.hidden) { last = 0; return; }
    if (!last || now - last >= 45) {
      elapsed += last ? Math.min(now - last, 100) : 0;
      last = now;
      draw();
    }
    frame = requestAnimationFrame(animate);
  }
  function sync() {
    control.hidden = false;
    control.textContent = paused ? 'Play rotation' : 'Pause rotation';
    control.setAttribute('aria-label', paused ? 'Play globe rotation' : 'Pause globe rotation');
    if (paused || !visible || document.hidden) { cancelAnimationFrame(frame); frame = 0; last = 0; }
    else if (!frame) frame = requestAnimationFrame(animate);
  }
  control.addEventListener('click', () => { paused = !paused; sync(); });
  reduced.addEventListener('change', () => { paused = reduced.matches; sync(); });
  document.addEventListener('visibilitychange', sync);
  if ('IntersectionObserver' in window) new IntersectionObserver(entries => {
    visible = entries[0].isIntersecting; sync();
  }, {rootMargin: '80px'}).observe(figure);
  draw(); sync();
})();
