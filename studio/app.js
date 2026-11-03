'use strict';
const $=(s,root=document)=>root.querySelector(s);
const $$=(s,root=document)=>[...root.querySelectorAll(s)];
const programs={
 chart:{name:'치과 전자차트 교육',title:'버튼을 외우기 전에, 기록의 흐름부터.',description:'사용 중인 처치 버튼을 살펴보고, 기록과 다음 진료가 연결되는 기준을 정리합니다.',points:['처치 버튼 이름·분류 정리','차팅 항목·기록 순서 통일','다음 진료·인수인계 기준'],recommendation:'처치 버튼 목록 → 공통 차팅 기준 → 다음 진료 연결'},
 system:{name:'업무 표준화 컨설팅',title:'누가 맡아도 이어지는 업무의 기준.',description:'반복 업무의 순서와 담당자를 정리하고, 교대·인수인계 때 확인할 항목을 함께 만듭니다.',points:['반복 업무·담당자 정리','업무별 점검표 구성','공유 문서·인수인계 기준'],recommendation:'반복 업무 확인 → 역할 분담 → 공통 점검표'},
 team:{name:'직원 실무 교육',title:'처음 배우는 직원도 따라오는 교육 순서.',description:'신규 직원에게 필요한 업무를 나누고, 설명·실습·확인 순서로 교육 기준을 구성합니다.',points:['입사 초기 교육 순서','시범·실습·확인 기준','직원별 교육 진행 점검'],recommendation:'교육 항목 정리 → 시범과 실습 → 담당자 확인'},
 ai:{name:'치과 AI 활용 교육',title:'반복 업무에서 시작하는 AI 활용.',description:'회의록, 직원 교육 자료, 설명 콘텐츠에 사용할 요청문을 실제 업무 흐름에 맞게 구성합니다.',points:['회의 결과·할 일 정리','직원 교육 자료 초안','설명 콘텐츠 구성 연습'],recommendation:'반복 업무 선택 → 요청문 작성 → 결과 확인'}
};
let selectedProgram='chart',selectedNeed='chart',currentResource=null,lastFocused=null,toastTimer;
function toast(message){const node=$('.toast');node.textContent=message;node.classList.add('visible');clearTimeout(toastTimer);toastTimer=setTimeout(()=>node.classList.remove('visible'),3200)}
async function copyText(text){try{if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(text)}else{const area=document.createElement('textarea');area.value=text;area.style.cssText='position:fixed;left:-9999px';document.body.append(area);area.select();if(!document.execCommand('copy'))throw new Error('copy');area.remove()}toast('복사했습니다. 필요한 곳에 붙여넣어 주세요.')}catch{toast('자동 복사가 어렵습니다. 내용을 선택해 복사해 주세요.')}}
function chooseProgram(key){selectedProgram=key;const p=programs[key];$$('[data-program]').forEach(b=>{const active=b.dataset.program===key;b.classList.toggle('selected',active);b.setAttribute('aria-pressed',String(active))});$('#detail-title').textContent=p.title;$('#detail-description').textContent=p.description;$('#detail-points').replaceChildren(...p.points.map(text=>{const li=document.createElement('li');li.textContent=text;return li}))}
$$('[data-program]').forEach(button=>button.addEventListener('click',()=>chooseProgram(button.dataset.program)));chooseProgram('chart');
function setInquiryTopic(key){$('#inquiry-topic').value=programs[key].name;$('#contact').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});toast('문의 주제를 선택했습니다.')}
$('#program-inquiry').addEventListener('click',()=>setInquiryTopic(selectedProgram));
$$('[data-need]').forEach(button=>button.addEventListener('click',()=>{selectedNeed=button.dataset.need;$$('[data-need]').forEach(b=>{const active=b===button;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active))});$('#recommendation-title').textContent=programs[selectedNeed].name;$('#recommendation-copy').textContent=programs[selectedNeed].recommendation}));
$('#recommendation-cta').addEventListener('click',()=>setInquiryTopic(selectedNeed));
$$('.workflow-step').forEach(button=>button.addEventListener('click',()=>{const open=button.getAttribute('aria-expanded')==='true';$$('.workflow-step').forEach(b=>{b.classList.remove('active');b.setAttribute('aria-expanded','false');$('.step-symbol',b).textContent='+';b.nextElementSibling.hidden=true});if(!open){button.classList.add('active');button.setAttribute('aria-expanded','true');$('.step-symbol',button).textContent='−';button.nextElementSibling.hidden=false}}));
const menu=$('.menu-toggle');menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));menu.setAttribute('aria-label',open?'메뉴 닫기':'메뉴 열기');$('#navigation').classList.toggle('open',open)});
$$('#navigation a').forEach(a=>a.addEventListener('click',()=>{menu.setAttribute('aria-expanded','false');menu.setAttribute('aria-label','메뉴 열기');$('#navigation').classList.remove('open')}));
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&menu.getAttribute('aria-expanded')==='true'){menu.click();menu.focus()}});
const resources={
 buttons:{category:'회원 전용 자료 · 구성 미리보기',title:'처치 버튼 정리, 세 가지 기준',intro:'처치 버튼의 이름·분류·연결 기준을 확인하는 점검표 구성입니다.',preview:['버튼 이름 점검 항목','진료 흐름에 맞는 분류 항목','기록·다음 진료 연결 점검 항목']},
 onboarding:{category:'회원 전용 자료 · 구성 미리보기',title:'신규 직원 교육, 세 단계',intro:'담당자와 신규 직원이 교육 진행을 함께 확인하는 순서표 구성입니다.',preview:['설명과 시범 단계','함께 실습하는 단계','수행 결과를 확인하는 단계']},
 meeting:{category:'회원 전용 자료 · 구성 미리보기',title:'회의록을 할 일로 바꾸는 요청문',intro:'회의 결과를 담당자·할 일·일정 중심으로 정리하는 요청문 구성입니다.',preview:['회의 결과 정리 항목','담당자·마감일 확인 항목','다음 회의 준비 항목']}
};
function openResource(key,trigger){currentResource=key;lastFocused=trigger;const r=resources[key];$('#resource-category').textContent=r.category;$('#resource-title').textContent=r.title;$('#resource-intro').textContent=r.intro;const body=$('#resource-content');body.replaceChildren();const ul=document.createElement('ul');ul.className='preview-list';r.preview.forEach(text=>{const li=document.createElement('li');li.textContent=text;ul.append(li)});body.append(ul);$('#resource-dialog').showModal()}
$$('[data-resource]').forEach(button=>button.addEventListener('click',()=>openResource(button.dataset.resource,button)));
$('.dialog-close').addEventListener('click',()=>$('#resource-dialog').close());
$('#resource-dialog').addEventListener('click',event=>{if(event.target===event.currentTarget){const rect=event.target.getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)event.currentTarget.close()}});
$('#resource-dialog').addEventListener('close',()=>lastFocused?.focus());
$('#membership-inquiry').addEventListener('click',()=>{const r=resources[currentResource];$('#resource-dialog').close();$('#inquiry-topic').value='회원 자료 이용 문의';$('#inquiry-message').value='「'+r.title+'」 자료 이용 및 회원 승인 절차를 문의드립니다.';$('#contact').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});toast('자료 이용 문의 주제를 선택했습니다.')});
$('#inquiry-form').addEventListener('submit',event=>{event.preventDefault();const values={topic:$('#inquiry-topic').value,audience:$('#inquiry-audience').value,format:$('#inquiry-format').value,date:$('#inquiry-date').value.trim()||'상담 후 협의',message:$('#inquiry-message').value.trim()||'우리 치과에 맞는 교육 내용을 상담하고 싶습니다.'};$('#inquiry-preview').value='안녕하세요, 조재연 강사님.\n강의·컨설팅 문의드립니다.\n\n관심 주제: '+values.topic+'\n교육 대상: '+values.audience+'\n진행 방식: '+values.format+'\n희망 일정: '+values.date+'\n\n문의 내용\n'+values.message;$('#inquiry-result').hidden=false;$('#inquiry-result').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'center'});toast('문의 문구를 만들었습니다. 복사해 카카오톡에 전달하세요.')});
$('#copy-inquiry').addEventListener('click',()=>copyText($('#inquiry-preview').value));
