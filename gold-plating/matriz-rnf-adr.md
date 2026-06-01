# Matriz RNF → ADR → Evidência

| RNF | Descrição | ADR relacionado | Evidência |
|---|---|---|---|
| RNF01 | Recalcular rotas em até 3 segundos | ADR 0001, ADR 0002 | Route Engine escalável, cache Redis e timeout |
| RNF02 | Resiliência contra falhas externas | ADR 0002 | Circuit Breaker, fallback e modo degradado |
| RNF03 | Escalabilidade 10x | ADR 0001, ADR 0003 | Containers e workers com escala horizontal |
| RNF04 | Confiabilidade dos dados | ADR 0001 | PostgreSQL gerenciado com transações ACID |
| RNF05 | Manutenibilidade | ADR 0001 | Clean Architecture e dependência por interfaces |
| RNF06 | Observabilidade | ADR 0001, ADR 0002 | Logs, métricas, tracing e alertas |
| RNF07 | Segurança | ADR 0001 | API Gateway, HTTPS, secrets e least privilege |
