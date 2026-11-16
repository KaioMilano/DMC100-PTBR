const {test}=require('node:test'),assert=require('node:assert/strict');
const N=require('../navigation.js'),R=require('../reference-renderer.js');
const step=(s,type,more={})=>N.transition(s,{type,...more});
test('top-level order matches observed history, settings, reset and about',()=>{
  let s=step(N.initial(),'MENU');assert.equal(N.tabs[s.tab],'history');
  for(const tab of ['settings','reset','about','history']){s=step(s,'RIGHT');assert.equal(N.tabs[s.tab],tab);}
  s=step(s,'HOLD');assert.equal(N.tabs[s.tab],'about');
});
test('mode categories and variants change only fixed display fixtures',()=>{
  let s=N.initial();assert.equal(N.display(s).title,'A DC');s=step(s,'MODE');assert.equal(N.display(s).title,'A ~');
  s=step(s,'RIGHT');assert.equal(N.display(s).title,'V DC');s=step(s,'MODE');assert.equal(N.display(s).title,'V ~');
  s=step(s,'RIGHT');assert.equal(N.display(s).id,'resistance');s=step(s,'MODE');assert.equal(N.display(s).id,'continuity');s=step(s,'MODE');assert.equal(N.display(s).id,'diode');
});
test('settings have distinct tab, page and option navigation with back',()=>{
  let s=step(N.initial(),'GO',{area:'settings'});s=step(s,'MODE');assert.equal(s.focus,'pages');
  s=step(s,'RIGHT');assert.equal(s.page,1);s=step(s,'MODE');assert.equal(s.focus,'options');
  s=step(s,'RIGHT');s=step(s,'MODE');assert.equal(s.settings.brightness,4);assert.equal(s.focus,'pages');
  s=step(s,'BACK');assert.equal(s.focus,'tabs');s=step(s,'BACK');assert.equal(s.area,'measurement');
});
test('reset defaults to return and requires explicit confirmation',()=>{
  let s=step(N.initial(),'PAGE',{index:1});s=step(s,'OPTION',{index:0});assert.equal(s.settings.brightness,0);
  s=step(s,'GO',{area:'reset'});s=step(s,'MODE');assert.equal(s.focus,'confirm');assert.equal(s.option,1);
  s=step(s,'MODE');assert.equal(s.settings.brightness,0);
  s=step(s,'MODE');s=step(s,'LEFT');s=step(s,'MODE');assert.equal(s.settings.brightness,3);assert.equal(s.notice,'reset');
});
test('saving and hold are volatile model actions, input states remain unchanged',()=>{
  const original=N.initial(),before=JSON.stringify(original);let s=step(original,'HOLD');assert.equal(s.held,true);
  for(let i=0;i<12;i++)s=step(s,'SAVE');assert.equal(s.records.length,8);assert.equal(original.records.length,6);
  assert.equal(JSON.stringify(original),before);assert.notEqual(s.settings,original.settings);
});
test('powered-off model ignores navigation and toggles back on',()=>{
  let s=step(N.initial(),'POWER');s=step(s,'MENU');assert.equal(s.area,'measurement');assert.equal(s.power,false);
  s=step(s,'POWER');assert.equal(s.power,true);
});
test('invalid navigation options are rejected',()=>{
  for(const event of [{type:'FLASH'},{type:'GO',area:'usb'},{type:'MODE_SELECT',index:99},{type:'PAGE',index:-1},{type:'OPTION',index:0}])assert.throws(()=>N.transition(N.initial(),event));
});
test('accent budgets are explicit hypothetical estimates',()=>{
  assert.equal(N.accentBudget().count,26);assert.equal(N.accentBudget().pairedSquareBytes,6864);assert.equal(N.accentBudget().pairedHalfWidthBytes,3848);
  assert.equal(N.accentBudget('áá').count,1);
});
test('reference renderer retains 240x320 for menus and all variants without assets',()=>{
  for(const area of ['measurement',...N.tabs])for(const language of ['en','pt'])for(const font of [12,16,24,32]){
    const s=step(N.initial(),'GO',{area}),svg=R.render(s,{language,font});assert.match(svg,/width="240" height="320" viewBox="0 0 240 320"/);
    assert.doesNotMatch(svg,/<image|<script|<foreignObject/);
  }
});
test('comparison language changes labels without changing readings',()=>{
  const s=N.initial(),values=language=>R.scene(s,{language}).lines.filter(l=>['value','unit'].includes(l.id)).map(l=>l.text);
  assert.deepEqual(values('en'),values('pt'));assert.deepEqual(values('pt'),['0.000','A']);
});
test('extended catalog has unique IDs and keeps observed offsets',()=>{
  assert.equal(R.catalog.entries.length,33);assert.equal(new Set(R.catalog.entries.map(e=>e.id)).size,33);
  assert.equal(R.catalog.entries.flatMap(e=>e.occurrences).length,21);
  assert.ok(R.catalog.entries.filter(e=>e.evidence==='video-v13').every(e=>e.context&&e.occurrences.length===0));
});
