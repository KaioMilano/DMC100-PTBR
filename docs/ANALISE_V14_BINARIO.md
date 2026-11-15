# Análise privada do arquivo V1.4

Data: 15/11/2026. Escopo estritamente offline e somente leitura. Este documento contém resultados e metadados revisados; não contém firmware, imagens, bitmaps de fonte ou decompilação.

## Proveniência e identificação

Arquivo: `APP_DMC-100_V1.4_250524.bin`.

- URL fornecida pelo mantenedor: `https://cdn.shopify.com/s/files/1/0694/8310/2426/files/APP_DMC-100_V1.4_250524.bin?v=1748313820`.
- O link V1.4 da [página do distribuidor VX](https://vx.com.ar/manuales-y-descargas/) aponta para a mesma URL. Isso confirma a associação pública do link, não uma assinatura do fabricante.
- HTTP 200, URL final idêntica, Content-Type `application/octet-stream` e Content-Length 95.984.
- Tamanho efetivamente recebido: **95.984 bytes** (`0x176F0`).
- SHA-256: **`f8eab197553e117a374dc9926989b8ec2105baa8120682bd5c864bda30e8364d`**.
- O conteúdo não começa como HTML/XML; vetores plausíveis, instruções Thumb e textos esperados sustentam a classificação como imagem de aplicação ARM, não página de erro.
- Uma segunda leitura HTTP produziu os mesmos bytes. SHA-256 local permaneceu igual depois das análises e dos testes.

O arquivo foi preservado em `private/firmware/` dentro do checkout local. Essa pasta e os relatórios brutos estão ignorados pelo Git. Não foi adicionado ao índice. O hash identifica o conteúdo observado; sem manifesto assinado independente, não prova autenticidade ou compatibilidade com uma revisão do equipamento.

## Endereçamento: descoberta crítica

Os primeiros words little-endian são SP `0x20007240` e reset `0x0800721D`. O bit Thumb é 1. Com base de carga **`0x08007000`**, o reset aponta para offset **`0x00021C`**, onde a desmontagem local mostra código de inicialização coerente. O mapa público do DOOM usa essa mesma base. Os ponteiros das tabelas de fontes também se resolvem integralmente dentro do arquivo nessa base.

Portanto, para esta imagem: `endereço_flash = 0x08007000 + offset_arquivo`. A imagem ocupa o intervalo `[0x08007000, 0x0801E6F0)`. Isso não descreve bootloader, configurações ou toda a flash física.

O guia cakenes usa base `0x08000000` em rótulos de decompilação. Seus offsets de arquivo úteis não devem ser confundidos com endereços físicos. Por exemplo: offset `0x005A44` corresponde a `0x0800CA44`, e a rotina de texto em offset `0x0012F2` corresponde a `0x080082F2`. Ler um ponteiro de fonte como se sua base fosse zero coloca algumas tabelas além do arquivo e produz uma falsa conclusão de truncamento. O reset sem bit Thumb é `0x0800721C`, distinto do word armazenado.

Essa correção não é licença para realocar ou gravar qualquer dado. Ainda não há reconstrução completa do mapa de seções, referências ou integridade.

## Strings, terminadores e referências

O inspetor atualizado encontra **14/14 textos**, todos com NUL imediatamente após o texto esperado. Os dois ajustes de offsets foram confirmados no binário:

| Extração antiga | Início útil confirmado | Motivo |
|---|---|---|
| `0x0058FF` | `0x005900` | O byte anterior é espaço; o código forma referência ao texto seguinte |
| `0x00B28F` | `0x00B290` | Mesmo caso na mensagem de carregamento |

Duplicatas terminadas em NUL:

| Texto conhecido | Offsets de arquivo |
|---|---|
| Language | `0x005A44`, `0x006150` |
| English | `0x005A5C`, `0x0060D0`, `0x0072C8` |
| System settings | `0x006140`, `0x00AE28` |

A varredura de instruções ADR Thumb T1 encontra **21 candidatos** de referências aos textos conhecidos/duplicatas. Exemplos conferidos por desmontagem: instrução em offset `0x005980` referencia `0x005A44`; `0x00B1F2` referencia `0x00B290`. A procura ingênua por ponteiros absolutos de 32 bits não encontrou esses endereços: são referências relativas ao PC. Isso reforça a necessidade de analisar instruções, não apenas substituir valores em tabelas.

A ferramenta varre halfwords alinhados, sem classificar automaticamente código e dados. Os 21 candidatos não representam todas as referências: outras formas de ADR, ponteiros indiretos, substrings e tabelas ainda podem existir. O inventário ASCII bruto encontra 859 sequências imprimíveis com pelo menos quatro bytes; muitas são coincidências em instruções/bitmaps. Não são 859 mensagens de interface. Há 40 candidatos de ASCII intercalado com zero; isso também não demonstra uso de UTF-16 na interface.

## Fontes e codificação

A leitura das instruções da rotina de texto confirma o fluxo: byte até `0x7F` avança um byte e meia altura; byte superior segue caminho de pares, avança dois bytes e uma altura. As alturas tratadas são 12, 16, 24 e 32. A variação ASCII aceita índices derivados de `caractere - 0x20`; a disposição das tabelas suporta 95 glifos imprimíveis de `0x20` a `0x7E` por tamanho. Isso não demonstra suporte ao byte DEL ou a Latin-1.

Os literais de ponteiros foram lidos diretamente do original; os limites de registros foram confrontados com a lógica de iteração e com a continuidade entre tabelas. Fins são exclusivos:

| Tipo | Altura | Literal no arquivo | Tabela no arquivo | Fim | Registros × bytes |
|---|---:|---|---|---|---:|
| ASCII | 12 | `0x0014FC` | `0x00F17A` | `0x00F5EE` | 95 × 12 |
| ASCII | 16 | `0x001500` | `0x00F5EE` | `0x00FBDE` | 95 × 16 |
| ASCII | 24 | `0x001504` | `0x00FBDE` | `0x010DAE` | 95 × 48 |
| ASCII | 32 | `0x0014F8` | `0x010DAE` | `0x01256E` | 95 × 64 |
| Pares | 12 | `0x0016D4` | `0x01256E` | `0x012728` | 17 × 26 |
| Pares | 16 | `0x0017C8` | `0x012728` | `0x0130DA` | 73 × 34 |
| Pares | 24 | `0x0018C0` | `0x0130DA` | `0x013BD6` | 38 × 74 |
| Pares | 32 | `0x001A78` | `0x013BD6` | `0x014888` | 25 × 130 |

Total dessas oito tabelas: **22.286 bytes**, incluindo identificadores de dois bytes nos registros de pares. Nenhum bitmap foi exportado. O perfil `v14.py` só aplica esses descritores ao SHA-256 exato acima; outros arquivos recebem apenas análise genérica.

Todas as chaves das tabelas de pares podem ser decodificadas como GBK; GB2312 cobre 16/17, 72/73, 37/38 e 25/25 respectivamente. Algumas chaves isoladas também passam no decodificador UTF-8 por coincidência. Isso favorece a hipótese de repertório chinês/GBK, sem estabelecer uma implementação Unicode geral.

Foi verificada a presença dos caracteres solicitados `áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ` codificados como GB2312, GBK e UTF-8. **Nenhuma dessas chaves está nas tabelas examinadas.** Não é suficiente trocar strings por UTF-8 para obter português acentuado. Um rótulo sem acentos é útil no protótipo, mas não resolve a fidelidade linguística nem autoriza alteração do renderizador.

## Recursos gráficos e memória

Há **72 ocorrências candidatas** de caminhos JPEG sob UI no executável. A varredura encontra um marcador SOI candidato em `0x016EDD` e nenhum EOI; não é evidência de um JPEG completo incorporado. Não foi obtida partição externa ou pasta UI do equipamento, portanto nomes de arquivos não permitem dizer quais contêm texto desenhado, suas dimensões, compressão ou capacidade disponível.

O tamanho do arquivo e o SP inicial não determinam RAM livre. Também não demonstram espaço de flash reutilizável depois da imagem. O cálculo de fonte e o mapa de carga são metadados; limites de heap/pilha, configuração, calibração e regiões do bootloader permanecem fora do mapa confirmado. Nenhum checksum foi ajustado ou assumido como validado.

## Reprodução e resultados

Na raiz do checkout, os comandos não escrevem no firmware:

```powershell
python -m src.dmc100_ptbr.inspect private/firmware/APP_DMC-100_V1.4_250524.bin --json
python -m src.dmc100_ptbr.analyze private/firmware/APP_DMC-100_V1.4_250524.bin
python -m unittest discover -s tests -v
$env:DMC100_V14_PATH = 'private/firmware/APP_DMC-100_V1.4_250524.bin'
python -m unittest discover -s tests -v
Remove-Item Env:DMC100_V14_PATH
```

Testes padrão: 24 aprovados e 3 testes privados ignorados intencionalmente. Com o caminho privado: **27/27 aprovados** no Windows/Python 3.11.15. Os testes privados verificam fingerprint/vetores, terminadores/duplicatas e limites das fontes/SHA-256 preservado. CI usa somente dados sintéticos, sem download proprietário. Resultados remotos finais são vinculados no PR.

A conferência local de instruções usou Capstone instalado isoladamente em `private/tooling`, sem dependência adicionada ao projeto; pacote instalado 5.0.9 (módulo informa 5.0.7). Não se executou código do firmware. As ferramentas e testes versionados usam apenas a biblioteca padrão do Python.

## Recomendação

A V1.4 está suficientemente identificada por conteúdo para continuar a análise offline desta amostra. O caminho mais conservador é desenvolver telas autorais com os rótulos ASCII e medidas reproduzidas, revisar terminologia e avisos, e só então estudar uma estratégia de acentuação. Antes de qualquer fase de patch, é necessário completar referências, recursos externos, revisão de hardware e mecanismo de integridade. Não há base para declarar a tradução segura, concluída ou pronta para instalação.
