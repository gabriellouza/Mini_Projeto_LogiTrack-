LogiTrack — Sistema de Otimização Dinâmica de Rotas

Sistema para otimização e recálculo dinâmico de rotas de entrega em tempo real, baseado em eventos operacionais como trânsito, telemetria GPS e mudanças logísticas.

Visão Geral

O LogiTrack resolve um problema crítico de operações logísticas:
rotas planejadas de forma estática não refletem a realidade dinâmica do dia, gerando atrasos, quebra de SLA e prejuízo financeiro.

A solução implementa:

processamento em tempo real de eventos
recálculo automático de rotas
integração com múltiplos provedores externos
fallback e operação em modo degradado

Conforme definido no projeto, o sistema transforma um processo reativo em proativo e orientado a eventos

Arquitetura (C4 Model)
Nível 1 — Contexto

O sistema atua como núcleo central integrando usuários e sistemas externos:

Operador Logístico → gerencia rotas
Motorista → executa entregas e atualiza status
Cliente Corporativo → recebe notificações de SLA
GPS → envia telemetria
Google Maps / OSM → cálculo de rotas
ERP → valida despacho
Notificação → envio de alertas
Nível 2 — Containers

A arquitetura é baseada em containers independentes, com separação clara de responsabilidades:

Container	Tecnologia	Responsabilidade
Web App	React / TypeScript	Interface para operadores
API Backend	Node.js / Express	Orquestra regras e expõe REST
Route Engine	Python / FastAPI	Núcleo de cálculo de rotas
Map Provider Adapter	Python	Integração com APIs de mapas + fallback
Route Cache	Redis	Cache para operação degradada
Database	PostgreSQL	Persistência transacional
Message Broker	RabbitMQ	Processamento de eventos

Essa separação permite escalabilidade e isolamento do domínio

Fluxo Principal do Sistema
GPS envia posição dos veículos → Message Broker
Broker envia eventos → API Backend
API solicita recálculo → Route Engine
Route Engine consulta Map Adapter
Map Adapter:
usa Google Maps (primário)
fallback para OSM
usa cache Redis em falhas
Resultado retorna → API → Web App
Notificações são enviadas para motoristas e clientes
ERP valida despachos
Estilo Arquitetural

O sistema adota:

Clean Architecture + Containers
domínio isolado da infraestrutura
uso de interfaces (ex: IMapProvider)
inversão de dependência aplicada

Isso corrige o problema clássico de acoplamento do N-Tier tradicional

Requisitos Não Funcionais (RNFs)
RNF01 — Performance
recálculo de rota em até 3 segundos
RNF02 — Resiliência
fallback entre provedores de mapa
cache de rotas com Redis
RNF03 — Escalabilidade
suporte a crescimento de até 10x
escalabilidade horizontal por container
RNF04 — Confiabilidade
uso de transações ACID (PostgreSQL)
perda máxima de dados < 0,01%
RNF05 — Manutenibilidade
domínio não depende de infraestrutura
testabilidade total via interfaces
Decisão Arquitetural Principal (ADR-001)

Problema:
Dependência direta de APIs externas tornava o sistema frágil e não testável.

Solução:

uso de interface IMapProvider
implementação de múltiplos adaptadores:
Google Maps (primário)
OpenStreetMap (fallback)
uso de cache Redis
circuit breaker para falhas

Resultado:

sistema continua operando mesmo com falha externa
domínio totalmente isolado
alta testabilidade
Trade-offs Arquiteturais
Aspecto	Decisão
Complexidade	maior que N-Tier
Resiliência	alta
Testabilidade	alta
Escalabilidade	alta
Custo inicial	médio

A escolha prioriza resiliência e qualidade sobre simplicidade inicial.

Tecnologias Utilizadas
Frontend: React + TypeScript
Backend: Node.js + Express
Domínio: Python + FastAPI
Mensageria: RabbitMQ
Banco: PostgreSQL
Cache: Redis
Map APIs: Google Maps + OpenStreetMap
Estratégia de Resiliência
fallback automático entre provedores
cache de rotas recentes
circuit breaker
processamento assíncrono com broker

Sem essas estratégias, o sistema pararia completamente em caso de falha externa

Benefícios do Sistema
redução de atrasos e violação de SLA
resposta em tempo real a eventos
operação contínua mesmo com falhas externas
redução de custo logístico