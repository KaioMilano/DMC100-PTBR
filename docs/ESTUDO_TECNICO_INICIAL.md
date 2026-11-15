# Estudo técnico inicial — DMC100-PTBR

**Data:** 15 de novembro de 2026

Atualização: veja [auditoria e viabilidade V1.4](VIABILIDADE_V14.md) e [análise direta da amostra](ANALISE_V14_BINARIO.md). Os limites e pendências abaixo descrevem o estudo inicial; a análise posterior confirma 14 offsets, oito tabelas de fontes e base de carga `0x08007000`. As afirmações comunitárias abaixo não são identificação confirmada do hardware.

**Aparelho de referência:** FNIRSI DMC-100, firmware V1.3 identificado na tela *About*.

## Resumo

A tradução de menus para português é **tecnicamente plausível, mas não demonstrada**. Não há evidência de uma versão PT-BR oficial ou de firmware traduzido e metrologicamente validado. Em particular, uma prova de execução de software próprio no hardware **não demonstra segurança das medições**.

## Fontes observadas

- Página do fabricante: https://www.fnirsi.com/products/dmc-100
- Página do fabricante para updates: https://www.fnirsi.com/pages/manuals-firmwares
- Inventário de engenharia reversa V1.4: https://github.com/cakenes/dmc100
- Firmware alternativo experimental: https://github.com/ArturBieniek4/DMC100-Doom
- Distribuidor que lista V1.4: https://vx.com.ar/manuales-y-descargas/

O repositório comunitário `cakenes/dmc100` informa arquitetura **ARM Cortex-M4F**, binário de **95.984 bytes** e decompilação com **364 funções**. Esses dados são de pesquisa independente, não documentação formal do fabricante. Sua lista pública `dmc100_strings.txt` contém strings e offsets que fundamentam o inventário inicial.

O projeto `DMC100-Doom` executa programa próprio no instrumento e examina armazenamento e display. Não preserva, nessa demonstração, as funções normais de medição.

## Hipótese de trabalho

Traduzir inicialmente apenas rótulos de interface, preservando a lógica original. Isso **não torna um patch automaticamente seguro**: até mudanças aparentemente simples podem afetar offsets, referências, fontes, telas, ponteiros e verificações de integridade. Também será necessário estudar recursos gráficos JPEG, não apenas strings em ASCII.

## Limites atuais

- **Não** há arquivo V1.4 original inspecionado diretamente pelo projeto.
- Offsets e tamanho são dados comunitários não verificados independentemente.
- Não sabemos ainda se há suporte a acentos.
- Não existe backup/restauração comprovado nesta unidade.
- Não existe firmware modificado, testado ou distribuível.

## Próxima investigação

1. Obter uma cópia legítima do firmware V1.4 para **análise privada**.
2. Rodar o inspetor somente leitura e registrar seu resultado.
3. Comparar strings, offsets e codificações com o inventário externo.
4. Mapear recursos gráficos e decidir quais traduções cabem sem deslocar estruturas.
5. Criar protótipo offline com revisão técnica e sem uso no multímetro.

**O resultado pretendido na fase atual é um relatório de viabilidade, não um arquivo de atualização.**
