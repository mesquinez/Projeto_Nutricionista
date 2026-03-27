import os
import sys
from pathlib import Path
from datetime import date, timedelta

# Configura ambiente de TESTE
os.environ["DB_PATH"] = "test_nutritionist.db"

# Adiciona diretório raiz ao path para importações
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.models.patient import Patient
from app.models.consulta import Consulta
from app.models.avaliacao import Avaliacao
from app.models.plano_alimentar import PlanoAlimentar
from app.models.anamnese import Anamnese

def seed():
    """Popula o banco de dados de teste com jornadas clínicas completas."""
    print(" [SEED] Iniciando população da base de teste...")
    
    test_db = Path("test_nutritionist.db")
    if test_db.exists():
        try:
            os.remove(test_db)
        except PermissionError:
            print(" [ERRO] Banco de teste em uso. Feche o sistema.")
            sys.exit(1)

    # Inicialização manual de infraestrutura (bypass GUI)
    from app.repositories import (
        SQLitePatientRepository, SQLiteAnamneseRepository,
        SQLiteConsultaRepository, SQLiteAvaliacaoRepository,
        SQLitePlanoAlimentarRepository
    )
    from app.services import (
        PatientService, AnamneseService,
        ConsultaService, AvaliacaoService,
        PlanoAlimentarService
    )
    from app.controllers import (
        PatientController, AnamneseController,
        ConsultaController, AvaliacaoController,
        PlanoAlimentarController
    )

    db_path = Path("test_nutritionist.db")
    
    # Repositorios e Services
    p_repo = SQLitePatientRepository(db_path); p_repo._init_db()
    p_ctrl = PatientController(PatientService(p_repo))
    
    a_repo = SQLiteAnamneseRepository(db_path); a_repo._init_db()
    a_ctrl = AnamneseController(AnamneseService(a_repo))
    
    c_repo = SQLiteConsultaRepository(db_path); c_repo._init_db()
    c_ctrl = ConsultaController(ConsultaService(c_repo))
    
    ev_repo = SQLiteAvaliacaoRepository(db_path); ev_repo._init_db()
    ev_ctrl = AvaliacaoController(AvaliacaoService(ev_repo))
    
    pl_repo = SQLitePlanoAlimentarRepository(db_path); pl_repo._init_db()
    pl_ctrl = PlanoAlimentarController(PlanoAlimentarService(pl_repo))

    # --- PERFIS ---

    # 1. João Inicial (Fluxo Completo Simples)
    print(" -> Criando João Inicial...")
    p1 = p_ctrl.create_patient(Patient(name="João Pedro Almeida", phone="(21) 99888-7766", email="joao.almeida@email.com", birth_date=date(1994, 6, 12)))
    c_ctrl.create(Consulta(patient_id=p1.id, date=date(2026, 3, 20), queixa_principal="Deseja emagrecer com saúde", conduta="Aumento de ingestão hídrica", peso_registrado=92.5))
    ev_ctrl.create(Avaliacao(patient_id=p1.id, date=date(2026, 3, 20), peso=92.5, altura=178, cintura=101, quadril=108))
    pl_ctrl.create(PlanoAlimentar(patient_id=p1.id, date=date(2026, 3, 20), calorias=2100, cafe_manha="Pão integral + ovos"))
    a_ctrl.create_anamnese(Anamnese(patient_id=p1.id, date=date(2026, 3, 20), objetivo_principal="Emagrecer com saúde e melhorar disposição", peso_desejado=82.0))

    # 2. Maria Retorno (Histórico e Evolução)
    print(" -> Criando Maria Retorno...")
    p2 = p_ctrl.create_patient(Patient(name="Maria Clara Souza", phone="(21) 99777-6655", email="maria.souza@email.com", birth_date=date(1988, 9, 3)))
    # Consultas e Avaliações Dinâmicas (3 meses)
    for i in range(3):
        d = date(2026, 1+i, 10+i)
        peso = 78.4 - (i * 1.2)
        c_ctrl.create(Consulta(patient_id=p2.id, date=d, queixa_principal=f"Retorno {i+1}", peso_registrado=peso))
        ev_ctrl.create(Avaliacao(patient_id=p2.id, date=d, peso=peso, altura=164, cintura=92-i*2))
    a_ctrl.create_anamnese(Anamnese(patient_id=p2.id, date=date(2026, 1, 10), objetivo_principal="Emagrecimento Constante"))

    # 3. Carlos Metabólico (Comorbidades)
    print(" -> Criando Carlos Metabólico...")
    p3 = p_ctrl.create_patient(Patient(name="Carlos Henrique Braga", phone="(21) 99666-5544", email="carlos.braga@email.com", birth_date=date(1977, 1, 19)))
    c_ctrl.create(Consulta(patient_id=p3.id, date=date(2026, 3, 22), queixa_principal="Glicemia alta", peso_registrado=104.2))
    a_ctrl.create_anamnese(Anamnese(patient_id=p3.id, date=date(2026, 3, 22), objetivo_principal="Melhora metabólica e glicêmica", medicamentos="Metformina, Losartana", doencas_previas="Hipertensão, Diabetes"))

    # 4. Ana Esportiva (Muitas Medidas)
    print(" -> Criando Ana Esportiva...")
    p4 = p_ctrl.create_patient(Patient(name="Ana Beatriz Lima", phone="(21) 99555-4433", email="ana.lima@email.com", birth_date=date(1996, 11, 27)))
    ev_ctrl.create(Avaliacao(patient_id=p4.id, date=date(2026, 3, 22), peso=61.7, altura=167, cintura=70, quadril=96, bracodireito=28, coxa=56, panturrilha=35))
    pl_ctrl.create(PlanoAlimentar(patient_id=p4.id, date=date(2026, 3, 22), calorias=2300, cafe_manha="Whey + Fruta", almoco="Arroz + Frango + Batata Doce"))

    # 5. Lúcia Sensível (Digestão)
    print(" -> Criando Lúcia Sensível...")
    p5 = p_ctrl.create_patient(Patient(name="Lúcia Helena Matos", phone="(21) 99444-3322", email="lucia.matos@email.com", birth_date=date(1991, 4, 14)))
    a_ctrl.create_anamnese(Anamnese(patient_id=p5.id, date=date(2026, 3, 21), objetivo_principal="Melhorar sintomas digestivos", alergio_intolerancias="Lactose", ritmo_intestinal="Irregular"))

    # 6. José Legado (Dados Problemáticos - Bypass Service)
    print(" -> Criando José Legado (Problemático)...")
    p6_model = Patient(name="José Legado", phone="123", email="jose@@email", birth_date=None)
    p6_id = p_repo.add(p6_model)
    # Consulta com campos bizarros via repo
    c_repo.add(Consulta(patient_id=p6_id, date=date(2000, 1, 1), queixa_principal="", peso_registrado=0.0))
    # Avaliação com strings onde deveria ser float (forçando resiliência)
    ev_repo.add(Avaliacao(patient_id=p6_id, date=date(2000, 1, 1), peso="oitenta", altura=None))

    # 7. Paula Administrativa (Enxuto)
    print(" -> Criando Paula Administrativa...")
    p_ctrl.create_patient(Patient(name="Paula Ribeiro", phone="(21) 99333-2211", email="paula.ribeiro@email.com", birth_date=date(1985, 7, 8)))

    # 8. Roberto Hipertrofia (Alta Caloria)
    print(" -> Criando Roberto Hipertrofia...")
    p8 = p_ctrl.create_patient(Patient(name="Roberto Nunes", phone="(21) 99222-1100", email="roberto.nunes@email.com", birth_date=date(1999, 2, 25)))
    pl_ctrl.create(PlanoAlimentar(patient_id=p8.id, date=date(2026, 3, 22), calorias=3200, proteinas=190, carboidratos=400, gorduras=80))

    print(" [SEED] Sucesso! 8 perfis clínicos carregados.")

if __name__ == "__main__":
    seed()
