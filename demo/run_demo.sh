#!/usr/bin/env bash
#
# Ejecuta la demo completa de búsqueda cuántica de subgrafos (Grover):
#   1. Demo mínimo (4 nodos, 3 qubits)
#   2. Barrido de host-nodes individuales (6, 8, 10, 12)
#   3. Curva de escalado completa N=4..12 (--sweep)
#
# Uso:
#   ./run_demo.sh              # corre todo
#   ./run_demo.sh min           # solo el demo mínimo
#   ./run_demo.sh scaled         # solo los host-nodes individuales
#   ./run_demo.sh sweep          # solo la curva de escalado
#
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

VENV_DIR="$DIR/.venv"
PYTHON="$VENV_DIR/bin/python"

if [[ ! -x "$PYTHON" ]]; then
    echo ">>> No se encontró venv en $VENV_DIR, creando uno nuevo..."
    python3 -m venv "$VENV_DIR"
fi

echo ">>> Verificando dependencias..."
if ! "$PYTHON" -c "import qiskit, qiskit_aer, numpy, matplotlib" >/dev/null 2>&1; then
    echo ">>> Instalando dependencias desde requirements.txt..."
    "$PYTHON" -m pip install -q -r requirements.txt
fi

HOST_NODES_SWEEP=(6 8 10 12)

run_min() {
    echo
    echo "======================================================="
    echo " 1/3  Demo mínimo (4 nodos, 3 qubits)"
    echo "======================================================="
    "$PYTHON" grover_subgraph_search.py
}

run_scaled() {
    echo
    echo "======================================================="
    echo " 2/3  Versión escalable — host-nodes individuales"
    echo "======================================================="
    for n in "${HOST_NODES_SWEEP[@]}"; do
        echo
        echo "--- host-nodes=$n ---"
        "$PYTHON" grover_subgraph_scaled.py --host-nodes "$n"
    done
}

run_sweep() {
    echo
    echo "======================================================="
    echo " 3/3  Curva de escalado completa N=4..12 (--sweep)"
    echo "======================================================="
    "$PYTHON" grover_subgraph_scaled.py --sweep
}

MODE="${1:-all}"

case "$MODE" in
    min)
        run_min
        ;;
    scaled)
        run_scaled
        ;;
    sweep)
        run_sweep
        ;;
    all)
        run_min
        run_scaled
        run_sweep
        ;;
    *)
        echo "Uso: $0 [min|scaled|sweep|all]" >&2
        exit 1
        ;;
esac

echo
echo "======================================================="
echo " Listo. Archivos generados en $DIR:"
echo "======================================================="
ls -1 "$DIR"/*.png 2>/dev/null || true
