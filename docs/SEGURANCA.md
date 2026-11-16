# Política de segurança técnica

O DMC-100 é um instrumento usado para medições elétricas. Erros de firmware podem afetar leituras, escalas, unidades e avisos. O projeto inclui análise, simulação visual e ensaios ARM virtuais. O mantenedor autorizou preparar candidato e primeiro teste físico em 16/11/2026; **ainda não há imagem pronta para gravar**. [Estado e preparação do teste real](PRIMEIRO_TESTE_REAL.md).

## Não fazer

- Não gravar firmware modificado no alicate usado em campo.
- Não testar firmware experimental em circuitos energizados, quadros ou rede doméstica.
- Não alterar calibração, lógica de medição, proteção, avisos, limites ou conversões.
- Não assumir que a tradução maior cabe no espaço reservado para a string.
- Não distribuir firmware original/derivado, dumps de recursos ou dados de calibração sem direitos necessários.
- Não usar o projeto de DOOM como evidência de que as medições funcionam após mudança.

## Pré-requisitos para um futuro experimento controlado

1. Identificar revisão de hardware, versão e proveniência do arquivo.
2. Registrar SHA-256 dos originais, preservados fora do Git.
3. Validar integridade, endereços, referências e eventual checksum.
4. Demonstrar recuperação do firmware por procedimento independente.
5. Revisar toda alteração byte a byte e registrar justificativa.
6. Submeter a revisão externa e testes em bancada isolada por profissional qualificado.
7. Comparar leituras com referências metrológicas, faixas e alertas.
8. Confirmar direitos de distribuição.

Testes de bancada **não certificam** categoria CAT, precisão ou segurança elétrica após alteração. Não vender nem recomendar firmware experimental para uso profissional.
