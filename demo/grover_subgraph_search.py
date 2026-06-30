#!/usr/bin/env python3
"""
grover_subgraph_search.py
=========================
Demostración del Algoritmo de Grover aplicado al problema de isomorfismo
de subgrafos acotado: encontrar un anillo de fraude circular (3-ciclo dirigido)
dentro de un grafo de transacciones bancarias.

Problema:
  Host G: 4 cuentas {0,1,2,3}, aristas dirigidas: (0→1), (1→2), (2→0), (0→3)
  Patrón P: ciclo dirigido A→B→C→A (fraude circular)
  Espacio de búsqueda: 8 mapeos candidatos codificados en 3 qubits (estados |000⟩ a |111⟩)

Complejidad:
  Clásica: O(N) = O(8) consultas en el peor caso
  Grover:  O(√N) ≈ O(2.83) consultas — ventaja cuadrática

Uso:
  python grover_subgraph_search.py
  python grover_subgraph_search.py --shots 4096
  python grover_subgraph_search.py --gpu        (requiere qiskit-aer-gpu)
"""

import argparse
import sys
import numpy as np

import matplotlib
matplotlib.use('Agg')   # backend sin pantalla (compatible con servidores remotos)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

try:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
except ImportError as e:
    print(f"Error de importación: {e}")
    print("Instala las dependencias: pip install -r requirements.txt")
    sys.exit(1)


# ──────────────────────────────────────────────────────────────────────────────
# 1. DEFINICIÓN DEL PROBLEMA
# ──────────────────────────────────────────────────────────────────────────────

# Grafo host G: 4 cuentas bancarias, transacciones dirigidas
HOST_EDGES = frozenset([(0, 1), (1, 2), (2, 0), (0, 3)])

# 8 mapeos candidatos codificados en 3 qubits.
# Cada tupla (A,B,C) representa el mapeo: patrón-nodo-0→A, patrón-nodo-1→B, patrón-nodo-2→C.
# Pregunta: ¿existe el ciclo A→B→C→A en HOST_EDGES?
CANDIDATOS = [
    (0, 1, 2),   # |000⟩  ← VÁLIDO: 0→1→2→0
    (0, 1, 3),   # |001⟩
    (0, 2, 1),   # |010⟩
    (0, 3, 1),   # |011⟩
    (1, 0, 2),   # |100⟩
    (1, 2, 0),   # |101⟩  ← VÁLIDO: 1→2→0→1 (rotación)
    (2, 0, 1),   # |110⟩  ← VÁLIDO: 2→0→1→2 (rotación)
    (2, 0, 3),   # |111⟩
]


def es_ciclo_valido(triple, edges):
    """Verifica si (a,b,c) forma un 3-ciclo dirigido en el grafo dado."""
    a, b, c = triple
    return (a, b) in edges and (b, c) in edges and (c, a) in edges


# ──────────────────────────────────────────────────────────────────────────────
# 2. COMPONENTES DEL CIRCUITO CUÁNTICO
# ──────────────────────────────────────────────────────────────────────────────

def _ccz(qc, q0, q1, q2):
    """
    Puerta CCZ: aplica fase -1 al estado |111⟩ (cuando q0=q1=q2=1).
    Implementación: CCZ = (I⊗I⊗H) · CCX · (I⊗I⊗H)
    """
    qc.h(q2)
    qc.ccx(q0, q1, q2)
    qc.h(q2)


def oraculo(qc):
    """
    Oráculo de fase para el isomorfismo de subgrafos.

    Aplica un cambio de fase -1 a los estados cuánticos que representan
    mapeos válidos (ciclos de fraude). Para este toy problem:
      |000⟩ → mapeo (0,1,2): ciclo 0→1→2→0  ← marcar
      |101⟩ → mapeo (1,2,0): ciclo 1→2→0→1  ← marcar
      |110⟩ → mapeo (2,0,1): ciclo 2→0→1→2  ← marcar

    Técnica: para marcar |xyz⟩, volteamos con X los bits que son 0,
    aplicamos CCZ (que marca |111⟩), y volvemos a voltear.

    Convención Qiskit: el string de estado "q2q1q0" se lee big-endian.
      |000⟩ → q[0]=0, q[1]=0, q[2]=0
      |101⟩ → q[0]=1, q[1]=0, q[2]=1  (flip q[1] para llegar a |111⟩)
      |110⟩ → q[0]=0, q[1]=1, q[2]=1  (flip q[0] para llegar a |111⟩)
    """
    # Marcar |000⟩: voltear todos → |111⟩ → CCZ → voltear todos
    qc.x([0, 1, 2])
    _ccz(qc, 0, 1, 2)
    qc.x([0, 1, 2])
    qc.barrier(label='O|000⟩')

    # Marcar |101⟩: q[1]=0 es el único 0; flip q[1] → |111⟩ → CCZ → flip q[1]
    qc.x(1)
    _ccz(qc, 0, 1, 2)
    qc.x(1)
    qc.barrier(label='O|101⟩')

    # Marcar |110⟩: q[0]=0 es el único 0; flip q[0] → |111⟩ → CCZ → flip q[0]
    qc.x(0)
    _ccz(qc, 0, 1, 2)
    qc.x(0)
    qc.barrier(label='O|110⟩')


def difusor(qc):
    """
    Difusor de Grover: 2|ψ₀⟩⟨ψ₀| − I

    Reflexión respecto al estado de superposición uniforme |ψ₀⟩.
    Amplifica la amplitud de estados marcados y suprime los no marcados.

    Implementación: H^n · X^n · CCZ · X^n · H^n
    """
    qc.h([0, 1, 2])
    qc.x([0, 1, 2])
    _ccz(qc, 0, 1, 2)
    qc.x([0, 1, 2])
    qc.h([0, 1, 2])
    qc.barrier(label='Difusor')


def construir_circuito_grover(n_iter):
    """Construye el circuito completo de Grover con n_iter iteraciones."""
    qc = QuantumCircuit(3, 3)

    # Inicialización: superposición uniforme sobre los 8 candidatos
    qc.h([0, 1, 2])
    qc.barrier(label='|ψ₀⟩')

    # Iteraciones de Grover: oráculo + difusor
    for i in range(n_iter):
        oraculo(qc)
        difusor(qc)

    # Medición: colapsa la superposición al estado más probable
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc


# ──────────────────────────────────────────────────────────────────────────────
# 3. BÚSQUEDA CLÁSICA DE REFERENCIA
# ──────────────────────────────────────────────────────────────────────────────

def busqueda_clasica():
    print("\n" + "─" * 55)
    print("BÚSQUEDA CLÁSICA (fuerza bruta — referencia)")
    print("─" * 55)

    indices_validos = [
        i for i, c in enumerate(CANDIDATOS)
        if es_ciclo_valido(c, HOST_EDGES)
    ]

    print(f"Espacio de búsqueda : {len(CANDIDATOS)} mapeos candidatos")
    print(f"Consultas peor caso : {len(CANDIDATOS)}")
    print(f"Consultas promedio  : {len(CANDIDATOS) // 2}")
    print(f"Soluciones válidas  : {len(indices_validos)}")

    for idx in indices_validos:
        a, b, c = CANDIDATOS[idx]
        print(f"  |{idx:03b}⟩ = ({a},{b},{c})  →  {a}→{b} ✓  {b}→{c} ✓  {c}→{a} ✓")

    print(f"\nCiclo de fraude único: 0 → 1 → 2 → 0")
    print(f"(Los {len(indices_validos)} mapeos son rotaciones del mismo ciclo)")
    return indices_validos


# ──────────────────────────────────────────────────────────────────────────────
# 4. BÚSQUEDA CUÁNTICA CON GROVER
# ──────────────────────────────────────────────────────────────────────────────

def busqueda_cuantica(shots, usar_gpu):
    print("\n" + "─" * 55)
    print("BÚSQUEDA CUÁNTICA (Algoritmo de Grover)")
    print("─" * 55)

    k, N = 3, 8
    theta = np.arcsin(np.sqrt(k / N))
    n_iter = max(1, round(np.pi / (4 * theta) - 0.5))
    p_exito_teorico = np.sin((2 * n_iter + 1) * theta) ** 2

    print(f"Qubits              : 3 (codifica N={N} candidatos)")
    print(f"Soluciones (k)      : {k}")
    print(f"Ángulo θ            : {np.degrees(theta):.2f}° = arcsin(√(k/N))")
    print(f"Iteraciones óptimas : {n_iter}")
    print(f"Éxito teórico       : {p_exito_teorico:.1%}")
    print(f"Complejidad cuántica: O(√{N}) ≈ {np.sqrt(N):.2f} evaluaciones del oráculo")
    print(f"Complejidad clásica : O({N}) = {N} evaluaciones (peor caso)")

    qc = construir_circuito_grover(n_iter)

    # Selección del backend
    if usar_gpu:
        print("\nIntentando backend GPU (cuStateVec)...")
        try:
            sim = AerSimulator(device='GPU')
            print("Backend GPU activado.")
        except Exception as exc:
            print(f"GPU no disponible ({exc}). Usando CPU.")
            sim = AerSimulator()
    else:
        sim = AerSimulator()

    print(f"Backend             : {sim.name}")
    print(f"Shots               : {shots}")
    print("\nEjecutando circuito cuántico...")

    job = sim.run(qc, shots=shots)
    resultado = job.result()
    conteos = resultado.get_counts()

    return conteos, qc, n_iter


# ──────────────────────────────────────────────────────────────────────────────
# 5. VISUALIZACIÓN
# ──────────────────────────────────────────────────────────────────────────────

def graficar_resultados(conteos, indices_validos, shots,
                        output='resultados_grover_fraude.png'):
    """Genera histograma de probabilidades y visualización del grafo."""

    estados = [f"{i:03b}" for i in range(8)]
    estados_validos = {f"{i:03b}" for i in indices_validos}
    frecuencias = [conteos.get(s, 0) / shots for s in estados]
    colores = ['#27ae60' if s in estados_validos else '#c0392b' for s in estados]

    fig, (ax_hist, ax_grafo) = plt.subplots(1, 2, figsize=(14, 5.5))
    fig.suptitle(
        "Grover's Algorithm — Isomorfismo de Subgrafos: Detección de Fraude Circular",
        fontsize=12, fontweight='bold', y=1.01
    )

    # ── Histograma ──────────────────────────────────────────────────────────
    barras = ax_hist.bar(estados, frecuencias, color=colores,
                         edgecolor='#2c3e50', linewidth=0.7)

    # Línea de referencia: distribución uniforme sin Grover
    p_uniforme = 1 / 8
    ax_hist.axhline(y=p_uniforme, color='#7f8c8d', linestyle='--',
                    linewidth=1.3, alpha=0.9, zorder=0)
    ax_hist.text(7.6, p_uniforme + 0.006, '12.5%\n(sin Grover)',
                 fontsize=8, color='#7f8c8d', va='bottom', ha='right')

    for estado, barra, freq in zip(estados, barras, frecuencias):
        if freq > 0.012:
            ax_hist.text(
                barra.get_x() + barra.get_width() / 2,
                barra.get_height() + 0.009,
                f'{freq:.1%}',
                ha='center', va='bottom', fontsize=9, fontweight='bold',
                color='#2c3e50'
            )

    # Etiquetas de estado
    etiquetas = []
    for i, estado in enumerate(estados):
        mapeo = CANDIDATOS[i]
        etiquetas.append(f"|{estado}⟩\n({mapeo[0]},{mapeo[1]},{mapeo[2]})")
    ax_hist.set_xticks(range(8))
    ax_hist.set_xticklabels(etiquetas, fontsize=8)

    ax_hist.set_xlabel('Estado cuántico |q₂q₁q₀⟩  y  mapeo candidato (A,B,C)',
                       fontsize=10)
    ax_hist.set_ylabel('Probabilidad de medición', fontsize=10)
    ax_hist.set_title('Distribución de probabilidad tras iteraciones de Grover', fontsize=10)
    ax_hist.set_ylim(0, 0.50)
    ax_hist.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda y, _: f'{y:.0%}')
    )

    leyenda = [
        mpatches.Patch(color='#27ae60', label='Mapeo válido — anillo de fraude'),
        mpatches.Patch(color='#c0392b', label='Mapeo inválido'),
        plt.Line2D([0], [0], color='#7f8c8d', linestyle='--',
                   label='Distribución uniforme (sin amplificación)'),
    ]
    ax_hist.legend(handles=leyenda, loc='upper center', fontsize=8.5,
                   framealpha=0.9)

    # ── Grafo de transacciones ───────────────────────────────────────────────
    ax_grafo.set_xlim(-0.8, 4.0)
    ax_grafo.set_ylim(-0.8, 3.2)
    ax_grafo.set_aspect('equal')
    ax_grafo.axis('off')
    ax_grafo.set_title('Grafo de Transacciones  (G) y Patrón de Fraude (P)',
                       fontsize=10)

    # Posiciones de los nodos
    pos = {0: (1.0, 2.5), 1: (2.8, 2.5), 2: (1.9, 0.8), 3: (3.5, 0.8)}
    color_nodo = {0: '#e74c3c', 1: '#e74c3c', 2: '#e74c3c', 3: '#95a5a6'}
    labels_nodo = {0: 'Cta 0', 1: 'Cta 1', 2: 'Cta 2', 3: 'Cta 3 (legítima)'}

    for nodo, (x, y) in pos.items():
        circ = plt.Circle((x, y), 0.32, color=color_nodo[nodo],
                          zorder=5, alpha=0.92)
        ax_grafo.add_patch(circ)
        ax_grafo.text(x, y, str(nodo), ha='center', va='center',
                      fontsize=14, fontweight='bold', color='white', zorder=6)
        ax_grafo.text(x, y - 0.52, labels_nodo[nodo],
                      ha='center', va='top', fontsize=7.5, color='#34495e')

    aristas_fraude = frozenset([(0, 1), (1, 2), (2, 0)])
    estilo_arco = 'arc3,rad=0.18'

    for (u, v) in sorted(HOST_EDGES):
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        es_fraude = (u, v) in aristas_fraude
        ax_grafo.annotate(
            '',
            xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle='->', lw=2.8 if es_fraude else 1.5,
                color='#e74c3c' if es_fraude else '#7f8c8d',
                connectionstyle=estilo_arco,
                mutation_scale=16
            ),
            zorder=4
        )

    ax_grafo.text(
        1.9, -0.55,
        '↗ Rojo: ciclo de fraude  0 → 1 → 2 → 0\n'
        '↗ Gris: transacción legítima (0 → 3)',
        ha='center', fontsize=8.5, style='italic', color='#555',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#fafafa', alpha=0.7)
    )

    # Leyenda del patrón buscado
    ax_grafo.text(
        -0.6, 3.1,
        'Patrón P: A→B→C→A\n(3-ciclo dirigido = fraude circular)',
        fontsize=8.5, color='#2c3e50',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#ffeaa7', alpha=0.85)
    )

    plt.tight_layout()

    try:
        plt.savefig(output, dpi=150, bbox_inches='tight')
        print(f"\nGráfico guardado: {output}")
    except Exception as exc:
        print(f"No se pudo guardar el gráfico: {exc}")
    finally:
        plt.close()


# ──────────────────────────────────────────────────────────────────────────────
# 6. ANÁLISIS DE RESULTADOS
# ──────────────────────────────────────────────────────────────────────────────

def imprimir_resultados(conteos, indices_validos, shots):
    print("\n" + "─" * 55)
    print("RESULTADOS DE LA MEDICIÓN")
    print("─" * 55)

    estados_validos = {f"{i:03b}" for i in indices_validos}
    total_shots_validos = sum(
        conteos.get(s, 0) for s in estados_validos
    )

    for estado in sorted(conteos, key=lambda s: -conteos[s]):
        idx = int(estado, 2)
        mapeo = CANDIDATOS[idx]
        es_valido = es_ciclo_valido(mapeo, HOST_EDGES)
        marca = "  ← ANILLO DE FRAUDE ✓" if es_valido else ""
        print(f"  |{estado}⟩ = {mapeo} : "
              f"{conteos[estado]:5d} shots  "
              f"({conteos[estado]/shots:.1%})"
              f"{marca}")

    p_exito_empirica = total_shots_validos / shots
    print(f"\nProbabilidad empírica de encontrar el fraude: {p_exito_empirica:.1%}")
    print(f"Ciclo único identificado: Cta 0 → Cta 1 → Cta 2 → Cta 0")
    print(f"(Los 3 mapeos amplificados son rotaciones equivalentes del mismo ciclo)")


# ──────────────────────────────────────────────────────────────────────────────
# 7. MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Búsqueda cuántica de anillo de fraude — Grover + Qiskit'
    )
    parser.add_argument('--shots', type=int, default=2048,
                        help='Número de mediciones cuánticas (default: 2048)')
    parser.add_argument('--gpu', action='store_true',
                        help='Intentar backend GPU via cuStateVec (requiere qiskit-aer-gpu)')
    args = parser.parse_args()

    print("=" * 55)
    print("  ISOMORFISMO DE SUBGRAFOS — BÚSQUEDA CUÁNTICA")
    print("  Algoritmo de Grover · Qiskit AerSimulator")
    print("=" * 55)

    print("\nGrafo de transacciones G:")
    print(f"  Nodos: {{0, 1, 2, 3}}  (cuentas bancarias)")
    print(f"  Aristas dirigidas: {sorted(HOST_EDGES)}")

    print("\nPatrón buscado P: ciclo dirigido A→B→C→A  (fraude circular)")

    print("\nEspacio de búsqueda (3 qubits = 8 estados):")
    for i, c in enumerate(CANDIDATOS):
        valido = es_ciclo_valido(c, HOST_EDGES)
        marca = "← VÁLIDO" if valido else ""
        print(f"  |{i:03b}⟩ = {c}  {marca}")

    # Referencia clásica
    indices_validos = busqueda_clasica()

    # Búsqueda cuántica
    conteos, circuito, n_iter = busqueda_cuantica(args.shots, args.gpu)

    # Resultados
    imprimir_resultados(conteos, indices_validos, args.shots)

    # Información del circuito
    print("\n" + "─" * 55)
    print("INFORMACIÓN DEL CIRCUITO")
    print("─" * 55)
    print(f"  Qubits           : {circuito.num_qubits}")
    print(f"  Bits clásicos    : {circuito.num_clbits}")
    print(f"  Profundidad      : {circuito.depth()} capas de puertas")
    print(f"  Puertas totales  : {circuito.size()}")
    print(f"  Iteraciones Grover: {n_iter}")
    print(f"  Shots usados     : {args.shots}")

    # Gráfico
    graficar_resultados(conteos, indices_validos, args.shots)

    print("\n" + "=" * 55)
    print("Demo completado. Ver resultados_grover_fraude.png")
    print("=" * 55)


if __name__ == '__main__':
    main()
