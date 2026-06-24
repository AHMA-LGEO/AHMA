(function () {
    function relayoutAll() {
        // Dispatch resize so Plotly's own responsive handler recalculates
        // tick positions, axis titles, and legend — relayout alone doesn't do this.
        window.dispatchEvent(new Event('resize'));
        if (!window.Plotly) return;
        document.querySelectorAll('.js-plotly-plot').forEach(function (el) {
            try { window.Plotly.relayout(el, {autosize: true}); } catch (e) {}
        });
    }

    // postMessage from WordPress parent (already-loaded tab re-shown)
    window.addEventListener('message', function (e) {
        if (e.data === 'tab-visible') {
            [0, 300, 800, 1500].forEach(function (d) {
                setTimeout(relayoutAll, d);
            });
        }
    });

    // Self-heal: when this iframe's document goes from 0-width to real width
    // (because the parent tab just became visible), resize all Plotly charts.
    // This fires even when the parent page never sends a postMessage.
    if (window.ResizeObserver) {
        var knownWidth = 0;
        var ro = new ResizeObserver(function (entries) {
            var w = entries[0].contentRect.width;
            if (w > 50 && knownWidth <= 50) {
                [0, 200, 600, 1200].forEach(function (d) {
                    setTimeout(relayoutAll, d);
                });
            }
            knownWidth = w;
        });
        ro.observe(document.documentElement);
    }
}());
