/* Uses the same renderer as the workbench; no screenshot of proprietary art. */
const galleryNames={measurement:'01 / Medição',settings:'02 / Configurações',history:'03 / Histórico',about:'04 / Sobre'};
for(const [screen,name] of Object.entries(galleryNames)) {
  const section=document.createElement('section');section.dataset.screen=screen;
  const title=document.createElement('h2');title.textContent=name;section.append(title);
  const pair=document.createElement('div');pair.className='pair';
  for(const language of ['en','pt']) {
    const column=document.createElement('div'),label=document.createElement('div');label.className='language';
    label.textContent=language==='en'?'ENGLISH':'PORTUGUÊS';const note=document.createElement('span');note.textContent='240 × 320';label.append(note);
    const bezel=document.createElement('div');bezel.className='bezel';bezel.innerHTML=DmcSimulator.render({screen,language});column.append(label,bezel);pair.append(column);
  }
  const caption=document.createElement('p');caption.className='caption';caption.textContent='Fonte de 16 px · proposta compacta com acentos · desenho autoral';
  section.append(pair,caption);document.getElementById('gallery').append(section);
}
