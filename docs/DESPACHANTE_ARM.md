# Despachante PT-BR em ARM — prova de integração sem hardware

Data: 16/11/2026. Base: PR #9. O mantenedor optou por continuar sem contato com o fabricante. A engenharia avança por código autoral, emulação e comparação diferencial; contato com fabricante não é exigência para esta etapa.

## Resultado concreto

Foi escrito um despachante autoral em assembly Thumb e executado num modelo de CPU Cortex-M4 com Unicorn. Não é o simulador JavaScript: a prova executa instruções ARM e, nos ensaios privados, a própria rotina de texto/glifos da amostra V1.4.

O idioma proposto 2 seleciona textos ASCII PT-BR por ponteiro; 0/1 e outros valores deixam o ponteiro original. O laço é limitado à quantidade validada de entradas. O código preserva os demais registradores, SP, LR, flags NZCVQ e argumentos de pilha nos casos testados. Valores inválidos ou ponteiros não mapeados não são traduzidos. Referências interiores não são reescritas automaticamente.

O experimento **não altera o arquivo original nem injeta um salto na imagem**, não modifica armazenamento, não executa medição/calibração/segurança e não produz firmware instalável. Código e dados adicionais ficam em regiões artificiais da CPU virtual (`0x10000000` / `0x10001000`), que não são endereços de gravação nem espaço demonstrado no DMC-100. Não há backend ou ligação USB com o aparelho.

## Implementação

`src/dmc100_ptbr/arm_dispatch.py` contém o assembler autoral, tabela de traduções própria e ambiente de teste. O código salva contexto, consulta o byte de idioma no endereço observado, procura uma correspondência exata e transfere para a entrada original de texto. Nada da decompilação proprietária foi incorporado.

Nesta prova são dez rótulos em catorze ocorrências terminadas em NUL, incluindo duplicatas. Os rascunhos usam somente ASCII para exercitar o caminho de fontes já existente. Português acentuado ainda não está implementado em ARM. AUTO shut_down, Low battery, Shutdown e Do not use while charging foram deliberadamente excluídos do mapeamento: ficam inalterados mesmo com idioma 2. Isso é cobertura parcial, não aprovação de todas as traduções.

Componentes lógicos montados neste ensaio: **60 bytes de código, 112 bytes de tabela e 91 bytes de textos próprios**. O total de 263 bytes não é tamanho de firmware, orçamento final ou prova de que caiba no intervalo antes das configurações. O mapa virtual inclui padding e páginas próprias. Ainda faltam integração de menu/persistência, local de execução real, eventuais trampolins, alinhamento, fontes, imagens, índices e integridade.

## Comparação com o original privado

A imagem é aceita somente pelo SHA-256 observado `f8eab197553e117a374dc9926989b8ec2105baa8120682bd5c864bda30e8364d`. Sua memória ROM virtual é protegida contra escrita e comparada com os bytes de entrada depois de cada ensaio. O arquivo local é novamente lido ao final. Nenhuma imagem, fonte, trecho de disassembly ou fluxo de pixels proprietário é exportado.

O teste privado executa a rotina original em offset `0x0012F2` e seus caminhos de glifos. As chamadas finais para janela LCD, dados de 16 bits e pixel são interceptadas por stubs: registram contagens e hash, sem acesso a periféricos. Execução fora da região de texto/glifos e desses stubs é rejeitada. Escritas fora da área de pilha de teste interrompem a execução. Há limites de instruções e tempo.

Foram comparados:

- **56 contratos de entrada**: quatro valores de idioma, catorze ponteiros; R2 é o único registrador permitido a mudar quando traduzido.
- **42 pares de rastros**: os idiomas 0/1 devem coincidir com o caminho original sem wrapper; o idioma 2 deve coincidir com a mesma rotina original recebendo diretamente o texto PT-BR esperado.
- Três referências chinesas nos tamanhos identificados nas chamadas (16/16/24), com chamadas de desenho efetivas e rastro preservado.
- Quatro tamanhos ASCII, 12/16/24/32, e os dois modos de desenho testados (fluxo de dados ou pixels).
- Quatro mensagens protegidas, sem redirecionamento em PT-BR.

As últimas três categorias acrescentam quinze pares privados, totalizando **57 comparações diferenciais de desenho** nos testes privados. Os testes sintéticos incluem ainda todas as 32 combinações NZCVQ nos idiomas 0/1/2.

Foi observado que uma referência chinesa do histórico não desenha glifos a 16 px, mas desenha a 24 px, como na chamada comunitária correspondente. Isso reforça que cobertura de repertório é específica por tamanho; não basta assumir uma única tabela universal.

## Reprodução

Dependências opcionais fixadas em `requirements-arm.txt`: Unicorn 2.1.4 e Keystone Engine 0.9.2, obtidas de PyPI. Não são dependências do simulador nem baixam firmware. As APIs foram consultadas no [tutorial do Unicorn](https://www.unicorn-engine.org/docs/tutorial.html) e nos [exemplos oficiais do Keystone no GitHub](https://github.com/keystone-engine/keystone/blob/master/bindings/python/sample.py). As bibliotecas mantêm suas licenças próprias; somente o código autoral deste repositório é MIT.

Em um ambiente Python de desenvolvimento:

```sh
python -m pip install -r requirements-arm.txt
python -m unittest discover -s tests -p test_arm_dispatch.py -v
```

Com uma cópia privada legítima da amostra:

```powershell
$env:DMC100_V14_PATH = 'private/firmware/APP_DMC-100_V1.4_250524.bin'
python -m unittest discover -s tests -v
python -m src.dmc100_ptbr.arm_dispatch --firmware $env:DMC100_V14_PATH
Remove-Item Env:DMC100_V14_PATH
```

Na sessão de desenvolvimento as bibliotecas foram instaladas isoladamente em `private/tooling`; `PYTHONPATH` apontou explicitamente para essa pasta. Os testes passaram: **48/48 Python** com dependências e imagem privada. Sem os motores/arquivo privado, a suíte padrão passa 35 casos e ignora 13 opcionais. O novo job de CI instala os motores e passa dez testes sintéticos; quatro privados ficam ignorados, sem transferir o binário. A CI Node/navegador anterior permanece.

O código de saída 0 da experiência significa apenas que as comparações passaram no ambiente de teste. O relatório mantém `firmware_generated: false` e `installable_ready: false`.

## O que esta prova não demonstra

Unicorn não modela o aparelho completo, o display físico, interrupções, temporização, medições, alimentação ou o protocolo de atualização. Os drivers finais são substituídos por stubs. Um mesmo hash de rastro nesses ensaios não certifica leituras, precisão ou segurança. O modelo Cortex-M4 não identifica a revisão do MCU real.

Não foi demonstrada preservação temporal, integração com todas as chamadas alternativas (incluindo a rotina em `0x00139E`), textos formatados, recursos JPEG ou estados de erro. Não foi criada a terceira opção no menu ARM nem persistido o idioma em flash. A seleção do byte 2 é preparada pelo ambiente virtual de teste.

## Continuação independente

1. Ampliar o modelo para chamar menus reais com substitutos autorais de recursos e testar a terceira opção em ARM, incluindo cancelamento e retorno.
2. Cobrir renderizadores alternativos, buffers formatados e todos os consumidores do idioma, preservando fallback dos dois idiomas existentes.
3. Implementar e testar uma estratégia de glifos/acentos autorais, com métricas e custo por tamanho, sem reutilizar bitmaps proprietários.
4. Estudar bootloader/integridade, memória e recuperação por fontes públicas e engenharia independente; não tomar o intervalo de 3.344 bytes por espaço disponível.
5. Somente depois avaliar um candidato privado de integração e um plano de validação apropriado. A exigência de não instalar no equipamento continua vigente.

Código e testes podem avançar sem resposta de fabricante. A decisão de distribuir ou instalar qualquer futuro derivado é uma etapa distinta; os arquivos proprietários continuam fora do GitHub.
