# Inventário inicial de interface PT-BR

**Rascunho, não aprovado para instalação.** Os offsets abaixo são os relatados por terceiros para a V1.4 e ainda não foram conferidos contra o arquivo original pelo projeto.

| Offset (V1.4 reportado) | Original | PT-BR preferido | ASCII provisório | Observações |
|---|---|---|---|---|
| `0x005A44` | Language | Idioma | Idioma | Configurações |
| `0x005C00` | Brightness | Brilho | Brilho | Tela |
| `0x005C0C` | Temperature unit | Unidade de temperatura | Unid. temp. | Não alterar °C/°F |
| `0x0058FF` | AUTO shut_down | Desligamento automático | Deslig. auto | Verificar largura |
| `0x006140` | System settings | Configurações do sistema | Ajustes sistema | Há duplicatas |
| `0x00ADE8` | History record | Histórico de registros | Historico | Validar fonte |
| `0x00AE00` | Measurement | Medição | Medicao | Validar fonte |
| `0x00AE58` | About | Sobre | Sobre | Identificação |
| `0x003DEC` | Return | Voltar | Voltar | Menu |
| `0x004B6C` | Data saved | Dados salvos | Dado salvo | Mensagem |
| `0x00554C` | Low battery | Bateria fraca | Bat. fraca | Aviso |
| `0x005558` | Shutdown | Desligar | Desligar | Revisar contexto |
| `0x00B28F` | Do not use while charging | Não utilize durante o carregamento | Nao usar durante a carga | **Segurança: revisão obrigatória** |

Não inferir que cada substituição cabe no mesmo lugar. Codificação, terminador, ponteiros, referência cruzada, fontes e checksums precisam ser investigados. Nenhum código do projeto grava um patch.
