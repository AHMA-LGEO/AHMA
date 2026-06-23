// After the page fully loads, trigger a resize so Plotly redraws charts
// at the correct container width (fixes overlap when loaded inside a hidden tab).
window.addEventListener('load', function () {
    setTimeout(function () {
        window.dispatchEvent(new Event('resize'));
    }, 500);
});

// Also respond to a postMessage from the WordPress parent when a tab is clicked,
// in case the iframe was already loaded when the user switches back to this tab.
window.addEventListener('message', function (e) {
    if (e.data === 'tab-visible') {
        setTimeout(function () {
            window.dispatchEvent(new Event('resize'));
        }, 100);
    }
});
