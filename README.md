# 1CCPO-Equipe02-S4-CS

## Equipe

| Integrante                 | RM       |
|----------------------------|----------|
| João Victor Canello Ferian | RM573295 |
| Gustavo Melo dos Santos    | RM573562 |
| João Pedro Costenari Silva | RM572260 |
| Lucas Klein                | RM570029 |

**Vídeo de demonstração:** 

# Estação de recarga inteligente para veículos elétricos comerciais

Protótipo simulado (Python) da **Sprint 04 – Computer Science**, Turma 1CCPO, Grupo 02.

## 1. Problema

Frotas de veículos elétricos comerciais precisam recarregar vários veículos ao mesmo tempo, mas a estação tem um limite de potência contratada. Ultrapassar esse limite gera risco de sobrecarga; além disso, só usuários autorizados devem iniciar uma recarga.

## 2. Solução proposta

Uma estação com teto de **100 kW** recebe vários veículos ao mesmo tempo. O sistema só inicia a recarga para quem passa no login e distribui a potência sem nunca ultrapassar o teto, dando prioridade ao veículo com menor nível de bateria.

## 3. Protótipo: entradas, decisões e saídas

| Papel    | No protótipo (`src/carregador.py`)                                                  |
|----------|-------------------------------------------------------------------------------------|
| Entradas | e-mail, senha, identificação do veículo, nível de bateria (SoC), ordem de chegada   |
| Decisões | `autenticar()` (login) e `q_simplificada()` / `alocar()` (decisão de potência Q)    |
| Saídas   | "Login autorizado" / "Acesso negado" e potência (kW) entregue a cada veículo        |

O protótipo integra duas lógicas booleanas validadas nas sprints anteriores:

| Bloco    | Lógica                                                                       | Sprint  |
|----------|------------------------------------------------------------------------------|---------|
| Login    | `Login = (Email ⊙ EmailCorreto) · (Senha ⊙ SenhaCorreta)` (AND de dois XNOR) | 01 e 02 |
| Potência | `Q = S · (¬T + M + ¬F)`, equivalente a Σm(8, 9, 10, 11, 12, 14, 15)          | 03      |

Variáveis da decisão de potência:

| Variável | Vale 1 quando                                      | Cálculo no código                                |
|----------|----------------------------------------------------|--------------------------------------------------|
| S        | há ao menos uma sessão ativa                       | veículos ≥ 1                                     |
| T        | o teto de 100 kW foi atingido                      | veículos × 50 kW ≥ 100 kW                        |
| M        | a sessão é a de menor bateria                      | menor SoC; no empate, vence quem chegou primeiro |
| F        | a fatia calculada é menor que o máximo do conector | 100 kW ÷ veículos < 50 kW                        |

`Q = 1`: a sessão recebe a potência nominal (50 kW). `Q = 0`: recebe uma fatia igual do que sobra do teto (`(100 − nº de sessões com Q=1 × 50) ÷ nº de sessões com Q=0`).

> Observação: F = 1 só ocorre com 3 ou mais veículos, e nesse caso T também vale 1. As combinações com T = 0 e F = 1 não ocorrem na prática (condições "don't care").

> Premissa: o conector de 50 kW não consta nas sprints anteriores. Ele é a constante `CONECTOR_KW` em `src/carregador.py`.

## 4. Como rodar

Requer Python 3.8 ou superior, sem dependências externas.

```
# modo interativo (login, conectar/desconectar veículos, ver potência)
python src/carregador.py

# plano de testes (11 testes)
python tests/testes.py

# reproduz a 1ª versão, sem desempate (testes 10 e 11 falham)
python tests/testes.py --sem-desempate
```

Credenciais de demonstração: e-mail `admin@email.com`, senha `1234`.

## 5. Demonstração de funcionamento

| Situação                      | Como demonstrar                                                   | Teste(s)   |
|-------------------------------|-------------------------------------------------------------------|------------|
| Funcionamento normal          | login válido e 1 veículo conectado: 50 kW                         | 01 e 03    |
| Decisão a partir das entradas | 3 veículos (60%, 15%, 40%): o de 15% recebe 50 kW, os outros 25 kW | 04 e 05    |
| Operação impedida             | senha incorreta: acesso negado, nenhuma sessão criada             | 02         |
| Exceção ou falha              | empate de bateria na v1: 150 kW (falha); na v2: 100 kW (corrigido) | 06, 07, 10, 11 |

## 6. Plano de testes e resultados (versão corrigida, v2)

| Teste | Situação e entradas | Resultado esperado | Resultado obtido | Status |
|-------|---------------------|--------------------|------------------|--------|
| 01 | Login válido: admin@email.com / 1234 | Login autorizado | Login autorizado | OK |
| 02 | Senha incorreta (0000), veículo CAM-01 (30%) | Acesso negado; nenhuma sessão criada | Acesso negado; sessões ativas = 0 | OK |
| 03 | 1 veículo: CAM-01 com 30% | S=1 T=0 F=0 → Q=1; 50 kW | S=1 T=0 F=0 → Q=1; 50 kW | OK |
| 04 | 2 veículos: CAM-01 20%, CAM-02 70% | Q=1 para ambos; 50 kW cada (total 100 kW) | CAM-01: Q=1 50 kW; CAM-02: Q=1 50 kW | OK |
| 05 | 3 veículos: CAM-01 60%, CAM-02 15%, CAM-03 40% | CAM-02: Q=1, 50 kW; CAM-01 e CAM-03: Q=0, 25 kW cada; total 100 kW | CAM-01: 25 kW; CAM-02: 50 kW; CAM-03: 25 kW | OK |
| 06 | Nenhum veículo conectado (S=0) | Q=0; 0 kW entregues | sessões=0; Q(S=0)=0; total=0.0 kW | OK |
| 07 | (a) e-mail e senha vazios; (b) login válido com SoC=150% | (a) acesso negado; (b) rejeitado; nenhuma sessão criada | (a) Acesso negado; (b) Nível de bateria inválido; sessões=0 | OK |
| 08 | Tabela verdade do login (4 combinações) | saída = 0,0,0,1 | saída = 0,0,0,1 | OK |
| 09 | Q original × Q simplificada (16 combinações) | 0 divergências | 0 divergências em 16 | OK |
| 10 | Empate no menor SoC: CAM-01, 02 e 03 com 20%, CAM-04 com 80% | total ≤ 100 kW (apenas 1 veículo prioritário) | total = 100.0 kW; veículos com M=1: 1 | OK |
| 11 | 0 a 6 veículos, SoC em {10, 50, 90}% (todas as combinações) | 0 violações do teto | 0 violações em 1093 cenários | OK |

## 7. Evidências

Saídas reais dos testes, geradas por `tests/testes.py`:

| Arquivo | Conteúdo | Testes |
|---------|----------|--------|
| [`docs/evidencias/saida_testes_v1.txt`](docs/evidencias/saida_testes_v1.txt) | 1ª versão, sem desempate: 9/11 OK | 01 a 11 (falhas nos testes 10 e 11) |
| [`docs/evidencias/saida_testes_v2.txt`](docs/evidencias/saida_testes_v2.txt) | versão corrigida: 11/11 OK | 01 a 11 |

Cada bloco `[Teste NN]` dentro dos arquivos mostra entradas, esperado, obtido e status do teste correspondente.

## 8. Análise dos resultados

Na 1ª versão, 9 de 11 testes passaram. Os testes 10 e 11 falharam.

| Teste | Comportamento observado | Possível causa | Correção proposta |
|-------|-------------------------|----------------|-------------------|
| 10 | 3 veículos com 20% receberam M=1 e 50 kW cada; total entregue = **150 kW** (esperado ≤ 100 kW) | Com empate no menor nível de bateria, a condição `soc == menor` marcava várias sessões como prioritárias | Desempate pela ordem de chegada: só a primeira sessão com o menor SoC recebe M=1 |
| 11 | **362 violações do teto em 1.093 cenários** | Mesma causa: os empates (comuns com SoC em {10, 50, 90}%) geravam mais de uma sessão com Q=1 | A mesma correção |

Após a correção: teste 10 com total de 100,0 kW e apenas 1 veículo com M=1; teste 11 com 0 violações em 1.093 cenários; plano completo com 11/11 OK.

## 9. Solução final

A estação resolve o problema com duas decisões simples e verificáveis: o login (AND de dois XNOR) e a decisão de potência Q por sessão.

- **Segura:** o teto de 100 kW nunca foi ultrapassado após a correção (teste 11: 0 violações em 1.093 cenários), e o acesso é bloqueado com credenciais incorretas ou vazias (testes 02 e 07).
- **Inteligente:** quando a demanda excede o teto, o veículo com menor bateria recebe a potência nominal e os demais dividem o restante (teste 05).
- **Eficiente:** com 3 ou mais veículos, a potência da estação é totalmente distribuída (100 kW nos testes 05 e 10), sem desperdício e sem excesso.
- **Confiável como lógica:** o login e o Q simplificado foram validados contra as tabelas verdade (testes 08 e 09), e o processo de teste encontrou e corrigiu uma falha real (testes 10 e 11).

## 10. Estrutura

```
src/carregador.py              protótipo: login, decisão Q, alocação e modo interativo
tests/testes.py                plano de testes com saída no formato Esperado/Obtido/Status
docs/evidencias/               saídas reais dos testes (v1 com 2 falhas, v2 corrigida)
```

## 11. Limitações

Simulação sem medição em carregador real; a potência de 50 kW por conector é uma premissa; o nível de bateria não é recalculado ao longo do tempo.
