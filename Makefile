PYTHON ?= python3
.DEFAULT_GOAL := help

.PHONY: help doctor model test test-model-artifact test-portable test-ai test-android-tools test-robotics test-qa test-robot test-quick vision-smoke compose-config status logs simulation-up simulation-down simulation-logs demo demo-route demo-client gazebo gazebo-up demo-visual rviz

help:
	@printf '%s\n' \
		'Maestro Agrícola - comandos principais' \
		'  make doctor      verifica o ambiente antes do simulador' \
		'  make test        executa testes portáteis, sem Docker/ROS no host' \
		'  make test-portable  executa todas as suítes Python em tests/portable' \
		'  make test-ai     executa somente os testes portáteis de IA' \
		'  make test-quick  executa testes e valida a configuração Compose' \
		'  make vision-smoke  verifica o QR plot-03 em imagem estática' \
		'  make demo        TESTE PRINCIPAL: verifica protocolo, Nav2 e movimento' \
		'  make demo-route  testa três plots + dock em modo headless NVIDIA' \
		'  make gazebo      abre uma simulação limpa no Gazebo usando a NVIDIA' \
		'  make demo-visual envia e verifica o comando com o Gazebo já aberto' \
		'  make rviz        abre mapa, robô, LiDAR e trajetórias no mesmo contêiner' \
		'  make status      mostra se o contêiner está ativo' \
		'  make logs        diagnóstico: mostra apenas os logs recentes' \
		'  make simulation-down  encerra e remove o contêiner'

doctor:
	$(PYTHON) tools/doctor.py

model:
	$(PYTHON) tools/train_intent_model.py

test: test-model-artifact test-portable test-robot

test-model-artifact:
	$(PYTHON) tools/train_intent_model.py --check

test-portable:
	$(PYTHON) -m unittest discover -s tests/portable -t . -p 'test_*.py'

test-ai:
	$(PYTHON) -m unittest discover -s tests/portable/ai -t . -p 'test_*.py'

test-android-tools:
	$(PYTHON) -m unittest discover -s tests/portable/android -t . -p 'test_*.py'

test-robotics:
	$(PYTHON) -m unittest discover -s tests/portable/robotics -t . -p 'test_*.py'

test-qa:
	$(PYTHON) -m unittest discover -s tests/portable/qa -t . -p 'test_*.py'

test-robot:
	PYTHONPATH=robot_ws/src/maestro_robot_bridge $(PYTHON) -m unittest discover -s robot_ws/src/maestro_robot_bridge/test -p 'test_*.py'

vision-smoke:
	@for plot in plot-01 plot-02 plot-03; do \
		$(PYTHON) tools/qr_target_detector.py \
			robot_ws/src/maestro_simulation/models/plot_marker/materials/textures/$$plot.png || exit; \
	done

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
	docker compose --profile visual --profile gpu down
	@command -v xhost >/dev/null && xhost -SI:localuser:root >/dev/null 2>&1 || true
	@printf '%s\n' 'SIMULAÇÃO ENCERRADA: o contêiner foi removido.'

simulation-logs:
	docker compose logs -f simulation

demo: doctor simulation-up
	$(PYTHON) tools/mock_glasses_client.py --wait-seconds 120
	$(PYTHON) -u tools/check_simulation.py --cycle-timeout 360 --expected-target plot-03
	@printf '\n%s\n%s\n%s\n' \
		'============================================================' \
		'DEMO APROVADA: undock, WebSocket, Nav2, movimento e dock verificados.' \
		'Para encerrar, execute: make simulation-down'

demo-route: doctor
	@command -v nvidia-smi >/dev/null || { echo 'Erro: driver NVIDIA não encontrado no host.'; exit 1; }
	@command -v xhost >/dev/null || { echo 'Erro: xhost não está instalado no host.'; exit 1; }
	@test -n "$$DISPLAY" || { echo 'Erro: nenhuma sessão gráfica X11 foi encontrada.'; exit 1; }
	@docker info --format '{{json .Runtimes}}' | grep -q 'nvidia' || { echo 'Erro: runtime NVIDIA não configurado no Docker.'; exit 1; }
	docker compose --profile visual --profile gpu down
	@xhost +SI:localuser:root >/dev/null
	docker compose --profile gpu up --build -d simulation-gpu
	$(PYTHON) tools/mock_glasses_client.py --wait-seconds 120 \
		--target plot-01 --target plot-02 --target plot-03
	MAESTRO_SIMULATION_SERVICE=simulation-gpu $(PYTHON) -u tools/check_simulation.py \
		--goal-timeout 180 --motion-timeout 120 --cycle-timeout 600 \
		--expected-target plot-01 --expected-target plot-02 --expected-target plot-03
	@printf '\n%s\n%s\n%s\n' \
		'============================================================' \
		'ROTA APROVADA: três plots visitados e retorno à doca confirmado.' \
		'Para encerrar, execute: make simulation-down'

demo-client:
	$(PYTHON) tools/mock_glasses_client.py --wait-seconds 10

gazebo: gazebo-up

gazebo-up:
	@command -v nvidia-smi >/dev/null || { echo 'Erro: driver NVIDIA não encontrado no host.'; exit 1; }
	@command -v xhost >/dev/null || { echo 'Erro: xhost não está instalado no host.'; exit 1; }
	@test -n "$$DISPLAY" || { echo 'Erro: nenhuma sessão gráfica X11 foi encontrada.'; exit 1; }
	@docker info --format '{{json .Runtimes}}' | grep -q 'nvidia' || { echo 'Erro: runtime NVIDIA não configurado no Docker.'; exit 1; }
	@docker compose --profile visual --profile gpu down --remove-orphans
	@xhost +SI:localuser:root >/dev/null
	@docker compose --profile visual up --build -d simulation-gui
	@printf '%s\n' \
		'GAZEBO ABERTO: ele roda dentro do contêiner com a GPU NVIDIA.' \
		'Quando o cenário carregar, execute: make demo-visual' \
		'Para encerrar e revogar o acesso X11: make simulation-down'

demo-visual: doctor
	@docker compose --profile visual ps --status running --services | grep -qx simulation-gui || { echo 'Erro: execute make gazebo primeiro.'; exit 1; }
	$(PYTHON) tools/mock_glasses_client.py --wait-seconds 120
	MAESTRO_SIMULATION_SERVICE=simulation-gui $(PYTHON) -u tools/check_simulation.py
	@printf '\n%s\n%s\n%s\n' \
		'============================================================' \
		'DEMO VISUAL APROVADA: NVIDIA, Gazebo, Nav2 e movimento verificados.' \
		'Para encerrar, execute: make simulation-down'

rviz:
	@docker compose --profile visual ps --status running --services | grep -qx simulation-gui || { echo 'Erro: execute make gazebo primeiro.'; exit 1; }
	docker compose --profile visual exec -T simulation-gui \
		bash -lc 'source /opt/ros/humble/setup.bash && \
			source /opt/maestro_ws/install/setup.bash && \
			rviz2 -d /opt/maestro_ws/install/maestro_simulation/share/maestro_simulation/config/maestro.rviz \
			--ros-args -r /tf:=/turtlebot1/tf -r /tf_static:=/turtlebot1/tf_static'
