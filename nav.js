/* =========================================================
   김석현 과장 사이트 공통 햄버거 메뉴 (nav.js)
   - 위치: main 저장소 (https://kim-benz.github.io/main/nav.js)
   - 사용법: 각 페이지 </body> 바로 위에 아래 한 줄만 추가
     <script src="https://kim-benz.github.io/main/nav.js"></script>
   - 메뉴 수정은 아래 MENU 목록만 고치면 모든 페이지에 반영됩니다.
========================================================= */
(function () {
  var MAIN = 'https://kim-benz.github.io/main/';

  // ▼▼▼ 메뉴 목록 (여기만 수정하세요) ▼▼▼
  var MENU = [
    { group: '이번 달 구매 조건', items: [
      { name: '이달의 프로모션', sub: '차종별 할인 · 최종가', url: MAIN + 'promotion.html' },
      { name: '출고 웰컴 서비스', sub: '틴팅 · 블랙박스 · 기프트', url: MAIN + 'welcome.html' },
      { name: '보증 & 서비스', sub: '보증기간 · 고객 케어', url: MAIN + 'service.html' },
      { name: '전 차종 공식 가격표', sub: 'PDF', url: MAIN + 'pdf/price_list.pdf', ext: true }
    ]},
    { group: '신차 · 모델', items: [
      { name: '전 차종 제원 · 가격표', sub: '세단 · SUV · 쿠페 · 전기차', url: MAIN + 'models.html' },
      { name: 'Electric GLB', sub: '사전계약', url: 'https://kim-benz.github.io/GLB_EV/' },
      { name: 'Electric CLA', sub: '신차 가이드', url: 'https://kim-benz.github.io/CLA/' },
      { name: 'Electric GLC', sub: '', url: 'https://kim-benz.github.io/GLC_EV/' },
      { name: '신형 GLE · GLS', sub: '11월 말 출시 예상', url: 'https://kim-benz.github.io/GLE_GLS/' },
      { name: 'V-Class', sub: '사전계약', url: 'https://kim-benz.github.io/V_CLASS/' },
      { name: 'S-Class', sub: '런칭', url: 'https://kim-benz.github.io/S-CLASS/' }
    ]},
    { group: '상담 · 방문', items: [
      { name: '시승 & 견적 신청', sub: '', url: MAIN + '#test-drive' },
      { name: '서비스 예약', sub: '출고 고객 정비 케어', url: MAIN + '#service-care' },
      { name: '전시장 오시는 길', sub: '새천년대로 210', url: 'https://naver.me/xAf1U2G5', ext: true }
    ]}
  ];
  var PHONE = '01093790999';
  var KAKAO = 'http://pf.kakao.com/_hTPGX/chat';
  // ▲▲▲ 메뉴 목록 끝 ▲▲▲

  if (document.getElementById('kbNavBtn')) return;

  var css = ''
    + '#kbNavBtn{position:fixed;top:12px;right:12px;z-index:999;width:46px;height:46px;border-radius:12px;'
    + 'border:1px solid rgba(255,255,255,.18);background:rgba(15,23,42,.82);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);'
    + 'cursor:pointer;display:flex;align-items:center;justify-content:center;padding:0;box-shadow:0 4px 14px rgba(0,0,0,.18)}'
    + '@media(max-width:650px){#kbNavBtn{top:6px;right:8px;width:40px;height:40px;border-radius:10px}}'
    + '#kbNavBtn span,#kbNavBtn span:before,#kbNavBtn span:after{display:block;width:20px;height:2px;background:#fff;border-radius:2px;position:relative;content:""}'
    + '#kbNavBtn span:before{position:absolute;top:-6px}#kbNavBtn span:after{position:absolute;top:6px}'
    + '.kb-dim{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:10000;opacity:0;visibility:hidden;transition:opacity .25s}'
    + '.kb-dim.open{opacity:1;visibility:visible}'
    + '.kb-drawer{position:fixed;top:0;right:0;bottom:0;width:min(380px,88vw);background:#0d1520;color:#fff;z-index:10001;'
    + 'transform:translateX(100%);transition:transform .3s ease;display:flex;flex-direction:column;'
    + 'font-family:"Pretendard",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;line-height:1.4;text-align:left}'
    + '.kb-drawer.open{transform:none}'
    + '.kb-drawer *{box-sizing:border-box;margin:0;padding:0}'
    + '.kb-head{display:flex;align-items:center;justify-content:space-between;padding:18px 20px;border-bottom:1px solid rgba(255,255,255,.08)}'
    + '.kb-home{color:#fff;text-decoration:none}'
    + '.kb-home b{display:block;font-size:15px;font-weight:800;letter-spacing:1.5px}'
    + '.kb-home small{display:block;font-size:12px;color:#94a3b8;margin-top:2px}'
    + '.kb-close{width:42px;height:42px;border-radius:12px;border:1px solid rgba(255,255,255,.15);background:transparent;color:#fff;font-size:22px;cursor:pointer;line-height:1}'
    + '.kb-body{flex:1;overflow-y:auto;padding:6px 20px 20px;-webkit-overflow-scrolling:touch}'
    + '.kb-group{padding:16px 0 6px;border-bottom:1px solid rgba(255,255,255,.07)}'
    + '.kb-group:last-child{border-bottom:0}'
    + '.kb-label{font-size:12px;font-weight:600;color:#7c8a9e;margin-bottom:4px;letter-spacing:.5px}'
    + '.kb-item{display:flex;align-items:baseline;flex-wrap:wrap;gap:8px;padding:11px 0;color:#fff;text-decoration:none;font-size:17px;font-weight:700}'
    + '.kb-item:hover{color:#7ed6ff}'
    + '.kb-item small{font-size:12.5px;font-weight:500;color:#7c8a9e}'
    + '.kb-item.cur{color:#38bdf8}'
    + '.kb-foot{display:flex;gap:8px;padding:14px 20px calc(14px + env(safe-area-inset-bottom));border-top:1px solid rgba(255,255,255,.08)}'
    + '.kb-foot a{flex:1;text-align:center;padding:12px 0;border-radius:10px;font-size:14px;font-weight:700;text-decoration:none}'
    + '.kb-call{background:#0284c7;color:#fff}.kb-kakao{background:#fee500;color:#191919}';

  var st = document.createElement('style');
  st.textContent = css;
  document.head.appendChild(st);

  var here = location.href.split('#')[0].replace(/index\.html$/, '');
  var html = '';
  MENU.forEach(function (g) {
    html += '<div class="kb-group"><div class="kb-label">' + g.group + '</div>';
    g.items.forEach(function (it) {
      var cur = it.url.split('#')[0] === here && it.url.indexOf('#') < 0 ? ' cur' : '';
      var tgt = it.ext ? ' target="_blank" rel="noopener noreferrer"' : '';
      html += '<a class="kb-item' + cur + '" href="' + it.url + '"' + tgt + '>' + it.name
        + (it.sub ? '<small>' + it.sub + '</small>' : '') + '</a>';
    });
    html += '</div>';
  });

  var btn = document.createElement('button');
  btn.id = 'kbNavBtn';
  btn.type = 'button';
  btn.setAttribute('aria-label', '전체 메뉴 열기');
  btn.innerHTML = '<span></span>';

  var dim = document.createElement('div');
  dim.className = 'kb-dim';

  var dr = document.createElement('nav');
  dr.className = 'kb-drawer';
  dr.setAttribute('aria-label', '전체 메뉴');
  dr.innerHTML =
    '<div class="kb-head"><a class="kb-home" href="' + MAIN + '"><b>MERCEDES-BENZ</b><small>포항전시장 김석현 과장 · 홈</small></a>'
    + '<button type="button" class="kb-close" aria-label="메뉴 닫기">×</button></div>'
    + '<div class="kb-body">' + html + '</div>'
    + '<div class="kb-foot"><a class="kb-call" href="tel:' + PHONE + '">📞 전화 상담</a>'
    + '<a class="kb-kakao" href="' + KAKAO + '" target="_blank" rel="noopener noreferrer">💬 카톡 상담</a></div>';

  document.body.appendChild(btn);
  document.body.appendChild(dim);
  document.body.appendChild(dr);

  var prevOverflow = '';
  function open() {
    prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    dim.classList.add('open'); dr.classList.add('open');
  }
  function close() {
    document.body.style.overflow = prevOverflow;
    dim.classList.remove('open'); dr.classList.remove('open');
  }
  btn.onclick = open;
  dim.onclick = close;
  dr.querySelector('.kb-close').onclick = close;
  dr.addEventListener('click', function (e) { if (e.target.closest('.kb-item')) close(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
})();
