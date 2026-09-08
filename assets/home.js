/* Progressive enhancement: the gallery and launch links work without JavaScript. */
(() => {
  'use strict';
  const $ = (selector) => document.querySelector(selector);
  const all = (selector) => Array.from(document.querySelectorAll(selector));
  const storage = { get(key) { try { return localStorage.getItem(key); } catch { return null; } }, set(key, value) { try { localStorage.setItem(key, value); } catch { /* Restricted storage must not break navigation. */ } } };
  let language = storage.get('sw-language') === 'zh' ? 'zh' : 'en';
  const button = $('#lang');
  const dialog = $('#world-preview');
  const mount = $('#preview-mount');
  let currentWorld = null;
  let lastTrigger = null;
  let slowTimer;
  const scenes = {
    bayline: { title: 'BAYLINE', path: 'bayline.html', description: { en: 'BAYLINE railway simulator', zh: 'BAYLINE 铁路模拟器' } },
    bayport: { title: 'BAYPORT', path: 'airport.html?v=2.1', description: { en: 'BAYPORT v2.1 aircraft-focused airport simulator', zh: 'BAYPORT v2.1 飞机聚焦版机场模拟器' } }
  };
  function applyLanguage() {
    document.documentElement.lang = language === 'zh' ? 'zh-CN' : 'en';
    all('[data-en][data-zh]').forEach(el => { el.textContent = el.dataset[language]; });
    all('[data-alt-en]').forEach(el => { el.alt = el.dataset[language === 'zh' ? 'altZh' : 'altEn']; });
    all('[data-label-en]').forEach(el => { el.setAttribute('aria-label', el.dataset[language === 'zh' ? 'labelZh' : 'labelEn']); });
    button.textContent = language === 'zh' ? 'EN' : '中文';
    button.setAttribute('aria-label', language === 'zh' ? 'Switch to English' : '切换到中文');
    button.setAttribute('lang', language === 'zh' ? 'en' : 'zh-CN');
    document.title = language === 'zh' ? 'Simulated World — 湾区微缩世界' : 'Simulated World — Small worlds, brought to life';
    if (currentWorld) { const frame = mount.querySelector('iframe'); if (frame) frame.title = scenes[currentWorld].description[language]; }
    updateCount();
  }
  function updateCount() {
    const count = all('.world-card').filter(card => !card.hidden).length;
    const label = $('#world-count');
    if (label) label.textContent = language === 'zh' ? `显示 ${count} 个世界，共 2 个` : `Showing ${count} of 2 worlds`;
  }
  button.addEventListener('click', () => { language = language === 'en' ? 'zh' : 'en'; storage.set('sw-language', language); applyLanguage(); });
  all('.filter').forEach(filter => {
    filter.addEventListener('click', () => {
      const category = filter.dataset.filter;
      all('.filter').forEach(item => item.setAttribute('aria-pressed', String(item === filter)));
      all('.world-card').forEach(card => { card.hidden = category !== 'all' && card.dataset.category !== category; });
      updateCount();
    });
  });
  all('.js-only').forEach(el => { el.hidden = false; });
  function closePreview() { if (dialog.open) dialog.close(); }
  if (dialog && typeof dialog.showModal === 'function') {
    all('[data-preview]').forEach(trigger => {
      trigger.hidden = false;
      trigger.addEventListener('click', () => {
        const key = trigger.dataset.preview;
        if (!scenes[key]) return;
        currentWorld = key;
        lastTrigger = trigger;
        const scene = scenes[key];
        $('#preview-title').textContent = scene.title;
        $('#preview-launch').href = scene.path;
        $('#preview-fallback').href = scene.path;
        const frame = document.createElement('iframe');
        frame.title = scene.description[language];
        frame.src = scene.path;
        frame.allow = 'fullscreen';
        frame.setAttribute('allowfullscreen', '');
        frame.referrerPolicy = 'same-origin';
        mount.replaceChildren(frame);
        // No WebGL context or remote dependency is loaded until a preview is requested.
        dialog.showModal();
        document.body.classList.add('preview-open');
        $('#preview-close').focus();
        $('#preview-slow').hidden = true;
        clearTimeout(slowTimer);
        slowTimer = setTimeout(() => { $('#preview-slow').hidden = false; }, 18000);
        frame.addEventListener('load', () => {
          // Catch Escape even when focus is inside the same-origin simulator.
          try { frame.contentWindow.addEventListener('keydown', e => { if (e.key === 'Escape') closePreview(); }); } catch { /* Direct open remains available for cross-origin deployments. */ }
        });
      });
    });
    $('#preview-close').addEventListener('click', closePreview);
    dialog.addEventListener('click', event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) closePreview(); } });
    dialog.addEventListener('close', () => {
      mount.replaceChildren(); // Unload the simulation and its audio/render loop.
      document.body.classList.remove('preview-open');
      currentWorld = null;
      clearTimeout(slowTimer);
      if (lastTrigger) lastTrigger.focus({ preventScroll: true });
    });
  }
  applyLanguage();
})();
