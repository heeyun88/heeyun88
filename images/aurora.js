/*!
 * Aurora — Tistory skin script
 * 의존성 없는 순수 자바스크립트 (jQuery 불필요)
 * 기능: 테마 전환 · 헤더 · 검색(Ctrl+K) · 드로어 · 카테고리 칩 · 보기 전환 · 카드 효과
 *       히어로(키워드·통계·카드 스택) · 태그 마키 · 목차/스크롤스파이 · 공유 · 코드 복사
 *       더 보기 로딩 · 커버 슬라이더/캐러셀 · 태그 필터 · 맨 위로
 */
(function () {
	'use strict';

	var doc = document;
	var root = doc.documentElement;
	var body = doc.body;
	if (!body) return;

	/* ---------- 유틸 ---------- */
	var $ = function (s, c) { return (c || doc).querySelector(s); };
	var $$ = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };
	var hasOpt = function (name) { return body.classList.contains(name); };
	var mm = function (q) { return window.matchMedia ? window.matchMedia(q) : { matches: false, addEventListener: function () {} }; };
	var reduceMotion = mm('(prefers-reduced-motion: reduce)').matches;
	var motionOK = hasOpt('opt-motion') && !reduceMotion;
	var finePointer = mm('(hover: hover) and (pointer: fine)').matches;
	var bodyId = body.id || '';
	var isIndex = bodyId === 'tt-body-index';
	var isPage = bodyId === 'tt-body-page';
	var blogTitle = (($('.brand__name') || {}).textContent || '').trim();
	var store = {
		get: function (k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } },
		set: function (k, v) { try { window.localStorage.setItem(k, v); } catch (e) { /* noop */ } },
		del: function (k) { try { window.localStorage.removeItem(k); } catch (e) { /* noop */ } }
	};
	var safe = function (fn) { try { fn(); } catch (e) { if (window.console) console.warn('[Aurora]', e); } };
	var icon = function (name, cls) { return '<svg class="i' + (cls ? ' ' + cls : '') + '" aria-hidden="true"><use href="#i-' + name + '"/></svg>'; };
	var headerH = function () { return parseFloat(getComputedStyle(root).getPropertyValue('--header-h')) || 64; };
	var clamp = function (n, a, b) { return Math.min(b, Math.max(a, n)); };
	var enc = encodeURIComponent;
	var normPath = function (u) {
		try {
			var p = new URL(u, location.href);
			if (p.origin !== location.origin) return null;
			return decodeURIComponent(p.pathname).replace(/\/+$/, '') || '/';
		} catch (e) { return null; }
	};
	var here = normPath(location.href);
	var parseDate = function (s) {
		var m = String(s || '').match(/(\d{4})\D+(\d{1,2})\D+(\d{1,2})(?:\D+(\d{1,2})\D+(\d{1,2}))?/);
		return m ? new Date(+m[1], +m[2] - 1, +m[3], +(m[4] || 0), +(m[5] || 0)) : null;
	};
	var textOf = function (el) {
		if (!el) return '';
		var c = el.cloneNode(true);
		$$('.c_cnt, img, svg', c).forEach(function (n) { n.remove(); });
		return c.textContent.replace(/\s+/g, ' ').trim();
	};
	var isUncategorized = function (t) { t = (t || '').trim(); return !t || t === '카테고리 없음' || t === '분류없음' || t === '분류 없음'; };

	/* ---------- 토스트 · 복사 ---------- */
	var toastEl = $('.toast');
	var toastTimer;
	function toast(msg) {
		if (!toastEl) return;
		toastEl.innerHTML = icon('check') + '<span></span>';
		toastEl.lastChild.textContent = msg;
		toastEl.classList.add('is-show');
		clearTimeout(toastTimer);
		toastTimer = setTimeout(function () { toastEl.classList.remove('is-show'); }, 2200);
	}
	function copyText(text) {
		if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
		return new Promise(function (resolve, reject) {
			var ta = doc.createElement('textarea');
			ta.value = text;
			ta.setAttribute('readonly', '');
			ta.style.cssText = 'position:fixed;top:-9999px;opacity:0';
			body.appendChild(ta);
			ta.select();
			try { doc.execCommand('copy') ? resolve() : reject(); } catch (e) { reject(e); }
			ta.remove();
		});
	}

	/* ---------- 1. 테마 ---------- */
	var THEME_KEY = 'aurora-theme';
	var currentTheme = function () { return root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light'; };
	function applyTheme(t) {
		root.setAttribute('data-theme', t);
		$$('meta[name="theme-color"]').forEach(function (m) { m.setAttribute('content', t === 'dark' ? '#07080e' : '#f6f7fb'); });
	}
	function toggleTheme(e) {
		var next = currentTheme() === 'dark' ? 'light' : 'dark';
		store.set(THEME_KEY, next);
		if (!doc.startViewTransition || !motionOK) { applyTheme(next); return; }
		var r = e && e.currentTarget ? e.currentTarget.getBoundingClientRect() : { left: innerWidth - 60, top: 20, width: 40, height: 40 };
		var x = r.left + r.width / 2;
		var y = r.top + r.height / 2;
		var rad = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
		root.classList.add('theme-vt');
		var vt = doc.startViewTransition(function () { applyTheme(next); });
		vt.ready.then(function () {
			root.animate(
				{ clipPath: ['circle(0px at ' + x + 'px ' + y + 'px)', 'circle(' + rad + 'px at ' + x + 'px ' + y + 'px)'] },
				{ duration: 700, easing: 'cubic-bezier(.22,1,.36,1)', pseudoElement: '::view-transition-new(root)' }
			);
		}).catch(function () {});
		vt.finished.then(function () { root.classList.remove('theme-vt'); }, function () { root.classList.remove('theme-vt'); });
	}
	safe(function () {
		applyTheme(currentTheme());
		$$('.theme-toggle').forEach(function (b) { b.addEventListener('click', toggleTheme); });
		var def = root.getAttribute('data-default-theme');
		var mq = mm('(prefers-color-scheme: dark)');
		var onChange = function () {
			if (!store.get(THEME_KEY) && !/^(light|dark)$/.test(def || '')) applyTheme(mq.matches ? 'dark' : 'light');
		};
		if (mq.addEventListener) mq.addEventListener('change', onChange);
		else if (mq.addListener) mq.addListener(onChange);
	});

	/* ---------- 2. 팝오버 (드로어·검색) + 미지원 브라우저 폴백 ---------- */
	var popSupported = typeof HTMLElement !== 'undefined' && Object.prototype.hasOwnProperty.call(HTMLElement.prototype, 'popover');
	var drawer = $('#drawer');
	var searchPanel = $('#search-panel');
	var searchInput = $('#search-input');
	function isOpen(el) {
		if (!el) return false;
		if (popSupported) { try { return el.matches(':popover-open'); } catch (e) { return false; } }
		return el.classList.contains('is-open');
	}
	function afterOpen(el) {
		if (el === searchPanel) {
			renderSearchPanel();
			if (searchInput) setTimeout(function () { searchInput.focus(); searchInput.select(); }, 30);
		} else if (el === drawer) {
			var f = $('.drawer__head .icon-btn', drawer);
			if (f && !popSupported) f.focus();
		}
	}
	function openPop(el) {
		if (!el || isOpen(el)) return;
		if (popSupported) { try { el.showPopover(); } catch (e) { /* noop */ } }
		else {
			closeAllPops();
			el.classList.add('is-open');
			root.classList.add('has-overlay');
			afterOpen(el);
		}
	}
	function closePop(el) {
		if (!el || !isOpen(el)) return;
		if (popSupported) { try { el.hidePopover(); } catch (e) { /* noop */ } }
		else {
			el.classList.remove('is-open');
			if (!$('.is-open[popover]')) root.classList.remove('has-overlay');
		}
	}
	function closeAllPops() { [drawer, searchPanel].forEach(closePop); }
	var anyPopOpen = function () { return isOpen(drawer) || isOpen(searchPanel); };

	safe(function () {
		if (popSupported) {
			[drawer, searchPanel].forEach(function (el) {
				if (el) el.addEventListener('toggle', function (e) { if (e.newState === 'open') afterOpen(el); });
			});
		} else {
			doc.addEventListener('click', function (e) {
				var btn = e.target.closest('[popovertarget]');
				if (btn) {
					var t = doc.getElementById(btn.getAttribute('popovertarget'));
					var act = btn.getAttribute('popovertargetaction') || 'toggle';
					if (t) {
						e.preventDefault();
						if (act === 'hide' || (act === 'toggle' && isOpen(t))) closePop(t);
						else openPop(t);
					}
					return;
				}
				$$('.is-open[popover]').forEach(function (p) { if (!p.contains(e.target)) closePop(p); });
			});
			doc.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeAllPops(); });
		}
	});

	/* ---------- 3. 검색 (단축키 · 최근 검색어 · 추천 태그) ---------- */
	var RECENT_KEY = 'aurora-recent-search';
	var getRecent = function () {
		try { return (JSON.parse(store.get(RECENT_KEY) || '[]') || []).filter(Boolean).slice(0, 8); } catch (e) { return []; }
	};
	var saveRecent = function (q) {
		q = (q || '').trim();
		if (!q) return;
		var list = getRecent().filter(function (x) { return x !== q; });
		list.unshift(q);
		store.set(RECENT_KEY, JSON.stringify(list.slice(0, 8)));
	};
	var collectTags = (function () {
		var cache = null;
		return function () {
			if (cache) return cache;
			var seen = {};
			cache = [];
			$$('.widget--tags .tag-pill, .tag-cloud .tag-pill').forEach(function (a) {
				var name = a.textContent.replace(/^#/, '').trim();
				if (!name || seen[name]) return;
				seen[name] = 1;
				cache.push({ name: name, href: a.getAttribute('href') });
			});
			return cache;
		};
	})();
	function renderSearchPanel() {
		var g = $('[data-recent]');
		var list = $('[data-recent-list]');
		if (g && list) {
			var recent = getRecent();
			list.innerHTML = '';
			recent.forEach(function (q) {
				var a = doc.createElement('a');
				a.href = '/search/' + enc(q);
				a.innerHTML = icon('clock');
				a.appendChild(doc.createTextNode(q));
				list.appendChild(a);
			});
			g.hidden = !recent.length;
		}
		var sg = $('[data-suggest]');
		var sl = $('[data-suggest-list]');
		if (sg && sl && !sl.children.length) {
			var tags = collectTags().slice(0, 12);
			tags.forEach(function (t) {
				var a = doc.createElement('a');
				a.href = t.href;
				a.textContent = '#' + t.name;
				sl.appendChild(a);
			});
			sg.hidden = !tags.length;
		}
	}
	safe(function () {
		if (/Mac|iPhone|iPad|iPod/i.test(navigator.platform || navigator.userAgent || '')) {
			$$('.search-trigger__kbd').forEach(function (k) { k.textContent = '⌘ K'; });
		}
		doc.addEventListener('keydown', function (e) {
			var t = e.target || {};
			var tag = (t.tagName || '').toLowerCase();
			var typing = tag === 'input' || tag === 'textarea' || tag === 'select' || t.isContentEditable;
			if ((e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey) && !e.altKey) {
				e.preventDefault();
				isOpen(searchPanel) ? closePop(searchPanel) : openPop(searchPanel);
			} else if (e.key === '/' && !typing && !e.metaKey && !e.ctrlKey && !e.altKey) {
				e.preventDefault();
				openPop(searchPanel);
			}
		});
		doc.addEventListener('submit', function (e) {
			var f = e.target;
			if (f && f.classList && f.classList.contains('search-form')) {
				var inp = f.querySelector('input[type="search"]');
				if (inp) saveRecent(inp.value);
			}
		}, true);
		var clear = $('[data-recent-clear]');
		if (clear) clear.addEventListener('click', function () { store.del(RECENT_KEY); renderSearchPanel(); });
	});

	/* ---------- 4. 스크롤: 헤더 · 읽기 진행 바 · 맨 위로 · 목차 ---------- */
	var header = $('.site-header');
	var progress = $('.progress');
	var toTop = $('.to-top');
	var postContent = $('[data-post-content]');
	var tocHeads = [];
	var tocLinks = [];
	var lastY = window.scrollY || 0;
	var ticking = false;
	var activeId = null;

	function setActiveToc(id) {
		if (id === activeId) return;
		activeId = id;
		tocLinks.forEach(function (l) {
			var on = l.getAttribute('href') === '#' + id;
			l.classList.toggle('is-active', on);
			if (on) {
				var list = l.closest('.post-rail .toc__list');
				if (list) {
					var top = l.offsetTop - list.clientHeight / 2;
					list.scrollTo({ top: top, behavior: 'auto' });
				}
			}
		});
	}
	function onScroll() {
		ticking = false;
		var y = window.scrollY || root.scrollTop || 0;
		var vh = window.innerHeight;
		if (header) {
			header.classList.toggle('is-scrolled', y > 8);
			var dy = y - lastY;
			if (y > 360 && dy > 6 && !anyPopOpen() && !header.contains(doc.activeElement)) header.classList.add('is-hidden');
			else if (dy < -6 || y < 360) header.classList.remove('is-hidden');
		}
		lastY = y;
		var max = root.scrollHeight - vh;
		var pageP = max > 0 ? clamp(y / max, 0, 1) : 0;
		if (toTop) {
			toTop.classList.toggle('is-visible', y > 640);
			toTop.style.setProperty('--p', pageP.toFixed(4));
		}
		if (progress && postContent && isPage) {
			var r = postContent.getBoundingClientRect();
			var total = r.height - vh * 0.55;
			var p = total > 0 ? clamp((vh * 0.3 - r.top) / total, 0, 1) : pageP;
			progress.style.setProperty('--p', p.toFixed(4));
		}
		if (tocHeads.length) {
			var line = headerH() + 40;
			var cur = tocHeads[0];
			for (var i = 0; i < tocHeads.length; i++) {
				if (tocHeads[i].getBoundingClientRect().top - line <= 0) cur = tocHeads[i];
				else break;
			}
			setActiveToc(cur.id);
		}
	}
	var requestScroll = function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } };
	safe(function () {
		window.addEventListener('scroll', requestScroll, { passive: true });
		window.addEventListener('resize', requestScroll, { passive: true });
		if (header) header.addEventListener('focusin', function () { header.classList.remove('is-hidden'); });
		if (toTop) toTop.addEventListener('click', function () {
			window.scrollTo({ top: 0, behavior: motionOK ? 'smooth' : 'auto' });
			var brand = $('.brand');
			if (brand) brand.focus({ preventScroll: true });
		});
		onScroll();
	});

	/* ---------- 5. 현재 위치 표시 · 카테고리 트리 ---------- */
	safe(function () {
		$$('.gnb a, .drawer__menu a').forEach(function (a) {
			var p = normPath(a.href);
			if (!p) return;
			if (p === here || (p !== '/' && here && here.indexOf(p + '/') === 0)) a.classList.add('is-current');
		});
		$$('.category-tree a').forEach(function (a) {
			if (a.querySelector('img')) a.classList.add('has-new');
			var cnt = a.querySelector('.c_cnt');
			if (cnt) cnt.textContent = cnt.textContent.replace(/[()\s]/g, '');
			if (normPath(a.href) === here) a.classList.add('is-current');
		});
		['.drawer__desc', '.footer-brand__text', '.author-card__desc', '.hero__desc', '.list-head__desc'].forEach(function (s) {
			$$(s).forEach(function (el) { if (!el.textContent.trim()) el.hidden = true; });
		});
		$$('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
	});

	/* ---------- 6. 카테고리 칩 바 ---------- */
	safe(function () {
		var bar = $('.chips-bar');
		if (!bar || !(isIndex || bodyId === 'tt-body-category')) return;
		var top = $('.category-tree .link_tit');
		var items = $$('.category-tree .category_list > li > a');
		if (!items.length) return;
		var mk = function (a, label, active) {
			var c = doc.createElement('a');
			c.href = a.getAttribute('href');
			c.textContent = label || textOf(a);
			var cnt = a.querySelector('.c_cnt');
			if (cnt && cnt.textContent.trim()) {
				var s = doc.createElement('small');
				s.textContent = cnt.textContent.replace(/[()\s]/g, '');
				c.appendChild(s);
			}
			if (active) c.classList.add('is-active');
			return c;
		};
		var frag = doc.createDocumentFragment();
		var anyActive = false;
		items.forEach(function (a) {
			var on = normPath(a.href) === here || (here && here.indexOf(normPath(a.href) + '/') === 0);
			anyActive = anyActive || on;
			frag.appendChild(mk(a, null, on));
		});
		if (top) bar.appendChild(mk(top, '전체', !anyActive));
		bar.appendChild(frag);
		bar.hidden = false;
		var act = $('.is-active', bar);
		if (act) bar.scrollLeft = Math.max(0, act.offsetLeft - 24);
	});

	/* ---------- 7. 카드: 텍스트 커버 · NEW · 상대 날짜 · 스포트라이트 ---------- */
	var io = null;
	var observeReveal = function () {};
	safe(function () {
		var supportsSDA = window.CSS && CSS.supports && CSS.supports('animation-timeline: view()');
		if (!motionOK || supportsSDA || !('IntersectionObserver' in window)) return;
		io = new IntersectionObserver(function (entries) {
			entries.forEach(function (en) {
				if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
			});
		}, { rootMargin: '0px 0px -6% 0px', threshold: 0.06 });
		observeReveal = function (scope) {
			var n = 0;
			$$('.reveal:not(.is-in)', scope).forEach(function (el) {
				if (el.getBoundingClientRect().top < window.innerHeight * 0.96) el.classList.add('is-in');
				else { el.style.setProperty('--i', String(n++ % 3)); io.observe(el); }
			});
		};
		observeReveal(doc);
		root.classList.add('io-reveal');
	});

	function relDate(d) {
		var now = new Date();
		var start = new Date(now.getFullYear(), now.getMonth(), now.getDate());
		var diffDays = Math.round((start - new Date(d.getFullYear(), d.getMonth(), d.getDate())) / 864e5);
		if (diffDays <= 0) {
			var h = Math.floor((now - d) / 36e5);
			return h >= 1 ? h + '시간 전' : '방금 전';
		}
		if (diffDays === 1) return '어제';
		return diffDays + '일 전';
	}
	function addPhText(card) {
		var ph = $('.ph', card);
		var title = $('.card__title', card);
		if (!ph || !title || ph.classList.contains('ph--lock') || $('.ph__text', ph)) return;
		var t = doc.createElement('span');
		t.className = 'ph__text';
		t.textContent = title.textContent.trim();
		var b = doc.createElement('span');
		b.className = 'ph__brand';
		b.textContent = blogTitle;
		ph.appendChild(t);
		ph.appendChild(b);
	}
	function enhanceCards(scope) {
		$$('.card, .slide', scope).forEach(function (card) {
			if (card.getAttribute('data-enhanced')) return;
			card.setAttribute('data-enhanced', '1');
			var img = $('.card__img, .slide__img', card);
			if (!img) addPhText(card);
			else {
				img.addEventListener('error', function () { img.remove(); addPhText(card); }, { once: true });
				if (img.complete && img.naturalWidth === 0 && img.getAttribute('src')) { img.remove(); addPhText(card); }
			}
			$$('.chip', card).forEach(function (c) { if (isUncategorized(c.textContent)) c.classList.add('is-hidden'); });
			var time = $('[data-date]', card);
			var d = time && parseDate(time.getAttribute('datetime') || time.textContent);
			if (d && !isNaN(d)) {
				var age = Date.now() - d.getTime();
				if (age > -864e5 && age < 7 * 864e5) {
					time.setAttribute('title', time.textContent.trim());
					time.textContent = relDate(d);
					var media = $('.card__media', card);
					if (media && !$('.badge-new', media)) {
						var badge = doc.createElement('span');
						badge.className = 'badge-new';
						badge.textContent = 'NEW';
						media.appendChild(badge);
					}
				}
			}
			if (motionOK && finePointer && card.classList.contains('card')) {
				card.addEventListener('pointermove', function (e) {
					var r = card.getBoundingClientRect();
					card.style.setProperty('--mx', (e.clientX - r.left) + 'px');
					card.style.setProperty('--my', (e.clientY - r.top) + 'px');
				});
			}
		});
	}
	safe(function () { enhanceCards(doc); });

	/* ---------- 8. 목록 보기 전환 (매거진·그리드·리스트) ---------- */
	safe(function () {
		var toggle = $('.view-toggle');
		var feed = $('#feed');
		if (!toggle || !feed || !$('.card', feed)) return;
		var VIEW_KEY = 'aurora-view';
		var layouts = ['magazine', 'grid', 'list'];
		var m = body.className.match(/\blayout-(magazine|grid|list)\b/);
		var def = m ? m[1] : 'magazine';
		var setLayout = function (l) {
			layouts.forEach(function (x) { body.classList.remove('layout-' + x); });
			body.classList.add('layout-' + l);
			$$('button[data-view]', toggle).forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-view') === l)); });
		};
		var saved = store.get(VIEW_KEY);
		setLayout(layouts.indexOf(saved) > -1 ? saved : def);
		toggle.hidden = false;
		toggle.addEventListener('click', function (e) {
			var b = e.target.closest('button[data-view]');
			if (!b) return;
			var l = b.getAttribute('data-view');
			store.set(VIEW_KEY, l);
			if (!doc.startViewTransition || !motionOK) { setLayout(l); return; }
			var cards = $$('.card', feed).slice(0, 24);
			cards.forEach(function (c, i) { c.style.viewTransitionName = 'aurora-card-' + i; });
			var vt = doc.startViewTransition(function () { setLayout(l); });
			var cleanup = function () { cards.forEach(function (c) { c.style.viewTransitionName = ''; }); };
			vt.finished.then(cleanup, cleanup);
		});
	});

	/* ---------- 9. 홈 히어로 ---------- */
	function countUp(el, target) {
		var fmt = function (n) { return Math.round(n).toLocaleString('ko-KR'); };
		if (!motionOK) { el.textContent = fmt(target); return; }
		var start = null;
		var dur = 1800;
		var step = function (ts) {
			if (!start) start = ts;
			var t = Math.min(1, (ts - start) / dur);
			var eased = t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
			el.textContent = fmt(target * eased);
			if (t < 1) requestAnimationFrame(step);
		};
		requestAnimationFrame(step);
	}
	function whenVisible(el, cb) {
		if (!('IntersectionObserver' in window)) { cb(); return; }
		var o = new IntersectionObserver(function (en) {
			if (en[0] && en[0].isIntersecting) { o.disconnect(); cb(); }
		}, { threshold: 0.3 });
		o.observe(el);
	}
	safe(function () {
		var hero = $('.hero');
		if (!hero || !isIndex) return;
		var pg = (location.search.match(/[?&]page=(\d+)/) || [])[1];
		if (pg && +pg > 1) { hero.remove(); return; }

		/* 순환 키워드 */
		var rot = $('.hero__rotator', hero);
		if (rot) {
			var raw = rot.getAttribute('data-words') || '';
			var words = raw.indexOf('[##') === 0 ? [] : raw.split(/[,，、|]/).map(function (s) { return s.trim(); }).filter(Boolean);
			var box = $('.hero__words', rot);
			if (!words.length || !box) rot.hidden = true;
			else {
				box.setAttribute('aria-hidden', 'true');
				var sr = doc.createElement('span');
				sr.className = 'sr-only';
				sr.textContent = words.join(', ');
				rot.appendChild(sr);
				var spans = words.map(function (w, i) {
					var s = doc.createElement('span');
					s.className = 'hero__word' + (i === 0 ? ' is-active' : '');
					s.textContent = w;
					box.appendChild(s);
					return s;
				});
				if (spans.length > 1 && motionOK) {
					var idx = 0;
					setInterval(function () {
						if (doc.hidden) return;
						var cur = spans[idx];
						idx = (idx + 1) % spans.length;
						var nxt = spans[idx];
						cur.classList.remove('is-active');
						cur.classList.add('is-leaving');
						nxt.classList.remove('is-leaving');
						nxt.classList.add('is-active');
						setTimeout(function () { cur.classList.remove('is-leaving'); }, 750);
					}, 2600);
				}
			}
		}

		/* 통계: 글 수 · 누적 방문 */
		var stats = $('.hero__stats', hero);
		if (stats && hasOpt('opt-stats')) {
			var shown = false;
			var setStat = function (key, val) {
				var n = parseInt(String(val || '').replace(/[^\d]/g, ''), 10);
				var el = $('[data-stat="' + key + '"]', stats);
				if (!el || !isFinite(n) || n <= 0) return;
				el.hidden = false;
				$('[data-countup]', el).setAttribute('data-target', n);
				shown = true;
			};
			var posts = $('[data-list-count]');
			var total = $('.widget--counter [data-count="total"]');
			if (posts) setStat('posts', posts.textContent);
			if (total) setStat('total', total.textContent);
			if (shown) {
				stats.hidden = false;
				whenVisible(stats, function () {
					$$('[data-countup]', stats).forEach(function (el) {
						var t = +el.getAttribute('data-target');
						if (t) countUp(el, t);
					});
				});
			}
		}

		/* 떠 있는 카드 스택 */
		var stack = $('.hero__stack', hero);
		if (stack && hasOpt('opt-stack') && window.innerWidth >= 1080) {
			var picks = $$('#feed .card, .covers .card, .covers .slide').filter(function (c) { return $('.card__img, .slide__img', c); }).slice(0, 3);
			if (picks.length >= 2) {
				picks.forEach(function (c) {
					var img = $('.card__img, .slide__img', c);
					var link = $('.card__link, .slide__link', c);
					var title = $('.card__title, .slide__title', c);
					var a = doc.createElement('a');
					a.className = 'stack-card';
					a.href = link ? link.href : '#';
					a.tabIndex = -1;
					a.innerHTML = '<span class="stack-card__inner"><img alt="" decoding="async"><span class="stack-card__title"></span></span>';
					$('img', a).src = img.currentSrc || img.src;
					$('.stack-card__title', a).textContent = title ? title.textContent.trim() : '';
					stack.appendChild(a);
				});
				stack.hidden = false;
			}
		}

		/* 포인터 패럴랙스 */
		if (motionOK && finePointer) {
			var raf = 0;
			hero.addEventListener('pointermove', function (e) {
				if (raf) return;
				raf = requestAnimationFrame(function () {
					raf = 0;
					var r = hero.getBoundingClientRect();
					hero.style.setProperty('--px', ((e.clientX - r.left) / r.width - 0.5).toFixed(3));
					hero.style.setProperty('--py', ((e.clientY - r.top) / r.height - 0.5).toFixed(3));
				});
			});
		}
	});

	/* ---------- 10. 흐르는 태그 띠 ---------- */
	safe(function () {
		var mq = $('.marquee');
		if (!mq || !isIndex || !hasOpt('opt-marquee')) return;
		var pg = (location.search.match(/[?&]page=(\d+)/) || [])[1];
		if (pg && +pg > 1) return;
		var tags = collectTags();
		if (tags.length < 4) return;
		var track = $('.marquee__track', mq);
		var build = function (dup) {
			tags.forEach(function (t) {
				var a = doc.createElement('a');
				a.className = 'marquee__item';
				a.href = t.href;
				a.textContent = t.name;
				a.tabIndex = -1;
				if (dup) a.setAttribute('aria-hidden', 'true');
				track.appendChild(a);
			});
		};
		build(false);
		build(true);
		track.style.setProperty('--marquee-dur', Math.max(32, tags.length * 3.4) + 's');
		mq.hidden = false;
	});

	/* ---------- 11. 방문자 수 표시 ---------- */
	safe(function () {
		$$('.widget--counter [data-count]').forEach(function (el) {
			var n = parseInt(el.textContent.replace(/[^\d]/g, ''), 10);
			if (!isFinite(n)) return;
			el.textContent = n.toLocaleString('ko-KR');
			if (el.getAttribute('data-count') === 'total' && n > 0) whenVisible(el, function () { countUp(el, n); });
		});
	});

	/* ---------- 12. 글 화면: 여백 정리 · 읽기 시간 · 표 · 코드 · 제목 앵커 · 목차 ---------- */
	function slugify(s) {
		return String(s).trim().toLowerCase()
			.replace(/[^\w\uAC00-\uD7A3\u3131-\u318E\s-]/g, '')
			.replace(/\s+/g, '-').replace(/-+/g, '-').slice(0, 60);
	}
	safe(function () {
		if (!isPage) return;
		$$('[data-post-content]').forEach(function (wrap, wrapIndex) {
			var content = $('.contents_style', wrap) || $('.tt_article_useless_p_margin', wrap) || wrap;

			/* 빈 문단(줄바꿈용)을 일정한 간격으로 */
			$$('p', content).forEach(function (p) {
				if (p.querySelector('img, iframe, video, svg, object, embed, input, button, canvas, figure')) return;
				if (!p.textContent.replace(/\u00a0/g, ' ').trim()) p.classList.add('is-spacer');
			});

			/* 예상 읽기 시간 */
			if (hasOpt('opt-reading') && wrapIndex === 0) {
				var text = content.textContent || '';
				var ko = (text.match(/[\uAC00-\uD7A3]/g) || []).length;
				var words = (text.replace(/[\uAC00-\uD7A3]/g, ' ').match(/[A-Za-z0-9]+/g) || []).length;
				var mins = Math.max(1, Math.round(ko / 500 + words / 220 + $$('img', content).length * 0.08));
				$$('[data-reading-time]').forEach(function (el) {
					$('span', el).textContent = mins + '분 읽기';
					el.hidden = false;
				});
			}

			/* 표 가로 스크롤 */
			$$('table', content).forEach(function (t) {
				if (t.closest('.table-scroll, .another_category')) return;
				var w = doc.createElement('div');
				w.className = 'table-scroll';
				t.parentNode.insertBefore(w, t);
				w.appendChild(t);
			});

			/* 코드 복사 버튼 */
			$$('pre', content).forEach(function (pre) {
				if (pre.closest('.code-wrap')) return;
				var w = doc.createElement('div');
				w.className = 'code-wrap';
				pre.parentNode.insertBefore(w, pre);
				w.appendChild(pre);
				var b = doc.createElement('button');
				b.type = 'button';
				b.className = 'code-copy';
				b.innerHTML = icon('copy') + '<span>복사</span>';
				b.addEventListener('click', function () {
					copyText(pre.innerText).then(function () {
						b.lastChild.textContent = '복사됨';
						toast('코드를 복사했어요');
						setTimeout(function () { b.lastChild.textContent = '복사'; }, 1600);
					}, function () {});
				});
				w.appendChild(b);
			});

			/* 제목 앵커 + 목차 */
			var heads = $$('h2, h3, h4', content).filter(function (h) {
				return h.textContent.trim() && !h.closest('.another_category, .container_postbtn, figure, table, blockquote, .toc-inline');
			});
			var labels = heads.map(function (h) { return h.textContent.replace(/\s+/g, ' ').trim(); });
			heads.forEach(function (h, i) {
				if (!h.id) {
					var base = slugify(labels[i]) || 'section';
					var id = base;
					var n = 2;
					while (doc.getElementById(id)) id = base + '-' + n++;
					h.id = id;
				}
				var a = doc.createElement('a');
				a.className = 'heading-anchor';
				a.href = '#' + h.id;
				a.setAttribute('aria-label', '이 섹션 링크 복사');
				a.textContent = '#';
				a.addEventListener('click', function (e) {
					e.preventDefault();
					history.replaceState(null, '', '#' + h.id);
					h.scrollIntoView({ behavior: motionOK ? 'smooth' : 'auto' });
					copyText(location.href).then(function () { toast('섹션 링크를 복사했어요'); }, function () {});
				});
				h.appendChild(a);
			});

			if (hasOpt('opt-toc') && heads.length >= 2 && wrapIndex === 0) {
				var minLv = Math.min.apply(null, heads.map(function (h) { return +h.tagName.charAt(1); }));
				var list = doc.createElement('ol');
				list.className = 'toc__list';
				heads.forEach(function (h, i) {
					var li = doc.createElement('li');
					li.className = 'lv-' + Math.min(4, +h.tagName.charAt(1) - minLv + 2);
					var a = doc.createElement('a');
					a.href = '#' + h.id;
					a.textContent = labels[i];
					li.appendChild(a);
					list.appendChild(li);
				});
				var layout = wrap.closest('.post-layout');
				var rail = layout && $('.post-rail', layout);
				if (rail) {
					var box = doc.createElement('div');
					box.className = 'toc';
					box.innerHTML = '<p class="toc__title">' + icon('toc') + '목차</p>';
					box.appendChild(list);
					rail.appendChild(box);
					var share = doc.createElement('div');
					share.className = 'rail-share';
					share.innerHTML =
						'<button type="button" class="share-btn" data-share-action="copy" aria-label="링크 복사">' + icon('link') + '</button>' +
						(navigator.share ? '<button type="button" class="share-btn" data-share-action="native" aria-label="공유하기">' + icon('share') + '</button>' : '<button type="button" class="share-btn" data-share-action="x" aria-label="X로 공유">' + icon('x') + '</button>') +
						($('#comments') ? '<a class="share-btn" href="#comments" aria-label="댓글로 이동">' + icon('comment') + '</a>' : '');
					rail.appendChild(share);
				}
				var det = doc.createElement('details');
				det.className = 'toc-inline';
				det.innerHTML = '<summary>' + icon('toc') + '<span>목차</span>' + icon('chevron-down', 'toc-inline__chev') + '</summary>';
				det.appendChild(list.cloneNode(true));
				wrap.parentNode.insertBefore(det, wrap);
				tocHeads = heads;
				tocLinks = $$('.toc__list a');
				onScroll();
			}
		});

		/* 카테고리 없음 → 경로 단순화 */
		$$('.breadcrumb').forEach(function (bc) {
			var links = $$('a', bc);
			var cat = links[1];
			if (cat && isUncategorized(cat.textContent)) {
				var sep = cat.previousElementSibling;
				if (sep && sep.tagName.toLowerCase() === 'svg') sep.remove();
				cat.remove();
			}
		});
		$$('.post-hero__cat .chip').forEach(function (c) { if (isUncategorized(c.textContent)) c.classList.add('is-hidden'); });

		/* 주소에 #제목이 있으면 이동 */
		if (location.hash && location.hash.length > 1) {
			var target = null;
			try { target = doc.getElementById(decodeURIComponent(location.hash.slice(1))); } catch (e) { /* noop */ }
			if (target && /^H[2-4]$/.test(target.tagName)) setTimeout(function () { target.scrollIntoView(); }, 60);
		}
	});

	/* ---------- 13. 공유 ---------- */
	safe(function () {
		if (navigator.share) $$('[data-share-action="native"]').forEach(function (b) { b.hidden = false; });
		doc.addEventListener('click', function (e) {
			var b = e.target.closest('[data-share-action]');
			if (!b) return;
			var act = b.getAttribute('data-share-action');
			var canon = $('link[rel="canonical"]');
			var url = (canon && canon.href) || location.href.split('#')[0];
			var titleEl = $('.post-title');
			var title = titleEl ? titleEl.textContent.trim() : doc.title;
			if (act === 'copy') {
				copyText(url).then(function () {
					toast('링크를 복사했어요');
					b.classList.add('is-done');
					setTimeout(function () { b.classList.remove('is-done'); }, 1800);
				}, function () { toast('복사하지 못했어요'); });
				return;
			}
			if (act === 'native') {
				if (navigator.share) navigator.share({ title: title, url: url }).catch(function () {});
				return;
			}
			var map = {
				naver: 'https://share.naver.com/web/shareView?url=' + enc(url) + '&title=' + enc(title),
				facebook: 'https://www.facebook.com/sharer/sharer.php?u=' + enc(url),
				x: 'https://x.com/intent/tweet?url=' + enc(url) + '&text=' + enc(title)
			};
			if (map[act]) window.open(map[act], '_blank', 'noopener,noreferrer,width=640,height=680');
		});
	});

	/* ---------- 14. 더 보기 로딩 ---------- */
	safe(function () {
		if (!hasOpt('opt-loadmore')) return;
		var lm = $('.load-more');
		var feed = $('#feed');
		var nextHref = function (el) {
			if (!el || el.classList.contains('no-more-next')) return null;
			var h = el.getAttribute('href');
			return h && h.charAt(0) !== '#' && !/^javascript:/i.test(h) ? h : null;
		};
		var url = nextHref($('.paging__next'));
		if (!lm || !feed || !url || !$('.card', feed)) return;
		body.classList.add('is-loadmore');
		lm.hidden = false;
		var btn = $('[data-load-more]', lm);
		var busy = false;
		var load = function () {
			if (busy || !url) return;
			busy = true;
			btn.classList.add('is-loading');
			btn.disabled = true;
			fetch(url, { credentials: 'same-origin' })
				.then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); })
				.then(function (html) {
					var d = new DOMParser().parseFromString(html, 'text/html');
					var cards = $$('#feed > .card', d);
					var frag = doc.createDocumentFragment();
					cards.forEach(function (c) { frag.appendChild(doc.importNode(c, true)); });
					feed.appendChild(frag);
					enhanceCards(feed);
					observeReveal(feed);
					url = nextHref(d.querySelector('.paging__next'));
					if (!url || !cards.length) { lm.hidden = true; toast('모든 글을 불러왔어요'); }
				})
				.catch(function () { body.classList.remove('is-loadmore'); lm.hidden = true; })
				.then(function () { busy = false; btn.classList.remove('is-loading'); btn.disabled = false; });
		};
		btn.addEventListener('click', load);
	});

	/* ---------- 15. 커버: 슬라이더 · 캐러셀 ---------- */
	safe(function () {
		$$('[data-slider]').forEach(function (slider) {
			var track = $('.slider__track', slider);
			var slides = $$('.slide', track);
			var ui = $('.slider__ui', slider);
			if (!slides.length) { slider.closest('.cover').hidden = true; return; }
			if (slides.length < 2) { if (ui) ui.hidden = true; slides[0].classList.add('is-active'); return; }
			var DUR = 6000;
			var cur = 0;
			var timer = null;
			var paused = false;
			slider.style.setProperty('--slide-ms', DUR + 'ms');
			var dotsBox = $('.slider__dots', slider);
			var dots = slides.map(function (s, i) {
				var b = doc.createElement('button');
				b.type = 'button';
				b.setAttribute('role', 'tab');
				b.setAttribute('aria-label', (i + 1) + '번째 슬라이드');
				b.addEventListener('click', function () { go(i, true); });
				dotsBox.appendChild(b);
				return b;
			});
			var setActive = function (i, restartDot) {
				cur = i;
				slides.forEach(function (s, k) {
					s.classList.toggle('is-active', k === i);
					$$('a', s).forEach(function (a) { a.tabIndex = k === i ? 0 : -1; });
				});
				dots.forEach(function (d, k) {
					if (k === i && restartDot) { d.removeAttribute('aria-selected'); void d.offsetWidth; }
					d.setAttribute('aria-selected', String(k === i));
				});
			};
			var stop = function () { clearInterval(timer); timer = null; };
			var start = function () {
				stop();
				if (motionOK && !paused) timer = setInterval(function () { go(cur + 1, false); }, DUR);
			};
			var go = function (i, user) {
				i = (i + slides.length) % slides.length;
				track.scrollTo({ left: slides[i].offsetLeft, behavior: motionOK ? 'smooth' : 'auto' });
				setActive(i, true);
				if (user) start();
			};
			var st;
			track.addEventListener('scroll', function () {
				clearTimeout(st);
				st = setTimeout(function () {
					var i = Math.round(track.scrollLeft / Math.max(1, track.clientWidth));
					if (i !== cur && slides[i]) { setActive(i, true); start(); }
				}, 140);
			}, { passive: true });
			$('[data-slider-prev]', slider).addEventListener('click', function () { go(cur - 1, true); });
			$('[data-slider-next]', slider).addEventListener('click', function () { go(cur + 1, true); });
			track.addEventListener('keydown', function (e) {
				if (e.key === 'ArrowLeft') { e.preventDefault(); go(cur - 1, true); }
				if (e.key === 'ArrowRight') { e.preventDefault(); go(cur + 1, true); }
			});
			var pause = function () { paused = true; slider.classList.add('is-paused'); stop(); };
			var resume = function () { paused = false; slider.classList.remove('is-paused'); setActive(cur, true); start(); };
			slider.addEventListener('mouseenter', pause);
			slider.addEventListener('mouseleave', resume);
			slider.addEventListener('focusin', pause);
			slider.addEventListener('focusout', function (e) { if (!slider.contains(e.relatedTarget)) resume(); });
			doc.addEventListener('visibilitychange', function () { doc.hidden ? stop() : (!paused && start()); });
			if (!motionOK) slider.classList.add('is-paused');
			setActive(0, false);
			start();
		});

		$$('.cover--carousel').forEach(function (sec) {
			var c = $('[data-carousel]', sec);
			if (!c) return;
			var step = function () { return Math.max(240, c.clientWidth * 0.8); };
			var prev = $('[data-carousel-prev]', sec);
			var next = $('[data-carousel-next]', sec);
			if (prev) prev.addEventListener('click', function () { c.scrollBy({ left: -step(), behavior: motionOK ? 'smooth' : 'auto' }); });
			if (next) next.addEventListener('click', function () { c.scrollBy({ left: step(), behavior: motionOK ? 'smooth' : 'auto' }); });
		});
	});

	/* ---------- 16. 태그 클라우드 필터 ---------- */
	safe(function () {
		var input = $('[data-tag-filter]');
		if (!input) return;
		var items = $$('.tag-cloud li');
		var empty = $('.tag-cloud__empty');
		input.addEventListener('input', function () {
			var q = input.value.trim().toLowerCase();
			var n = 0;
			items.forEach(function (li) {
				var ok = !q || li.textContent.toLowerCase().indexOf(q) > -1;
				li.hidden = !ok;
				if (ok) n++;
			});
			if (empty) empty.hidden = n > 0;
		});
	});

	root.classList.add('aurora-ready');
})();
