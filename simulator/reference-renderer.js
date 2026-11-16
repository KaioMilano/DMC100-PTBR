(function(root,factory){const api=factory(typeof module==='object'&&module.exports?require('./model.js'):root.DmcSimulator,typeof module==='object'&&module.exports?require('./navigation.js'):root.DmcNavigation,typeof module==='object'&&module.exports?require('./navigation-catalog.js'):root.DmcNavigationCatalog);if(typeof module==='object'&&module.exports)module.exports=api;else root.DmcReference=api;})(globalThis,function(M,N,C){
  'use strict';
  const ids=new Map(C.entries.map(e=>[e.id,e]));
  function t(id,language,variant){const e=ids.get(id);if(!e)throw new Error('Unknown reference label');return language==='zh'?e.zh:language==='en'?e.en:variant==='full'?e.pt:variant==='ascii'?M.ascii(e.compact):e.compact;}
  function scene(state,options={}){
    const o={language:'pt',font:16,variant:'compact',family:'sans',...options};M.normalize({...o,language:o.language==='zh'?'en':o.language,screen:'measurement'});
    const shapes=[],lines=[],hotspots=[],label=id=>t(id,o.language,o.variant);
    const rect=(x,y,w,h,fill,stroke='none',rx=0)=>shapes.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${fill}" stroke="${stroke}"/>`);
    const text=(id,x,y,w,value,size=o.font,color='#34404c',height=24)=>lines.push({id,x,y,w,text:value,size,color,maxHeight:height});
    const box=(action,index,x,y,w,h)=>hotspots.push({action,index,x,y,w,h});
    rect(0,0,240,320,state.power?'#f5f7f8':'#142129');
    if(!state.power){text('power',30,155,180,'DMC100-PTBR',19,'#9fb3bc');text('off',40,184,160,'OFFLINE / DEMO',12,'#9fb3bc');return{shapes,lines,hotspots,options:o};}
    if(state.area==='measurement'){
      const d=N.display(state);text('demo',8,15,110,'SIM',10,'#738b9b',14);
      rect(211,7,20,10,'none','#8398a8',1);rect(214,10,12,4,'#76c9e9');
      text('mode',77,59,150,d.title==='TEMP'?d.unit:d.title,d.title.length>5?22:30,'#455b70',38);
      if(state.held)text('hold',10,34,65,'HOLD',12,'#168eb7',18);
      shapes.push('<path d="M14 75H226 M14 151H226" stroke="#39b7e8" stroke-width="3" fill="none"/>');
      text('value',18,132,194,d.value,44,'#506a80',54);text('unit',193,143,39,d.unit,12,'#536b7c',18);
      ['min','max'].forEach((id,i)=>{const x=15+i*111;rect(x,163,99,65,'#f1f5f5','#bed0db',5);text(id,x+30,182,70,label(id),14,i?'#b07972':'#7c9995',20);text(id+'Value',x+8,214,88,d.value,18,'#7f929e',24);});
      N.modes.forEach((mode,i)=>{const x=5+i*39;rect(x,251,35,31,i===state.mode?'#39b7e8':'#eff4f8','#bcced9',4);text('modeIcon'+i,x+5,271,28,['A','V','Ω','C','Hz','NCV'][i],i===5?10:14,i===state.mode?'#fff':'#7892a5',18);box('MODE_SELECT',i,x,248,37,38);});
      text('synthetic',14,310,215,label('demo'),10,'#8297a5',14);
    }else{
      N.tabs.forEach((tab,i)=>{const x=8+i*59;rect(x,8,44,38,'#f5f7f8',i===state.tab?'#25b6e9':'#c0cdd7',5);text('tabIcon'+i,x+14,34,28,['≡','⚙','R','i'][i],22,i===state.tab?'#26afe4':'#8497a7',27);box('GO',tab,x,7,45,40);});
      const title=label(N.tabs[state.tab]);
      shapes.push('<path d="M7 62H140L155 84H7Z" fill="#2bb9ec"/><path d="M157 83H233" stroke="#a5b2bb" stroke-width="2"/>');
      text('title',13,78,132,title,o.font,'#fff',28);
      if(state.tab===0){
        text('columnMode',41,112,80,label('modeColumn'),14,'#8497a7');text('columnValue',125,112,106,label('measurement'),14,'#8497a7');
        state.records.slice(0,6).forEach((r,i)=>{const y=144+i*29;text('rowNumber'+i,13,y,22,String(i+1)+'.',14,'#94a4ae');text('rowMode'+i,41,y,77,r.mode,14);text('rowValue'+i,124,y,75,r.value,14);text('rowUnit'+i,201,y,34,r.unit,12);});
      }else if(state.tab===1){
        const names=['language','brightness','shutdownAuto'];text('settingTitle',27,127,205,label(names[state.page]),o.font,'#6b8294');
        const options=state.page===0?N.locales.map(l=>label(l.labelId)+(l.proposed?' *':'')):state.page===1?['20%','40%','60%','80%','100%','°C','°F']:[label('off'),'5 min','15 min','30 min'];
        const selected=state.page===0?state.settings.language:state.page===1?state.settings.brightness:state.settings.auto;
        if(state.page===1)text('temperatureTitle',18,150,218,label('temperature'),12,'#8999a7',18);
        const start=state.page===1?174:166,step=state.page===1?17:29;
        options.forEach((value,i)=>{const y=start+i*step;const active=state.focus==='language-confirm'?state.pendingLanguage===i:state.focus==='options'?state.option===i:state.page===1?(i<5?selected===i:(i===5?'°C':'°F')===state.settings.unit):selected===i;
          rect(26,y-11,11,11,active?'#2bb9ec':'none','#b0c0cd');text('option'+i,45,y,179,value,state.page===1?12:o.font,'#73899a',state.page===1?18:24);box('OPTION',i,21,y-16,209,step);});
        if(state.page===0){
          if(state.focus==='language-confirm'){
            text('applyLanguage',20,252,214,label('applyLanguage'),13,'#3b718b',20);
            [['confirm','APPLY_LANGUAGE'],['cancel','CANCEL_LANGUAGE']].forEach(([id,action],i)=>{const x=19+i*105;rect(x,268,98,25,i?'#a4b3bf':'#2bb9ec','none',3);text(id,x+8,285,90,label(id),13,'#fff',20);box(action,0,x,268,98,25);});
          }else text('languageProposal',20,257,214,'* '+label('languageProposal'),10,'#7e91a0',16);
        }
        for(let i=0;i<3;i++){rect(105+i*13,299,6,6,i===state.page?'#2bb9ec':'#afbfc9','none',3);box('PAGE',i,100+i*13,292,13,22);}
      }else if(state.tab===2){
        text('notice',63,137,160,'△ '+label('notice'),20,'#c49661',28);
        const msg=o.language==='zh'?['重置所有设置？']:o.language==='en'?['Reset all','settings?']:o.variant==='full'?['Restaurar todas','as configurações?']:o.variant==='ascii'?['Restaurar','os ajustes?']:['Restaurar','os ajustes?'];
        msg.forEach((line,i)=>text('resetMessage'+i,45,174+i*25,190,line,o.font,'#8b99a2'));
        ['reset','return'].forEach((id,i)=>{rect(65,225+i*34,111,25,state.focus==='confirm'&&state.option===i?'#2bb9ec':'#9eacb6','none',2);text(id,76,244+i*34,99,label(id),14,'#fff',20);box(i?'BACK':'RESET_CONFIRM',0,65,225+i*34,111,25);});
      }else{
        text('brand',39,162,184,'DMC-100',28,'#29afd9',36);text('authorial',40,193,188,label('authorial'),12,'#8193a1',18);
        text('version',51,230,180,'DMC-100 V1.3',16,'#7c8e9e');text('reference',25,270,210,o.language==='zh'?'视频参考 · 原创布局':o.language==='en'?'Video reference · authored':'Referência do vídeo · autoral',11,'#8a9ca9',16);
      }
      text('focus',9,318,222,label('demo'),9,'#879ba8',12);
    }
    return{shapes,lines,hotspots,options:o};
  }
  function render(state,options){const s=scene(state,options),family=s.options.family==='mono'?'Consolas, monospace':'Arial, sans-serif';return `<svg xmlns="http://www.w3.org/2000/svg" width="240" height="320" viewBox="0 0 240 320" style="overflow:hidden" role="img" aria-label="${M.escape((state.area==='measurement'?'Measurement':N.tabs[state.tab])+' '+s.options.language+' — authorial V1.3 reference')}"><title>Authorial navigation model; synthetic data</title>${s.shapes.join('')}<g font-family="${family}">${s.lines.map(l=>`<text x="${l.x}" y="${l.y}" font-size="${l.size}" fill="${l.color}" data-label="${M.escape(l.id)}" data-max-width="${l.w}" data-max-height="${l.maxHeight}">${M.escape(l.text)}</text>`).join('')}</g>${s.hotspots.map(h=>`<rect x="${h.x}" y="${h.y}" width="${h.w}" height="${h.h}" fill="transparent" data-action="${h.action}" data-index="${M.escape(h.index)}"/>`).join('')}</svg>`;}
  return{scene,render,t,catalog:C};
});
