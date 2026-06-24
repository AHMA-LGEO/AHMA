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

    function triggerResize() {
        [0, 300, 700, 1400].forEach(function (d) { setTimeout(resizeAll, d); });
    }

    // Trigger 1: window resize (fires in some browsers when display:none -> visible)
    window.addEventListener('resize', triggerResize);

    // Trigger 2: postMessage from WordPress parent tab switcher
    window.addEventListener('message', function (e) {
        if (e.data === 'tab-visible') triggerResize();
    });

    // Trigger 3: poll vw() every 500ms — catches browsers where the resize
    // event does NOT fire on display:none -> visible. When the hidden iframe's
    // parent tab becomes visible, window.innerWidth jumps from 0 to real width.
    // This transition is the guaranteed detection mechanism.
    var prevVw = vw();
    setInterval(function () {
        var cur = vw();
        if (prevVw < 50 && cur >= 50) triggerResize();
        prevVw = cur;
    }, 500);
}());
