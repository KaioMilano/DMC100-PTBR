for(const [area,name] of Object.entries({measurement:'01 / Medição',settings:'02 / Configurações — idioma',history:'03 / Histórico',about:'04 / Sobre'})){
  const state=DmcNavigation.transition(DmcNavigation.initial(),{type:'GO',area}),section=document.createElement('section');section.dataset.area=area;
  const title=document.createElement('h2');title.textContent=name;const pair=document.createElement('div');pair.className='pair';
  for(const language of ['en','pt']){const column=document.createElement('div'),label=document.createElement('div'),bezel=document.createElement('div');label.className='language';label.textContent=language==='en'?'ENGLISH':'PORTUGUÊS';bezel.className='bezel';bezel.innerHTML=DmcReference.render(state,{language});column.append(label,bezel);pair.append(column);}
  const caption=document.createElement('p');caption.className='caption';caption.textContent='Composição de referência V1.3 · elementos autorais · textos em revisão';section.append(title,pair,caption);document.getElementById('gallery').append(section);
}
