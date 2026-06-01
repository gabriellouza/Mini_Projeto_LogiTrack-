# Quality Gate Arquitetural

Este Quality Gate define critérios mínimos para aceitar evolução do LogiTrack.

| Critério | Regra |
|---|---|
| ADR obrigatório | Toda decisão estrutural precisa de ADR |
| Mermaid no README | Diagrama C4 deve continuar em sintaxe Mermaid |
| RNF rastreável | Cada RNF precisa estar ligado a uma decisão |
| Código executável | Protótipo deve rodar localmente sem depender de API externa real |
| Resiliência | Integrações externas devem ter timeout e fallback |
| Segurança | Nenhuma chave ou segredo pode ser versionado |
| Observabilidade | Fluxos críticos devem registrar erro e latência |
| Git | Commits devem ser claros e representar mudanças reais |

## Critérios para Pull Request

- README atualizado quando a arquitetura mudar.
- ADR novo ou alterado quando houver decisão relevante.
- Nenhum arquivo `.env`, chave ou senha versionado.
- Testes básicos do protótipo passando.
- Links internos do README funcionando.
