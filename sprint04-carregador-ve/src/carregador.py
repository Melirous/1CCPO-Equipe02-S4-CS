# -*- coding: utf-8 -*-
"""
Protótipo final – Estação de recarga de veículos elétricos comerciais (Sprint 04)

Integra a lógica validada nas sprints anteriores:
  * Sprints 01-02: autenticação  Login = (Email ⊙ EmailCorreto) · (Senha ⊙ SenhaCorreta)
  * Sprint 03:     decisão de potência  Q = S·(¬T + M + ¬F)  (equivalente a Σm(8,9,10,11,12,14,15))

Entradas  : e-mail, senha, nível de bateria (SoC) de cada veículo conectado
Decisões  : porta AND/XNOR do login + função booleana Q por sessão
Saídas    : "Login autorizado"/"Acesso negado" + potência (kW) entregue a cada veículo

Premissas do protótipo (a equipe pode ajustar as constantes abaixo):
  * teto de potência contratada da estação ........ 100 kW  (Sprint 03)
  * potência máxima / nominal de cada conector .... 50 kW   (premissa)
  * prioridade: veículo com MENOR nível de bateria recebe a potência nominal;
    os demais dividem o que sobra do teto.
"""

CAP_KW = 100.0        # teto de potência contratada
CONECTOR_KW = 50.0    # potência máxima/nominal de um conector

EMAIL_CORRETO = "admin@email.com"   # credenciais da Sprint 02 (Python)
SENHA_CORRETA = "1234"


# ----------------------------------------------------------------------------
# 1) AUTENTICAÇÃO  (Sprints 01 e 02)
# ----------------------------------------------------------------------------
def xnor(a: bool, b: bool) -> bool:
    """Porta XNOR: 1 somente quando as duas entradas são iguais."""
    return a == b


def autenticar(email_digitado: str, senha_digitada: str) -> bool:
    """Login = (Email ⊙ EmailCorreto) · (Senha ⊙ SenhaCorreta)  — porta AND de dois XNOR.

    Cada XNOR compara 'o dado confere com o cadastrado' (True) com True (esperado)."""
    email_ok = xnor(email_digitado == EMAIL_CORRETO, True)
    senha_ok = xnor(senha_digitada == SENHA_CORRETA, True)
    return email_ok and senha_ok


# ----------------------------------------------------------------------------
# 2) DECISÃO DE POTÊNCIA  (Sprint 03)
# ----------------------------------------------------------------------------
MINTERMOS_Q = {8, 9, 10, 11, 12, 14, 15}   # expressão original (soma de produtos canônica)


def q_original(S: int, T: int, M: int, F: int) -> int:
    """Expressão original: 1 nos mintermos 8,9,10,11,12,14,15 (índice = S T M F em binário)."""
    return 1 if (S << 3 | T << 2 | M << 1 | F) in MINTERMOS_Q else 0


def q_simplificada(S: int, T: int, M: int, F: int) -> int:
    """Expressão simplificada pelo mapa de Karnaugh:  Q = S·(¬T + M + ¬F)."""
    return int(bool(S and ((not T) or M or (not F))))


# ----------------------------------------------------------------------------
# 3) ALOCAÇÃO DE POTÊNCIA DA ESTAÇÃO
# ----------------------------------------------------------------------------
def alocar(sessoes, desempate=True):
    """Calcula S, T, M, F, Q e a potência (kW) de cada sessão.

    sessoes   : lista de (id_veiculo, soc_percentual) na ordem de chegada
    desempate : se True, havendo empate no menor SoC, só a sessão que chegou
                primeiro recebe M=1 (corrige falha encontrada no Teste 10).
    """
    n = len(sessoes)
    S = int(n >= 1)
    T = int(n * CONECTOR_KW >= CAP_KW)                       # demanda nominal atinge o teto
    F = int(n > 0 and (CAP_KW / n) < CONECTOR_KW)            # fatia igualitária < máximo do conector

    socs = [soc for _, soc in sessoes]
    menor = min(socs) if socs else None
    if desempate and socs:
        idx_prioritario = socs.index(menor)                  # primeira com menor SoC
    resultado = []
    for i, (vid, soc) in enumerate(sessoes):
        M = int(i == idx_prioritario) if desempate else int(soc == menor)
        Q = q_simplificada(S, T, M, F)
        resultado.append({"id": vid, "soc": soc, "S": S, "T": T, "M": M, "F": F, "Q": Q})

    # Q = 1 -> potência nominal; Q = 0 -> divide o que sobrou do teto
    n_q1 = sum(r["Q"] for r in resultado)
    n_q0 = n - n_q1
    sobra = max(0.0, CAP_KW - n_q1 * CONECTOR_KW)
    for r in resultado:
        r["kw"] = CONECTOR_KW if r["Q"] else (sobra / n_q0 if n_q0 else 0.0)
    return resultado


def total_kw(resultado) -> float:
    return sum(r["kw"] for r in resultado)


# ----------------------------------------------------------------------------
# 4) ESTAÇÃO (fluxo integrado: login -> sessão -> alocação)
# ----------------------------------------------------------------------------
class Estacao:
    def __init__(self, desempate=True):
        self.sessoes = []            # [(id, soc)] em ordem de chegada
        self.desempate = desempate

    def iniciar_sessao(self, email, senha, veiculo, soc):
        """Só inicia a recarga se o login for autorizado e o SoC for válido."""
        if not autenticar(email, senha):
            return False, "Acesso negado"
        if not isinstance(soc, (int, float)) or not (0 <= soc <= 100):
            return False, "Nível de bateria inválido (use 0 a 100%)"
        self.sessoes.append((veiculo, soc))
        return True, "Login autorizado"

    def encerrar_sessao(self, veiculo):
        self.sessoes = [s for s in self.sessoes if s[0] != veiculo]

    def estado(self):
        return alocar(self.sessoes, self.desempate)


def imprimir_estado(resultado):
    if not resultado:
        print("  (nenhuma sessão ativa)  S=0  Q=0  total = 0.0 kW")
        return
    print("  Veículo   SoC   S T M F | Q | Potência")
    for r in resultado:
        print(f"  {r['id']:<9} {r['soc']:>3.0f}%  {r['S']} {r['T']} {r['M']} {r['F']} | {r['Q']} | {r['kw']:6.1f} kW")
    print(f"  Total entregue: {total_kw(resultado):.1f} kW (teto {CAP_KW:.0f} kW)")


# ----------------------------------------------------------------------------
# 5) MODO INTERATIVO
# ----------------------------------------------------------------------------
def main():
    est = Estacao()
    print("=== Estação de recarga – protótipo Sprint 04 ===")
    while True:
        print("\n1) Conectar veículo  2) Desconectar veículo  3) Ver potência  0) Sair")
        op = input("Opção: ").strip()
        if op == "1":
            email = input("E-mail: ")
            senha = input("Senha: ")
            vid = input("Identificação do veículo: ")
            try:
                soc = float(input("Nível de bateria (%): "))
            except ValueError:
                soc = -1
            ok, msg = est.iniciar_sessao(email, senha, vid, soc)
            print(msg)
            if ok:
                imprimir_estado(est.estado())
        elif op == "2":
            est.encerrar_sessao(input("Veículo: "))
            imprimir_estado(est.estado())
        elif op == "3":
            imprimir_estado(est.estado())
        elif op == "0":
            break


if __name__ == "__main__":
    main()
