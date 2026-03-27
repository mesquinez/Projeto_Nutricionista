import subprocess
import os
import sys
from pathlib import Path

def run():
    print("========================================")
    print("   ESTEIRA DE TESTES - NUTRICIONISTA    ")
    print("========================================\n")
    
    fast_mode = "--fast" in sys.argv
    python_exe = sys.executable
    e2e_dir = Path("tests/e2e")
    
    # [PASSO 1/3] Seeding
    print("[PASSO 1/3] Gerando 8 perfis clínicos para homologação...")
    try:
        subprocess.check_call([python_exe, str(e2e_dir / "seeder.py")])
        print(" -> [OK] Banco de teste pronto.")
    except subprocess.CalledProcessError:
        print("\n [ERRO] Falha ao semear dados. Abortando.")
        sys.exit(1)

    # [PASSO 2/3] Smoke Test
    mode_str = "RÁPIDO" if fast_mode else "VISÍVEL (COM PAUSAS)"
    print(f"\n[PASSO 2/3] Executando 4 Jornadas Clínicas em modo {mode_str}...")
    
    env = os.environ.copy()
    if fast_mode:
        env["SMOKE_FAST"] = "1"
    
    try:
        subprocess.check_call([python_exe, str(e2e_dir / "smoke_runner.py")], env=env)
        print(" -> [OK] Fluxos validados com sucesso.")
    except subprocess.CalledProcessError:
        print("\n [ERRO] Falha na execução do Smoke Test.")
        sys.exit(1)

    # [PASSO 3/3] Finalização
    print("\n[PASSO 3/3] Finalizando esteira...")
    print("========================================")
    print("    [SUCESSO] SISTEMA HOMOLOGADO!       ")
    print("========================================")
    sys.exit(0)

if __name__ == "__main__":
    run()
