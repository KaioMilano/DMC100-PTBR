(function(){
  'use strict';const N=DmcNavigation,R=DmcReference,$=id=>document.getElementById(id);let state=N.initial(),longPress=false,timer;
  const titles={measurement:'Medição',history:'Histórico',settings:'Configurações',reset:'Restaurar',about:'Sobre'};
  const options=language=>({language,font:Number($('nav-font').value),variant:$('nav-variant').value});
  function download(data,type,name){const url=URL.createObjectURL(new Blob([data],{type})),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  function render(){
    const area=state.area==='measurement'?'measurement':N.tabs[state.tab],issues=[];
    $('nav-pair').dataset.view=$('nav-language').value;$('nav-title').textContent=(state.power?titles[area]:'Desligado')+' · '+({tabs:'navegar',pages:'escolher subpágina',options:'escolher opção',confirm:'confirmar restauração'})[state.focus];
    for(const language of ['en','pt']){
      $('nav-'+language).innerHTML=R.render(state,options(language));
      for(const text of $('nav-'+language).querySelectorAll('text[data-label]')){const b=text.getBBox();if(b.width>Number(text.dataset.maxWidth)+0.5||b.height>Number(text.dataset.maxHeight)+0.5||b.x<0||b.x+b.width>240.5||b.y<0||b.y+b.height>320.5){text.classList.add('overflow');issues.push({language,id:text.dataset.label,width:Math.round(b.width)});}}
    }
    const diag=$('nav-diagnostics');diag.classList.toggle('warn',issues.length>0);diag.textContent=issues.length?`${issues.length} excesso(s) de texto. Sem ajuste automático. Exemplos: ${issues.slice(0,3).map(i=>i.language+'/'+i.id+' ('+i.width+' px)').join(', ')}.`:'Texto dentro das caixas declaradas. A fonte do firmware continua não emulada.';
    $('nav-feedback').textContent=state.notice==='saved'?'Amostra fictícia adicionada ao histórico desta página.':state.notice==='reset'?'Somente os valores simulados desta página foram restaurados.':state.notice==='setting'?'Opção alterada apenas no modelo local. Não modifica o equipamento.':'';
    $('nav-evidence').textContent=area==='settings'&&state.page>0?'Subpágina inferida da análise estática V1.4; não demonstrada no vídeo V1.3.':'Composição orientada pelo vídeo V1.3, com elementos próprios. Botões, tempos e estados completos ainda exigem conferência.';
    for(const button of document.querySelectorAll('[data-go]'))button.setAttribute('aria-pressed',String(button.dataset.go===area));
    globalThis.DmcNavigatorState={state,issues};
  }
  function send(event){state=N.transition(state,event);render();}
  document.querySelectorAll('[data-go]').forEach(b=>b.addEventListener('click',()=>send({type:'GO',area:b.dataset.go})));
  document.querySelectorAll('[data-page]').forEach(b=>b.addEventListener('click',()=>send({type:'PAGE',index:Number(b.dataset.page)})));
  document.querySelectorAll('[data-key]').forEach(b=>b.addEventListener('click',()=>{if(b.id==='save-menu'&&longPress){longPress=false;return;}send({type:b.dataset.key});}));
  $('menu-toggle').addEventListener('click',()=>send({type:'MENU'}));
  $('save-menu').addEventListener('pointerdown',()=>{longPress=false;timer=setTimeout(()=>{longPress=true;send({type:'MENU'});},600);});
  for(const event of ['pointerup','pointercancel','pointerleave'])$('save-menu').addEventListener(event,()=>clearTimeout(timer));
  for(const language of ['en','pt'])$('nav-'+language).addEventListener('click',event=>{const target=event.target.closest('[data-action]');if(!target)return;const action=target.dataset.action,index=target.dataset.index;
    if(action==='GO')send({type:'GO',area:index});
    else if(action==='RESET_CONFIRM'){if(state.focus==='confirm'&&state.option!==0)state=N.transition(state,{type:'LEFT'});send({type:'MODE'});}
    else send({type:action,index:Number(index)});
  });
  document.addEventListener('keydown',event=>{if(['INPUT','SELECT','TEXTAREA'].includes(event.target.tagName)||event.repeat||event.ctrlKey||event.altKey||event.metaKey||(event.target.tagName==='BUTTON'&&['Enter',' '].includes(event.key)))return;const key=event.key.toLowerCase(),type=key==='s'&&event.shiftKey?'MENU':({arrowleft:'LEFT',arrowright:'RIGHT',enter:'MODE',m:'MODE',h:'HOLD',s:'SAVE',escape:'BACK',p:'POWER'})[key];if(type){event.preventDefault();send({type});}});
  for(const id of ['nav-language','nav-font','nav-variant'])$(id).addEventListener('change',render);
  $('nav-scale').addEventListener('change',()=>document.documentElement.style.setProperty('--scale',$('nav-scale').value));
  $('nav-export-svg').addEventListener('click',()=>download(R.render(state,options('pt')),'image/svg+xml','dmc100-navegacao-ptbr.svg'));
  $('nav-export-catalog').addEventListener('click',()=>download(JSON.stringify(R.catalog,null,2),'application/json','dmc100-catalogo-navegacao.json'));
  $('accent-bytes').textContent=N.accentBudget().pairedSquareBytes.toLocaleString('pt-BR')+' bytes';render();
})();
