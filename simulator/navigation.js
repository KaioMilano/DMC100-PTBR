/* UI state model only. No sampling, conversions, device IO or safety logic. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.DmcNavigation=api;})(globalThis,function(){
  'use strict';
  const tabs=['history','settings','reset','about'];
  const modes=[
    {id:'A',variants:[{id:'dc',title:'A DC',value:'0.000',unit:'A'},{id:'ac',title:'A ~',value:'0.000',unit:'A'}]},
    {id:'V',variants:[{id:'dc',title:'V DC',value:'0.000',unit:'V'},{id:'ac',title:'V ~',value:'0.000',unit:'V'}]},
    {id:'R',variants:[{id:'resistance',title:'Ω',value:'O.L',unit:'MΩ'},{id:'continuity',title:'CONT',value:'O.L',unit:'Ω'},{id:'diode',title:'DIODE',value:'O.L',unit:'V'}]},
    {id:'C',variants:[{id:'capacitance',title:'C',value:'0.000',unit:'nF'}]},
    {id:'H',variants:[{id:'frequency',title:'Hz',value:'0.000',unit:'Hz'},{id:'temperature',title:'TEMP',value:'23.0',unit:'°C'}]},
    {id:'L',variants:[{id:'live',title:'LIVE',value:'—',unit:''},{id:'ncv',title:'NCV',value:'—',unit:''}]},
  ];
  const initialRecords=()=>[
    {mode:'A ~',value:'0.000',unit:'A'},{mode:'A ~',value:'0.000',unit:'A'},
    {mode:'V ~',value:'230.0',unit:'V'},{mode:'V ~',value:'230.0',unit:'V'},
    {mode:'V DC',value:'0.000',unit:'V'},{mode:'V DC',value:'0.000',unit:'V'}];
  function initial(){return{power:true,area:'measurement',tab:0,focus:'tabs',page:0,option:0,mode:0,variant:0,held:false,settings:{language:1,brightness:3,unit:'°C',auto:2},records:initialRecords(),notice:''};}
  const wrap=(n,length)=>(n+length)%length;
  function display(state){
    const value={...modes[state.mode].variants[state.variant]};
    if(value.id==='temperature'&&state.settings.unit==='°F'){value.value='73.4';value.unit='°F';}
    return value; // Every number is a fixed synthetic fixture, never computed.
  }
  function optionCount(state){return state.page===0?2:state.page===1?7:4;}
  function applyOption(state){
    if(state.page===0)state.settings.language=state.option;
    else if(state.page===1){if(state.option<5)state.settings.brightness=state.option;else state.settings.unit=state.option===5?'°C':'°F';}
    else state.settings.auto=state.option;
  }
  function transition(previous,event){
    const allowed=['HOLD','LEFT','RIGHT','MODE','SAVE','MENU','POWER','BACK','GO','PAGE','OPTION','MODE_SELECT'];
    if(!event||!allowed.includes(event.type))throw new Error('Unknown navigation event');
    const s={...previous,settings:{...previous.settings},records:previous.records.map(r=>({...r})),notice:''};
    if(event.type==='POWER'){s.power=!s.power;return s;}
    if(!s.power)return s;
    if(event.type==='GO'){
      if(event.area==='measurement'){s.area='measurement';s.focus='tabs';return s;}
      if(!tabs.includes(event.area))throw new Error('Unknown area');
      s.area='menu';s.tab=tabs.indexOf(event.area);s.focus='tabs';return s;
    }
    if(event.type==='MODE_SELECT'){
      if(!Number.isInteger(event.index)||event.index<0||event.index>=modes.length)throw new Error('Invalid mode');
      s.mode=event.index;s.variant=0;s.area='measurement';s.held=false;return s;
    }
    if(event.type==='PAGE'){
      if(!Number.isInteger(event.index)||event.index<0||event.index>2)throw new Error('Invalid settings page');
      s.area='menu';s.tab=1;s.page=event.index;s.focus='pages';return s;
    }
    if(event.type==='OPTION'){
      if(s.area!=='menu'||s.tab!==1||!Number.isInteger(event.index)||event.index<0||event.index>=optionCount(s))throw new Error('Invalid option');
      s.option=event.index;applyOption(s);s.focus='pages';s.notice='setting';return s;
    }
    if(event.type==='MENU'){s.area=s.area==='measurement'?'menu':'measurement';s.focus='tabs';return s;}
    if(event.type==='BACK'){
      if(s.area==='menu'&&s.focus==='options')s.focus='pages';
      else if(s.area==='menu'&&s.focus==='pages')s.focus='tabs';
      else if(s.area==='menu'&&s.focus==='confirm')s.focus='tabs';
      else s.area='measurement';
      return s;
    }
    if(event.type==='SAVE'){
      if(s.area==='menu'){s.area='measurement';s.focus='tabs';}
      else {const d=display(s);s.records=[{mode:d.title,value:d.value,unit:d.unit},...s.records].slice(0,8);s.notice='saved';}
      return s;
    }
    if(s.area==='measurement'){
      if(event.type==='HOLD')s.held=!s.held;
      else if(event.type==='LEFT'||event.type==='RIGHT'){s.mode=wrap(s.mode+(event.type==='LEFT'?-1:1),modes.length);s.variant=0;s.held=false;}
      else if(event.type==='MODE')s.variant=wrap(s.variant+1,modes[s.mode].variants.length);
      return s;
    }
    if(event.type==='LEFT'||event.type==='HOLD'||event.type==='RIGHT'){
      const step=event.type==='RIGHT'?1:-1;
      if(s.focus==='tabs')s.tab=wrap(s.tab+step,tabs.length);
      else if(s.focus==='pages')s.page=wrap(s.page+step,3);
      else if(s.focus==='options')s.option=wrap(s.option+step,optionCount(s));
      else if(s.focus==='confirm')s.option=wrap(s.option+step,2);
    }else if(event.type==='MODE'){
      if(s.tab===1){
        if(s.focus==='tabs')s.focus='pages';
        else if(s.focus==='pages'){s.focus='options';s.option=s.page===0?s.settings.language:s.page===1?s.settings.brightness:s.settings.auto;}
        else {applyOption(s);s.focus='pages';s.notice='setting';}
      }else if(s.tab===2){
        if(s.focus!=='confirm'){s.focus='confirm';s.option=1;}
        else if(s.option===0){s.settings=initial().settings;s.records=initialRecords();s.focus='tabs';s.notice='reset';}
        else s.focus='tabs';
      }
    }
    return s;
  }
  function accentBudget(characters='áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ'){
    const count=new Set([...characters.normalize('NFC')]).size;
    return{count,pairedSquareBytes:count*[12,16,24,32].reduce((n,h)=>n+2+Math.ceil(h/8)*h,0),
      pairedHalfWidthBytes:count*[12,16,24,32].reduce((n,h)=>n+2+Math.ceil((h/2)/8)*h,0),
      notice:'Hypothetical authorial glyph storage only; no font, patch or available-memory claim.'};
  }
  return{tabs,modes,initial,transition,display,accentBudget};
});
