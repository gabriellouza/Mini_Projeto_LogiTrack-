# Checklist de Validação Técnica — LogiTrack

Este checklist serve para validar se o repositório atende aos critérios da entrega e se a arquitetura está coerente com os RNFs.

## Estrutura do repositório

| Item | Status esperado |
|---|---|
| README.md na raiz | Obrigatório |
| Diagrama C4 em Mermaid no README | Obrigatório |
| `/docs/adrs/0001-estrategia-nuvem.md` | Obrigatório |
| `/docs/adrs/0002-padrao-resiliencia.md` | Obrigatório |
| `/docs/adrs/0003-modelo-comunicacao.md` | Obrigatório |
| `/docs/sad/sad-fase3.md` | Obrigatório |
| `/docs/diagrams` com diagramas extras | Recomendado |
| `/src` com protótipo executável | Recomendado |
| `.gitignore` | Obrigatório |

## Validação arquitetural

| Pergunta | Resposta esperada |
|---|---|
| A arquitetura responde ao problema de negócio? | Sim, reduz atrasos e melhora reação a eventos dinâmicos |
| Existe estratégia de nuvem? | Sim, PaaS com containers gerenciados |
| Existe estratégia de escalabilidade? | Sim, escala horizontal por serviço |
| Existe resiliência contra falha externa? | Sim, Circuit Breaker, fallback e cache |
| O modelo de comunicação foi justificado? | Sim, REST para fluxos imediatos e mensageria para eventos |
| Há trade-offs documentados? | Sim, nos três ADRs e no SAD |

## Teste local do protótipo

```bash
cd src
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Acessar:

```text
http://127.0.0.1:8000/docs
```
