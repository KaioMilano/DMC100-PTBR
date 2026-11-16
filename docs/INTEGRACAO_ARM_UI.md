# Menu, UTF-8 e acentos integrados em CPU virtual

16/11/2026 · Base: PR #12. Desenvolvimento autorizado pelo mantenedor, que possui duas unidades V1.3. Esta entrega avança a implementação; **não conclui o firmware, não gera instalável e não executa teste físico**.

## Implementação demonstrada

`arm_ui.py` mantém seletor, estado, ponte ARM de eventos, wrapper de desenho, decodificador UTF-8 e renderizador na **mesma CPU virtual**. Uma chamada direta ARM → ARM aplica o evento e escreve o idioma na RAM virtual. O Python não copia o resultado dos três registradores entre instâncias como na primeira prova.

O ponto original em offset `0x5938` é redirecionado por hook do emulador ao wrapper autoral. O wrapper chama o menu original intacto e redesenha a região de opções com três linhas, preservando título/ornamentos originais no ensaio privado. Navegar, confirmar, cancelar e voltar aos idiomas existentes são executados em Thumb. A terceira opção mostra **Português (BR)** com ê autoral. A confirmação é volátil; não é a confirmação/persistência do firmware original.

Há duas modalidades:

- Sem imagem: a chamada ao menu original é substituída por um retorno sintético. A CI demonstra apenas o código autoral.
- Com a amostra privada V1.4 identificada por hash: o menu original é executado. Opcionalmente também executamos sua rotina de texto/glifos para chinês, inglês e os fragmentos ASCII da composição. Apenas fronteiras de LCD permanecem interceptadas. Rastros de pixels proprietários não são exportados: somente contagens e hash. Os pixels dos acentos próprios podem ser conferidos nos testes.

Os novos endereços `0x10000000`–`0x1000FFFF` e o estado em `0x20001000` são **reservas artificiais do emulador**, sem prova de disponibilidade no aparelho. R4–R11 e SP são conferidos, a ROM é protegida e comparada; desenho não pode mudar estado. Eventos só podem escrever a região declarada de estado e o byte de idioma. Execução tem regiões permitidas, limite de instruções/tempo e escritas limitadas à pilha/reservas de teste. Isso não modela interrupções, RTOS, tempos de resposta, alimentação ou o instrumento completo.

Os hooks ainda fornecem serviços essenciais: redirecionam a entrada original, escolhem o título PT-BR por ponteiro, fornecem comprimento conhecido e direcionam os textos autorais ao renderizador. A altura de estresse também é fornecida pelo host. Nenhum salto foi inserido na ROM, nenhum handler físico de botões foi substituído, e o boot não foi emulado. **Não é uma integração pronta para transplantar os bytes para flash.**

## UTF-8 e fonte própria

`arm_utf8.py` aceita ASCII imprimível, NUL e os 26 caracteres previstos após normalização NFC: `áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ`. O decodificador Thumb recebe ponteiro/comprimento, devolve ponto Unicode, bytes consumidos e índice do glifo. Entrada ausente/NUL encerra; sequências inválidas ou não suportadas devolvem U+FFFD com avanço de um byte. Não é um decodificador Unicode geral; o renderizador usa `?` como fallback.

`accent_font.py` contém bases e marcas desenhadas à mão para esta prova. Nenhuma fonte do sistema ou bitmap FNIRSI foi copiado. Uma tabela própria armazena por registro uma chave Unicode de dois bytes e nove linhas de cinco bits: **26 × 11 = 286 bytes**. O renderizador ARM faz a ampliação inteira em tempo de execução nos tamanhos 12/16/24/32, com avanço de meia altura e uma coluna de espaçamento. Os pixels coincidem com o rasterizador Python nas 104 combinações de caractere/tamanho.

ASCII é delegado em fragmentos de um caractere à rotina original de texto; os acentos usam chamadas de pixel com desenhos próprios. O ê na palavra “Português” ocupa um avanço, não dois por estar em UTF-8. Pixels autorais são limitados a 240 × 320 antes de atingir a fronteira de desenho. Este caminho suporta overlay 1; apagar fundo/mode 0 e outros renderizadores ainda não estão integrados. Misturar a fonte original e a nova exige revisão visual de peso, baseline e legibilidade; os glifos são protótipos.

A redução de armazenamento usa divisão inteira e chamadas por pixel durante a ampliação. O ê a 16 px produz quarenta chamadas autorais de pixel no ensaio. Não foi demonstrado custo de tempo, ausência de cintilação ou compatibilidade com interrupções/RTOS reais. Velocidade da CPU virtual não mede desempenho do display físico.

O texto completo da terceira opção, começando em x=106, termina em x=190/218/274/330 para alturas 12/16/24/32. **Cabe a 12/16; transborda a 24/32.** Há diagnóstico e recorte de pixels, sem abreviação automática que esconda o problema. O padrão do menu é 16. Os tamanhos maiores são ensaios de estresse, não aprovação do layout.

## Memória: redução demonstrada, posicionamento pendente

As quatro tabelas pré-expandidas custariam 3.848 bytes, incluindo chaves. A primeira versão desta sessão usou tabela 16 px e somava 1.246 bytes de componentes; a alternativa com as quatro tabelas somaria 4.626. Essa hipótese foi substituída pela fonte compacta de 286 bytes, ampliada em ARM.

| Componente atual | Bytes lógicos |
|---|---:|
| Seletor | 64 |
| Ponte de eventos | 36 |
| Wrapper de menu | 268 |
| Decodificador UTF-8 | 112 |
| Renderizador misto e recorte | 252 |
| Índice Unicode do decodificador | 52 |
| Fonte compacta | 286 |
| Ponteiros das três linhas | 12 |
| Textos autorais UTF-8 com NUL | 34 |
| **Total desta prova** | **1.116** |

Esse total **não é orçamento completo de firmware**: exclui padding de páginas virtuais, pilha, trampolins em endereços físicos, handlers de botões, persistência, cobertura global de traduções e recursos gráficos. Não inclui como código embarcado as decisões realizadas pelos hooks Python. Os endereços de retorno/dados ainda apontam para reservas virtuais e precisam ser redesenhados/realocados. O intervalo de 3.344 bytes antes das configurações continua sem prova de estar livre; o tamanho menor não o torna disponível.

## Carga de configurações original

`settings_probe.py` executa somente o trecho original de decodificação em offset `0xD56C`, com um **buffer RAM sintético pré-carregado** em `0x200000A0` e marcador zero. A função inicial de busca dos dados é substituída, e qualquer caminho de reset/flash/periférico é rejeitado.

Os 256 valores de idioma foram copiados pelo trecho original para `0x200001D8`, sem validação nessa etapa. Também foi demonstrada a truncagem de halfword para byte (`0x1002` → 2). As sete escritas de configuração foram conferidas e limitadas. Isso confirma apenas a decodificação do buffer; **não comprova serialização, gravação em flash, validação na inicialização ou comportamento dos demais consumidores**. Não rodamos a rotina de gravação nem tratamos essas configurações como calibração conhecida.

## Reprodução e resultados

Instale as dependências de `requirements-arm.txt` num ambiente de desenvolvimento. A versão pública não requer firmware:

```powershell
python -m unittest discover -s tests -v
python -m src.dmc100_ptbr.integration_report
```

Com a cópia privada, somente leitura:

```powershell
$env:DMC100_V14_PATH = 'private/firmware/APP_DMC-100_V1.4_250524.bin'
python -m unittest discover -s tests -v
python -m src.dmc100_ptbr.integration_report --firmware $env:DMC100_V14_PATH
Remove-Item Env:DMC100_V14_PATH
```

Nesta sessão as dependências ficam isoladas em `private/tooling`, acessadas por `PYTHONPATH`. A CI instala os motores em um job próprio e executa a suíte pública completa. Não baixa a amostra ou recursos do aparelho. Resultados finais da suíte e da CI ficam registrados no PR; a amostra original mantém o hash `f8eab197553e117a374dc9926989b8ec2105baa8120682bd5c864bda30e8364d`.

Resultado local final: **86/86 testes Python passaram** com motores/amostra privada. Sem opcionais passaram 50 e foram ignorados 36. Com motores e sem amostra, os quatorze testes privados permanecem ignorados. Nenhuma dependência do simulador visual foi alterada.

Os ensaios cobrem pixels das 104 combinações, recorte, posicionamento após UTF-8, sequência de confirmação/cancelamento, estado inalterado no desenho, decodificação ASCII/acentos/inválidos e carga RAM dos 256 valores de idioma. Os testes privados de coexecução repetem o desenho em três idiomas e conferem hash estável da fronteira de glifos. Nenhuma figura nativa foi publicada.

## Pendências que impedem o instalável

1. Substituir os hooks por implementação embarcada e ligar os eventos reais, incluindo inicialização/seleção inicial e cancelamento. O handler original ainda conhece dois idiomas.
2. Integrar os demais textos e renderizadores da aplicação. O despachante anterior continua sendo uma prova distinta; não está acoplado globalmente a este caminho UTF-8. Avisos, medições e calibração não foram modificados.
3. Validar persistência e seus consumidores, sem apagar a página de configurações; o ensaio de buffer não grava nada.
4. Determinar memória física e trampolins seguros, além das dependências JPEG ainda não caracterizadas. A aplicação fornecida começa em `0x08007000` e não inclui o bootloader anterior a esse endereço.
5. Obter evidência do contrato de atualização/integridade e recuperação aplicável às duas unidades V1.3. O fluxo comunitário de restauração continua sendo referência não demonstrada nessas unidades, não um procedimento pronto do nosso projeto.
6. Revisar e validar uma futura imagem privada completa antes do primeiro teste isolado de inicialização/UI. Nenhum teste físico foi realizado nesta etapa.

Esses itens não exigem contato com fabricante, mas também não podem ser considerados resolvidos por autorização ou por passar nos testes de CPU. O trabalho solicitado permanece **em andamento**, não concluído para instalação. [Preparação física](PRIMEIRO_TESTE_REAL.md).
