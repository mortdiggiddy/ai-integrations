import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

/** Build one offline walkthrough from the delivered graph and authored details. */
function buildWalkthrough() {
  const directory = dirname(fileURLToPath(import.meta.url));
  const base = readFileSync(join(directory, 'architecture.html'), 'utf8');
  const data = JSON.parse(readFileSync(join(directory, 'walkthrough.json'), 'utf8'));
  const candidate = JSON.parse(readFileSync(join(directory, 'candidate.json'), 'utf8'));
  data.repository = candidate.meta.repository;
  data.sources = Object.fromEntries(candidate.components.map(node => [node.id, node.sources]));
  const encoded = JSON.stringify(data).replaceAll('<', '\\u003c');
  const extension = String.raw`
<style>
#walk-dock,#walk-panel,#walk-tip{box-sizing:border-box;font-family:ui-sans-serif,system-ui,sans-serif;color:#e8eef8}
#walk-dock{position:fixed;bottom:18px;left:18px;z-index:1000;display:flex;gap:5px;align-items:center;padding:7px;border:1px solid #53647d;background:#101a2cf2;border-radius:12px;box-shadow:0 10px 35px #0005}
#walk-dock button,#walk-panel button,#walk-panel select{font:inherit;color:inherit;background:#203049;border:1px solid #62748e;border-radius:7px;padding:8px 12px;cursor:pointer}
#walk-panel{position:fixed;top:18px;right:18px;bottom:85px;z-index:1010;width:min(470px,calc(100vw - 36px));background:#111b2df7;border:1px solid #6882a5;border-radius:16px;box-shadow:0 20px 60px #0006;display:flex;flex-direction:column;overflow:hidden}
#walk-panel[hidden],#walk-tip[hidden]{display:none!important}
#walk-scope{margin:0 0 16px;padding:12px 16px;border:1px solid #687f9e;border-radius:10px;font:13px/1.5 ui-sans-serif,system-ui,sans-serif;background:#142039;color:#ffdc98}
html[data-theme="light"] #walk-scope{background:#fff6de;color:#65470b;border-color:#d2b578}
#walk-panel header{padding:18px 22px;border-bottom:1px solid #3b4d68;display:flex;gap:14px;justify-content:space-between;align-items:flex-start}
#walk-panel h2{font-size:20px;line-height:1.25;margin:5px 0 8px}
#walk-panel .eyebrow{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:#a7c0e3}
#walk-panel .status{font-size:12px;color:#ffda91}
#walk-panel main{padding:18px 22px;overflow-y:auto;overscroll-behavior:contain;line-height:1.55;font-size:14px}
#walk-panel p{margin:0 0 18px}
#walk-panel h3{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:#94c9ff;margin:20px 0 7px}
#walk-panel a{color:#b8d8ff;overflow-wrap:anywhere}
#walk-panel footer{padding:12px 18px;border-top:1px solid #3b4d68;display:flex;gap:8px;align-items:center;justify-content:space-between}
#walk-panel select{width:min(285px,60vw);font-size:12px}
#walk-tip{position:fixed;left:18px;bottom:78px;z-index:1000;width:min(390px,calc(100vw - 36px));background:#15233bf5;border:1px solid #637e9f;border-radius:12px;padding:13px 16px;pointer-events:none;box-shadow:0 12px 35px #0004;font-size:13px;line-height:1.45}
#walk-tip strong{display:block;margin-bottom:6px;color:#b3d5ff}
#walk-dock button:focus-visible,#walk-panel button:focus-visible,#walk-panel select:focus-visible{outline:3px solid #ffdc8c;outline-offset:3px}
html[data-theme="light"] #walk-panel,html[data-theme="light"] #walk-dock,html[data-theme="light"] #walk-tip{background:#f5f8fffa;color:#1a2940;border-color:#72849d}
html[data-theme="light"] #walk-panel button,html[data-theme="light"] #walk-panel select,html[data-theme="light"] #walk-dock button{background:#e4ecf8;border-color:#8b9bb2}
html[data-theme="light"] #walk-panel h3,html[data-theme="light"] #walk-tip strong{color:#155b91}
html[data-theme="light"] #walk-panel .eyebrow{color:#4f6582}
html[data-theme="light"] #walk-panel .status{color:#80510b}
html[data-theme="light"] #walk-panel a{color:#174f95}
@media(max-width:620px){#walk-panel{left:12px;right:12px;top:12px;bottom:85px;width:auto}#walk-dock{left:12px;bottom:12px}#walk-panel main{font-size:14px}}
@media print{#walk-panel,#walk-tip,#walk-dock{display:none!important}}
</style>
<div id="walk-dock" aria-label="Numbered architecture walkthrough">
  <button id="walk-open" type="button">Walkthrough: 23 steps</button>
  <button id="walk-prev" type="button" aria-label="Previous step">←</button>
  <button id="walk-next" type="button" aria-label="Next step">→</button>
</div>
<div id="walk-tip" hidden role="tooltip"></div>
<aside id="walk-panel" hidden aria-label="Architecture step details">
  <header>
    <div><div id="walk-domain" class="eyebrow"></div><h2 id="walk-title"></h2><div id="walk-status" class="status"></div></div>
    <button id="walk-close" type="button" aria-label="Close step details">Close</button>
  </header>
  <main id="walk-content"></main>
  <footer><span id="walk-position"></span><select id="walk-select" aria-label="Jump to a walkthrough step"></select></footer>
</aside>
<script id="walk-data" type="application/json">__DATA__</script>
<script>
(function(){
'use strict';
const data=JSON.parse(document.getElementById('walk-data').textContent);
const byId=new Map(data.steps.map(step=>[step.id,step]));
const numbered=data.steps.filter(step=>Number.isInteger(step.number));
const graph=document.querySelector('.diagram-container > svg');
const panel=document.getElementById('walk-panel');
const content=document.getElementById('walk-content');
const tip=document.getElementById('walk-tip');
const selector=document.getElementById('walk-select');
const openButton=document.getElementById('walk-open');
let currentId='s01';
let returnFocus=openButton;
function element(tag,text){const node=document.createElement(tag);node.textContent=text;return node;}
const scopeNotice=element('div',data.scope+' Click a numbered node or use Walkthrough for full handoffs and owners. Domain boxes show responsibility, not separate physical hosts.');
scopeNotice.id='walk-scope';
if(graph)graph.parentElement.before(scopeNotice);
function graphNode(id){return graph&&graph.querySelector('[data-node-id="'+id+'"]');}
function sourceLink(source){
  const link=element('a',source.label+': '+source.path+':'+source.line);
  link.href=data.repository.url.replace(/\.git$/,'')+'/blob/'+data.repository.revision+'/'+source.path+'#L'+source.line+(source.end_line?'-L'+source.end_line:'');
  link.target='_blank';link.rel='noopener noreferrer';return link;
}
numbered.forEach(step=>{const option=element('option',step.number+'. '+step.title);option.value=step.id;selector.append(option);});
function show(id,scroll){
  const step=byId.get(id);if(!step)return;
  currentId=id;tip.hidden=true;panel.hidden=false;
  document.getElementById('walk-domain').textContent=step.domain;
  document.getElementById('walk-title').textContent=(step.number?step.number+'. ':'')+step.title;
  document.getElementById('walk-status').textContent=step.status;
  content.replaceChildren(element('p',step.description));
  [['Directional handoff','handoff'],['Persistence owner and boundary','persistence'],['Refusal and failure rule','refusal'],['Implementation and qualification','qualification']].forEach(([label,key])=>{content.append(element('h3',label),element('p',step[key]));});
  content.append(element('h3','Evidence at the starting revision'));
  (data.sources[id]||[]).forEach(source=>{const p=document.createElement('p');p.append(sourceLink(source));content.append(p);});
  content.append(element('h3','Scope'),element('p',data.scope+' Domain columns show responsibility, not physical host separation.'));
  document.getElementById('walk-position').textContent=step.number?'Step '+step.number+' / 23':'Failure / delivery branch';
  selector.value=step.number?id:'';
  openButton.textContent=step.number?'Step '+step.number+' / 23: details':'Branch details';
  content.scrollTop=0;
  if(scroll){const node=graphNode(id);if(node)node.scrollIntoView({block:'center',inline:'nearest',behavior:'instant'});}
}
function close(){panel.hidden=true;tip.hidden=true;openButton.textContent='Walkthrough: 23 steps';if(returnFocus&&returnFocus.isConnected)returnFocus.focus({preventScroll:true});}
function move(delta){const current=byId.get(currentId);const number=current&&current.number||1;show(numbered[Math.max(0,Math.min(22,number-1+delta))].id,true);}
openButton.addEventListener('click',()=>{returnFocus=openButton;show(currentId,true);document.getElementById('walk-close').focus({preventScroll:true});});
document.getElementById('walk-close').addEventListener('click',close);
document.getElementById('walk-prev').addEventListener('click',()=>move(-1));
document.getElementById('walk-next').addEventListener('click',()=>move(1));
selector.addEventListener('change',()=>show(selector.value,true));
if(graph){
  graph.addEventListener('click',event=>{const node=event.target.closest('[data-node-id]');if(!node||!byId.has(node.dataset.nodeId))return;event.preventDefault();event.stopImmediatePropagation();returnFocus=node;show(node.dataset.nodeId,false);document.getElementById('walk-close').focus({preventScroll:true});},true);
  graph.addEventListener('keydown',event=>{if(event.key!=='Enter'&&event.key!==' ')return;const node=event.target.closest('[data-node-id]');if(!node||!byId.has(node.dataset.nodeId))return;event.preventDefault();event.stopImmediatePropagation();returnFocus=node;show(node.dataset.nodeId,false);document.getElementById('walk-close').focus({preventScroll:true});},true);
  graph.addEventListener('pointerover',event=>{if(!panel.hidden)return;const node=event.target.closest('[data-node-id]');const step=node&&byId.get(node.dataset.nodeId);if(!step)return;tip.replaceChildren(element('strong',(step.number?step.number+'. ':'')+step.title),element('span',step.description+' Click or press Enter for owners, handoffs and failure rules.'));tip.hidden=false;});
  graph.addEventListener('pointerout',event=>{const from=event.target.closest('[data-node-id]');const target=event.relatedTarget;const to=target&&target.closest?target.closest('[data-node-id]'):null;if(from!==to)tip.hidden=true;});
}
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&!panel.hidden){event.preventDefault();close();}},true);
window.assessmentWalkthrough=Object.freeze({show,close,count:numbered.length});
})();
</script>
`;
  if (!base.includes('</body>')) throw new Error('Delivered graph has no body closing tag');
  const result = base.replace('</body>', extension.replace('__DATA__', encoded) + '\n</body>').replace(/^[\t ]+$/gm, '');
  writeFileSync(join(directory, 'assessment-durability.html'), result);
  process.stdout.write('Built standalone HTML with 23 numbered steps and explicit acceptance/failure/delivery details.\n');
}
buildWalkthrough();
