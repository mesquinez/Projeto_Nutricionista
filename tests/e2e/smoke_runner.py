import os
import sys
import time
import tkinter as tk
from pathlib import Path

# Setup environment
os.environ["DB_PATH"] = "test_nutritionist.db"
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.main import create_app

def run_smoke_test():
    is_fast = os.getenv("SMOKE_FAST") == "1"
    WAIT_NORMAL = 400 if is_fast else 1000
    WAIT_LONG = 700 if is_fast else 2000
    
    # MOCK MESSAGEBOX
    from tkinter import messagebox
    messagebox.askyesno = lambda t, m: (print(f" [MOCK] Sim: {m}") or True)
    messagebox.showerror = lambda t, m: print(f" [MOCK] Erro: {m}")
    messagebox.showinfo = lambda t, m: print(f" [MOCK] Info: {m}")

    if not Path("test_nutritionist.db").exists():
        print(" [ERRO] Banco de teste não encontrado.")
        sys.exit(1)

    app_window = create_app()
    root = app_window.root
    
    # Estado compartilhado entre passos
    state = {"last_win": None}

    def find_patient_in_tree(name_parts):
        """Busca paciente que contenha todas as partes do nome informadas."""
        for item_id in app_window.tree.get_children():
            vals = [str(v) for v in app_window.tree.item(item_id, "values")]
            if all(any(p.lower() in v.lower() for v in vals) for p in name_parts):
                return item_id
        return None

    def find_toplevel_by_title(title_part):
        """Busca recursiva por janelas Toplevel pelo título."""
        def walk(parent):
            for child in parent.winfo_children():
                if isinstance(child, tk.Toplevel):
                    try:
                        if title_part.lower() in child.title().lower():
                            return child
                    except: pass
                res = walk(child)
                if res: return res
            return None
        return walk(root)

    def close_all_toplevels():
        for child in root.winfo_children():
            if isinstance(child, tk.Toplevel):
                child.destroy()

    # --- JORNADAS ---

    def start():
        print(f" [INFO] Iniciando Esteira de Homologação Clínica {'(FAST)' if is_fast else ''}")
        root.after(1000, jornada_1_joao)

    def jornada_1_joao():
        print(" [JORNADA 1/4] João Inicial - Primeiro Atendimento Completo")
        item = find_patient_in_tree(["Jo", "Pedro"])
        if not item: 
            print(" [ERRO] João não localizado na lista.")
            sys.exit(1)
        
        app_window.tree.selection_set(item)
        app_window._open_patient_detail()
        root.after(WAIT_LONG, step_joao_2)

    def step_joao_2():
        win = find_toplevel_by_title("João Pedro")
        if win:
            print(" -> [OK] Prontuário aberto. Verificando Consultas...")
            win.notebook.select(win.tab_consultas)
            state["last_win"] = win
            root.after(WAIT_NORMAL, step_joao_3)
        else:
            print(" [ERRO] Prontuário João não abriu."); sys.exit(1)

    def step_joao_3():
        print(" -> [OK] Verificando Anamnese...")
        win = state["last_win"]
        win._abrir_anamnese()
        root.after(WAIT_NORMAL, step_joao_4)

    def step_joao_4():
        ana_win = find_toplevel_by_title("Anamnese")
        if ana_win:
            print(" -> [OK] Anamnese aberta com sucesso.")
            close_all_toplevels()
            root.after(WAIT_NORMAL, jornada_2_maria)
        else:
            print(" [ERRO] Anamnese não abriu."); sys.exit(1)

    def jornada_2_maria():
        print(" [JORNADA 2/4] Maria Retorno - Histórico de 3 Consultas")
        item = find_patient_in_tree(["Maria", "Clara"])
        if not item:
            print(" [ERRO] Maria não localizada."); sys.exit(1)
        app_window.tree.selection_set(item)
        app_window._open_patient_detail()
        root.after(WAIT_LONG, step_maria_check)

    def step_maria_check():
        win = find_toplevel_by_title("Maria Clara")
        if win:
            count = len(win.consultas_tree.get_children())
            print(f" -> [OK] Maria aberta. Registros encontrados: {count}")
            if count < 3:
                print(" [ERRO] Histórico de Maria incompleto."); sys.exit(1)
            close_all_toplevels()
            root.after(WAIT_NORMAL, jornada_3_jose)
        else: 
            print(" [ERRO] Prontuário Maria não abriu."); sys.exit(1)

    def jornada_3_jose():
        print(" [JORNADA 3/4] José Legado - Resiliência a Dados Malformados")
        item = find_patient_in_tree(["José", "Legado"])
        if not item:
            # Fallback sem acento se necessário por causa de encoding do terminal
            item = find_patient_in_tree(["Jos", "Legado"])
        
        if not item:
            print(" [ERRO] José não localizado."); sys.exit(1)
            
        app_window.tree.selection_set(item)
        app_window._open_patient_detail()
        root.after(WAIT_LONG, step_jose_check)

    def step_jose_check():
        win = find_toplevel_by_title("José Legado")
        if win:
            print(" -> [OK] Prontuário legado aberto sem crash.")
            win.notebook.select(win.tab_avaliacoes)
            its = win.avaliacoes_tree.get_children()
            if its:
                win.avaliacoes_tree.selection_set(its[0])
                win._editar_avaliacao()
                root.after(WAIT_NORMAL, step_jose_final)
            else:
                print(" [ERRO] Avaliação do legado não encontrada."); sys.exit(1)
        else: 
            print(" [ERRO] Prontuário José não abriu."); sys.exit(1)

    def step_jose_final():
        av_win = find_toplevel_by_title("Avaliação")
        if av_win:
            print(" -> [OK] Janela de Avaliação legada aberta (Resiliência OK).")
            close_all_toplevels()
            root.after(WAIT_NORMAL, jornada_4_ana)
        else: 
             print(" [ERRO] Janela de Avaliação legada não abriu."); sys.exit(1)

    def jornada_4_ana():
        print(" [JORNADA 4/4] Ana Esportiva - Medidas Ricas")
        item = find_patient_in_tree(["Ana", "Beatriz"])
        if not item:
             print(" [ERRO] Ana não localizada."); sys.exit(1)
             
        app_window.tree.selection_set(item)
        app_window._open_patient_detail()
        root.after(WAIT_LONG, step_ana_check)

    def step_ana_check():
        win = find_toplevel_by_title("Ana Beatriz")
        if win:
            print(" -> [OK] Abrindo Plano Alimentar de Atleta...")
            win.notebook.select(win.tab_planos)
            its = win.planos_tree.get_children()
            if its:
                win.planos_tree.selection_set(its[0])
                win._editar_plano()
                root.after(WAIT_NORMAL, end_test)
            else:
                 print(" [ERRO] Plano de Ana não encontrado."); sys.exit(1)
        else: 
             print(" [ERRO] Prontuário Ana não abriu."); sys.exit(1)

    def end_test():
        print(" -> [OK] Todas as jornadas clínicas validadas com sucesso.")
        close_all_toplevels()
        root.after(500, root.destroy)

    root.after(1000, start)
    app_window.run()

if __name__ == "__main__":
    run_smoke_test()
