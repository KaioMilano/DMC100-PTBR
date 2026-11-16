# Integração real PT-BR — situação e bloqueios

Atualização de 16/11/2026: o mantenedor optou por avançar sem contato com o fabricante. Esse contato não é pré-requisito para continuar a engenharia independente. Foi implementada uma [prova ARM do despachante de textos](DESPACHANTE_ARM.md), executada em CPU virtual e comparada com a rotina original privada. Os itens abaixo descrevem a avaliação anterior e os limites para futura instalação, não uma obrigação de solicitar autorização para cada avanço offline.

Data: 16/11/2026. Base: PR #8. O mantenedor confirmou que deseja avançar do simulador para firmware PT-BR destinado ao aparelho. A confirmação autoriza o desenvolvimento, mas não comprova prontidão técnica. Permanecem as restrições de preservar o original, não gravar no equipamento, não alterar medição/calibração/segurança e não publicar arquivos proprietários.

**Resultado atual: firmware instalável não pronto. Nenhum binário modificado foi gerado.** O mantenedor informou não possuir cópia da pasta UI, identificação da revisão de hardware ou recuperação documentada. Esses dados não podem ser substituídos por testes do simulador.

## Mapa confirmado na amostra V1.4

SHA-256: `f8eab197553e117a374dc9926989b8ec2105baa8120682bd5c864bda30e8364d`. Arquivo original preservado privadamente, sem modificação.

| Item | Valor / evidência |
|---|---|
| Base da aplicação | `0x08007000` |
| Fim exclusivo da aplicação | `0x0801E6F0` |
| Base da estrutura de configurações na RAM | `0x200001B8`, corroborada em sete literais de rotinas de UI |
| Campo de idioma | deslocamento `0x20`, endereço RAM `0x200001D8` |
| Operação de UI conferida | leitura de byte do campo na rotina de idioma, instrução em offset `0x00596C` |
| Carga do idioma conferida | escrita do byte do campo na rotina de carga, em offset `0x00D580` |
| Buffer de carga/gravação | `0x200000A0`, literais em `0x00D5A0` / `0x00D6B8` |
| Endereço de configurações em flash referenciado pelo gravador | `0x0801F400`, literal em `0x00D6BC`; outra referência em `0x00B174` |
| Intervalo entre fim da aplicação e início referenciado de configurações | **3.344 bytes**, ainda **não comprovados como espaço livre** |

Esses números não devem ser transplantados para outro arquivo ou revisão. A carga observada lê o idioma de um campo de 16 bits do buffer e o coloca no byte da estrutura RAM; a serialização completa ainda exige rastreamento. O mapa não identifica dados de calibração nem autoriza modificar páginas de flash.

As condições zero/não zero continuam apontando para dois ramos de idioma. Rotinas candidatas relevantes, com offsets de arquivo: idioma `0x005938`, navegação de configurações `0x005C34`, seleção inicial `0x00710C`, menu principal `0x00AAD4`, carga `0x00D56C` e gravação `0x00D678`. O cruzamento da decompilação com literais gerou vinte funções candidatas a investigar; não é uma análise completa de fluxo nem prova de que todo acesso em cada função trate do idioma. Nomes comunitários de funções não são documentação do fabricante.

## Arquitetura a investigar

Uma hipótese é preservar os ramos originais chinês/inglês e selecionar textos PT-BR no ponto de desenho de texto, quando o idioma proposto estiver ativo. Isso poderia evitar reescrever cada ramificação de tela. A rotina principal de texto foi identificada em offset `0x0012F2` (endereço `0x080082F2`), mas há também outra rotina de texto em `0x00139E`, chamadas diretas de glifos, buffers formatados e recursos gráficos.

Essa hipótese **não está implementada ou demonstrada no firmware**. Ainda requer cobertura de todas as chamadas, ABI, registradores/flags, comportamento temporal, retorno seguro para os idiomas existentes e compatibilidade com inicialização/configuração. Traduzir só os textos literais interceptados deixaria outros textos sem tradução. Não se deve recompilar pseudocódigo comunitário como substituto do original, nem aplicar um salto em código sem validar os efeitos.

A terceira opção também exige mudanças no menu/seleção e compatibilidade dos valores persistidos. Apenas escrever “2” não cria o idioma. A alternativa de substituir o inglês diretamente reduziria parte da implementação, mas removeria a escolha inglesa e não cumpre o produto trilíngue pretendido; não foi feita.

## Fontes e recursos

Os 3.344 bytes de intervalo não cobrem sequer a estimativa anterior de 3.848 bytes para 26 glifos em meia largura nos quatro tamanhos, sem contar código/textos/índices. Isso não demonstra impossibilidade: um subconjunto de glifos/tamanhos ou outra arquitetura pode ter custo diferente. Também não demonstra espaço utilizável; o intervalo precisa de mapa e validação próprios. O custo de textos e gráficos continua adicional.

A análise encontra **64 caminhos JPEG únicos terminados em NUL** sob as seis famílias UI, correspondentes às 72 ocorrências já reportadas. A diferença é de duplicatas, não arquivos recuperados. Nenhum desses recursos foi fornecido nesta fase. Não sabemos quais incorporam palavras ou dependem de temas; LOGO é referência adicional fora desse conjunto. Os desenhos do simulador não substituem automaticamente esses arquivos no equipamento.

Foi consultada a [página oficial de downloads](https://www.fnirsi.com/pages/manuals-firmwares). O catálogo dinâmico não expôs arquivos no conteúdo textual acessível; a requisição pública ao endpoint de downloads indicado pela página retornou HTTP 403. Não houve tentativa de contornar esse acesso. Não se conclui que o fabricante não disponibilize recursos por outro canal. O [projeto DOOM](https://github.com/ArturBieniek4/DMC100-Doom) descreve depender das imagens originais para restauração, não um pacote universal validado para esta unidade. Nenhuma instrução de instalação desse projeto foi executada.

## Ferramenta de avaliação

```powershell
python -m src.dmc100_ptbr.readiness private/firmware/APP_DMC-100_V1.4_250524.bin
```

O comando só lê e imprime metadados. Retorno 1 significa que a prontidão não foi demonstrada; o comando não possui um caminho que gere/aprove firmware. O perfil de endereços é aplicado somente ao SHA-256 observado. Se existir futuramente uma cópia legítima **local** de UI, pode-se informar `--ui-directory private/UI` para contar somente os nomes conhecidos e conferir assinaturas JPEG mínimas. Não apontar para unidade do instrumento. Assinatura JPEG não comprova conteúdo, direitos ou compatibilidade com o decodificador.

O relatório atual marca `installable_ready: false` e `firmware_generated: false`. Seus impedimentos incluem implementação embarcada ausente, integridade/formato de atualização não verificados, hardware não confirmado, recuperação não demonstrada, validação independente ausente e recursos UI incompletos. Nenhum dos bloqueios pode ser removido apenas marcando uma opção de linha de comando.

Sete testes novos cobrem fingerprint desconhecido, caminhos/terminadores/duplicatas, rejeição de travessia, inventário seletivo sem alteração, HTML com extensão JPEG e retorno de impedimento sem gerar arquivos. Total local: **34/34 testes Python** com os três privados habilitados; CI padrão executa 31 e ignora três privados. Os componentes Node/navegador anteriores foram mantidos, sem alterações nesta fase.

## Insumos necessários antes de entregar um instalável

1. Pacote legítimo de recursos UI compatível com a revisão e confirmação de direitos para o uso/distribuição pretendidos.
2. Identificação confiável da revisão e compatibilidade da amostra V1.4 com o aparelho V1.3 observado.
3. Procedimento de recuperação/restauração tecnicamente demonstrado, por documentação oficial ou investigação independente, sem executá-lo nesta fase.
4. Contrato de atualização/integridade e mapa de memória completos; depois, implementação e testes de interface/idioma em ambiente apropriado.
5. Revisão independente e validação das funcionalidades/avisos antes de classificar uma imagem como pronta para instalação. Testes offline não certificam o instrumento.

Documentação/pacotes legítimos do fabricante seriam insumos úteis, mas não condicionam a continuidade. O caminho ativo é emulação, testes diferenciais e código autoral. A caracterização de recursos pode usar investigação independente e substitutos autorais de teste, sem publicar ativos proprietários. O rascunho de solicitação ao fabricante continua opcional; nenhuma mensagem foi enviada.
