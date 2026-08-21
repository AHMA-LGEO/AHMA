(function () {
    // Dash renders links via dcc.Markdown (external sources, e.g. table 9.1/9.3
    // reference links) and html.A - clicking one navigated away in the same tab,
    // replacing the whole dashboard. Force every link to open in a new tab
    // instead, without needing to touch each Markdown/html.A call site.
    function fixLinks() {
        document.querySelectorAll('a[href]').forEach(function (a) {
            if (a.target !== '_blank') {
                a.target = '_blank';
                a.rel = 'noopener noreferrer';
            }
        });
    }

    document.addEventListener('DOMContentLoaded', fixLinks);

    // Dash re-renders page-content on every tab switch / geography change,
    // so keep watching for newly added links rather than fixing once.
    var observer = new MutationObserver(fixLinks);
    observer.observe(document.body, { childList: true, subtree: true });
}());
