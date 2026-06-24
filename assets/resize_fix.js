(function () {
    function resizePlots() {
        if (!window.Plotly) return;
        document.querySelectorAll('.js-plotly-plot').forEach(function (el) {
            try { window.Plotly.relayout(el, {autosize: true}); } catch (e) {}
        });
    }

    // Poll every 500ms for 25 seconds — never stop early.
    // Dash renders each chart via a separate async callback, so stopping
    // when the first chart appears leaves every later chart un-relayout'd.
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
