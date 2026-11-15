# Plano de trabalho

## Fase 0 — Preparação
- [x] Identificar o aparelho de referência como FNIRSI DMC-100 V1.3.
- [x] Reunir estudos públicos sobre a V1.4.
- [x] Publicar documentação, ferramenta de inspeção somente leitura e testes.
- [ ] Obter autorização/orientação do fabricante sobre localização e redistribuição.
- [x] Obter arquivo original V1.4 para análise privada; origem e SHA-256 documentados.

## Fase 1 — Análise estática
- [x] Confirmar tamanho, SHA-256 e os 14 offsets iniciais no arquivo real.
- [ ] Mapear terminadores, tamanho das strings, duplicatas, fontes e referências.
- [ ] Separar claramente textos de interface de textos de segurança/metrologia.
- [ ] Coletar capturas de telas sem informações pessoais.

## Fase 2 — Protótipo offline
- [ ] Revisar glossário PT-BR por usuários com conhecimento em eletricidade.
- [x] Verificar acentuação nas oito tabelas mapeadas: chaves PT-BR testadas ausentes; estratégia de suporte continua pendente.
- [x] Criar comparações autorais de layouts em 240 × 320 sem instalar firmware.
- [ ] Documentar diffs de cada alteração proposta.
- [ ] Analisar como JPEGs da interface são armazenados e exibidos.

Fase visual: [simulador e resultados](SIMULADOR_VISUAL.md), [referências a recursos externos](RECURSOS_EXTERNOS.md). A navegação e as famílias JPEG foram investigadas; a partição externa e seus pixels continuam indisponíveis. Comparações do navegador não validam fontes embarcadas.

## Fase 3 — Segurança e qualidade
- [ ] Validar procedimento de recuperação com fonte independente.
- [ ] Usar somente instrumento de laboratório separado do aparelho de uso.
- [ ] Submeter mudanças a revisão técnica externa.
- [ ] Testar interface, alertas e calibração em ambiente controlado.
- [ ] Comparar medições com referências metrológicas.

## Fase 4 — Publicação
- [ ] Verificar direitos de distribuição e licença dos artefatos.
- [ ] Documentar limites, resultados e testes repetíveis.
- [ ] Liberar binário somente quando autorização e validação forem suficientes.
- [ ] Habilitar apoio voluntário se houver canal legítimo.

**Bloqueio:** nenhum firmware experimental é considerado seguro para gravação apenas porque inicia ou desenha menus corretamente.
