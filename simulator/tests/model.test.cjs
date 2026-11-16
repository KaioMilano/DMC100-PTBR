const {test}=require('node:test');
const assert=require('node:assert/strict');
const M=require('../model.js');

test('catalog preserves observed duplicates and distinguishes authored labels',()=>{
  const entries=M.catalog.entries;
  assert.equal(new Set(entries.map(e=>e.id)).size,entries.length);
  assert.deepEqual(entries.find(e=>e.id==='language').occurrences,[0x5a44,0x6150]);
  assert.deepEqual(entries.find(e=>e.id==='english').occurrences,[0x5a5c,0x60d0,0x72c8]);
  assert.deepEqual(entries.find(e=>e.id==='reset').occurrences,[0x3de4,0xae44]);
  assert.ok(entries.filter(e=>e.evidence==='prototype-only').every(e=>e.occurrences.length===0));
  const offsets=entries.flatMap(e=>e.occurrences);assert.equal(new Set(offsets).size,offsets.length);
});
test('resource families total 72 references, not 72 confirmed images',()=>{
  assert.equal(M.catalog.resources.reduce((n,r)=>n+r.count,0),72);
  assert.ok(M.catalog.resources.every(r=>r.evidence&&r.note));
});
test('render all supported screens, languages, sizes and variants at intrinsic 240 by 320',()=>{
  for(const screen of M.screens) for(const language of ['en','pt'])
    for(const font of [12,16,24,32]) for(const variant of ['full','compact','ascii']) {
      const svg=M.render({screen,language,font,variant});
      assert.match(svg, /width="240" height="320" viewBox="0 0 240 320"/);
      assert.doesNotMatch(svg.replace('http://www.w3.org/2000/svg',''), /<image|<script|<foreignObject|https?:\/\//);
      assert.match(svg, /data-label="title"/);
    }
});
test('accent and abbreviation choices remain distinct',()=>{
  assert.equal(M.label('settings','pt','full'),'Configurações do sistema');
  assert.equal(M.label('settings','pt','compact'),'Configurações');
  assert.equal(M.label('settings','pt','ascii'),'Configuracoes');
  assert.equal(M.label('measurement','en','ascii'),'Measurement');
});
test('byte budget uses NFC UTF-8 and never claims allocation',()=>{
  const measurement=M.catalog.entries.find(e=>e.id==='measurement');
  const result=M.byteBudget(measurement,'Medic\u0327a\u0303o');
  assert.equal(result.bytes,9);assert.equal(result.withNul,10);assert.equal(result.original,11);
  assert.equal(result.allocationKnown,false);
  assert.equal(M.byteBudget(M.catalog.entries.find(e=>e.id==='range'),'Faixa').withinOriginalLength,null);
});
test('unknown states are rejected',()=>{
  for(const options of [{font:0},{screen:'firmware'},{family:'remote'},{variant:'patch'},{language:'xx'}]) assert.throws(()=>M.render(options));
  assert.throws(()=>M.label('unknown'));assert.throws(()=>M.label('about','xx'));
});
test('user text cannot insert SVG markup',()=>{
  const svg=M.render({override:'<script>alert("x")</script>'});
  assert.ok(svg.includes('&lt;script&gt;'));assert.ok(!svg.includes('<script>'));
});
test('synthetic readings and SI units are identical across languages',()=>{
  const values=lang=>M.scene({screen:'measurement',language:lang}).lines.filter(x=>['value','unit','rangeValue'].includes(x.id)).map(x=>x.text);
  assert.deepEqual(values('en'),['230.4','V','750.0 V']);assert.deepEqual(values('pt'),values('en'));
});
test('font stress never silently shrinks labels',()=>{
  const line=M.scene({screen:'settings',font:32,variant:'full'}).lines.find(x=>x.id==='temperature');
  assert.equal(line.size,32);assert.equal(line.text,'Unidade de temperatura');assert.equal(line.w,210);
});
