# -*- coding: utf-8 -*-
"""미리보기용 샘플 데이터 (실제 블로그 주제를 참고해 만든 예시입니다)."""

BLOG = {
    "title": "가볼만한 곳",
    "blogger": "소망이 있으므로",
    "desc": "여행지부터 생활 정보, 쇼핑 꿀팁까지 — 알아두면 쓸모 있는 이야기를 차곡차곡 모읍니다.",
    "image": "/_preview/assets/avatar.svg",
    "count_total": "685675",
    "count_today": "212",
    "count_yesterday": "348",
    "post_total": 66,
}

CATEGORIES = [
    {"name": "여행", "count": 18, "subs": [{"name": "해외", "count": 9}, {"name": "국내", "count": 9}]},
    {"name": "가볼만한 곳", "count": 14, "subs": []},
    {"name": "생활 정보", "count": 21, "subs": []},
    {"name": "쇼핑 가이드", "count": 13, "subs": []},
]

IMG = "/_preview/assets/img/"

POSTS = [
    {"id": 66, "title": "알리 라부부 구매 가이드: 정품 구별 팁부터 배송까지 완벽 정리!", "category": "쇼핑 가이드",
     "date": (2026, 9, 26, 21, 40), "thumb": IMG + "toy.jpg", "comments": 7,
     "summary": "요즘 가장 핫한 아트토이, 어디서 사야 안전할까요? 정품 박스와 스티커 확인법, 가품을 피하는 판매자 체크리스트, 배송 기간과 관세 기준까지 한 번에 정리했어요.",
     "tags": ["라부부 정품", "아트토이", "해외직구"]},
    {"id": 65, "title": "2025년 다이소 핫한 아이템 5가지! 품절 대란 필수템 완전 정복", "category": "쇼핑 가이드",
     "date": (2026, 9, 23, 10, 12), "thumb": None, "comments": 12,
     "summary": "출시되자마자 품절되는 다이소 인기템, 직접 써 보고 골랐습니다. 가격 대비 만족도가 높은 수납·주방·욕실 아이템과 재입고 알림 받는 방법까지.",
     "tags": ["다이소 추천템", "살림템"]},
    {"id": 64, "title": "교토 교통패스 완벽 정복 가이드: 어떤 패스를 선택해야 할까?", "category": "해외",
     "date": (2026, 9, 18, 8, 30), "thumb": IMG + "kyoto.jpg", "comments": 24,
     "summary": "버스 1일권이 사라진 뒤 교토 여행자에게 가장 알맞은 패스는 무엇일까요? 일정별 추천 조합과 IC카드 활용법, 동선 짜는 요령을 정리했습니다.",
     "tags": ["교토 교통패스", "교토 여행", "일본 여행"]},
    {"id": 63, "title": "캐나다 비행시간: 어디로 떠나시나요? 도시별 직항·경유 총정리", "category": "해외",
     "date": (2026, 9, 10, 19, 5), "thumb": IMG + "canada.jpg", "comments": 5,
     "summary": "밴쿠버, 토론토, 캘거리까지 인천에서 출발하는 캐나다 주요 도시별 비행시간과 시차, 경유 노선을 비교했어요.",
     "tags": ["캐나다 비행시간", "캐나다 정보"]},
    {"id": 62, "title": "내장산 단풍 절정 시기와 가볼만한 코스 BEST 5", "category": "가볼만한 곳",
     "date": (2026, 9, 3, 7, 50), "thumb": IMG + "autumn.jpg", "comments": 9,
     "summary": "올해 내장산 단풍은 언제 절정일까요? 우화정과 단풍터널을 잇는 인기 코스, 주차 팁과 붐비지 않는 시간대를 알려드립니다.",
     "tags": ["내장산 단풍절정시기", "단풍 축제", "단풍구경 가볼만한 곳"]},
    {"id": 61, "title": "서울 첫눈 시기, 올해는 언제 내릴까? 첫눈의 기준까지", "category": "생활 정보",
     "date": (2026, 8, 28, 22, 15), "thumb": IMG + "snow.jpg", "comments": 3,
     "summary": "서울의 첫눈은 어디에서 관측될 때 공식 기록이 될까요? 최근 10년 첫눈 날짜와 올해 전망을 살펴봤어요.",
     "tags": ["서울 첫눈 시기", "서울 첫눈 정의"]},
    {"id": 60, "title": "에버랜드 사파리 가격과 스페셜 투어 예약 꿀팁", "category": "가볼만한 곳",
     "date": (2026, 8, 20, 11, 0), "thumb": IMG + "safari.jpg", "comments": 6,
     "summary": "사파리월드 기본 탑승과 스페셜 투어의 차이, 대기 시간을 줄이는 예약 방법과 아이와 함께 가기 좋은 시간대를 정리했습니다.",
     "tags": ["에버랜드 사파리 가격", "아이와 가볼만한 곳"]},
    {"id": 59, "title": "iptime 공유기 설정 방법: 초보도 5분이면 끝", "category": "",
     "date": (2026, 8, 12, 14, 20), "thumb": None, "comments": 15,
     "summary": "관리자 페이지 접속부터 와이파이 이름·비밀번호 변경, 보안 설정까지 순서대로 따라 하면 누구나 쉽게 끝낼 수 있어요.",
     "tags": ["iptime 공유기 설정 방법"]},
    {"id": 58, "title": "워터파크 신발, 꼭 필요할까? 아쿠아슈즈 고르는 법", "category": "쇼핑 가이드",
     "date": (2026, 8, 5, 9, 45), "thumb": IMG + "waterpark.jpg", "comments": 2,
     "summary": "미끄럼 방지와 발 보호에 좋은 아쿠아슈즈, 사이즈와 밑창 고르는 요령과 워터파크별 신발 규정을 알아봤어요.",
     "tags": ["워터파크 신발", "여름 준비물"]},
    {"id": 57, "title": "주말농장 파종 시기 캘린더: 봄·가을 작물 총정리", "category": "생활 정보",
     "date": (2026, 7, 29, 6, 30), "thumb": IMG + "farm.jpg", "comments": 4,
     "summary": "상추, 감자, 배추, 무까지 — 주말농장 초보도 실패하지 않는 작물별 파종·수확 시기를 한눈에 볼 수 있게 정리했습니다.",
     "tags": ["주말농장 파종시기", "텃밭 가꾸기"]},
    {"id": 56, "title": "추석 선물세트 1위는? 올해 인기 선물 트렌드 분석", "category": "쇼핑 가이드",
     "date": (2026, 7, 21, 18, 0), "thumb": IMG + "toy.jpg", "comments": 8,
     "summary": "가격대별로 가장 많이 팔린 추석 선물세트와 받는 사람이 좋아하는 선물 유형을 데이터로 살펴봤어요.",
     "tags": ["추석 선물세트 1위"]},
    {"id": 55, "title": "금리인하 요구권 대상과 신청 방법 총정리", "category": "생활 정보",
     "date": (2026, 7, 14, 12, 10), "thumb": None, "comments": 11,
     "summary": "승진·연봉 상승·신용점수 개선이 있었다면 대출 금리를 낮출 수 있어요. 대상 조건과 은행별 신청 방법을 정리했습니다.",
     "tags": ["금리인하 요구권 대상"]},
    {"id": 54, "title": "가을 단풍 여행지 추천: 서울 근교 드라이브 코스", "category": "국내",
     "date": (2026, 7, 6, 16, 40), "thumb": IMG + "autumn.jpg", "comments": 5,
     "summary": "서울에서 두 시간 이내로 다녀올 수 있는 단풍 명소와 드라이브 동선, 근처 맛집까지 함께 소개합니다.",
     "tags": ["단풍구경 가볼만한 곳", "드라이브 코스"]},
    {"id": 53, "title": "밴쿠버 여행 준비물 체크리스트와 날씨별 옷차림", "category": "해외",
     "date": (2026, 6, 28, 9, 0), "thumb": IMG + "canada.jpg", "comments": 3,
     "summary": "비가 잦은 밴쿠버, 계절별로 무엇을 챙겨야 할까요? 전압·유심·교통카드까지 출국 전 체크리스트를 만들었어요.",
     "tags": ["캐나다 정보"]},
]

NOTICES = [
    {"id": 1, "title": "블로그가 새 옷을 입었어요 — Aurora 스킨 적용 안내", "date": (2026, 9, 27, 9, 0), "thumb": None,
     "summary": "더 읽기 편하고 빠른 블로그로 새단장했습니다. 다크 모드와 검색 단축키도 사용해 보세요."},
]

TAGS = [
    ("iptime 공유기 설정 방법", 2), ("신탁원부 인터넷발급", 4), ("국세가족 행복포탈", 5), ("워터파크 신발", 3),
    ("공군체력단련장 골프장", 5), ("내장산 단풍절정시기", 1), ("금리인하 요구권 대상", 3), ("서울 첫눈 시기", 2),
    ("네이버지도 바로가기", 4), ("캐나다 정보", 3), ("추석 선물세트 1위", 2), ("주말농장 파종시기", 4),
    ("캐나다 비행시간", 2), ("서울 첫눈 정의", 5), ("인서울 대학 순위", 3), ("에버랜드 사파리 가격", 1),
    ("수협 아이적금", 5), ("단풍 축제", 2), ("단풍구경 가볼만한 곳", 1), ("교토 교통패스", 1),
    ("다이소 추천템", 2), ("라부부 정품", 3), ("해외직구", 4), ("일본 여행", 3),
]

RECENT_COMMENTS = [
    {"desc": "교토 버스 패스 정보 정말 도움이 됐어요! 덕분에 동선 짜기 쉬웠습니다.", "name": "여행하는곰", "time": "09.26", "post": 64},
    {"desc": "다이소 수납템 저도 샀는데 진짜 좋더라고요 👍", "name": "살림고수", "time": "09.24", "post": 65},
    {"desc": "공유기 설정 따라 했더니 5분 만에 끝났어요. 감사합니다!", "name": "초보유저", "time": "09.21", "post": 59},
    {"desc": "올해 단풍 시기도 업데이트 부탁드려요~", "name": "가을좋아", "time": "09.18", "post": 62},
]

LINKS = [
    {"url": "https://www.tistory.com", "site": "티스토리"},
    {"url": "https://korean.visitkorea.or.kr", "site": "대한민국 구석구석"},
]

ARCHIVES = [("2026/09", "202609", 4), ("2026/08", "202608", 4), ("2026/07", "202607", 4), ("2026/06", "202606", 3), ("2026/05", "202605", 6)]

ARTICLE_HTML = """
<p data-ke-size="size16">교토 여행을 준비하면서 가장 많이 받는 질문이 바로 <b>"어떤 교통패스를 사야 하나요?"</b>입니다. 예전에는 버스 1일권 하나면 충분했지만, 지금은 여행 스타일에 따라 선택지가 조금 복잡해졌어요. 이 글에서는 일정별로 가장 알맞은 조합을 정리해 볼게요.</p>
<p data-ke-size="size16">&nbsp;</p>
<figure class="imageblock alignCenter" data-ke-mobilestyle="widthOrigin" data-origin-width="1024" data-origin-height="640"><span data-url="/_preview/assets/img/kyoto.jpg" data-lightbox="lightbox"><img src="/_preview/assets/img/kyoto.jpg" data-origin-width="1024" data-origin-height="640" /></span><figcaption>해 질 녘의 히가시야마 거리. 걸어서 둘러보기 좋은 구간이에요.</figcaption></figure>
<p data-ke-size="size16">&nbsp;</p>
<h2 data-ke-size="size26">1. 교토 교통패스 한눈에 비교</h2>
<p data-ke-size="size16">아래 표는 여행자가 가장 많이 고민하는 선택지를 정리한 것입니다. 가격과 판매 여부는 시기마다 달라질 수 있으니 출발 전 공식 안내를 꼭 확인하세요.</p>
<table style="border-collapse: collapse; width: 100%;" border="1" data-ke-align="alignLeft" data-ke-style="style12">
<tbody>
<tr><td>구분</td><td>이용 범위</td><td>이런 분께 추천</td></tr>
<tr><td>지하철·버스 1일권</td><td>시영 지하철 + 시 버스</td><td>하루에 5곳 이상 이동하는 분</td></tr>
<tr><td>IC카드 (ICOCA 등)</td><td>대부분의 대중교통</td><td>일정이 유동적인 자유여행자</td></tr>
<tr><td>간사이 지역 패스</td><td>교토 + 오사카 + 나라</td><td>여러 도시를 오가는 분</td></tr>
</tbody>
</table>
<h3 data-ke-size="size23">버스 1일권이 사라진 이유</h3>
<p data-ke-size="size16">관광객이 몰리는 버스 혼잡을 줄이기 위해 버스 전용 1일권 판매가 종료됐어요. 대신 지하철과 함께 쓰는 통합권을 활용하면 오히려 이동이 빨라지는 경우가 많습니다.</p>
<blockquote data-ke-style="style2"><p data-ke-size="size16">💡 버스는 편리하지만 성수기에는 정체가 잦아요. 먼 거리는 지하철로 이동하고, 가까운 명소는 걸어서 둘러보는 것이 가장 효율적입니다.</p></blockquote>
<h2 data-ke-size="size26">2. 일정별 추천 조합</h2>
<ul style="list-style-type: disc;" data-ke-list-type="disc">
<li><b>당일치기</b> — 지하철·버스 1일권 하나로 충분해요.</li>
<li><b>2~3일</b> — IC카드를 기본으로, 이동이 많은 날만 1일권을 추가하세요.</li>
<li><b>간사이 일주</b> — 지역 패스로 도시 간 이동 비용을 아낄 수 있어요.</li>
</ul>
<h3 data-ke-size="size23">하루 코스 예시: 기요미즈데라 → 기온</h3>
<ol style="list-style-type: decimal;" data-ke-list-type="decimal">
<li>아침 일찍 기요미즈데라에서 한적한 풍경 즐기기</li>
<li>산넨자카·니넨자카 골목을 따라 천천히 내려오기</li>
<li>야사카 신사를 지나 기온 거리에서 저녁 산책</li>
</ol>
<blockquote data-ke-style="style1"><span>여행의 만족도는 결국 동선에서 결정됩니다.</span></blockquote>
<h2 data-ke-size="size26">3. 알아두면 좋은 꿀팁</h2>
<h4 data-ke-size="size20">IC카드 잔액은 미리 넉넉하게</h4>
<p data-ke-size="size16">역마다 충전기가 있지만 현금만 받는 곳이 많아요. <code>ICOCA</code> 카드는 편의점 결제에도 쓸 수 있어 남은 잔액을 알뜰하게 소진할 수 있습니다.</p>
<pre id="code_1700000000001" class="bash" data-ke-language="bash" data-ke-type="codeblock"><code># 여행 경비 메모 (예시)
교통비   = 1일권 x 2일 + IC카드 충전 3,000엔
환율     = 100엔 ≈ 910원
합계     ≈ 약 5만 원</code></pre>
<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style5" />
<blockquote data-ke-style="style3"><p data-ke-size="size16">📌 이 글은 미리보기용 예시 글입니다. 실제 블로그에서는 작성하신 글이 이 디자인으로 보여요.</p></blockquote>
<p data-ke-size="size16">&nbsp;</p>
<figure id="og_1700000000002" contenteditable="false" data-ke-type="opengraph" data-ke-align="alignCenter" data-og-type="website" data-og-title="교토 공식 여행 가이드" data-og-description="교토의 명소, 교통, 축제 정보를 한곳에서" data-og-host="kyoto.travel" data-og-source-url="https://kyoto.travel/ko/" data-og-url="https://kyoto.travel/ko/"><a href="https://kyoto.travel/ko/" target="_blank" rel="noopener" data-source-url="https://kyoto.travel/ko/"><div class="og-image" style="background-image: url('/_preview/assets/img/kyoto.jpg');">&nbsp;</div><div class="og-text"><p class="og-title" data-ke-size="size16">교토 공식 여행 가이드</p><p class="og-desc" data-ke-size="size16">교토의 명소, 교통, 축제 정보를 한곳에서</p><p class="og-host" data-ke-size="size16">kyoto.travel</p></div></a></figure>
<p data-ke-size="size16">&nbsp;</p>
<p data-ke-size="size16">교통패스만 잘 골라도 교토 여행이 한결 가벼워집니다. 궁금한 점은 댓글로 남겨 주세요. 다음 글에서는 <a href="/63">캐나다 비행시간 총정리</a>를 소개할게요!</p>
"""

POST_BUTTONS_HTML = """
<div class="container_postbtn #post_button_group">
  <div class="postbtn_like">
    <div class="wrap_btn" id="reaction-64"><button class="btn_post uoc-icon"><div class="uoc-icon"><span class="ico_postbtn ico_like">좋아요</span><span class="txt_like uoc-count">42</span></div></button></div>
    <div class="wrap_btn wrap_btn_share"><button type="button" class="btn_post sns_btn btn_share" aria-expanded="false"><span class="ico_postbtn ico_share">공유하기</span></button></div>
    <div class="wrap_btn wrap_btn_etc" data-entry-id="64"><button type="button" class="btn_post btn_etc1" aria-expanded="false"><span class="ico_postbtn ico_etc">게시글 관리</span></button></div>
  </div>
  <div data-tistory-react-app="SupportButton"></div>
</div>
"""

ANOTHER_CATEGORY_HTML = """
<div class="another_category another_category_color_gray">
  <h4>'<a href="/category/%EC%97%AC%ED%96%89/%ED%95%B4%EC%99%B8">여행/해외</a>' 카테고리의 다른 글</h4>
  <table><tbody>
    <tr><th><a href="/63">캐나다 비행시간: 어디로 떠나시나요? 도시별 직항·경유 총정리</a>&nbsp;&nbsp;<span>(5)</span></th><td>2026.09.10</td></tr>
    <tr><th><a href="/64" class="current">교토 교통패스 완벽 정복 가이드: 어떤 패스를 선택해야 할까?</a>&nbsp;&nbsp;<span>(24)</span></th><td>2026.09.18</td></tr>
    <tr><th><a href="/53">밴쿠버 여행 준비물 체크리스트와 날씨별 옷차림</a>&nbsp;&nbsp;<span>(3)</span></th><td>2026.06.28</td></tr>
  </tbody></table>
</div>
"""


def _reply(name, date, text, thumb_hue=250, children=""):
    avatar = "/_preview/assets/avatar.svg"
    return f"""
    <li class="tt-item-reply rp_general">
      <div class="tt-wrap-cmt">
        <div class="tt-box-thumb"><a href="#"><span class="tt-thumbnail" style="background-image: url('{avatar}'); filter: hue-rotate({thumb_hue}deg);"></span></a></div>
        <div class="tt-box-content">
          <div class="tt-box-meta"><a href="#" class="tt-link-user">{name}</a></div>
          <div class="tt-wrap-desc"><p class="tt_desc">{text}</p></div>
          <div class="tt-wrap-info"><span class="tt_date">{date}</span><span class="tt-wrap-link-comment"><a href="#" class="tt-link-comment"><span class="tt_txt_g">답글</span><span class="tt_num_g"></span></a></span></div>
          <div class="tt-box-modify"><button type="button" class="tt_img_area_reply tt-button-modify">더보기</button></div>
        </div>
      </div>
      {children}
    </li>"""


def comment_html(count=3, guestbook=False):
    replies = _reply("여행하는곰", "2026. 9. 26. 21:14", "교토 버스 패스가 없어진 줄 몰랐는데 덕분에 계획을 다시 세웠어요. 표로 정리해 주셔서 한눈에 보기 좋네요!", 0,
                     children='<ul class="tt-list-reply-comment">' + _reply("소망이 있으므로", "2026. 9. 26. 22:03", "도움이 되셨다니 다행이에요 😊 즐거운 교토 여행 되세요!", 120) + "</ul>")
    replies += _reply("가을좋아", "2026. 9. 25. 08:41", "IC카드 팁 좋네요. 편의점에서 잔액 쓰는 방법은 처음 알았어요.", 200)
    label = "방명록" if guestbook else "댓글"
    return f"""
<div data-tistory-react-app="Comment"><div class="tt-comment-cont">
  <div class="tt-box-total"><span class="tt_txt_g">{label}</span><span class="tt_num_g">{count}</span></div>
  <div class="tt-area-reply"><ul class="tt-list-reply">{replies}</ul></div>
  <form style="margin: 0px;"><div class="tt-area-write">
    <div class="tt-box-thumb"><span class="tt-thumbnail" style="background-image: url('/_preview/assets/avatar.svg');"></span></div>
    <div class="tt_wrap_write">
      <div class="tt-box-account"><input type="text" title="이름" placeholder="이름" maxlength="32" value=""><input type="password" title="비밀번호" maxlength="12" placeholder="비밀번호" value=""></div>
      <div class="tt-box-textarea"><div class="tt-inner-g"><div contenteditable="true" placeholder="내용을 입력하세요." class="tt-cmt"></div></div></div>
      <div class="tt-box-write"><label class="tt-xe-label"><input type="checkbox" id="secret"><span class="tt_img_area_reply tt-xe-input-helper"></span><span class="tt-xe-label-text">비밀글</span></label><button type="submit" class="tt-btn_register" disabled="">등록</button></div>
    </div>
  </div></form>
</div></div>
"""
