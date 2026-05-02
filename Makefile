.PHONY: help install run test coverage docker-up docker-down docker-logs docker-test clean

help:
	@echo "Targets disponíveis:"
	@echo "  install        Instala todas as dependências (runtime + teste)"
	@echo "  run            Sobe a API local com uvicorn (--reload)"
	@echo "  test           Executa pytest"
	@echo "  coverage       Executa pytest com relatório de cobertura HTML em docs/cov_html/"
	@echo "  docker-up      Sobe API + Postgres via docker compose"
	@echo "  docker-down    Derruba os containers (mantém volume)"
	@echo "  docker-logs    Mostra logs do compose"
	@echo "  docker-test    Roda pytest dentro do container da API"
	@echo "  clean          Remove caches, *.pyc, *.db locais"

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload

test:
	pytest

coverage:
	pytest --cov=app --cov-report=html:docs/cov_html --cov-report=term

docker-up:
	docker compose up --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-test:
	docker compose run --rm api pytest

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	rm -f *.db .coverage
	rm -rf docs/cov_html htmlcov
