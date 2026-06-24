(function () {
    console.log('[resize_fix v4] loaded — url:', window.location.href, '| vw:', window.innerWidth);

    function vw() {
        return window.innerWidth || document.documentElement.clientWidth || 0;
    }

    function resizeAll() {
        console.log('[resize_fix v4] resizeAll called — vw:', vw(), '| plots:', document.querySelectorAll('.js-plotly-plot').length);
        if (vw() < 50) return; // Don't run when iframe still has 0-width
        window.dispatchEvent(new Event('resize')); // Triggers Plotly's responsive handler
        if (!window.Plotly) return;
        document.querySelectorAll('.js-plotly-plot').forEach(function (el) {
            try {
                // Plotly.Plots.resize() does the full recalculation (ticks, labels, legend).
                // relayout({autosize:true}) alone doesn't recalculate label positions.
                if (window.Plotly.Plots && window.Plotly.Plots.resize) {
                    window.Plotly.Plots.resize(el);
                } else {
                    window.Plotly.relayout(el, {autosize: true});
                }
            } catch (e) {}
        });
    }

    // postMessage from WordPress parent (tab re-shown after already being loaded)
    window.addEventListener('message', function (e) {
        if (e.data === 'tab-visible') {
            [0, 300, 800, 1500].forEach(function (d) {
                setTimeout(resizeAll, d);
            });
        }
    });

    // Polling healer: checks every second whether Plotly charts exist AND the viewport
    // has real width, then fires resizeAll. This catches timing races where fixed-delay
    // approaches (postMessage, ResizeObserver) fire before Plotly has rendered.
    // Stops after 5 successful resizes or 60 attempts (~60 seconds).
    var done = 0, attempts = 0;
    (function tick() {
        if (done >= 5 || attempts++ >= 60) return;
        var plots = document.querySelectorAll('.js-plotly-plot').length;
        console.log('[resize_fix v4] tick #' + attempts + ' — vw:', vw(), '| plots:', plots, '| done:', done);
        if (vw() > 50 && plots > 0) {
            resizeAll();
            done++;
        }
        setTimeout(tick, 1000);
    })();
}());
