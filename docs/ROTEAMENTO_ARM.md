# Roteamento em ARM e entradas na ROM virtual

16/11/2026 · Base: PR #13. Esta etapa substitui decisões de roteamento antes realizadas pelos hooks Python. Não é firmware pronto para instalação, não modifica o arquivo original, não acessa aparelho e não emite imagem binária.

## O que mudou

`arm_text_gate.py` implementa em Thumb:

1. Seleção do título “Idioma” pelo byte de idioma 2 e ponteiro original exato.
2. Busca limitada numa tabela de ponteiros/comprimentos dos três buffers autorais UTF-8.
3. Validação de altura 12/16/24/32 e overlay 1 antes de chamar o renderizador próprio.
4. Encaminhamento dos demais textos à entrada original por trampoline.

O Python observa os argumentos para testar, mas, neste modo, **não escolhe o novo ponteiro, não fornece R12/comprimento e não decide o destino do texto**. Essas decisões são instruções ARM. A tabela de comprimento inclui NUL e usa comprimento UTF-8 em bytes.

Há uma reserva de 64 bytes na pilha do gate para salvar R0–R12, LR e flags NZCVQ. Ao entrar no caminho nativo, registradores/flags/argumentos da pilha são restaurados integralmente. No caminho autoral, R2 recebe o ponteiro próprio e R12 o comprimento declarado; os demais argumentos são preservados. O renderizador continua usando uma ABI própria para R12, não uma nova ABI atribuída ao firmware original.

Ponteiros desconhecidos e referências interiores não são reinterpretados como UTF-8. Para o título nativo em formato não suportado, mantém-se o texto original. Para um buffer UTF-8 autoral em formato não suportado, retorna sem desenhar em vez de enviá-lo ao decodificador GBK. Esse caso é uma limitação explícita: overlay 0 ainda não está implementado no caminho autoral e precisa ser resolvido antes de considerar cobertura completa.

## Duas alterações somente em memória virtual

O modo opcional `shadow_entries=True` escreve **dois B.W de quatro bytes na ROM do emulador**, nos offsets `0x12F2` (texto) e `0x5938` (menu). O arquivo de entrada permanece intacto. Não é mais correto dizer que a ROM virtual está totalmente igual ao original nesse modo: o teste confere que as diferenças ficam restritas a essas duas entradas. O modo anterior com hooks continua disponível como referência.

Cada entrada começa com um PUSH.W de quatro bytes, sem dependência do PC. O perfil confere exatamente essa instrução antes de movê-la para um trampoline. A continuação retorna à entrada original +4, mantendo as instruções PC-relativas nos endereços originais. Não se tenta realocar arbitrariamente instruções encontradas.

Os branches vão a veneers em `0x08100000` / `0x08100020`, e as continuações usam `0x08100100` / `0x08100120`. Esses endereços estão **fora da flash de 128 KiB assumida pelo modelo** e são mapeamentos artificiais. Os veneers transferem ao código autoral em `0x1000xxxx`, também exclusivo da CPU virtual. Portanto, **os bytes dessa prova não podem ser gravados no equipamento**. Nenhum comando permite exportá-los como firmware.

Na entrada de menu, o branch chama o wrapper autoral; o wrapper chama a continuação original, evitando recursão. Na entrada de texto, o branch passa pelo gate; caracteres ASCII fragmentados pelo renderizador também passam pelo gate e retornam ao motor original via trampoline.

A mudança adiciona 148 bytes de gate, 24 de tabela de ponteiro/comprimento, 16 de veneers e 16 de trampolines, além dos oito bytes de entradas substituídas. O relatório soma **1.328 bytes de componentes/entradas** neste modelo. Esse número inclui os oito bytes sobrescritos e as instruções copiadas nas continuações; não é espaço adicional efetivo em flash nem um layout real. Padding, pilha, persistência, handlers físicos, outros textos e integração global continuam excluídos.

## Correção do emulador encontrada pelos testes

O teste altera a fonte 12 → 16 → 24 → 32 → 16 na mesma CPU. A primeira implementação manteve blocos de instruções traduzidos em cache após trocar o wrapper autoral e reutilizou a altura anterior. A correção invalida explicitamente o cache de tradução do intervalo DRAW depois de reescrever o código autoral de estresse.

Trata-se de um problema no ambiente de teste, não de cache do display físico. A altura continua sendo um parâmetro de geração/ensaio do host. Os testes anteriores que criavam uma CPU nova para cada altura não detectavam essa falha. A nova sequência passa nos cinco passos reutilizando a mesma CPU.

## Rotina original de ações de configurações

Foi executada separadamente a rotina em offset `0x5C34` com fixtures de argumentos e três ações, sem executar drivers/JPEG. É uma rotina de apresentação/ação das configurações, **não a identificação concluída do decodificador físico dos botões**.

| Ação no terceiro argumento (R2) | Resultado confirmado na fixture |
|---|---|
| 1 | Escreve idioma 0; solicita o recurso JPEG de fundo |
| 2 | Escreve idioma 1; solicita o recurso JPEG de fundo |
| 3 | Não muda o idioma; chama a prévia gráfica de brilho em `0x558C` |

Assim, acrescentar o valor 3 ao enum existente **não cria a terceira opção de idioma**: esse identificador já pertence a outra ação. A nova lista precisa de estado e encaminhamento próprios, com adaptação dos chamadores/handlers e revisão das outras configurações. Os testes mantêm os demais bytes de RAM inalterados e interceptam a chamada de brilho, sem executar controle do hardware.

As ações 1/2 confirmam também uma dependência do desenho de fundo externo. O arquivo JPEG não foi lido, extraído ou publicado; apenas a chamada em `0x9274` foi observada. Isso não revela se a imagem contém texto.

## Reprodução

Com as dependências opcionais instaladas, sem firmware:

```powershell
python -m src.dmc100_ptbr.integration_report --shadow-entries
python -m unittest discover -s tests -p 'test_arm_text_gate.py' -v
```

Com a amostra privada legítima:

```powershell
$env:DMC100_V14_PATH = 'private/firmware/APP_DMC-100_V1.4_250524.bin'
python -m src.dmc100_ptbr.integration_report --shadow-entries --firmware $env:DMC100_V14_PATH
python -m unittest discover -s tests -v
Remove-Item Env:DMC100_V14_PATH
```

`--shadow-entries` somente produz metadados JSON. O CLI relê o original ao terminar e rejeita uma alteração concorrente do arquivo. Não tem opção para salvar imagem, escrever flash ou conectar a dispositivo. As dependências nesta sessão estão isoladas em `private/tooling`, usadas por `PYTHONPATH`.

## Verificações

- As 32 combinações NZCVQ são verificadas em três rotas: nativa, buffer autoral e título traduzido (96 contratos).
- SP, LR, registradores e os três argumentos de pilha são conferidos no ponto de saída do gate.
- Cancelar/confirmar e retorno aos idiomas existentes continuam passando com branches reais na ROM virtual.
- Alturas consecutivas, ponteiro interior, formato não suportado e slots de texto inválidos têm testes próprios.
- Nos três idiomas, a execução privada com os branches produz as mesmas contagens e hash da fronteira de glifos que a referência anterior baseada em hooks.
- As diferenças na cópia ROM virtual ficam dentro das duas janelas de quatro bytes; o arquivo original mantém o SHA-256 `f8eab197553e117a374dc9926989b8ec2105baa8120682bd5c864bda30e8364d`.
- A execução das três ações originais confirma a colisão com brilho, sem modificar outras configurações.

Resultados finais da suíte e CI são registrados no PR. Testes privados exigem opt-in; a CI não baixa ou recebe firmware. Metadados são compartilháveis; os bytes relocados permanecem apenas na memória privada da sessão.

Resultado local final: **95/95 testes Python passaram** com motores e amostra privada. Sem opcionais: 52 passaram e 43 foram ignorados. Com motores, mas sem amostra, os dezesseis casos privados permanecem ignorados. A comparação privada do novo roteamento cobriu os três idiomas e a janela completa da aplicação, além dos argumentos do gate.

## O que ainda impede a instalação

A rota de texto deixou de depender de decisões Python, mas o aparelho completo não foi emulado. O host ainda injeta eventos abstratos, inicializa fixtures, mapeia memória inexistente no chip, gera o tamanho de estresse, substitui LCD e, na modalidade pública, o corpo original. A integração física precisa de endereços reais e trampolines refeitos para esse mapa.

Também faltam eventos/chamadores reais, persistência, modo de desenho 0, cobertura dos demais textos/renderizadores, caracterização dos recursos externos, contrato do bootloader/atualização e recuperação demonstrada nas unidades V1.3. A preservação do rastro de desenho não prova preservação temporal, funcionamento metrológico ou segurança elétrica. Não foi testada interrupção no meio do gate nem retomada do RTOS.

Nenhuma rotina de medição/calibração/segurança foi alterada, nenhum equipamento acessado e nenhuma imagem instalável produzida. [Etapa anterior](INTEGRACAO_ARM_UI.md) · [Preparação do teste real](PRIMEIRO_TESTE_REAL.md).
