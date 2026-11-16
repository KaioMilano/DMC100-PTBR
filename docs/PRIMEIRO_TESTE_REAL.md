# Preparação do primeiro teste real — ainda sem imagem candidata

16/11/2026 · Base: PR #11. O mantenedor autorizou preparar instalação e primeiro teste real, e informou possuir **duas unidades, ambas V1.3**. A restrição anterior de não instalar foi substituída por esse objetivo. Isso não demonstra compatibilidade, recuperação ou prontidão do código. Original privado, medição, calibração, segurança e ativos proprietários continuam preservados.

**Resultado desta etapa: não há firmware PT-BR pronto para gravar.** Não foram gerados arquivos instaláveis, acessados dispositivos ou executados instaladores. A entrega anterior é um simulador visual e código ARM autoral em endereços artificiais. Não é uma aplicação completa que possa ser empacotada para o bootloader.

## Avanço na integração original

Foi implementado `src/dmc100_ptbr/original_menu.py`, que executa as instruções do **menu original V1.4**, offset `0x5938`, numa CPU virtual. Aceita exclusivamente a amostra de SHA-256 `f8eab197553e117a374dc9926989b8ec2105baa8120682bd5c864bda30e8364d`. A ROM é protegida e conferida; somente escritas de pilha são permitidas. SP, R4–R11 e idioma são conferidos na saída. Execução fora da função e dos pontos de interceptação é rejeitada, com limite de instruções e tempo.

Chamadas de desenho são substituídas antes de executar drivers ou glifos. Não se exportam fontes, textos chineses, imagens ou pixels. São ensaios de fluxo/argumentos, não capturas do equipamento. As cores da estrutura RAM são fixtures; não representam todas as configurações ou temas.

O teste confirmou:

- Idiomas 1, 2 e 255 produzem exatamente o mesmo rastro de chamadas/argumentos; 0 produz outro ramo.
- Cada execução tem três chamadas de texto: título e duas alternativas. Não aparece uma terceira opção ao escrever 2.
- No ramo inglês o título está em (93, 158), opções em (106, 203) e (106, 244), fonte 16 e modo 1.
- O menu termina antes de `0x5A3C`. O limite inicial de ensaio `0x5A34` interrompia o ramo chinês; foi corrigido após conferir o salto de retorno em `0x5A38` e testar os quatro idiomas. Não se alterou o original para contornar a falha.

O despachante anterior traduz textos, mas não cria geometria, entrada ou persistência para uma terceira opção. O seletor do PR #11 ainda usa contrato próprio e passagem pelo harness Python. A integração exige redesenhar a lista, ligar eventos reais e auditar os consumidores do idioma, inclusive inicialização. Não basta concatenar as duas provas ARM.

Reprodução em ambiente com as dependências opcionais:

```powershell
$env:DMC100_V14_PATH = 'private/firmware/APP_DMC-100_V1.4_250524.bin'
python -m src.dmc100_ptbr.original_menu $env:DMC100_V14_PATH
python -m unittest discover -s tests -v
Remove-Item Env:DMC100_V14_PATH
```

Na sessão local, `PYTHONPATH` aponta para as dependências isoladas em `private/tooling`. O JSON do comando expõe apenas metadados e resultados, não os rastros completos.

## Atualização e recuperação: evidência encontrada

Foi revisado, **sem executar**, o código comunitário no commit [`0cdc78eb66cdddacc43112d5f79c258c4a5440b7`](https://github.com/ArturBieniek4/DMC100-Doom/tree/0cdc78eb66cdddacc43112d5f79c258c4a5440b7). Trata-se de outro programa que substitui as funções de multímetro; não é um pacote de tradução nem comprovação para nossas unidades.

| Fonte | Informação / limite |
|---|---|
| [README, restauração](https://github.com/ArturBieniek4/DMC100-Doom/blob/0cdc78eb66cdddacc43112d5f79c258c4a5440b7/README.md#going-back-to-the-original-firmware) | Descreve restauração dependente de firmware original e cópia das imagens UI; não foi demonstrada por nós |
| [restore.py](https://github.com/ArturBieniek4/DMC100-Doom/blob/0cdc78eb66cdddacc43112d5f79c258c4a5440b7/tools/restore.py) | Assume aplicação em `0x08007000`, flash de 128 KiB, RAM até `0x20008000`, configurações em `0x0801F400` e página de 1.024 bytes |
| restore.py, load_firmware | Checa comprimento, SP, bit Thumb e destino de reset; não estabelece autenticação, checksum ou compatibilidade do nosso derivado |
| restore.py, stock_image | Preenche a imagem até o fim da página de configurações, 100.352 bytes no total; pode apagar/restaurar essa página |
| [install.py](https://github.com/ArturBieniek4/DMC100-Doom/blob/0cdc78eb66cdddacc43112d5f79c258c4a5440b7/tools/install.py) | Contém operações de cópia, remoção e formatação relacionadas a dados/UI; não é ferramenta somente leitura nem deve ser reutilizada como teste da tradução |

A amostra original tem 95.984 bytes; o fluxo preenchido descrito acrescenta 4.368 bytes, incluindo o intervalo de 3.344 bytes e a página de configurações. Isso mostra por que preservar o tamanho/limites e compreender apagamento por página importa. **Não demonstra que o intervalo esteja livre.** Não geramos a imagem preenchida nem fornecemos comando de gravação.

A ausência de uma validação de checksum nesse script não demonstra ausência de checksum no bootloader. O script não contém o bootloader das nossas unidades. O relato de que a página contém configurações e não calibração precisa de confirmação independente; não autoriza apagá-la.

## Sequência até o primeiro candidato

1. Reservar uma unidade como referência original V1.3 e identificar a outra nos registros de desenvolvimento. Duas unidades não substituem recuperação. Compatibilidade física ainda não confirmada; não solicitamos abertura ou conexão nesta etapa.
2. Concluir integração de menu e consumidores de idioma em emulação, com fallback inglês/chinês, retorno e estados de inicialização. Depois resolver glifos/acentos e dependências gráficas.
3. Determinar espaço de código/dados e trampolins em memória real, sem atingir vetores, medição, calibração, configurações ou bootloader. Repetir análise de todas as diferenças e ensaios diferenciais.
4. Investigar contrato de atualização, apagamento por página, integridade e recuperação aplicável à revisão. Manter uma cópia legítima de restauração e recursos necessários; não tratar o pacote DOOM como plano já validado.
5. Somente com um candidato técnico verificável, preparar artefato privado, hashes, mapa de diferenças e roteiro de retorno. O GitHub recebe código autoral, testes e metadados, nunca firmware ou recursos privados.
6. O primeiro ensaio físico terá escopo de inicialização, tela, idioma, botões e desligamento em bancada isolada, sem pontas conectadas, condutores no alicate, carregamento ou circuitos energizados. A aprovação da UI não libera uso em medições; comparações metrológicas e revisão de avisos são etapas posteriores.

Os itens 2–4 ainda são trabalho de engenharia, não caixas que possam ser liberadas por uma confirmação do mantenedor. Contato com fabricante continua opcional. A autorização para desenvolver e testar está registrada; não é necessário pedi-la novamente para continuar o trabalho autorizado.

## Testes e entrega

Três testes novos verificam rejeição de amostra desconhecida, comparação dos quatro idiomas no menu original e coordenadas/argumentos das chamadas. Os dois últimos exigem amostra privada e não rodam com dados proprietários na CI. A suíte Python passou localmente **59/59** com motores opcionais e amostra privada; sem esses insumos passaram 40 e foram ignorados 19 opcionais. A imagem original permaneceu intacta. Resultados da CI são registrados no PR desta etapa.

[Integração e mapa](INTEGRACAO_FIRMWARE.md) · [Versão testável no computador](VERSAO_TESTAVEL.md).
