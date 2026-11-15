# Inventário inicial de interface PT-BR

**Rascunho, não aprovado para instalação.** Os offsets abaixo foram conferidos na [amostra V1.4 identificada por SHA-256](ANALISE_V14_BINARIO.md), incluindo o terminador NUL. São offsets de arquivo, não endereços de flash.

| Offset (V1.4 reportado) | Original | PT-BR preferido | ASCII provisório | Observações |
|---|---|---|---|---|
| `0x005A44` | Language | Idioma | Idioma | Configurações |
| `0x005C00` | Brightness | Brilho | Brilho | Tela |
| `0x005C0C` | Temperature unit | Unidade de temperatura | Unid. temp. | Não alterar °C/°F |
| `0x005900` | AUTO shut_down | Desligamento automático | Deslig. auto | Extração começa em espaço em 0x0058FF |
| `0x006140` | System settings | Configurações do sistema | Ajustes sistema | Há duplicatas |
| `0x00ADE8` | History record | Histórico de registros | Historico | Validar fonte |
| `0x00AE00` | Measurement | Medição | Medicao | Validar fonte |
| `0x00AE58` | About | Sobre | Sobre | Identificação |
| `0x003DEC` | Return | Voltar | Voltar | Menu |
| `0x004B6C` | Data saved | Dados salvos | Dado salvo | Mensagem |
| `0x00554C` | Low battery | Bateria fraca | Bat. fraca | Aviso |
| `0x005558` | Shutdown | Desligar | Desligar | Revisar contexto |
| `0x00B290` | Do not use while charging | Não utilize durante o carregamento | Nao usar durante a carga | Extração começa em espaço em 0x00B28F; **segurança: revisão obrigatória** |

Não inferir que cada substituição cabe no mesmo lugar. Codificação, terminador, ponteiros, referência cruzada, fontes e checksums precisam ser investigados. Nenhum código do projeto grava um patch.

Correção de offsets baseada na lista e nas referências `+1` da decompilação comunitária, confirmada no original analisado. Foram confirmadas também System settings em `0x00AE28`, Language em `0x006150` e English em `0x0060D0`/`0x0072C8`, fora dos 14 pontos de comparação iniciais. O analisador procura ocorrências terminadas em NUL de todos os textos conhecidos, sem assumir que sejam objetos independentes.
