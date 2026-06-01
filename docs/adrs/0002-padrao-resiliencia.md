# ADR 0002 — Padrão de Resiliência

## Status

Aceita

## Data

2026.1 — Ciclo 3 / Fase 4

## Contexto

O LogiTrack depende de APIs externas para cálculo de rota, dados de tráfego, notificações e validação de despacho. O ponto mais sensível é a integração com provedores de mapas, pois uma falha nesse serviço pode impedir o recálculo dinâmico de rotas e afetar diretamente o SLA dos clientes.

No cenário de produção, falhas externas são esperadas. A arquitetura não pode assumir que Google Maps, OpenStreetMap, ERP ou serviço de SMS estarão sempre disponíveis. Também não pode insistir indefinidamente em chamadas com erro, pois isso geraria lentidão, consumo de recursos e falhas em cascata.

## Decisão

Adotar o padrão **Circuit Breaker** no Map Provider Adapter, combinado com **fallback**, **cache Redis**, **timeout curto**, **retry controlado** e **observabilidade**.

O fluxo de decisão será:

1. O Route Engine solicita cálculo de rota pela porta `IMapProvider`.
2. O Map Provider Adapter tenta consultar o provedor primário.
3. Se o provedor primário responder dentro do limite, a rota é retornada e salva no Redis.
4. Se ocorrer timeout ou excesso de falhas, o Circuit Breaker abre.
5. Com o circuito aberto, novas chamadas deixam de ir ao provedor instável por um período.
6. O adapter tenta o provedor secundário.
7. Se o provedor secundário também falhar, o sistema usa a última rota válida no cache.
8. A falha é registrada em logs, métricas e alertas.

## Padrões utilizados

| Padrão | Uso no LogiTrack |
|---|---|
| Circuit Breaker | Evita chamadas repetidas para provedor instável |
| Fallback | Alterna de Google Maps para OpenStreetMap |
| Cache | Usa rotas recentes quando provedores externos falham |
| Timeout | Impede que uma chamada externa bloqueie o fluxo |
| Retry controlado | Tenta novamente apenas em falhas transitórias |
| Observabilidade | Registra falhas, latência, uso de fallback e abertura do circuito |

## Alternativas consideradas

### Alternativa 1 — Apenas retry

A primeira alternativa seria repetir a chamada algumas vezes quando o provedor falhasse.

**Vantagens:**

- Implementação simples.
- Resolve falhas rápidas e temporárias.
- Pouco impacto no desenho da arquitetura.

**Motivos para rejeição:**

- Pode piorar a sobrecarga quando o provedor está indisponível.
- Aumenta latência do recálculo de rota.
- Não resolve falha prolongada.
- Pode causar efeito cascata na API e nos workers.

### Alternativa 2 — Apenas cache

A segunda alternativa seria manter rotas em cache e usar cache sempre que houvesse falha externa.

**Vantagens:**

- Resposta rápida.
- Baixo custo computacional.
- Ajuda no modo degradado.

**Motivos para rejeição:**

- Rotas antigas podem não refletir o trânsito atual.
- Não é suficiente para entregas novas sem rota calculada.
- Não identifica nem isola o provedor com problema.

### Alternativa 3 — Multi-região

A terceira alternativa seria implantar o sistema inteiro em múltiplas regiões.

**Vantagens:**

- Alta disponibilidade em caso de falha regional.
- Melhor continuidade do serviço.
- Adequada para operação nacional ou internacional.

**Motivos para rejeição:**

- Custo e complexidade altos para a fase atual.
- Exige replicação de dados, estratégia de consistência e roteamento global.
- Não resolve sozinho falha de API externa se todos os ambientes chamarem o mesmo provedor.

### Alternativa 4 — Bulkhead

A quarta alternativa seria isolar recursos por tipo de integração, evitando que uma falha de mapas consuma recursos de outros módulos.

**Vantagens:**

- Reduz impacto entre módulos.
- Ajuda em cenários de alta carga.
- Complementa bem microsserviços.

**Motivos para não ser a decisão principal:**

- É útil, mas não ataca diretamente a dependência crítica de mapas.
- Será considerado como evolução futura para separar pools de conexão e filas por tipo de evento.

## Justificativa teórica

Nygard defende que sistemas de produção precisam ser projetados para falhas reais, não apenas para o caminho feliz. O Circuit Breaker é adequado porque reconhece que chamadas externas podem falhar e impede que o sistema continue insistindo em uma dependência indisponível.

Newman reforça que microsserviços precisam tolerar falhas parciais, pois um serviço distribuído raramente falha por completo; normalmente apenas uma dependência ou integração fica instável. Por isso, a arquitetura deve degradar de forma controlada.

A decisão também está alinhada com Pressman e Maxim, pois transforma requisitos não funcionais em mecanismos concretos de projeto. A resiliência deixa de ser uma intenção genérica e passa a existir como decisão arquitetural verificável.

## Trade-offs aceitos

| Ponto | Benefício | Custo / Risco |
|---|---|---|
| Circuit Breaker | Evita falha em cascata | Exige calibrar limites de falha e tempo de recuperação |
| Fallback | Mantém operação ativa | Pode usar provedor com precisão diferente |
| Cache Redis | Reduz latência e apoia modo degradado | Pode retornar rota menos atualizada |
| Retry controlado | Resolve falhas transitórias | Pode aumentar latência se configurado errado |
| Observabilidade | Facilita diagnóstico | Exige instrumentação e alertas |

## Consequências

### Consequências positivas

- Falha no Google Maps não derruba o recálculo de rotas.
- O sistema consegue operar em modo degradado.
- A latência fica mais previsível em momentos de instabilidade.
- A equipe consegue medir quantas vezes o fallback foi usado.
- A arquitetura atende melhor o RNF02 de resiliência.

### Consequências negativas

- A implementação fica mais complexa do que uma chamada HTTP simples.
- O Redis passa a ser componente crítico para modo degradado.
- É necessário definir política de expiração das rotas em cache.
- O time precisa monitorar falso positivo de abertura do circuito.

## Mapeamento com os RNFs

| RNF | Como a decisão atende |
|---|---|
| RNF01 | Timeout e cache reduzem tempo de resposta em falhas externas |
| RNF02 | Circuit Breaker, fallback e cache mantêm operação disponível |
| RNF03 | Adapter isolado pode escalar separado em alto volume |
| RNF04 | Evita perda de estado ao persistir resultado válido no banco e no cache |
| RNF05 | Mantém a resiliência na infraestrutura, sem acoplar domínio ao provedor |

## Decisão final

A equipe adotará **Circuit Breaker como padrão principal de resiliência**, complementado por fallback entre provedores, cache Redis, timeout, retry controlado e métricas de observabilidade. Essa decisão reduz o risco operacional mais crítico do LogiTrack: a dependência de APIs externas de mapas.

## Referências

- NYGARD, Michael T. *Release It!: Design and Deploy Production-Ready Software*. Pragmatic Bookshelf, 2018.
- NEWMAN, Sam. *Building Microservices*. O'Reilly Media, 2021.
- PRESSMAN, Roger S.; MAXIM, Bruce R. *Engenharia de Software: Uma Abordagem Profissional*. McGraw-Hill, 2021.
- MARTIN, Robert C. *Clean Architecture*. Prentice Hall, 2017.
