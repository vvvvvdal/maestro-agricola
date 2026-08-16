PYTHON ?= python3

.PHONY: model test test-ai test-robot compose-config simulation-up simulation-down simulation-logs demo demo-client

model:
	$(PYTHON) tools/train_intent_model.py

test: model test-ai test-robot

test-ai:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py'

test-robot:
	PYTHONPATH=robot_ws/src/maestro_robot_bridge $(PYTHON) -m unittest discover -s robot_ws/src/maestro_robot_bridge/test -p 'test_*.py'

compose-config:
	docker compose config --quiet

simulation-up:
	docker compose up --build -d simulation

simulation-down:
	docker compose down

simulation-logs:
	docker compose logs -f simulation

demo: simulation-up
	$(PYTHON) tools/mock_glasses_client.py --wait-seconds 120

demo-client:
	$(PYTHON) tools/mock_glasses_client.py --wait-seconds 10
