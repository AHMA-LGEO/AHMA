(function () {
    function resizePlots() {
        // Dispatch window resize so Dash's own responsive handler fires at the React level
        window.dispatchEvent(new Event('resize'));
        // Also call Plotly directly on each chart element
        if (window.Plotly) {
            document.querySelectorAll('.js-plotly-plot').forEach(function (el) {
                try { window.Plotly.Plots.resize(el); } catch (e) {}
            });
        }
    }

    // Run every 500ms for 25 seconds — never stop early.
    // Dash renders each chart via a separate async callback, so stopping
    // when the first chart appears leaves every later chart unsized.
    var n = 0;
    var t = setInterval(function () {
        resizePlots();
        if (++n >= 50) clearInterval(t);
    }, 500);

    // Burst-fire when WordPress parent signals this tab just became visible
    window.addEventListener('message', function (e) {
        if (e.data === 'tab-visible') {
            [0, 300, 800, 1500, 3000].forEach(function (d) {
                setTimeout(resizePlots, d);
            });
        }
    });
}());
