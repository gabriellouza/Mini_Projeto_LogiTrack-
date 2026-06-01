# Protótipo LogiTrack

Protótipo simples em FastAPI para demonstrar o fluxo arquitetural principal do LogiTrack.

## Executar localmente

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Acesse:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

| Método | Endpoint | Função |
|---|---|---|
| GET | `/health` | Verifica status da API |
| POST | `/routes/recalculate` | Recalcula rota simulada |
| GET | `/routes/{delivery_id}` | Consulta rota calculada |
| POST | `/events/gps` | Registra evento de GPS |
| GET | `/metrics` | Consulta métricas simples |
