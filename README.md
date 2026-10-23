# 1CCPO-Equipe02-S4-CS

## Equipe

| Integrante                 | RM       |
|----------------------------|----------|
| João Victor Canello Ferian | RM573295 |
| Gustavo Melo dos Santos    | RM573562 |
| João Pedro Costenari Silva | RM572260 |
| Lucas Klein                | RM570029 |

# Estação de recarga inteligente para veículos elétricos comerciais

Protótipo simulado (Python) da **Sprint 04 – Computer Science**, Turma 1CCPO, Grupo 02.

Uma estação com teto de **100 kW** recebe vários veículos comerciais ao mesmo tempo. O sistema só inicia a recarga para quem passa no login e distribui a potência sem nunca ultrapassar o teto, dando prioridade ao veículo com menor nível de bateria.

## Como funciona

O protótipo integra duas lógicas booleanas validadas nas sprints anteriores:

| Bloco | Lógica | Sprint |
| --- | --- | --- |
| Login | `Login = (Email ⊙ EmailCorreto) · (Senha ⊙ SenhaCorreta)` (AND de dois XNOR) | 01 e 02 |
| Potência | `Q = S · (¬T + M + ¬F)`, equivalente a Σm(8, 9, 10, 11, 12, 14, 15) | 03 |

Variáveis da decisão de potência:

| Variável | Vale 1 quando | Cálculo no código |
| --- | --- | --- |
| S | há ao menos uma sessão ativa | veículos ≥ 1 |
| T | o teto de 100 kW foi atingido | veículos × 50 kW ≥ 100 kW |
| M | a sessão é a de menor bateria | menor SoC; no empate, vence quem chegou primeiro |
| F | a fatia calculada é menor que o máximo do conector | 100 kW ÷ veículos < 50 kW |

`Q = 1`: a sessão recebe a potência nominal (50 kW). `Q = 0`: recebe uma fatia do que sobra do teto.

> Premissa: o conector de 50 kW não consta nas sprints anteriores. Ele é a constante `CONECTOR_KW` em `src/carregador.py`.

## Como rodar

Requer Python 3.8 ou superior, sem dependências externas.

```bash
# modo interativo (login, conectar/desconectar veículos, ver potência)
python src/carregador.py

# plano de testes (11 testes)
python tests/testes.py

# reproduz a 1ª versão, sem desempate (testes 10 e 11 falham)
python tests/testes.py --sem-desempate
```

Credenciais de demonstração: e-mail `admin@email.com`, senha `1234`.

## Estrutura

```
src/carregador.py              protótipo: login, decisão Q, alocação e modo interativo
tests/testes.py                plano de testes com saída no formato Esperado/Obtido/Status
docs/evidencias/               saídas reais dos testes (v1 com 2 falhas, v2 corrigida)
```

## Resultados dos testes

- 1ª versão: 9 de 11 testes OK. Os testes 10 e 11 falharam porque, com empate no menor nível de bateria, várias sessões recebiam prioridade e a estação passava de 100 kW (150 kW no teste 10; 362 violações em 1.093 cenários no teste 11).
- Versão corrigida (desempate pela ordem de chegada): 11 de 11 testes OK, 0 violações do teto.

## Limitações

Simulação sem medição em carregador real; a potência de 50 kW por conector é uma premissa; o nível de bateria não é recalculado ao longo do tempo.

## Integrantes

- Gustavo Melo dos Santos (RM573562)
- João Pedro Costenari Silva (RM572260)
- João Victor Canello Ferian (RM573295)
- Lucas Klein da Veiga (RM570029)
