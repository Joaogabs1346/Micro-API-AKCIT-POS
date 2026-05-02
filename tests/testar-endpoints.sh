#!/usr/bin/env bash
# Script para testar manualmente os endpoints da Micro-API de Tarefas.
# Pré-requisito: API rodando em http://localhost:8000
#   docker compose up -d
#
# Uso:
#   chmod +x testar-endpoints.sh
#   ./testar-endpoints.sh

set -e

BASE="http://localhost:8000/api/v1"

echo "=========================================="
echo " 0. Health check"
echo "=========================================="
curl -i $BASE/health
echo -e "\n"

echo "=========================================="
echo " 1. Criar tarefa (POST)"
echo "=========================================="
curl -i -X POST $BASE/tasks -H "Content-Type: application/json" -d '{"title":"Estudar Docker Compose","description":"Ler a documentação oficial"}'
echo -e "\n"

echo "=========================================="
echo " 2. Criar tarefa com título vazio (deve dar 422)"
echo "=========================================="
curl -i -X POST $BASE/tasks -H "Content-Type: application/json" -d '{"title":""}'
echo -e "\n"

echo "=========================================="
echo " 3. Listar todas as tarefas (GET)"
echo "=========================================="
curl -s $BASE/tasks | jq
echo -e "\n"

echo "=========================================="
echo " 4. Listar filtrando por status=pending"
echo "=========================================="
curl -s "$BASE/tasks?status=pending" | jq
echo -e "\n"

echo "=========================================="
echo " 5. Buscar por ID (GET)"
echo "=========================================="
curl -i $BASE/tasks/1
echo -e "\n"

echo "=========================================="
echo " 6. Buscar ID inexistente (deve dar 404)"
echo "=========================================="
curl -i $BASE/tasks/9999
echo -e "\n"

echo "=========================================="
echo " 7. Atualizar tarefa (PUT)"
echo "=========================================="
curl -i -X PUT $BASE/tasks/1 -H "Content-Type: application/json" -d '{"title":"Título atualizado","status":"in_progress"}'
echo -e "\n"

echo "=========================================="
echo " 8. Concluir tarefa (PATCH /complete)"
echo "=========================================="
curl -i -X PATCH $BASE/tasks/1/complete
echo -e "\n"

echo "=========================================="
echo " 9. Remover tarefa (DELETE)"
echo "=========================================="
curl -i -X DELETE $BASE/tasks/1
echo -e "\n"

echo "=========================================="
echo " 10. Confirmar remoção (GET deve dar 404)"
echo "=========================================="
curl -i $BASE/tasks/1
echo -e "\n"

echo "=========================================="
echo " FLUXO E2E COMPLETO (criar -> ler -> atualizar -> concluir -> remover)"
echo "=========================================="

echo ">> Criando tarefa..."
ID=$(curl -s -X POST $BASE/tasks -H "Content-Type: application/json" -d '{"title":"Tarefa E2E","description":"Fluxo completo"}' | jq -r .id)
echo "Tarefa criada com ID=$ID"
echo

echo ">> Listando..."
curl -s $BASE/tasks | jq
echo

echo ">> Buscando ID=$ID..."
curl -s $BASE/tasks/$ID | jq
echo

echo ">> Atualizando para status=in_progress..."
curl -s -X PUT $BASE/tasks/$ID -H "Content-Type: application/json" -d '{"status":"in_progress"}' | jq
echo

echo ">> Marcando como concluída..."
curl -s -X PATCH $BASE/tasks/$ID/complete | jq
echo

echo ">> Removendo..."
curl -i -X DELETE $BASE/tasks/$ID
echo -e "\n"

echo "Fim dos testes."
