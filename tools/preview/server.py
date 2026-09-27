#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aurora 스킨 로컬 미리보기 서버 (파이썬 표준 라이브러리만 사용)

티스토리 치환자 문법(그룹 치환자 <s_...>, 값 치환자 [##_..._##], 스킨 옵션, 홈 커버)을
샘플 데이터로 해석해서 실제 블로그와 비슷하게 보여 줍니다.

    python3 tools/preview/server.py              # http://localhost:8080
    python3 tools/preview/server.py --port 9000
    python3 tools/preview/server.py --lint       # 모든 화면을 렌더링하고 알 수 없는 치환자를 검사

주소 예시
    /                 홈 (글 목록)          /?cover=1          홈 커버
    /64               글 (목차·댓글 등)      /category/여행      카테고리
    /tag              태그 클라우드          /tag/캐나다 정보     태그 글 목록
    /search/교토       검색 결과              /search/없는글      검색 결과 없음
    /guestbook        방명록                 /notice/1          공지사항
    /99               보호글                 /pages/about       페이지
    ?owner=1          관리자(수정/삭제) 보기   ?var.list-layout=grid   스킨 옵션 바꿔 보기
    ?clean=1          미리보기 도구 막대 숨김
"""
import argparse
import base64
import datetime
import html
import json
import math
import os
import random
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
SKIN_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE_DIR = os.path.join(HERE, ".cache", "tistory-cdn")
sys.path.insert(0, HERE)
import sample_data as D  # noqa: E402

GROUP_RE = re.compile(r"<(/?)s_([A-Za-z0-9_\-]+)([^>]*)>")
VALUE_RE = re.compile(r"\[##_([A-Za-z0-9_\-]+)_##\]")
TISTORY_CSS = ["content.css", "postBtn.css", "another_category.css", "comment.css"]
UNWRAP = {"t3", "search", "sidebar", "sidebar_element"}
TODAY = datetime.date(2026, 9, 27)
WARNINGS = {}


def warn(msg):
    WARNINGS[msg] = WARNINGS.get(msg, 0) + 1


# --------------------------------------------------------------------------- 파서
class Group:
    __slots__ = ("name", "attrs", "children")

    def __init__(self, name, attrs):
        self.name, self.attrs, self.children = name, attrs, []

    def attr(self, key):
        m = re.search(key + r"""\s*=\s*['"]([^'"]*)['"]""", self.attrs or "")
        return m.group(1) if m else None


def parse(src):
    root = Group("#root", "")
    stack, pos = [root], 0
    for m in GROUP_RE.finditer(src):
        if m.start() > pos:
            stack[-1].children.append(src[pos:m.start()])
        closing, name, attrs = m.group(1), m.group(2), m.group(3)
        if closing:
            if stack[-1].name != name:
                idx = next((i for i in range(len(stack) - 1, 0, -1) if stack[i].name == name), None)
                if idx is None:
                    warn("짝이 없는 닫는 태그 </s_%s>" % name)
                    pos = m.end()
                    continue
                warn("</s_%s> 앞에서 닫히지 않은 그룹: %s" % (name, [g.name for g in stack[idx + 1:]]))
                del stack[idx + 1:]
            stack.pop()
        else:
            g = Group(name, attrs)
            stack[-1].children.append(g)
            stack.append(g)
        pos = m.end()
    if pos < len(src):
        stack[-1].children.append(src[pos:])
    if len(stack) > 1:
        warn("닫히지 않은 그룹: %s" % [g.name for g in stack[1:]])
    return root


class Ctx:
    __slots__ = ("data", "parent")

    def __init__(self, data, parent=None):
        self.data, self.parent = data, parent

    def get(self, key, default=None):
        c = self
        while c is not None:
            if key in c.data:
                return c.data[key]
            c = c.parent
        return default

    def child(self, data):
        return Ctx(data, self)


# --------------------------------------------------------------------------- 스킨 정보
def load_skin_info():
    tree = ET.parse(os.path.join(SKIN_DIR, "index.xml"))
    variables = {}
    for v in tree.iter("variable"):
        name = (v.findtext("name") or "").strip()
        variables[name] = {"type": (v.findtext("type") or "").strip().upper(), "default": (v.findtext("default") or "").strip()}
    defaults = {}
    d = tree.find("default")
    if d is not None:
        for child in d:
            defaults[child.tag] = (child.text or "").strip()
    return variables, defaults


# --------------------------------------------------------------------------- 날짜 · 링크 도우미
def dt(t):
    return datetime.datetime(*t)


def tistory_date(t):  # 2026. 9. 18. 08:30
    d = dt(t)
    return "%d. %d. %d. %02d:%02d" % (d.year, d.month, d.day, d.hour, d.minute)


def tistory_simple(t):  # 2026. 9. 18.
    d = dt(t)
    return "%d. %d. %d." % (d.year, d.month, d.day)


def dotted(t, time=False):  # 2026.09.18 (08:30)
    d = dt(t)
    s = "%d.%02d.%02d" % (d.year, d.month, d.day)
    return s + (" %02d:%02d" % (d.hour, d.minute) if time else "")


def q(s):
    return urllib.parse.quote(s)


def cat_path(name):
    for c in D.CATEGORIES:
        if c["name"] == name:
            return "/category/" + q(name)
        for s in c["subs"]:
            if s["name"] == name:
                return "/category/" + q(c["name"]) + "/" + q(name)
    return "/category"


def cat_label(name):
    for c in D.CATEGORIES:
        for s in c["subs"]:
            if s["name"] == name:
                return c["name"] + "/" + name
    return name or "카테고리 없음"


def post_by_id(pid):
    return next((p for p in D.POSTS if p["id"] == pid), None)


# --------------------------------------------------------------------------- 티스토리가 만들어 주는 HTML 흉내
def blog_menu_html():
    return ('<ul><li class="t_menu_home first"><a href="/" target="">홈</a></li>'
            '<li class="t_menu_tag"><a href="/tag" target="">태그</a></li>'
            '<li class="t_menu_guestbook last"><a href="/guestbook" target="">방명록</a></li></ul>')


def category_list_html():
    items = []
    for c in D.CATEGORIES:
        subs = ""
        if c["subs"]:
            subs = '<ul class="sub_category_list">' + "".join(
                '<li class=""><a href="%s" class="link_sub_item">%s <span class="c_cnt">(%d)</span></a></li>' % (cat_path(s["name"]), s["name"], s["count"])
                for s in c["subs"]) + "</ul>"
        new_icon = ' <img alt="N" src="/_preview/assets/new.svg" style="vertical-align:middle;padding-left:2px;">' if c["name"] == "쇼핑 가이드" else ""
        items.append('<li class=""><a href="%s" class="link_item">%s <span class="c_cnt">(%d)</span>%s</a>%s</li>' % (cat_path(c["name"]), c["name"], c["count"], new_icon, subs))
    return ('<ul class="tt_category"><li class=""><a href="/category" class="link_tit">분류 전체보기 <span class="c_cnt">(%d)</span></a>'
            '<ul class="category_list">%s</ul></li></ul>' % (D.BLOG["post_total"], "".join(items)))


def calendar_html():
    y, m = TODAY.year, TODAY.month
    post_days = {dt(p["date"]).day for p in D.POSTS if dt(p["date"]).year == y and dt(p["date"]).month == m}
    rows, week = [], []
    first_wd = (datetime.date(y, m, 1).weekday() + 1) % 7  # 일요일 시작
    week = ['<td class="cal_day1 cal_day2"></td>'] * first_wd
    days = (datetime.date(y + (m == 12), m % 12 + 1, 1) - datetime.timedelta(days=1)).day
    for day in range(1, days + 1):
        wd = (first_wd + day - 1) % 7
        cls = "cal_day cal_day3" + (" cal_day_sunday" if wd == 0 else "") + (" cal_day4" if day == TODAY.day else "")
        inner = '<a class="cal_click" href="/archive/%d%02d%02d">%d</a>' % (y, m, day, day) if day in post_days else str(day)
        week.append('<td class="%s">%s</td>' % (cls, inner))
        if len(week) == 7:
            rows.append('<tr class="cal_week">' + "".join(week) + "</tr>")
            week = []
    if week:
        rows.append('<tr class="cal_week">' + "".join(week + ['<td class="cal_day1 cal_day2"></td>'] * (7 - len(week))) + "</tr>")
    heads = "".join('<th class="cal_week%d">%s</th>' % (2 if i == 0 else 1, d) for i, d in enumerate("일월화수목금토"))
    return ('<table class="tt-calendar" cellpadding="0" cellspacing="1" style="width: 100%%; table-layout: fixed">'
            '<caption class="cal_month"><a href="/archive/%d%02d" title="1개월 앞의 달력을 보여줍니다.">«</a> &nbsp; '
            '<a href="/archive/%d%02d" title="현재 달의 달력을 보여줍니다.">%d/%02d</a> &nbsp; <a href="/archive/%d%02d" title="1개월 뒤의 달력을 보여줍니다.">»</a></caption>'
            '<thead><tr>%s</tr></thead><tbody>%s</tbody></table>'
            % (y, m - 1, y, m, y, m, y, m + 1, heads, "".join(rows)))


def article_desc(p):
    if p["id"] == 64:
        body = D.ARTICLE_HTML
    else:
        img = ('<figure class="imageblock alignCenter" data-origin-width="1024" data-origin-height="640"><span data-lightbox="lightbox">'
               '<img src="%s" data-origin-width="1024" data-origin-height="640" /></span></figure>' % p["thumb"]) if p["thumb"] else ""
        body = ('<p data-ke-size="size16">%s</p><p data-ke-size="size16">&nbsp;</p>%s'
                '<h2 data-ke-size="size26">한눈에 보는 핵심 정리</h2><p data-ke-size="size16">미리보기용 예시 문단입니다. 실제 블로그에서는 작성하신 본문이 이 자리에 이 디자인으로 표시됩니다.</p>'
                '<h2 data-ke-size="size26">자세히 알아보기</h2><p data-ke-size="size16">목차는 본문의 제목(H2~H4)을 읽어서 자동으로 만들어집니다.</p>'
                '<ul data-ke-list-type="disc"><li>체크 포인트 하나</li><li>체크 포인트 둘</li></ul>' % (html.escape(p["summary"]), img))
    return ('<div class="tt_article_useless_p_margin contents_style">%s</div>%s%s'
            % (body, D.POST_BUTTONS_HTML, D.ANOTHER_CATEGORY_HTML if p["category"] else ""))


SEARCH_JS = ("try { window.location.href = '/search' + '/' + encodeURIComponent(document.getElementsByName('search')[0].value); "
             "document.getElementsByName('search')[0].value = ''; return false; } catch (e) {}")


# --------------------------------------------------------------------------- 렌더러
class Renderer:
    def __init__(self, page, variables, defaults, owner=False, overrides=None):
        self.page, self.variables, self.defaults, self.owner = page, variables, defaults, owner
        self.overrides = overrides or {}

    # 스킨 옵션 ---------------------------------------------------------------
    def var(self, name):
        if name in self.overrides:
            return self.overrides[name]
        v = self.variables.get(name)
        if v is None:
            warn("index.xml에 없는 스킨 옵션: %s" % name)
            return ""
        return v["default"]

    def var_true(self, name):
        val = self.var(name)
        v = self.variables.get(name, {})
        if v.get("type") == "BOOL":
            return val.lower() == "true"
        return bool(val.strip())

    # 값 치환자 ----------------------------------------------------------------
    def value(self, name, ctx):
        if name.startswith("var_"):
            return self.var(name[4:])
        val = ctx.get(name)
        if val is None:
            warn("알 수 없는 값 치환자 [##_%s_##]" % name)
            return ""
        return str(val)

    def render(self, nodes, ctx):
        out = []
        for n in nodes:
            if isinstance(n, str):
                out.append(VALUE_RE.sub(lambda m: self.value(m.group(1), ctx), n))
            else:
                out.append(self.group(n, ctx))
        return "".join(out)

    def group(self, g, ctx):
        n = g.name
        if n.startswith("if_var_"):
            return self.render(g.children, ctx) if self.var_true(n[7:]) else ""
        if n.startswith("not_var_"):
            return "" if self.var_true(n[8:]) else self.render(g.children, ctx)
        if n in UNWRAP:
            return self.render(g.children, ctx)
        h = getattr(self, "g_" + n, None)
        if h is None:
            warn("알 수 없는 그룹 치환자 <s_%s>" % n)
            return self.render(g.children, ctx)
        return h(g, ctx)

    def when(self, cond, g, ctx, data=None):
        if not cond:
            return ""
        return self.render(g.children, ctx.child(data) if data else ctx)

    def loop(self, items, g, ctx, bind):
        return "".join(self.render(g.children, ctx.child(bind(it, i))) for i, it in enumerate(items))

    # 페이지 구조 ---------------------------------------------------------------
    def g_ad_div(self, g, ctx):
        return self.when(self.owner, g, ctx)

    def g_list(self, g, ctx):
        return self.when(self.page.get("list") is not None, g, ctx)

    def g_list_empty(self, g, ctx):
        return self.when(not self.page["articles"] and not self.page["protected"], g, ctx)

    def g_list_image(self, g, ctx):
        return ""

    def g_list_rep(self, g, ctx):
        return ""

    def g_index_article_rep(self, g, ctx):
        return self.when(ctx.get("_mode") == "index", g, ctx)

    def g_permalink_article_rep(self, g, ctx):
        return self.when(ctx.get("_mode") == "permalink", g, ctx)

    def g_article_rep(self, g, ctx):
        p = self.page
        if p["type"] == "permalink":
            return self.render(g.children, ctx.child(article_ctx(p["article"], "permalink")))
        return self.loop(p["articles"], g, ctx, lambda a, i: article_ctx(a, "index"))

    def g_article_protected(self, g, ctx):
        p = self.page
        if p["type"] == "protected":
            return self.render(g.children, ctx.child(article_ctx(p["article"], "permalink")))
        return self.loop(p["protected"], g, ctx, lambda a, i: article_ctx(a, "index"))

    def g_notice_rep(self, g, ctx):
        p = self.page
        if p["type"] == "notice":
            return self.render(g.children, ctx.child(notice_ctx(p["article"], "permalink")))
        return self.loop(p.get("notices", []), g, ctx, lambda a, i: notice_ctx(a, "index"))

    def g_page_rep(self, g, ctx):
        p = self.page
        return self.when(p["type"] == "page", g, ctx, article_ctx(p["article"], "permalink") if p["type"] == "page" else None)

    def g_article_rep_thumbnail(self, g, ctx):
        return self.when(ctx.get("_thumb"), g, ctx)

    def g_notice_rep_thumbnail(self, g, ctx):
        return self.when(ctx.get("_thumb"), g, ctx)

    def g_rp_count(self, g, ctx):
        return self.render(g.children, ctx)

    def g_tag_label(self, g, ctx):
        return self.when(ctx.get("_tags"), g, ctx)

    def g_rp(self, g, ctx):
        return self.when(ctx.get("_mode") == "permalink", g, ctx)

    def g_article_related(self, g, ctx):
        return self.when(ctx.get("_mode") == "permalink" and ctx.get("_related"), g, ctx)

    def g_article_related_rep(self, g, ctx):
        def bind(r, i):
            return {"article_related_rep_type": "thumb_type" if r["thumb"] else "text_type",
                    "article_related_rep_link": "/%d" % r["id"], "article_related_rep_title": html.escape(r["title"]),
                    "article_related_rep_date": dotted(r["date"]), "article_related_rep_thumbnail_link": r["thumb"] or "", "_rthumb": bool(r["thumb"])}
        return self.loop(ctx.get("_related") or [], g, ctx, bind)

    def g_article_related_rep_thumbnail(self, g, ctx):
        return self.when(ctx.get("_rthumb"), g, ctx)

    def _nav(self, g, ctx, key, prefix):
        a = ctx.get(key)
        if not a:
            return ""
        return self.render(g.children, ctx.child({
            prefix + "_type": "thumb_type" if a["thumb"] else "text_type", prefix + "_link": "/%d" % a["id"],
            prefix + "_title": html.escape(a["title"]), prefix + "_date": dotted(a["date"]), prefix + "_thumbnail_link": a["thumb"] or "",
            "_navthumb": bool(a["thumb"])}))

    def g_article_prev(self, g, ctx):
        return self._nav(g, ctx, "_prev", "article_prev")

    def g_article_next(self, g, ctx):
        return self._nav(g, ctx, "_next", "article_next")

    def g_article_prev_thumbnail(self, g, ctx):
        return self.when(ctx.get("_navthumb"), g, ctx)

    g_article_next_thumbnail = g_article_prev_thumbnail

    def g_paging(self, g, ctx):
        pg = self.page.get("paging")
        return self.when(pg is not None, g, ctx, pg and pg["values"])

    def g_paging_rep(self, g, ctx):
        return self.loop(self.page["paging"]["items"], g, ctx, lambda it, i: it)

    def g_tag(self, g, ctx):
        return self.when(self.page["type"] == "tag_cloud", g, ctx)

    def g_tag_rep(self, g, ctx):
        tags = sorted(D.TAGS, key=lambda t: t[0])
        return self.loop(tags, g, ctx, lambda t, i: {"tag_link": "/tag/" + q(t[0]), "tag_class": "cloud%d" % t[1], "tag_name": html.escape(t[0])})

    def g_guest(self, g, ctx):
        return self.when(self.page["type"] == "guestbook", g, ctx)

    # 사이드바 ----------------------------------------------------------------
    def _rctps(self, posts, g, ctx):
        def bind(p, i):
            return {"rctps_rep_link": "/%d" % p["id"], "rctps_rep_title": html.escape(p["title"]), "rctps_rep_rp_cnt": p["comments"],
                    "rctps_rep_author": D.BLOG["blogger"], "rctps_rep_date": dotted(p["date"], True), "rctps_rep_simple_date": dotted(p["date"]),
                    "rctps_rep_thumbnail": p["thumb"] or "", "rctps_rep_category": cat_label(p["category"]), "rctps_rep_category_link": cat_path(p["category"]),
                    "_pthumb": bool(p["thumb"])}
        return self.loop(posts, g, ctx, bind)

    def g_rctps_popular_rep(self, g, ctx):
        return self._rctps(sorted(D.POSTS, key=lambda p: -p["comments"])[:5], g, ctx)

    def g_rctps_rep(self, g, ctx):
        return self._rctps(D.POSTS[:5], g, ctx)

    def g_rctps_rep_thumbnail(self, g, ctx):
        return self.when(ctx.get("_pthumb"), g, ctx)

    def g_rct_notice(self, g, ctx):
        return self.when(bool(D.NOTICES), g, ctx)

    def g_rct_notice_rep(self, g, ctx):
        return self.loop(D.NOTICES, g, ctx, lambda n, i: {"notice_rep_link": "/notice/%d" % n["id"], "notice_rep_title": html.escape(n["title"])})

    def g_rctrp_rep(self, g, ctx):
        return self.loop(D.RECENT_COMMENTS, g, ctx, lambda c, i: {
            "rctrp_rep_link": "/%d#comment%d" % (c["post"], 1000 + i), "rctrp_rep_desc": html.escape(c["desc"]),
            "rctrp_rep_name": html.escape(c["name"]), "rctrp_rep_time": c["time"]})

    def g_random_tags(self, g, ctx):
        tags = D.TAGS[:]
        random.Random(7).shuffle(tags)
        return self.loop(tags[:18], g, ctx, lambda t, i: {"tag_link": "/tag/" + q(t[0]), "tag_class": "cloud%d" % t[1], "tag_name": html.escape(t[0])})

    def g_archive_rep(self, g, ctx):
        return self.loop(D.ARCHIVES, g, ctx, lambda a, i: {"archive_rep_link": "/archive/" + a[1], "archive_rep_date": a[0], "archive_rep_count": a[2]})

    def g_link_rep(self, g, ctx):
        return self.loop(D.LINKS, g, ctx, lambda l, i: {"link_url": l["url"], "link_site": html.escape(l["site"])})

    # 홈 커버 ------------------------------------------------------------------
    def g_cover_group(self, g, ctx):
        return self.when(self.page.get("cover"), g, ctx)

    def g_cover_rep(self, g, ctx):
        return self.loop(cover_data(), g, ctx, lambda c, i: {"_cover": c, "cover_title": html.escape(c["title"]), "cover_url": c["url"]})

    def g_cover(self, g, ctx):
        c = ctx.get("_cover")
        return self.when(c and c["name"] == g.attr("name"), g, ctx)

    def g_cover_url(self, g, ctx):
        c = ctx.get("_cover")
        return self.when(c and c["url"], g, ctx)

    def g_cover_item(self, g, ctx):
        c = ctx.get("_cover")
        return self.loop(c["items"] if c else [], g, ctx, cover_item_ctx)

    def g_cover_item_article_info(self, g, ctx):
        return self.when(ctx.get("_kind") == "article", g, ctx)

    def g_cover_item_not_article_info(self, g, ctx):
        return self.when(ctx.get("_kind") != "article", g, ctx)

    def g_cover_item_thumbnail(self, g, ctx):
        return self.when(ctx.get("cover_item_thumbnail"), g, ctx)


def article_ctx(a, mode):
    d = dt(a["date"])
    ctx = {
        "_mode": mode, "_thumb": bool(a.get("thumb")), "_tags": bool(a.get("tags")),
        "article_rep_id": a["id"], "article_rep_link": "/%d" % a["id"],
        "article_rep_title": html.escape(a["title"]), "article_rep_title_text": html.escape(a["title"]),
        "article_rep_category": html.escape(cat_label(a.get("category", ""))), "article_rep_category_link": cat_path(a.get("category", "")),
        "article_rep_date": tistory_date(a["date"]), "article_rep_simple_date": tistory_simple(a["date"]),
        "article_rep_date_year": d.year, "article_rep_date_month": "%02d" % d.month, "article_rep_date_day": "%02d" % d.day,
        "article_rep_date_hour": "%02d" % d.hour, "article_rep_date_minute": "%02d" % d.minute, "article_rep_date_second": "00",
        "article_rep_author": D.BLOG["blogger"], "article_rep_summary": html.escape(a.get("summary", "")),
        "article_rep_thumbnail_raw_url": a.get("thumb") or "", "article_rep_thumbnail_url": a.get("thumb") or "",
        "article_rep_rp_link": "", "article_rep_rp_cnt": a.get("comments", 0),
        "tag_label_rep": ", ".join('<a href="/tag/%s" rel="tag">%s</a>' % (q(t), html.escape(t)) for t in a.get("tags", [])),
        "s_ad_m_link": "/manage/newpost/%d" % a["id"], "s_ad_m_onclick": "return false", "s_ad_s1_label": "공개",
        "s_ad_s2_onclick": "alert('미리보기: 공개 상태 변경'); return false", "s_ad_s2_label": "비공개",
        "s_ad_t_onclick": "return false", "s_ad_d_onclick": "alert('미리보기: 삭제'); return false",
        "article_password": "entry%dpassword" % a["id"], "article_dissolve": "alert('미리보기: 비밀번호 확인')",
    }
    if mode == "permalink":
        ctx["article_rep_desc"] = article_desc(a) if a.get("id") != 1000 else a.get("desc", "")
        ctx["comment_group"] = D.comment_html(a.get("comments", 0))
        same = [p for p in D.POSTS if p["id"] != a["id"] and p.get("category") and a.get("category")
                and (p["category"] == a["category"] or cat_path(p["category"]).startswith(cat_path(a["category"]).rsplit("/", 1)[0] + "/"))]
        ctx["_related"] = same[:4] if a.get("category") else []
        ids = [p["id"] for p in D.POSTS]
        if a["id"] in ids:
            i = ids.index(a["id"])
            ctx["_prev"] = D.POSTS[i + 1] if i + 1 < len(D.POSTS) else None
            ctx["_next"] = D.POSTS[i - 1] if i > 0 else None
    return ctx


def notice_ctx(n, mode):
    d = dt(n["date"])
    return {
        "_mode": mode, "_thumb": bool(n.get("thumb")),
        "notice_rep_link": "/notice/%d" % n["id"], "notice_rep_title": html.escape(n["title"]),
        "notice_rep_date": tistory_date(n["date"]), "notice_rep_simple_date": tistory_simple(n["date"]),
        "notice_rep_date_year": d.year, "notice_rep_date_month": "%02d" % d.month, "notice_rep_date_day": "%02d" % d.day,
        "notice_rep_date_hour": "%02d" % d.hour, "notice_rep_date_minute": "%02d" % d.minute, "notice_rep_date_second": "00",
        "notice_rep_author": D.BLOG["blogger"], "notice_rep_summary": html.escape(n["summary"]),
        "notice_rep_desc": '<div class="tt_article_useless_p_margin contents_style"><p data-ke-size="size16">%s</p>'
                           '<h2 data-ke-size="size26">무엇이 달라졌나요?</h2><ul data-ke-list-type="disc"><li>다크 모드와 자동 목차</li><li>Ctrl+K 빠른 검색</li><li>모바일 최적화</li></ul>'
                           '<h2 data-ke-size="size26">앞으로도 잘 부탁드려요</h2><p data-ke-size="size16">감사합니다.</p></div>' % html.escape(n["summary"]),
        "notice_rep_thumbnail_raw_url": n.get("thumb") or "", "notice_rep_thumbnail_url": n.get("thumb") or "",
        "s_ad_m_link": "/manage/notice/%d" % n["id"], "s_ad_d_onclick": "return false",
    }


def cover_item_ctx(it, i):
    if it.get("kind") == "custom":
        return {"_kind": "custom", "cover_item_title": html.escape(it["title"]), "cover_item_summary": html.escape(it["summary"]),
                "cover_item_url": it["url"], "cover_item_thumbnail": it.get("thumb") or ""}
    p = it
    return {"_kind": "article", "cover_item_title": html.escape(p["title"]), "cover_item_summary": html.escape(p["summary"]),
            "cover_item_url": "/%d" % p["id"], "cover_item_thumbnail": p["thumb"] or "",
            "cover_item_category": html.escape(cat_label(p["category"])), "cover_item_category_url": cat_path(p["category"]),
            "cover_item_date": dotted(p["date"], True), "cover_item_simple_date": dotted(p["date"]), "cover_item_comment_count": p["comments"]}


def cover_data():
    with_thumb = [p for p in D.POSTS if p["thumb"]]
    return [
        {"name": "slider", "title": "", "url": "", "items": with_thumb[:5]},
        {"name": "grid", "title": "최신 글", "url": "/category", "items": D.POSTS[:6]},
        {"name": "banner", "title": "Guestbook", "url": "", "items": [{"kind": "custom", "title": "여행 이야기를 들려주세요", "summary": "가 보고 싶은 곳, 궁금한 정보가 있다면 방명록에 남겨 주세요. 다음 글의 주제가 될지도 몰라요!", "url": "/guestbook", "thumb": D.IMG + "canada.jpg"}]},
        {"name": "carousel", "title": "놓치면 아쉬운 인기 글", "url": "", "items": sorted(D.POSTS, key=lambda p: -p["comments"])[:8]},
        {"name": "list", "title": "생활 정보", "url": "/category/" + q("생활 정보"), "items": [p for p in D.POSTS if p["category"] in ("생활 정보", "")][:4]},
    ]


# --------------------------------------------------------------------------- 라우팅
def paging(base, cur, total_pages, sep="?"):
    def link(n):
        return 'href="%s%spage=%d"' % (base, sep, n)
    items = []
    nums = list(range(1, min(total_pages, 5) + 1))
    for n in nums:
        items.append({"paging_rep_link": link(n), "paging_rep_link_num": '<span class="%s">%d</span>' % ("selected" if n == cur else "", n)})
    if total_pages > 6:
        items.append({"paging_rep_link": "", "paging_rep_link_num": '<span class="interword">···</span>'})
    if total_pages > 5:
        items.append({"paging_rep_link": link(total_pages), "paging_rep_link_num": '<span class="%s">%d</span>' % ("selected" if total_pages == cur else "", total_pages)})
    return {"items": items, "values": {
        "prev_page": link(cur - 1) if cur > 1 else 'href="#none"', "no_more_prev": "" if cur > 1 else "no-more-prev",
        "next_page": link(cur + 1) if cur < total_pages else 'href="#none"', "no_more_next": "" if cur < total_pages else "no-more-next"}}


def list_page(page, posts, pg, conform, count, desc, base, per_page):
    total_pages = max(1, math.ceil(count / per_page))
    pool = [p for p in posts if not p.get("protected")]
    if pool:
        start = ((pg - 1) * per_page) % len(pool)
        take = min(per_page, len(pool)) if count > len(pool) else len(pool)
        rotated = (pool[start:] + pool[:start])[:take] if pg > 1 else pool[:per_page]
    else:
        rotated = []
    page["articles"] = rotated
    page["list"] = {"list_conform": html.escape(conform), "list_count": count, "list_description": html.escape(desc), "list_style": ""}
    page["paging"] = paging(base, pg, total_pages) if rotated else None


def build_page(path, query, per_page):
    p = urllib.parse.unquote(path).rstrip("/") or "/"
    pg = int(query.get("page", "1") or 1) if (query.get("page", "1") or "1").isdigit() else 1
    page = {"type": None, "body_id": "tt-body-index", "articles": [], "protected": [], "notices": [], "article": None,
            "list": None, "paging": None, "cover": False, "title": D.BLOG["title"], "search": ""}

    def cat_posts(name):
        return [x for x in D.POSTS if x["category"] == name or cat_path(x["category"]).startswith(cat_path(name) + "/")]

    if p == "/":
        page.update(type="index", body_id="tt-body-index", cover=query.get("cover") == "1")
        if not page["cover"]:
            list_page(page, D.POSTS, pg, "전체 글", D.BLOG["post_total"], D.BLOG["desc"], "/", per_page)
    elif p == "/category" or p.startswith("/category/"):
        name = p.split("/")[-1] if p.startswith("/category/") else ""
        posts = cat_posts(name) if name else D.POSTS
        cnt = next((c["count"] for c in D.CATEGORIES if c["name"] == name), None) or next((s["count"] for c in D.CATEGORIES for s in c["subs"] if s["name"] == name), None) or (len(posts) if name else D.BLOG["post_total"])
        page.update(type="category", body_id="tt-body-category", title=name or "분류 전체보기")
        list_page(page, posts, pg, cat_label(name) if name else "분류 전체보기", cnt, "%s 관련 글을 모았습니다." % (name or "전체"), p, per_page)
    elif p == "/tag":
        page.update(type="tag_cloud", body_id="tt-body-tag", title="태그")
    elif p.startswith("/tag/"):
        name = p[5:]
        posts = [x for x in D.POSTS if name in x.get("tags", [])]
        page.update(type="tag", body_id="tt-body-tag", title=name)
        list_page(page, posts, pg, name, len(posts), D.BLOG["desc"], p, per_page)
    elif p.startswith("/search/"):
        kw = p[8:]
        posts = [x for x in D.POSTS if kw.lower() in (x["title"] + " " + " ".join(x.get("tags", [])) + " " + x["summary"]).lower()]
        page.update(type="search", body_id="tt-body-search", title=kw, search=kw)
        list_page(page, posts, pg, kw, len(posts), D.BLOG["desc"], p, per_page)
    elif p.startswith("/archive/"):
        ym = p[9:]
        posts = [x for x in D.POSTS if ("%d%02d" % dt(x["date"]).timetuple()[:2]).startswith(ym[:6])]
        page.update(type="archive", body_id="tt-body-archive", title=ym)
        list_page(page, posts, pg, "%s/%s" % (ym[:4], ym[4:6]), len(posts), D.BLOG["desc"], p, per_page)
    elif p == "/guestbook":
        page.update(type="guestbook", body_id="tt-body-guestbook", title="방명록")
    elif p == "/notice":
        page.update(type="notice_list", body_id="tt-body-category", title="공지사항", notices=D.NOTICES)
        page["list"] = {"list_conform": "공지사항", "list_count": len(D.NOTICES), "list_description": "", "list_style": ""}
    elif p.startswith("/notice/"):
        n = next((x for x in D.NOTICES if str(x["id"]) == p[8:]), D.NOTICES[0])
        page.update(type="notice", body_id="tt-body-page", title=n["title"], article=n)
    elif p == "/99":
        a = {"id": 99, "title": "우리 가족 여행 사진 모음 (가족만 보기)", "category": "여행", "date": (2026, 9, 1, 20, 0), "thumb": None, "comments": 0, "summary": "", "tags": []}
        page.update(type="protected", body_id="tt-body-page", title=a["title"], article=a)
    elif p == "/pages/about":
        a = {"id": 1000, "title": "블로그 소개", "category": "", "date": (2026, 1, 1, 0, 0), "thumb": None, "comments": 0, "summary": "", "tags": [],
             "desc": '<div class="tt_article_useless_p_margin contents_style"><p data-ke-size="size16">안녕하세요, 가볼만한 곳입니다. 여행지와 생활 정보를 쉽고 정확하게 전하려고 노력합니다.</p></div>'}
        page.update(type="page", body_id="tt-body-page", title=a["title"], article=a)
    elif re.fullmatch(r"/\d+", p) and post_by_id(int(p[1:])):
        a = post_by_id(int(p[1:]))
        page.update(type="permalink", body_id="tt-body-page", title=a["title"], article=a)
        page["paging"] = paging("/", 1, 1)
    else:
        return None
    return page


def global_ctx(page):
    return Ctx({
        "title": html.escape(D.BLOG["title"]), "blogger": html.escape(D.BLOG["blogger"]), "desc": html.escape(D.BLOG["desc"]),
        "image": D.BLOG["image"], "blog_image": '<img src="%s" alt="">' % D.BLOG["image"], "blog_link": "/",
        "rss_url": "/rss", "taglog_link": "/tag", "guestbook_link": "/guestbook", "owner_url": "/manage",
        "page_title": html.escape(page["title"]), "body_id": page["body_id"], "blog_menu": blog_menu_html(),
        "category_list": category_list_html(), "category": category_list_html(),
        "revenue_list_upper": "", "revenue_list_lower": "",
        "search_name": "search", "search_text": html.escape(page.get("search", "")), "search_onclick_submit": SEARCH_JS,
        "count_total": D.BLOG["count_total"], "count_today": D.BLOG["count_today"], "count_yesterday": D.BLOG["count_yesterday"],
        "calendar": calendar_html(), "guestbook_group": D.comment_html(12, guestbook=True),
        **(page["list"] or {}),
    })


# --------------------------------------------------------------------------- 후처리
PREVIEW_BAR = """
<details id="aurora-preview-bar" style="position:fixed;left:14px;bottom:14px;z-index:2147483000;font:600 13px/1.4 system-ui,sans-serif;color:#fff;background:rgba(12,14,24,.88);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.14);border-radius:14px;box-shadow:0 12px 30px rgba(0,0,0,.3);max-width:calc(100vw - 90px)">
<summary style="cursor:pointer;padding:9px 14px;list-style:none;white-space:nowrap">✦ 미리보기 화면 선택</summary>
<nav style="display:flex;flex-wrap:wrap;gap:6px;padding:4px 12px 12px">
%s
</nav></details>
"""


def preview_bar(path_qs):
    links = [("/", "홈"), ("/?cover=1", "홈 커버"), ("/64", "글"), ("/category/" + q("여행"), "카테고리"), ("/tag", "태그"),
             ("/search/" + q("교토"), "검색"), ("/search/" + q("없는검색어"), "검색 결과 없음"), ("/guestbook", "방명록"),
             ("/notice/1", "공지"), ("/99", "보호글"), ("/?var.list-layout=grid", "그리드 목록"), ("/?var.list-layout=list", "리스트 목록"),
             ("/64?owner=1", "관리자 보기")]
    a = "".join('<a href="%s" style="color:#fff;text-decoration:none;padding:5px 10px;border-radius:9px;background:rgba(255,255,255,.1)">%s</a>' % (h, t) for h, t in links)
    return PREVIEW_BAR % a


def postprocess(out, clean=False, version="0"):
    out = re.sub(r"https://i1\.daumcdn\.net/thumb/[^?\"'\s]+/\?fname=(/_preview/[^\"'\s,)]+)", r"\1", out)
    out = re.sub(r'<script async src="https://www\.googletagmanager\.com/gtag/js\?id=[^"]+"></script>\s*<script>[\s\S]*?</script>',
                 "<!-- [미리보기] Google Analytics 비활성화 -->", out, count=1)
    out = re.sub(r'<script async src="https://pagead2\.googlesyndication\.com/[^"]+"\s*crossorigin="anonymous"></script>',
                 "<!-- [미리보기] AdSense 비활성화 -->", out)
    cdn = "".join('<link rel="stylesheet" href="/_preview/tistory/%s">' % f for f in TISTORY_CSS if os.path.exists(os.path.join(CACHE_DIR, f)))
    out = out.replace('<link rel="stylesheet" href="./style.css">', cdn + '<link rel="stylesheet" href="/style.css?v=%s">' % version)
    out = out.replace('src="./images/aurora.js"', 'src="/images/aurora.js?v=%s"' % version)
    out = out.replace('"./images/', '"/images/')
    if not clean:
        out = out.replace("</body>", preview_bar("") + "</body>")
    return out


def ensure_tistory_css():
    """티스토리가 블로그에 자동으로 넣는 CSS를 흉내 내기 위해 캐시합니다 (MIT 라이선스 torytis 저장소 사본)."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    for f in TISTORY_CSS:
        dest = os.path.join(CACHE_DIR, f)
        if os.path.exists(dest):
            continue
        local = os.path.join("/tmp/torytis/src/packages/torytis/static/tistory-cdn", f)
        try:
            if os.path.exists(local):
                data = open(local, "rb").read()
            else:
                url = "https://api.github.com/repos/wisdomstar94/torytis/contents/src/packages/torytis/static/tistory-cdn/" + f
                with urllib.request.urlopen(url, timeout=10) as r:
                    data = base64.b64decode(json.loads(r.read().decode())["content"])
            open(dest, "wb").write(data)
        except Exception as e:  # 오프라인이면 없이 진행
            print("  (티스토리 기본 CSS %s 없이 진행: %s)" % (f, e))


# --------------------------------------------------------------------------- HTTP 서버
class App:
    def __init__(self):
        self.reload()

    def reload(self):
        src = open(os.path.join(SKIN_DIR, "skin.html"), encoding="utf-8").read()
        self.tree = parse(src)
        self.variables, self.defaults = load_skin_info()
        self.per_page = int(self.defaults.get("entriesOnPage", "9") or 9)
        self.version = str(int(max(os.path.getmtime(os.path.join(SKIN_DIR, f)) for f in ("skin.html", "style.css", "images/aurora.js"))))

    def render(self, path, query):
        self.reload()
        page = build_page(path, query, self.per_page)
        if page is None:
            return None
        overrides = {k[4:]: v for k, v in query.items() if k.startswith("var.")}
        r = Renderer(page, self.variables, self.defaults, owner=query.get("owner") == "1", overrides=overrides)
        out = r.render(self.tree.children, global_ctx(page))
        return postprocess(out, clean=query.get("clean") == "1", version=self.version)


APP = None
MIME = {".css": "text/css; charset=utf-8", ".js": "application/javascript; charset=utf-8", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".svg": "image/svg+xml", ".gif": "image/gif", ".webp": "image/webp", ".html": "text/html; charset=utf-8"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("  %s\n" % (fmt % args))

    def send(self, code, body, ctype="text/html; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def static(self, base, rel):
        full = os.path.abspath(os.path.join(base, rel))
        if not full.startswith(os.path.abspath(base)) or not os.path.isfile(full):
            return self.send(404, "not found", "text/plain; charset=utf-8")
        ext = os.path.splitext(full)[1].lower()
        with open(full, "rb") as fh:
            self.send(200, fh.read(), MIME.get(ext, "application/octet-stream"))

    def do_GET(self):
        u = urllib.parse.urlsplit(self.path)
        path = u.path
        query = dict(urllib.parse.parse_qsl(u.query, keep_blank_values=True))
        if path == "/style.css":
            return self.static(SKIN_DIR, "style.css")
        if path.startswith("/images/"):
            return self.static(os.path.join(SKIN_DIR, "images"), urllib.parse.unquote(path[8:]))
        if path.startswith("/_preview/assets/"):
            return self.static(os.path.join(HERE, "assets"), urllib.parse.unquote(path[17:]))
        if path.startswith("/_preview/tistory/"):
            return self.static(CACHE_DIR, path[18:])
        if path == "/_preview/lint":
            return self.send(200, json.dumps(WARNINGS, ensure_ascii=False, indent=2), "application/json; charset=utf-8")
        if path in ("/favicon.ico", "/rss", "/manage") or path.startswith("/manage/"):
            return self.send(204, b"", "text/plain")
        try:
            out = APP.render(path, query)
        except Exception as e:  # 개발 중 오류를 화면에 보여 줌
            import traceback
            return self.send(500, "<pre>%s</pre>" % html.escape(traceback.format_exc()))
        if out is None:
            return self.send(404, "<h1>404</h1><p><a href='/'>홈으로</a></p>")
        self.send(200, out)


LINT_PATHS = ["/", "/?page=2", "/?cover=1", "/64", "/63?owner=1", "/59", "/category", "/category/" + q("여행"),
              "/tag", "/tag/" + q("캐나다 정보"), "/search/" + q("교토"), "/search/zzz", "/archive/202609",
              "/guestbook", "/notice", "/notice/1", "/99", "/pages/about"]


def main():
    global APP
    ap = argparse.ArgumentParser(description="Aurora 티스토리 스킨 미리보기")
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8080")))
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--lint", action="store_true", help="모든 화면을 렌더링하고 경고를 출력")
    args = ap.parse_args()
    ensure_tistory_css()
    APP = App()
    if args.lint:
        for p in LINT_PATHS:
            u = urllib.parse.urlsplit(p)
            out = APP.render(u.path, dict(urllib.parse.parse_qsl(u.query)))
            left = re.findall(r"\[##_[^\]]+_##\]|</?s_[a-z_\-]+", out or "")
            print("%-32s %s" % (p, "OK" if out and not left else ("남은 치환자: %s" % sorted(set(left)) if out else "404")))
        print("\n경고:" if WARNINGS else "\n경고 없음")
        for k, v in sorted(WARNINGS.items()):
            print("  - %s (x%d)" % (k, v))
        return
    print("Aurora 미리보기: http://%s:%d  (Ctrl+C로 종료)" % ("localhost" if args.host == "0.0.0.0" else args.host, args.port))
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
