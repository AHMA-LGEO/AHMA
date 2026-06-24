(function () {
    function vw() {
        return window.innerWidth || document.documentElement.clientWidth || 0;
    }

    function resizeAll() {
        if (vw() < 50 || !window.Plotly) return;
        document.querySelectorAll('.js-plotly-plot').forEach(function (el) {
            try {
                if (window.Plotly.Plots && window.Plotly.Plots.resize) {
                    window.Plotly.Plots.resize(el);
                } else {
                    window.Plotly.relayout(el, {autosize: true});
                }
            } catch (e) {}
        });
    }

    // PRIMARY: when the parent tab goes from display:none to visible, the iframe
    // viewport changes from 0 → real width, which fires a window resize event.
    window.addEventListener('resize', function () {
        [0, 300, 800, 1500].forEach(function (d) { setTimeout(resizeAll, d); });
    });

    // SECONDARY: postMessage from WordPress parent
    window.addEventListener('message', function (e) {
        if (e.data === 'tab-visible') {
            [0, 300, 800, 1500].forEach(function (d) { setTimeout(resizeAll, d); });
        }
    });

    // TERTIARY: handles the race where the resize event fires before Plotly has
    // rendered. Polls every 2s; once vw is real AND charts exist, resizes and stops.
    var ticks = 0;
    (function tick() {
        if (ticks++ >= 300) return; // 10-minute ceiling
        if (vw() > 50 && document.querySelectorAll('.js-plotly-plot').length > 0) {
            resizeAll();
            return; // stop once we have both real width and rendered charts
        }
        setTimeout(tick, 2000);
    })();
}());
