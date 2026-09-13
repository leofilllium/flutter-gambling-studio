import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const source=readFileSync(new URL('../web_verify.mjs',import.meta.url),'utf8');
const begin=source.indexOf('async function readSemantics()');
const end=source.indexOf('\nfunction findByLabel',begin);
assert.ok(begin>=0 && end>begin,'Verifier exposes its semantic reader');
const reader=source.slice(begin,end);

function fixture({placeholder=true,enabled=false,nested=false}={}){
  const state={enabled,clicks:0,taps:[]};
  const element=(tag,label,rect,click=()=>{})=>({tagName:tag,textContent:label,shadowRoot:null,
    getAttribute:name=>name==='aria-label'?label:name==='role'?'button':null,
    getBoundingClientRect:()=>rect,click});
  const hidden=element('FLT-SEMANTICS-PLACEHOLDER','Enable accessibility',
    {left:-1,top:-1,width:1,height:1,right:0,bottom:0},()=>{state.enabled=true;state.clicks++;});
  const spin=element('FLT-SEMANTICS','Spin',
    {left:120,top:700,width:160,height:56,right:280,bottom:756});
  const inner={querySelectorAll:()=>state.enabled?[spin]:placeholder?[hidden]:[]};
  const host=element('FLUTTER-VIEW','',{});host.shadowRoot=inner;
  const document=nested?{querySelectorAll:()=>[host]}:inner;
  const context={manifest:{},VW:390,VH:844,
    evaluate:async expression=>vm.runInNewContext(expression,{document}),
    tap:async(...point)=>state.taps.push(point),sleep:async()=>{}};
  const run=vm.runInNewContext('('+reader+')',context);
  return {state,run};
}

for(const nested of [false,true])test('offscreen placeholder enables semantics without a gameplay tap'+(nested?' inside shadow DOM':''),async()=>{
  const {state,run}=fixture({nested});const labels=await run();
  assert.equal(state.clicks,1);
  assert.equal(state.taps.length,0);
  assert.ok(labels.some(node=>node.label==='Spin'));
});
test('missing placeholder never becomes a blind top-left tap',async()=>{
  const {state,run}=fixture({placeholder:false});const labels=await run();
  assert.equal(state.taps.length,0);assert.equal(labels.length,0);
});
test('an already enabled tree is collected without an unrelated tap',async()=>{
  const {state,run}=fixture({enabled:true});const labels=await run();
  assert.equal(state.clicks,0);assert.equal(state.taps.length,0);
  assert.ok(labels.some(node=>node.label==='Spin'));
});
