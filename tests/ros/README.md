# Testes ROS e bridge

Os testes do bridge permanecem em
`robot_ws/src/maestro_robot_bridge/test`, junto ao pacote ROS que validam. Isso
preserva a descoberta pelo ecossistema ament/colcon.

O gate portátil pode ser executado no host:

```bash
PYTHONPATH=robot_ws/src/maestro_robot_bridge \
  python3 -m unittest discover \
  -s robot_ws/src/maestro_robot_bridge/test -p 'test_*.py'
```

Para uma mudança exclusiva de lifecycle, execute primeiro o teste focado
documentado no `AGENTS.md`:

```bash
python3 -m pytest \
  robot_ws/src/maestro_robot_bridge/test/test_mission_cycle.py -q
```

Simulação e E2E não devem ser usados como gate de toda mudança quando o teste
unitário focado é suficiente.
