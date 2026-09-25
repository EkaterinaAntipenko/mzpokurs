/* =========================================================
   МЦПО · main.js — только фронтенд-поведение, без бэкенда.
   Всё на data-атрибутах: разметку можно переносить в CMS как есть.
   ========================================================= */
(function () {
  'use strict';

  var doc = document.documentElement;
  doc.classList.remove('no-js');

  // ?static — режим для скриншотов/QA: без анимаций, все картинки сразу
  var isStatic = /[?&]static(?:$|[&=])/.test(window.location.search) || (window.parent !== window && /[?&]static(?:$|[&=])/.test(window.parent.location.search));
  if (isStatic) {
    doc.classList.add('no-js');
    Array.prototype.forEach.call(document.querySelectorAll('img[loading="lazy"]'), function (img) { img.loading = 'eager'; });
  }
  var reduceMotion = isStatic || window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };
  var store = {
    get: function (k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { window.localStorage.setItem(k, v); } catch (e) { /* private mode */ } }
  };
  // Ховер в CSS только для устройств с курсором (@media (hover: hover)) — на телефоне он
  // «залипал», если кнопку зажали и отпустили без нажатия. Отклик на касание даёт :active,
  // а iOS Safari включает :active, только когда на странице слушают касания.
  document.addEventListener('touchstart', function () {}, { passive: true });

  /* ---------- Promo bar (закрытие запоминается) ---------- */
  var promo = $('[data-promo]');
  if (promo) {
    var promoKey = 'mcpo-promo-' + (promo.getAttribute('data-promo') || 'default');
    if (store.get(promoKey) === 'closed') promo.classList.add('is-hidden');
    var promoClose = $('[data-promo-close]', promo);
    if (promoClose) promoClose.addEventListener('click', function () {
      promo.classList.add('is-hidden');
      store.set(promoKey, 'closed');
      // полоса исчезла — сдвиг закреплённой шапки стал меньше
      if (typeof setVar === 'function') setVar();
    });
  }

  /* ---------- Закреплённый верх (промо + шапка): тень, компактный режим, высота в CSS-переменную ---------- */
  var siteTop = $('[data-site-top]');
  function topHeight() { return siteTop ? siteTop.getBoundingClientRect().height : 0; }
  if (siteTop) {
    // Шапка закрепляется со сдвигом вверх ровно на расстояние до строки меню:
    // промо-полоса и верхний ряд уезжают за край, у верха остаётся только
    // строка с каталогом. Высоту в потоке при этом не трогаем — иначе контент
    // подпрыгнул бы на эту же величину в момент закрепления.
    var navRow = $('.header__nav', siteTop);
    var offset = 0;
    var setVar = function () {
      var visible = navRow && navRow.offsetParent !== null;   // на мобильном строка скрыта
      offset = 0;
      if (visible) {
        var r = navRow.getBoundingClientRect(), t = siteTop.getBoundingClientRect();
        offset = Math.max(0, Math.round(r.top - t.top));
      }
      siteTop.style.top = (-offset) + 'px';
      doc.style.setProperty('--site-top-h', Math.round(topHeight() - offset) + 'px');
    };
    var onScroll = function () { siteTop.classList.toggle('is-scrolled', window.scrollY > offset + 4); };
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', function () { setVar(); onScroll(); });
    window.addEventListener('load', function () { setVar(); onScroll(); });
    setVar(); onScroll();
  }

  /* ---------- Якорные ссылки: цель по центру экрана, с учётом закреплённой шапки ---------- */
  function scrollToTarget(el) {
    var top = topHeight();
    var r = el.getBoundingClientRect();
    var free = window.innerHeight - top;
    var y = window.scrollY + r.top - top - Math.max(16, (free - r.height) / 2);
    window.scrollTo({ top: Math.max(0, y), behavior: reduceMotion ? 'auto' : 'smooth' });
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href^="#"]');
    if (!a) return;
    var id = a.getAttribute('href').slice(1);
    var el = id && document.getElementById(id);
    if (!el) return;
    e.preventDefault();
    closeOpenLayers();
    scrollToTarget(el);
    if (history.replaceState) history.replaceState(null, '', '#' + id);
  });
  window.addEventListener('load', function () {
    var el = window.location.hash && document.getElementById(window.location.hash.slice(1));
    if (el) setTimeout(function () { scrollToTarget(el); }, 50);
  });

  /* ---------- Overlays: drawer menu, filters, modal ---------- */
  var lastFocus = null;
  function openLayer(el) {
    if (!el) return;
    lastFocus = document.activeElement;
    el.classList.add('is-open');
    el.removeAttribute('aria-hidden');
    document.body.classList.add('is-locked');
    // окно фильтров: фокус на «Закрыть», а не в поле цены — иначе на телефоне сразу выскакивает клавиатура
    var focusable = el.hasAttribute('data-no-autofocus') ? $('button[data-close]', el)
      : ($('input:not([type=checkbox])', el) || $('button, a, input, select', el));
    if (focusable) setTimeout(function () { focusable.focus(); }, 50);
  }
  function closeLayer(el) {
    if (!el) return;
    el.classList.remove('is-open');
    // колонка фильтров на компьютере остаётся на экране — от скринридеров её не прячем
    if (!(el.classList.contains('catalog__filters') && window.matchMedia('(min-width: 1200px)').matches)) el.setAttribute('aria-hidden', 'true');
    if (!$('.drawer.is-open, .modal.is-open, .catalog__filters.is-open')) document.body.classList.remove('is-locked');
    if (lastFocus) lastFocus.focus();
  }
  $$('[data-open]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      openLayer(document.getElementById(btn.getAttribute('data-open')));
      btn.setAttribute('aria-expanded', 'true');
    });
  });
  $$('[data-close]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      closeLayer(btn.closest('.drawer, .modal, .catalog__filters'));
      $$('[data-open][aria-expanded="true"]').forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });
    });
  });
  function closeOpenLayers() { $$('.drawer.is-open, .modal.is-open, .catalog__filters.is-open').forEach(closeLayer); }

  /* ---------- Меню на телефоне: «Каталог курсов» и «Расписание» раскрываются ---------- */
  $$('.drawer__toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var group = btn.closest('.drawer__group');
      var open = !group.classList.contains('is-open');
      group.classList.toggle('is-open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeOpenLayers(); });

  /* ---------- Поиск из шапки (окно #modal-search): карточки курсов прямо во время ввода ---------- */
  (function () {
    var modal = document.getElementById('modal-search');
    var form = modal && $('[data-search-form]', modal);
    var input = form && $('input[type="search"]', form);
    if (!input) return;
    var idle = $('[data-search-idle]', modal);
    var box = $('[data-search-results]', modal);
    var list = $('[data-search-list]', modal);
    var count = $('[data-search-count]', modal);
    var none = $('[data-search-none]', modal);
    var status = $('[data-search-status]', modal);
    var MIN = 2;          // с одной буквы совпадает полкаталога
    var courses = null;   // assets/js/search-index.js, грузится при первом открытии окна
    var loading = false;
    // Служебные слова не обязаны быть в названии: «курсы массажа» находит курсы массажа
    var STOP = ['курс', 'курсы', 'курса', 'курсов', 'обучение', 'обучения', 'для', 'по', 'и', 'в', 'на', 'с'];

    function norm(s) { return String(s).toLowerCase().replace(/ё/g, 'е'); }
    function words(s) { return norm(s).match(/[a-zа-я0-9]+/g) || []; }
    // Без окончания: «массажа» находит «массаж», «косметологии» — «косметолог»
    function stem(w) {
      for (var i = 0; i < 2 && w.length > 4 && /[аеиоуыэюяйь]$/.test(w); i++) w = w.slice(0, -1);
      return w;
    }
    function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
    function plural(n) {
      var a = n % 10, b = n % 100;
      return a === 1 && b !== 11 ? 'курс' : a >= 2 && a <= 4 && (b < 12 || b > 14) ? 'курса' : 'курсов';
    }

    function prepare(data) {
      courses = data.map(function (c, i) { return { c: c, i: i, w: words(c.t) }; });
    }
    function load() {
      if (courses || loading) return;
      if (window.MZPO_COURSES) { prepare(window.MZPO_COURSES); return; }
      loading = true;
      var s = document.createElement('script');
      s.src = modal.getAttribute('data-search-index') || 'assets/js/search-index.js';
      s.onload = function () { loading = false; prepare(window.MZPO_COURSES || []); render(); };
      s.onerror = function () { loading = false; courses = []; render(); };
      document.head.appendChild(s);
    }
    $$('[data-open="modal-search"]').forEach(function (b) { b.addEventListener('click', load); });
    input.addEventListener('focus', load);

    // Каждое слово запроса — начало какого-то слова названия
    function search(q) {
      var qw = words(q);
      var need = qw.filter(function (w) { return STOP.indexOf(w) < 0; });
      if (!need.length) need = qw;
      var parts = need.map(function (w) { return { w: w, s: stem(w) }; });
      var found = [];
      courses.forEach(function (it) {
        var pos = 0;
        for (var k = 0; k < parts.length; k++) {
          var p = parts[k], at = -1;
          for (var j = 0; j < it.w.length; j++) {
            if (it.w[j].indexOf(p.w) === 0 || it.w[j].indexOf(p.s) === 0) { at = j; break; }
          }
          if (at < 0) return;
          pos += at;
        }
        // выше — курсы, чьё название начинается с запроса, потом совпадения ближе к началу, потом с ценой
        found.push({ it: it, score: (pos === 0 ? 0 : 1000) + pos * 10 + (it.c.p ? 0 : 5) });
      });
      found.sort(function (a, b) { return a.score - b.score || a.it.i - b.it.i; });
      return { items: found.map(function (f) { return f.it.c; }), hl: parts.reduce(function (a, p) { return a.concat(p.w, p.s); }, []) };
    }

    // Подсвечивает совпавшее начало слова
    function highlight(title, hl) {
      var out = '', last = 0, re = /[a-zа-яё0-9]+/gi, m;
      while ((m = re.exec(title))) {
        var w = m[0], n = norm(w), len = 0;
        hl.forEach(function (q) { if (q.length > len && n.indexOf(q) === 0) len = q.length; });
        out += esc(title.slice(last, m.index)) + (len ? '<mark>' + esc(w.slice(0, len)) + '</mark>' + esc(w.slice(len)) : esc(w));
        last = re.lastIndex;
      }
      return out + esc(title.slice(last));
    }

    // Карточка — уменьшенная карточка корзины без крестика
    function card(c, hl) {
      var badges = (c.b || []).map(function (b) {
        // часы — белым бейджем: badge--hours рассчитан на фото
        return '<span class="badge badge--' + (b[0] === 'hours' ? 'count' : esc(b[0])) + '">' + esc(b[1]) + '</span>';
      }).join('');
      var title = highlight(c.t, hl);
      var price = c.p ? '<p class="search-card__price">' + (c.o ? '<span class="search-card__old">' + esc(c.o) + '</span>' : '') +
        '<span class="search-card__now">' + esc(c.p) + '</span></p>' : '';
      return '<article class="search-card' + (c.h ? ' search-card--link' : '') + '" role="listitem">' +
        '<div class="search-card__media"><img src="assets/img/' + esc(c.i) + '.webp" alt="" width="880" height="540" loading="lazy" decoding="async"></div>' +
        '<div class="search-card__info">' +
          (badges ? '<div class="search-card__badges">' + badges + '</div>' : '') +
          '<h3 class="search-card__title">' + (c.h ? '<a href="' + esc(c.h) + '">' + title + '</a>' : title) + '</h3>' +
          (c.m ? '<p class="search-card__meta">' + esc(c.m) + '</p>' : '') +
        '</div>' + price +
        '<a class="btn btn--primary btn--m search-card__btn" role="button" tabindex="0" data-popup="lead" data-popup-title="Записаться на курс">Записаться</a>' +
      '</article>';
    }

    function render() {
      var q = input.value.trim();
      var active = q.length >= MIN;
      idle.hidden = active;
      box.hidden = !active;
      if (!active) { list.innerHTML = ''; status.textContent = ''; return; }
      if (!courses) { load(); count.hidden = false; count.textContent = 'Ищем курсы…'; none.hidden = true; return; }
      var r = search(q);
      var n = r.items.length;
      list.innerHTML = r.items.map(function (c) { return card(c, r.hl); }).join('');
      list.hidden = !n;
      count.hidden = !n;
      count.textContent = n ? 'Найдено ' + n + ' ' + plural(n) : '';
      none.hidden = !!n;
      $('[data-search-query]', none).textContent = q;
      status.textContent = n ? count.textContent : 'Курсов не нашли';
    }
    input.addEventListener('input', render);

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      // TODO backend: переход на страницу результатов (макет «Поиск» в ките) с ?q=
      input.focus();
    });
    // «Очистить» не вызывает input: возвращаем направления сами, курсор остаётся в строке
    form.addEventListener('reset', function () { setTimeout(function () { render(); input.focus(); }, 0); });
  })();

  /* ---------- Tabs (визуальное переключение; фильтрацию подключит бэкенд) ---------- */
  $$('[role="tablist"]').forEach(function (list) {
    var tabs = $$('[role="tab"]', list);
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        tabs.forEach(function (t) { t.setAttribute('aria-selected', 'false'); t.classList.remove('is-active'); t.tabIndex = -1; });
        tab.setAttribute('aria-selected', 'true'); tab.classList.add('is-active'); tab.tabIndex = 0;
        var panelId = tab.getAttribute('aria-controls');
        if (panelId) {
          var panel = document.getElementById(panelId);
          if (panel) {
            tabs.forEach(function (t) { var pp = document.getElementById(t.getAttribute('aria-controls')); if (pp && pp !== panel) pp.hidden = true; });
            panel.hidden = false;
            panel.classList.remove('is-switching'); void panel.offsetWidth; panel.classList.add('is-switching');
          }
        }
      });
      tab.addEventListener('keydown', function (e) {
        var i = tabs.indexOf(tab);
        if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
          e.preventDefault();
          var next = tabs[(i + (e.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length];
          next.focus(); next.click();
        }
      });
    });
  });

  /* ---------- Простая горизонтальная лента: стрелки прокручивают, без зацикливания ---------- */
  $$('[data-scroll]').forEach(function (wrap) {
    var track = $('[data-track]', wrap);
    if (!track) return;
    var prev = $('[data-prev]', wrap), next = $('[data-next]', wrap);
    var step = function () { return Math.max(240, Math.round(track.clientWidth * 0.6)); };
    var sync = function () {
      var max = track.scrollWidth - track.clientWidth;
      if (prev) prev.disabled = track.scrollLeft < 4;
      if (next) next.disabled = track.scrollLeft > max - 4;
    };
    if (prev) prev.addEventListener('click', function () { track.scrollBy({ left: -step(), behavior: 'smooth' }); });
    if (next) next.addEventListener('click', function () { track.scrollBy({ left: step(), behavior: 'smooth' }); });
    track.addEventListener('scroll', function () { requestAnimationFrame(sync); }, { passive: true });
    window.addEventListener('resize', sync);
    sync();
  });

  /* ---------- Carousels: бесконечная лента (стрелки, точки, свайп) ---------- */
  // Как любой зацикленный слайдер: в ленте карточки, которые влезают в экран,
  // и ещё по две за каждым краем. Шаг — лента плавно едет на одну карточку; перед
  // шагом крайняя карточка с дальней стороны переезжает на ближнюю, а прокрутка
  // мгновенно компенсирует перенос. Переносится всегда то, что за краем экрана,
  // поэтому стыка не видно, и у ленты нет ни начала, ни конца. Если карточек
  // меньше, чем «экран + по две за краями», набор дублируется.
  // Ленту двигает только скрипт (класс is-loop): прилипание scroll-snap и плавная
  // прокрутка браузера перехватывали ход на середине, и нажатие терялось.
  $$('[data-carousel]').forEach(function (wrap) {
    var track = $('[data-track]', wrap);
    if (!track) return;
    var prev = $('[data-prev]', wrap), next = $('[data-next]', wrap), dots = $('[data-dots]', wrap);
    var originals = Array.prototype.slice.call(track.children);
    var n = originals.length;
    if (n < 2) { if (dots) dots.hidden = true; return; }
    var BUF = 2;          // карточек за каждым краем
    var DUR = 480;        // мс на шаг
    var eager = false;    // картинки уже грузятся без lazy

    originals.forEach(function (el, i) { el.setAttribute('data-index', i); });
    track.classList.add('is-loop');

    function clone(el) {
      var c = el.cloneNode(true);
      c.setAttribute('aria-hidden', 'true');
      c.tabIndex = -1;
      // клон не должен ловить Tab: оригинал с тем же содержимым уже есть в ленте
      Array.prototype.forEach.call(c.querySelectorAll('a, button, input, select, textarea, [tabindex]'),
        function (f) { f.tabIndex = -1; });
      if (eager) $$('img', c).forEach(function (im) { im.loading = 'eager'; });
      return c;
    }
    function kids() { return Array.prototype.slice.call(track.children); }
    function gap() { return parseFloat(getComputedStyle(track).columnGap) || 0; }
    function stepOf(el) { return el.offsetWidth + gap(); }
    // положение карточки в ленте; прокрутка на x(el) ставит её к левому краю
    function x(el) { return el.offsetLeft - track.firstElementChild.offsetLeft; }

    function fill() {
      var min = Infinity;
      kids().forEach(function (el) { min = Math.min(min, stepOf(el)); });
      var need = Math.ceil(track.clientWidth / Math.max(1, min)) + 1 + BUF * 2;
      for (var guard = 0; track.children.length < need && guard < 12; guard++) {
        originals.forEach(function (el) { track.appendChild(clone(el)); });
      }
    }
    // Ровно BUF карточек перед anchor. Лишние слева уезжают в конец, недостающие
    // берутся с конца; прокрутка сдвигается на ту же величину, и кадр не меняется.
    function rebuffer(anchor) {
      for (var guard = 0; kids().indexOf(anchor) > BUF && guard < 200; guard++) {
        var first = track.firstElementChild, d = stepOf(first);
        track.appendChild(first);
        track.scrollLeft -= d;
      }
      for (guard = 0; kids().indexOf(anchor) < BUF && guard < 200; guard++) {
        var last = track.lastElementChild, d2 = stepOf(last);
        track.insertBefore(last, track.firstElementChild);
        track.scrollLeft += d2;
      }
    }
    // карточки целиком за краем не ловят фокус и клики
    function settle(s) {
      var w = track.clientWidth;
      kids().forEach(function (el) {
        var a = x(el), b = a + el.offsetWidth;
        if (b <= s + 1 || a >= s + w - 1) el.setAttribute('inert', ''); else el.removeAttribute('inert');
      });
    }
    function mark() {
      if (!dots) return;
      var k = +target.getAttribute('data-index');
      $$('span', dots).forEach(function (d, j) { d.classList.toggle('is-active', j === k); });
    }

    var target = originals[0];    // карточка у левого края (или та, к которой едем)
    var raf = 0, from = 0, t0 = 0;
    function ease(p) { return 1 - Math.pow(1 - p, 4); }
    function frame(now) {
      var p = Math.max(0, Math.min(1, (now - t0) / DUR));
      track.scrollLeft = from + (x(target) - from) * ease(p);
      raf = p < 1 ? window.requestAnimationFrame(frame) : 0;
    }
    function stop() { if (raf) { window.cancelAnimationFrame(raf); raf = 0; } }
    // Повторное нажатие во время хода не теряется: лента продолжает путь
    // с того места, где была, уже к следующей карточке.
    function goTo(el) {
      stop();
      target = el;
      rebuffer(target);
      mark();
      settle(x(target));
      if (reduceMotion) { track.scrollLeft = x(target); return; }
      // отсчёт — будто шаг начался кадр назад: иначе на каждом нажатии лента
      // стояла бы один кадр на месте, и быстрое листание подтормаживало
      from = track.scrollLeft; t0 = window.performance.now() - 16;
      raf = window.requestAnimationFrame(frame);
    }
    function go(d) {
      var el = d > 0 ? target.nextElementSibling : target.previousElementSibling;
      if (el) goTo(el);
    }

    function setup() {
      stop();
      fill();
      rebuffer(target);
      track.scrollLeft = x(target);
      settle(track.scrollLeft);
      mark();
    }
    if (dots) {
      dots.innerHTML = '';
      dots.hidden = false;
      for (var i = 0; i < n; i++) dots.appendChild(document.createElement('span'));
    }
    setup();

    if (prev) prev.addEventListener('click', function () { go(-1); });
    if (next) next.addEventListener('click', function () { go(1); });

    // Свайп и перетаскивание мышью: лента идёт за пальцем, после отпускания
    // доезжает до ближайшей карточки в сторону жеста. Вертикальный жест — это
    // прокрутка страницы, его не трогаем.
    var drag = null, dragged = false;
    function nearest() {
      var s = track.scrollLeft, best = target, bd = Infinity;
      kids().forEach(function (el) { var dd = Math.abs(x(el) - s); if (dd < bd) { bd = dd; best = el; } });
      return best;
    }
    track.addEventListener('pointerdown', function (e) {
      if (e.pointerType === 'mouse' && e.button !== 0) return;
      var wasMoving = !!raf;
      stop();
      drag = { x: e.clientX, y: e.clientY, s: track.scrollLeft, id: e.pointerId, moved: false, wasMoving: wasMoving, card: nearest() };
      // отпустить могут и за пределами ленты — ловим на всём окне
      window.addEventListener('pointerup', endDrag, true);
      window.addEventListener('pointercancel', endDrag, true);
    });
    track.addEventListener('pointermove', function (e) {
      if (!drag || e.pointerId !== drag.id) return;
      var dx = e.clientX - drag.x, dy = e.clientY - drag.y;
      if (!drag.moved) {
        if (Math.abs(dx) < 6) return;
        if (Math.abs(dy) > Math.abs(dx)) { endDrag(e); return; }
        drag.moved = true;
        try { track.setPointerCapture(e.pointerId); } catch (err) { /* указатель уже отпущен */ }
        track.classList.add('is-dragging');
      }
      track.scrollLeft = drag.s - dx;
      // длинный жест: запас за краем пополняется на ходу
      var before = track.scrollLeft;
      rebuffer(nearest());
      drag.s += track.scrollLeft - before;
    });
    function endDrag(e) {
      if (!drag || e.pointerId !== drag.id) return;
      var d = drag; drag = null;
      window.removeEventListener('pointerup', endDrag, true);
      window.removeEventListener('pointercancel', endDrag, true);
      track.classList.remove('is-dragging');
      if (!d.moved) { if (d.wasMoving) goTo(target); return; }
      dragged = true;
      window.setTimeout(function () { dragged = false; }, 0);
      // ближайшая карточка, но короткий жест всё равно листает на одну в его сторону
      var dx = e.clientX - d.x, best = nearest();
      if (best === d.card && Math.abs(dx) > 40) best = (dx < 0 ? d.card.nextElementSibling : d.card.previousElementSibling) || best;
      goTo(best);
    }
    // после перетаскивания отпускание кнопки над ссылкой не должно её открывать
    track.addEventListener('click', function (e) { if (dragged) { e.preventDefault(); e.stopPropagation(); } }, true);
    track.addEventListener('dragstart', function (e) { e.preventDefault(); });
    // горизонтальный жест тачпада — один шаг на жест
    var wheelLock = 0;
    track.addEventListener('wheel', function (e) {
      if (Math.abs(e.deltaX) <= Math.abs(e.deltaY) || Math.abs(e.deltaX) < 4) return;
      e.preventDefault();
      var now = Date.now();
      if (now < wheelLock) return;
      wheelLock = now + 600;
      go(e.deltaX > 0 ? 1 : -1);
    }, { passive: false });
    // Tab на карточке у края — подвозим её к началу ленты (только фокус с клавиатуры:
    // клик мышью по кнопке в карточке ленту не двигает)
    track.addEventListener('focusin', function (e) {
      var kb = true;
      try { kb = e.target.matches(':focus-visible'); } catch (err) { /* старый браузер */ }
      var card = e.target.closest('[data-index]');
      if (kb && card && card.parentNode === track && card !== target) goTo(card);
    });

    // Карточки за краем с loading="lazy" въезжали бы пустыми — грузим, как лента подъехала
    var loadAll = function () { eager = true; $$('img[loading="lazy"]', track).forEach(function (im) { im.loading = 'eager'; }); };
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) { loadAll(); io.disconnect(); }
      }, { rootMargin: '600px 0px' });
      io.observe(wrap);
    } else loadAll();

    // на телефоне resize приходит и при скрытии адресной строки — ширина та же, ленту не трогаем
    var lastW = track.clientWidth;
    window.addEventListener('resize', function () {
      if (track.clientWidth === lastW) return;
      lastW = track.clientWidth;
      setup();
    });
    window.addEventListener('load', setup);
  });

  /* ---------- Бегущая галерея («О нас»): копии мозаики грузим заранее ---------- */
  // Ленивая загрузка не видит картинки, спрятанные за краем ленты, и копии
  // въезжали бы в кадр пустыми. Как только лента подъехала к экрану — грузим всё.
  $$('.gallery-band').forEach(function (band) {
    var eager = function () { $$('img[loading="lazy"]', band).forEach(function (img) { img.loading = 'eager'; }); };
    if (!('IntersectionObserver' in window)) { eager(); return; }
    var io = new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting) { eager(); io.disconnect(); }
    }, { rootMargin: '600px 0px' });
    io.observe(band);
  });

  /* ---------- Reveal on scroll + stagger ---------- */
  var reveals = $$('.reveal');
  $$('[data-stagger]').forEach(function (group) {
    $$('.reveal', group).forEach(function (el, i) { el.style.setProperty('--reveal-delay', (i * 0.07) + 's'); });
  });
  if ('IntersectionObserver' in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add('is-visible'); io.unobserve(entry.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* ---------- Счётчики цифр (data-count="350000" data-prefix/suffix) ---------- */
  function formatNum(n) { return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ' '); }
  var counters = $$('[data-count]');
  if ('IntersectionObserver' in window && !reduceMotion) {
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target, target = parseFloat(el.getAttribute('data-count')), start = null;
        var pre = el.getAttribute('data-prefix') || '', suf = el.getAttribute('data-suffix') || '';
        var tick = function (t) {
          if (!start) start = t;
          var p = Math.min(1, (t - start) / 1400), eased = 1 - Math.pow(1 - p, 3);
          el.textContent = pre + formatNum(target * eased) + suf;
          if (p < 1) window.requestAnimationFrame(tick);
        };
        window.requestAnimationFrame(tick);
        co.unobserve(el);
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { co.observe(el); });
  }

  /* ---------- Маска телефона +7 (___) ___-__-__ ---------- */
  $$('input[type="tel"]').forEach(function (input) {
    var format = function () {
      var d = input.value.replace(/\D/g, '');
      if (d.charAt(0) === '8' || d.charAt(0) === '7') d = d.slice(1);
      d = d.slice(0, 10);
      var out = '+7';
      if (d.length) out += ' (' + d.slice(0, 3);
      if (d.length >= 3) out += ')';
      if (d.length > 3) out += ' ' + d.slice(3, 6);
      if (d.length > 6) out += '-' + d.slice(6, 8);
      if (d.length > 8) out += '-' + d.slice(8, 10);
      input.value = d.length ? out : '';
    };
    input.addEventListener('input', format);
    input.addEventListener('focus', function () { if (!input.value) input.value = '+7 ('; });
    input.addEventListener('blur', function () { if (input.value.replace(/\D/g, '').length <= 1) input.value = ''; });
  });

  /* ---------- Формы: валидация + «Спасибо» (без отправки на сервер) ---------- */
  var modal = document.getElementById('modal-success');
  function setError(field, on) { if (field) field.classList.toggle('is-error', on); }
  $$('form[data-lead]').forEach(function (form) {
    var consent = $('input[name="consent"]', form);
    var submit = $('[type="submit"]', form);
    var sync = function () { if (consent && submit) submit.classList.toggle('is-disabled', !consent.checked); };
    if (consent) { consent.addEventListener('change', sync); sync(); }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = true;
      $$('[required]', form).forEach(function (input) {
        var field = input.closest('.field');
        var valid = input.type === 'tel' ? input.value.replace(/\D/g, '').length === 11 : input.value.trim().length > 1;
        if (input.type === 'checkbox') valid = input.checked;
        setError(field, !valid);
        if (!valid && ok) { input.focus(); ok = false; }
      });
      if (!ok) return;
      // TODO backend: отправка данных формы (fetch на endpoint CRM) + цель Метрики
      form.reset(); sync();
      var host = form.closest('.modal');
      if (host) closeLayer(host);
      openLayer(modal);
    });
    $$('input', form).forEach(function (input) {
      input.addEventListener('input', function () { setError(input.closest('.field'), false); });
    });
  });

  /* ---------- «Где нас найти»: адрес → карта этого корпуса ---------- */
  // Интерактивная карта грузится только по действию посетителя (скорость загрузки):
  // по кнопке «Открыть интерактивную карту» — для выбранного адреса — или по нажатию
  // на адрес. На телефоне карта стоит под списком, поэтому после выбора прокручиваем к ней.
  $$('.map-block').forEach(function (block) {
    var box = $('.map-block__map', block);
    var btns = $$('[data-location]', block);
    var loadBtn = $('[data-map-load]', block);
    if (!box || !btns.length) return;
    function show(b) {
      var iframe = $('iframe', box);
      if (!iframe) {
        iframe = document.createElement('iframe');
        box.insertBefore(iframe, box.firstChild);   // до плашек с телефоном и графиком — они остаются сверху
        var pic = $('img', box);
        if (pic) pic.remove();
        if (loadBtn) loadBtn.remove();
      }
      if (iframe.getAttribute('src') !== b.getAttribute('data-map')) iframe.src = b.getAttribute('data-map');
      iframe.title = b.getAttribute('data-map-title') || 'Карта';
    }
    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        btns.forEach(function (x) { x.classList.toggle('is-active', x === b); x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        show(b);
        // прокручиваем, только если карту закрывает шапка или она за краем экрана (телефон)
        var r = box.getBoundingClientRect();
        var covered = siteTop ? Math.max(0, siteTop.getBoundingClientRect().bottom) : 0;
        if (r.top < covered || r.bottom > window.innerHeight) scrollToTarget(box);
      });
    });
    if (loadBtn) loadBtn.addEventListener('click', function () {
      show(btns.filter(function (x) { return x.classList.contains('is-active'); })[0] || btns[0]);
    });
  });

  /* ---------- «Как МЦПО помогает…» на телефоне: вертикальный слайдер ---------- */
  // Карточка у середины экрана в полный размер, остальные уменьшены и приглушены;
  // при прокрутке фокус плавно переходит на следующую. Страница мягко прилипает
  // к карточкам (scroll-snap proximity в CSS), поэтому листается по одной.
  (function () {
    var list = $('[data-focus-list]');
    if (!list || reduceMotion) return;
    var cards = Array.prototype.slice.call(list.children);
    var mq = window.matchMedia('(max-width: 767px)');
    var queued = false;
    function paint() {
      queued = false;
      if (!mq.matches) return;
      var top = topHeight(), h = window.innerHeight - top;
      var focus = top + h / 2;
      cards.forEach(function (c) {
        var r = c.getBoundingClientRect();
        var d = Math.min(1, Math.abs(r.top + r.height / 2 - focus) / (h * 0.7));
        c.style.transform = 'scale(' + (1 - 0.1 * d).toFixed(3) + ')';
        c.style.opacity = (1 - 0.5 * d).toFixed(3);
      });
    }
    function request() { if (!queued) { queued = true; requestAnimationFrame(paint); } }
    function setup() {
      list.classList.toggle('is-focus', mq.matches);
      doc.classList.toggle('has-focus-snap', mq.matches);
      if (mq.matches) paint();
      else cards.forEach(function (c) { c.style.transform = ''; c.style.opacity = ''; });
    }
    window.addEventListener('scroll', request, { passive: true });
    window.addEventListener('resize', request);
    if (mq.addEventListener) mq.addEventListener('change', setup); else mq.addListener(setup);
    setup();
  })();

  /* ---------- Корзина: удаление + пересчёт ---------- */
  function recalcCart() {
    var items = $$('[data-cart-item]');
    var sum = items.reduce(function (s, el) { return s + parseInt(el.getAttribute('data-price'), 10); }, 0);
    $$('[data-cart-sum]').forEach(function (el) { el.textContent = formatNum(sum) + ' ₽'; });
    $$('[data-cart-count]').forEach(function (el) { el.textContent = items.length; });
    var empty = $('[data-cart-empty]');
    if (empty) empty.hidden = items.length > 0;
  }
  $$('[data-cart-remove]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var item = btn.closest('[data-cart-item]');
      item.classList.add('is-removing');
      setTimeout(function () { item.remove(); recalcCart(); }, reduceMotion ? 0 : 340);
    });
  });

  /* ---------- Фильтры каталога: счётчик выбранных ---------- */
  var filters = $('.catalog__filters');
  if (filters) {
    var badges = $$('[data-filter-count]');   // в кнопке «Фильтры (2)» и на значке фильтров (телефон)
    var filterIcon = $('.filter-btn');
    var countChecked = function () {
      var k = $$('input[type=checkbox]:checked', filters).length;
      // при нуле счётчик не показываем: на значке нет кружка, у кнопки — «Фильтры» без «(0)»
      badges.forEach(function (b) { b.textContent = k; (b.closest('[data-filter-count-wrap]') || b).hidden = k === 0; });
      if (filterIcon) filterIcon.setAttribute('aria-label', 'Фильтры, выбрано ' + k);
    };
    filters.addEventListener('change', countChecked);
    countChecked();
  }

  /* ---------- Каталог на телефоне: список направлений вместо ряда вкладок ---------- */
  $$('[data-dir-select]').forEach(function (sel) {
    var value = $('[data-dir-value]', sel.parentNode);
    var tabs = $$('.catalog__tabs [role="tab"]');
    var title = $('.catalog__bar h2');
    function show(text) { if (value) value.textContent = text; if (title) title.textContent = text; }
    sel.addEventListener('change', function () {
      show(sel.value);
      if (tabs[sel.selectedIndex]) tabs[sel.selectedIndex].click();
    });
    // и наоборот: вкладка на планшете/компьютере меняет выбранное в списке
    tabs.forEach(function (tab, i) {
      tab.addEventListener('click', function () { sel.selectedIndex = i; show(sel.value); });
    });
  });

  /* ---------- Sticky CTA на мобильном (после первого экрана) ---------- */
  var sticky = $('.sticky-cta');
  if (sticky) {
    document.body.classList.add('has-sticky-cta');
    var trigger = $('[data-sticky-trigger]') || $('.main > *');
    if ('IntersectionObserver' in window && trigger) {
      new IntersectionObserver(function (entries) {
        sticky.classList.toggle('is-visible', !entries[0].isIntersecting);
      }).observe(trigger);
    } else { sticky.classList.add('is-visible'); }
  }

  /* ---------- Переходы между страницами ----------
     Chrome/Edge 126+: CSS @view-transition (см. base.css), JS не нужен.
     Остальные браузеры: мягкое затухание перед переходом. */
  var supportsVT = window.CSS && CSS.supports && CSS.supports('view-transition-name: none') && 'onpagereveal' in window;
  if (!supportsVT && !reduceMotion) {
    document.addEventListener('click', function (e) {
      var a = e.target.closest('a[href]');
      if (!a || a.target === '_blank' || e.metaKey || e.ctrlKey || e.shiftKey) return;
      var href = a.getAttribute('href');
      if (!href || href.charAt(0) === '#' || /^(tel|mailto|https?):/i.test(href)) return;
      e.preventDefault();
      document.body.classList.add('is-leaving');
      setTimeout(function () { window.location.href = href; }, 200);
    });
    window.addEventListener('pageshow', function () { document.body.classList.remove('is-leaving'); });
  }


  /* ---------- Hero-слайдер: листается только сам; прогресс заполняется за интервал ---------- */
  $$('[data-hero-slider]').forEach(function (slider) {
    var imgs = $$('.hero-slider__img', slider), texts = $$('.hero-slider__text', slider), segs = $$('.hero-progress__seg', slider);
    var n = texts.length; if (n < 2) return;
    var interval = parseInt(slider.getAttribute('data-interval'), 10) || 6000;
    slider.style.setProperty('--hero-interval', interval + 'ms');
    var i = 0, timer = null, started = 0, left = interval;
    imgs.forEach(function (im) { im.loading = 'eager'; });
    function show(k) {
      [imgs, texts, segs].forEach(function (list) { list.forEach(function (el, j) { el.classList.toggle('is-active', j === k); }); });
      texts.forEach(function (t, j) { if (j === k) t.removeAttribute('aria-hidden'); else t.setAttribute('aria-hidden', 'true'); });
      // перезапуск анимации заполнения
      var bar = segs[k] && segs[k].querySelector('i');
      if (bar) { bar.style.animation = 'none'; void bar.offsetWidth; bar.style.animation = ''; }
      // то же для наезда: на втором круге класс вешается на уже показанный кадр,
      // и без сброса анимация не запустилась бы заново
      var pic = imgs[k];
      if (pic) { pic.style.animation = 'none'; void pic.offsetWidth; pic.style.animation = ''; }
    }
    function schedule(ms) { clearTimeout(timer); started = Date.now(); left = ms; timer = setTimeout(next, ms); }
    function next() { i = (i + 1) % n; show(i); schedule(interval); }
    function pause() { if (!timer) return; clearTimeout(timer); timer = null; left = Math.max(0, left - (Date.now() - started)); slider.classList.add('is-paused'); }
    function resume() { if (timer) return; slider.classList.remove('is-paused'); schedule(left); }
    document.addEventListener('visibilitychange', function () { if (document.hidden) pause(); else resume(); });
    if (isStatic) return;
    schedule(interval);
  });

  /* ---------- Карусель преподавателей: по 1 карточке, центральная крупнее, бесконечная ---------- */
  $$('[data-focus-carousel]').forEach(function (wrap) {
    var track = $('[data-track]', wrap);
    var originals = Array.prototype.slice.call(track.children);
    var n = originals.length; if (!n) return;
    // клоны слева и справа для бесшовной прокрутки
    originals.forEach(function (el) { var c = el.cloneNode(true); c.setAttribute('aria-hidden', 'true'); c.tabIndex = -1; track.appendChild(c); });
    originals.slice().reverse().forEach(function (el) { var c = el.cloneNode(true); c.setAttribute('aria-hidden', 'true'); c.tabIndex = -1; track.insertBefore(c, track.firstChild); });
    var items = Array.prototype.slice.call(track.children);
    var idx = n; // первый оригинал
    function render(animate) {
      track.classList.toggle('no-anim', !animate);
      items.forEach(function (el, j) { el.classList.toggle('is-center', j === idx); });
      var vp = track.parentElement.getBoundingClientRect().width;
      var el = items[idx];
      var x = vp / 2 - (el.offsetLeft + el.offsetWidth / 2);
      track.style.transform = 'translateX(' + x + 'px)';
    }
    // текущий сдвиг ленты, в том числе посреди анимации
    function currentX() {
      var m = getComputedStyle(track).transform;
      if (!m || m === 'none') return 0;
      var v = m.slice(m.indexOf('(') + 1, -1).split(',');
      return parseFloat(v.length === 16 ? v[12] : v[4]) || 0;
    }
    // Мгновенный перенос на эквивалентный набор (ровно на его длину — визуально тот же
    // кадр), начиная с того места, где лента сейчас, даже посреди хода.
    function jump(shift) {
      var setW = items[n].offsetLeft - items[0].offsetLeft;
      var x0 = currentX() - (shift / n) * setW;
      track.classList.add('no-anim');
      idx += shift;
      items.forEach(function (el, j) { el.classList.toggle('is-center', j === idx); });
      track.style.transform = 'translateX(' + x0 + 'px)';
      void track.offsetWidth;
    }
    // Новое нажатие во время хода просто перенацеливает CSS-переход: он продолжается
    // с текущего места, без остановки. Раньше ленту сперва ставили в конец прошлого
    // шага — отсюда рывок на середине при быстром листании. К оригиналам [n, 2n)
    // возвращаемся, когда лента остановилась, а посреди хода — только если запас
    // клонов почти кончился.
    function goTo(to) {
      if (to < 2 || to > items.length - 3) {
        var shift = (((to - n) % n + n) % n + n) - to;
        jump(shift);
        to += shift;
      }
      idx = to;
      render(!reduceMotion);
    }
    track.addEventListener('transitionend', function (e) {
      if (e.target !== track || e.propertyName !== 'transform' || (idx >= n && idx < 2 * n)) return;
      jump((((idx - n) % n + n) % n + n) - idx);
    });
    function go(d) { goTo(idx + d); }
    var prev = $('[data-prev]', wrap), next = $('[data-next]', wrap);
    if (prev) prev.addEventListener('click', function () { go(-1); });
    if (next) next.addEventListener('click', function () { go(1); });
    // свайп
    var sx = null;
    track.addEventListener('pointerdown', function (e) { sx = e.clientX; });
    track.addEventListener('pointerup', function (e) { if (sx === null) return; var dx = e.clientX - sx; sx = null; if (Math.abs(dx) > 40) go(dx < 0 ? 1 : -1); });
    track.addEventListener('click', function (e) { var card = e.target.closest('.teacher'); if (card && !card.classList.contains('is-center')) { e.preventDefault(); goTo(items.indexOf(card)); } });
    window.addEventListener('resize', function () { render(false); });
    window.addEventListener('load', function () { render(false); });
    render(false);
  });

  /* ---------- Аккордеон: плавное открытие/закрытие, в группе [data-accordion] открыт только один ---------- */
  function animateDetails(d, open) {
    var summary = d.querySelector('summary');
    if (d._anim) { var a = d._anim; d._anim = null; a.cancel(); d.style.overflow = ''; }
    clearTimeout(d._t);
    d._target = open;
    var startH = d.offsetHeight;
    if (open) d.open = true;
    var border = d.offsetHeight - d.clientHeight;
    var endH = open ? d.scrollHeight + border : summary.offsetHeight + border;
    if (reduceMotion || !d.animate) { if (!open) d.open = false; return; }
    d.style.overflow = 'hidden';
    var anim = d.animate({ height: [startH + 'px', endH + 'px'] }, { duration: 320, easing: 'cubic-bezier(0.22, 1, 0.36, 1)' });
    d._anim = anim;
    var done = function () { if (d._anim !== anim) return; clearTimeout(d._t); d._anim = null; d.style.overflow = ''; if (!open) d.open = false; anim.cancel(); };
    anim.onfinish = done;
    clearTimeout(d._t); d._t = setTimeout(done, 360); // страховка, если событие анимации не придёт
  }
  $$('details.module').forEach(function (d) {
    d.addEventListener('click', function (e) {
      if (e.target.closest('summary')) return;
      if (d.open && !d._anim) animateDetails(d, false);
    });
  });
  $$('details.faq, details.module').forEach(function (d) {
    var summary = d.querySelector('summary');
    summary.addEventListener('click', function (e) {
      e.preventDefault();
      var willOpen = !(d._anim ? d._target : d.open);
      var group = d.closest('[data-accordion]');
      if (willOpen && group) $$('details[open]', group).forEach(function (o) { if (o !== d) animateDetails(o, false); });
      animateDetails(d, willOpen);
    });
  });


  /* ---------- Всплывающая форма заявки [data-popup="lead"] ---------- */
  var leadModal = document.getElementById('modal-lead');
  function popupTitle(btn) {
    var t = (btn.textContent || '').toLowerCase();
    if (t.indexOf('звон') > -1) return 'Заказать звонок';
    if (t.indexOf('подобрать') > -1) return 'Подобрать курс';
    if (t.indexOf('бесплатно') > -1 || btn.closest('.event')) return 'Записаться на мероприятие';
    return 'Записаться на курс';
  }
  function openPopup(btn) {
    if (!leadModal) return;
    var title = leadModal.querySelector('[data-popup-title]');
    if (title) title.textContent = btn.getAttribute('data-popup-title') || popupTitle(btn);
    closeOpenLayers();
    openLayer(leadModal);
  }
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-popup]');
    if (!btn) return;
    e.preventDefault();
    openPopup(btn);
  });
  document.addEventListener('keydown', function (e) {
    var btn = e.target.closest && e.target.closest('[data-popup]');
    if (btn && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); openPopup(btn); }
  });

  /* ---------- Выпадающий каталог: факультет → направление → курс ---------- */
  (function () {
    var root = $('[data-mega-root]');
    var mega = root && $('[data-mega]', root);
    var trigger = root && $('[data-mega-trigger]', root);
    if (!mega || !trigger) return;

    var colFac = $('.mega__col--fac', mega);
    var colDir = $('.mega__col--dir', mega);
    var colCourse = $('.mega__col--course', mega);
    var media = $('[data-mega-img]', mega);
    var timer = null;
    // Картинка показывает самый глубокий уровень, на котором сейчас курсор
    var level = { fac: null, dir: null, course: null };

    function setImg(name) {
      if (!media || !name) return;
      var src = 'assets/img/' + name + '.webp';
      if (media.getAttribute('src') === src) return;
      if (reduceMotion) { media.src = src; return; }
      media.classList.add('is-swapping');
      var pre = new Image();
      pre.onload = pre.onerror = function () { media.src = src; media.classList.remove('is-swapping'); };
      pre.src = src;
    }
    function paint() { setImg(level.course || level.dir || level.fac); }

    function showCourses(did) {
      $$('.mega__list', colCourse).forEach(function (ul) { ul.classList.toggle('is-shown', ul.getAttribute('data-courses') === did); });
    }
    function selectFac(item) {
      if (!item.classList.contains('is-active')) {
        $$('.mega__item', colFac).forEach(function (a) { a.classList.toggle('is-active', a === item); });
        var fid = item.getAttribute('data-fac');
        $$('.mega__list', colDir).forEach(function (ul) { ul.classList.toggle('is-shown', ul.getAttribute('data-dirs') === fid); });
        var first = colDir.querySelector('.mega__list.is-shown .mega__item');
        $$('.mega__item', colDir).forEach(function (a) { a.classList.toggle('is-active', a === first); });
        showCourses(first ? first.getAttribute('data-dir') : null);
      }
      level.fac = item.getAttribute('data-img'); level.dir = null; level.course = null; paint();
    }
    function selectDir(item) {
      if (!item.classList.contains('is-active')) {
        $$('.mega__item', colDir).forEach(function (a) { a.classList.toggle('is-active', a === item); });
        showCourses(item.getAttribute('data-dir'));
      }
      level.dir = item.getAttribute('data-img'); level.course = null; paint();
    }

    mega.addEventListener('mouseover', function (e) {
      var item = e.target.closest && e.target.closest('.mega__item');
      if (!item) return;
      if (item.hasAttribute('data-fac')) selectFac(item);
      else if (item.hasAttribute('data-dir')) selectDir(item);
      else { level.course = item.getAttribute('data-img'); paint(); }
    });

    // Идемпотентно: раньше был ранний выход при !hidden — и если увести курсор и
    // вернуться, пока ещё не отработало отложенное скрытие, панель оставалась
    // видимой в потоке, но без класса is-open, то есть прозрачной.
    function open() {
      clearTimeout(timer);
      if (mega.hidden) {
        mega.hidden = false;
        void mega.offsetWidth; // пересчёт раскладки, чтобы переход отыграл с нуля
      }
      trigger.setAttribute('aria-expanded', 'true');
      mega.classList.add('is-open');
    }
    function close() {
      clearTimeout(timer);
      mega.classList.remove('is-open');
      trigger.setAttribute('aria-expanded', 'false');
      timer = setTimeout(function () { mega.hidden = true; }, reduceMotion ? 0 : 300);
    }
    function closeSoon() { clearTimeout(timer); timer = setTimeout(close, 160); }

    trigger.addEventListener('mouseenter', open);
    trigger.addEventListener('focus', open);
    trigger.addEventListener('mouseleave', closeSoon);
    mega.addEventListener('mouseenter', function () { clearTimeout(timer); });
    mega.addEventListener('mouseleave', closeSoon);
    // по клику уходим на страницу каталога — убираем панель сразу, без затухания,
    // иначе она попадает в снимок перехода между страницами
    trigger.addEventListener('click', function () {
      clearTimeout(timer);
      mega.classList.remove('is-open');
      mega.hidden = true;
      trigger.setAttribute('aria-expanded', 'false');
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !mega.hidden) close(); });
    // уводим фокус за пределы меню — закрываем
    root.addEventListener('focusout', function (e) { if (!root.contains(e.relatedTarget)) close(); });
  })();

  /* ---------- Направление из меню подставляется в фильтр расписания ---------- */
  (function () {
    var sel = $('[data-filter-direction]');
    if (!sel) return;
    var want;
    try { want = new URLSearchParams(window.location.search).get('napravlenie'); } catch (e) { return; }
    if (!want) return;
    for (var i = 0; i < sel.options.length; i++) {
      if (sel.options[i].value === want) { sel.selectedIndex = i; return; }
    }
  })();

  /* ---------- Обратный отсчёт до конца акции ---------- */
  (function () {
    var nodes = $$('[data-countdown]');
    if (!nodes.length) return;
    // 1 день / 2 дня / 5 дней
    function plural(n, one, few, many) {
      var d = n % 10, h = n % 100;
      if (d === 1 && h !== 11) return one;
      if (d >= 2 && d <= 4 && (h < 10 || h >= 20)) return few;
      return many;
    }
    function render(el) {
      var end = new Date(el.getAttribute('data-countdown')).getTime();
      if (isNaN(end)) return;
      var left = end - Date.now();
      var card = el.closest ? el.closest('.promo-card') : null;
      if (left <= 0) {
        el.textContent = 'Акция завершена';
        if (card) card.classList.add('is-over');
        return;
      }
      // Трёхзначный отсчёт ничего не сообщает и только давит на вёрстку —
      // дальше 99 дней показываем, что срок не поджимает.
      if (left > 99 * 86400000) { el.textContent = 'Бессрочно'; return; }
      var m = Math.floor(left / 60000), h = Math.floor(m / 60), d = Math.floor(h / 24);
      m %= 60; h %= 24;
      var parts = [];
      if (d) parts.push(d + ' ' + plural(d, 'день', 'дня', 'дней'));
      if (d || h) parts.push(h + ' ' + plural(h, 'час', 'часа', 'часов'));
      parts.push(m + ' ' + plural(m, 'минута', 'минуты', 'минут'));
      el.textContent = parts.join(' ');
    }
    nodes.forEach(render);
    // секунды не показываем, поэтому пересчёт раз в полминуты
    setInterval(function () { nodes.forEach(render); }, 30000);
  })();

  /* ---------- Текущий год в подвале ---------- */
  $$('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
