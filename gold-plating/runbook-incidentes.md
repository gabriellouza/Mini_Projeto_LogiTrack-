# Runbook de Incidentes — LogiTrack

## Incidente 1 — Provedor de mapas indisponível

### Sintomas

- Aumento de timeout no Map Provider Adapter.
- Métrica de fallback acima do normal.
- Circuit Breaker aberto por mais de um ciclo de recuperação.

### Ação imediata

1. Verificar se o fallback para OpenStreetMap está ativo.
2. Confirmar se o cache Redis está respondendo.
3. Validar se o problema está apenas no provedor primário.
4. Manter operação em modo degradado se houver rota recente em cache.
5. Registrar incidente e horário de início.

### Critério de normalização

- Circuit Breaker volta ao estado fechado.
- Taxa de erro do provedor primário retorna ao padrão.
- Percentual de fallback reduz para nível normal.

---

## Incidente 2 — Fila de GPS acumulada

### Sintomas

- Tamanho da fila aumenta continuamente.
- Workers processam menos eventos do que entram.
- Atualizações de rota chegam com atraso.

### Ação imediata

1. Aumentar réplicas dos Event Workers.
2. Verificar erros de processamento nos logs.
3. Confirmar se o banco está aceitando gravações.
4. Pausar eventos não críticos se necessário.

### Critério de normalização

- Fila volta a reduzir.
- Latência média de processamento retorna ao limite esperado.

---

## Incidente 3 — Latência acima de 3 segundos

### Sintomas

- Tempo de recálculo de rota passa do limite do RNF01.
- Usuários relatam demora na interface.
- Tracing mostra lentidão no Route Engine ou Map Adapter.

### Ação imediata

1. Verificar latência das APIs externas.
2. Conferir uso de CPU e memória do Route Engine.
3. Aumentar réplicas do Route Engine.
4. Validar se o Redis está respondendo com baixa latência.
5. Acionar fallback se a lentidão vier do provedor primário.

### Critério de normalização

- Tempo médio de recálculo volta para menos de 3 segundos.
