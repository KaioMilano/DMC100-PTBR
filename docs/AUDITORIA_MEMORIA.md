# Inventário para posicionamento físico

## Classificação posterior e inicialização

Revisão posterior de 16/11/2026: os candidatos 0x21FC, 0x6A28, 0x7A34 e 0x9928 são instruções Thumb de 32 bits (SUB.W/MOV.W/MOV.W/ADD.W), não ponteiros para o intervalo. A ocorrência 0x132E4 está dentro da tabela de glifos de pares 24px, não constitui evidência de acesso a RAM. O inventário inicial abaixo permanece como histórico de candidatos, não como ocupação comprovada.

O campo em 0x17640 pertence a um descritor de inicialização: origem 0x0801E6F0, destino 0x200000A0, tamanho 0x71A0 e função 0x080071C8. Essa função zera o destino e não lê a origem. Assim, esse valor também não demonstra dados necessários no intervalo após o fim do arquivo.

A rotina original de limpeza foi executada isoladamente em Unicorn, com a RAM preenchida por canário 0xA5 e ROM protegida. Resultado: exatamente 29.088 bytes entre 0x200000A0 e 0x20007240 foram zerados; prefixo e sufixo permaneceram intactos. Não foi executado boot completo nem periférico. O estado artificial PT-BR em 0x20001000 fica dentro dessa região original inicializada. Isso não identifica qual objeto utiliza esse endereço, mas impede pressupor uma reserva independente para o protótipo.

Eliminar esses falsos positivos não comprova espaço livre de flash. A ocupação dinâmica da RAM, heap/pilha, mapa físico completo, botões, persistência e recuperação continuam pendentes. O teste isolado não autoriza instalar a tradução hoje.

16/11/2026. Base PR #14. A imagem V1.4 observada termina em 0x0801E6F0. O intervalo até 0x0801F400 não é uma reserva demonstrada.

`python -m src.dmc100_ptbr.memory_audit private/firmware/APP_DMC-100_V1.4_250524.bin` exige o fingerprint conhecido, lê palavras alinhadas e produz apenas metadados. Não extrai recursos ou cria imagem.

| Offset no arquivo | Valor candidato dentro do intervalo |
|---|---|
| 0x21FC | 0x0801F1A8 |
| 0x6A28 | 0x0801F04F |
| 0x7A34 | 0x0801F04F |
| 0x9928 | 0x0801F108 |
| 0x17640 | 0x0801E6F0 |

Há também duas palavras 0x0801F400 nos offsets 0xB174/0xD6BC, coerentes com a investigação anterior de configurações. A palavra 0x20001000, endereço escolhido artificialmente para estado nos ensaios, ocorre em 0x132E4.

**Esses candidatos não demonstram acessos de execução.** Podem ser dados, instruções ou ponteiros. Precisam de classificação por segmento e referências cruzadas; em particular, não se deve disassemblar linearmente dados e tratar o resultado como fluxo válido. Ausência de palavras também não exclui endereços calculados, heap, pilha, DMA ou referências indiretas.

O resultado não autoriza reservar nenhum byte. Os endereços virtuais ainda não foram substituídos por um mapa físico validado. A aplicação não fornece os bytes do bootloader abaixo de 0x08007000, e o firmware V1.3 das duas unidades não foi fornecido para comparação. Compatibilidade e recuperação permanecem sem demonstração.

Dois testes sintéticos cobrem limites exclusivos, duplicatas, cauda incompleta, intervalos inválidos e fingerprint desconhecido. O código não altera medição, calibração, configurações ou arquivos privados. A próxima etapa necessária é classificar esses candidatos e rastrear a inicialização/RAM antes de qualquer decisão de posicionamento. Não há imagem instalável nesta entrega.
