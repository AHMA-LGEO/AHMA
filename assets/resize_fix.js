(function () {
    function resizePlots() {
        var graphs = document.querySelectorAll('.js-plotly-plot');
        if (!graphs.length) return false;
        if (window.Plotly) {
            graphs.forEach(function (el) {
                try { window.Plotly.Plots.resize(el); } catch (e) {}
            });
        } else {
            window.dispatchEvent(new Event('resize'));
        }
        return true;
    }

    // Poll every 500ms until Plotly charts appear in the DOM, then resize.
    // Dash renders charts asynchronously via React/callbacks, so window.load
    // fires long before the charts exist.
    var attempts = 0;
    var timer = setInterval(function () {
        if (resizePlots() || ++attempts > 30) clearInterval(timer);
    }, 500);

    // Re-resize when WordPress parent signals this tab just became visible.
    window.addEventListener('message', function (e) {
        if (e.data === 'tab-visible') {
            setTimeout(resizePlots, 300);
        }
    });
}());
