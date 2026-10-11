(function () {
  // Проекты отдаёт Java-сервер: GET /api/projects (данные в src/main/resources/projects.json)
  fetch('api/projects')
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .catch(function () { return []; })
    .then(start);

  function start(PROJECTS) {
    var $ = function (id) { return document.getElementById(id); };
    var fmtNum = function (n) { return String(n).replace('.', ','); };
    var fmtArea = function (n) { return (Math.round(n * 100) / 100).toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); };
    var fmtPrice = function (n) { return n.toLocaleString('ru-RU') + ' ₽'; };
    var areaOf = function (p) { return p.totalArea; };
    var priceOf = function (p) { return p.minPrice; };
    var tiersHTML = function (p) {
      return p.prices ? '<ul class="tiers">' + p.prices.map(function (x) { return '<li><span>' + x.label + '</span><b>' + fmtPrice(x.price) + '</b></li>'; }).join('') + '</ul>' : '';
    };
    var bedsText = function (n) { return n + (n === 1 ? ' спальня' : ' спальни'); };
    var floorsText = function (n) { return n + ' ' + (n === 1 ? 'этаж' : 'этажа'); };
    var esc = function (s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;'); };
    var pad2 = function (n) { return (n < 10 ? '0' : '') + n; };
    var byId = function (id) { return PROJECTS.filter(function (p) { return p.id === id; })[0]; };

    /* ---------- Меню ---------- */
    var menu = $('menu'), menuOpen = $('menuOpen'), lastFocus = null;
    function setLock(on) { document.documentElement.style.overflow = on ? 'hidden' : ''; }
    function openMenu() { menu.hidden = false; menuOpen.setAttribute('aria-expanded', 'true'); setLock(true); $('menuClose').focus(); }
    function closeMenu() { menu.hidden = true; menuOpen.setAttribute('aria-expanded', 'false'); setLock(false); menuOpen.focus(); }
    menuOpen.addEventListener('click', openMenu);
    $('menuClose').addEventListener('click', closeMenu);
    menu.addEventListener('click', function (e) {
      if (e.target.closest('[data-nav]')) { menu.hidden = true; menuOpen.setAttribute('aria-expanded', 'false'); setLock(false); }
    });

    /* ---------- Слайдер проектов ---------- */
    var track = $('track'), prev = $('prev'), next = $('next'), counter = $('counter');
    function slideHTML(p) {
      return '<article class="slide" data-id="' + p.id + '">' +
        '<img class="slide-img" src="' + p.images[0].src + '" alt="' + esc(p.images[0].alt) + '" loading="lazy">' +
        '<div class="slide-body">' +
          '<p class="price">от ' + fmtPrice(priceOf(p)) + '</p>' + tiersHTML(p) +
          '<h3>' + p.name + '</h3>' +
          '<p class="meta">' + fmtNum(areaOf(p)) + ' м² · ' + floorsText(p.floors) + ' · ' + bedsText(p.bedrooms) + '</p>' +
          '<p class="desc">' + p.desc + '</p>' +
          '<button class="btn btn-primary" type="button" data-open="' + p.id + '">Подробнее</button>' +
        '</div></article>';
    }
    var ownSlide = '<article class="slide own"><div class="slide-body">' +
      '<h3>Нужен другой дом?</h3><p>Расскажите, какой дом вам нужен, и мы рассчитаем стоимость по вашему проекту или подберём подходящий.</p>' +
      '<a class="btn btn-inv" href="#zayavka">Оставить заявку</a></div></article>';
    track.innerHTML = PROJECTS.map(slideHTML).join('') + ownSlide;
    var slides = track.querySelectorAll('.slide');

    function slideStep() { return slides.length > 1 ? slides[1].offsetLeft - slides[0].offsetLeft : track.clientWidth; }
    function updateSlider() {
      var atEnd = track.scrollLeft + track.clientWidth >= track.scrollWidth - 2;
      var idx = atEnd ? slides.length - 1 : Math.round(track.scrollLeft / Math.max(1, slideStep()));
      counter.innerHTML = pad2(idx + 1) + ' <span>/ ' + pad2(slides.length) + '</span>';
      prev.disabled = track.scrollLeft <= 2;
      next.disabled = atEnd;
      var fits = track.scrollWidth <= track.clientWidth + 2;
      $('sliderBar').hidden = fits;
    }
    var tick = 0;
    track.addEventListener('scroll', function () { if (!tick) tick = requestAnimationFrame(function () { tick = 0; updateSlider(); }); });
    prev.addEventListener('click', function () { track.scrollBy({ left: -slideStep(), behavior: 'smooth' }); });
    next.addEventListener('click', function () { track.scrollBy({ left: slideStep(), behavior: 'smooth' }); });
    window.addEventListener('resize', updateSlider);
    updateSlider();

    /* ---------- Окно проекта ---------- */
    var modal = $('modal'), panel = modal.querySelector('.modal-panel'), modalBody = $('modalBody');
    function wallsHTML(p) {
      if (!p.walls) return '';
      var items = p.walls.options.map(function (o, i) {
        return '<li><small>Вариант ' + (i + 1) + (i < p.walls.base ? ' · цена в каталоге' : '') + '</small><b>' + o.title + '</b><span>' + o.text + '</span></li>';
      }).join('');
      return '<p class="rooms-title">Материал стен на выбор</p><ul class="walls">' + items + '</ul><p class="walls-note">' + p.walls.note + '</p>';
    }
    function detailHTML(p) {
      var maxRoom = Math.max.apply(null, p.rooms.map(function (r) { return r.area; }));
      var thumbs = p.images.map(function (im, i) {
        return '<button class="thumb' + (im.plan ? ' is-plan' : '') + '" type="button" data-i="' + i + '" aria-label="' + esc(im.cap) + '" aria-current="' + (i === 0) + '"><img src="' + im.src + '" alt="" loading="lazy"></button>';
      }).join('');
      var rooms = p.rooms.map(function (r) {
        return '<li><span>' + r.name + '</span><span class="a">' + fmtArea(r.area) + ' м²</span><span class="bar"><i style="width:' + (r.area / maxRoom * 100).toFixed(1) + '%"></i></span></li>';
      }).join('') + '<li class="sum"><span>Итого' + (p.totalNote ? ' (' + p.totalNote + ')' : '') + '</span><span class="a">' + fmtNum(areaOf(p)) + ' м²</span></li>';
      var im0 = p.images[0];
      return '<div class="detail" data-id="' + p.id + '">' +
        '<div class="gallery">' +
          '<div class="stage"><img src="' + im0.src + '" alt="' + esc(im0.alt) + '"><span class="stage-cap">' + im0.cap + '</span></div>' +
          '<div class="thumbs">' + thumbs + '</div>' +
        '</div>' +
        '<div class="info">' +
          '<h3 id="mTitle">' + p.name + '</h3>' +
          (p.prices ? tiersHTML(p) : '<p class="price">' + fmtPrice(p.price) + '<small>под ключ</small></p>') +
          '<p class="desc">' + p.desc + '</p>' +
          '<dl class="spec">' +
            '<div><dt>Общая площадь</dt><dd>' + fmtNum(areaOf(p)) + ' м²</dd></div>' +
            '<div><dt>Этажность</dt><dd>' + p.floors + '</dd></div>' +
            '<div><dt>Спальни</dt><dd>' + p.bedrooms + '</dd></div>' +
            (p.specs || []).map(function (r) { return '<div><dt>' + r.name + '</dt><dd>' + r.value + '</dd></div>'; }).join('') +
          '</dl>' +
          '<p class="rooms-title">Помещения</p>' +
          '<ul class="rooms">' + rooms + '</ul>' + wallsHTML(p) +
          '<div class="actions"><button class="btn btn-primary" type="button" data-pick="' + p.id + '">Оставить заявку на этот дом</button></div>' +
        '</div></div>';
    }
    function openModal(id) {
      var p = byId(id); if (!p) return;
      lastFocus = document.activeElement;
      modalBody.innerHTML = detailHTML(p);
      modal.hidden = false; setLock(true);
      modal.scrollTop = 0;
      panel.focus();
    }
    function closeModal() { modal.hidden = true; setLock(false); if (lastFocus && lastFocus.focus) lastFocus.focus(); }
    track.addEventListener('click', function (e) { var b = e.target.closest('[data-open]'); if (b) openModal(b.getAttribute('data-open')); });
    modal.addEventListener('click', function (e) {
      if (e.target.closest('[data-close]')) { closeModal(); return; }
      var t = e.target.closest('.thumb');
      if (t) {
        var d = t.closest('.detail'), p = byId(d.getAttribute('data-id')), im = p.images[Number(t.getAttribute('data-i'))];
        var stage = d.querySelector('.stage');
        stage.classList.toggle('is-plan', !!im.plan);
        stage.querySelector('img').src = im.src; stage.querySelector('img').alt = im.alt;
        stage.querySelector('.stage-cap').textContent = im.cap;
        d.querySelectorAll('.thumb').forEach(function (x) { x.setAttribute('aria-current', String(x === t)); });
        return;
      }
      var pick = e.target.closest('[data-pick]');
      if (pick) {
        select.value = pick.getAttribute('data-pick');
        closeModal();
        $('zayavka').scrollIntoView();
        setTimeout(function () { $('fName').focus({ preventScroll: true }); }, 400);
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { if (!modal.hidden) closeModal(); else if (!menu.hidden) closeMenu(); return; }
      if (e.key === 'Tab' && (!modal.hidden || !menu.hidden)) {
        var root = !modal.hidden ? panel : menu;
        var f = Array.prototype.filter.call(root.querySelectorAll('a[href], button, input, select, textarea, [tabindex="0"]'), function (el) { return !el.disabled && el.offsetParent !== null; });
        if (!f.length) return;
        var first = f[0], last = f[f.length - 1];
        if (e.shiftKey && (document.activeElement === first || document.activeElement === root)) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });

    /* ---------- Формы ---------- */
    var select = $('fProject');
    select.innerHTML = '<option value="">Пока не выбрал(а)</option>' +
      PROJECTS.map(function (p) { return '<option value="' + p.id + '">' + p.name + ' · от ' + fmtPrice(priceOf(p)) + '</option>'; }).join('');
    // Заявка уходит на Java-сервер: POST /api/leads
    document.querySelectorAll('.js-form').forEach(function (f) {
      f.addEventListener('submit', function (e) {
        e.preventDefault();
        var s = f.querySelector('.status'), btn = f.querySelector('[type="submit"]');
        var data = {};
        new FormData(f).forEach(function (v, k) { data[k] = v; });
        btn.disabled = true;
        fetch('api/leads', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
          .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, j: j }; }); })
          .then(function (res) {
            s.hidden = false;
            s.textContent = res.j.message || (res.ok ? 'Заявка отправлена.' : 'Не удалось отправить заявку.');
            if (res.ok) f.reset();
          })
          .catch(function () {
            s.hidden = false;
            s.textContent = 'Нет связи с сервером. Позвоните нам: +7 967 772 2214.';
          })
          .then(function () { btn.disabled = false; });
      });
    });

    $('cookieOk').addEventListener('click', function () { $('cookie').hidden = true; });
  }
})();
