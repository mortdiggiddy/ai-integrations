import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';

const directory = dirname(fileURLToPath(import.meta.url));
const executable = process.env.ARCHIFY_CHROME;
if (!executable) throw new Error('Supply an existing browser through ARCHIFY_CHROME');
const profile = mkdtempSync(join(tmpdir(), 'assessment-diagram-browser-'));
const browser = spawn(executable, ['--headless', '--no-sandbox', '--disable-dev-shm-usage', '--disable-background-networking', '--remote-debugging-port=0', '--user-data-dir='+profile, 'about:blank'], {stdio:['ignore','ignore','pipe'], env:process.env});
let socket;
let stderr = '';
let counter = 0;
const pending = new Map();
const errors = [];
const network = [];
const checks = [];
let session;

/** Send a DevTools request and reject on an explicit browser error or timeout. */
function send(method, params = {}, sessionId = session) {
  const id = ++counter;
  return new Promise((resolve,reject)=>{
    const timer = setTimeout(()=>{pending.delete(id);reject(new Error('DevTools timeout: '+method));},12000);
    pending.set(id,{resolve,reject,timer});
    socket.send(JSON.stringify({id,method,params,...(sessionId?{sessionId}:{})}));
  });
}

/** Evaluate an expression and return its serialized value, refusing script errors. */
async function evaluate(expression) {
  const result = await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
  if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
  return result.result.value;
}

/** Record one required behavior and fail the inspection if it is false. */
function check(name, pass, evidence) {
  checks.push({name,pass,evidence});
  if (!pass) throw new Error('Inspection failed: '+name+' '+JSON.stringify(evidence));
}

/** Capture the current viewport as a browser-generated review image. */
async function capture(name) {
  const result = await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
  writeFileSync(join(directory,name+'.png'),Buffer.from(result.data,'base64'));
}

/** Inspect the extended HTML in the existing browser without installing packages. */
async function inspect() {
  const endpoint = await new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>reject(new Error('Browser did not expose DevTools: '+stderr.slice(-1200))),12000);
    browser.stderr.on('data',chunk=>{
      stderr+=chunk.toString();
      const match=stderr.match(/DevTools listening on (ws:\/\/[^\s]+)/);
      if(match){clearTimeout(timer);resolve(match[1]);}
    });
    browser.on('exit',(code)=>{clearTimeout(timer);reject(new Error('Browser exited '+code+': '+stderr.slice(-1200)));});
  });
  socket = new WebSocket(endpoint);
  await new Promise((resolve,reject)=>{socket.addEventListener('open',resolve,{once:true});socket.addEventListener('error',reject,{once:true});});
  socket.addEventListener('message',event=>{
    const message=JSON.parse(event.data);
    if(message.id){const request=pending.get(message.id);if(request){clearTimeout(request.timer);pending.delete(message.id);message.error?request.reject(new Error(JSON.stringify(message.error))):request.resolve(message.result||{});}}
    else if(message.method==='Runtime.exceptionThrown') errors.push(message.params.exceptionDetails);
    else if(message.method==='Network.requestWillBeSent') network.push(message.params.request.url);
  });
  const target=await send('Target.createTarget',{url:'about:blank'},null);
  session=(await send('Target.attachToTarget',{targetId:target.targetId,flatten:true},null)).sessionId;
  await send('Page.enable');
  await send('Runtime.enable');
  await send('Network.enable');
  await send('Emulation.setDeviceMetricsOverride',{width:1440,height:900,deviceScaleFactor:1,mobile:false});
  const output=join(directory,'assessment-durability.html');
  await send('Page.navigate',{url:pathToFileURL(output).href});
  let ready=false;
  for(let n=0;n<40;n++){ready=await evaluate("typeof window.assessmentWalkthrough === 'object'");if(ready)break;await new Promise(resolve=>setTimeout(resolve,100));}
  check('Walkthrough initialized',ready);
  await evaluate('document.fonts.ready.then(()=>true)');
  const inventory=await evaluate("({steps:assessmentWalkthrough.count,nodes:document.querySelectorAll('.diagram-container > svg [data-node-id]').length,options:document.querySelector('#walk-select').options.length})");
  check('Complete numbered/detail inventory',inventory.steps===23&&inventory.options===23&&inventory.nodes===26,inventory);
  for(const [width,height] of [[1440,900],[1600,1000],[1920,1080],[2048,1320]]){
    await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});
    const bounds=await evaluate("({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,height:innerHeight,scrollHeight:document.documentElement.scrollHeight})");
    check('No horizontal overflow at '+width,bounds.scrollWidth<=bounds.width,bounds);
  }
  await send('Emulation.setDeviceMetricsOverride',{width:1440,height:900,deviceScaleFactor:1,mobile:false});
  await evaluate("document.documentElement.setAttribute('data-theme','dark');window.scrollTo(0,0);assessmentWalkthrough.close()");
  await capture('overview-dark');
  await evaluate("document.documentElement.setAttribute('data-theme','light')");
  await capture('overview-light');
  await evaluate("document.documentElement.setAttribute('data-theme','dark');document.querySelector('.diagram-container > svg [data-node-id=\"s11\"]').scrollIntoView({block:'center'});true");
  const point=await evaluate("(()=>{const r=document.querySelector('.diagram-container > svg [data-node-id=\"s11\"]').getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()");
  await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:point.x,y:point.y});
  check('Real pointer hover shows description',await evaluate("!document.querySelector('#walk-tip').hidden"));
  await send('Input.dispatchMouseEvent',{type:'mousePressed',x:point.x,y:point.y,button:'left',clickCount:1});
  await send('Input.dispatchMouseEvent',{type:'mouseReleased',x:point.x,y:point.y,button:'left',clickCount:1});
  check('Real click opens full handoff details',await evaluate("!document.querySelector('#walk-panel').hidden&&document.querySelector('#walk-title').textContent.startsWith('11.')&&document.querySelector('#walk-content').textContent.includes('not durable intent admission')"));
  await capture('capture-details');
  await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Escape',code:'Escape',windowsVirtualKeyCode:27});
  await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Escape',code:'Escape',windowsVirtualKeyCode:27});
  check('Escape closes details',await evaluate("document.querySelector('#walk-panel').hidden"));
  await evaluate("document.querySelector('.diagram-container > svg [data-node-id=\"s17\"]').focus();true");
  await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});
  await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});
  check('Keyboard opens outcome gap details',await evaluate("document.querySelector('#walk-title').textContent.startsWith('17.')&&!document.querySelector('#walk-panel').hidden"));
  await evaluate("assessmentWalkthrough.show('s17',true)");
  await capture('outcome-gap-details');
  await evaluate("document.querySelector('#walk-next').click()");
  check('Next advances to 18',await evaluate("document.querySelector('#walk-title').textContent.startsWith('18.')"));
  await evaluate("document.querySelector('#walk-prev').click()");
  check('Previous returns to 17',await evaluate("document.querySelector('#walk-title').textContent.startsWith('17.')"));
  await evaluate("document.querySelector('#walk-select').value='s23';document.querySelector('#walk-select').dispatchEvent(new Event('change'));true");
  check('Jump reaches retention',await evaluate("document.querySelector('#walk-title').textContent.startsWith('23.')"));
  await evaluate("assessmentWalkthrough.show('completion-head',true)");
  check('Separate completion acceptance detail',await evaluate("document.querySelector('#walk-domain').textContent==='Temporal authority'&&document.querySelector('#walk-content').textContent.includes('checkpoint service holds bytes')"));
  await evaluate("assessmentWalkthrough.show('park',true)");
  check('Unresolved action policy preserved',await evaluate("document.querySelector('#walk-content').textContent.includes('abort-only action proposal was not approved')"));
  const urls=network.filter(url=>/^https?:/.test(url));
  check('No automatic external network request',urls.length===0,urls);
  check('No browser script exceptions',errors.length===0,errors);
  const bytes=readFileSync(output);
  const receipt={status:'pass',artifact:'assessment-durability.html',sha256:createHash('sha256').update(bytes).digest('hex'),checks,viewports:[[1440,900],[1600,1000],[1920,1080],[2048,1320]],captures:['overview-dark.png','overview-light.png','capture-details.png','outcome-gap-details.png'],scope:'Extended HTML interactions and viewport bounds; not runtime architecture qualification.'};
  writeFileSync(join(directory,'walkthrough-browser.json'),JSON.stringify(receipt,null,2)+'\n');
  process.stdout.write(JSON.stringify(receipt)+'\n');
}
try { await inspect(); }
catch(error) { writeFileSync(join(directory,'walkthrough-browser-failure.json'),JSON.stringify({status:'fail',error:String(error),checks,errors},null,2)+'\n');throw error; }
finally { if(socket)socket.close();browser.kill('SIGTERM');await new Promise(resolve=>setTimeout(resolve,300));rmSync(profile,{recursive:true,force:true}); }
