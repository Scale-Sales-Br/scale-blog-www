#!/usr/bin/env node
/**
 * Carrossel de Instagram a partir de um artigo do blog.
 *
 *   NODE_PATH=/Users/mac/monitor-fipecafi/node_modules node social.js fonte/<arquivo>.md
 *
 * Le o roteiro em fonte/<mesmo nome>.carrossel.md, uma linha por cartao:
 *
 *   tipo | titulo | corpo
 *
 * tipo: capa | numero | texto | passos | fecho
 * No tipo "passos", separe os itens do corpo com " ;; ".
 * Saida: social/<slug>/01.png ... e social/<slug>/legenda.txt (1080x1350).
 */
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const AQUI = __dirname;
const DIAG = 'scalesales.com.br';

function lerMeta(arq) {
  const t = fs.readFileSync(arq, 'utf8');
  const m = t.match(/^---\s*\n([\s\S]*?)\n---\s*\n/);
  if (!m) { console.error('ERRO: artigo sem cabecalho ---'); process.exit(1); }
  const meta = {};
  for (const ln of m[1].split('\n')) {
    const i = ln.indexOf(':');
    if (i > 0) meta[ln.slice(0, i).trim()] = ln.slice(i + 1).trim();
  }
  return meta;
}

function lerRoteiro(arq) {
  const alvo = arq.replace(/\.md$/, '.carrossel.md');
  if (!fs.existsSync(alvo)) {
    console.error('ERRO: falta o roteiro ' + alvo);
    console.error('Uma linha por cartao:  tipo | titulo | corpo');
    process.exit(1);
  }
  return fs.readFileSync(alvo, 'utf8').split('\n')
    .map(l => l.trim())
    .filter(l => l && !l.startsWith('#'))
    .map(l => {
      const p = l.split('|').map(x => x.trim());
      return { tipo: p[0] || 'texto', titulo: p[1] || '', corpo: p[2] || '' };
    });
}

const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function cartaoHTML(c, n, total) {
  const rodape = `<div class="pe"><span>${DIAG}</span><span>${n}/${total}</span></div>`;
  if (c.tipo === 'capa') {
    return `<section class="c capa">${rodape}<div class="in">
      <p class="olho">Inteligência Artificial</p>
      <h1>${esc(c.titulo)}</h1>${c.corpo ? `<p class="sub">${esc(c.corpo)}</p>` : ''}
      <span class="arr">arraste &#8594;</span></div></section>`;
  }
  if (c.tipo === 'numero') {
    return `<section class="c">${rodape}<div class="in">
      <p class="num">${esc(c.titulo)}</p><p class="sub">${esc(c.corpo)}</p></div></section>`;
  }
  if (c.tipo === 'passos') {
    const itens = c.corpo.split(';;').map(x => x.trim()).filter(Boolean)
      .map((x, i) => `<li><i>${String(i + 1).padStart(2, '0')}</i><span>${esc(x)}</span></li>`).join('');
    return `<section class="c">${rodape}<div class="in">
      <h2>${esc(c.titulo)}</h2><ul class="passos">${itens}</ul></div></section>`;
  }
  if (c.tipo === 'fecho') {
    return `<section class="c fecho">${rodape}<div class="in">
      <h2>${esc(c.titulo)}</h2><p class="sub">${esc(c.corpo)}</p>
      <span class="botao">Diagnóstico gratuito &#8599;</span>
      <span class="link">${DIAG}</span></div></section>`;
  }
  return `<section class="c">${rodape}<div class="in">
    <h2>${esc(c.titulo)}</h2>${c.corpo ? `<p class="sub">${esc(c.corpo)}</p>` : ''}</div></section>`;
}

const PAGINA = cartoes => `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#060310;font-family:'Inter',sans-serif}
.c{width:1080px;height:1350px;position:relative;overflow:hidden;background:
   radial-gradient(1100px 760px at 78% 8%,rgba(228,87,249,.20),transparent 62%),
   linear-gradient(170deg,#1A0A36 0%,#120727 46%,#0C0418 100%);
   color:#F3EEFF;display:flex;align-items:center;margin:0 0 40px}
.c::after{content:"";position:absolute;left:0;right:0;bottom:0;height:7px;
   background:linear-gradient(90deg,#E457F9,rgba(228,87,249,0))}
.in{padding:0 96px;width:100%}
.olho{font-family:'Poppins';font-weight:500;font-size:25px;letter-spacing:.2em;
   text-transform:uppercase;color:#F7C9FF;margin-bottom:38px}
h1{font-family:'Poppins';font-weight:600;font-size:88px;line-height:1.05;
   letter-spacing:-.025em;text-wrap:balance}
h2{font-family:'Poppins';font-weight:600;font-size:66px;line-height:1.12;
   letter-spacing:-.02em;text-wrap:balance}
.sub{font-size:36px;line-height:1.5;color:#C9BCE6;margin-top:34px;max-width:21ch}
.capa .sub{color:#F7C9FF;max-width:23ch}
.num{font-family:'Poppins';font-weight:700;font-size:168px;line-height:1;
   letter-spacing:-.04em;color:#F7C9FF}
.passos{list-style:none;margin-top:44px;display:grid;gap:22px}
.passos li{display:flex;gap:26px;align-items:flex-start;font-size:33px;line-height:1.4;
   color:#E4DBF7;border:1px solid rgba(255,255,255,.14);border-radius:22px;padding:26px 30px;
   background:rgba(255,255,255,.055)}
.passos i{font-style:normal;font-family:'Poppins';font-weight:600;color:#F7C9FF;font-size:28px;padding-top:4px}
.arr{position:absolute;left:96px;bottom:118px;font-family:'Poppins';font-weight:500;
   font-size:27px;color:#9385B5;letter-spacing:.08em}
.fecho .botao{display:inline-flex;align-items:center;gap:16px;margin-top:52px;padding:30px 52px;
   border-radius:999px;background:#E457F9;color:#1A0320;font-family:'Poppins';font-weight:600;font-size:38px}
.fecho .link{display:block;margin-top:30px;font-size:30px;color:#C9BCE6}
.pe{position:absolute;left:96px;right:96px;bottom:54px;display:flex;justify-content:space-between;
   font-size:25px;color:#7E6FA6;letter-spacing:.04em}
</style></head><body>${cartoes}</body></html>`;

(async () => {
  const arq = process.argv[2];
  if (!arq) { console.error('uso: node social.js fonte/<arquivo>.md'); process.exit(1); }
  const meta = lerMeta(path.resolve(AQUI, arq));
  const cards = lerRoteiro(path.resolve(AQUI, arq));
  const destino = path.join(AQUI, 'social', meta.slug);
  fs.mkdirSync(destino, { recursive: true });

  const html = PAGINA(cards.map((c, i) => cartaoHTML(c, i + 1, cards.length)).join(''));
  const tmp = path.join(destino, '_cartoes.html');
  fs.writeFileSync(tmp, html);

  const b = await chromium.launch({ channel: 'chrome' });
  const p = await (await b.newContext({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 })).newPage();
  await p.goto('file://' + tmp, { waitUntil: 'load' });
  await p.waitForTimeout(1800);

  const secs = await p.$$('.c');
  for (let i = 0; i < secs.length; i++) {
    const nome = String(i + 1).padStart(2, '0') + '.png';
    await secs[i].screenshot({ path: path.join(destino, nome) });
    const alto = await secs[i].evaluate(e => {
      const t = e.querySelector('.in');
      return t.scrollHeight > 1350 - 240;
    });
    console.log(' ' + nome + (alto ? '   ATENCAO: texto perto de estourar o cartao' : ''));
  }
  await b.close();
  fs.unlinkSync(tmp);

  const legenda = [
    meta.titulo, '',
    meta.resumo, '',
    'A leitura completa está no blog da Scale Sales. Link na bio.', '',
    'Quer saber onde a sua operação comercial está perdendo venda? O diagnóstico é gratuito.', '',
    '#inteligenciaartificial #vendas #gestaocomercial #processocomercial #IA'
  ].join('\n');
  fs.writeFileSync(path.join(destino, 'legenda.txt'), legenda);
  console.log('\n' + secs.length + ' cartoes em social/' + meta.slug + '/ · legenda.txt junto');
})();
