# Referências a recursos externos — fase visual

Consulta em 15/11/2026. Amostra privada com SHA-256 `f8eab197553e117a374dc9926989b8ec2105baa8120682bd5c864bda30e8364d`. Foram inspecionados caminhos/terminadores no executável e referências de chamadas na [decompilação comunitária fixada em 1a7684b](https://github.com/cakenes/dmc100/tree/1a7684b7a49f1d8bd4a9bab079d578663dda9912). Nenhum JPEG, bitmap, partição ou código de terceiros foi incorporado ao projeto.

## Inventário por família

| Família em UI | Ocorrências de caminhos | Indicação nas referências |
|---|---:|---|
| decorat | 25 | HOLD, setas, menu, lanterna, NCV e decoração |
| decorate | 25 | Conjunto paralelo de nomes; mesma classe de controles |
| mode | 6 | Ícones com nomes V/R/C/H/L/A |
| mode_1 | 6 | Outro conjunto dos seis ícones |
| cel | 5 | Bateria, arquivos numerados 1–5 |
| cell | 5 | Outro conjunto de estados de bateria |
| **Total** | **72** | Ocorrências no binário, não quantidade comprovada de arquivos existentes |

O marcador `2:` sugere unidade lógica; não revela por si só onde começa uma partição física. Não normalizar `decorat` para `decorate`, `cel` para `cell` nem eliminar duplicatas. Os nomes paralelos podem representar temas/variantes, mas o conteúdo visual e a finalidade exata não foram comprovados. LOGO é referência adicional fora do filtro UI e não entra no total de 72.

## Relação com telas

Os nomes de função abaixo são atribuições comunitárias. Os offsets são do arquivo; para a amostra observada, endereço físico = `0x08007000 + offset`. Não usar os rótulos de endereço da decompilação como endereços físicos.

| Área | Referências identificadas | Dependência demonstrada / limite |
|---|---|---|
| Medição | `ui_draw_hold_icon` (`0x003124`), `ui_draw_range_nav_arrows` (`0x0031BC`), `ui_draw_mode_icon` (`0x0035E0`), `ui_draw_battery_icon` (`0x003BE0`), `ui_draw_led_icon` (`0x00525C`), rotinas NCV (`0x0052F8`, `0x00627C`) | Chamadas usam JPEGs das famílias indicadas. Faltam pixels, dimensões e distribuição dos estados para reproduzir a interface original. A curva do simulador é inteiramente sintética. |
| Configurações e navegação | `ui_handle_settings_nav` (`0x005C34`), `ui_draw_menu_background` (`0x0061D8`) | Há referências a `decorat/menu.jpg` e `decorate/menu.jpg`. Submenus também usam texto e primitivas; não se afirma que cada item seja desenhado em JPEG. |
| Histórico | `ui_draw_main_menu` (`0x00AAD4`) usa imagens de menu e apresenta a opção de histórico | A dependência do menu é conhecida; a renderização específica da página de registros e sua cadeia completa de chamadas ainda não foram isoladas. A tabela do simulador é proposta autoral, não reconstrução. |
| Sobre | `ui_draw_about_screen` (`0x003F24`) apresenta primitivas e texto | Não há chamada JPEG direta demonstrada no corpo consultado. Cabeçalho, bateria global e composição completa permanecem pendentes; ausência local não prova independência total. |
| Carregamento | `ui_show_charging_screen` (`0x00B1B8`) e barras de carga | Desenho por primitivas/texto nas referências consultadas; outros avisos/ícones globais ainda precisam de rastreamento. O aviso do protótipo não foi aprovado para uso real. |

Os bitmaps do instrumento continuam indisponíveis. Não sabemos quais trazem palavras desenhadas nem se contêm só molduras/ícones. O simulador substitui todos os elementos por formas próprias: **nenhuma tela do simulador depende de arquivos externos FNIRSI**. O mapa acima descreve obstáculos para uma futura tradução da interface real.

## O que falta

Capturas legitimamente fornecidas podem ajudar a distinguir texto de imagem, mas devem ser revisadas antes de publicação. Uma eventual investigação privada de recursos externos exige escopo próprio; esta fase não lê unidades USB ou dumps do aparelho. Precisamos ainda de resolução/formato de cada recurso, referências por estado/tema, armazenamento/alinhamento e comportamento de falha quando um arquivo falta. Capacidade nominal de NOR não equivale a espaço disponível.
