/* Authorial translations and reviewed metadata, never firmware assets. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.DmcCatalog = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const fingerprint = 'f8eab197553e117a374dc9926989b8ec2105baa8120682bd5c864bda30e8364d';
  // All offsets are FILE offsets in the fingerprint above. Compact = proposal.
  const known = [
    ['language', 'Language', 'Idioma', 'Idioma', [0x5a44, 0x6150], 'settings'],
    ['english', 'English', 'Inglês', 'Inglês', [0x5a5c, 0x60d0, 0x72c8], 'settings'],
    ['brightness', 'Brightness', 'Brilho', 'Brilho', [0x5c00], 'settings'],
    ['temperature', 'Temperature unit', 'Unidade de temperatura', 'Unid. temp.', [0x5c0c], 'settings'],
    ['shutdownAuto', 'AUTO shut_down', 'Desligamento automático', 'Deslig. auto', [0x5900], 'settings'],
    ['settings', 'System settings', 'Configurações do sistema', 'Configurações', [0x6140, 0xae28], 'settings'],
    ['history', 'History record', 'Histórico de registros', 'Histórico', [0xade8], 'history'],
    ['measurement', 'Measurement', 'Medição', 'Medição', [0xae00], 'measurement'],
    ['about', 'About', 'Sobre', 'Sobre', [0xae58], 'about'],
    ['return', 'Return', 'Voltar', 'Voltar', [0x3dec], 'all'],
    ['saved', 'Data saved', 'Dados salvos', 'Dados salvos', [0x4b6c], 'alerts'],
    ['lowBattery', 'Low battery', 'Bateria fraca', 'Bateria fraca', [0x554c], 'alerts'],
    ['shutdown', 'Shutdown', 'Desligar', 'Desligar', [0x5558], 'alerts'],
    ['chargingWarning', 'Do not use while charging', 'Não utilize durante o carregamento', 'Não usar durante a carga', [0xb290], 'alerts'],
    ['reset', 'Reset', 'Restaurar', 'Restaurar', [0x3de4, 0xae44], 'settings'],
  ].map(([id, en, pt, compact, occurrences, screen]) => ({
    id, en, pt, compact, occurrences, screen, evidence: 'confirmed-v14',
    risk: ['chargingWarning', 'lowBattery', 'shutdown', 'reset', 'temperature'].includes(id) ? 'review' : 'label',
  }));
  // These are useful in an authored layout, not claimed as extracted strings.
  const prototype = [
    ['range', 'Range', 'Faixa', 'Faixa', 'measurement'],
    ['records', 'Records', 'Registros', 'Registros', 'history'],
    ['model', 'Model', 'Modelo', 'Modelo', 'about'],
    ['version', 'Reference firmware', 'Firmware de referência', 'FW de referência', 'about'],
    ['languageValue', 'Portuguese (Brazil)', 'Português brasileiro', 'Português (BR)', 'settings'],
    ['demo', 'SIMULATED DATA', 'DADOS SIMULADOS', 'DADOS SIMULADOS', 'all'],
    ['charging', 'Charging', 'Carregando', 'Carregando', 'alerts'],
    ['lastSamples', 'Last three samples', 'Últimas três amostras', 'Últimas amostras', 'history'],
    ['authorial', 'Authored interface', 'Interface autoral', 'Interface autoral', 'about'],
    ['review', 'Translation study', 'Estudo de tradução', 'Estudo de tradução', 'about'],
  ].map(([id, en, pt, compact, screen]) => ({
    id, en, pt, compact, screen, occurrences: [], evidence: 'prototype-only', risk: 'label',
  }));
  const entries = [...known, ...prototype];
  const resources = [
    {group:'decorat / decorate', count:50, purpose:'Molduras, menu, HOLD, setas, lanterna e NCV',
      screens:['measurement','settings','history'], evidence:'caminhos + chamadas comunitárias',
      note:'25 ocorrências por família. Não foi comprovado que todas sejam temas.'},
    {group:'mode / mode_1', count:12, purpose:'Ícones de modo V, R, C, H, L e A',
      screens:['measurement'], evidence:'caminhos + ui_draw_mode_icon', note:'6 ocorrências por família; bitmaps não obtidos.'},
    {group:'cel / cell', count:10, purpose:'Indicadores de bateria, estados 1 a 5',
      screens:['measurement','settings','history','about'], evidence:'caminhos + ui_draw_battery_icon',
      note:'5 ocorrências por família. Uso da bateria em cada tela não foi rastreado integralmente.'},
  ];
  return {fingerprint, entries, resources};
});
