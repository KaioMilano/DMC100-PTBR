/* Offline only: no fetch, storage, firmware import, or device API. */
(function () {
  'use strict';
  const M=globalThis.DmcSimulator, $=id=>document.getElementById(id);
  let screen='measurement';
  const names={measurement:'Medição',settings:'Configurações',history:'Histórico',about:'Sobre',alerts:'Avisos'};
  const options=language=>({screen,language,variant:$('variant').value,font:Number($('font').value),
    family:$('family').value,grid:$('grid').checked,alert:$('alert').value,
    override:language==='pt' && screen!=='alerts' ? $('custom').value : null});
  function download(content,type,name) {
    const url=URL.createObjectURL(new Blob([content],{type})), a=document.createElement('a');
    a.href=url; a.download=name; a.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  function updateCatalog() {
    const query=$('catalog-search').value.toLocaleLowerCase('pt-BR');
    const entries=M.catalog.entries.filter(e=>[e.en,e.pt,e.compact,...e.occurrences.map(x=>'0x'+x.toString(16).padStart(6,'0'))].join(' ').toLocaleLowerCase('pt-BR').includes(query));
    $('catalog-body').replaceChildren(...entries.map(e=>{
      const row=document.createElement('tr');
      for (const value of [e.en,e.pt,e.compact,e.occurrences.length ? e.occurrences.map(x=>'0x'+x.toString(16).toUpperCase().padStart(6,'0')).join(' · ') : '—']) {
        const td=document.createElement('td');td.textContent=value;row.append(td);
      }
      const tag=document.createElement('small');tag.textContent=e.evidence==='confirmed-v14'?'Confirmado V1.4 · '+e.occurrences.length+' ocorrência(s)':'Rótulo autoral · sem offset';
      if(e.risk==='review') tag.textContent+=' · revisão técnica';
      row.firstChild.append(tag);return row;
    }));
    $('catalog-count').textContent=`${entries.length} textos · duplicatas preservadas`;
  }
  function render() {
    const issues=[];
    for(const lang of ['en','pt']) {
      $(lang).innerHTML=M.render(options(lang));
      for(const node of $(lang).querySelectorAll('text[data-label]')) {
        const box=node.getBBox(), maxWidth=Number(node.dataset.maxWidth),maxHeight=Number(node.dataset.maxHeight);
        if(box.width>maxWidth+0.5 || box.height>maxHeight+0.5 || box.x<0 || box.x+box.width>240.5 || box.y<0 || box.y+box.height>320.5) {
          node.classList.add('overflow');issues.push({language:lang,id:node.dataset.label,width:Math.round(box.width),height:Math.round(box.height),maxWidth,maxHeight});
        }
      }
    }
    $('screen-name').textContent=names[screen];
    $('alert-control').hidden=screen!=='alerts';
    $('custom').disabled=screen==='alerts';
    const diag=$('diagnostics');diag.replaceChildren();diag.classList.toggle('warn',issues.length>0);
    const headline=document.createElement('p');
    headline.textContent=issues.length ? `${issues.length} texto(s) excedem a caixa de teste. Nada foi reduzido automaticamente.` : 'Sem excesso nas caixas de texto deste cenário. Não valida a fonte do equipamento.';
    diag.append(headline);
    if(issues.length) {
      const ul=document.createElement('ul');
      for(const issue of issues.slice(0,5)) {const li=document.createElement('li');li.textContent=`${issue.language.toUpperCase()} / ${issue.id}: ${issue.width} × ${issue.height} px; caixa ${issue.maxWidth} × ${issue.maxHeight} px`;ul.append(li);}
      diag.append(ul);
    }
    const id=screen==='alerts' ? $('alert').value==='charging'?'chargingWarning':$('alert').value==='battery'?'lowBattery':'saved' : screen;
    const entry=M.catalog.entries.find(e=>e.id===id), value=(screen!=='alerts' && $('custom').value) || M.label(id,'pt',$('variant').value), b=M.byteBudget(entry,value);
    $('budget').replaceChildren();const strong=document.createElement('strong');strong.textContent=b.bytes+' bytes UTF-8';
    const line=document.createElement('div');line.textContent=`${b.withNul} com NUL · original: ${b.original} bytes`;
    const note=document.createElement('small');note.textContent='Texto analisado: “'+value+'”. '+(b.withinOriginalLength?'Dentro do comprimento original. ':'Excede o comprimento original. ')+'Não é tamanho de alocação nem prova de glifos. '+(b.nonAscii.length?'Acentos/símbolos: '+b.nonAscii.join(' '):'Somente ASCII neste texto.');
    $('budget').append(strong,line,note);
    $('dependencies').textContent=screen==='about' ? 'A rotina de informações usa primitivas e texto. Ícone global de bateria e composição final ainda exigem rastreamento; sem dependência JPEG direta demonstrada nesta rotina.' : screen==='alerts' ? 'A tela de carregamento usa primitivas e texto nas referências consultadas. Avisos e ícones globais continuam em revisão.' : screen==='history' ? 'O menu que leva ao histórico usa imagens de fundo. A dependência JPEG da página de registros ainda não foi isolada. A tabela aqui é autoral.' : screen==='settings' ? 'Menu e navegação referenciam decorat/menu.jpg e decorate/menu.jpg. São substituídos aqui por formas próprias.' : 'Modo, HOLD, setas, bateria, lanterna e NCV têm referências JPEG. Todos os elementos deste protótipo são próprios.';
    globalThis.DmcDiagnostics={screen,issues,budget:b};
  }
  $('screens').addEventListener('click',event=>{
    const button=event.target.closest('button[data-screen]');if(!button)return;
    screen=button.dataset.screen;
    for(const item of $('screens').querySelectorAll('button')) item.setAttribute('aria-pressed',String(item===button));
    render();
  });
  for(const id of ['variant','font','family','grid','alert']) $(id).addEventListener('change',render);
  $('custom').addEventListener('input',render);
  $('scale').addEventListener('change',()=>document.documentElement.style.setProperty('--scale',$('scale').value));
  $('catalog-search').addEventListener('input',updateCatalog);
  for(const button of document.querySelectorAll('[data-export]')) button.addEventListener('click',()=>download(M.render(options(button.dataset.export)),'image/svg+xml',`dmc100-${screen}-${button.dataset.export}.svg`));
  $('export-catalog').addEventListener('click',()=>download(JSON.stringify(M.catalog,null,2),'application/json','dmc100-translations.json'));
  updateCatalog();render();
})();
