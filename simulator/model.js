(function (root, factory) {
  const api = factory(typeof module === 'object' && module.exports ? require('./catalog.js') : root.DmcCatalog);
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.DmcSimulator = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function (catalog) {
  'use strict';
  const WIDTH = 240, HEIGHT = 320;
  const byId = new Map(catalog.entries.map(entry => [entry.id, entry]));
  const screens = ['measurement', 'settings', 'history', 'about', 'alerts'];
  const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
  const ascii = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').normalize('NFC');
  function label(id, language = 'pt', variant = 'compact') {
    const entry = byId.get(id);
    if (!entry) throw new Error('Unknown label: ' + id);
    if (language === 'en') return entry.en;
    if (language !== 'pt') throw new Error('Unknown language');
    if (!['full','compact','ascii'].includes(variant)) throw new Error('Unknown variant');
    return variant === 'full' ? entry.pt : variant === 'ascii' ? ascii(entry.compact) : entry.compact;
  }
  function byteBudget(entry, text) {
    const bytes = new TextEncoder().encode(text.normalize('NFC')).length;
    const original = new TextEncoder().encode(entry.en).length;
    return {bytes, withNul: bytes + 1, original,
      withinOriginalLength: entry.occurrences.length ? bytes <= original : null,
      allocationKnown: false, nonAscii: [...new Set([...text].filter(c => c.codePointAt(0) > 127))]};
  }
  function normalize(options = {}) {
    const o = {screen:'measurement', language:'pt', variant:'compact', font:16,
      family:'sans', grid:false, alert:'charging', override:null, ...options};
    if (!screens.includes(o.screen) || !['pt','en'].includes(o.language) ||
        !['full','compact','ascii'].includes(o.variant) || ![12,16,24,32].includes(Number(o.font)) ||
        !['sans','mono'].includes(o.family) || !['charging','battery','saved'].includes(o.alert)) throw new Error('Invalid simulator option');
    o.font = Number(o.font);
    return o;
  }
  // Each text has a declared box for browser measurement. No auto-fit or ellipsis.
  function scene(options) {
    const o = normalize(options), t = id => label(id,o.language,o.variant);
    const lines = [], shapes = [];
    const text = (id, x,y,w, content, size=o.font, color='#eaf3ee', maxHeight=22) =>
      lines.push({id,x,y,w,text:content,size,color,maxHeight});
    const shape = value => shapes.push(value);
    const rect = (x,y,w,h,fill,rx=0) => shape(`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${fill}"/>`);
    rect(0,0,240,320,'#112820');
    rect(0,0,240,28,'#0b1d17');
    text('status',12,19,155,'DMC-100  /  DEMO',10,'#91b4a4',14);
    shape('<rect x="204" y="9" width="21" height="10" rx="2" fill="none" stroke="#93c8ae"/><rect x="226" y="12" width="2" height="4" fill="#93c8ae"/><rect x="207" y="12" width="14" height="4" fill="#93c8ae"/>');
    text('title',12,59,216,t(o.screen==='alerts' ? o.alert==='charging'?'charging':o.alert==='battery'?'lowBattery':'saved' : o.screen),o.font,'#ffffff',32);
    rect(12,74,216,1,'#3c5c4e');
    if (o.screen==='measurement') {
      text('mode',14,99,180,'AC  ·  AUTO',12,'#9ee3ba',16);
      text('value',12,151,184,'230.4',48,'#ffffff',58);
      text('unit',195,149,32,'V',28,'#9ee3ba',36);
      text('range',14,187,100,t('range'),o.font,'#a4c6b5');
      text('rangeValue',126,187,100,'750.0 V',14);
      rect(12,204,216,56,'#18392d',5);
      shape('<path d="M14 234 L29 230 L44 238 L59 225 L74 233 L89 223 L104 235 L119 227 L134 234 L149 224 L164 231 L179 220 L194 229 L209 222 L226 226" fill="none" stroke="#a5e4bd" stroke-width="2"/>');
      text('demo',14,283,210,t('demo'),11,'#91b4a4',16);
    } else if (o.screen==='settings') {
      [['language',o.language==='en'?'English':t('languageValue')], ['brightness','80%'],
       ['temperature','°C'], ['shutdownAuto','15 min']].forEach(([id,value],i) => {
        const y=98+i*46;
        text(id,14,y,210,t(id));
        text(id+'Value',14,y+19,210,value,12,'#a5e4bd',16);
        rect(12,y+28,216,1,'#2f4e40');
      });
    } else if (o.screen==='history') {
      text('lastSamples',14,98,210,t('lastSamples'),12,'#a4c6b5',16);
      ['230.4','229.8','230.1'].forEach((value,i) => {
        const y=120+i*46;
        rect(12,y,216,40,i===0?'#24533d':'#18392d',4);
        text('sample'+i,22,y+25,112,value+' V',22,'#fff',28);
        text('time'+i,162,y+25,56,['10:32','10:31','10:30'][i],12,'#b6d5c4',16);
      });
      text('records',14,278,210,t('records')+'  03',o.font,'#a4c6b5');
    } else if (o.screen==='about') {
      [['model','DMC-100'],['version','V1.4'],['authorial','DMC100-PTBR']].forEach(([id,value],i)=>{
        const y=100+i*55;
        text(id,14,y,210,t(id),o.font,'#a4c6b5');
        text(id+'Value',14,y+23,210,value,18,'#fff',24);
      });
      text('review',14,279,210,t('review'),12,'#a5e4bd',16);
    } else {
      rect(83,93,74,36,'#244b38',5);
      shape('<rect x="93" y="104" width="49" height="14" rx="2" fill="none" stroke="#b5e6bd"/><rect x="143" y="108" width="4" height="6" fill="#b5e6bd"/><rect x="97" y="108" width="34" height="6" fill="#b5e6bd"/>');
      const id=o.alert==='charging'?'chargingWarning':o.alert==='battery'?'lowBattery':'saved';
      // Fixed authored lines: intentionally allow font stress to reveal overflow.
      const message=t(id);
      const split=o.alert==='charging' ? (o.language==='en' ? ['Do not use','while charging'] :
        o.variant==='full' ? ['Não utilize durante','o carregamento'] : o.variant==='ascii' ? ['Nao usar durante','a carga'] : ['Não usar durante','a carga']) : [message];
      split.forEach((line,i)=>text('message'+i,16,175+i*34,208,line,o.font,'#ffe1a6',30));
      text('demo',14,277,210,t('demo'),11,'#91b4a4',16);
    }
    rect(0,297,240,23,'#0b1d17');
    text('return',12,313,128,'‹ '+t('return'),12,'#c9dfd2',16);
    text('footer',155,313,75,'UI STUDY',10,'#91b4a4',14);
    if (o.override) {
      const target=lines.find(l=>l.id==='title');
      if (target) target.text=[...String(o.override).normalize('NFC')].slice(0,160).join('');
    }
    return {options:o,lines,shapes};
  }
  function render(options) {
    const s=scene(options), family=s.options.family==='mono'?'Consolas, monospace':'Arial, sans-serif';
    const grid=s.options.grid ? '<defs><pattern id="grid" width="8" height="8" patternUnits="userSpaceOnUse"><path d="M8 0H0V8" fill="none" stroke="#a5e4bd" stroke-opacity="0.17" stroke-width="0.5"/></pattern></defs><rect width="240" height="320" fill="url(#grid)"/>' : '';
    return `<svg xmlns="http://www.w3.org/2000/svg" width="${WIDTH}" height="${HEIGHT}" viewBox="0 0 ${WIDTH} ${HEIGHT}" role="img" aria-label="${escape(s.options.screen+' '+s.options.language+' — authored offline study')}" style="overflow:hidden"><title>Authorial UI study — synthetic readings</title>${s.shapes.join('')}${grid}<g font-family="${family}">${s.lines.map(l=>`<text x="${l.x}" y="${l.y}" font-size="${l.size}" fill="${l.color}" data-label="${escape(l.id)}" data-max-width="${l.w}" data-max-height="${l.maxHeight}">${escape(l.text)}</text>`).join('')}</g></svg>`;
  }
  return {WIDTH,HEIGHT,catalog,screens,label,byteBudget,normalize,scene,render,escape,ascii};
});
