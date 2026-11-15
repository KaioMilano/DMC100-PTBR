# Como contribuir

Contribuições são bem-vindas: traduções PT-BR, revisão de terminologia elétrica, testes automatizados, estudo de fonts e menus, documentação e relatórios de compatibilidade.

1. Abra uma issue descrevendo o problema e sua evidência.
2. Faça alterações pequenas, documentando a origem das informações.
3. Execute `python -m unittest discover -s tests -v`.
4. Envie pull request indicando se houve contato com hardware ou se foi análise estática.

**Não inclua** firmware original ou modificado, dumps, conteúdo proprietário de flash externa, números de série, backups, dados de calibração, senhas ou informações pessoais.

Nenhum patch deve alterar leituras, unidades, proteção, alertas, limites ou rotinas críticas. Qualquer mudança experimental fica bloqueada para instalação até validação independente.
