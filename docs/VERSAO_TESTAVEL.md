# Versão testável: computador e futura integração no aparelho

16/11/2026 · Base: PR #10. A solicitação de avançar foi atendida com um pacote visual offline reproduzível e um seletor autoral executável em CPU ARM virtual. **Ainda não há imagem para testar no aparelho.** Não foi alterado o firmware original nem gerado instalável.

## Testar agora

Gere o pacote a partir da raiz do repositório:

```powershell
python -m src.dmc100_ptbr.preview_package ../DMC100-PTBR-alfa-offline-1.zip
```

Extraia todo o ZIP e abra `ABRIR.html`. Não requer instalação, servidor, Python ou internet para usar o resultado. A página orienta seleção de PT-BR, confirmação/cancelamento, retorno ao inglês, comparação das quatro telas e bancada de fontes. O pacote contém apenas dezesseis arquivos HTML/CSS/JS autorais, licença, instruções e manifesto SHA-256. A lista de inclusão é explícita; não percorre `private/`, vídeo, fontes ou firmware. Hashes do manifesto detectam diferenças, não autenticam autoria. A versão alfa do pacote não é uma versão do firmware.

O navegador mantém os layouts de 240 × 320, acentos das fontes locais, leituras fictícias e estado volátil. Não executa código ARM e não representa precisão, temporização ou segurança do aparelho. O desenho básico é o mesmo já revisado; esta entrega acrescenta empacotamento e roteiro, não maior fidelidade visual.

Registre problemas com tela, sequência de botões, idioma, tamanho de fonte, resultado esperado e observado. Compare apenas visualmente com o aparelho. Recarregar apaga alterações da simulação.

## Seleção de idioma em ARM

`src/dmc100_ptbr/arm_menu.py` implementa código Thumb próprio, separado do original. Entradas: R0 idioma ativo, R1 cursor, R2 confirmação pendente, R3 evento (0 anterior, 1 próximo, 2 confirmar, 3 voltar). Os valores de idioma são 0 chinês, 1 inglês, 2 PT-BR. O primeiro confirmar solicita confirmação; o segundo aplica. Voltar desfaz a proposta. Navegar remove confirmação antiga. O estado está nos registradores, sem persistência ou escrita em flash.

R0–R2 e flags são resultados/temporários; R3–R12, SP e LR são preservados. A rotina não acessa RAM nem periféricos. O adaptador Python rejeita estados/eventos inválidos antes de executar. Trata-se de um contrato autoral, não da ABI demonstrada do menu original. O teste integra a saída confirmada à entrada do despachante ARM por meio do ambiente Python; ainda não há ligação direta entre as duas rotinas na imagem original.

Instale as dependências opcionais de `requirements-arm.txt` em seu ambiente de desenvolvimento e execute:

```powershell
python -m src.dmc100_ptbr.arm_menu down ok ok
python -m src.dmc100_ptbr.arm_menu down ok back
python -m unittest discover -s tests -p 'test_arm*.py' -v
```

O primeiro comando termina em português; o segundo permanece em inglês. Sem argumentos, o comando executa a primeira sequência. Isso permite testar a lógica sem amostra proprietária. Não exige contato com fabricante ou equipamento conectado.

## Validação desta entrega

- 56 testes Python passaram localmente com motores opcionais e amostra privada; os ensaios privados anteriores continuam incluindo 56 contratos de entrada e 57 pares de desenho.
- A matriz nova cobre 72 transições (3 ativos × 3 cursores × 2 estados de confirmação × 4 eventos), preservação de registradores, cancelamento, aplicação, retorno aos idiomas originais e integração com seleção de texto.
- O empacotador verifica integridade por manifesto, fechamento de referências locais HTML, reprodução byte a byte e falha sem arquivo parcial quando faltam entradas.
- 26 testes Node passaram. Os 13 testes de navegador são executáveis contra o pacote extraído definindo `DMC_PREVIEW_ROOT` como o caminho absoluto da subpasta `simulator`; sem a variável usam a árvore-fonte. O browser usa arquivos locais e verifica ausência de pedidos HTTP, controles e fontes.
- A CI pública executa os testes sintéticos, sem baixar firmware. O job ARM passa a incluir o seletor; testes privados continuam opcionais. Resultados da execução ficam registrados no PR.

## O que ainda falta para uma imagem candidata ao aparelho

| Trabalho | Situação atual / critério necessário |
|---|---|
| Inserção no menu original | Seletor autoral passa em CPU virtual; faltam integração das chamadas, desenho, eventos e confirmação no menu V1.4 real |
| Consumidores do idioma | Despachante cobre dez rótulos/catorze ocorrências; faltam demais renderizadores, buffers formatados e estados de erro |
| Persistência | Somente estado volátil; falta compreender serialização/validação e compatibilidade sem atingir calibração |
| Português acentuado | Funciona com fontes do computador; falta caminho embarcado para glifos autorais, métricas e custo por tamanho |
| Recursos gráficos | 64 caminhos JPEG externos únicos, conteúdo não caracterizado; identificar textos incorporados e substituições próprias necessárias |
| Memória | Endereços da prova são artificiais; faltam mapa, posicionamento e trampolins; os 3.344 bytes não são comprovadamente livres |
| Formato de atualização | Faltam verificação de integridade, contrato do bootloader e testes de rejeição/retorno |
| Unidade de referência | V1.3 no vídeo e V1.4 na análise; compatibilidade/revisão não demonstradas |
| Recuperação e validação | Falta demonstrar restauração e revisar efeitos, avisos e temporização antes de propor instalação |

O próximo passo de integração é investigar o fluxo do menu original e os outros caminhos de texto, depois implementar glifos autorais e testar consumidores do idioma. Esses trabalhos podem continuar de forma independente. O seletor autoral não elimina essas pendências e o pacote do navegador não deve ser renomeado como firmware.

O projeto continua sem instalar nada no equipamento, alterar medição/calibração/segurança ou publicar ativos proprietários. [Mapa anterior](INTEGRACAO_FIRMWARE.md) · [Prova do despachante](DESPACHANTE_ARM.md).
