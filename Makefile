PYTHON ?= python3
.DEFAULT_GOAL := help

.PHONY: help doctor model test test-model-artifact test-ai test-robot test-quick vision-smoke compose-config status logs simulation-up simulation-down simulation-logs demo demo-client

help:
	@printf '%s\n' \
		'Maestro Agrícola - comandos principais' \
		'  make doctor      verifica o ambiente antes do simulador' \
		'  make test        executa testes portáteis, sem Docker/ROS no host' \
		'  make test-quick  executa testes e valida a configuração Compose' \
		'  make vision-smoke  verifica o QR plot-03 em imagem estática' \
		'  make demo        inicia a simulação headless e envia um comando' \
		'  make status      mostra se o contêiner está ativo' \
		'  make logs        mostra os logs recentes' \
		'  make simulation-down  encerra e remove o contêiner'

doctor:
	$(PYTHON) tools/doctor.py

model:
	$(PYTHON) tools/train_intent_model.py

test: test-model-artifact test-ai test-robot

test-model-artifact:
	$(PYTHON) tools/train_intent_model.py --check

test-ai:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py'

test-robot:
	PYTHONPATH=robot_ws/src/maestro_robot_bridge $(PYTHON) -m unittest discover -s robot_ws/src/maestro_robot_bridge/test -p 'test_*.py'

vision-smoke:
	$(PYTHON) tools/qr_target_detector.py robot_ws/src/maestro_simulation/models/plot_marker/materials/textures/plot-03.png

compose-config:
	docker compose config --quiet

test-quick: test compose-config

status:
	docker compose ps

logs:
	docker compose logs --tail 120 simulation

simulation-up:
	docker compose up --build -d simulation

simulation-down:
	docker compose down

simulation-logs:
	docker compose logs -f simulation

demo: doctor simulation-up
	$(PYTHON) tools/mock_glasses_client.py --wait-seconds 120
	$(PYTHON) -u tools/check_simulation.py

demo-client:
	$(PYTHON) tools/mock_glasses_client.py --wait-seconds 10
