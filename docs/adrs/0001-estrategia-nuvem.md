# ADR 0001 — Estratégia de Nuvem e Escalabilidade

## Status

Aceita

## Data

2026.1 — Ciclo 3 / Fase 4

## Contexto

O LogiTrack precisa recalcular rotas em tempo quase real, processar eventos de GPS, lidar com cancelamentos e manter comunicação com APIs externas de mapas. A arquitetura anterior já separava Web App, API Backend, Route Engine, Map Provider Adapter, Redis, PostgreSQL e RabbitMQ. Porém, para ambiente real de produção, ainda era necessário definir como essa arquitetura seria implantada em nuvem e como ela suportaria crescimento de carga sem refatoração estrutural.

O principal requisito de negócio é manter a operação logística funcionando mesmo com aumento de entregas e com instabilidade parcial de serviços externos. Os principais RNFs impactados são:

| RNF | Necessidade |
|---|---|
| RNF01 | Recalcular rotas em até 3 segundos |
| RNF02 | Continuar operando mesmo com falha em API externa |
| RNF03 | Suportar crescimento de até 10x no volume atual |
| RNF04 | Preservar consistência dos dados de despacho |
| RNF05 | Manter baixo acoplamento entre domínio e infraestrutura |

## Decisão

Adotar uma estratégia de **PaaS com containers gerenciados**, usando escalabilidade horizontal para os serviços de aplicação e serviços gerenciados para banco, cache, mensageria e observabilidade.

A implantação proposta é:

| Componente | Modelo de implantação | Justificativa |
|---|---|---|
| Web App | Hospedagem estática gerenciada | Baixo custo e deploy simples |
| API Gateway | Serviço gerenciado de gateway | Centraliza autenticação, rate limit e roteamento |
| API Backend | Container gerenciado | Escala conforme volume de chamadas REST |
| Route Engine | Container gerenciado | Escala separado da API em picos de cálculo |
| Event Worker | Container gerenciado | Consome eventos do broker de forma independente |
| PostgreSQL | Banco gerenciado | Alta disponibilidade, backup e transações ACID |
| Redis | Cache gerenciado | Baixa latência e suporte ao modo degradado |
| RabbitMQ/Broker | Serviço gerenciado de mensageria | Desacopla eventos de telemetria e cancelamento |
| Observabilidade | Serviço gerenciado de logs, métricas e tracing | Facilita investigação e melhoria contínua |

## Alternativas consideradas

### Alternativa 1 — IaaS com máquinas virtuais

A alternativa seria implantar todos os serviços em uma ou mais VMs, com Docker instalado manualmente.

**Vantagens:**

- Maior controle sobre sistema operacional, rede e configuração.
- Pode ser mais simples para um protótipo inicial.
- Custo previsível em cargas pequenas.

**Motivos para rejeição:**

- Exige mais responsabilidade operacional da equipe.
- Escalabilidade horizontal depende de configuração manual.
- Aumenta risco de falha concentrada em uma única VM.
- Não combina bem com a necessidade de crescimento gradual do LogiTrack.

### Alternativa 2 — SaaS completo

A alternativa seria usar uma plataforma pronta de roteirização como serviço e apenas integrar o sistema.

**Vantagens:**

- Menor esforço de desenvolvimento.
- Implantação inicial mais rápida.
- Menor necessidade de equipe técnica especializada.

**Motivos para rejeição:**

- Menor controle sobre regras de negócio logístico.
- Dependência forte de fornecedor externo.
- Dificuldade para aplicar regras específicas de SLA, fallback e priorização.
- Pode gerar custo alto por volume de entregas.

### Alternativa 3 — Serverless

A alternativa seria usar funções serverless para API, eventos e processamento de rotas.

**Vantagens:**

- Escala automática.
- Baixo custo quando há pouca utilização.
- Menor preocupação com servidores.

**Motivos para rejeição:**

- Pode gerar cold start em momentos críticos.
- Fluxos de recálculo podem ficar fragmentados em muitas funções.
- Observabilidade e rastreabilidade ficam mais complexas.
- Para processamento contínuo de eventos GPS, containers gerenciados oferecem mais previsibilidade.

### Alternativa 4 — Kubernetes completo

A alternativa seria implantar tudo em um cluster Kubernetes gerenciado.

**Vantagens:**

- Alto controle de escalabilidade, rede e deploy.
- Excelente para ambientes de grande porte.
- Facilita estratégias avançadas como canary e rolling update.

**Motivos para rejeição:**

- Complexidade operacional alta para o estágio atual do projeto.
- Exige conhecimento específico de cluster, ingress, service mesh e segurança.
- Pode gerar custo e esforço desnecessários para uma equipe pequena.

## Justificativa teórica

A decisão segue a ideia de Richards e Ford de que arquitetura envolve trade-offs, não respostas absolutas. Para o LogiTrack, o equilíbrio mais adequado é ganhar escalabilidade e resiliência sem assumir a complexidade operacional completa de Kubernetes ou IaaS.

A escolha também respeita a Regra de Dependência de Martin: os serviços de domínio continuam isolados da infraestrutura. A nuvem passa a hospedar e escalar os containers, mas não deve contaminar o núcleo de negócio com detalhes de provedores.

Pressman e Maxim destacam que requisitos de qualidade precisam orientar decisões de projeto. Neste caso, a estratégia de nuvem foi escolhida por atender diretamente performance, resiliência, escalabilidade, confiabilidade e manutenibilidade.

## Trade-offs aceitos

| Ponto | Benefício | Custo / Risco |
|---|---|---|
| PaaS com containers | Escalabilidade com menor esforço operacional | Menos controle que IaaS puro |
| Banco gerenciado | Backup, disponibilidade e manutenção simplificada | Custo maior que banco local em VM |
| Cache gerenciado | Baixa latência e apoio ao fallback | Mais um componente para monitorar |
| Broker gerenciado | Desacoplamento e absorção de picos | Exige desenho correto de filas e retentativas |
| Escala horizontal | Crescimento seletivo por serviço | Precisa de serviços stateless sempre que possível |

## Consequências

### Consequências positivas

- O Route Engine pode escalar sem escalar todo o sistema.
- A API Backend pode manter tempo de resposta menor mesmo com muitos eventos GPS.
- O banco gerenciado reduz risco de perda de dados críticos.
- A equipe evita administrar infraestrutura de baixo nível.
- O sistema fica mais preparado para crescimento gradual.

### Consequências negativas

- O custo mensal tende a ser maior que uma implantação simples em VM.
- A equipe precisa configurar observabilidade desde o início.
- Serviços distribuídos exigem cuidado com rede, autenticação interna e rastreamento.
- O projeto passa a depender parcialmente dos recursos do provedor cloud escolhido.

## Mapeamento com os RNFs

| RNF | Como a decisão atende |
|---|---|
| RNF01 | Containers independentes permitem escalar Route Engine e API conforme carga |
| RNF02 | Serviços gerenciados reduzem falhas operacionais e facilitam recuperação |
| RNF03 | Escala horizontal atende crescimento de até 10x |
| RNF04 | PostgreSQL gerenciado mantém transações críticas e backup |
| RNF05 | Infraestrutura continua fora do domínio, preservando Clean Architecture |

## Decisão final

A equipe adotará **PaaS com containers gerenciados**, banco PostgreSQL gerenciado, Redis gerenciado, broker gerenciado e observabilidade centralizada. Essa decisão entrega o melhor equilíbrio entre escalabilidade, custo, simplicidade operacional e aderência aos RNFs do LogiTrack.

## Referências

- MARTIN, Robert C. *Clean Architecture*. Prentice Hall, 2017.
- PRESSMAN, Roger S.; MAXIM, Bruce R. *Engenharia de Software: Uma Abordagem Profissional*. McGraw-Hill, 2021.
- RICHARDS, Mark; FORD, Neal. *Fundamentals of Software Architecture*. O'Reilly Media, 2020.
- NEWMAN, Sam. *Building Microservices*. O'Reilly Media, 2021.
