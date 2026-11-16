(function(root,factory){const api=factory(typeof module==='object'&&module.exports?require('./catalog.js'):root.DmcCatalog);if(typeof module==='object'&&module.exports)module.exports=api;else root.DmcNavigationCatalog=api;})(globalThis,function(base){
  const extra=[
    ['min','MIN','MÍN','MÍN','video-v13','00:15–00:59'],
    ['max','MAX','MÁX','MÁX','video-v13','00:15–00:59'],
    ['modeColumn','Gera','Modo','Modo','confirmed-v14','cabeçalho observado no vídeo e confirmado como Gera no binário'],
    ['notice','Notice','Aviso','Aviso','video-v13','00:38–00:42'],
    ['resetNotice','Reset all settings','Restaurar todas as configurações','Restaurar ajustes','video-v13','00:38–00:42; frase normalizada'],
    ['chinese','Chinese (simplified)','Chinês simplificado','Chinês (simpl.)','authorial-label','opção chinesa visível; descrição traduzida'],
    ['simulation','SIMULATION','SIMULAÇÃO','SIMULAÇÃO','authorial-label',''],
    ['off','OFF','Desativado','Desativado','static-v14','página não demonstrada no vídeo'],
  ].map(([id,en,pt,compact,evidence,context])=>({id,en,pt,compact,evidence,context,occurrences:[]}));
  extra.find(e=>e.id==='modeColumn').occurrences=[0xadf8];
  return{fingerprint:base.fingerprint,entries:[...base.entries,...extra],videoReference:'Private V1.3 video; no media included'};
});
