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
    ['portuguese','Portuguese (Brazil)','Português (Brasil)','Português (BR)','project-proposal','terceira opção proposta; não existe no firmware analisado'],
    ['languageProposal','PT-BR: project proposal','PT-BR: proposta do projeto','PT-BR: proposta do projeto','project-proposal',''],
    ['applyLanguage','Apply language?','Aplicar idioma?','Aplicar idioma?','authorial-label','confirmação somente no simulador'],
    ['confirm','Confirm','Confirmar','Confirmar','authorial-label',''],
    ['cancel','Cancel','Cancelar','Cancelar','authorial-label',''],
  ].map(([id,en,pt,compact,evidence,context])=>({id,en,pt,compact,evidence,context,occurrences:[]}));
  extra.find(e=>e.id==='modeColumn').occurrences=[0xadf8];
  // Authored Chinese preview. Not extracted/manufacturer-approved translations.
  const zh={language:'语言',english:'英语',brightness:'亮度',temperature:'温度单位',shutdownAuto:'自动关机',settings:'系统设置',history:'历史记录',measurement:'测量',about:'关于',return:'返回',saved:'数据已保存',lowBattery:'电量不足',shutdown:'关机',chargingWarning:'充电时请勿使用',reset:'重置',range:'量程',records:'记录',model:'型号',version:'参考固件',languageValue:'巴西葡萄牙语',demo:'模拟数据',charging:'充电中',lastSamples:'最近样本',authorial:'原创界面',review:'翻译研究',min:'最小',max:'最大',modeColumn:'档位',notice:'注意',resetNotice:'重置所有设置',chinese:'简体中文',simulation:'模拟',off:'关闭',portuguese:'葡萄牙语（巴西）',languageProposal:'PT-BR：项目提案',applyLanguage:'应用语言？',confirm:'确认',cancel:'取消'};
  return{fingerprint:base.fingerprint,entries:[...base.entries,...extra].map(e=>({...e,zh:zh[e.id],zhEvidence:'authored-preview-unreviewed'})),videoReference:'Private V1.3 video; no media included'};
});
