# Testes Python portáteis

Estas suítes não exigem Android, ROS 2 ou dispositivo físico. Os subdiretórios
são pacotes Python para permitir descoberta recursiva determinística.

```bash
# suíte completa
python3 -m unittest discover -s tests/portable -t . -p 'test_*.py'

# somente IA local e resolução determinística
python3 -m unittest discover -s tests/portable/ai -t . -p 'test_*.py'

# ferramentas Android executadas no host
python3 -m unittest discover -s tests/portable/android -t . -p 'test_*.py'

# robótica, simulação, visão e mocks
python3 -m unittest discover -s tests/portable/robotics -t . -p 'test_*.py'

# evidências e consistência de QA
python3 -m unittest discover -s tests/portable/qa -t . -p 'test_*.py'
```

As dependências aprovadas para o gate estão em `tools/requirements-dev.txt`.
Os casos de visão que exigem OpenCV/NumPy continuam opcionais quando essas
bibliotecas não estão disponíveis.
