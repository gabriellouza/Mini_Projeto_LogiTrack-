# ADR 0003 — Modelo de Comunicação

## Status

Aceita

## Data

2026.1 — Ciclo 3 / Fase 4

## Contexto

O LogiTrack possui fluxos com necessidades diferentes de comunicação. Algumas operações exigem resposta imediata, como consulta de rota, autenticação, abertura de entrega e recálculo solicitado pelo operador. Outras operações acontecem em grande volume e não precisam bloquear a resposta da API, como eventos de GPS, cancelamentos, atualizações de status e alertas de trânsito.

Usar apenas comunicação síncrona simplificaria o projeto, mas criaria risco de sobrecarga na API. Usar apenas comunicação assíncrona aumentaria complexidade e dificultaria fluxos que precisam de resposta imediata. Por isso, a arquitetura precisa combinar os dois modelos de forma consciente.

## Decisão

Adotar um modelo de comunicação **híbrido**:

- **Síncrono via HTTPS/REST** para operações de consulta, cadastro, autenticação, recálculo sob demanda e integração direta com o frontend.
- **Assíncrono via mensageria** para eventos de GPS, cancelamentos, atualização de status, alertas de SLA e processamento em lote operacional.

## Fluxos síncronos

| Fluxo | Comunicação | Justificativa |
|---|---|---|
| Login e autenticação | REST | Usuário precisa de resposta imediata |
| Consulta de rota | REST | Interface precisa exibir resultado no momento da solicitação |
| Recálculo manual pelo operador | REST | Operador espera retorno direto |
| Cadastro de entrega | REST | Precisa confirmar sucesso ou erro |
| Consulta de SLA | REST | Informação usada pela tela de monitoramento |

## Fluxos assíncronos

| Fluxo | Comunicação | Justificativa |
|---|---|---|
| Evento de GPS | Mensageria | Alto volume e chegada contínua |
| Cancelamento de entrega | Mensageria | Pode ser processado sem travar a API |
| Atualização de status | Mensageria | Pode ocorrer em segundo plano |
| Alerta de trânsito | Mensageria | Pode disparar recálculo por evento |
| Notificação de SLA | Mensageria | Não deve bloquear a operação principal |

## Alternativas consideradas

### Alternativa 1 — Comunicação totalmente síncrona

Todos os serviços se comunicariam por HTTP/REST.

**Vantagens:**

- Implementação inicial mais simples.
- Fluxo fácil de testar pelo Swagger.
- Menor curva de aprendizado para a equipe.

**Motivos para rejeição:**

- Eventos de GPS podem gerar alto volume de requisições.
- Um serviço lento pode bloquear outros serviços.
- A API pode ficar sobrecarregada em horário de pico.
- Menor tolerância a falhas temporárias.

### Alternativa 2 — Comunicação totalmente assíncrona

Todos os fluxos seriam baseados em eventos e filas.

**Vantagens:**

- Alto desacoplamento.
- Boa absorção de picos.
- Maior tolerância a falhas transitórias.

**Motivos para rejeição:**

- Complexidade maior para fluxos simples.
- Usuário pode não receber resposta imediata.
- Exige controle de idempotência, ordenação e rastreamento.
- Pode dificultar depuração para uma equipe pequena.

### Alternativa 3 — Comunicação híbrida

Combinar REST para fluxos de resposta imediata e mensageria para eventos.

**Vantagens:**

- Equilibra simplicidade e resiliência.
- Mantém boa experiência do usuário.
- Desacopla fluxos de alto volume.
- Permite evolução gradual para microsserviços.

**Motivo para aceitação:**

- É a opção que melhor atende os RNFs do LogiTrack sem aumentar demais a complexidade.

## Justificativa teórica

Newman explica que microsserviços precisam escolher cuidadosamente seus mecanismos de comunicação, pois chamadas síncronas aumentam acoplamento temporal, enquanto eventos assíncronos aumentam autonomia e tolerância a picos. No LogiTrack, isso é especialmente importante porque eventos de GPS são contínuos e podem chegar em grande volume.

Richards e Ford reforçam que toda decisão arquitetural envolve trade-offs. A decisão híbrida aceita mais complexidade do que um REST puro, mas evita o excesso de complexidade de um sistema totalmente event-driven.

Fowler também defende a separação entre operações de comando/consulta e fluxos de integração, o que ajuda a manter o sistema compreensível e evolutivo.

## Trade-offs aceitos

| Ponto | Benefício | Custo / Risco |
|---|---|---|
| REST para operações interativas | Simples e direto para o frontend | Pode criar acoplamento temporal |
| Mensageria para eventos | Absorve picos e desacopla serviços | Exige filas, consumidores e tratamento de falhas |
| Workers assíncronos | Processam GPS e cancelamentos sem travar API | Precisam de idempotência |
| Eventos de domínio | Facilitam evolução futura | Exigem padronização de payload |
| Modelo híbrido | Equilibra simplicidade e robustez | Exige documentação clara dos fluxos |

## Consequências

### Consequências positivas

- A API fica protegida contra picos de telemetria.
- O usuário mantém resposta rápida nas operações principais.
- Eventos podem ser reprocessados em caso de falha.
- O sistema fica mais preparado para escalar por serviço.
- O modelo facilita evolução para novos consumidores de eventos.

### Consequências negativas

- O sistema precisa controlar duplicidade de mensagens.
- Logs e tracing são necessários para rastrear fluxos assíncronos.
- A equipe precisa documentar contratos de eventos.
- A consistência pode ser eventual em alguns fluxos operacionais.

## Estratégias complementares

Para reduzir os riscos da comunicação assíncrona, serão aplicadas as seguintes práticas:

| Estratégia | Aplicação |
|---|---|
| Idempotência | Eventos repetidos de GPS não devem duplicar atualização |
| Dead Letter Queue | Mensagens com erro persistente serão isoladas para análise |
| Correlation ID | Cada fluxo terá identificador para rastreamento |
| Retry com limite | Falhas transitórias terão nova tentativa controlada |
| Contrato de evento | Payloads serão documentados e versionados |

## Mapeamento com os RNFs

| RNF | Como a decisão atende |
|---|---|
| RNF01 | REST mantém resposta rápida para operações interativas |
| RNF02 | Mensageria permite reprocessamento e tolerância a falhas temporárias |
| RNF03 | Workers e consumidores podem escalar horizontalmente |
| RNF04 | Eventos críticos terão idempotência e rastreamento |
| RNF05 | Serviços ficam menos acoplados e mais fáceis de alterar |

## Decisão final

A equipe adotará **comunicação híbrida**, usando REST para fluxos síncronos e mensageria para eventos operacionais. Essa decisão mantém a experiência do usuário simples e rápida, ao mesmo tempo em que prepara o LogiTrack para lidar com volume, falhas parciais e crescimento futuro.

## Referências

- NEWMAN, Sam. *Building Microservices*. O'Reilly Media, 2021.
- RICHARDS, Mark; FORD, Neal. *Fundamentals of Software Architecture*. O'Reilly Media, 2020.
- FOWLER, Martin. *Patterns of Enterprise Application Architecture*. Addison-Wesley, 2002.
- NYGARD, Michael T. *Release It!: Design and Deploy Production-Ready Software*. Pragmatic Bookshelf, 2018.
