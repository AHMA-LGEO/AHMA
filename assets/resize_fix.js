(function () {
    // Backup resize handler for postMessage from WordPress parent.
    // Primary resize is handled by the Dash clientside_callback in app.py.
    function relayoutAll() {
        if (!window.Plotly) return;
        document.querySelectorAll('.js-plotly-plot').forEach(function (el) {
            try { window.Plotly.relayout(el, {autosize: true}); } catch (e) {}
        });
    }

    window.addEventListener('message', function (e) {
        if (e.data === 'tab-visible') {
            [0, 300, 800, 1500].forEach(function (d) {
                setTimeout(relayoutAll, d);
            });
        }
    });
}());
