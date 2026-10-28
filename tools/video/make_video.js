// Usage: node tools/video/make_video.js tools/video/scenarios/cost.json out.mp4 [baseUrl]
// Records the REAL app with Playwright (no fake UI), overlays Arabic subtitles/cards, encodes 1080x1920 MP4 with ffmpeg.
// Needs: playwright (chromium) and ffmpeg. Serve the site first, e.g. `python3 -m http.server 8130`.
const {chromium}=require('playwright'),fs=require('fs'),os=require('os'),path=require('path'),{execFileSync}=require('child_process');
const [,, scenarioPath, outMp4='out.mp4', base='http://localhost:8130']=process.argv;
if(!scenarioPath){console.error('usage: make_video.js scenario.json out.mp4 [baseUrl]');process.exit(1);}
const S=JSON.parse(fs.readFileSync(scenarioPath,'utf8'));
const FPS=S.fps||20, DUR=S.duration, N=FPS*DUR, lang=S.lang||'ar';
const ease=x=>x<0?0:x>1?1:x*x*(3-2*x), lerp=(a,b,x)=>a+(b-a)*ease(x), seg=(t,a,b)=>(t-a)/(b-a);
const FONT='system-ui,"Noto Sans Arabic","Noto Sans",sans-serif';
const CSS=`.bottom-nav,.compare-float{display:none!important}html{scroll-behavior:auto!important}
#vr-top{position:fixed;top:0;left:0;right:0;height:84px;z-index:99999;display:flex;align-items:center;justify-content:space-between;padding:0 16px;background:linear-gradient(#050a14 70%,rgba(5,10,20,0));color:#fff;font-family:${FONT};direction:rtl}
#vr-top b{font-size:20px;color:#00f2fe;direction:ltr}#vr-top span{font-size:14px;color:#cbd5e1;font-weight:700}
#vr-sub{position:fixed;left:14px;right:14px;bottom:26px;z-index:99999;padding:13px 14px;border-radius:16px;background:rgba(2,6,15,.82);border:1px solid rgba(0,242,254,.35);color:#fff;font:800 18px/1.6 ${FONT};text-align:center;direction:rtl;opacity:0}
#vr-card{position:fixed;inset:0;z-index:100000;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;padding:28px;text-align:center;direction:rtl;color:#fff;font-family:${FONT};background:radial-gradient(circle at 50% 0%,rgba(0,242,254,.22),transparent 55%),#0b1220;opacity:0}
#vr-card .big{font-size:34px;font-weight:900;line-height:1.5}#vr-card .mid{font-size:19px;color:#cbd5e1;line-height:1.8;font-weight:700}
#vr-card .url{font-size:22px;font-weight:900;color:#001116;background:linear-gradient(135deg,#00f2fe,#4facfe);padding:12px 20px;border-radius:14px;direction:ltr}
#vr-card .brand{font-size:26px;font-weight:900;color:#00f2fe;direction:ltr}#vr-card .fine{font-size:13px;color:#94a3b8;line-height:1.7;max-width:300px}`;
const esc=s=>String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const cardHtml=c=>`<div class="brand">⚡ VoltRide</div><div class="big">${esc(c.title)}</div>`+(c.lines?`<div class="mid">${c.lines.map(esc).join('<br>')}</div>`:'')+(c.url?`<div class="url">${esc(c.url)}</div>`:'')+(c.fine?`<div class="fine">${esc(c.fine)}</div>`:'');
(async()=>{
 const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'vrvid-'));
 const b=await chromium.launch();
 const ctx=await b.newContext({viewport:{width:360,height:640},deviceScaleFactor:3,locale:S.locale||'ar-MA'});
 await ctx.addInitScript(l=>{localStorage.setItem('voltride_language',l);localStorage.setItem('voltride_consent','denied');},lang);
 const p=await ctx.newPage();
 await p.goto(base+(S.page||'/index.html'));await p.waitForTimeout(800);
 await p.addStyleTag({content:CSS});
 await p.evaluate(top=>document.body.insertAdjacentHTML('beforeend',`<div id="vr-top"><b>⚡ VoltRide</b><span>${top}</span></div><div id="vr-sub"></div><div id="vr-card"></div>`),S.topLabel||'تجربة حقيقية من التطبيق');
 // sanity checks: each is a JS expression that must be truthy, so the video never shows stale numbers
 for(const a of S.setup||[]) await p.evaluate(a);
 for(const c of S.assert||[]){ if(!await p.evaluate(c)) throw new Error('assertion failed: '+c); }
 // scroll keyframes: [{t, to:"#selector", offset}] interpolated between consecutive keys
 const keys=[];for(const k of S.scroll){const y=await p.evaluate(([s,o])=>document.querySelector(s).getBoundingClientRect().top+scrollY-o,[k.to,k.offset||0]);keys.push({t:k.t,y});}
 const fired=new Set();
 for(let i=0;i<N;i++){
  const t=i/FPS;
  for(const [j,a] of (S.actions||[]).entries()) if(t>=a.t&&!fired.has(j)){fired.add(j);await p.evaluate(a.js);}
  let sc=keys[0].y;for(let k=0;k<keys.length;k++){if(t>=keys[k].t){sc=keys[k].y;if(keys[k+1]&&t<keys[k+1].t)sc=lerp(keys[k].y,keys[k+1].y,seg(t,keys[k].t,keys[k+1].t));}}
  const intro=S.intro&&t<S.intro.until, outro=S.outro&&t>=S.outro.from;
  let cOp=0,cHtml=null;
  if(intro){cOp=t>S.intro.until-.4?1-seg(t,S.intro.until-.4,S.intro.until):1;cHtml=cardHtml(S.intro);}
  if(outro){cOp=t<S.outro.from+.4?seg(t,S.outro.from,S.outro.from+.4):1;cHtml=cardHtml(S.outro);}
  const sub=(S.subs||[]).find(s=>t>=s[0]&&t<s[1]);let sOp=0;if(sub)sOp=Math.min(1,(t-sub[0])/.25,(sub[1]-t)/.25);
  await p.evaluate(([sc,sub,sOp,card,cOp])=>{scrollTo(0,sc);const s=document.getElementById('vr-sub');s.style.opacity=sOp;if(sub!==null)s.textContent=sub;const c=document.getElementById('vr-card');c.style.opacity=cOp;if(card!==null)c.innerHTML=card;},[sc,sub?sub[2]:null,sOp,cHtml,cOp]);
  await p.waitForTimeout(25);
  await p.screenshot({path:path.join(tmp,`f${String(i).padStart(4,'0')}.jpg`),type:'jpeg',quality:92});
 }
 await b.close();
 execFileSync('ffmpeg',['-y','-loglevel','error','-framerate',String(FPS),'-i',path.join(tmp,'f%04d.jpg'),'-vf','scale=1080:1920:flags=lanczos,format=yuv420p','-c:v','libx264','-crf','20','-preset','medium','-movflags','+faststart',outMp4]);
 fs.rmSync(tmp,{recursive:true,force:true});
 console.log('wrote',outMp4);
})().catch(e=>{console.error('FAIL',e.message);process.exit(1)});
