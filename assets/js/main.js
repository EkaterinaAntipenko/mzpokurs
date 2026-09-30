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
  function targetY(el) {
    var top = topHeight();
    var r = el.getBoundingClientRect();
    var free = window.innerHeight - top;
    // data-scroll-bias — доля свободной высоты, на которую цель поднимается выше центра.
    // Нужна длинным блокам (карточки курсов): по центру у них видна середина, а не начало.
    var bias = parseFloat(el.getAttribute('data-scroll-bias')) || 0;
    var y = window.scrollY + r.top - top - Math.max(16, (free - r.height) / 2 - free * bias);
    var max = document.documentElement.scrollHeight - window.innerHeight;
    return Math.max(0, Math.min(y, max));
  }
  // Своя плавная прокрутка вместо behavior: 'smooth' (заказчик, 29.09: «К тарифам» слишком резко).
  // Браузерная на длинном пути (до тарифов ~7000 px) разгоняется до ~22 000 px/с и резко встаёт.
  // Здесь длительность растёт с расстоянием (0,5–1,8 с), кривая smootherstep: мягкий разгон
  // и мягкая остановка, пик скорости втрое ниже. Колесо, касание, клавиши — прокрутка отдаётся посетителю.
  var scrollStop = null;
  function scrollToTarget(el) {
    if (scrollStop) scrollStop();
    var html = document.documentElement;
    // пока идёт своя прокрутка, CSS scroll-behavior: smooth выключен — иначе браузер сглаживает каждый шаг
    html.style.scrollBehavior = 'auto';
    var start = window.scrollY, dist = Math.abs(targetY(el) - start);
    if (reduceMotion || dist < 2) { window.scrollTo(0, targetY(el)); html.style.scrollBehavior = ''; return; }
    var dur = Math.min(1800, Math.max(500, 350 + dist * 0.2));
    var t0 = null, frame = 0;
    var stops = ['wheel', 'touchstart', 'keydown', 'mousedown'];
    var stop = function () {
      window.cancelAnimationFrame(frame);
      stops.forEach(function (ev) { window.removeEventListener(ev, stop); });
      html.style.scrollBehavior = '';
      scrollStop = null;
    };
    var step = function (now) {
      if (t0 === null) t0 = now;
      var p = Math.min(1, (now - t0) / dur);
      var k = p * p * p * (p * (p * 6 - 15) + 10);
      window.scrollTo(0, start + (targetY(el) - start) * k);   // цель пересчитывается: на пути могут догрузиться картинки
      if (p < 1) frame = window.requestAnimationFrame(step);
      else stop();
    };
    stops.forEach(function (ev) { window.addEventListener(ev, stop, { passive: true }); });
    scrollStop = stop;
    frame = window.requestAnimationFrame(step);
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
  // слои с затемнением: меню, окна, фильтры каталога и расписания (на телефоне — окна)
  var LAYERS = '.drawer, .modal, .catalog__filters, .sched-filters__layer';
  var OPEN_LAYERS = LAYERS.split(', ').map(function (s) { return s + '.is-open'; }).join(', ');
  var TOUCH = window.matchMedia('(hover: none)');
  // Под открытым окном страница не прокручивается (overflow: hidden). На компьютере при этом
  // пропадает полоса прокрутки, страница становится шире на её ширину, и вся вёрстка
  // перестраивается — фон дёргается. Пока окно открыто, возвращаем эту ширину отступом справа.
  function lockScroll() {
    if (document.body.classList.contains('is-locked')) return;
    var bar = window.innerWidth - document.documentElement.clientWidth;
    if (bar > 0) document.body.style.paddingRight = bar + 'px';
    document.body.classList.add('is-locked');
  }
  function unlockScroll() {
    document.body.classList.remove('is-locked');
    document.body.style.paddingRight = '';
  }
  function openLayer(el) {
    if (!el) return;
    lastFocus = document.activeElement;
    el.classList.add('is-open');
    el.removeAttribute('aria-hidden');
    lockScroll();
    // Фокус на «Закрыть», а не в поле: у окон фильтров всегда, у остальных окон — на телефоне.
    // Иначе сразу выскакивает клавиатура, и окно со страницей под ним прыгают.
    // Поиск (data-autofocus) — исключение: там сразу печатают.
    var noField = el.hasAttribute('data-no-autofocus') || (TOUCH.matches && !el.hasAttribute('data-autofocus'));
    var focusable = (noField && $('button[data-close]', el))
      || $('input:not([type=checkbox])', el) || $('button, a, input, select', el);
    if (focusable) setTimeout(function () { focusable.focus({ preventScroll: true }); }, 50);
  }
  function closeLayer(el) {
    if (!el) return;
    el.classList.remove('is-open');
    // прячем от скринридеров только окна; фильтры, которые на этой ширине стоят на странице
    // (колонка каталога на компьютере, полоса расписания), остаются доступными
    if (getComputedStyle(el).position === 'fixed') el.setAttribute('aria-hidden', 'true');
    if (!$(OPEN_LAYERS)) unlockScroll();
    if (lastFocus) lastFocus.focus({ preventScroll: true });
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
      // «Показать курсы/группы» на компьютере — не окно: закрывать нечего, фокус не трогаем
      var layer = btn.closest(LAYERS);
      if (layer && layer.classList.contains('is-open')) closeLayer(layer);
      $$('[data-open][aria-expanded="true"]').forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });
    });
  });
  function closeOpenLayers() { $$(OPEN_LAYERS).forEach(closeLayer); }

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
        // «Подробнее» — на страницу курса (h из индекса); страницы нет — кнопка неактивна
        (c.h ? '<a class="btn btn--primary btn--m search-card__btn" href="' + esc(c.h) + '">Подробнее</a>'
             : '<span class="btn btn--primary btn--m search-card__btn is-disabled" aria-disabled="true">Подробнее</span>') +
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
        // Число внутри фразы (.count-inline, «350 000+ специалистов уже…»): пока оно растёт, его
        // ширина меняется и текст рядом дёргается. Держим место под итоговое число — в разметке
        // уже оно; цифры одной ширины и число прижато вправо (CSS). Досчитало — ширину отпускаем.
        var inline = el.classList.contains('count-inline');
        if (inline) el.style.width = el.getBoundingClientRect().width + 'px';
        var tick = function (t) {
          if (!start) start = t;
          var p = Math.min(1, (t - start) / 1400), eased = 1 - Math.pow(1 - p, 3);
          el.textContent = pre + formatNum(target * eased) + suf;
          if (p < 1) window.requestAnimationFrame(tick);
          else if (inline) el.style.width = '';
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
    // form.elements — вместе с кнопками вне формы (атрибут form, нижняя панель оформления на телефоне)
    var submits = [].filter.call(form.elements, function (el) { return el.type === 'submit'; });
    var inputs = [].filter.call(form.elements, function (el) { return el.tagName === 'INPUT'; });
    // Кнопка отправки активна, только когда во всех полях что-то написано и стоит галочка согласия
    // (заказчик, 29.09). «+7 (» маска подставляет сама — это ещё не ввод.
    var filled = function (input) {
      if (input.type === 'checkbox') return input.checked;
      if (input.type === 'tel') return input.value.replace(/\D/g, '').length > 1;
      return input.value.trim().length > 0;
    };
    var sync = function () {
      var ready = inputs.every(filled);
      submits.forEach(function (btn) {
        btn.classList.toggle('is-disabled', !ready);
        btn.setAttribute('aria-disabled', ready ? 'false' : 'true');
      });
    };
    form.addEventListener('input', sync);
    form.addEventListener('change', sync);
    sync();

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = true;
      $$('[required]', form).forEach(function (input) {
        var field = input.closest('.field');
        var valid = input.type === 'tel' ? input.value.replace(/\D/g, '').length === 11 : input.value.trim().length > 1;
        if (input.type === 'email') valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value.trim());
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

  /* ---------- «Как МЦПО помогает…» на телефоне: карточка в фокусе крупнее ---------- */
  // Карточка у середины экрана в полный размер, остальные уменьшены и приглушены;
  // при прокрутке фокус плавно переходит на следующую. Прокрутка обычная, без прилипания.
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
  // Удаление из корзины в два шага: курс уезжает вправо и гаснет (.is-removing, 0,35 с), затем его место плавно
  // схлопывается — высота, поля и отступ до соседа уходят в ноль, и курсы ниже, и подвал поднимаются плавно.
  // Раньше карточка пропадала разом, и подвал прыгал вверх на всю её высоту (заказчик, 30.09).
  // Последний курс: «Корзина пуста» (она внутри того же списка) растёт на его месте в то же время — карточка
  // сменяется строкой одним движением. Раньше строка выскакивала после схлопывания, и подвал дёргался обратно вниз.
  var COLLAPSE = { duration: 500, easing: 'cubic-bezier(0.4, 0, 0.2, 1)' };
  function shown(el) { return el && !el.hidden && !el.classList.contains('is-removing'); }
  $$('[data-cart-remove]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var item = btn.closest('[data-cart-item]');
      if (item.classList.contains('is-removing')) return;
      item.classList.add('is-removing');
      if (reduceMotion || !item.animate) { item.remove(); recalcCart(); return; }
      setTimeout(function () {
        var list = item.parentElement, empty = $('[data-cart-empty]', list);
        var last = $$('[data-cart-item]', list).every(function (el) { return el === item || el.classList.contains('is-removing'); });
        if (last && empty) {
          empty.hidden = false;
          var eh = empty.offsetHeight;
          empty.style.overflow = 'hidden';
          empty.animate([{ height: '0px', opacity: 0, transform: 'translateY(6px)' }, { opacity: 0, offset: 0.3 },
            { height: eh + 'px', opacity: 1, transform: 'none' }], COLLAPSE).onfinish = function () { empty.style.overflow = ''; };
        }
        var cs = getComputedStyle(item);
        var next = item.nextElementSibling, prev = item.previousElementSibling;
        while (next && !shown(next)) next = next.nextElementSibling;
        while (prev && !shown(prev)) prev = prev.previousElementSibling;
        var gap = (next || prev) ? (parseFloat(getComputedStyle(list).rowGap) || 0) : 0;
        var side = next ? 'marginBottom' : 'marginTop';   // отступ до соседа уходит вместе с курсом
        var from = { height: item.offsetHeight + 'px', paddingTop: cs.paddingTop, paddingBottom: cs.paddingBottom };
        var to = { height: '0px', paddingTop: '0px', paddingBottom: '0px' };
        // отступ до «Корзина пуста» появился только что — гасим его сразу, иначе страница подскочит в первом кадре
        from[side] = (last && next === empty ? -gap : 0) + 'px'; to[side] = -gap + 'px';
        item.style.overflow = 'hidden';
        item.animate([from, to], Object.assign({ fill: 'forwards' }, COLLAPSE))
          .onfinish = function () { item.remove(); recalcCart(); };
      }, 340);
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

  /* ---------- «В корзину» на карточке курса (демо — по-настоящему добавит бэкенд) ----------
     Нажатие добавляет курс: счётчик корзины в шапке +1, открывается окно «Курс добавлен в корзину», на кнопке вместо
     корзины крестик (aria-pressed, заказчик 30.09). Нажатие на крестик убирает курс — без окна. Для бэкенда — события
     cart:add / cart:remove с названием курса. */
  var cartModal = document.getElementById('modal-cart'), cartModalCourse = cartModal && $('[data-cart-modal-course]', cartModal);
  var cartBtns = $$('[data-add-to-cart]');
  cartBtns.forEach(function (btn) {
    var card = btn.closest('.course-card'), titleEl = card && $('.course-card__title', card);
    btn.cartTitle = titleEl ? titleEl.textContent.trim() : '';
  });
  cartBtns.forEach(function (btn) {
    var title = btn.cartTitle;
    btn.addEventListener('click', function () {
      var added = btn.getAttribute('aria-pressed') !== 'true';
      // у курса может быть несколько карточек (копии в бесконечной карусели «Популярных курсов») — меняем все сразу
      cartBtns.forEach(function (b) {
        if (b.cartTitle !== title) return;
        b.setAttribute('aria-pressed', added ? 'true' : 'false');
        b.setAttribute('aria-label', (added ? 'Убрать из корзины: ' : 'Добавить в корзину: ') + title);
      });
      $$('[data-cart-count]').forEach(function (el) { el.textContent = Math.max(0, (parseInt(el.textContent, 10) || 0) + (added ? 1 : -1)); });
      btn.dispatchEvent(new CustomEvent(added ? 'cart:add' : 'cart:remove', { bubbles: true, detail: { title: title } }));
      if (added && cartModal) {
        if (cartModalCourse) cartModalCourse.textContent = '«' + title + '» — оформите заказ сейчас или выберите ещё курсы.';
        openLayer(cartModal);
      }
    });
  });

  /* ---------- Фильтры каталога применяются сразу, без кнопки (заказчик, 30.09) ----------
     Отбор демо-карточек: цена — data-price, галочки группы data-filter="ключ" — по data-f-ключ у карточки
     (build.py, COURSE_TAGS). Внутри группы — любое из отмеченного, между группами — всё сразу.
     На бэкенде здесь запрос к серверу: событие catalog:filter уходит с выбранными значениями.
     Уходящие карточки гаснут, оставшиеся съезжают на новые места (FLIP), новые проявляются. */
  var FLIP_EASE = 'cubic-bezier(0.22, 1, 0.36, 1)';
  $$('.catalog').forEach(function (catalog) {
    var aside = $('.catalog__filters', catalog), grid = $('.catalog__grid', catalog);
    if (!aside || !grid) return;
    var cards = $$('.course-card', grid);
    var empty = $('[data-catalog-empty]', catalog);
    var found = $('.catalog__bar .t-muted', catalog), foundText = found ? found.textContent : '';
    var showBtn = $('.filters-foot .btn', aside), showText = showBtn ? showBtn.textContent : '';
    var forms = /программ/.test(foundText) ? ['программа', 'программы', 'программ'] : ['курс', 'курса', 'курсов'];
    function plural(n) {
      var a = n % 10, b = n % 100;
      return forms[a === 1 && b !== 11 ? 0 : a >= 2 && a <= 4 && (b < 12 || b > 14) ? 1 : 2];
    }
    function read() {
      var st = { groups: [], min: null, max: null };
      $$('[data-filter]', aside).forEach(function (fs) {
        var vals = $$('input:checked', fs).map(function (i) { return i.value; });
        if (vals.length) st.groups.push({ key: fs.getAttribute('data-filter'), values: vals });
      });
      var mn = $('[data-price="min"]', aside), mx = $('[data-price="max"]', aside);
      if (mn && mn.value !== '') st.min = +mn.value;
      if (mx && mx.value !== '') st.max = +mx.value;
      return st;
    }
    function fits(card, st) {
      var price = +card.getAttribute('data-price');
      if (st.min !== null && price < st.min) return false;
      if (st.max !== null && price > st.max) return false;
      return st.groups.every(function (g) {
        var tags = (card.getAttribute('data-f-' + g.key) || '').split(' ');
        return g.values.some(function (v) { return tags.indexOf(v) !== -1; });
      });
    }
    // уходящая карточка догасла (или её прервал новый отбор): прячем и возвращаем в поток
    var fading = [];
    function gone(c) {
      c.getAnimations().forEach(function (a) { a.cancel(); });
      c.hidden = true;
      ['position', 'margin', 'pointer-events', 'left', 'top', 'width', 'height'].forEach(function (p) { c.style.removeProperty(p); });
      fading = fading.filter(function (x) { return x !== c; });
    }
    // FLIP: замерили места до, поменяли состав, замерили после — и сдвигаем карточки из старых мест в новые
    function relayout(show) {
      fading.slice().forEach(gone);                                                              // прошлый отбор — сразу к концу
      cards.forEach(function (c) { c.getAnimations().forEach(function (a) { a.finish(); }); });
      var before = cards.filter(function (c) { return !c.hidden; });
      var leaving = before.filter(function (c) { return show.indexOf(c) === -1; });
      var entering = show.filter(function (c) { return c.hidden; });
      if (reduceMotion || !grid.animate) { cards.forEach(function (c) { c.hidden = show.indexOf(c) === -1; }); return; }
      var first = before.map(function (c) { return c.getBoundingClientRect(); });
      var box = grid.getBoundingClientRect();
      // уходящие — из потока, но на прежнем месте, пока гаснут; остальные уже встают на новые места
      leaving.forEach(function (c) {
        var r = first[before.indexOf(c)];
        c.style.cssText += ';position:absolute;margin:0;pointer-events:none;left:' + (r.left - box.left) + 'px;top:' + (r.top - box.top) + 'px;width:' + r.width + 'px;height:' + r.height + 'px';
      });
      entering.forEach(function (c) { c.hidden = false; });
      before.forEach(function (c, i) {
        if (leaving.indexOf(c) !== -1) return;
        var r = c.getBoundingClientRect(), dx = first[i].left - r.left, dy = first[i].top - r.top;
        if (Math.abs(dx) > 0.5 || Math.abs(dy) > 0.5) {
          c.animate([{ transform: 'translate(' + dx + 'px, ' + dy + 'px)' }, { transform: 'none' }], { duration: 420, easing: FLIP_EASE });
        }
      });
      entering.forEach(function (c) {
        c.animate([{ opacity: 0, transform: 'scale(0.96)' }, { opacity: 1, transform: 'none' }], { duration: 360, delay: 120, easing: FLIP_EASE, fill: 'backwards' });
      });
      leaving.forEach(function (c) {
        fading.push(c);
        var a = c.animate([{ opacity: 1, transform: 'none' }, { opacity: 0, transform: 'scale(0.96)' }], { duration: 200, easing: 'ease-in', fill: 'forwards' });
        a.onfinish = function () { if (fading.indexOf(c) !== -1) gone(c); };
      });
    }
    var revealed = false;
    function apply() {
      // после первого отбора карточки больше не «проявляются при прокрутке»: их прозрачностью ведает FLIP
      if (!revealed) { revealed = true; cards.forEach(function (c) { c.classList.remove('reveal'); }); }
      var st = read(), active = st.groups.length > 0 || st.min !== null || st.max !== null;
      var show = cards.filter(function (c) { return fits(c, st); }), n = show.length;
      relayout(show);
      if (found) found.textContent = active ? 'Найдено ' + n + ' ' + plural(n) : foundText;
      if (empty) empty.hidden = n > 0;
      // на планшете и телефоне фильтры — окно, кнопка внизу его закрывает и показывает, сколько нашлось
      if (showBtn) showBtn.textContent = !active ? showText : n ? 'Показать ' + n + ' ' + plural(n) : 'Нет подходящих ' + forms[2];
      catalog.dispatchEvent(new CustomEvent('catalog:filter', { bubbles: true, detail: st }));
    }
    var typing = null;
    aside.addEventListener('input', function (e) {
      if (!e.target.matches('[data-price]')) return;
      clearTimeout(typing); typing = setTimeout(apply, 400);   // цену применяем, когда перестали печатать
    });
    aside.addEventListener('change', function (e) {
      if (e.target.matches('[data-price]')) clearTimeout(typing);
      apply();
    });
    $$('[data-filters-reset]', catalog).forEach(function (b) {
      b.addEventListener('click', function () {
        $$('input[type=checkbox]', aside).forEach(function (i) { i.checked = false; });
        $$('[data-price]', aside).forEach(function (i) { i.value = ''; });
        aside.dispatchEvent(new Event('change'));   // и счётчик у кнопки «Фильтры», и отбор
      });
    });
  });

  /* ---------- Расписание и страница преподавателя: список курсов слева ----------
     Каждый пункт прокручивает к графику своего курса (#c0…, общий обработчик якорей выше);
     выделен курс, чей график сейчас посередине экрана. */
  $$('.course-list').forEach(function (list) {
    var links = $$('a[href^="#"]', list);
    var targets = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
    function mark(k) { links.forEach(function (a, i) { if (i === k) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current'); }); }
    links.forEach(function (a, i) { a.addEventListener('click', function () { mark(i); }); });
    if (!('IntersectionObserver' in window)) return;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) mark(targets.indexOf(e.target)); });
    }, { rootMargin: '-45% 0px -50% 0px' });
    targets.forEach(function (t) { if (t) io.observe(t); });
  });

  /* ---------- График курса: «Показать ещё даты» раскрывает ещё 3 даты, «Свернуть» — прячет ---------- */
  $$('[data-more-dates]').forEach(function (btn) {
    var card = btn.closest('.sched-course');
    var extra = card ? $$('tr[data-extra]', card) : [];
    if (!extra.length) { btn.hidden = true; return; }
    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') !== 'true';
      extra.forEach(function (tr, i) { tr.style.setProperty('--i', i); tr.hidden = !open; });
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.textContent = open ? 'Свернуть' : 'Показать ещё даты';
    });
  });

  /* ---------- «Есть промокод?»: по нажатию — поле ввода с кнопкой-стрелкой ----------
     Ссылка уступает место полю (анимация в pages.css), курсор сразу в поле. Проверку промокода
     сделает бэкенд — пока стрелка только возвращает в пустое поле. */
  $$('[data-promo-toggle]').forEach(function (link) {
    var form = document.getElementById(link.getAttribute('aria-controls'));
    if (!form) return;
    var input = $('input', form);
    link.addEventListener('click', function () {
      link.setAttribute('aria-expanded', 'true');
      link.hidden = true;
      form.hidden = false;
      if (input) input.focus({ preventScroll: true });
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (input && !input.value.trim()) input.focus();
    });
  });

  /* ---------- Оформление, шаг 1: календарь старта очной группы ----------
     Выбрали «Очно в Москве» — вместо текста под формами обучения появляется календарь
     (месяц → дата → время). Формат, старт и цена сразу видны в заказе справа, в строке над
     шагом (телефон) и в нижней панели. */
  $$('[data-start-picker]').forEach(function (picker) {
    var step = picker.closest('.checkout__step') || document;
    var note = $('[data-format-note]', step);
    var formats = $$('input[name="format"]', step);
    var months = $$('[data-month]', picker), groups = $$('[data-month-days]', picker);
    var arrows = $$('[data-month-step]', picker);
    var cur = 0;
    function setText(sel, text) { $$(sel).forEach(function (el) { el.textContent = text; }); }
    function value(name) { var r = $('input[name="' + name + '"]:checked', picker); return r ? r.value : ''; }
    function update() {
      var f = formats.filter(function (r) { return r.checked; })[0];
      if (!f) return;
      var offline = f.value === 'offline';
      picker.hidden = !offline;
      if (note) note.hidden = offline;
      var name = $('.format-option__name', f.closest('label')).textContent;
      var price = f.getAttribute('data-price');
      var start = offline ? value('start-date') + ', ' + value('start-time') : f.getAttribute('data-start');
      setText('[data-order-format]', name);
      setText('[data-order-start]', start);
      setText('[data-order-total]', price);
      setText('[data-order-pay]', 'Оплатить ' + price);
      setText('[data-order-line]', name + ' · старт ' + start + ' · ' + price);
    }
    function showMonth(i) {
      cur = Math.max(0, Math.min(months.length - 1, i));
      months.forEach(function (b, k) { b.classList.toggle('is-active', k === cur); b.setAttribute('aria-pressed', k === cur ? 'true' : 'false'); });
      groups.forEach(function (g, k) { g.hidden = k !== cur; });
      // у дат общее имя: в другом месяце выбираем его первую дату, иначе в заказе осталась бы скрытая
      var shown = groups[cur];
      if (shown && !$('input:checked', shown)) { var first = $('input', shown); if (first) first.checked = true; }
      arrows.forEach(function (b) { var s = +b.getAttribute('data-month-step'); b.disabled = s < 0 ? cur === 0 : cur === months.length - 1; });
      update();
    }
    months.forEach(function (b, k) { b.addEventListener('click', function () { showMonth(k); }); });
    arrows.forEach(function (b) { b.addEventListener('click', function () { showMonth(cur + (+b.getAttribute('data-month-step'))); }); });
    formats.forEach(function (r) { r.addEventListener('change', update); });
    picker.addEventListener('change', update);
    showMonth(0);
  });

  /* ---------- Фильтры каталога на компьютере: колонка слева, по умолчанию скрыта ----------
     Кнопка «Фильтры» над курсами показывает и прячет её; на планшете и телефоне вместо этой
     кнопки видна другая, с data-open, — она открывает окно фильтров */
  $$('[data-filters-toggle]').forEach(function (btn) {
    var catalog = btn.closest('.catalog');
    function apply(open) {
      catalog.classList.toggle('is-filters-open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
    btn.addEventListener('click', function () {
      var open = !catalog.classList.contains('is-filters-open');
      // Колонка выезжает слева, а каждая карточка переезжает на своё новое место — 4 в ряд → 3 и обратно
      // (заказчик, 30.09). Это View Transitions: у карточек, полосы над ними и шапки на время перехода
      // свои имена, стили — в pages.css. Без API и при prefers-reduced-motion — сразу, как раньше.
      if (!document.startViewTransition || reduceMotion) { apply(open); return; }
      $$('.course-card', catalog).forEach(function (c) { c.getAnimations().forEach(function (a) { a.finish(); }); });
      var named = [];
      var vtName = function (el, name) { el.style.viewTransitionName = name; named.push(el); };
      $$('.catalog__grid > .course-card:not([hidden])', catalog).forEach(function (el, i) { vtName(el, 'catalog-' + i); });
      // Полоса над курсами и «ничего не нашли» меняют ширину. Одним снимком их растягивало вместе с текстом:
      // название направления на миг увеличивалось и прыгало вниз-вверх (заказчик, 30.09). Поэтому фон —
      // своим снимком, а надписи и кнопки — своими, в натуральную величину: только едут (pages.css)
      [['.catalog__bar', 'catalog-bar'], ['.catalog__bar > h2', 'catalog-bar-title'],
       ['.catalog__filter-toggle', 'catalog-bar-toggle'], ['.catalog__bar > .t-muted', 'catalog-bar-found']]
        .forEach(function (p) { var el = $(p[0], catalog); if (el) vtName(el, p[1]); });
      var empty = $('[data-catalog-empty]:not([hidden])', catalog);
      if (empty) {
        vtName(empty, 'catalog-empty');
        $$(':scope > *', empty).forEach(function (el, i) { vtName(el, 'catalog-empty-' + i); });
      }
      catalog.classList.add('is-filters-anim'); doc.classList.add('vt-catalog');
      var done = function () {
        catalog.classList.remove('is-filters-anim'); doc.classList.remove('vt-catalog');
        named.forEach(function (el) { el.style.removeProperty('view-transition-name'); });
      };
      document.startViewTransition(function () { apply(open); }).finished.then(done, done);
    });
  });

  /* ---------- Направления каталога: теги над курсами, на телефоне — список ----------
     По умолчанию не выбрано ни одно — показаны все курсы раздела (заказчик, 30.09). Тег выбирает
     направление, повторное нажатие снимает выбор; название в полосе над курсами и список на телефоне
     (первый пункт — «все») следуют за ним */
  $$('.catalog__tabs').forEach(function (list) {
    var tags = $$('.tab', list), scope = list.parentNode;
    var sel = $('[data-dir-select]', scope), value = sel && $('[data-dir-value]', sel.parentNode);
    var title = $('.catalog__bar h2', scope), allTitle = title ? title.textContent : '';
    function choose(i) { // -1 — все направления
      tags.forEach(function (t, j) { t.classList.toggle('is-active', j === i); t.setAttribute('aria-pressed', j === i ? 'true' : 'false'); });
      if (title) title.textContent = i < 0 ? allTitle : tags[i].textContent;
      if (sel) { sel.selectedIndex = i + 1; if (value) value.textContent = sel.options[i + 1].text; }
      // TODO backend: отбор курсов по направлению (direction: null — все)
      list.dispatchEvent(new CustomEvent('catalog:direction', { bubbles: true, detail: { direction: i < 0 ? null : tags[i].textContent } }));
    }
    tags.forEach(function (t, i) {
      t.addEventListener('click', function () { choose(t.getAttribute('aria-pressed') === 'true' ? -1 : i); });
    });
    if (sel) sel.addEventListener('change', function () { choose(sel.selectedIndex - 1); });
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
    var slides = $$('.hero-slider__slide', slider), imgs = $$('.hero-slider__img', slider);
    var texts = $$('.hero-slider__text', slider), segs = $$('.hero-progress__seg', slider);
    var n = texts.length; if (n < 2) return;
    var interval = parseInt(slider.getAttribute('data-interval'), 10) || 4000;
    slider.style.setProperty('--hero-interval', interval + 'ms');
    var i = 0, timer = null, started = 0, left = interval;
    // все картинки грузим и декодируем заранее — иначе на первой смене слайда заминка на декодирование
    imgs.forEach(function (im) { im.loading = 'eager'; if (im.decode) im.decode().catch(function () {}); });
    // Пассивное приближение (см. .hero-slider__slide в components.css): картинка растёт CSS-анимацией
    // hero-zoom (28 с, linear infinite), пока у слайда класс is-zooming. Ставим его при показе — рост идёт
    // со 100 %; снимаем, когда слайд погас: уходящий растёт, пока гаснет, и в 100 % возвращается невидимым.
    var FADE = 900, unzooms = [];
    function zoom(k) {
      var s = slides[k];
      if (!s || reduceMotion) return;
      clearTimeout(unzooms[k]);
      if (s.classList.contains('is-zooming')) { s.classList.remove('is-zooming'); void s.offsetWidth; } // перезапуск
      s.classList.add('is-zooming');
    }
    function unzoom(k) {
      clearTimeout(unzooms[k]);
      unzooms[k] = setTimeout(function () { slides[k].classList.remove('is-zooming'); }, FADE + 100);
    }
    function show(k) {
      slides.forEach(function (s, j) { if (j !== k && s.classList.contains('is-active')) unzoom(j); });
      zoom(k);
      [slides, texts, segs].forEach(function (list) { list.forEach(function (el, j) { el.classList.toggle('is-active', j === k); }); });
      texts.forEach(function (t, j) { if (j === k) t.removeAttribute('aria-hidden'); else t.setAttribute('aria-hidden', 'true'); });
      // перезапуск анимации заполнения
      var bar = segs[k] && segs[k].querySelector('i');
      if (bar) { bar.style.animation = 'none'; void bar.offsetWidth; bar.style.animation = ''; }
    }
    function schedule(ms) { clearTimeout(timer); started = Date.now(); left = ms; timer = setTimeout(next, ms); }
    function next() { i = (i + 1) % n; show(i); schedule(interval); }
    function pause() {
      if (!timer) return; clearTimeout(timer); timer = null; left = Math.max(0, left - (Date.now() - started)); slider.classList.add('is-paused');
    }
    function resume() {
      if (timer) return; slider.classList.remove('is-paused'); schedule(left);
    }
    document.addEventListener('visibilitychange', function () { if (document.hidden) pause(); else resume(); });
    if (isStatic) return;
    zoom(0);
    schedule(interval);
  });

  /* ---------- Цитаты преподавателей (факультет массажа): листаются сами, как слайдер главной ----------
     Раз в интервал — следующая цитата, прогресс на фото заполняется за интервал (.hero-progress).
     Стрелка — сразу к следующей, отсчёт начинается заново. Стоит, только пока блок вне экрана, на скрытой
     вкладке и при фокусе с клавиатуры. При prefers-reduced-motion и ?static сам не листает — только стрелкой. */
  $$('[data-quote-slider]').forEach(function (slider) {
    var pics = $$('.expert__pic', slider), slides = $$('.expert__slide', slider), segs = $$('.hero-progress__seg', slider);
    var next = $('.expert__next', slider);
    var n = slides.length; if (n < 2) return;
    var interval = parseInt(slider.getAttribute('data-interval'), 10) || 8000;
    slider.style.setProperty('--hero-interval', interval + 'ms');
    var auto = !reduceMotion && !isStatic;
    var i = 0, timer = null, started = 0, left = interval, holds = {};
    function show(k) {
      [pics, slides, segs].forEach(function (list) { list.forEach(function (el, j) { el.classList.toggle('is-active', j === k); }); });
      slides.forEach(function (s, j) { if (j === k) s.removeAttribute('aria-hidden'); else s.setAttribute('aria-hidden', 'true'); });
      var bar = segs[k] && segs[k].querySelector('i');
      if (bar) { bar.style.animation = 'none'; void bar.offsetWidth; bar.style.animation = ''; }
    }
    function held() { return Object.keys(holds).length > 0; }
    function schedule(ms) { clearTimeout(timer); timer = null; left = ms; if (!auto || held()) return; started = Date.now(); timer = setTimeout(step, ms); }
    function step() { i = (i + 1) % n; show(i); schedule(interval); }
    function hold(why) {
      if (held()) { holds[why] = true; return; }
      holds[why] = true;
      if (timer) { clearTimeout(timer); timer = null; left = Math.max(0, left - (Date.now() - started)); }
      slider.classList.add('is-paused');
    }
    function release(why) {
      if (!holds[why]) return;
      delete holds[why];
      if (held()) return;
      if (auto) slider.classList.remove('is-paused');
      schedule(left);
    }
    next.addEventListener('click', function () { i = (i + 1) % n; show(i); schedule(interval); });
    // Листается всегда, как слайдер главной (заказчик, 30.09): под курсором больше не стоит — со стороны это
    // выглядело как «не листается». Пауза — только при фокусе с клавиатуры (:focus-visible); после нажатия
    // стрелки мышью кнопка тоже в фокусе, и прежняя пауза на любой фокус останавливала слайдер насовсем.
    slider.addEventListener('focusin', function (e) { if (e.target.matches && e.target.matches(':focus-visible')) hold('focus'); });
    slider.addEventListener('focusout', function (e) { if (!slider.contains(e.relatedTarget)) release('focus'); });
    document.addEventListener('visibilitychange', function () { if (document.hidden) hold('tab'); else release('tab'); });
    // блок внизу страницы: пока его не видно, стоит — посетитель застаёт первую цитату, а не случайную
    if ('IntersectionObserver' in window) {
      hold('offscreen');
      new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { if (en.isIntersecting) release('offscreen'); else hold('offscreen'); });
      }, { threshold: 0.35 }).observe(slider);
    }
    if (!auto) slider.classList.add('is-paused');
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
    function hideNow() {
      clearTimeout(timer);
      mega.classList.remove('is-open');
      mega.hidden = true;
      trigger.setAttribute('aria-expanded', 'false');
    }
    trigger.addEventListener('click', hideNow);
    // по ссылке из панели (раздел, курс) тоже уходим со страницы
    mega.addEventListener('click', function (e) { if (e.target.closest('a.mega__item[href]')) hideNow(); });
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

  /* ---------- Расписание на телефоне: направление в строке, остальные фильтры в окне ---------- */
  // Список направлений в строке — копия поля из полосы фильтров (оно на телефоне в окне скрыто),
  // значения синхронизированы. На значке — сколько фильтров в окне изменено, при нуле кружка нет.
  $$('[data-sched-filters]').forEach(function (form) {
    var dir = $('[data-filter-direction]', form), mirror = $('[data-dir-mirror]', form);
    var value = $('[data-dir-value]', form), badge = $('[data-sched-count]', form), btn = $('.filter-btn', form);
    var layer = $('.sched-filters__layer', form);
    function sync() {
      if (dir && mirror) mirror.value = dir.value;
      if (dir && value) value.textContent = dir.options[dir.selectedIndex].text;
      var k = 0;
      $$('select', layer).forEach(function (s) { if (s !== dir && s.selectedIndex > 0) k++; });
      $$('input', layer).forEach(function (i) { if (i.value !== '') k++; });
      if (badge) { badge.textContent = k; badge.hidden = k === 0; }
      if (btn) btn.setAttribute('aria-label', k ? 'Фильтры, изменено ' + k : 'Фильтры');
    }
    if (dir && mirror) mirror.addEventListener('change', function () { dir.value = mirror.value; });
    form.addEventListener('change', sync);
    form.addEventListener('input', sync);
    form.addEventListener('reset', function () { setTimeout(sync, 0); });
    sync();
  });

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
