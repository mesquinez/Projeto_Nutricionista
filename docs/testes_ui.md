# Testes de UI

## Status atual

Hoje a suíte roda com este resultado:

```bash
108 passed, 24 skipped
```

Os `24 skipped` acontecem porque o runtime `Tk/Tcl` não está disponível de forma funcional neste ambiente. Os testes que precisam abrir `tk.Tk()` falham na inicialização do `Tkinter`, então eles são pulados de propósito no `tests/conftest.py`.

## Arquivos afetados

Os skips afetam estes arquivos:

- `tests/test_patient_ui.py`
- `tests/test_patient_ui_rapid.py`
- `tests/test_patient_window_ui.py`

O arquivo abaixo continua rodando normalmente:

- `tests/test_patient_ui_fast.py`

## Como rodar a suíte completa

```bash
pytest -q
```

Resultado esperado hoje:

```bash
108 passed, 24 skipped
```

## Como rodar só os testes de UI

```bash
pytest -q tests/test_patient_ui.py tests/test_patient_ui_fast.py tests/test_patient_ui_rapid.py tests/test_patient_window_ui.py
```

Resultado esperado hoje:

```bash
16 passed, 24 skipped
```
