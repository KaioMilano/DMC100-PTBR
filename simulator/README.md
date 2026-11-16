# Simulador visual offline DMC100-PTBR

Abra **index.html** no navegador depois de manter os arquivos desta pasta juntos. Não precisa de instalação, Node, Python, servidor ou internet para usar. Agora essa página apresenta navegação autoral orientada pelo vídeo privado V1.3. `reference-gallery.html` mostra as quatro comparações atualizadas. A bancada anterior de tipografia está em `lab.html`, e sua galeria em `gallery.html`. Não abra pela visualização de código do GitHub: baixe/extraia os arquivos primeiro.

São layouts autorais em dimensões de **240 × 320 pixels**, com valores fixos fictícios. Não reproduzem pixel a pixel a interface ou as fontes proprietárias. Nenhuma imagem foi extraída do equipamento; nenhum arquivo de firmware é carregado. Não há acesso a USB, rede, aparelho ou calibração.

## Usar

Na navegação V1.3, escolha inglês, PT-BR ou ambos. Use os atalhos externos ou os quatro ícones superiores. HOLD/← e V-A/→ navegam, MODE confirma, SAVE sai do menu; na medição, MODE alterna variante, V-A avança categoria e HOLD alterna apenas o indicador. SAVE curto adiciona fixture ao histórico; segurar SAVE abre o menu (600 ms é limiar autoral, não medição do equipamento). Energia liga/desliga só a simulação. Todos esses mapeamentos são provisórios e estão descritos no [relatório do vídeo](../docs/VIDEO_V13_NAVEGACAO.md).

Teclado: setas, Enter/M, H, S, Shift+S, Esc e P. O estado é volátil, sem persistência. Reset precisa de confirmação e só restaura opções da página. Nas configurações, MODE entra nas subpáginas, setas escolhem a página, MODE entra em opções e confirma a escolhida. Brilho/unidade/desligamento vêm da análise estática V1.4 e não foram demonstrados no vídeo; níveis de brilho são uma proposta de interação. O catálogo estendido tem 33 entradas com evidência, incluindo 16 textos confirmados em 21 ocorrências.

Para a bancada de tipografia em **lab.html**:

1. Escolha Medição, Configurações, Histórico, Sobre ou Avisos.
2. Compare inglês e PT-BR simultaneamente. As leituras e unidades permanecem iguais.
3. Alterne português completo, compacto com acentos ou compacto sem acentos.
4. Teste tamanhos 12/16/24/32, fonte sem serifa/monoespaçada, grade e ampliação 1/1,5/2×. A ampliação não muda o SVG intrínseco de 240 × 320.
5. Experimente um título em PT-BR. Esse campo não altera o catálogo nem é usado nos cenários de aviso.
6. Verifique diagnósticos de largura/altura e comprimento UTF-8. Não há ajuste automático ou reticências: excessos aparecem como problema.
7. Exporte SVG por idioma ou o catálogo JSON. A exportação de SVG usa somente o desenho próprio; pode mostrar texto recortado nos cenários de estresse.

O catálogo indica todas as ocorrências conhecidas, incluindo duplicatas, e separa rótulos confirmados de rótulos criados para o protótipo. “Confirmado” se refere ao original inglês/offset/NUL na amostra identificada por hash; nenhuma tradução foi aprovada para firmware. O orçamento apresentado analisa o título da tela (ou a mensagem crítica em Avisos), não o total de bytes de toda a tela.

As formas geométricas, curva de exemplo e ícones de bateria são autorais. A tipografia vem de Arial/Consolas ou fallback local. Fontes substitutas mudam métricas entre sistemas; acentos que funcionam no navegador não demonstram suporte no firmware.

## Desenvolvimento e testes

Node 22+ e `npm ci` são necessários apenas para os testes de desenvolvimento. Runtime sem dependências. A dependência Playwright é fixada no lockfile e não participa do simulador entregue.

```sh
cd simulator
npm ci
npm test
npx playwright install chromium
npm run test:browser
npm run preview:export
```

Os testes de navegador abrem `file://`, verificam que não há requisições HTTP, exercitam controles, exportações, acentos, excessos, fluxos de navegação e layout móvel. São 20 casos Node e 11 testes de navegador; os casos anteriores incluem 120 combinações de tela/idioma/tamanho/variante. No Linux, `playwright install --with-deps chromium` também prepara bibliotecas do navegador.

Pode-se usar um Chrome já instalado em vez do Chromium baixado, apontando `DMC_CHROME_PATH` para seu executável. No PowerShell:

```powershell
$env:DMC_CHROME_PATH = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
npm run test:browser
node tools/export-preview.cjs ../docs/images
node tools/export-reference.cjs ../docs/images
```

Opcional e privado, sem download nem escrita no original:

```sh
node tools/verify-private-catalog.cjs ../private/firmware/APP_DMC-100_V1.4_250524.bin
node tools/verify-private-catalog.cjs ../private/firmware/APP_DMC-100_V1.4_250524.bin --navigation
```

Esses comandos exigem o SHA-256 registrado e comparam o catálogo básico (15/20) ou estendido de navegação (16/21), verificando NUL e hash antes/depois. Nunca enviar o arquivo para GitHub/CI. Para servir localmente, limite a raiz a esta pasta: `python -m http.server 8927 --bind 127.0.0.1 --directory simulator` a partir da raiz do repositório. Não sirva a raiz que contém `private/`.

Mais detalhes: [relatório da fase visual](../docs/SIMULADOR_VISUAL.md) e [recursos externos](../docs/RECURSOS_EXTERNOS.md). Código e desenhos originais sob a licença MIT do repositório. FNIRSI e DMC-100 pertencem aos respectivos titulares; projeto não oficial.
