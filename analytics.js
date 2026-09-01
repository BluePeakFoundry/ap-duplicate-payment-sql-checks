(function () {
  function track(name) {
    if (!name || !window.goatcounter || typeof window.goatcounter.count !== 'function') return;
    window.goatcounter.count({ path: 'event/' + name, title: name, event: true });
  }
  document.addEventListener('click', function (event) {
    var target = event.target.closest('[data-analytics-event]');
    if (target) track(target.getAttribute('data-analytics-event'));
  });
}());
