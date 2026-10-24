"""Plano de testes – Sprint 04.  Uso:  python testes.py [--sem-desempate]
A opção --sem-desempate reproduz a 1ª versão do protótipo (antes da correção dos Testes 10 e 11)."""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import carregador as c

DESEMPATE = "--sem-desempate" not in sys.argv
resultados = []


def registrar(num, titulo, entradas, esperado, obtido, ok, extra=None):
    status = "OK" if ok else "Falhou"
    resultados.append((num, status))
    print(f"[Teste {num:02d}] {titulo}")
    print(f"  Entradas : {entradas}")
    print(f"  Esperado : {esperado}")
    print(f"  Obtido   : {obtido}")
    if extra:
        for linha in extra:
            print("  " + linha)
    print(f"  Status   : {status}\n")


def tabela(res):
    linhas = ["Veículo   SoC   S T M F | Q | Potência"]
    for r in res:
        linhas.append(f"{r['id']:<9} {r['soc']:>3.0f}%  {r['S']} {r['T']} {r['M']} {r['F']} | {r['Q']} | {r['kw']:6.1f} kW")
    linhas.append(f"Total: {c.total_kw(res):.1f} kW")
    return linhas


print(f"Protótipo: teto={c.CAP_KW:.0f} kW, conector={c.CONECTOR_KW:.0f} kW, desempate={'ligado' if DESEMPATE else 'DESLIGADO (versão 1)'}\n")

# 01 – Login válido
ok = c.autenticar("admin@email.com", "1234")
registrar(1, "Funcionamento normal: login válido",
          "e-mail=admin@email.com, senha=1234", "Login autorizado",
          "Login autorizado" if ok else "Acesso negado", ok is True)

# 02 – Senha errada: operação impedida
est = c.Estacao(DESEMPATE)
aut, msg = est.iniciar_sessao("admin@email.com", "0000", "CAM-01", 30)
registrar(2, "Operação impedida: senha incorreta",
          "e-mail=admin@email.com, senha=0000, veículo CAM-01 (30%)",
          "Acesso negado; nenhuma sessão criada",
          f"{msg}; sessões ativas = {len(est.sessoes)}", (not aut) and len(est.sessoes) == 0)

# 03 – Um veículo
est = c.Estacao(DESEMPATE)
est.iniciar_sessao("admin@email.com", "1234", "CAM-01", 30)
res = est.estado()
ok = len(res) == 1 and res[0]["Q"] == 1 and res[0]["kw"] == 50 and (res[0]["S"], res[0]["T"], res[0]["F"]) == (1, 0, 0)
registrar(3, "Funcionamento normal: 1 veículo, teto não atingido",
          "login válido; CAM-01 com 30%", "S=1 T=0 F=0 -> Q=1; 50 kW (nominal)",
          f"S={res[0]['S']} T={res[0]['T']} F={res[0]['F']} -> Q={res[0]['Q']}; {res[0]['kw']:.0f} kW", ok, tabela(res))

# 04 – Dois veículos (teto exatamente atingido, ainda sem corte)
est = c.Estacao(DESEMPATE)
est.iniciar_sessao("admin@email.com", "1234", "CAM-01", 20)
est.iniciar_sessao("admin@email.com", "1234", "CAM-02", 70)
res = est.estado()
ok = all(r["Q"] == 1 and r["kw"] == 50 for r in res) and c.total_kw(res) == 100
registrar(4, "Decisão: 2 veículos, teto de 100 kW atingido sem corte",
          "login válido; CAM-01 20%, CAM-02 70%", "T=1, F=0 -> Q=1 para ambos; 50 kW cada (total 100 kW)",
          "; ".join(f"{r['id']}: Q={r['Q']} {r['kw']:.0f} kW" for r in res), ok, tabela(res))

# 05 – Três veículos: prioridade à menor bateria
est = c.Estacao(DESEMPATE)
for v, s in [("CAM-01", 60), ("CAM-02", 15), ("CAM-03", 40)]:
    est.iniciar_sessao("admin@email.com", "1234", v, s)
res = est.estado()
por_id = {r["id"]: r for r in res}
ok = (por_id["CAM-02"]["Q"] == 1 and por_id["CAM-02"]["kw"] == 50
      and por_id["CAM-01"]["Q"] == 0 and por_id["CAM-01"]["kw"] == 25
      and por_id["CAM-03"]["Q"] == 0 and por_id["CAM-03"]["kw"] == 25
      and c.total_kw(res) == 100)
registrar(5, "Decisão: 3 veículos excedem o teto; prioridade à menor bateria",
          "login válido; CAM-01 60%, CAM-02 15%, CAM-03 40%",
          "CAM-02 (15%): Q=1, 50 kW; CAM-01 e CAM-03: Q=0, 25 kW cada; total 100 kW",
          "; ".join(f"{r['id']}: Q={r['Q']} {r['kw']:.0f} kW" for r in res), ok, tabela(res))

# 06 – Sem sessão
est = c.Estacao(DESEMPATE)
res = est.estado()
ok = res == [] and c.total_kw(res) == 0 and c.q_simplificada(0, 0, 0, 0) == 0
registrar(6, "Exceção: nenhuma sessão ativa (S=0)",
          "nenhum veículo conectado", "Q=0; 0 kW entregues",
          f"sessões={len(res)}; Q(S=0)={c.q_simplificada(0, 0, 0, 0)}; total={c.total_kw(res):.1f} kW", ok)

# 07 – Entradas vazias / SoC inválido
est = c.Estacao(DESEMPATE)
a1, m1 = est.iniciar_sessao("", "", "CAM-01", 30)
a2, m2 = est.iniciar_sessao("admin@email.com", "1234", "CAM-02", 150)
ok = (not a1) and (not a2) and len(est.sessoes) == 0
registrar(7, "Exceção: campos vazios e nível de bateria inválido",
          "(a) e-mail='' senha=''; (b) login válido com SoC=150%",
          "(a) Acesso negado; (b) rejeitado; nenhuma sessão criada",
          f"(a) {m1}; (b) {m2}; sessões={len(est.sessoes)}", ok)

# 08 – Tabela verdade do login (Sprints 01/02)
esperado_login = {(0, 0): 0, (0, 1): 0, (1, 0): 0, (1, 1): 1}
obtido_login = {}
for e, s in esperado_login:
    obtido_login[(e, s)] = int(c.autenticar(c.EMAIL_CORRETO if e else "x@x.com", c.SENHA_CORRETA if s else "0000"))
ok = obtido_login == esperado_login
registrar(8, "Lógica do login: tabela verdade completa (AND de 2 XNOR)",
          "4 combinações de (e-mail correto, senha correta)", "saída = 0,0,0,1",
          "saída = " + ",".join(str(obtido_login[k]) for k in esperado_login), ok)

# 09 – Equivalência Qorig x Qsimp
dif = [(S, T, M, F) for S, T, M, F in itertools.product((0, 1), repeat=4)
       if c.q_original(S, T, M, F) != c.q_simplificada(S, T, M, F)]
registrar(9, "Lógica de potência: Q original == Q simplificada",
          "16 combinações de (S,T,M,F)", "0 divergências em 16",
          f"{len(dif)} divergências em 16", len(dif) == 0)

# 10 – Empate no menor nível de bateria
sessoes = [("CAM-01", 20), ("CAM-02", 20), ("CAM-03", 20), ("CAM-04", 80)]
res = c.alocar(sessoes, DESEMPATE)
tot = c.total_kw(res)
ok = tot <= c.CAP_KW + 1e-9
registrar(10, "Exceção: empate no menor nível de bateria (4 veículos)",
          "CAM-01 20%, CAM-02 20%, CAM-03 20%, CAM-04 80%",
          "total entregue <= 100 kW (apenas 1 veículo prioritário)",
          f"total = {tot:.1f} kW; veículos com M=1: {sum(r['M'] for r in res)}", ok, tabela(res))

# 11 – Invariante do teto em todas as combinações até 6 veículos
violacoes = 0
casos = 0
for n in range(0, 7):
    for socs in itertools.product((10, 50, 90), repeat=n):
        res = c.alocar([(f"V{i}", s) for i, s in enumerate(socs)], DESEMPATE)
        casos += 1
        if c.total_kw(res) > c.CAP_KW + 1e-9 or any(r["kw"] < 0 for r in res):
            violacoes += 1
registrar(11, "Segurança: teto de 100 kW nunca é ultrapassado",
          "0 a 6 veículos, SoC em {10, 50, 90}% (todas as combinações)",
          "0 violações do teto",
          f"{violacoes} violações em {casos} cenários", violacoes == 0)

# Resumo
print("=" * 50)
print("RESUMO")
for num, st in resultados:
    print(f"  Teste {num:02d}: {st}")
n_ok = sum(1 for _, st in resultados if st == "OK")
print(f"Total: {n_ok}/{len(resultados)} OK")
