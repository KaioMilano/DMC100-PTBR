# DMC100-PTBR 🇧🇷

Projeto comunitário e **não oficial** para pesquisar a tradução da interface do multímetro/alicate amperímetro **FNIRSI DMC-100** para português do Brasil.

> **STATUS: PESQUISA / PRÉ-ALFA. NÃO EXISTE FIRMWARE PT-BR VALIDADO PARA INSTALAÇÃO.** Não grave modificações experimentais em aparelhos usados para medições elétricas. Este repositório contém somente ferramentas de análise estática e documentação.

## Objetivos

- Catalogar os textos e menus das versões de firmware do DMC-100.
- Traduzir mensagens e avisos, preservando a terminologia elétrica e as unidades.
- Investigar fontes, imagens da interface e limites de armazenamento dos textos.
- Criar verificadores de firmware **somente leitura**, com testes automatizados.
- Exigir validação independente e testes de segurança antes de qualquer possível firmware instalável.

Equipamento de referência: **DMC-100 V1.3**. Há um arquivo V1.4 divulgado por canais de distribuição, porém ainda não foi analisado diretamente neste projeto.

## Estado

| Etapa | Situação |
|---|---|
| Estudo e fontes | Iniciado |
| Catálogo PT-BR | Rascunho |
| Inspeção estática com testes | Disponível |
| Validar offsets no arquivo original | Pendente |
| Mapear JPEGs/fontes | Pendente |
| Protótipo offline | Pendente |
| Testes metrológicos e revisão independente | Pendente |
| Firmware instalável | **Indisponível** |

## Executar o verificador local

Use **somente uma cópia obtida legitimamente** do firmware; não publique o arquivo nem inclua backups do aparelho no Git.

```bash
python -m src.dmc100_ptbr.inspect caminho/para/APP_DMC-100_V1.4_250524.bin
python -m src.dmc100_ptbr.inspect caminho/para/APP_DMC-100_V1.4_250524.bin --json
python -m unittest discover -s tests -v
```

O programa apenas lê o arquivo, calcula SHA-256, confere o tamanho e compara textos com offsets relatados pela comunidade, **ainda não validados**. Coincidências não atestam autenticidade, segurança ou compatibilidade.

## Documentação

- [Estudo técnico](docs/ESTUDO_TECNICO_INICIAL.md)
- [Roteiro de desenvolvimento](docs/ROADMAP.md)
- [Traduções preliminares](docs/TRADUCOES.md)
- [Segurança técnica](docs/SEGURANCA.md)
- [Fontes e créditos](docs/FONTES.md)
- [Como contribuir](CONTRIBUTING.md)
- [Apoio voluntário](APOIE.md)

## Apoio voluntário

Quando houver canal de recebimento definido, interessados poderão contribuir opcionalmente com **R$ 5** para manutenção e testes. Não é compra, taxa de acesso ou garantia de entrega. Não há arrecadação ativa. O código e a documentação autoral permanecerão acessíveis sem pagamento.

## Direitos e independência

Sem vínculo com a FNIRSI. Marcas FNIRSI e DMC-100 pertencem aos titulares. A licença MIT vale **apenas para código e documentação autorais aqui publicados**, não para firmware, imagens, documentação ou outros ativos de terceiros. Não redistribuímos binários proprietários ou derivados sem a autorização necessária.

**Leia [SECURITY.md](SECURITY.md) antes de contribuir com alterações técnicas.**
