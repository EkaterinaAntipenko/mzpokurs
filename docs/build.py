# -*- coding: utf-8 -*-
"""Генератор статичных HTML-страниц МЦПО из общих частей.
Результат — обычные .html без зависимостей."""
import json, os, re

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # папка проекта
PHONE = "+7 (495) 320-44-09"
PHONE_HREF = "tel:+74953204409"
PHONE_TEL = "+74953204409"
EMAIL = "info@mzpokurs.com"
ADDR = "Москва, ул. Кузнецкий Мост, 21/5, подъезд 1, этаж 4, офис 4002"
LICENSE = "№ 041596"
LICENSE_FULL = "№ 041596, выдана Департаментом образования города Москвы"
ORG_BRAND = "Международный центр профессионального образования"
ORG_LEGAL = "ООО «МЦПО»"
INN = "9702027419"
OGRN = "1207700494616"
YEAR_FROM = "2021"
SITE = "https://www.mzpokurs.com"

# Атрибуты со внутренними кавычками вынесены в константы:
# f-строка не может содержать обратный слэш в выражении на Python < 3.12.
A_CUR_PAGE = ' aria-current="page"'
A_CUR_TRUE = ' aria-current="true"'
A_CUR_STEP = ' aria-current="step"'
CLS_SOON = ' class="is-soon"'
CLS_DONE = ' class="is-done"'


ICON_PATHS = {
 "phone": "<path d='M22 16.92v3a2 2 0 0 1-2.18 2 19.8 19.8 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z'/>",
 "mail": "<rect x='2' y='4' width='20' height='16' rx='2'/><path d='m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7'/>",
 "map-pin": "<path d='M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z'/><circle cx='12' cy='10' r='3'/>",
 "cart": "<circle cx='8' cy='21' r='1'/><circle cx='19' cy='21' r='1'/><path d='M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12'/>",
 "menu": "<path d='M4 6h16M4 12h16M4 18h16'/>",
 "chevron-down": "<path d='m6 9 6 6 6-6'/>",
 "chevron-right": "<path d='m9 18 6-6-6-6'/>",
 "chevron-left": "<path d='m15 18-6-6 6-6'/>",
 "arrow-up-right": "<path d='M7 17 17 7M7 7h10v10'/>",
 "arrow-right": "<path d='M5 12h14M13 6l6 6-6 6'/>",
 "close": "<path d='M18 6 6 18M6 6l12 12'/>",
 "check": "<path d='M20 6 9 17l-5-5'/>",
 "calendar": "<rect x='3' y='4' width='18' height='18' rx='2'/><path d='M16 2v4M8 2v4M3 10h18'/>",
 "send": "<path d='m22 2-7 20-4-9-9-4Z'/><path d='M22 2 11 13'/>",
 "filter": "<path d='M3 6h18M7 12h10M10 18h4'/>",
 "star": "<path d='M12 3.2 14.72 8.71 20.8 9.6 16.4 13.89 17.44 19.95 12 17.09 6.56 19.95 7.6 13.89 3.2 9.6 9.28 8.71Z'/>",
 "search": "<circle cx='11' cy='11' r='7'/><path d='m20 20-3.5-3.5'/>",
}

def icon(name, cls="icon"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICON_PATHS[name]}</svg>'

QUOTE = '<svg class="review__quote" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h7v7H7l-1.5 5H3.5L5 13H3z M14 6h7v7h-3l-1.5 5h-2L16 13h-2z"/></svg>'
PLAY = '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M7 4.5v15l12-7.5z" fill="#1C263B"/></svg>'

LOGO_SVG = open(os.path.join(OUT, "assets", "icons", "logo.svg"), encoding="utf-8").read().replace('<svg ', '<svg class="logo__mark" ', 1).replace(' role="img" aria-label="МЦПО"', ' aria-hidden="true"')

def logo(light=False):
    return f'''<a class="logo{' logo--light' if light else ''}" href="index.html" aria-label="МЦПО — Международный центр профессионального образования, на главную">
      {LOGO_SVG}
      <span class="logo__text">Международный центр профессионального образования</span>
    </a>'''

NAV = [("schedule.html","Расписание",True),("accreditation.html","Аккредитация",False),("employment.html","Трудоустройство",False),("events.html","Мероприятия",False),("promotions.html","Акции",False),("about.html","О центре",True),("contacts.html","Контакты",False)]
# Подпункты разделов шапки, у которых есть стрелка вниз.
SUBMENU = {
    "О центре": [("teachers.html", "Преподаватели")],
}
# Под строкой в окне поиска из шапки — направления, как в подвале
SEARCH_DIRECTIONS = ["Медицинская подготовка", "Аккредитация медработников", "Курсы НМО для врачей",
                     "Косметология", "Массаж и реабилитация", "Диетология"]

# Готовые страницы. Ссылки на всё остальное рендерятся как неактивные (без href, без hover).
READY_FACULTY = "Массаж и реабилитация"
READY_COURSE = "course-classic-massage.html"
# Куда ведут направления из меню, подвала и плиток. Остальные — заглушки.
FAC_LINKS = {"Массаж и реабилитация": "faculty-massage.html",
             "Медицинская подготовка": "doctors.html",
             "Курсы НМО для врачей": "doctors.html",
             "Аккредитация медработников": "accreditation.html"}

# ---------- Каталог для выпадающего меню ----------
# (id, факультет, картинка, [(id, направление, картинка, [(курс, картинка)])])
CATALOG = [
 ("massage", "Массаж и реабилитация", "dir-massage", [
   ("med", "Медицинский массаж", "tile-massage", [
     ("Классический массаж с нуля, 72 ак. ч.", "course-1"),
     ("Медицинский массаж: повышение квалификации, 144 ак. ч.", "dir-massage"),
     ("Медицинский массаж: первичная специализация, 288 ак. ч.", "group-practice"),
     ("Антицеллюлитный массаж, 8 ак. ч.", "course-desc"),
     ("Лимфодренажный массаж", "tile-massage"),
     ("Спортивный массаж", "persp-2"),
     ("Массаж при заболеваниях позвоночника", "persp-4"),
   ]),
   ("child", "Детский массаж и развитие ребёнка", "dir-child", [
     ("Детский массаж: повышение квалификации, 144 ак. ч.", "dir-child"),
     ("Массаж и гимнастика для детей до года", "dir-child"),
   ]),
   ("lfk", "ЛФК и спортивная медицина", "persp-4", [
     ("Инструктор по фитнесу, 600 ак. ч.", "persp-2"),
     ("Инструктор-методист по адаптивной физкультуре, 600 ак. ч.", "persp-4"),
     ("Лечебная физкультура", "group-practice"),
   ]),
   ("spa", "SPA-массаж и коррекция фигуры", "persp-3", [
     ("SPA-массаж", "persp-3"),
     ("Коррекция фигуры", "persp-1"),
     ("SPA-эстетист", "dir-cosm"),
   ]),
   ("face", "Массаж лица", "tile-cosm", [
     ("Классический массаж лица", "tile-cosm"),
     ("Буккальный массаж лица", "dir-cosm"),
   ]),
 ]),
 ("cosm", "Косметология", "dir-cosm", [
   ("estet", "Медицинская и эстетическая косметология", "tile-cosm", [
     ("Врач-косметолог, 576 ак. ч.", "dir-cosm"),
     ("Врач-косметолог: повышение квалификации, 144 ак. ч.", "tile-cosm"),
     ("Сестринское дело в косметологии, 144 ак. ч.", "expert"),
   ]),
   ("apparat", "Аппаратная косметология", "quiz-doctor", [
     ("Аппаратная косметология", "quiz-doctor"),
     ("Гальваника и ультразвук", "tile-cosm"),
   ]),
   ("inject", "Инъекционная косметология", "dir-med", [
     ("Инъекционная косметология для врачей", "dir-med"),
     ("Мезотерапия и биоревитализация", "tile-med"),
   ]),
   ("brows", "Архитектура бровей и ресниц", "persp-1", [
     ("Архитектура и окрашивание бровей", "persp-1"),
     ("Наращивание ресниц", "dir-cosm"),
   ]),
 ]),
 ("medp", "Медицинская подготовка", "dir-med", [
   ("doctors", "Курсы для врачей", "tile-med", [
     ("Кардиология, 144 ак. ч.", "dir-med"),
     ("Неврология, 144 ак. ч.", "tile-med"),
     ("Анестезиология-реаниматология, 144 ак. ч.", "group-practice"),
     ("Терапия, 144 ак. ч.", "dir-med"),
     ("Педиатрия, 144 ак. ч.", "dir-child"),
     ("Офтальмология, 144 ак. ч.", "tile-med"),
     ("Урология, 144 ак. ч.", "dir-med"),
     ("Травматология и ортопедия, 144 ак. ч.", "persp-4"),
     ("Психиатрия, 144 ак. ч.", "expert"),
     ("Диетология: переподготовка, 504 ак. ч.", "course-desc"),
     ("Физиотерапия: переподготовка, 504 ак. ч.", "group-practice"),
     ("Авиационная и космическая медицина, 36 ак. ч.", "tile-med"),
   ]),
   ("nurse", "Сестринское дело", "expert", [
     ("Сестринское дело, 144 ак. ч.", "expert"),
     ("Акушерское дело", "dir-child"),
     ("Лечебное дело", "dir-med"),
     ("Лабораторная диагностика", "tile-med"),
     ("Скорая и неотложная помощь", "group-practice"),
     ("Физиотерапия и УВТ", "persp-4"),
     ("Медицинская статистика", "salary"),
   ]),
   ("junior", "Младший медицинский персонал", "group-practice", [
     ("Санитарка / санитар, 244 ак. ч.", "group-practice"),
     ("Младшая медсестра по уходу за больными, 304 ак. ч.", "expert"),
   ]),
 ]),
 ("diet", "Диетология", "course-desc", [
   ("diet-sert", "Диетология с сертификатом", "course-desc", [
     ("Диетология: повышение квалификации, 144 ак. ч.", "course-desc"),
     ("Диетология: переподготовка, 504 ак. ч.", "dir-med"),
   ]),
   ("diet-free", "Диетология без медицинского образования", "persp-1", [
     ("Нутрициология", "persp-1"),
     ("Основы здорового питания", "course-desc"),
   ]),
 ]),
 ("hair", "Парикмахерское и визажное искусство", "persp-3", [
   ("hairdress", "Парикмахерское искусство", "persp-3", [
     ("Парикмахер-универсал", "persp-3"),
     ("Колористика", "persp-1"),
   ]),
   ("makeup", "Школа визажа", "tile-cosm", [
     ("Визажист-стилист", "tile-cosm"),
     ("Свадебный и вечерний макияж", "dir-cosm"),
   ]),
 ]),
 ("safety", "Безопасность и охрана труда", "tile-accred", [
   ("labour", "Охрана труда", "tile-accred", [
     ("Охрана труда для руководителей и специалистов", "tile-accred"),
     ("Пожарная безопасность", "jobs-cap"),
   ]),
   ("firstaid", "Оказание первой помощи", "group-practice", [
     ("Первая доврачебная помощь", "group-practice"),
   ]),
 ]),
 ("buh", "Бухгалтерский учёт и кадры", "salary", [
   ("buh-main", "Бухгалтерский учёт и кадровое дело", "salary", [
     ("Бухгалтерский учёт", "salary"),
     ("Кадровое делопроизводство", "jobs-cap"),
   ]),
 ]),
 ("manager", "Менеджерская подготовка", "jobs-cap", [
   ("manager-main", "Менеджмент и салонный бизнес", "jobs-cap", [
     ("Менеджмент в здравоохранении", "jobs-cap"),
     ("Управление салоном красоты", "persp-3"),
   ]),
 ]),
 ("ped", "Педагогика и психология", "expert", [
   ("ped-main", "Педагогика и психология", "expert", [
     ("Педагог дополнительного образования", "expert"),
     ("Психологическое консультирование", "lead-operator"),
   ]),
 ]),
 ("sport", "Физическая культура и спорт", "persp-2", [
   ("sport-main", "Физическая культура и спорт", "persp-2", [
     ("Инструктор тренажёрного зала", "persp-2"),
     ("Адаптивная физическая культура", "persp-4"),
   ]),
 ]),
]


# «Расписание» раскрывается тем же списком факультетов, что и каталог: выбранный
# пункт приезжает на страницу расписания параметром и подставляется в фильтр.
SUBMENU["Расписание"] = [(f"schedule.html?napravlenie={fid}", fname) for fid, fname, _i, _d in CATALOG]


def mega_menu():
    """Выпадающий каталог: факультеты → направления → курсы, справа — картинка.
    Все списки отрисованы сразу, JS только переключает активный."""
    fac_items, dir_cols, course_cols = [], [], []
    for fi, (fid, fname, fimg, dirs) in enumerate(CATALOG):
        href = FAC_LINKS.get(fname, "#")
        act = " is-active" if fi == 0 else ""
        fac_items.append(
            f'<li><a class="mega__item{act}" href="{href}" data-fac="{fid}" data-img="{fimg}">'
            f'<span>{fname}</span>{icon("chevron-right","icon icon--xs")}</a></li>')

        d_items = []
        for di, (did, dname, dimg, courses) in enumerate(dirs):
            dact = " is-active" if di == 0 else ""
            d_items.append(
                f'<li><a class="mega__item{dact}" href="#" data-dir="{fid}.{did}" data-img="{dimg}">'
                f'<span>{dname}</span>{icon("chevron-right","icon icon--xs")}</a></li>')
            c_items = "".join(
                f'<li><a class="mega__item" href="#" data-img="{cimg}"><span>{cname}</span></a></li>'
                for cname, cimg in courses)
            cshow = " is-shown" if (fi == 0 and di == 0) else ""
            course_cols.append(f'<ul class="mega__list{cshow}" data-courses="{fid}.{did}" role="list">{c_items}</ul>')
        show = " is-shown" if fi == 0 else ""
        dir_cols.append(f'<ul class="mega__list{show}" data-dirs="{fid}" role="list">{"".join(d_items)}</ul>')

    first_img = CATALOG[0][2]
    return f'''<div class="mega" data-mega hidden>
          <div class="mega__panel">
            <ul class="mega__col mega__col--fac" role="list">{"".join(fac_items)}</ul>
            <div class="mega__col mega__col--dir">{"".join(dir_cols)}</div>
            <div class="mega__col mega__col--course">{"".join(course_cols)}</div>
            <div class="mega__media">{img(first_img,"",880,880,"mega__img",True," data-mega-img")}</div>
          </div>
        </div>'''

def header(active=""):
    def nav_item(h, t, dd):
        cur = A_CUR_PAGE if active == t else ""
        sub = SUBMENU.get(t)
        if not sub:
            return f'<a class="nav__link" href="{h}"{cur}>{t}{icon("chevron-down") if dd else ""}</a>'
        inner = "".join(f'<a href="{sh}">{st}</a>' for sh, st in sub)
        # У раздела без своей страницы триггер — кнопка: отключённая ссылка выпала бы
        # из таб-порядка, и список нельзя было бы раскрыть с клавиатуры.
        trigger = (f'<button class="nav__link" type="button" aria-haspopup="true">{t}{icon("chevron-down")}</button>'
                   if h == "#" else
                   f'<a class="nav__link" href="{h}"{cur} aria-haspopup="true">{t}{icon("chevron-down")}</a>')
        return (f'<div class="nav__group">{trigger}'
                f'<div class="nav__drop"><div class="nav__drop-inner">{inner}</div></div></div>')
    links = "".join(nav_item(h, t, dd) for h, t, dd in NAV)
    dlinks = "".join(
        f'<a href="{h}">{t}</a>' + "".join(f'<a class="drawer__sub" href="{sh}">{st}</a>' for sh, st in SUBMENU.get(t, []))
        for h, t, _ in NAV)
    search_chips = "".join(f'<a class="search-chip" href="{FAC_LINKS.get(f, "#")}">{f}</a>' for f in SEARCH_DIRECTIONS)
    return f'''
  <div class="site-top" data-site-top>
  <div class="promo" data-promo="autumn-2026">
    <div class="promo__inner container">
      <p class="promo__text">Скидка до 25% на курсы с осенним стартом — до 30 сентября</p>
      <a class="promo__cta" href="faculty-massage.html">Выбрать курс</a>
    </div>
    <button class="icon-btn icon-btn--sm icon-btn--white promo__close" type="button" data-promo-close aria-label="Закрыть акцию">{icon("close","icon icon--sm")}</button>
  </div>
  <header class="header">
    <div class="container">
      <div class="header__top">
        {logo()}
        <div class="header__contact">{icon("map-pin")}<span>Москва, м. Кузнецкий Мост,<br>ул. Кузнецкий Мост, 21/5</span></div>
        <div class="header__contacts">
          <a class="header__phone t-nums" href="{PHONE_HREF}">{icon("phone","icon icon--sm")}{PHONE}</a>
          <a class="header__mail" href="mailto:{EMAIL}">{icon("mail","icon icon--sm")}{EMAIL}</a>
        </div>
        <div class="header__actions">
          <a class="header__callback" href="#lead" ><span>Заказать звонок</span><i class="icon-btn">{icon("phone","icon icon--sm")}</i></a>
          <button class="icon-btn" type="button" data-open="modal-search" aria-controls="modal-search" aria-expanded="false" aria-label="Поиск по сайту">{icon("search")}</button>
          <a class="icon-btn cart-btn" href="cart.html" aria-label="Корзина">{icon("cart")}<span class="cart-btn__count" data-cart-count>2</span></a>
        </div>
        <div class="header__mobile-actions">
          <a class="icon-btn icon-btn--sm icon-btn--accent" href="{PHONE_HREF}" aria-label="Позвонить">{icon("phone","icon icon--sm")}</a>
          <button class="icon-btn icon-btn--sm" type="button" data-open="modal-search" aria-controls="modal-search" aria-expanded="false" aria-label="Поиск по сайту">{icon("search","icon icon--sm")}</button>
          <a class="icon-btn icon-btn--sm" href="cart.html" aria-label="Корзина">{icon("cart","icon icon--sm")}</a>
          <button class="icon-btn icon-btn--sm icon-btn--dark" type="button" data-open="menu" aria-controls="menu" aria-expanded="false" aria-label="Открыть меню">{icon("menu","icon icon--sm")}</button>
        </div>
      </div>
      <div class="header__nav" data-mega-root>
        <a class="catalog-btn" href="faculty-massage.html" data-mega-trigger aria-haspopup="true" aria-expanded="false">{icon("menu")}Каталог курсов</a>
        <nav class="nav" aria-label="Основное меню">{links}</nav>
        {mega_menu()}
      </div>
    </div>
  </header>
  </div>
  <div class="drawer" id="menu" aria-hidden="true">
    <div class="drawer__overlay" data-close></div>
    <div class="drawer__panel" role="dialog" aria-modal="true" aria-label="Меню">
      <div class="drawer__head">{logo()}<button class="icon-btn icon-btn--sm" type="button" data-close aria-label="Закрыть меню">{icon("close","icon icon--sm")}</button></div>
      <nav class="drawer__nav" aria-label="Мобильное меню"><a href="faculty-massage.html">Каталог курсов</a>{dlinks}</nav>
      <a class="btn btn--primary btn--block" href="{PHONE_HREF}">{icon("phone")}Позвонить</a>
      <p class="t-body-s t-muted">{ADDR}<br>Пн–Пт 9:00–20:00, Сб–Вс 10:00–16:00</p>
    </div>
  </div>
  <div class="modal modal--search" id="modal-search" aria-hidden="true">
    <div class="modal__overlay" data-close></div>
    <div class="modal__dialog search-modal" role="dialog" aria-modal="true" aria-label="Поиск по сайту">
      <div class="search-modal__head">
        <form class="search-bar" role="search" action="#" data-search-form>
          <label class="search-bar__field">{icon("search")}<span class="visually-hidden">Поиск по сайту</span><input class="search-bar__input" type="search" name="q" placeholder="Текст поискового запроса" autocomplete="off" enterkeyhint="search" aria-controls="search-results"></label>
          <button class="search-bar__clear" type="reset" aria-label="Очистить запрос">{icon("close","icon icon--sm")}</button>
        </form>
        <button class="icon-btn icon-btn--sm search-modal__close" type="button" data-close aria-label="Закрыть поиск">{icon("close","icon icon--sm")}</button>
      </div>
      <div class="search-modal__body" data-search-idle>
        <p class="search-modal__label">Направления обучения</p>
        <div class="search-modal__chips">{search_chips}</div>
      </div>
      <!-- Живая выдача: карточки курсов появляются во время ввода (курсы — assets/js/search-index.js) -->
      <div class="search-modal__body" data-search-results hidden>
        <p class="search-modal__label" data-search-count></p>
        <div class="search-results" id="search-results" role="list" aria-label="Найденные курсы" data-search-list></div>
        <div class="search-none" data-search-none hidden>
          <p class="t-h4">По запросу «<span data-search-query></span>» курсов не нашли</p>
          <p class="t-body-s t-secondary">Проверьте написание или оставьте заявку — методист подберёт программу под вашу специальность.</p>
          <div><a class="btn btn--primary btn--m" href="#lead">Подобрать курс</a></div>
        </div>
      </div>
      <p class="visually-hidden" role="status" aria-live="polite" data-search-status></p>
    </div>
  </div>'''

def field(kind="text", name="name", ph="Имя*", required=True, surface=False, error=None):
    req = " required" if required else ""
    cls = "field field--surface" if surface else "field"
    err = error or ("Введите номер полностью" if kind=="tel" else "Заполните поле")
    auto = {"name":"name","phone":"tel","email":"email","fio":"name","spec":"organization-title"}.get(name,"on")
    if kind == "tel":
        return f'''<div class="{cls}"><label class="field__control"><span class="field__prefix"><i class="flag-ru"></i>{icon("chevron-down","icon icon--xs")}</span><span class="visually-hidden">Телефон</span><input class="field__input" type="tel" name="{name}" inputmode="tel" autocomplete="tel" placeholder="+7 (___) ___-__-__"{req}></label><span class="field__error">{err}</span></div>'''
    typ = "email" if name=="email" else "text"
    return f'''<div class="{cls}"><label class="field__control"><span class="visually-hidden">{ph.rstrip("*")}</span><input class="field__input" type="{typ}" name="{name}" autocomplete="{auto}" placeholder="{ph}"{req}></label><span class="field__error">{err}</span></div>'''

def consent(dark=False, rules=False):
    # rules — формулировка блока «Остались вопросы?» из макета, со ссылкой на правила Платформы
    text = ('Соглашаюсь на <a href="#">обработку персональных данных</a> и с <a href="#">правилами пользования Платформой</a>.'
            if rules else 'Согласен(на) на <a href="#">обработку персональных данных</a>')
    return f'''<label class="check"><input type="checkbox" name="consent" required checked><span class="check__box"></span><span>{text}</span></label>'''

def footer():
    fac = ["Медицинская подготовка","Аккредитация медработников","Курсы НМО для врачей","Косметология","Массаж и реабилитация","Диетология","Здоровье и развитие ребёнка","Парикмахерское искусство","Бухгалтерский учёт и кадры","Менеджмент"]
    menu = [("schedule.html","Расписание"),("accreditation.html","Аккредитация"),("employment.html","Трудоустройство"),("events.html","Мероприятия"),("promotions.html","Акции"),("about.html","О центре"),("teachers.html","Преподаватели"),("#","Сведения об образовательной организации"),("contacts.html","Контакты")]
    return f'''
  <footer class="footer" id="lead">
    <div class="container">
      <div class="footer__lead">
        <div class="stack gap-md">
          <h2>Не нашли свой курс?<br>Подберём программу за 5 минут</h2>
          <p class="t-body-m">Оставьте телефон — методист перезвонит в рабочее время, уточнит вашу специальность и подскажет курс под аккредитацию, баллы НМО или новую профессию. Бесплатно и без навязчивых звонков.</p>
        </div>
        <form class="footer__form on-dark" data-lead novalidate>
          {field("text","name","Имя*")}
          <div class="row">{field("tel","phone")}{field("text","spec","Ваша специальность",False)}</div>
          {consent(True)}
          <div><button class="btn btn--primary" type="submit">Подобрать курс</button></div>
        </form>
      </div>
      <div class="footer__divider"></div>
      <div class="footer__cols">
        <div class="footer__col"><h3>Направления</h3>{"".join(f'<a href="{FAC_LINKS.get(f, "#")}">{f}</a>' for f in fac)}</div>
        <div class="footer__col footer__col--menu"><h3>Центр</h3>{"".join(f'<a href="{h}">{t}</a>' for h,t in menu)}</div>
        <div class="footer__col"><h3>Новости и акции</h3><p class="footer__muted">Даты стартов, скидки и бесплатные мероприятия — раз в неделю</p>
          <div><a class="btn btn--primary btn--m" href="#">{icon("send","icon icon--sm")}Подписаться в Telegram</a></div>
          <a class="store-badge" href="#"><span><small>Скачайте из</small><b>RuStore</b></span></a></div>
        <div class="footer__col">
          {logo(True)}
          <a class="t-h4 t-nums" href="{PHONE_HREF}">{PHONE}</a>
          <a href="mailto:{EMAIL}">{EMAIL}</a>
          <address class="footer__muted">{ADDR}. Пн–Пт 9:00–20:00, Сб–Вс 10:00–16:00</address>
          <p class="footer__legal">{ORG_LEGAL} — {ORG_BRAND}. Лицензия на образовательную деятельность {LICENSE_FULL}. ИНН {INN}, ОГРН {OGRN}</p>
          <img class="footer__portal" src="assets/img/moscow-portal.webp" width="300" height="59" loading="lazy" alt="Участник портала поставщиков Правительства Москвы">
        </div>
      </div>
      <div class="footer__divider"></div>
      <div class="footer__bottom"><span>© {YEAR_FROM}–<span data-year>2026</span> {ORG_LEGAL}</span><a href="#">Политика конфиденциальности</a><a href="#">Оферта</a></div>
    </div>
  </footer>
  <div class="modal" id="modal-lead" aria-hidden="true">
    <div class="modal__overlay" data-close></div>
    <div class="modal__dialog modal__dialog--form" role="dialog" aria-modal="true" aria-labelledby="lead-popup-title">
      <button class="icon-btn icon-btn--sm modal__close" type="button" data-close aria-label="Закрыть">{icon("close","icon icon--sm")}</button>
      <div class="lead-popup__head">
        <h2 class="t-h3" id="lead-popup-title" data-popup-title>Записаться на курс</h2>
        <p class="t-body-s t-secondary">Оставьте имя и телефон — методист перезвонит за 15 минут в рабочее время и ответит на вопросы.</p>
      </div>
      <form class="lead-popup__form" data-lead novalidate>
        {field("text","name","Имя*",surface=True)}
        {field("tel","phone",surface=True)}
        <button class="btn btn--primary btn--block" type="submit">Отправить</button>
        <p class="t-caption t-muted">Нажимая «Отправить», вы соглашаетесь на обработку персональных данных</p>
      </form>
    </div>
  </div>
  <div class="modal" id="modal-success" aria-hidden="true">
    <div class="modal__overlay" data-close></div>
    <div class="modal__dialog" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <button class="icon-btn icon-btn--sm modal__close" type="button" data-close aria-label="Закрыть">{icon("close","icon icon--sm")}</button>
      <div class="modal__icon">{icon("check")}</div>
      <h2 class="t-h3" id="modal-title">Спасибо! Заявка принята</h2>
      <p class="t-body-m t-secondary">Методист перезвонит в течение 15 минут в рабочее время: Пн–Пт 9:00–20:00, Сб–Вс 10:00–16:00.</p>
      <button class="btn btn--primary btn--m" type="button" data-close>Хорошо</button>
    </div>
  </div>'''

ORG_LD = {
  "@context":"https://schema.org","@type":"EducationalOrganization",
  "name":ORG_BRAND+" (МЦПО)","alternateName":"МЦПО","legalName":ORG_LEGAL,
  "url":SITE,"logo":SITE+"/assets/icons/logo.svg","telephone":PHONE_TEL,"email":EMAIL,
  "taxID":INN,"identifier":OGRN,
  "address":{"@type":"PostalAddress","streetAddress":"ул. Кузнецкий Мост, 21/5, подъезд 1, этаж 4, офис 4002","addressLocality":"Москва","addressCountry":"RU"},
  "hasCredential":{"@type":"EducationalOccupationalCredential","credentialCategory":"Лицензия на образовательную деятельность "+LICENSE_FULL},
  "openingHours":["Mo-Fr 09:00-20:00","Sa-Su 10:00-16:00"]
}

def crumbs_ld(items):
    return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":SITE+"/"+u} for i,(n,u) in enumerate(items)]}

def breadcrumbs(items):
    lis = []
    for i,(n,u) in enumerate(items):
        if i == len(items)-1: lis.append(f'<li><span aria-current="page">{n}</span></li>')
        else: lis.append(f'<li><a href="{u}">{n}</a></li>')
    return f'<nav class="breadcrumbs" aria-label="Хлебные крошки"><ol>{"".join(lis)}</ol></nav>'

def page(fname, title, desc, body, active="", lds=(), crumbs=None, extra_end=""):
    ld = [ORG_LD] + list(lds)
    if crumbs: ld.append(crumbs_ld(crumbs))
    robots = '\n  <meta name="robots" content="noindex, follow">' if fname.startswith(("cart", "checkout")) else ""
    ld_html = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    html = f'''<!DOCTYPE html>
<html lang="ru" class="no-js">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{SITE}/{fname}">{robots}
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="{SITE}/assets/img/hero.webp">
  <meta name="theme-color" content="#1c263b">
  <link rel="icon" href="assets/icons/logo.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Onest:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/tokens.css">
  <link rel="stylesheet" href="assets/css/base.css">
  <link rel="stylesheet" href="assets/css/components.css">
  <link rel="stylesheet" href="assets/css/pages.css">
  {ld_html}
</head>
<body>
  <a class="skip-link" href="#main">Перейти к содержанию</a>
  <div class="page">
{header(active)}
  <main class="main page-fade" id="main">
{body}
  </main>
{footer()}
  </div>
{extra_end}
  <script src="assets/js/main.js" defer></script>
</body>
</html>
'''
    html = finalize(html)
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(html)
    return fname

def finalize(html):
    # Кнопки заявки (Записаться, Заказать звонок, Подобрать курс) открывают всплывающую форму
    html = html.replace(' href="#lead"', ' role="button" tabindex="0" data-popup="lead"')
    html = html.replace(' href="#quiz"', ' role="button" tabindex="0" data-popup="lead"')
    # Ссылки на неготовые страницы: без href, без перехода и без hover
    html = html.replace(' href="#"', ' aria-disabled="true"')
    # Кнопки-заглушки
    for label in ("Показать ещё 18 курсов", "Показать ещё даты", "Есть промокод?"):
        html = html.replace(f'type="button">{label}<', f'type="button" aria-disabled="true">{label}<')
        html = html.replace(f'type="button" style="align-self:center">{label}<', f'type="button" style="align-self:center" aria-disabled="true">{label}<')
        html = html.replace(f'type="button" style="align-self:flex-start">{label}<', f'type="button" style="align-self:flex-start" aria-disabled="true">{label}<')
    return html

# ======================= Блоки =======================
def img(src, alt, w, h, cls="", lazy=True, extra=""):
    l = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="assets/img/{src}.webp" alt="{alt}" width="{w}" height="{h}"{l}{extra}>'

def section_head(title, lead=None, center=True, tag="h2"):
    lead_html = f'<p class="section-head__lead">{lead}</p>' if lead else ""
    return f'<div class="section-head{" section-head--center" if center else ""} reveal"><{tag} class="section-head__title">{title}</{tag}>{lead_html}</div>'

def course_card(title, meta, old, price, badges, image, href=None, btn="Записаться на курс"):
    b = "".join(f'<span class="badge badge--{k}">{t}</span>' for k,t in badges)
    if href is None:
        href = READY_COURSE if title.startswith("Классический массаж с нуля") else "#"
    hover = " card-hover" if href != "#" else ""
    old_html = f'<span class="course-card__old">{old}</span>' if old else ""
    return f'''<article class="course-card{hover} reveal">
        <div class="course-card__media media-zoom">{img(image, title, 880, 540)}<div class="course-card__badges">{b}</div></div>
        <div class="course-card__body">
          <h3 class="course-card__title"><a href="{href}">{title}</a></h3>
          <p class="course-card__meta">{meta}</p>
          <p class="course-card__price">{old_html}<span class="course-card__now">{price}</span></p>
          <div class="course-card__actions"><a class="btn btn--primary btn--m" href="#lead">{btn}</a><a class="more-link" href="{href}">Подробнее{icon("arrow-right")}</a></div>
        </div>
      </article>'''

def tabs(items, active=0, label="Направления", size=""):
    return f'<div class="tabs" role="tablist" aria-label="{label}">' + "".join(
        f'<button class="tab{" tab--l" if size=="l" else ""}{" is-active" if i==active else ""}" type="button" role="tab" aria-selected="{"true" if i==active else "false"}" tabindex="{0 if i==active else -1}">{t}</button>' for i,t in enumerate(items)) + '</div>'

def reviews_block(title="Отзывы выпускников МЦПО"):
    data = [("Прошла повышение квалификации по медицинскому массажу. 70% занятий — практика на моделях, преподаватель ставит руку лично. Удостоверение пришло в ФИС ФРДО через 2 недели.","Ольга К.","Медицинский массаж, 144 ч"),
            ("Училась дистанционно из Казани: лекции смотрела вечером после смены, тесты сдавала на платформе. Баллы НМО засчитали без вопросов.","Марина Л., медсестра","Сестринское дело, 36 ч"),
            ("Пришёл без медицинского образования, через 2 месяца уже работал в SPA-салоне. Отдельное спасибо за разбор анатомии.","Александр Д.","Классический массаж, 72 ч"),
            ("Повышение квалификации по кардиологии, 144 часа. Материалы открыты круглосуточно — занимался после дежурств. Удостоверение потом сам проверил в ФИС ФРДО.","Сергей В., врач-кардиолог","Кардиология, 144 ч"),
            ("Переподготовка по диетологии после терапии. Больше всего пригодились разборы клинических случаев — с января веду приём по новой специальности.","Ирина П., врач","Диетология, 504 ч"),
            ("Сдавала первичную специализированную аккредитацию там же, где училась. Перед процедурой сходила на отработку навыков — на самой аккредитации волнения почти не было.","Наталья Ж., медсестра","Медицинский массаж, ПСА"),
            ("Работаю косметологом, добирала баллы НМО. Свидетельство выдали сразу после итогового теста, у работодателя вопросов не возникло.","Юлия С., врач-косметолог","Сестринское дело в косметологии"),
            ("Живу в Новосибирске, училась дистанционно. Куратор напоминал о дедлайнах, это правда помогло дойти до конца, а не бросить на середине.","Екатерина М., медсестра","Физиотерапия, 144 ч")]
    items = []
    for i,(t,n,c) in enumerate(data):
        items.append(f'<article class="review"><div>{QUOTE}</div><p class="review__text">{t}</p><div><p class="review__name">{n}</p><p class="review__course">{c}</p></div></article>')
        if i < 2: items.append(f'<button class="review review--video" type="button" aria-label="Смотреть видеоотзыв выпускника">{img("review-video","Видеоотзыв выпускника",420,536)}<span class="play">{PLAY}</span></button>')
    return f'''<section class="section container" aria-labelledby="reviews-title">
      <div class="section-head section-head--center reveal"><h2 class="section-head__title" id="reviews-title">{title}</h2><p class="section-head__lead">Врачи, медсёстры и массажисты — о практике, преподавателях и документах</p></div>
      <div class="carousel stack gap-xl" data-carousel>
        <div class="scroller" data-track>{"".join(items)}</div>
        <div class="row gap-md" style="justify-content:center"><button class="carousel__btn" type="button" data-prev aria-label="Назад">{icon("chevron-left")}</button><div class="dots" data-dots></div><button class="carousel__btn" type="button" data-next aria-label="Вперёд">{icon("chevron-right")}</button></div>
      </div>
    </section>'''

TEACHERS = [("Селявин Михаил Юрьевич","Медицинский массажист, стаж преподавания 10 лет","teacher"),
            ("Шепелев Владимир Иванович","Врач-педиатр, массажист, стаж 15 лет","teacher"),
            ("Орлова Марина Сергеевна","Врач ЛФК и спортивной медицины, стаж 12 лет","expert"),
            ("Климов Андрей Петрович","Врач-невролог, реабилитолог, стаж 18 лет","teacher"),
            ("Соколова Елена Викторовна","Врач-косметолог, дерматолог, стаж 14 лет","expert"),
            ("Гаврилов Денис Олегович","Медицинский массажист, стаж 10 лет","teacher"),
            ("Никитина Ольга Андреевна","Врач-терапевт, методист НМО, стаж 20 лет","expert"),
            ("Морозов Илья Константинович","Остеопат, мануальный терапевт, стаж 11 лет","teacher"),
            ("Белова Анна Дмитриевна","Врач-диетолог, стаж 9 лет","expert")]

# У кого есть своя страница — карточка ведёт на неё, остальные на общий список.
TEACHER_LINKS = {"Селявин Михаил Юрьевич": "teacher-selyavin.html"}

def teacher_card(name, role, pic, cls="teacher"):
    return f'<a class="{cls}" href="{TEACHER_LINKS.get(name, "teachers.html")}">{img(pic, name, 600, 720)}<div class="teacher__info"><div class="grow"><p class="teacher__name">{name}</p><p class="teacher__role">{role}</p></div><span class="icon-btn">{icon("arrow-up-right","icon icon--sm")}</span></div></a>'

def teachers_block():
    cards = "".join(teacher_card(*t) for t in TEACHERS)
    return f"""<section class="section container" aria-labelledby="teachers-title">
      <div class="section-head section-head--center reveal"><h2 class="section-head__title" id="teachers-title">Преподаватели — практикующие врачи и эксперты</h2></div>
      <div class="focus-carousel stack gap-xl" data-focus-carousel>
        <div class="focus-carousel__viewport"><div class="focus-carousel__track" data-track>{cards}</div></div>
        <div class="row gap-md" style="justify-content:center"><button class="carousel__btn" type="button" data-prev aria-label="Предыдущий преподаватель">{icon("chevron-left")}</button><a class="btn btn--outline btn--m" href="teachers.html">Все преподаватели</a><button class="carousel__btn" type="button" data-next aria-label="Следующий преподаватель">{icon("chevron-right")}</button></div>
      </div>
    </section>"""

def faq_block(title, qs, ident="faq"):
    items = "".join(f'<details class="faq reveal"{" open" if i==0 else ""}><summary><span class="faq__q">{q}</span><span class="faq__icon">{icon("chevron-down")}</span></summary><div class="faq__a"><p>{a}</p></div></details>' for i,(q,a) in enumerate(qs))
    ld = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in qs]}
    return f'''<section class="section container" aria-labelledby="{ident}-title" data-stagger>
      <div class="section-head section-head--center reveal"><h2 class="section-head__title" id="{ident}-title">{title}</h2></div>
      <div class="stack gap-md" data-accordion>{items}</div>
    </section>''', ld

# Кузнецкий Мост — административный корпус, занятия идут на двух учебных.
LOCATIONS = [("Автозаводская","Учебный корпус: ул. Ленинская Слобода, 26, к. С,<br>БЦ «Омега-2», этаж 2"),
             ("Ботанический сад","Учебный корпус: ул. Вильгельма Пика, 11,<br>БЦ «Ботаника»"),
             ("Кузнецкий мост","Административный корпус: ул. Кузнецкий Мост, 21/5,<br>подъезд 1, этаж 4, офис 4002")]

def map_block(title="Где нас найти", tag="h2", extra=""):
    locs = "".join(f'<button class="location{" is-active" if i==0 else ""}" type="button" data-location aria-pressed="{"true" if i==0 else "false"}"><span class="location__title">{t}</span><address class="location__addr">{a}</address><span class="location__link">Смотреть на карте{icon("arrow-right")}</span></button>' for i,(t,a) in enumerate(LOCATIONS))
    return f"""<section class="container{(" " + extra) if extra else ""}" aria-labelledby="map-title">
      <div class="map-block reveal">
        <div class="map-block__list" data-locations>
          <{tag} id="map-title" class="map-block__title">{title}</{tag}>
          {locs}
        </div>
        <div class="map-block__map">
          {img("map","Карта: МЦПО у метро Кузнецкий Мост",1920,960)}
          <button class="btn btn--white btn--m map-block__load" type="button" data-map-load="https://yandex.ru/map-widget/v1/?text=Москва%2C%20Кузнецкий%20Мост%2021%2F5&amp;z=16">Открыть интерактивную карту</button>
          <div class="map-block__chips">
            <div class="map-chip"><a class="t-medium t-nums" href="{PHONE_HREF}">{icon("phone","icon icon--sm")}{PHONE}</a><a href="mailto:{EMAIL}">{icon("mail","icon icon--sm")}{EMAIL}</a></div>
            <div class="map-chip"><b>График работы</b><span>Пн - Пт: 9:00 - 20:00<br>Сб - Вс: 10:00 - 16:00</span></div>
          </div>
        </div>
      </div>
    </section>"""

def lead_block(title="Остались вопросы?"):
    """Блок заявки — макет 973-4665: тёмная карточка с формой и гарнитурой, справа фото."""
    return f'''<section class="container" aria-labelledby="lead-title">
      <div class="lead-block reveal">
        <div class="lead-block__card">
          <div class="lead-block__art" aria-hidden="true">
            {img("lead-3d","",354,536,"lead-block__headset")}
            {img("star-3d","",600,586,"lead-block__star lead-block__star--s")}
            {img("star-3d","",600,586,"lead-block__star lead-block__star--l")}
          </div>
          <div class="lead-block__head">
            <h2 id="lead-title">{title}</h2>
            <p class="lead-block__text">Оставьте заявку и наш менеджер свяжется с вами</p>
          </div>
          <form class="lead-form on-dark" data-lead novalidate>
            <div class="lead-form__fields">
              {field("text","name","Имя*")}
              {field("tel","phone")}
            </div>
            {consent(True, rules=True)}
            <div class="lead-form__submit"><button class="btn btn--primary" type="submit">Записаться</button></div>
          </form>
        </div>
        <div class="lead-block__photo">{img("lead-operator","Менеджер МЦПО консультирует по телефону",946,1000)}</div>
      </div>
    </section>'''

def why_block():
    stats = [("stat-medal","20+","20","лет обучаем медицинских специалистов","","+"),("stat-teacher","160+","160","преподавателей-практиков: врачей и экспертов","","+"),("stat-cap","350\u00a0000+","350000","выпускников по всей России","","+"),("stat-one","400+","400","программ повышения квалификации и переподготовки","","+")]
    def stat_html(i, v, c, l, p, su):
        attrs = f' data-count="{c}" data-prefix="{p}" data-suffix="{su}"'
        return (f'<div class="stat reveal"><span class="stat__media">{img(i,"",400,400,"stat__img")}</span>'
                f'<div class="stat__body"><p class="stat__value"{attrs}>{v}</p><p class="stat__label">{l}</p></div></div>')
    s = "".join(stat_html(*row) for row in stats)
    return f'''<section class="container" aria-labelledby="why-title">
      <div class="why">
        <div class="section-head section-head--center reveal"><h2 class="section-head__title" id="why-title">Почему выбирают МЦПО</h2><p class="section-head__lead">{ORG_BRAND} обучает медицинских специалистов более 20 лет. Лицензия {LICENSE_FULL}. Программы соответствуют профстандартам, а документы вносятся в федеральный реестр ФИС ФРДО.</p></div>
        <a class="btn btn--primary reveal" href="#">Подробнее о центре</a>
        <div class="why__stats" data-stagger>{s}</div>
      </div>
    </section>'''

# ======================= СТРАНИЦЫ =======================
HOME_FAQ = [("Какие документы я получу после обучения?","Удостоверение о повышении квалификации или диплом о профессиональной переподготовке установленного образца. Сведения о документе вносим в федеральный реестр ФИС ФРДО."),
            ("Можно ли учиться дистанционно, если я не в Москве?","Да. Большинство программ доступны онлайн: лекции и тесты на платформе 24/7, документы отправляем почтой по всей России."),
            ("Засчитываются ли курсы в баллы НМО?","Да, если программа размещена на портале НМО (edu.rosminzdrav.ru): 1 академический час = 1 зачётная единица. Количество баллов указано на странице курса."),
            ("Можно ли вернуть 13% стоимости обучения?","Да. У МЦПО есть образовательная лицензия, поэтому вы можете оформить социальный налоговый вычет. Справку и копию лицензии выдаём бесплатно."),
            ("Можно ли пройти курс без медицинского образования?","Да, для курсов классического массажа, SPA-процедур и эстетической косметологии медицинское образование не требуется. Медицинский массаж и врачебные программы — только для медработников.")]

POPULAR = [("Медицинский массаж: повышение квалификации, 144 ч","Для медсестёр по массажу · очно или онлайн · удостоверение в ФИС ФРДО","24 000 ₽","от 19 100 ₽",[("edu","с мед. образованием"),("hours","144 ак. ч.")],"course-1"),
           ("Классический массаж с нуля: курс с сертификатом","Без медицинского образования · 80% практики · группы до 12 человек","21 000 ₽","от 16 900 ₽",[("edu","без мед. образования"),("hours","72 ак. ч.")],"dir-massage"),
           ("Врач-косметолог: профессиональная переподготовка","Для врачей-дерматовенерологов · диплом о переподготовке · 576 ак. ч.","110 000 ₽","от 89 000 ₽",[("edu","с мед. образованием"),("hours","576 ак. ч.")],"tile-cosm"),
           ("Медицинский массаж: первичная специализация, 288 ч","Для медсестёр без сертификата по массажу · сертификат специалиста","42 000 ₽","от 34 500 ₽",[("edu","с мед. образованием"),("hours","288 ак. ч.")],"tile-massage"),
           ("Лимфодренажный массаж","Ручные техники · отработка на моделях · сертификат","12 000 ₽","от 9 500 ₽",[("edu","без мед. образования"),("hours","24 ак. ч.")],"persp-2"),
           ("Инъекционная косметология для врачей","Контурная пластика и ботулинотерапия · удостоверение о ПК","64 000 ₽","от 52 000 ₽",[("edu","с мед. образованием"),("hours","140 ак. ч.")],"dir-cosm"),
           ("Подготовка к периодической аккредитации","Портфолио, тестирование, баллы НМО · дистанционно","9 900 ₽","от 7 600 ₽",[("nmo","36 баллов НМО"),("hours","36 ак. ч.")],"tile-accred"),
           ("Детский массаж: повышение квалификации","Для медсестёр по массажу · практика с детьми · удостоверение","26 000 ₽","от 21 000 ₽",[("edu","с мед. образованием"),("hours","72 ак. ч.")],"dir-child")]

def home():
    tiles = [("Медицинская подготовка","tile-med"),("Аккредитация медработников","tile-accred"),("Косметология","tile-cosm"),("Массаж и реабилитация","tile-massage")]
    tiles_html = "".join(f'<a class="cat-tile" href="{FAC_LINKS.get(t, "#")}">{img(i,"",626,626)}<span class="cat-tile__title">{t}</span><span class="icon-btn">{icon("arrow-up-right","icon icon--sm")}</span></a>' for t,i in tiles)
    slides = [("hero","Повышение квалификации и переподготовка медицинских специалистов","Курсы для врачей, медсестёр, массажистов и косметологов с баллами НМО. Удостоверение вносим в ФИС ФРДО. Очно в Москве или дистанционно.","Преподаватель МЦПО показывает технику массажа слушателям"),
              ("course-desc","Курсы массажа с удостоверением — от классического до медицинского","66 программ для начинающих и практикующих специалистов: 80% занятий — практика на моделях у м. Автозаводская и Ботанический сад.","Занятие по классическому массажу"),
              ("quiz-doctor","Курсы НМО для врачей дистанционно — из любого города России","Лекции и тесты на платформе 24/7, баллы засчитываются на портале НМО, документ вносим в ФИС ФРДО.","Врач проходит курс повышения квалификации онлайн"),
              ("group-practice","Практика в небольших группах до 12 человек","Преподаватель ставит руку каждому слушателю, а видеозаписи техник остаются на платформе.","Группа на практическом занятии")]
    media, texts, prog = [], [], []
    for i, (im, t, l, alt) in enumerate(slides):
        act = " is-active" if i == 0 else ""
        load = ' fetchpriority="high"' if i == 0 else ' loading="lazy" decoding="async"'
        media.append(f'<img class="hero-slider__img{act}" src="assets/img/{im}.webp" alt="{alt}" width="1404" height="1300"{load}>')
        title = f"<h1>{t}</h1>" if i == 0 else f'<p class="t-h1">{t}</p>'
        hidden = "" if i == 0 else ' aria-hidden="true"'
        texts.append(f'<div class="hero-slider__text{act}"{hidden}>{title}</div>')
        prog.append(f'<span class="hero-progress__seg{act}"><i></i></span>')
    slides_media, slides_text, slides_progress = "".join(media), "".join(texts), "".join(prog)
    dirs = [("Массаж и реабилитация","66 курсов","dir-massage"),("Косметология","39 курсов","dir-cosm"),("Медицинская подготовка","155 курсов","dir-med"),("Здоровье и развитие ребёнка","8 курсов","dir-child")]
    dirs_html = "".join(f'<a class="dir-tile reveal" href="{FAC_LINKS.get(t, "#")}">{img(i,"",660,854)}<span class="badge badge--count">{c}</span><span class="dir-tile__title">{t}</span></a>' for t,c,i in dirs)
    faq_html, faq_ld = faq_block("Частые вопросы об обучении", HOME_FAQ)
    body = f'''
    <section class="container" aria-label="Главный экран">
      <div class="hero">
        <div class="hero__main hero-slider" data-hero-slider data-interval="6000">
          <div class="hero-slider__media" aria-hidden="true">{slides_media}</div>
          <div class="hero-slider__body">
            <div class="hero-slider__texts" aria-live="polite">{slides_text}</div>
            <div class="hero-slider__bar">
              <a class="btn btn--white hero-slider__more" href="faculty-massage.html">Подробнее{icon("arrow-up-right")}</a>
              <div class="hero-progress" aria-hidden="true">{slides_progress}</div>
            </div>
          </div>
        </div>
        <div class="hero__tiles">{tiles_html}</div>
      </div>
    </section>

    <section class="section container" aria-labelledby="popular-title">
      {section_head("Популярные курсы повышения квалификации","Программы с удостоверением установленного образца: очно в Москве или онлайн из любого города").replace('<h2 class="section-head__title">','<h2 class="section-head__title" id="popular-title">')}
      <div class="row" style="justify-content:center">{tabs(["Массаж","Косметология","Медицина","Диетология","Менеджмент"], 0, "Направления курсов")}</div>
      <div class="carousel stack gap-xl" data-carousel>
        <div class="scroller courses-scroller" data-track>{"".join(course_card(*c) for c in POPULAR)}</div>
        <div class="row gap-md" style="justify-content:center"><button class="carousel__btn" type="button" data-prev aria-label="Предыдущий курс">{icon("chevron-left")}</button><div class="dots" data-dots></div><button class="carousel__btn" type="button" data-next aria-label="Следующий курс">{icon("chevron-right")}</button></div>
      </div>
      <div class="row" style="justify-content:center"><a class="btn btn--outline" href="faculty-massage.html">Все курсы массажа</a></div>
    </section>

    <section class="section container" aria-labelledby="dirs-title">
      <div class="section-head section-head--center reveal"><h2 class="section-head__title" id="dirs-title">Направления обучения</h2></div>
      <div class="grid grid-4" data-stagger>{dirs_html}</div>
      <div class="quiz reveal" id="quiz">
        <div class="quiz__card"><span class="quiz__decor" aria-hidden="true">{img("quiz-3d","",235,280,"quiz__doc")}{img("star-3d","",600,586,"quiz__star quiz__star--1")}{img("star-3d","",600,586,"quiz__star quiz__star--2")}{img("star-3d","",600,586,"quiz__star quiz__star--3")}</span><div class="stack gap-md"><h2>Не знаете, какой курс выбрать?</h2><p class="quiz__text">Ответьте на 4 вопроса — покажем программы под вашу специальность, образование и цель: аккредитация, баллы НМО или новая профессия.</p></div><div><a class="btn btn--primary" href="#">Пройти тест за 1 минуту</a></div></div>
        <div class="quiz__photo">{img("quiz-doctor","Врач выбирает курс повышения квалификации онлайн",892,890)}</div>
      </div>
    </section>

{why_block()}

    <section class="section container" aria-labelledby="bento-title">
      {section_head("Как МЦПО помогает стать востребованным специалистом","Практика на моделях, преподаватели из клиник и документы, которые принимает любой работодатель").replace('class="section-head__title"','class="section-head__title" id="bento-title"')}
      <div class="bento" data-stagger>
        <article class="feature bento__diploma reveal"><div class="feature__media">{img("adv-diploma","Выпускница МЦПО с удостоверением",748,440)}</div><h3 class="feature__title">Удостоверение в ФИС ФРДО</h3><p class="feature__text">Документ установленного образца: сведения вносим в федеральный реестр — работодатель и аккредитационная комиссия проверят его онлайн.</p></article>
        <article class="feature feature--deco bento__loyalty reveal"><h3 class="feature__title">Скидки до 35% постоянным слушателям</h3><p class="feature__text">Программа лояльности: чем больше курсов вы проходите, тем выгоднее следующий.</p>{img("adv-percent","",1028,798,"feature__deco")}</article>
        <article class="feature feature--photo bento__teachers reveal"><div class="stack gap-sm"><h3 class="feature__title">Преподаватели — практикующие врачи</h3><p class="feature__text">Ведут занятия специалисты с клинической практикой: разбирают реальные случаи, а не только теорию.</p></div>{img("adv-teachers","Преподаватели МЦПО",748,560,"feature__photo")}</article>
        <article class="feature bento__access reveal"><h3 class="feature__title">Материалы остаются у вас</h3><p class="feature__text">Доступ к лекциям, видео и методичкам на платформе — без ограничения срока.</p></article>
        <article class="feature feature--row bento__format reveal"><div class="stack gap-sm"><h3 class="feature__title">Очно в Москве или дистанционно</h3><p class="feature__text">Практика в учебных классах у м. Автозаводская и Ботанический сад или онлайн-обучение из любого города России — документ одинаковый.</p></div>{img("adv-online","Онлайн-занятие по массажу",454,333,"feature__side")}</article>
        <article class="feature bento__approach reveal"><h3 class="feature__title">Небольшие группы и индивидуальный формат</h3><p class="feature__text">Преподаватель успевает поставить руку каждому. Можно учиться индивидуально в удобное время.</p></article>
      </div>
    </section>

    <section class="container" aria-labelledby="docs-title">
      <div class="docs reveal">
        <div class="stack gap-lg"><h2 id="docs-title">Документы, которые вы получите</h2><p class="t-secondary">Удостоверение о повышении квалификации или диплом о профессиональной переподготовке установленного образца. Сведения вносим в ФИС ФРДО.</p><div><a class="btn btn--primary" href="#">Смотреть образцы</a></div></div>
        <div class="docs__imgs">{img("doc-1","Образец удостоверения о повышении квалификации",462,672)}{img("doc-2","Образец диплома о профессиональной переподготовке",250,350)}{img("doc-3","Образец диплома",462,672)}</div>
      </div>
    </section>

{reviews_block()}

    <section class="section container" aria-labelledby="jobs-title">
      {section_head("Помогаем с трудоустройством после обучения","Массажисты и косметологи востребованы в клиниках, SPA-центрах и частной практике. Передаём резюме выпускников партнёрам и учим выстраивать собственную практику.").replace('class="section-head__title"','class="section-head__title" id="jobs-title"')}
      <div class="jobs reveal">
        <article class="jobs__photo-card"><h3>9 из 10 выпускников находят работу по специальности</h3><p class="t-body-s t-muted">80% занятий — практика на моделях: к первому собеседованию рука уже поставлена.</p>{img("jobs-girl","Выпускница МЦПО делает массаж",748,600)}</article>
        <div class="jobs__col">
          <article class="jobs__dark">{img("jobs-cap","",585,467,"deco")}<h3>База вакансий партнёров</h3><p class="t-body-s">Вакансии клиник и SPA-центров с приоритетным рассмотрением выпускников МЦПО</p><a class="btn btn--primary" href="#">Смотреть вакансии</a></article>
          <article class="jobs__light"><h3>Своя практика — с первого месяца</h3><p class="t-body-s t-muted">Пошагово разбираем, как найти первых клиентов, оформить самозанятость и выйти на стабильный доход после получения документа.</p></article>
        </div>
      </div>
    </section>

    <section class="container" aria-labelledby="app-title">
      <div class="app reveal">
        {img("app-bg","",1380,465,"app__bg")}
        <div class="stack gap-lg"><h2 id="app-title">Учитесь в приложении — с телефона и в любое время</h2><p class="t-secondary">Лекции, тесты и связь с преподавателем в одном приложении. Прогресс сохраняется между телефоном и компьютером.</p><div><a class="store-badge store-badge--dark" href="#"><span><small>Скачайте из</small><b>RuStore</b></span></a></div></div>
        {img("app-phone","Приложение МЦПО на смартфоне",463,434,"app__phone")}
      </div>
    </section>

{teachers_block()}
{faq_html}
{map_block()}
'''
    return page("index.html","Курсы повышения квалификации для врачей и медработников в Москве — МЦПО",
                "Повышение квалификации врачей, медсестёр, массажистов и косметологов с баллами НМО. Удостоверение в ФИС ФРДО, очно в Москве и онлайн. Обучаем более 20 лет.",
                body, "", [faq_ld])

MASSAGE_FAQ = [("Нужно ли медицинское образование для курсов массажа?","Для классического, SPA- и антицеллюлитного массажа — нет. Для курсов «Медицинский массаж» нужно среднее или высшее медицинское образование: по окончании выдаём удостоверение или сертификат специалиста."),
               ("Сколько длится обучение массажу?","От 16 академических часов (короткие техники) до 288 часов (первичная специализация «Медицинская сестра по массажу»). Базовый курс классического массажа — 72 часа, около месяца."),
               ("Как проходит практика?","80% занятий — отработка на моделях в учебных классах у м. Автозаводская и Ботанический сад. Группы небольшие, преподаватель проверяет постановку рук у каждого."),
               ("Какой документ я получу?","Удостоверение о повышении квалификации или диплом о профпереподготовке установленного образца с внесением в ФИС ФРДО; для коротких курсов — сертификат МЦПО."),
               ("Можно ли учиться в рассрочку?","Да, доступна рассрочка, а также налоговый вычет 13%. Условия рассрочки уточнит методист.")]

# Карточки курсов на странице факультета массажа. Их же с ценами показывает поиск в шапке.
MASSAGE_COURSES = [("Медицинский массаж: повышение квалификации, 144 ч","Для медсестёр по массажу · очно или онлайн","24 000 ₽","от 19 100 ₽",[("edu","с мед. образованием"),("hours","144 ак. ч.")],"course-1"),
               ("Медицинский массаж: первичная специализация, 288 ч","Для медсестёр без сертификата по массажу","42 000 ₽","от 34 500 ₽",[("edu","с мед. образованием"),("hours","288 ак. ч.")],"dir-massage"),
               ("Классический массаж с нуля","Без медицинского образования · 80% практики","21 000 ₽","от 16 900 ₽",[("edu","без мед. образования"),("hours","72 ак. ч.")],"tile-massage"),
               ("Антицеллюлитный массаж","Короткий практический курс · сертификат","9 900 ₽","от 7 600 ₽",[("edu","без мед. образования"),("hours","16 ак. ч.")],"course-1"),
               ("Лимфодренажный массаж","Ручные техники · отработка на моделях","12 000 ₽","от 9 500 ₽",[("edu","без мед. образования"),("hours","24 ак. ч.")],"dir-massage"),
               ("Массаж при заболеваниях позвоночника","Для массажистов с опытом · сертификат","18 000 ₽","от 14 400 ₽",[("edu","с мед. образованием"),("hours","36 ак. ч.")],"tile-massage")]

def faculty():
    cr = [("Главная","index.html"),("Каталог курсов","faculty-massage.html"),("Массаж и реабилитация","faculty-massage.html")]
    subs = ["Медицинский и оздоровительный массаж","ЛФК и спортивная медицина","SPA-процедуры и коррекция фигуры","Медицинская реабилитация","Массаж лица","Детский массаж"]
    subs_html = '<div class="tabs tabs--wrap" role="tablist" aria-label="Подкатегории">' + "".join(f'<button class="tab tab--l{" is-active" if i==0 else ""}" type="button" role="tab" aria-selected="{"true" if i==0 else "false"}" tabindex="{0 if i==0 else -1}">{t}</button>' for i,t in enumerate(subs)) + '</div>'
    courses = MASSAGE_COURSES
    def fgroup(title, opts, checked=()):
        return f'<fieldset class="filter-group"><legend>{title}</legend>' + "".join(f'<label class="check"><input type="checkbox" name="f"{" checked" if i in checked else ""}><span class="check__box"></span><span>{o}</span></label>' for i,o in enumerate(opts)) + '</fieldset>'
    whom = [("num-1","Новичкам без опыта","Освоите анатомию и базовые техники классического массажа с нуля и сможете принимать первых клиентов."),("num-2","Практикующим массажистам","Добавите медицинский, лимфодренажный и спортивный массаж, расширите услуги и поднимете стоимость сеанса."),("num-3","Медсёстрам и специалистам смежных сфер","Получите сертификат «Медицинский массаж», а фитнес-тренеры и косметологи — востребованный навык.")]
    whom_html = "".join(f'<article class="whom-card reveal"><div class="whom-card__head">{img(i,"",120,128)}<h3>{t}</h3></div><p class="t-body-s t-muted">{d}</p></article>' for i,t,d in whom)
    persp = f'''<div class="persp" data-stagger>
        <article class="persp__card reveal"><p class="t-display" data-count="95" data-suffix="%">95%</p><p class="t-body-s t-muted">выпускников работают по специальности, открывают кабинет или ведут частную практику</p></article>
        <article class="persp__card persp__card--photo reveal"><h3>Медицинские учреждения</h3><p class="t-body-s t-muted">Поликлиники, больницы, реабилитационные и санаторные центры</p>{img("persp-1","",580,432)}</article>
        <article class="persp__card persp__card--photo reveal"><h3>SPA и фитнес-центры</h3><p class="t-body-s t-muted">Салоны красоты, SPA-комплексы и фитнес-клубы</p>{img("persp-2","",580,432)}</article>
        <article class="persp__card reveal"><p class="t-display" data-count="80" data-suffix="%">80%</p><p class="t-body-s t-muted">времени курса — практика на моделях под контролем преподавателя</p></article>
        <article class="persp__card persp__card--photo reveal"><h3>Собственный кабинет</h3><p class="t-body-s t-muted">Частная практика, выезд к клиентам или аренда кабинета</p>{img("persp-3","",580,432)}</article>
        <article class="persp__card persp__card--photo reveal"><h3>Реабилитация</h3><p class="t-body-s t-muted">Восстановление после травм и операций в центрах реабилитации</p>{img("persp-4","",580,432)}</article>
      </div>'''
    faq_html, faq_ld = faq_block("Вопросы о курсах массажа", MASSAGE_FAQ)
    body = f'''
    <section class="container intro">
      {breadcrumbs(cr)}
      <h1>Курсы массажа в Москве с удостоверением</h1>
      <p class="intro__lead">66 программ: от классического массажа с нуля до медицинского массажа для медсестёр. Очно в Москве или онлайн — документ установленного образца.</p>
      {subs_html}
      <div class="catalog">
        <aside class="catalog__filters" id="filters" aria-label="Фильтры">
          <div class="filters-head"><h2 class="t-h3">Фильтры</h2><button class="icon-btn icon-btn--sm" type="button" data-close aria-label="Закрыть фильтры">{icon("close","icon icon--sm")}</button></div>
          <fieldset class="filter-group"><legend>Стоимость, ₽</legend><div class="range"><input type="number" inputmode="numeric" placeholder="от 5 000" aria-label="Цена от"><input type="number" inputmode="numeric" placeholder="до 120 000" aria-label="Цена до"></div></fieldset>
          {fgroup("Ваше образование",["Без медицинского","Среднее медицинское","Высшее медицинское","Знаю основы массажа"])}
          {fgroup("Форма обучения",["Онлайн","Очно в Москве","Индивидуально","Интенсив","По выходным"],(1,))}
          {fgroup("Документ",["Удостоверение о ПК","Диплом о переподготовке","Сертификат","С баллами НМО"],(1,))}
          <button class="btn btn--primary btn--m" type="button" data-close>Показать курсы</button>
        </aside>
        <div class="catalog__results">
          <div class="catalog__bar"><h2 class="t-h3">Медицинский и оздоровительный массаж</h2><button class="btn btn--outline btn--m catalog__filter-btn" type="button" data-open="filters">{icon("filter","icon icon--sm")}<span>Фильтры (<span data-filter-count>2</span>)</span></button><span class="t-body-s t-muted">Найдено 24 курса</span></div>
          <div class="grid grid-3" data-stagger>{"".join(course_card(*c, btn="Записаться") for c in courses)}</div>
        </div>
      </div>
    </section>

    <section class="section container" aria-labelledby="whom-title">
      {section_head("Кому подойдут курсы массажа в МЦПО","Программы разделены по уровню подготовки — выберите свою стартовую точку").replace('class="section-head__title"','class="section-head__title" id="whom-title"')}
      <div class="grid grid-3" data-stagger>{whom_html}</div>
    </section>

    <section class="section container" aria-labelledby="persp-title">
      <div class="section-head section-head--center reveal"><h2 class="section-head__title" id="persp-title">Перспективы профессии массажиста в 2026 году</h2></div>
      {persp}
    </section>

{reviews_block("Отзывы выпускников курсов массажа")}
{lead_block()}

    <section class="container" aria-label="Руководитель факультета">
      <div class="expert reveal">
        <div class="expert__photo">{img("expert","Шепелев Владимир Иванович — руководитель факультета массажа",818,910)}</div>
        <div class="expert__card">
          <div class="expert__tags"><span>Руководитель факультета</span><span>Стаж 15 лет</span><span>Врач ЛФК и спортивной медицины</span></div>
          <h2>Шепелев Владимир Иванович</h2>
          <blockquote class="expert__quote">«Массаж — это прежде всего анатомия. Поэтому на курсах мы сначала учим понимать, что происходит под руками, и только потом — технику. Выпускник должен уверенно работать с первым клиентом, а не бояться навредить».</blockquote>
        </div>
      </div>
    </section>

{faq_html}
{map_block()}
{teachers_block()}
'''
    return page("faculty-massage.html","Курсы массажа в Москве с удостоверением — обучение от 16 900 ₽ | МЦПО",
                "Курсы массажа с нуля и повышение квалификации по медицинскому массажу: 66 программ, 80% практики, удостоверение в ФИС ФРДО. Очно в Москве и онлайн.",
                body, "Аккредитация", [faq_ld], cr)

def course():
    cr = [("Главная","index.html"),("Массаж и реабилитация","faculty-massage.html"),("Классический массаж с нуля","course-classic-massage.html")]
    mods = [("1 модуль","Анатомия и физиология для массажиста","16 ч",["Анатомия опорно-двигательного аппарата","Физиология кожи и мышц","Показания и противопоказания к массажу"]),
            ("2 модуль","Классический массаж: приёмы и техники","24 ч",["Поглаживание, растирание, разминание, вибрация","Эргономика и постановка рук","Отработка на моделях — 70% времени модуля"]),
            ("3 модуль","Массаж отдельных частей тела","24 ч",["Спина и шейно-воротниковая зона","Конечности","Общий массаж тела"]),
            ("4 модуль","Самостоятельная работа и итоговая аттестация","8 ч",["Видеоуроки на платформе","Практический экзамен","Выдача удостоверения"])]
    mods_html = "".join(f'<details class="module reveal"{" open" if i==0 else ""}><summary><span class="module__num">{n}</span><span class="module__title">{t}</span><span class="module__hours">{h}</span>{icon("chevron-down")}</summary><div class="module__content"><ul>{"".join(f"<li>{x}</li>" for x in lst)}</ul></div></details>' for i,(n,t,h,lst) in enumerate(mods))
    rows = [("19 октября 2026","Пн, Ср, Пт",True),("9 ноября 2026","Вт, Чт",False),("23 ноября 2026","Сб, Вс",False)]
    rows_html = "".join(f'<tr{CLS_SOON if s else ""}><td data-label="Дата">{d}</td><td data-label="Дни">{dy}</td><td data-label="Время">09:00–15:00</td><td data-label="Стоимость">38 700 ₽</td><td><a class="btn btn--primary" href="#lead">Записаться</a></td></tr>' for d,dy,s in rows)
    logos = "".join(img(n,a,w,h) for n,a,w,h in [("logo-3sestry","Три сестры",274,270),("logo-dema","ДЭМА",260,310),("logo-emc","EMC",526,316),("logo-ifr","Институт физической реабилитации",500,208),("logo-rehab","Центр реабилитации",594,188)])
    faq_html, faq_ld = faq_block("Вопросы о курсе классического массажа", MASSAGE_FAQ)
    live = [("Практика","Практика на моделях в учебном кабинете","Каждое занятие преподаватель показывает приём, затем вы отрабатываете его в паре и получаете обратную связь. Видеозаписи техник остаются на платформе — можно повторить дома.","group-practice","Группа на практическом занятии по массажу"),
            ("Тесты","Тесты после каждого модуля","Короткие тесты на платформе закрепляют теорию: анатомию, показания и противопоказания. Результаты видит куратор и подсказывает, что повторить перед аттестацией.","quiz-doctor","Слушатель проходит тест на платформе"),
            ("Чат с куратором","Куратор на связи всё обучение","Задавайте вопросы в чате в рабочее время: куратор отвечает по программе, расписанию и документам, а преподаватель — по технике и разбору ваших видео.","lead-operator","Куратор отвечает слушателям"),
            ("Материалы","Методички и конспекты остаются у вас","Все лекции, схемы и методические материалы доступны на платформе и после окончания курса — к ним удобно возвращаться в работе.","course-1","Учебные материалы курса"),
            ("Видео","Видеоуроки с разбором техник","Каждый приём снят крупным планом с нескольких ракурсов: можно пересматривать в замедлении и отрабатывать дома между занятиями.","course-desc","Видеоурок по классическому массажу")]
    live_tabs = '<div class="tabs" role="tablist" aria-label="Форматы обучения">' + "".join(f'<button class="tab{" is-active" if i==0 else ""}" type="button" role="tab" id="live-tab{i}" aria-controls="live-p{i}" aria-selected="{"true" if i==0 else "false"}" tabindex="{0 if i==0 else -1}">{t}</button>' for i,(t,_,_,_,_) in enumerate(live)) + '</div>'
    live_panels = "".join(f'<div class="live" role="tabpanel" id="live-p{i}" aria-labelledby="live-tab{i}"{"" if i==0 else " hidden"}><div class="stack gap-md"><h3 class="t-h2">{h}</h3><p class="t-secondary">{d}</p></div>{img(im, alt, 1052, 802)}</div>' for i,(_,h,d,im,alt) in enumerate(live))
    course_ld = {"@context":"https://schema.org","@type":"Course","name":"Курс классического массажа с нуля","description":"Курс классического массажа для начинающих без медицинского образования: 72 академических часа, 80% практики, удостоверение о повышении квалификации.",
                 "provider":{"@type":"EducationalOrganization","name":"МЦПО","sameAs":SITE},"offers":{"@type":"Offer","price":"16900","priceCurrency":"RUB","category":"Paid"},
                 "hasCourseInstance":[{"@type":"CourseInstance","courseMode":"Blended","startDate":"2026-10-19","location":{"@type":"Place","name":"МЦПО","address":ADDR}}]}
    body = f'''
    <section class="container intro" data-sticky-trigger>
      {breadcrumbs(cr)}
      <div class="course-hero">
        {img("course-hero","",1380,545,lazy=False)}
        <div class="course-hero__copy hero-in">
          <div class="row gap-xs wrap"><span class="badge badge--photo">без мед. образования</span><span class="badge badge--photo">72 ак. ч.</span></div>
          <h1>Курс классического массажа с нуля в Москве</h1>
          <ul class="bullets"><li>Медицинское образование не требуется</li><li>80% занятий — практика на моделях</li><li>Сертификат и удостоверение о повышении квалификации</li></ul>
          <div class="row gap-md wrap course-hero__actions"><a class="btn btn--primary" href="#start">Выбрать дату старта</a><a class="btn btn--outline-inverse" href="#program">Программа курса{icon("arrow-up-right")}</a></div>
        </div>
        <form class="course-hero__form" data-lead novalidate>
          <h2 class="t-h3">Поможем выбрать формат и дату</h2>
          <p class="t-body-s t-muted">Перезвоним за 15 минут в рабочее время</p>
          {field("text","name","Имя*",surface=True)}
          {field("tel","phone",surface=True)}
          {consent()}
          <button class="btn btn--primary btn--block" type="submit">Получить консультацию</button>
        </form>
      </div>
      <p class="price-line"><span class="t-h2">от 16 900 ₽</span><span class="t-body-s t-muted t-strike">21 000 ₽</span></p>
      <div class="grid grid-3" data-stagger>
        <article class="feature reveal"><h3 class="feature__title">Материалы остаются навсегда</h3><p class="feature__text">Лекции и видео доступны на платформе и после окончания курса</p></article>
        <article class="feature reveal"><h3 class="feature__title">Удостоверение в ФИС ФРДО</h3><p class="feature__text">Документ установленного образца — проверяется работодателем онлайн</p></article>
        <article class="feature reveal"><h3 class="feature__title">Учитесь с телефона</h3><p class="feature__text">Теория и тесты — в приложении, практика — в учебном кабинете</p></article>
      </div>
    </section>

    <section class="container" id="start" aria-labelledby="start-title">
      <div class="schedule-card reveal">
        <div class="section-head section-head--center"><h2 class="section-head__title" id="start-title">Ближайшие даты старта группы</h2><p class="section-head__lead">Очная группа в Москве — до 12 человек</p></div>
        <table class="schedule-table"><thead><tr><th scope="col">Дата</th><th scope="col">Дни</th><th scope="col">Время</th><th scope="col">Стоимость</th><th><span class="visually-hidden">Запись</span></th></tr></thead><tbody>{rows_html}</tbody></table>
      </div>
    </section>

    <section class="container" aria-labelledby="desc-title">
      <div class="desc reveal">
        <div class="stack gap-lg"><h2 id="desc-title">Описание курса</h2><p>Курс классического массажа подходит тем, кто начинает с нуля. Вы изучите анатомию и физиологию, освоите приёмы гигиенического (общеукрепляющего) массажа тела и отработаете их на моделях под контролем преподавателя.</p><p>Классический массаж — базовый модуль для курсов медицинского, детского массажа и ЛФК: после него можно продолжить обучение по более сложным техникам.</p></div>
        {img("course-desc","Преподаватель проводит массаж на занятии",1060,836)}
      </div>
    </section>

    <section class="section container" id="program" aria-labelledby="program-title" data-stagger>
      {section_head("Программа курса по модулям","72 академических часа: теория онлайн, практика — в учебном кабинете").replace('class="section-head__title"','class="section-head__title" id="program-title"')}
      <div class="stack gap-md">{mods_html}</div>
    </section>

    <section class="container" aria-labelledby="cdocs-title">
      <div class="docs docs--course reveal">
        <div class="stack gap-lg"><h2 id="cdocs-title">Документы после курса</h2><p class="t-secondary">Удостоверение о повышении квалификации установленного образца — сведения вносим в ФИС ФРДО. Дополнительно выдаём сертификат МЦПО о прохождении практики.</p><a class="link t-body-s" href="#">Обучаем по государственной лицензии {LICENSE}</a></div>
        <div class="docs__diploma">{img("diploma","Диплом МЦПО",1074,680)}</div>
      </div>
    </section>

    <section class="container" aria-labelledby="salary-title">
      <div class="salary reveal">
        <div class="salary__bars">
          <h2 id="salary-title">Доход растёт вместе с навыками</h2>
          <div class="salary__track"><div class="salary__bar" style="--w:45%"><b class="t-h3">60 000 ₽</b><small>Начинающий массажист</small></div></div>
          <div class="salary__track"><div class="salary__bar" style="--w:65%"><b class="t-h3">100 000 ₽</b><small>Массажист с опытом 1–2 года</small></div></div>
          <div class="salary__track"><div class="salary__bar" style="--w:90%"><b class="t-h3">180 000 ₽</b><small>Медицинский массажист, частная практика</small></div></div>
          <p class="t-caption" style="opacity:.5">Источник: вакансии hh.ru, Москва, 2026</p>
        </div>
        {img("salary","Специалист по аппаратной косметологии",780,598)}
      </div>
    </section>

{reviews_block("Отзывы выпускников курса")}

    <section class="section container" aria-labelledby="live-title">
      <div class="section-head section-head--center reveal"><h2 class="section-head__title" id="live-title">Живая практика + видеоуроки</h2></div>
      <div class="row" style="justify-content:center">{live_tabs}</div>
      <div class="live-panels">{live_panels}</div>
    </section>

    <section class="section container" aria-labelledby="partners-title">
      {section_head("Выпускники работают в ведущих клиниках и центрах","Среди работодателей наших выпускников:").replace('class="section-head__title"','class="section-head__title" id="partners-title"')}
      <div class="logos reveal">{logos}</div>
      <div class="cta reveal"><p class="cta__text"><span class="t-hl" data-count="350000" data-suffix="+">350 000+</span> специалистов уже повысили квалификацию в МЦПО. Следующий — вы</p><a class="btn btn--primary" href="#start">Подобрать дату</a></div>
    </section>

{why_block()}
{lead_block()}
{faq_html}
{map_block()}
{teachers_block()}
'''
    sticky = f'<div class="sticky-cta" aria-hidden="false"><div><p class="t-h4">от 16 900 ₽</p><p class="t-caption t-muted">старт 19 октября</p></div><a class="btn btn--primary" href="#lead">Записаться</a></div>'
    return page("course-classic-massage.html","Курс классического массажа с нуля в Москве — 72 часа, удостоверение | МЦПО",
                "Курс классического массажа для начинающих без медицинского образования: 72 ак. часа, 80% практики на моделях, удостоверение в ФИС ФРДО. Старт 19 октября, от 16 900 ₽.",
                body, "", [course_ld, faq_ld], cr, sticky)

def intro(cr, h1, lead=None):
    l = f'<p class="intro__lead">{lead}</p>' if lead else ""
    return f'{breadcrumbs(cr)}<h1>{h1}</h1>{l}'

def schedule():
    cr = [("Главная","index.html"),("Расписание","schedule.html")]
    names = ["Медицинский массаж: повышение квалификации, 144 ч","Медицинский массаж: первичная специализация, 288 ч","Классический массаж с нуля","Детский массаж","Лимфодренажный массаж","Антицеллюлитный массаж","Спортивный массаж","Массаж лица"]
    lst = "".join(f'<a href="{"#c" + str(i) if i < 2 else "#"}"{A_CUR_TRUE if i==0 else ""}>{n}</a>' for i,n in enumerate(names))
    dir_options = "".join(f'<option value="{fid}">{fname}</option>' for fid, fname, _i, _d in CATALOG)
    def card(i, title, hrs):
        rows = [("19 октября 2026","Пн, Ср, Пт",True),("26 октября 2026","Вт, Чт",False),("31 октября 2026","Сб, Вс",False)]
        r = "".join(f'<tr{CLS_SOON if s else ""}><td data-label="Дата">{d}</td><td data-label="Дни">{dy}</td><td data-label="Время">09:00–15:00</td><td data-label="Стоимость">38 700 ₽</td><td><a class="btn btn--primary" href="#lead">Записаться</a></td></tr>' for d,dy,s in rows)
        return f'''<article class="sched-course reveal" id="c{i}">
          <div class="sched-course__head"><h2>{title}</h2><span class="badge badge--outline">{hrs}</span></div>
          {tabs(["Октябрь","Ноябрь","Декабрь"],0,"Месяц")}
          <table class="schedule-table"><thead><tr><th scope="col">Дата</th><th scope="col">Дни</th><th scope="col">Время</th><th scope="col">Стоимость</th><th><span class="visually-hidden">Запись</span></th></tr></thead><tbody>{r}</tbody></table>
          <button class="link t-body-s" type="button" style="align-self:center">Показать ещё даты</button>
        </article>'''
    body = f'''
    <section class="container intro">
      {intro(cr,"Расписание курсов и ближайшие даты старта групп","Выберите направление и формат — покажем группы с набором на ближайшие 3 месяца.")}
      <form class="filter-bar" aria-label="Фильтр расписания" onsubmit="return false">
        <label><span>Направление</span><span class="select"><select class="select__native" data-filter-direction><option value="">Все направления</option>{dir_options}</select></span></label>
        <label><span>Форма обучения</span><span class="select"><select class="select__native"><option>Очно</option><option>Онлайн</option></select></span></label>
        <label><span>Дни</span><span class="select"><select class="select__native"><option>Пн, Ср, Пт</option><option>Вт, Чт</option><option>Сб, Вс</option></select></span></label>
        <label><span>Стоимость, ₽</span><span class="range"><input type="number" placeholder="от" aria-label="от"><input type="number" placeholder="до" aria-label="до"></span></label>
        <div class="filter-bar__actions"><button class="btn btn--primary btn--m" type="submit">Показать группы</button><button type="reset">Сбросить фильтры</button></div>
      </form>
      <div class="sched-layout">
        <nav class="course-list" aria-label="Курсы">{lst}</nav>
        <div class="stack gap-2xl">{card(0,"Медицинский массаж: повышение квалификации с сертификатом","144 ак. ч.")}{card(1,"Медицинский массаж: первичная специализация","288 ак. ч.")}</div>
      </div>
    </section>
'''
    return page("schedule.html","Расписание курсов массажа и повышения квалификации в Москве — МЦПО",
                "Ближайшие даты старта групп: медицинский и классический массаж, косметология, курсы для врачей. Очно в Москве и онлайн. Запись онлайн.",
                body, "Расписание", [], cr)

def events():
    cr = [("Главная","index.html"),("Мероприятия","events.html")]
    ev = [("Мастер-класс по массажу лица","24 октября, 18:00","course-1","2026-10-24T18:00"),("Вебинар: как подготовиться к периодической аккредитации","29 октября, 19:00","tile-cosm","2026-10-29T19:00"),("Открытый урок по инъекционной косметологии","2 ноября, 12:00","dir-cosm","2026-11-02T12:00"),("Мастер-класс: лимфодренажный массаж","7 ноября, 18:00","dir-massage","2026-11-07T18:00"),("Вебинар: как набрать баллы НМО за год","12 ноября, 19:00","tile-accred","2026-11-12T19:00"),("День карьеры для массажистов","16 ноября, 15:00","jobs-girl","2026-11-16T15:00")]
    cards = "".join(f'<article class="event reveal"><div class="event__media media-zoom" data-popup="lead">{img(i,t,880,540)}</div><h2 class="event__title">{t}</h2><time class="event__date" datetime="{dt}">{icon("calendar")}{d}</time><a class="btn btn--primary btn--m" href="#lead">Записаться бесплатно</a></article>' for t,d,i,dt in ev)
    lds = [{"@context":"https://schema.org","@type":"Event","name":t,"startDate":dt,"eventAttendanceMode":"https://schema.org/MixedEventAttendanceMode","isAccessibleForFree":True,"location":{"@type":"Place","name":"МЦПО","address":ADDR},"organizer":{"@type":"Organization","name":"МЦПО","url":SITE}} for t,d,i,dt in ev]
    body = f'''
    <section class="container intro">
      {intro(cr,"Мероприятия и дни открытых дверей","Бесплатные мастер-классы, вебинары и открытые уроки — познакомьтесь с преподавателями до начала обучения.")}
      <div class="events-grid" data-stagger>
        <article class="event event--featured reveal">
          <div><p class="t-h2 event__countdown">Осталось 2 дня</p><p class="t-body-m" style="opacity:.6">Количество мест ограничено — 20 человек</p></div>
          <div class="event__row"><span class="media-zoom" data-popup="lead">{img("event-group","Слушатели на дне открытых дверей МЦПО",580,480)}</span><div class="stack gap-md"><h2>День открытых дверей МЦПО</h2><time class="t-body-l" datetime="2026-10-28T19:00">28 октября, 19:00 · Кузнецкий Мост</time><a class="btn btn--primary" href="#lead" style="margin-top:auto">Записаться</a></div></div>
        </article>
        {cards}
      </div>
    </section>
    <section class="container"><div class="cta reveal"><p class="cta__text">Не пропустите следующее мероприятие — пришлём приглашение в <span class="t-hl">Telegram</span></p><a class="btn btn--primary" href="#">Подписаться</a></div></section>
'''
    return page("events.html","Мероприятия МЦПО: бесплатные мастер-классы, вебинары и дни открытых дверей",
                "Бесплатные мастер-классы по массажу и косметологии, вебинары об аккредитации и баллах НМО, дни открытых дверей в Москве. Запись онлайн.",
                body, "Мероприятия", lds, cr)

def teachers_page():
    cr = [("Главная","index.html"),("Преподаватели","teachers.html")]
    def grid(n): return "".join(teacher_card(*TEACHERS[i % len(TEACHERS)], cls="teacher reveal") for i in range(n))
    person_ld = {"@context":"https://schema.org","@type":"Person","name":"Шепелев Владимир Иванович","jobTitle":"Врач-педиатр, массажист, преподаватель МЦПО","worksFor":{"@type":"EducationalOrganization","name":"МЦПО"}}
    body = f'''
    <section class="container intro">
      {intro(cr,"Преподаватели МЦПО — практикующие врачи и эксперты","Каждый преподаватель ведёт клиническую или частную практику: на занятиях вы разбираете реальные случаи, а не только теорию.")}
      <section class="teacher-group" aria-labelledby="g1"><h2 id="g1">Массаж и реабилитация</h2><div class="teachers-grid" data-stagger>{grid(8)}</div></section>
      <section class="teacher-group" aria-labelledby="g2"><h2 id="g2">Косметология</h2><div class="teachers-grid" data-stagger>{grid(4)}</div></section>
    </section>
'''
    return page("teachers.html","Преподаватели МЦПО — практикующие врачи, массажисты и косметологи",
                "Преподаватели МЦПО: практикующие врачи, массажисты и косметологи со стажем от 10 лет. Специальности, опыт и курсы, которые ведут.",
                body, "О центре", [person_ld], cr)

def contacts():
    cr = [("Главная","index.html"),("Контакты","contacts.html")]
    body = f'''
    <section class="container intro">
      {intro(cr,"Контакты учебного центра МЦПО в Москве","Приходите на консультацию или звоните — подберём курс под вашу специальность.")}
    </section>
{map_block("Адреса и график","h2","map-section--tight")}
    <section class="container">
      <div class="details" data-stagger>
        <article class="feature reveal"><h2 class="feature__title">Телефон и почта</h2><p><a class="t-nums" href="{PHONE_HREF}">{PHONE}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p></article>
        <article class="feature reveal"><h2 class="feature__title">Режим работы</h2><p>Пн–Пт: 9:00–20:00<br>Сб–Вс: 10:00–16:00<br>Онлайн-заявки — круглосуточно</p></article>
        <article class="feature reveal"><h2 class="feature__title">Реквизиты</h2><p class="t-body-s">{ORG_LEGAL} — {ORG_BRAND}<br>Лицензия на образовательную деятельность {LICENSE_FULL}<br>ИНН {INN} · ОГРН {OGRN}</p></article>
      </div>
    </section>
{lead_block()}
'''
    return page("contacts.html","Контакты МЦПО: адрес у м. Кузнецкий Мост, телефон, график работы",
                f"МЦПО у м. Кузнецкий Мост: ул. Кузнецкий Мост, 21/5. Телефон {PHONE}, Пн–Пт 9:00–20:00, Сб–Вс 10:00–16:00. Реквизиты и лицензия.",
                body, "Контакты", [], cr)

def cart():
    cr = [("Главная","index.html"),("Корзина","cart.html")]
    items = [("Медицинский массаж: повышение квалификации, 144 ч","Онлайн · старт 10 ноября",19100,"course-1"),("Лимфодренажный массаж","Очно · старт 7 ноября",9500,"dir-massage")]
    def fmt(n): return f"{n:,}".replace(",", "\u00a0") + "\u00a0₽"
    it = "".join(f'''<article class="cart-item reveal" data-cart-item data-price="{p}">
        <div class="cart-item__media">{img(i,t,880,540)}</div>
        <div class="cart-item__info">
          <div class="row gap-xs wrap cart-item__badges"><span class="badge badge--edu">с мед. образованием</span><span class="badge badge--nmo">36 баллов НМО</span></div>
          <h2 class="t-h3">{t}</h2><p class="t-secondary">{m}</p>
        </div>
        <div class="cart-item__bottom">
          <p class="cart-item__price"><span class="t-secondary">К оплате:</span><span class="t-h2 t-nums">{fmt(p)}</span></p>
          <a class="btn btn--primary" href="checkout-1.html">Оформить</a>
        </div>
        <button class="icon-btn icon-btn--sm icon-btn--white cart-item__remove" type="button" data-cart-remove aria-label="Удалить курс из корзины">{icon("close","icon icon--sm")}</button>
      </article>''' for t,m,p,i in items)
    body = f'''
    <section class="container intro">
      {intro(cr,"Корзина")}
      <div class="stack gap-lg">{it}</div>
      <p class="t-body-m t-secondary" data-cart-empty hidden>Корзина пуста. <a class="link" href="faculty-massage.html">Перейти в каталог</a></p>
      <p class="t-body-s t-muted">Вернём 13% через налоговый вычет — справку выдаём бесплатно</p>
    </section>
'''
    # Общей оплаты нескольких курсов нет: каждый курс оформляется отдельно своей кнопкой,
    # поэтому ни итоговой плашки «N курсов на сумму», ни нижней панели на мобильном
    return page("cart.html","Корзина — МЦПО","Выбранные курсы МЦПО: оформление заявки и оплата.", body, "", [], cr)

def checkout(step):
    cr = [("Главная","index.html"),("Корзина","cart.html"),("Оформление заявки",f"checkout-{step}.html")]
    steps = "".join(f'<li{CLS_DONE if i<step-1 else ""}{A_CUR_STEP if i==step-1 else ""}>{t}</li>' for i,t in enumerate(["Формат и дата","Контакты","Оплата"]))
    if step == 1:
        inner = f'''<h1>Какой формат вам подходит?</h1>
          <p class="t-body-l t-secondary">Выберите форму обучения</p>
          <div class="format-options" role="radiogroup" aria-label="Форма обучения">
            <label class="format-option"><input type="radio" name="format" checked><span class="format-option__name">Онлайн</span><span class="t-caption t-muted t-strike">9 600 ₽</span><span class="t-h3 t-nums">7 600 ₽</span></label>
            <label class="format-option"><input type="radio" name="format"><span class="format-option__name">Очно в Москве</span><span class="t-caption t-muted t-strike">24 000 ₽</span><span class="t-h3 t-nums">19 100 ₽</span></label>
          </div>
          <ul class="bullets t-secondary"><li>Верните 13% стоимости через налоговый вычет — справку выдаём бесплатно</li><li>Скидка 15% при полной оплате на сайте</li><li>Рассрочка — условия уточнит методист</li></ul>
          <a class="btn btn--outline btn--m checkout__next" href="checkout-2.html">Далее{icon("chevron-right")}</a>'''
        sticky_label, sticky_href = "Далее", "checkout-2.html"
    else:
        inner = f'''<h1>Как с вами связаться?</h1>
          <p class="t-body-l t-secondary">Заполните поля — пришлём договор и ссылку на оплату</p>
          <form class="checkout__form" data-lead novalidate id="checkout-form">
            {field("text","fio","ФИО полностью (для документа)*")}
            {field("tel","phone")}
            {field("text","email","Email",False)}
            <fieldset style="border:0;padding:0;margin:0" class="stack gap-sm"><legend class="t-h4" style="margin-bottom:12px">Есть ли у вас медицинское образование?</legend>
              <div class="choice-row"><label><input type="radio" name="edu"><span>Высшее</span></label><label><input type="radio" name="edu" checked><span>Среднее</span></label><label><input type="radio" name="edu"><span>Нет</span></label></div>
            </fieldset>
            {consent()}
            <button class="btn btn--outline btn--m checkout__next" type="submit">Далее{icon("chevron-right")}</button>
          </form>'''
        sticky_label, sticky_href = "Перейти к оплате", "#checkout-form"
    body = f'''
    <section class="container intro">
      {breadcrumbs(cr)}
      <div class="checkout">
        <div class="checkout__step">
          <ol class="stepper" aria-label="Шаги оформления">{steps}</ol>
          <div class="checkout__mini"><p class="t-body-s t-medium">Медицинский массаж: повышение квалификации, 144 ч</p><p class="t-caption t-muted">Онлайн · старт 10 ноября · 7 600 ₽</p></div>
          {inner}
        </div>
        <aside class="checkout__side" aria-label="Ваш заказ">
          <div class="summary">
            <div class="summary__media">{img("group-practice","",1052,802)}</div>
            <h2 class="t-h3">Медицинский массаж: повышение квалификации, 144 ч</h2>
            <div class="summary__meta"><div><p class="t-caption t-muted">Формат</p><p class="t-medium">Онлайн</p></div><div><p class="t-caption t-muted">Старт</p><p class="t-medium">10 ноября</p></div></div>
            <p class="row gap-sm" style="align-items:baseline"><span class="t-secondary">Итого:</span><span class="t-h2 t-nums">7 600 ₽</span></p>
            <button class="link t-body-s" type="button" style="align-self:flex-start">Есть промокод?</button>
            <p class="t-caption t-muted">Вернём 13% через налоговый вычет — справку выдаём бесплатно</p>
          </div>
          <a class="btn btn--primary btn--block" href="#">Оплатить 7 600 ₽</a>
          <p class="t-caption t-muted">Оплата картой МИР, Visa, Mastercard или по счёту для организаций. Договор-оферта отправляется на email.</p>
        </aside>
      </div>
    </section>
'''
    sticky = f'<div class="sticky-cta sticky-cta--always"><div><p class="t-h4">7 600 ₽</p><p class="t-caption t-muted">Онлайн</p></div><a class="btn btn--primary" href="{sticky_href}">{sticky_label}</a></div>'
    return page(f"checkout-{step}.html", f"Оформление заявки — шаг {step} из 3 | МЦПО", "Оформление заявки на курс МЦПО.", body, "", [], cr, sticky)

# ======================= Курсы для врачей =======================

DOCTORS_FAQ = [
 ("Засчитываются ли баллы НМО за обучение?",
  "Часть программ идёт со свидетельством НМО — это указано в карточке курса. Сколько зачётных единиц даёт конкретная программа, методист назовёт при записи."),
 ("Какой документ я получу?",
  "После повышения квалификации — удостоверение о повышении квалификации, после переподготовки от 250 часов — диплом о профессиональной переподготовке. Сведения о выданных документах вносим в ФИС ФРДО, и работодатель может проверить их в реестре."),
 ("Нужно ли приезжать в Москву?",
  "Нет. Программы для врачей проходят дистанционно: лекции и материалы на платформе, итоговое тестирование онлайн. Документ забираете в офисе или получаете почтой."),
 ("Сколько времени занимает обучение?",
  "Зависит от объёма программы: 36, 144 часа или 504 часа при переподготовке. Внутри срока темп задаёте сами — заниматься можно после смены и в выходные."),
 ("Может ли оплатить работодатель?",
  "Да. Заключаем договор с юридическим лицом и выставляем счёт — этим занимается отдел по работе с юридическими лицами."),
 ("Есть ли рассрочка?",
  "Да, оплату можно разбить на части или оформить кредит. За обучение в лицензированном центре вы вправе вернуть 13% стоимости через налоговый вычет."),
]

# Карточки курсов на странице «Курсы для врачей». Их же с ценами показывает поиск в шапке.
DOCTOR_COURSES = [("Кардиология — повышение квалификации, 144 ч","Для врачей-кардиологов и терапевтов · дистанционно","","11 400 ₽",[("edu","высшее медицинское"),("hours","144 ак. ч.")],"dir-med"),
               ("Неврология — повышение квалификации, 144 ч","Для врачей-неврологов · дистанционно","","11 400 ₽",[("edu","высшее медицинское"),("hours","144 ак. ч.")],"tile-med"),
               ("Анестезиология-реаниматология, 144 ч","Для анестезиологов-реаниматологов · дистанционно","","11 400 ₽",[("edu","высшее медицинское"),("hours","144 ак. ч.")],"group-practice"),
               ("Диетология — профессиональная переподготовка, 504 ч","Новая специальность · диплом о переподготовке","","18 300 ₽",[("edu","высшее медицинское"),("hours","504 ак. ч.")],"course-desc"),
               ("Физиотерапия — профессиональная переподготовка, 504 ч","Новая специальность · диплом о переподготовке","","18 300 ₽",[("edu","высшее медицинское"),("hours","504 ак. ч.")],"dir-med"),
               ("Авиационная и космическая медицина, 36 ч","Короткая программа со свидетельством НМО","","4 500 ₽",[("nmo","свидетельство НМО"),("hours","36 ак. ч.")],"tile-med")]

def doctors():
    cr = [("Главная","index.html"),("Курсы для врачей","doctors.html")]
    groups = ["Терапия и общая практика","Неврология и психиатрия","Хирургия","Диагностика","Анестезиология и реанимация","Организация здравоохранения"]
    groups_html = '<div class="tabs tabs--wrap" role="tablist" aria-label="Группы специальностей">' + "".join(f'<button class="tab tab--l{" is-active" if i==0 else ""}" type="button" role="tab" aria-selected="{"true" if i==0 else "false"}" tabindex="{0 if i==0 else -1}">{t}</button>' for i,t in enumerate(groups)) + '</div>'

    courses = DOCTOR_COURSES

    def fgroup(title, opts, checked=()):
        return f'<fieldset class="filter-group"><legend>{title}</legend>' + "".join(f'<label class="check"><input type="checkbox" name="f"{" checked" if i in checked else ""}><span class="check__box"></span><span>{o}</span></label>' for i,o in enumerate(opts)) + '</fieldset>'

    steps = [("num-1","Оставляете заявку","Методист уточняет вашу специальность и действующий сертификат, подбирает программу и присылает договор."),
             ("num-2","Учитесь на платформе","Лекции, материалы и промежуточные тесты доступны круглосуточно. Темп внутри срока задаёте сами."),
             ("num-3","Получаете документ","После итогового тестирования выдаём удостоверение или диплом и вносим сведения в ФИС ФРДО.")]
    steps_html = "".join(f'<article class="whom-card reveal"><div class="whom-card__head">{img(i,"",120,128)}<h3>{t}</h3></div><p class="t-body-s t-muted">{d}</p></article>' for i,t,d in steps)

    faq_html, faq_ld = faq_block("Вопросы врачей об обучении", DOCTORS_FAQ, "docfaq")

    body = f'''
    <section class="container intro">
      {breadcrumbs(cr)}
      <h1>Повышение квалификации врачей дистанционно</h1>
      <p class="intro__lead">Более 50 врачебных специальностей: повышение квалификации от 36 часов и профессиональная переподготовка от 504 часов. Удостоверение или диплом установленного образца, сведения вносим в ФИС ФРДО. Учитесь без отрыва от работы — от 4 500 ₽.</p>
      {groups_html}
      <div class="catalog">
        <aside class="catalog__filters" id="filters" aria-label="Фильтры">
          <div class="filters-head"><h2 class="t-h3">Фильтры</h2><button class="icon-btn icon-btn--sm" type="button" data-close aria-label="Закрыть фильтры">{icon("close","icon icon--sm")}</button></div>
          <fieldset class="filter-group"><legend>Стоимость, ₽</legend><div class="range"><input type="number" inputmode="numeric" placeholder="от 2 500" aria-label="Цена от"><input type="number" inputmode="numeric" placeholder="до 40 000" aria-label="Цена до"></div></fieldset>
          {fgroup("Объём программы",["36 часов","144 часа","250–504 часа","Более 504 часов"],(1,))}
          {fgroup("Документ",["Удостоверение о ПК","Диплом о переподготовке","Свидетельство НМО"],(0,))}
          {fgroup("Формат",["Дистанционно","Очно в Москве","Индивидуально"],(0,))}
          <button class="btn btn--primary btn--m" type="button" data-close>Показать программы</button>
        </aside>
        <div class="catalog__results">
          <div class="catalog__bar"><h2 class="t-h3">Терапия и общая практика</h2><button class="btn btn--outline btn--m catalog__filter-btn" type="button" data-open="filters">{icon("filter","icon icon--sm")}<span>Фильтры (<span data-filter-count>2</span>)</span></button><span class="t-body-s t-muted">Найдено 52 программы</span></div>
          <div class="grid grid-3" data-stagger>{"".join(course_card(*c, btn="Записаться") for c in courses)}</div>
          <div class="row" style="justify-content:center"><button class="btn btn--outline" type="button">Показать ещё 18 курсов</button></div>
        </div>
      </div>
    </section>

    <section class="section container" aria-labelledby="dsteps-title">
      <div class="section-head section-head--center reveal"><h2 class="section-head__title" id="dsteps-title">Как проходит обучение</h2><p class="section-head__lead">Три шага от заявки до документа в реестре</p></div>
      <div class="grid grid-3" data-stagger>{steps_html}</div>
    </section>

    <section class="container" aria-labelledby="ddocs-title">
      <div class="docs reveal">
        <div class="stack gap-lg"><h2 id="ddocs-title">Документы, которые получает врач</h2><p class="t-secondary">По программам повышения квалификации — удостоверение, по переподготовке от 250 часов — диплом о профессиональной переподготовке. Сведения о документе вносим в ФИС ФРДО: работодатель и аккредитационная комиссия проверяют его в федеральном реестре. По отдельным программам выдаём свидетельство НМО.</p><div><a class="btn btn--primary" href="#lead">Подобрать программу</a></div></div>
        <div class="docs__imgs">{img("doc-1","Образец удостоверения о повышении квалификации",462,672)}{img("doc-2","Образец диплома о профессиональной переподготовке",250,350)}{img("doc-3","Образец диплома",462,672)}</div>
      </div>
    </section>

    <section class="section container" aria-labelledby="nmo-title">
      <div class="section-head reveal" style="max-width:56ch"><h2 class="section-head__title" id="nmo-title">Что такое НМО и зачем врачу баллы</h2><p class="section-head__lead">Непрерывное медицинское образование — система, по которой врач подтверждает квалификацию не одним экзаменом раз в пять лет, а регулярным обучением. Часть наших программ идёт со свидетельством НМО и засчитывается в портфолио для периодической аккредитации.</p></div>
      <div class="grid grid-3" data-stagger>
        <article class="feature reveal"><h3 class="feature__title">Обучение вместо экзамена</h3><p class="feature__text">Вместо разового сертификационного цикла вы набираете зачётные единицы в течение всего периода и подаёте портфолио.</p></article>
        <article class="feature reveal"><h3 class="feature__title">Без отрыва от работы</h3><p class="feature__text">Программы дистанционные: материалы и тесты открыты круглосуточно, расписание подстраивается под смены.</p></article>
        <article class="feature reveal"><h3 class="feature__title">Документ в федеральном реестре</h3><p class="feature__text">Удостоверение и диплом попадают в ФИС ФРДО — подтверждать обучение бумажной копией не нужно.</p></article>
      </div>
    </section>

{lead_block("Подберём программу под вашу специальность")}
{faq_html}
{map_block()}
{teachers_block()}
'''
    return page("doctors.html","Повышение квалификации врачей дистанционно — курсы с НМО от 4 500 ₽ | МЦПО",
                "Повышение квалификации и переподготовка для врачей: более 50 специальностей, 36–504 часа, от 4 500 ₽. Свидетельство НМО, удостоверение в ФИС ФРДО. Дистанционно.",
                body, "Аккредитация", [faq_ld], cr)


# ======================= Аккредитация медработников =======================

ACCRED_FAQ = [
 ("По каким специальностям МЦПО проводит аккредитацию?",
  "Аккредитационная площадка МЦПО принимает первичную специализированную аккредитацию по медицинскому массажу и сестринскому делу в косметологии, а также первичную и первичную специализированную аккредитацию по сестринскому делу. По остальным специальностям мы помогаем подготовиться к процедуре."),
 ("Чем первичная аккредитация отличается от первичной специализированной?",
  "Первичную проходят сразу после выпуска из колледжа или вуза по полученной специальности. Первичную специализированную — после профессиональной переподготовки или ординатуры, когда специалист получает допуск к новой специальности."),
 ("Что входит в процедуру аккредитации?",
  "Компьютерное тестирование по теории, оценка практических навыков на симуляционном оборудовании и, где это предусмотрено программой, решение ситуационных задач."),
 ("Что взять с собой на аккредитацию?",
  "Паспорт, СНИЛС и медицинскую форму: халат и шапочку. Маникюр должен быть коротким; если вы пользуетесь очками, возьмите их с собой."),
 ("Когда ближайшее заседание подкомиссии?",
  "График заседаний обновляется по мере формирования групп. Ближайшие даты по вашей специальности и стоимость процедуры назовёт специалист центра — оставьте заявку."),
 ("На основании какого документа проводится аккредитация?",
  "Процедура проводится по Положению об аккредитации специалистов, утверждённому приказом Министерства здравоохранения Российской Федерации № 709н."),
]

def accreditation():
    cr = [("Главная","index.html"),("Аккредитация","accreditation.html")]

    specs = [("Медицинский массаж","Первичная специализированная аккредитация","tile-massage"),
             ("Сестринское дело","Первичная и первичная специализированная аккредитация","tile-med"),
             ("Сестринское дело в косметологии","Первичная специализированная аккредитация","tile-cosm")]
    specs_html = "".join(f'<article class="course-card reveal"><div class="course-card__media media-zoom">{img(i,t,880,540)}</div><div class="course-card__body"><h3 class="course-card__title">{t}</h3><p class="course-card__meta">{d}</p><div class="course-card__actions"><a class="btn btn--primary btn--m" href="#lead">Записаться на аккредитацию</a></div></div></article>' for t,d,i in specs)

    kinds = [("Первичная аккредитация","Проходят выпускники колледжа или вуза сразу после получения диплома — чтобы начать работать по специальности."),
             ("Первичная специализированная","Для тех, кто закончил профессиональную переподготовку или ординатуру и получает допуск к новой специальности."),
             ("Периодическая","Продление допуска к работе раз в пять лет: портфолио с отчётом о работе и зачётными единицами НМО.")]
    kinds_html = "".join(f'<article class="feature reveal"><h3 class="feature__title">{t}</h3><p class="feature__text">{d}</p></article>' for t,d in kinds)

    stages = [("num-1","Тестирование","Компьютерное тестирование по теоретической части — вопросы формируются из единой базы оценочных средств."),
              ("num-2","Практические навыки","Отработка на симуляционном оборудовании: подкомиссия оценивает выполнение по чек-листу."),
              ("num-3","Ситуационные задачи","Третий этап там, где он предусмотрен программой: разбор клинических случаев.")]
    stages_html = "".join(f'<article class="whom-card reveal"><div class="whom-card__head">{img(i,"",120,128)}<h3>{t}</h3></div><p class="t-body-s t-muted">{d}</p></article>' for i,t,d in stages)

    faq_html, faq_ld = faq_block("Вопросы об аккредитации", ACCRED_FAQ, "acfaq")

    body = f'''
    <section class="container intro">
      {breadcrumbs(cr)}
      <h1>Аккредитация медицинских работников в Москве</h1>
      <p class="intro__lead">МЦПО — аккредитационная площадка: мы не только готовим к процедуре, но и проводим её. Заседания подкомиссии проходят на нашем симуляционном оборудовании, по итогам специалист получает допуск к профессиональной деятельности.</p>
    </section>

    <section class="section container" aria-labelledby="specs-title">
      <div class="section-head reveal" style="max-width:60ch"><h2 class="section-head__title" id="specs-title">Специальности, по которым мы проводим аккредитацию</h2><p class="section-head__lead">Это направления, где МЦПО выступает аккредитационной площадкой. По другим специальностям мы готовим к процедуре, но принимает её другая площадка.</p></div>
      <div class="grid grid-3" data-stagger>{specs_html}</div>
    </section>

    <section class="section container" aria-labelledby="kinds-title">
      <div class="section-head section-head--center reveal"><h2 class="section-head__title" id="kinds-title">Какая аккредитация нужна именно вам</h2></div>
      <div class="grid grid-3" data-stagger>{kinds_html}</div>
    </section>

    <section class="section container" aria-labelledby="stages-title">
      <div class="section-head section-head--center reveal"><h2 class="section-head__title" id="stages-title">Как проходит процедура</h2><p class="section-head__lead">Этапы идут последовательно, по Положению об аккредитации специалистов (приказ Минздрава России № 709н)</p></div>
      <div class="grid grid-3" data-stagger>{stages_html}</div>
    </section>

    <section class="container" aria-labelledby="prep-title">
      <div class="docs reveal">
        <div class="stack gap-lg"><h2 id="prep-title">Что взять с собой</h2><ul class="bullets"><li>Паспорт</li><li>СНИЛС</li><li>Медицинский халат и шапочку</li><li>Короткий маникюр</li><li>Очки, если вы ими пользуетесь</li></ul><p class="t-secondary">Приходите заранее: перед началом подкомиссия сверяет документы участников.</p></div>
        <div class="docs__imgs docs__imgs--single">{img("group-practice","Отработка практических навыков на симуляционном оборудовании",900,640)}</div>
      </div>
    </section>

    <section class="section container" aria-labelledby="train-title">
      <div class="section-head reveal" style="max-width:56ch"><h2 class="section-head__title" id="train-title">Подготовка к аккредитации</h2><p class="section-head__lead">Если до процедуры хочется потренироваться — записывайтесь на отработку практических навыков. Занятие идёт на том же оборудовании и по тем же чек-листам, по которым оценивает подкомиссия.</p></div>
      <div class="grid grid-3" data-stagger>
        <article class="feature reveal"><h3 class="feature__title">Те же чек-листы</h3><p class="feature__text">Разбираем критерии, по которым выставляется оценка, и типичные ошибки на практическом этапе.</p></article>
        <article class="feature reveal"><h3 class="feature__title">То же оборудование</h3><p class="feature__text">Симуляционное оборудование площадки — к процедуре вы приходите в знакомую обстановку.</p></article>
        <article class="feature reveal"><h3 class="feature__title">Портфолио и баллы НМО</h3><p class="feature__text">Для периодической аккредитации подскажем, как собрать портфолио и чем добрать недостающие зачётные единицы.</p></article>
      </div>
    </section>

{lead_block("Записаться на аккредитацию")}
{faq_html}
{map_block()}
'''
    return page("accreditation.html","Аккредитация медработников в Москве — аккредитационная площадка МЦПО",
                "Аккредитационная площадка МЦПО: первичная и первичная специализированная аккредитация по медицинскому массажу и сестринскому делу. Этапы, что взять с собой, подготовка.",
                body, "Аккредитация", [faq_ld], cr)


# ======================= Страница преподавателя =======================

# Курсы, которые ведёт преподаватель: (id, название, часы)
SELYAVIN_COURSES = [
    ("Медицинский массаж: повышение квалификации", "144 ак. ч."),
    ("Медицинский массаж: первичная специализация", "288 ак. ч."),
    ("Классический массаж с нуля", "72 ак. ч."),
    ("Детский массаж", "144 ак. ч."),
    ("Лимфодренажный массаж", "24 ак. ч."),
    ("Спортивный массаж", "36 ак. ч."),
    ("Массаж при заболеваниях позвоночника", "36 ак. ч."),
    ("Антицеллюлитный массаж", "8 ак. ч."),
]


def teacher_profile():
    cr = [("Главная", "index.html"), ("Преподаватели", "teachers.html"), ("Селявин Михаил Юрьевич", "teacher-selyavin.html")]

    badges = ["10 лет преподавания", "медицинский массажист", "среднее медицинское образование"]
    badges_html = "".join(f'<span class="badge badge--outline">{b}</span>' for b in badges)

    education = ["Среднее специальное медицинское образование, 1996 г.",
                 "Высшее психолого-педагогическое образование, 2016 г."]
    upskill = ["Психолого-педагогическое образование, 2016 г., бакалавр",
               "Свидетельство по массажу, 31.03.1994",
               "Сертификат «Медицинский массаж», 2020 г.",
               "Удостоверение о повышении квалификации «Медицинский массаж», 2020 г.",
               "Удостоверение о повышении квалификации «Организация и проведение практического обучения в средних медицинских образовательных организациях с использованием стандартов WorldSkills Russia», 24 ч., 2017 г."]
    ul = lambda items: '<ul class="bullets">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"

    # Левый столбец — список курсов преподавателя, активный подсвечен
    lst = "".join(
        f'<a href="{"#c" + str(i) if i < 2 else "#"}"{A_CUR_TRUE if i == 0 else ""}>{n}</a>'
        for i, (n, h) in enumerate(SELYAVIN_COURSES))

    def card(i, title, hrs):
        rows = [("19 октября 2026", "Пн, Ср, Пт", True), ("26 октября 2026", "Вт, Чт", False), ("31 октября 2026", "Сб, Вс", False)]
        r = "".join(
            f'<tr{CLS_SOON if s else ""}><td data-label="Дата">{d}</td><td data-label="Дни">{dy}</td>'
            f'<td data-label="Время">09:00–15:00</td><td data-label="Стоимость">38 700 ₽</td>'
            f'<td><a class="btn btn--primary" href="#lead">Записаться</a></td></tr>' for d, dy, s in rows)
        return f'''<article class="sched-course reveal" id="c{i}">
          <div class="sched-course__head"><h3>{title}</h3><span class="badge badge--outline">{hrs}</span></div>
          {tabs(["Октябрь","Ноябрь","Декабрь"],0,"Месяц")}
          <table class="schedule-table"><thead><tr><th scope="col">Дата</th><th scope="col">Дни</th><th scope="col">Время</th><th scope="col">Стоимость</th><th><span class="visually-hidden">Запись</span></th></tr></thead><tbody>{r}</tbody></table>
          <button class="link t-body-s" type="button" style="align-self:center">Показать ещё даты</button>
        </article>'''

    person_ld = {
        "@context": "https://schema.org", "@type": "Person",
        "name": "Селявин Михаил Юрьевич",
        "jobTitle": "Преподаватель медицинского массажа",
        "description": "Медицинский массажист, преподаватель МЦПО. Среднее специальное медицинское образование, высшее психолого-педагогическое образование. Стаж преподавания 10 лет.",
        "worksFor": {"@type": "EducationalOrganization", "name": ORG_BRAND + " (МЦПО)", "url": SITE},
        "knowsAbout": ["Медицинский массаж", "Классический массаж", "Детский массаж", "Лечебная физкультура"],
    }

    body = f'''
    <section class="container intro">
      {breadcrumbs(cr)}
      <div class="person">
        <div class="person__photo">
          {img("star-3d","",600,586,"person__star")}
          {img("teacher","Селявин Михаил Юрьевич — преподаватель медицинского массажа",600,720,"person__img",False)}
        </div>
        <div class="person__card">
          <div class="stack gap-md">
            <div class="person__badges">{badges_html}</div>
            <h1>Селявин Михаил Юрьевич</h1>
          </div>
          <div class="person__block">
            <h2 class="person__subtitle">Образование</h2>
            {ul(education)}
          </div>
          <div class="person__block">
            <h2 class="person__subtitle">Повышения квалификации</h2>
            {ul(upskill)}
          </div>
          <button class="link t-body-s person__more" type="button">Читать полностью</button>
        </div>
      </div>
    </section>

    <section class="section container" aria-labelledby="tsched-title">
      <div class="section-head reveal"><h2 class="section-head__title" id="tsched-title">Расписание курсов с этим преподавателем</h2><p class="section-head__lead">Понравился преподаватель? Запишитесь к нему на курс и проверьте его в деле.</p></div>
      <div class="sched-layout">
        <nav class="course-list" aria-label="Курсы преподавателя">{lst}</nav>
        <div class="stack gap-2xl">{card(0, SELYAVIN_COURSES[0][0], SELYAVIN_COURSES[0][1])}{card(1, SELYAVIN_COURSES[1][0], SELYAVIN_COURSES[1][1])}</div>
      </div>
    </section>

{lead_block("Записаться к преподавателю")}
{map_block()}
'''
    return page("teacher-selyavin.html",
                "Селявин Михаил Юрьевич — преподаватель медицинского массажа в МЦПО",
                "Селявин Михаил Юрьевич: медицинский массажист, 10 лет преподавания, среднее специальное медицинское образование. Курсы, которые он ведёт, и ближайшие даты старта.",
                body, "О центре", [person_ld], cr)

# ======================= Акции =======================

# (заголовок, описание, картинка-баннер, когда заканчивается)
PROMOS = [
    ("Бесплатный пробный урок",
     "Приходите на открытое занятие: посмотрите, как устроена практика, и познакомьтесь с преподавателем до оплаты.",
     "event-group", "2026-10-31T23:59"),
    ("Скидка до 25% на курсы с осенним стартом",
     "Действует на очные группы, которые стартуют до конца ноября. Складывается с рассрочкой.",
     "course-1", "2026-09-30T23:59"),
    ("Скидки до 35% постоянным слушателям",
     "Чем больше курсов вы у нас прошли, тем выгоднее следующий. Размер скидки назовёт методист при записи.",
     "group-practice", "2026-12-31T23:59"),
    ("«Вложись в будущее»",
     "Оплатите обучение заранее — цена фиксируется на весь курс, даже если стоимость программы вырастет.",
     "dir-cosm", "2026-11-30T23:59"),
]


def promotions():
    cr = [("Главная", "index.html"), ("Акции", "promotions.html")]

    def card(title, text, pic, end):
        return f'''<article class="promo-card reveal">
          <div class="promo-card__media media-zoom" data-popup="lead">{img(pic, title, 880, 328)}</div>
          <div class="promo-card__body">
            <div class="stack gap-sm">
              <h2 class="promo-card__title">{title}</h2>
              <p class="promo-card__text">{text}</p>
            </div>
            <div class="promo-card__timer">
              <span class="promo-card__label">До конца акции:</span>
              <time class="promo-card__left t-nums" datetime="{end}" data-countdown="{end}">…</time>
            </div>
            <a class="btn btn--primary btn--block" href="#lead">Подробнее</a>
          </div>
        </article>'''

    cards = "".join(card(*p) for p in PROMOS)
    faq_html, faq_ld = faq_block("Вопросы об акциях", PROMO_FAQ, "promofaq")

    body = f'''
    <section class="container intro">
      {intro(cr,"Акции и скидки на обучение","Действующие предложения МЦПО: бесплатные пробные занятия, скидки на очные группы и условия для постоянных слушателей.")}
      <div class="promos" data-stagger>{cards}</div>
    </section>

{lead_block("Не нашли подходящую акцию?")}
{faq_html}
{map_block()}
'''
    return page("promotions.html",
                "Акции и скидки на курсы МЦПО — действующие предложения",
                "Действующие акции МЦПО: бесплатный пробный урок, скидка до 25% на осенние группы, скидки до 35% постоянным слушателям. Сроки и условия.",
                body, "Акции", [faq_ld], cr)


PROMO_FAQ = [
    ("Можно ли объединить несколько акций?",
     "Скидки по акциям не складываются между собой — применяется та, что выгоднее для вас. А вот с рассрочкой и налоговым вычетом 13% акция совмещается."),
    ("Как получить скидку?",
     "Скажите методисту, какая акция вас интересует, при записи на курс. Скидка учитывается в договоре — задним числом пересчитать её не получится."),
    ("Что будет, если акция закончится во время обучения?",
     "Ничего: условия фиксируются в договоре на момент оплаты. Срок акции важен только на день записи."),
    ("Действуют ли акции на дистанционные программы?",
     "Зависит от акции — это указано в её условиях. Бесплатный пробный урок проводится очно, скидки на осенние группы касаются очного обучения."),
]

# ======================= О нас =======================

# Описание под каждой цифрой в макете одинаковое — это рыба, ждём реальные тексты
ABOUT_LOREM = ("МЦПО приглашает пройти курсы массажа с нуля всех, кто желает овладеть приемами "
               "и техниками классического гигиенического (общеукрепляющего) массажа тела.")

ABOUT_NUMBERS = [("1994 - 2026", "star-3d"), ("400 000+", "quiz-3d"),
                 ("500+", "course-3d"), ("100+", "check-3d")]

ABOUT_USEFUL = [("35 000+", "партнеров медицинских и реабилитационных учреждений"),
                ("3 000+", "партнеров медицинских и реабилитационных учреждений"),
                ("3 000+", "партнеров медицинских и реабилитационных учреждений")]

# Логотипы партнёров — 18 штук, порядок как в макете
ABOUT_PARTNERS = [
    ("partner-ifr", "Институт физической реабилитации", 387, 200),
    ("partner-genevie", "Genevie", 704, 363),
    ("partner-avam", "Ассоциация врачей авиационной медицины", 377, 200),
    ("partner-vmeste", "Вместе с мамой", 387, 200),
    ("partner-megapolis", "Мегаполис Эстетик", 387, 200),
    ("partner-abv", "АБВ", 387, 200),
    ("partner-cosmosuits", "Cosmosuits", 387, 200),
    ("partner-1touch", "1-Touch и Spatouch Professional", 387, 200),
    ("partner-ravetape", "Rave Tape", 387, 200),
    ("partner-flow", "Flow", 387, 200),
    ("partner-volga", "Санаторий «Волжский Утёс»", 387, 200),
    ("partner-mechta", "Мечта Бьюти", 387, 200),
    ("partner-medicina", "Медицина", 285, 200),
    ("partner-kdl", "KDL клинико-диагностические лаборатории", 616, 409),
    ("partner-cmd", "CMD Центр молекулярной диагностики", 962, 200),
    ("partner-remedy", "Remedy Lab", 387, 200),
    ("partner-armed", "Армед", 387, 200),
    ("partner-rhana", "Rhana", 387, 200),
]

# Карточка преподавателя в макете продублирована пять раз — данные нужны реальные.
# Фото — из макета 1313-4432 (в teacher.webp другой человек, Селявин)
ABOUT_TUTORS = [("Шепелев Владимир Иванович", "Массажист", "10 лет",
                 "Московский медицинский фармацевтический колледж, «Фармацевт» — 2017 год", "tutor-shepelev")] * 5

# Плитки галереи: буква — место в сетке из макета (c и f высокие, j широкая)
ABOUT_GALLERY = [("a", "group-practice"), ("b", "course-1"), ("c", "teacher"),
                 ("d", "event-group"), ("e", "course-desc"), ("f", "expert"),
                 ("g", "persp-1"), ("h", "persp-2"), ("i", "persp-4"),
                 ("j", "course-hero"), ("k", "persp-3")]

# Документы — сканы из макета «О нас» (блок «Лицензии и документы»): имя, alt, ширина, высота
ABOUT_DOCS = [("doc-license", "Лицензия на образовательную деятельность № 036718 от 2 ноября 2015 г.", 500, 688),
              ("doc-register", "Выписка из реестра лицензий Департамента образования и науки Москвы", 509, 720),
              ("doc-license-annex", "Приложение № 1.1 к лицензии № 036718", 500, 688),
              ("doc-trademark", "Свидетельство на товарный знак МЦПО № 636478", 520, 720)]


def jobs_wall(btn):
    """«Помощь с трудоустройством»: 18 логотипов работодателей. Общий блок «О нас» и «Трудоустройства»,
    кнопка у каждой страницы своя."""
    logos = "".join(img(n, a, w, h) for n, a, w, h in ABOUT_PARTNERS)
    return f'''<section class="section container" aria-labelledby="jobs-title">
      <div class="jobs-head">
        <div class="stack gap-sm">
          <h2 id="jobs-title">Помощь с трудоустройством</h2>
          <p class="t-secondary">Наши выпускники трудоустроились в ведущие медицинские и социальные учреждения, спортивные и СПА-центры, салоны красоты</p>
        </div>
        {btn}
      </div>
      <div class="logos logos--wall reveal">{logos}</div>
    </section>'''


def licences_block(docs):
    """«Лицензии и документы»: тёмная карточка, сканы листаются по кругу ([data-carousel]).
    Общий блок «О нас» и «Трудоустройства», набор сканов у каждой страницы свой."""
    scans = "".join(img(n, a, w, h) for n, a, w, h in docs)
    return f'''<section class="container" aria-labelledby="lic-title">
      <div class="licences reveal" data-carousel>
        <div class="licences__text">
          <h2 id="lic-title">Лицензии и документы</h2>
          <p class="licences__lead">{ABOUT_LOREM}</p>
          <div class="row gap-md">
            <button class="carousel__btn" type="button" data-prev aria-label="Назад">{icon("chevron-left")}</button>
            <button class="carousel__btn" type="button" data-next aria-label="Вперёд">{icon("chevron-right")}</button>
          </div>
        </div>
        <div class="scroller licences__docs" data-track>{scans}</div>
      </div>
    </section>'''


def center_block(first=False):
    """«Мы — международный центр профессионального образования»: фото, цифры в две колонки.
    Общий блок «Трудоустройства» и «О нас». На «О нас» он первый на странице (first):
    заголовок — h1, фото грузится сразу, без появления при прокрутке."""
    tag = "h1" if first else "h2"
    facts = "".join('<ul class="checklist checklist--inverse" role="list">'
                    + "".join(f'<li><span class="icon-badge icon-badge--s">{icon("check")}</span>{f}</li>' for f in col)
                    + '</ul>' for col in JOBS_FACTS)
    return f'''<div class="jobs-center{"" if first else " reveal"}">
        {img("jobs-center", "Слушатели МЦПО на занятии", 875, 590, "jobs-center__bg", lazy=not first)}
        <{tag} class="jobs-center__title" id="center-title">Мы — международный центр профессионального образования</{tag}>
        <div class="jobs-center__facts">{facts}</div>
      </div>'''


def about():
    cr = [("Главная", "index.html"), ("О нас", "about.html")]

    numbers = "".join(
        f'''<article class="number reveal">
          <div class="number__text"><p class="number__value t-nums">{v}</p><p class="number__desc">{ABOUT_LOREM}</p></div>
          {img(pic, "", 600, 600, "number__pic")}
        </article>''' for v, pic in ABOUT_NUMBERS)

    tiles = "".join(
        f'<a class="dir-tile reveal" href="{FAC_LINKS.get(t, "#")}">{img(i,"",660,854)}'
        f'<span class="badge badge--count">{c}</span><span class="dir-tile__title">{t}</span></a>'
        for t, c, i in [("Массаж и реабилитация", "66 курсов", "dir-massage"),
                        ("Косметология", "39 курсов", "dir-cosm"),
                        ("Медицинская подготовка", "155 курсов", "dir-med"),
                        ("Здоровье и развитие ребёнка", "8 курсов", "dir-child")])

    useful = "".join(
        f'<div class="useful__item"><p class="useful__value t-nums">{v}</p><p class="useful__label">{l}</p></div>'
        for v, l in ABOUT_USEFUL)

    tutors = "".join(
        f'''<article class="tutor">
          <div class="tutor__media">{img(pic, name, 800, 1067)}<span class="badge badge--edu tutor__badge">{role}</span></div>
          <h3 class="tutor__name">{name}</h3>
          <dl class="tutor__facts">
            <div class="tutor__row"><dt>Опыт преподавания</dt><dd>{exp}</dd></div>
            <div class="tutor__row tutor__row--stack"><dt>Образование</dt><dd>{edu}</dd></div>
          </dl>
        </article>''' for name, role, exp, edu, pic in ABOUT_TUTORS)

    gallery = "".join(img(g, "Занятие в учебном классе МЦПО", 880, 660, "gallery__pic gallery__pic--" + a)
                      for a, g in ABOUT_GALLERY)
    # копии мозаики для бесконечной ленты — без alt, скринридеру хватит оригинала
    gallery_copy = "".join(img(g, "", 880, 660, "gallery__pic gallery__pic--" + a) for a, g in ABOUT_GALLERY)

    org_ld = {"@context": "https://schema.org", "@type": "AboutPage",
              "name": "О нас — " + ORG_BRAND,
              "mainEntity": {"@type": "EducationalOrganization", "name": ORG_BRAND + " (МЦПО)", "url": SITE}}

    body = f'''
    <section class="container intro" aria-labelledby="center-title">
      {breadcrumbs(cr)}
      {center_block(first=True)}
    </section>

    <section class="container" aria-labelledby="numbers-title">
      <div class="numbers">
        <h2 class="numbers__title" id="numbers-title">Международный центр профессионального образования <span class="t-accent">в цифрах</span></h2>
        <div class="numbers__list" data-stagger>{numbers}</div>
      </div>
    </section>

    {licences_block(ABOUT_DOCS)}

    <section class="section container" aria-labelledby="dir-title">
      {section_head("Направление обучения").replace('class="section-head__title"','class="section-head__title" id="dir-title"')}
      <div class="grid grid-4" data-stagger>{tiles}</div>
      <div class="useful reveal">
        <p class="useful__title">Занятия у нас <span class="t-accent">по-настоящему полезны</span></p>
        <div class="useful__stats">{useful}</div>
      </div>
    </section>

    {jobs_wall('<a class="btn btn--primary btn--m" href="employment.html">Подробнее о трудоустройстве</a>')}

    <section class="tutors-band" aria-labelledby="tutors-title">
      <div class="container stack gap-3xl">
        <h2 class="tutors-band__title" id="tutors-title">Наши преподаватели</h2>
        <div class="carousel stack gap-xl" data-carousel>
          <div class="scroller tutors" data-track>{tutors}</div>
          <div class="row gap-md" style="justify-content:center"><button class="carousel__btn" type="button" data-prev aria-label="Назад">{icon("chevron-left")}</button><div class="dots" data-dots></div><button class="carousel__btn" type="button" data-next aria-label="Вперёд">{icon("chevron-right")}</button></div>
        </div>
      </div>
    </section>

    <section class="section container" aria-labelledby="how-title">
      {section_head("Как проходит обучение","Фото с наших занятий с профессиональными преподавателями, которые поставят руку каждому").replace('class="section-head__title"','class="section-head__title" id="how-title"')}
      <div class="gallery-band reveal">
        <div class="gallery-track">
          <div class="gallery">{gallery}</div>
          <div class="gallery" aria-hidden="true">{gallery_copy}</div>
          <div class="gallery" aria-hidden="true">{gallery_copy}</div>
        </div>
      </div>
    </section>

{lead_block()}
'''
    return page("about.html",
                "О нас — Международный центр профессионального образования (МЦПО)",
                "МЦПО с 1994 года: 400 000+ выпускников, 500+ программ, 100+ преподавателей. Лицензии, направления обучения, помощь с трудоустройством.",
                body, "О центре", [org_ld], cr)

# ======================= Трудоустройство =======================
# Страница для работодателей — макет в ките «Трудоустройство — Desktop» (1362-6282)

JOBS_OFFERS = [("jobs-offer-1", "Подбор персонала под ваш профиль и требования", "Собеседование с кандидатом"),
               ("jobs-offer-2", "Стажировки студентов в вашей компании", "Студенты на стажировке в компании"),
               ("jobs-offer-3", "Повышение квалификации вашего персонала — новые техники, сертификаты", "Обучение сотрудников компании")]

JOBS_STEPS = ["Зарегистрируйте компанию на сайте",
              "Подтвердите почту, которую указали при регистрации, и дождитесь модерации с нашей стороны, в среднем это занимает до 2 часов",
              "После модерации у вас появится возможность разместить свои вакансии и получить доступ к кандидатам, смотреть статистику по вакансиям и компании"]

JOBS_ADVANTAGES = ["Гибкий формат — стажировки, подбор, повышение квалификации",
                   "Гарантированное качество — кандидаты уже проверены практикой"]

# Цифры из макета — в две колонки
JOBS_FACTS = [["1994 год основания МЦПО", "3 000+ партнеров медицинских и реабилитационных учреждений",
               "1 500 курсантов получили повышение квалификации", "500 000+ выпускников"],
              ["35 000+ выпускников трудоустроено", "2 000 образовательных программ", "100+ преподавателей и спикеров"]]

# (пиктограмма, заголовок, текст, вариант карточки: accent — первая, dark — последняя)
JOBS_REASONS = [
    ("diploma", "Диплом сертифицированного образца", "Документ государственного образца — подтверждение вашей квалификации, внесенное в ФИС ФРДО медицинского образования.", "accent"),
    ("study-format", "Очное и дистанционное обучение", "Доступны очные и дистанционные курсы и семинары с выдачей авторских учебных пособий.", ""),
    ("teacher", "Высококвалифицированный преподавательский состав", "Высококвалифицированные практики, эксперты и профессионалы своего дела, имеющие огромный опыт и педагогический стаж.", ""),
    ("individual", "Индивидуальный подход", "Внимание каждому студенту и учет его потребностей. Обучение проходит в небольших группах согласно расписанию, или индивидуальное обучение в удобное для Вас время.", ""),
    ("schedule", "Гибкий график", "Гибкий график обучения — возможность выбора удобного времени занятий для каждого студента.", ""),
    ("methods", "Современные методики обучения", "Использование передовых технологий и подходов к обучению.", ""),
    ("access", "Неограниченный доступ к материалам", "Все учебные материалы останутся у вас в личном кабинете навсегда.", ""),
    ("percent", "Программа лояльности", "Скидки для постоянных клиентов до <b>−35%</b>", "dark"),
]

JOBS_DOCS = ABOUT_DOCS + [("doc-license-annex-2", "Приложение № 1.1 к лицензии № 036718, оборотная сторона", 500, 693)]

JOBS_VIDEOS = [("jobs-review-1", "Смотреть видеоотзыв партнёра МЦПО", 1060, 596),
               ("jobs-review-2", "Смотреть видеоотзыв клиники «Евромедсервис»", 1060, 591),
               ("jobs-review-3", "Смотреть видеоотзыв партнёра МЦПО", 1060, 596)]


def employment():
    cr = [("Главная", "index.html"), ("Трудоустройство", "employment.html")]
    play_light = PLAY.replace('fill="#1C263B"', 'fill="currentColor"')

    hexes = "".join(f'<img class="jobs-guide__hex jobs-guide__hex--{i}" src="assets/icons/jobs-hex-{i}.svg" alt="" width="267" height="304">'
                    for i in (1, 2))
    offers = "".join(f'''<article class="offer-card reveal">
          {img(pic, alt, 1000, 667)}
          <div class="offer-card__head"><span class="icon-badge">{icon("check")}</span><h3 class="offer-card__title">{t}</h3></div>
        </article>''' for pic, t, alt in JOBS_OFFERS)
    steps = "".join(f'<li><span class="steps__num">{i}</span><span>{t}</span></li>' for i, t in enumerate(JOBS_STEPS, 1))

    def adv_head(t):
        return f'<div class="advantage__head"><span class="icon-badge">{icon("star")}</span><h3 class="advantage__title">{t}</h3></div>'
    advantages = "".join(f'<article class="advantage reveal">{adv_head(t)}</article>' for t in JOBS_ADVANTAGES)

    reasons = "".join(f'''<article class="reason{" reason--" + mod if mod else ""} reveal">
          <span class="reason__icon"><img src="assets/icons/pict-{ic}.svg" alt="" width="48" height="48"></span>
          <div class="reason__body"><h3 class="reason__title">{t}</h3><p class="reason__text">{d}</p></div>
        </article>''' for ic, t, d, mod in JOBS_REASONS)

    videos = "".join(f'<button class="video-card reveal" type="button" aria-label="{label}">{img(pic, "", w, h)}<span class="play">{PLAY}</span></button>'
                     for pic, label, w, h in JOBS_VIDEOS)

    body = f'''
    <section class="container intro">
      {intro(cr, "Трудоустройство")}
      <div class="jobs-hero">
        {img("jobs-hero", "", 1920, 1280, "jobs-hero__bg", lazy=False)}
        <div class="jobs-hero__copy">
          <p class="jobs-hero__title">Станьте партнёром МЦПО — зарегистрируйтесь на портале и найдите сотрудника прямо сейчас!</p>
          <p class="jobs-hero__lead">Получите доступ к проверенным выпускникам-специалистам: массажа, косметологии и медицинскому персоналу.</p>
          <div><a class="btn btn--primary" href="#lead">Оставить заявку</a></div>
        </div>
        <figure class="jobs-guide">
          <div class="jobs-guide__cover">
            <span class="logo logo--light">{LOGO_SVG}<span class="logo__text">Международный центр профессионального образования</span></span>
            {hexes}
          </div>
          <figcaption class="jobs-guide__caption">Инструкция по работе с порталом МЦПО Работа</figcaption>
        </figure>
      </div>
    </section>

    <section class="container" aria-labelledby="offers-title">
      <div class="jobs-panel">
        <h2 class="t-h1" id="offers-title">Что мы предлагаем партнёрам</h2>
        <div class="offers" data-stagger>{offers}</div>
      </div>
    </section>

    <section class="container jobs-steps" aria-labelledby="steps-title">
      <div class="jobs-steps__text">
        <h2 class="t-h1" id="steps-title">Как оставить заявку и найти сотрудника</h2>
        <ol class="steps">{steps}</ol>
        <p class="jobs-steps__note">В разделе резюме вы найдете кандидатов, которые уже разместили свои резюме у нас на портале, выбрав подходящие вам фильтры: категории, образование, направления.</p>
        <div><a class="btn btn--primary" href="#lead">Стать партнером по трудоустройству</a></div>
      </div>
      <div class="jobs-steps__photo">{img("jobs-steps", "Работодатель беседует с кандидатами", 927, 596)}</div>
    </section>

    <section class="container" aria-labelledby="adv-title">
      <div class="jobs-panel jobs-panel--dark">
        <h2 class="t-h1" id="adv-title">Преимущества сотрудничества</h2>
        <div class="advantages">
          <article class="advantage advantage--photo reveal">{img("jobs-advantage", "", 1800, 1201)}{adv_head("Экономия времени и ресурсов — мы готовим профессионалов")}</article>
          <div class="advantages__col">{advantages}</div>
        </div>
      </div>
    </section>

    <section class="container" aria-labelledby="center-title">
      {center_block()}
    </section>

    <section class="section container" aria-labelledby="reasons-title">
      <div class="section-head reveal"><h2 class="section-head__title t-h1" id="reasons-title"><span class="reasons-count">9</span> причин обучаться у нас</h2><p class="section-head__lead">Международный Центр Профессионального Образования — это профессиональное обучение, повышение квалификации, профпереподготовка, усовершенствование. В центре работает более 160 сотрудников — директорат, учебный совет, методисты, менеджеры по работе с клиентами, организаторы работы со Слушателями, преподаватели.</p></div>
      <div class="reasons" data-stagger>{reasons}</div>
    </section>

    <section class="container" aria-labelledby="learn-title">
      <div class="jobs-panel jobs-learn">
        <div class="jobs-learn__col">
          <h2 class="t-h1" id="learn-title">Как проходит обучение</h2>
          <p class="jobs-learn__sub">Изучайте курсы в комфортном темпе</p>
          <p class="jobs-learn__text">Смотрите видео в любое время. Доступ к курсу и всем новым материалам останется с вами навсегда.</p>
          <button class="video-card video-card--platform" type="button" aria-label="Смотреть, как устроена учебная платформа">{img("jobs-platform", "Личный кабинет учебной платформы МЦПО", 1232, 582)}<span class="play">{play_light}</span></button>
        </div>
        <div class="jobs-learn__col">
          <h2 class="t-h1">Учебные материалы всегда под рукой</h2>
          <p class="jobs-learn__text">Вы можете проходить обучение в мобильном приложении платформы прямо с телефона — весь прогресс сохранится</p>
          <a class="store-badge-img" href="#"><img src="assets/icons/rustore-badge-dark.svg" alt="Скачайте из RuStore" width="172" height="61"></a>
          <div class="jobs-learn__phone">{img("jobs-phone", "Мобильное приложение платформы МЦПО", 706, 464)}</div>
        </div>
      </div>
    </section>

    {licences_block(JOBS_DOCS)}

    <section class="container jobs-videos" aria-label="Видеоотзывы партнёров">{videos}</section>

    {jobs_wall('<a class="btn btn--primary btn--m" href="#lead">Стать партнёром</a>')}
'''
    return page("employment.html",
                "Трудоустройство выпускников МЦПО — подбор персонала для работодателей",
                "Партнёрам МЦПО: подбор выпускников — массажистов, косметологов, медицинского персонала, стажировки студентов и повышение квалификации сотрудников. Регистрация на портале МЦПО Работа.",
                body, "Трудоустройство", [], cr)

# ======================= Поиск в шапке =======================
# Живая выдача ищет по всем курсам каталога (мегаменю). Если у курса есть карточка
# с ценой (главная, факультет массажа, курсы для врачей), в выдаче её данные,
# иначе — часы из названия и раздел каталога.
def _search_key(title, badges=()):
    """(название без часов в нижнем регистре, часы) — чтобы узнать один курс под разными названиями."""
    hours = (re.search(r"(\d+)\s*(?:ак\.\s*)?ч\b", title)
             or next((re.search(r"(\d+)", t) for k, t in badges if k == "hours"), None))
    base = re.sub(r",?\s*\d+\s*(?:ак\.\s*)?ч\b\.?", "", title).lower().replace("ё", "е")
    return " ".join(re.findall(r"[a-zа-я0-9]+", base)), hours.group(1) if hours else ""

def _same_course(a, b):
    (ba, ha), (bb, hb) = a, b
    if ba == bb:
        return True
    if ba.startswith(bb + " ") or bb.startswith(ba + " "):
        return not ha or not hb or ha == hb
    # «Кардиология — повышение квалификации, 144 ч» и «Кардиология, 144 ак. ч.»
    return bool(ha) and ha == hb and ba.split()[0] == bb.split()[0]

def search_index():
    items, keys = [], []
    for t, m, old, price, badges, image in POPULAR + MASSAGE_COURSES + DOCTOR_COURSES:
        key = _search_key(t, badges)
        if any(_same_course(key, k) for k in keys):
            continue
        keys.append(key)
        href = READY_COURSE if t.startswith("Классический массаж с нуля") else ""
        items.append({"t": t, "m": m, "o": old, "p": price, "b": [list(b) for b in badges], "i": image, "h": href})
    seen = set()
    for _fid, fname, _fimg, dirs in CATALOG:
        for _did, dname, _dimg, courses in dirs:
            for cname, cimg in courses:
                key = _search_key(cname)
                if cname in seen or any(_same_course(key, k) for k in keys):
                    continue
                seen.add(cname)
                meta = fname if dname == fname else f"{fname} · {dname}"
                badges = [["hours", f"{key[1]} ак. ч."]] if key[1] else []
                href = READY_COURSE if cname.startswith("Классический массаж с нуля") else ""
                items.append({"t": cname, "m": meta, "o": "", "p": "", "b": badges, "i": cimg, "h": href})
    js = ("/* Сгенерировано docs/build.py (search_index) — руками не править.\n"
          "   Курсы для живого поиска в шапке, окно #modal-search. main.js подгружает файл при первом открытии окна.\n"
          "   t — название, m — подпись, o — старая цена, p — цена, b — бейджи, i — картинка, h — страница курса. */\n"
          "window.MZPO_COURSES = " + json.dumps(items, ensure_ascii=False, separators=(",", ":")).replace("},{", "},\n{") + ";\n")
    with open(os.path.join(OUT, "assets", "js", "search-index.js"), "w", encoding="utf-8") as f:
        f.write(js)
    return f"assets/js/search-index.js ({len(items)} курсов)"

if __name__ == "__main__":
    built = [home(), doctors(), accreditation(), teacher_profile(), promotions(), about(), employment(), faculty(), course(), schedule(), events(), teachers_page(), contacts(), cart(), checkout(1), checkout(2), search_index()]
    print("built:", built)
