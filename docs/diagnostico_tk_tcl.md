# Diagnóstico Tk/Tcl

## O que falta no ambiente

Falta um runtime `Tk/Tcl` funcional para o Python usado nos testes.

Os arquivos principais existem neste ambiente:

- `Python311\tcl\tcl8.6\init.tcl`
- `Python311\tcl\tk8.6\tk.tcl`
- `Python311\DLLs\tcl86t.dll`
- `Python311\DLLs\tk86t.dll`

Mesmo assim, o `Tkinter` não consegue inicializar e retorna erro ao criar `tk.Tk()`.

## Como verificar

Verificação rápida:

```bash
python -c "import tkinter as tk; root = tk.Tk(); root.withdraw(); root.destroy(); print('ok')"
```

Hoje o esperado neste ambiente é falhar com erro parecido com:

```text
_tkinter.TclError: Can't find a usable init.tcl
```

Também é possível conferir a presença dos arquivos:

```bash
python -c "import os, sys; b=getattr(sys,'base_prefix',sys.prefix); print(os.path.exists(os.path.join(b,'tcl','tcl8.6','init.tcl'))); print(os.path.exists(os.path.join(b,'tcl','tk8.6','tk.tcl')))"
```

## Correção necessária no ambiente

A correção não é nos testes. É no ambiente Python/Tk:

- reinstalar o Python com o componente `tcl/tk` íntegro
- garantir que o Python usado pelo `pytest` seja o mesmo que contém `tcl86t.dll`, `tk86t.dll`, `init.tcl` e `tk.tcl`
- se necessário, ajustar `TCL_LIBRARY` e `TK_LIBRARY` para a pasta `tcl` do mesmo `base_prefix` do Python em uso

## Resumo objetivo

- não falta teste
- não falta fixture nova
- o bloqueio real é a inicialização quebrada do `Tkinter` no ambiente atual
- quando `tk.Tk()` voltar a abrir normalmente, os testes de UI deixam de precisar de `skip`
