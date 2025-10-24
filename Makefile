.PHONY: help install install-dev test lint format type-check clean run build-docker run-docker setup pre-commit

# Variáveis
PYTHON := python
PIP := pip
VENV_NAME := .venv
VENV_ACTIVATE := $(VENV_NAME)/bin/activate

help: ## Mostra esta mensagem de ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Configura o ambiente de desenvolvimento completo
	$(PYTHON) -m venv $(VENV_NAME)
	. $(VENV_ACTIVATE) && $(PIP) install --upgrade pip
	. $(VENV_ACTIVATE) && $(PIP) install -e ".[dev]"
	. $(VENV_ACTIVATE) && pre-commit install
	@echo "Ambiente configurado! Execute 'source $(VENV_ACTIVATE)' para ativar."

install: ## Instala dependências de produção
	$(PIP) install -e .

install-dev: ## Instala dependências de desenvolvimento
	$(PIP) install -e ".[dev]"

test: ## Executa todos os testes
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

test-quick: ## Executa testes rápidos (sem coverage)
	pytest tests/ -v

lint: ## Executa linting com flake8
	flake8 src tests main.py --max-line-length=88 --extend-ignore=E203,W503

format: ## Formata código com black
	black src tests main.py --line-length=88

format-check: ## Verifica se código está formatado
	black src tests main.py --check --line-length=88

type-check: ## Executa verificação de tipos com mypy
	mypy src --ignore-missing-imports

quality: lint format-check type-check ## Executa todas as verificações de qualidade

pre-commit: ## Executa pre-commit em todos os arquivos
	pre-commit run --all-files

clean: ## Remove arquivos temporários e cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/ dist/ htmlcov/ .tox/ .cache/

run: ## Executa o jogo
	$(PYTHON) main.py

debug: ## Executa o jogo em modo debug
	$(PYTHON) -u main.py

build-docker: ## Constrói imagem Docker
	docker build -t 1942-clone .

run-docker: ## Executa jogo no Docker (requer X11 forwarding)
	docker run --rm -e DISPLAY=$(DISPLAY) -v /tmp/.X11-unix:/tmp/.X11-unix 1942-clone

# Comandos para CI/CD
ci-test: install-dev lint type-check test ## Pipeline completo de CI

# Comandos de release
version: ## Mostra versão atual
	$(PYTHON) -c "import src; print(src.__version__)" 2>/dev/null || echo "Versão não encontrada"

# Análise de código
complexity: ## Analisa complexidade do código
	@echo "Analisando complexidade..."
	@find src -name "*.py" -exec wc -l {} + | tail -1
	@echo "Arquivos Python encontrados:"
	@find src -name "*.py" | wc -l