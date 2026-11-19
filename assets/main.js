// Copy-to-clipboard feedback for code blocks. Everything else works without JS.
document.querySelectorAll('.code button').forEach(function (b) {
  b.addEventListener('click', function () {
    var t = b.closest('.code').querySelector('pre').innerText;
    (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject()).then(function () {
      b.textContent = 'Copied'; setTimeout(function () { b.textContent = 'Copy'; }, 1500);
    }, function () { b.textContent = 'Press Ctrl+C'; setTimeout(function () { b.textContent = 'Copy'; }, 1500); });
  });
});
