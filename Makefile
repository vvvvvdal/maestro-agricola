PYTHON ?= python3
.DEFAULT_GOAL := help

.PHONY: help doctor model test test-model-artifact test-ai test-robot test-quick vision-smoke compose-config status logs simulation-up simulation-down simulation-logs demo demo-client gazebo-gui rviz

help:
	@printf '%s\n' \
		'Maestro Agrícola - comandos principais' \
		'  make doctor      verifica o ambiente antes do simulador' \
		'  make test        executa testes portáteis, sem Docker/ROS no host' \
		'  make test-quick  executa testes e valida a configuração Compose' \
		'  make vision-smoke  verifica o QR plot-03 em imagem estática' \
		'  make demo        TESTE PRINCIPAL: verifica protocolo, Nav2 e movimento' \
		'  make gazebo-gui  abre o mundo 3D de uma simulação já ativa' \
		'  make rviz        abre mapa, robô, LiDAR e trajetórias no RViz2' \
		'  make status      mostra se o contêiner está ativo' \
		'  make logs        diagnóstico: mostra apenas os logs recentes' \
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
	@printf '%s\n' 'SIMULAÇÃO ENCERRADA: o contêiner foi removido.'

simulation-logs:
	docker compose logs -f simulation

demo: doctor simulation-up
	$(PYTHON) tools/mock_glasses_client.py --wait-seconds 120
	$(PYTHON) -u tools/check_simulation.py
	@printf '\n%s\n%s\n%s\n' \
		'============================================================' \
		'DEMO APROVADA: WebSocket, Nav2 e movimento foram verificados.' \
		'Para encerrar, execute: make simulation-down'

demo-client:
	$(PYTHON) tools/mock_glasses_client.py --wait-seconds 10

gazebo-gui:
	@command -v ign >/dev/null || { echo 'Erro: Gazebo Ignition não está instalado no host.'; exit 1; }
	@test -n "$$DISPLAY" || { echo 'Erro: nenhuma sessão gráfica X11 foi encontrada.'; exit 1; }
	@docker compose ps --status running --services | grep -qx simulation || { echo 'Erro: execute make demo antes de abrir o Gazebo.'; exit 1; }
	env LIBGL_ALWAYS_SOFTWARE=1 QT_X11_NO_MITSHM=1 ign gazebo -g --force-version 6 --render-engine-gui ogre

rviz:
	@command -v xhost >/dev/null || { echo 'Erro: xhost não está instalado no host.'; exit 1; }
	@test -n "$$DISPLAY" || { echo 'Erro: nenhuma sessão gráfica X11 foi encontrada.'; exit 1; }
	@docker compose ps --status running --services | grep -qx simulation || { echo 'Erro: execute make demo antes de abrir o RViz2.'; exit 1; }
	@set -e; \
		xhost +SI:localuser:root >/dev/null; \
		trap 'xhost -SI:localuser:root >/dev/null' EXIT INT TERM; \
		docker compose run --rm --no-deps --no-TTY \
			-e MAESTRO_HEADLESS=0 \
			-e DISPLAY="$$DISPLAY" \
			-e QT_X11_NO_MITSHM=1 \
			-e LIBGL_ALWAYS_SOFTWARE=1 \
			-v /tmp/.X11-unix:/tmp/.X11-unix:rw \
			-v "$(CURDIR)/robot_ws/src/maestro_simulation/config/maestro.rviz:/tmp/maestro.rviz:ro" \
			simulation rviz2 -d /tmp/maestro.rviz \
			--ros-args -r /tf:=/turtlebot1/tf -r /tf_static:=/turtlebot1/tf_static
