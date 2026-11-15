# Viabilidade V1.4 — auditoria e investigação offline

Data: 15/11/2026. Base auditada: `6cf9fcb`. Escopo: todos os 18 arquivos versionados dessa base, histórico disponível e issues #1–#4 (abertas, sem comentários na consulta). Nenhum arquivo original V1.4 estava disponível localmente. Nenhuma comunicação com instrumento, alteração de firmware, compilação ARM ou geração de imagem instalável foi realizada.

## Parecer

A pesquisa de localização é viável; uma tradução funcional e segura ainda não está demonstrada. O próximo marco deve ser um mapa verificável de recursos e referências do original, seguido de protótipo visual. Não se recomenda recompilar a decompilação ou produzir patch nesta fase. Os resultados abaixo distinguem observação no código público, inferência e confirmação ainda pendente no binário.

## Auditoria do projeto

O código original é pequeno: catálogo de 14 textos e inspetor somente leitura, sem dependências externas. As três provas automatizadas existentes passam, mas usam fixtures montadas a partir do próprio catálogo: não conseguem revelar offsets incorretos no catálogo. A prova de imutabilidade comparava uma cópia imutável com o bytearray original; era limitada para detectar escrita em arquivo. Não havia cobertura de CLI, terminadores, duplicatas, EOF, tamanho divergente com todas as strings presentes ou erros de leitura.

Achados e tratamento nesta branch:

| Achado | Consequência | Tratamento |
|---|---|---|
| Dois offsets omitiam espaço presente na extração | Falsos negativos prováveis | Corrigir início útil para `0x005900` e `0x00B290`, sustentado pelas referências `+1` comunitárias; original ainda pendente |
| Comparação apenas de prefixo | Texto maior poderia parecer coincidente | Manter `matches` e acrescentar `nul_terminated_match` e contagem agregada |
| CLI ignorava tamanho ao retornar sucesso | Arquivo diferente podia retornar 0 | Exigir tamanho reportado e terminadores; ainda não autentica versão |
| `found_hex` expunha bytes do arquivo | Relatórios poderiam transportar conteúdo não revisado | Remover o campo; não exportar bytes nem textos desconhecidos |
| Catálogo contempla uma ocorrência por termo | Alterações futuras poderiam deixar duplicatas inconsistentes | Relatar todas as ocorrências terminadas em NUL como candidatas |
| `.gitignore` como única barreira a arquivos privados | Arquivo pode ser adicionado com força ou extensão diferente | Documentar revisão de `git diff --cached`; ignore não é garantia de confidencialidade |

Não há código de patch, acesso USB, calibração, conversão de unidades ou medição no projeto. A licença MIT exclui expressamente material de terceiros. Código externo foi consultado, sem incorporá-lo.

## Evidências externas e estrutura provável

Referências consultadas em 15/11/2026, fixadas quando possível:

1. [cakenes/dmc100, commit 1a7684b](https://github.com/cakenes/dmc100/tree/1a7684b7a49f1d8bd4a9bab079d578663dda9912): README, inventário de strings, nomes de funções e trechos relevantes de decompilação limpa. Não foi tratado como código-fonte original, nem como imagem reconstruível.
2. [DMC100-Doom, commit 0cdc78e](https://github.com/ArturBieniek4/DMC100-Doom/tree/0cdc78eb66cdddacc43112d5f79c258c4a5440b7): README, mapa de diretórios, cabeçalho de plataforma, configurações e modelo Renode. Não foram executados instaladores, restauração ou testes que acessam hardware.
3. [Produto FNIRSI](https://www.fnirsi.com/products/dmc-100): confirma tela 240×320. O seletor de idioma do site não demonstra idioma disponível no firmware.
4. [Página de downloads FNIRSI](https://www.fnirsi.com/pages/manuals-firmwares): conteúdo textual acessível não forneceu um manifesto autenticado do binário.
5. [Distribuidor VX](https://vx.com.ar/manuales-y-descargas/): lista DMC-100 V1.4, sem demonstrar que um arquivo local seja idêntico à referência estudada. Nenhum binário foi baixado.
6. [Relato de desmontagem](https://www.mydigit.cn/thread-559140-1-1.html): identifica AT32F415CBT7, SD7502 e W25Q32JVSQI por leitura/reconstrução de marcações. Evidência secundária de uma unidade, não identificação da unidade do projeto.

### Texto, menus e fontes

O inventário comunitário indica duplicatas de System settings e Language. Seus nomes de funções sugerem rotinas distintas de texto e JPEG. O renderizador em `0x080012F2` aparenta consumir um byte para ASCII e dois para valores altos; `0x080016D8` parece pesquisar pares de bytes em tabela. Isso sugere codificação de dois bytes e fontes tabuladas, não comprova UTF-8 ou uma codificação chinesa específica. A decompilação inclui parâmetros artificialmente zerados e assinaturas incompletas: não deve ser executada como implementação equivalente.

Consequência: substituir apenas strings por UTF-8 pode produzir glifos incorretos, perder caracteres ou avançar sobre terminadores. Devem ser resolvidos os ponteiros de tabelas, cobertura de glifos e avanço por tamanho antes de decidir sobre acentos. Abreviações ASCII servem somente para estudo. Avisos e símbolos precisam de revisão técnica humana.

### Recursos gráficos

Referências a `UI/decorat`, `UI/decorate`, `UI/mode`, `UI/mode_1`, `UI/cel`, `UI/cell` e LOGO apontam para recursos fora do texto executável. Diferenças de nome podem representar temas, variantes ou artefatos da extração; não devem ser normalizadas sem verificar referências. Um caminho não prova que a imagem exista ou que contenha palavras.

O projeto DOOM relata NOR externa de 4 MB, unidades lógicas de 1 MB e 3 MB e aproximadamente 1,2 MB de imagens originais. Demonstra uso do display e armazenamento por um programa substituto; não preserva medição. Seu emulador modela periféricos para o jogo, não certifica o comportamento do instrumento original. Não é necessário nem autorizado usar o instalador para obter recursos.

### Memória e integridade

Os 95.984 bytes reportados descrevem o arquivo estudado pela comunidade, não toda a capacidade de flash. Não é válido subtrair esse número da capacidade nominal e chamar o restante de espaço livre. Bootloader, páginas de configuração, alinhamento e tabelas podem ocupar o restante; a RAM também requer medição de heap, pilha e buffers.

Há descrições comunitárias diferentes de arquitetura e orçamento de memória; identificar MCU, FPU e revisão continua pendente. O modelo DOOM declara 128 KB de flash e 32 KB de SRAM; o orçamento do programa e a página de configurações do próprio jogo não são o mapa do firmware original. Um framebuffer RGB565 de 240×320 requer 153.600 bytes: com 32 KB de RAM reportados, o estudo deve considerar desenho por linhas/blocos, sem assumir framebuffer completo.

A sugestão de CRC32 final no guia comunitário é especulativa. Não implementar correção de CRC, preenchimento ou truncamento com base nela. Vetores, endereço de carga, formato de atualização, checksum e assinatura devem ser verificados no original. Correspondência de tamanho e textos não autentica nenhum desses itens.

## Ferramentas entregues e limites

`inspect` mantém a comparação conhecida e acrescenta terminadores, ocorrências e comprimentos. `analyze` apresenta os primeiros dois words como vetores candidatos, contagens de sequências ASCII/ASCII em UTF-16LE, posições de caminhos JPEG e marcadores, e entropia por blocos de 4 KiB. Não descomprime nem extrai recursos, não reconhece fontes e não recupera referências de instruções. Marcadores podem ser coincidências. Bytes zero/FF não são memória livre. O relatório é metadado de pesquisa, não inventário definitivo do executável.

`layout` separa orçamento de bytes de largura assumida. Todos os 14 rascunhos ASCII cabem no comprimento do texto original, mas isso não demonstra capacidade alocada, terminador disponível, ponteiros válidos ou tradução adequada. Em largura assumida de 220 px: célula de 8 px não apresenta excesso; 12 px apresenta um; 16 px apresenta dois. A mensagem de carregamento tem 24 caracteres e excede 220 px com célula de 12 px. O protótipo é matemático; capturas reais e reprodução gráfica das fontes continuam pendentes.

## Testes e reprodução

Antes das mudanças: 3/3 testes passam. Depois: 17/17 passam localmente no Windows, Python 3.11.15, com `python -m unittest discover -s tests -v`. `git diff --check` passa. A CI foi expandida para Linux/Windows e Python 3.12/3.13; a execução remota é registrada no PR, sem antecipar seu resultado.

Os novos casos cobrem falso prefixo, NUL ausente no EOF, duplicatas, busca sobreposta, arquivo vazio/truncado, bloco parcial, candidatos UTF-16LE em posição ímpar, metadados sem conteúdo arbitrário, tamanho divergente, CLI, entrada ausente, limites de layout e normalização NFC. Um teste usa arquivo temporário sintético, verifica SHA-256 antes/depois e ausência de arquivos extras. Nenhuma fixture real ou instalável foi salva no repositório.

Essas provas validam ferramentas, não offsets reais, fontes, medições ou segurança. O teste construído a partir do catálogo continua explicitamente sintético. A aceitação da V1.4 exige evidência independente.

## Próxima fase e critérios de avanço

1. Disponibilizar `private/firmware/APP_DMC-100_V1.4_250524.bin` legitimamente, registrar origem, data, tamanho e SHA-256 em registro local privado. O nome é referência comunitária, não assinatura. Não anexar firmware a issues/PR.
2. Executar os comandos do README; investigar divergências antes de afirmar que se trata da mesma imagem. Publicar somente metadados revisados. Sem o original, a issue #1 permanece pendente.
3. Construir mapa de seções/dados e referências ARM/Thumb de cada texto, incluindo referências interiores e duplicatas. Validar base com vetores e chamadas; não inferir função por proximidade da string.
4. Mapear tabelas de glifos e codificação, tamanhos 12/16/24/32 sugeridos pelas rotinas; produzir primeiro fonte e telas autorais offline. Comparar capturas legítimas, posições, recorte e estados de tema. Issue #2 permanece parcial.
5. Revisar glossário: faixa/escala conforme contexto, histórico e mensagens críticas. Preservar símbolos SI, polaridade, AC/DC e estados de alerta. Não aprovar a abreviação de segurança só porque cabe. Issue #4 depende da comunidade.
6. Esclarecer direitos com fabricante e validar recuperação em pesquisa independente antes de qualquer futura proposta de hardware; não realizar contato nem gravação nesta fase. Issue #3 continua aberta. O plano metrológico e revisão externa são marcos futuros.

Riscos principais: atribuir versão incorreta, interpretar decompilação como fonte original, misturar recursos de revisões, confundir tamanho com espaço disponível, gerar texto ilegível ou ambíguo e comprometer alertas. O avanço autorizado atual termina nas ferramentas de leitura, simulação e documentação; firmware instalável permanece indisponível.
