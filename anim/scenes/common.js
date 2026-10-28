// 读取地址参数，写成 CSS 变量（时间点用秒），方便按配音重新对时
(function () {
  const p = new URLSearchParams(location.search);
  const root = document.documentElement;
  p.forEach((v, k) => {
    if (/^t[A-Z0-9]/.test(k)) root.style.setProperty('--' + k, v + 's');
  });
  window.Q = (k, d) => (p.has(k) ? p.get(k) : d);
  window.fillText = () => {
    document.querySelectorAll('[data-q]').forEach((el) => {
      const v = window.Q(el.dataset.q, null);
      if (v !== null) el.textContent = v;
    });
  };
  document.addEventListener('DOMContentLoaded', window.fillText);
})();
document.addEventListener('DOMContentLoaded', () => {
  if (window.Q('preview', null)) document.body.classList.add('opaque');
});
