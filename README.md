# power_pnl

**power_pnl** é um framework completo para modelagem, simulação e resolução simbólica de problemas não lineares restritos na área de sistemas elétricos de potência. Ele oferece suporte à construção de modelos com geração térmica, hidráulica, cargas, transformadores, linhas, elementos reativos, e mais — com uma arquitetura extensível, verificação simbólica das condições KKT, e suporte a resolução com métodos de Newton simbólico.

---

## 📁 Estrutura do Projeto

```bash
power_pnl/
├── data/
│   └── base_dados.json
├── eletricmodels/
│   ├── electric_elements/
│   │   ├── capacitor.py
│   │   ├── factory.py
│   │   ├── interfaces.py
│   │   └── reactor.py
│   ├── generation/
│   │   ├── thermal/
│   │   │   ├── biomass_generator.py
│   │   │   ├── coal_generator.py
│   │   │   ├── combined_generator.py
│   │   │   ├── diesel_generator.py
│   │   │   ├── gas_generator.py
│   │   │   ├── nuclear_generator.py
│   │   │   └── oil_generator.py
│   │   ├── base_generator.py
│   │   ├── ficticious_generator.py
│   │   ├── generator_factory.py
│   │   ├── hydro_generator.py
│   │   ├── thermal_generator.py
│   │   └── wind_generator.py
│   ├── hydro/
│   │   ├── hydro_plant.py
│   │   └── hydro_system.py
│   ├── power/
│   │   ├── bus.py
│   │   ├── deficit.py
│   │   ├── line.py
│   │   ├── load.py
│   │   └── power_system.py
│   ├── system/
│   │   └── full_system.py
│   ├── transformers/
│   │   ├── dual_transformer.py
│   │   ├── phase_transformer.py
│   │   ├── tap_transformer.py
│   │   ├── transformer.py
│   │   └── transformer_factor.py
│   └── reability_mixin.py
├── power_pnl/
│   ├── engine/
│   │   ├── convexity.py
│   │   ├── derivatives.py
│   │   └── lagrangian.py
│   ├── interface/
│   │   ├── model.py
│   │   └── objetivo.py
│   ├── models/
│   │   ├── constraints.py
│   │   ├── objective.py
│   │   └── variables.py
│   ├── solver/
│   │   └── solver.py
│   ├── symbolic/
│   │   ├── chute_inicial.py
│   │   ├── karush_kunh_tucker.py
│   │   └── model_builder.py
├── reader/
│   ├── loader.py
```

---

## 🚀 Instalação

Este projeto utiliza o [Poetry](https://python-poetry.org/) para gerenciamento de dependências.

```bash
# Clonar o repositório
git clone https://github.com/gsjunqueira/power_pnl.git
cd power_pnl

# Instalar com poetry
poetry install
```

---

## 📌 Funcionalidades

- Modelagem extensível de sistemas elétricos de potência
- Suporte simbólico para restrições e variáveis
- Construção da Lagrangeana
- Resolução com Newton simbólico
- Análise das condições KKT

---

## 📜 Licença

Este projeto está licenciado sob os termos da licença MIT.

---

## 👨‍💻 Autor

Desenvolvido por **Giovani Santiago Junqueira**
Mestrando em Engenharia Elétrica – Sistemas de Potência
Universidade Federal de Juiz de Fora
