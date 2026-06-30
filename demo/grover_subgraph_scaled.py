#!/usr/bin/env python3
"""
grover_subgraph_scaled.py
=========================
Versión escalable del isomorfismo de subgrafos con el Algoritmo de Grover.

Codificación: cada uno de los P(N,k) = N!/(N-k)! mapeos candidatos se
asigna a un estado cuántico. Se necesitan n = ⌈log₂(P(N,k))⌉ qubits.
Como P(N,3) ~ N³, el crecimiento de qubits es O(3·log₂N) — logarítmico
en N, mientras que el espacio de búsqueda crece cúbico.

Ventaja demostrada:
  Clásico: O(P(N,k)) consultas     →  crece cúbico con N
  Grover:  O(√P(N,k)) consultas    →  crece como √N³ ≈ N^1.5

Uso:
  python grover_subgraph_scaled.py                    # N=6 nodos, demo rápido
  python grover_subgraph_scaled.py --host-nodes 8     # 9 qubits
  python grover_subgraph_scaled.py --sweep            # curva de escalado N=4..12
  python grover_subgraph_scaled.py --gpu              # backend GPU (cuStateVec)
"""

import argparse
import sys
import numpy as np
from itertools import permutations

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

try:
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import XGate
    from qiskit_aer import AerSimulator
except ImportError as e:
    print(f"Error: {e}\nInstala: pip install qiskit qiskit-aer")
    sys.exit(1)


# ──────────────────────────────────────────────────────────────────────────────
# 1. GENERACIÓN DEL GRAFO HOST
# ──────────────────────────────────────────────────────────────────────────────

def generar_grafo(n_nodes, densidad=0.25, seed=42, k=3):
    """
    Genera un grafo dirigido aleatorio de n_nodes nodos con:
    - Probabilidad `densidad` de existencia de cada arista dirigida
    - Ciclo de fraude garantizado: 0→1→2→...→(k-1)→0
    """
    rng = np.random.default_rng(seed)
    adj = rng.random((n_nodes, n_nodes)) < densidad
    np.fill_diagonal(adj, 0)
    # Garantizar al menos un k-ciclo: el anillo 0→1→...→(k-1)→0
    for i in range(k):
        adj[i][(i + 1) % k] = True
    edges = frozenset(
        (i, j) for i in range(n_nodes) for j in range(n_nodes) if adj[i][j]
    )
    return edges


def encontrar_mapeos(n_nodes, k, edges):
    """
    Enumera todos los k-tuplas ordenadas inyectivas (P(n_nodes,k) candidatos).
    Devuelve (lista_completa, índices_de_los_válidos).
    Un candidato es válido si sus k nodos forman un k-ciclo dirigido en G.
    """
    candidatos = list(permutations(range(n_nodes), k))
    validos = [
        i for i, m in enumerate(candidatos)
        if all((m[j], m[(j + 1) % k]) in edges for j in range(k))
    ]
    return candidatos, validos


# ──────────────────────────────────────────────────────────────────────────────
# 2. PUERTAS CUÁNTICAS ESCALABLES
# ──────────────────────────────────────────────────────────────────────────────

def _mcx(qc, controles, target):
    """
    Multi-controlled X compatible con Qiskit 1.x y 2.x.
    Usa CX/CCX para 1-2 controles y XGate().control(n) para más.
    """
    n = len(controles)
    if n == 0:
        qc.x(target)
    elif n == 1:
        qc.cx(controles[0], target)
    elif n == 2:
        qc.ccx(controles[0], controles[1], target)
    else:
        qc.append(XGate().control(n), controles + [target])


def _mcz(qc, n_qubits):
    """
    Multi-controlled Z: aplica fase -1 cuando todos los n_qubits son |1⟩.
    Implementación: H · MCX(0..n-2, n-1) · H en el qubit target.
    """
    target = n_qubits - 1
    controles = list(range(n_qubits - 1))
    qc.h(target)
    _mcx(qc, controles, target)
    qc.h(target)


def marcar_estado(qc, estado_int, n_qubits):
    """
    Aplica fase -1 al estado |estado_int⟩:
    1. Voltea los bits que son 0 en estado_int (convierte |estado⟩ → |111...1⟩)
    2. Aplica MCZ (que marca |111...1⟩)
    3. Vuelve a voltear los bits (restaura la base)
    """
    bits_a_voltear = [b for b in range(n_qubits) if not (estado_int >> b) & 1]
    if bits_a_voltear:
        qc.x(bits_a_voltear)
    _mcz(qc, n_qubits)
    if bits_a_voltear:
        qc.x(bits_a_voltear)


def oraculo_escalable(qc, validos, n_qubits):
    """
    Oráculo de fase: aplica -1 a todos los estados válidos.
    Complejidad: O(k_sol × n_qubits) puertas donde k_sol = len(validos).
    """
    for idx in validos:
        marcar_estado(qc, idx, n_qubits)
    qc.barrier(label=f'Oracle ({len(validos)} sols)')


def difusor_escalable(qc, n_qubits):
    """
    Difusor de Grover generalizado: 2|ψ₀⟩⟨ψ₀| − I
    Funciona para cualquier número de qubits.
    """
    target = n_qubits - 1
    controles = list(range(n_qubits - 1))
    qc.h(range(n_qubits))
    qc.x(range(n_qubits))
    qc.h(target)
    _mcx(qc, controles, target)
    qc.h(target)
    qc.x(range(n_qubits))
    qc.h(range(n_qubits))
    qc.barrier(label='Diffuser')


def construir_circuito_escalable(n_qubits, validos, n_iter):
    """Circuito de Grover completo con n_iter iteraciones."""
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(range(n_qubits))           # superposición uniforme
    qc.barrier(label='|ψ₀⟩')
    for _ in range(n_iter):
        oraculo_escalable(qc, validos, n_qubits)
        difusor_escalable(qc, n_qubits)
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


# ──────────────────────────────────────────────────────────────────────────────
# 3. CÁLCULO DE PARÁMETROS ÓPTIMOS
# ──────────────────────────────────────────────────────────────────────────────

def calcular_parametros(n_candidatos, k_sol, n_qubits):
    """
    Calcula iteraciones óptimas y probabilidad teórica de éxito de Grover.
    Usa el espacio real 2^n_qubits (que puede incluir estados de padding).
    """
    N_espacio = 2 ** n_qubits
    if k_sol == 0:
        return 0, 0.0
    theta = np.arcsin(np.sqrt(k_sol / N_espacio))
    n_iter = max(1, round(np.pi / (4 * theta) - 0.5))
    p_teorico = np.sin((2 * n_iter + 1) * theta) ** 2
    return n_iter, p_teorico


# ──────────────────────────────────────────────────────────────────────────────
# 4. EJECUCIÓN DE UN CASO
# ──────────────────────────────────────────────────────────────────────────────

def ejecutar_caso(n_host, k=3, shots=1024, seed=42, gpu=False, verbose=True):
    """
    Ejecuta Grover para un grafo host de n_host nodos buscando un k-ciclo.
    Reintenta con seed+1 si no hay soluciones.
    """
    for intento in range(5):
        edges = generar_grafo(n_host, k=k, seed=seed + intento)
        candidatos, validos = encontrar_mapeos(n_host, k, edges)
        if validos:
            break
    else:
        print(f"  [Advertencia] No se encontraron {k}-ciclos para N={n_host}")
        return None

    n_candidatos = len(candidatos)
    n_qubits = max(3, int(np.ceil(np.log2(n_candidatos + 1))))
    N_espacio = 2 ** n_qubits
    k_sol = len(validos)

    n_iter, p_teorico = calcular_parametros(n_candidatos, k_sol, n_qubits)

    if verbose:
        print(f"\n── N={n_host} nodos | k={k} | {n_qubits} qubits ─────────────────")
        print(f"  Candidatos P(N,k) : {n_candidatos}")
        print(f"  Espacio cuántico  : 2^{n_qubits} = {N_espacio} estados")
        print(f"  Padding (no usados): {N_espacio - n_candidatos}")
        print(f"  Soluciones k_sol  : {k_sol}  ({k_sol/n_candidatos:.1%} del espacio real)")
        print(f"  Iteraciones Grover: {n_iter}")
        print(f"  Éxito teórico     : {p_teorico:.1%}")
        print(f"  Speedup vs clásico: ~{n_candidatos // max(1, n_iter)}x "
              f"(consultas: {n_candidatos} clásico vs {n_iter} Grover)")

    qc = construir_circuito_escalable(n_qubits, validos, n_iter)

    if gpu:
        try:
            sim = AerSimulator(device='GPU')
            if verbose:
                print(f"  Backend           : GPU (cuStateVec)")
        except Exception:
            sim = AerSimulator()
            if verbose:
                print(f"  Backend           : CPU (GPU no disponible)")
    else:
        sim = AerSimulator()
        if verbose:
            print(f"  Backend           : CPU (AerSimulator statevector)")

    job = sim.run(qc, shots=shots)
    conteos = job.result().get_counts()

    estados_validos_str = {f"{i:0{n_qubits}b}" for i in validos}
    shots_validos = sum(conteos.get(s, 0) for s in estados_validos_str)
    p_empirica = shots_validos / shots

    if verbose:
        print(f"  Éxito empírico    : {p_empirica:.1%}  ({shots_validos}/{shots} shots en válidos)")
        print(f"  Profundidad       : {qc.depth()} capas")
        print(f"  Puertas totales   : {qc.size()}")
        print(f"\n  Top-5 estados medidos:")
        for estado in sorted(conteos, key=lambda s: -conteos[s])[:5]:
            idx = int(estado, 2)
            es_valido = idx in set(validos)
            mapeo = candidatos[idx] if idx < n_candidatos else "(padding)"
            marca = "← FRAUDE ✓" if es_valido else ""
            print(f"    |{estado}⟩: {conteos[estado]:5d} ({conteos[estado]/shots:.1%})  "
                  f"{str(mapeo):16s} {marca}")

    return {
        'n_host': n_host,
        'k': k,
        'n_qubits': n_qubits,
        'N_espacio': N_espacio,
        'n_candidatos': n_candidatos,
        'k_sol': k_sol,
        'n_iter': n_iter,
        'p_teorico': p_teorico,
        'p_empirica': p_empirica,
        'shots_validos': shots_validos,
        'profundidad': qc.depth(),
        'n_puertas': qc.size(),
        'conteos': conteos,
        'candidatos': candidatos,
        'validos': validos,
        'edges': edges,
    }


# ──────────────────────────────────────────────────────────────────────────────
# 5. MODO SWEEP: CURVA DE ESCALADO
# ──────────────────────────────────────────────────────────────────────────────

def sweep_escalado(n_host_values, k=3, shots=512, seed=42, gpu=False):
    """
    Ejecuta Grover para múltiples tamaños y grafica la curva de escalado.
    """
    print("\n" + "=" * 75)
    print("  BARRIDO DE ESCALADO: Clásico vs Grover")
    print("=" * 75)
    encabezado = (f"{'N':>5} {'Qubits':>7} {'Candidatos':>12} {'Sols':>6} "
                  f"{'Clásico (prom)':>16} {'Grover (iters)':>15} {'Speedup':>8} {'Éxito':>7}")
    print(encabezado)
    print("─" * 75)

    resultados = []
    for n_host in n_host_values:
        r = ejecutar_caso(n_host, k, shots, seed, gpu, verbose=False)
        if r is None:
            continue
        speedup = r['n_candidatos'] // max(1, r['n_iter'])
        print(f"{n_host:>5} {r['n_qubits']:>7} {r['n_candidatos']:>12} "
              f"{r['k_sol']:>6} {r['n_candidatos']//2:>16} "
              f"{r['n_iter']:>15} {speedup:>7}x {r['p_empirica']:>6.1%}")
        resultados.append(r)

    if resultados:
        graficar_sweep(resultados, k)
    return resultados


# ──────────────────────────────────────────────────────────────────────────────
# 6. VISUALIZACIONES
# ──────────────────────────────────────────────────────────────────────────────

def graficar_histograma(resultado, shots, output=None):
    """Histograma de probabilidades para un caso concreto."""
    conteos = resultado['conteos']
    n_qubits = resultado['n_qubits']
    validos = resultado['validos']
    n_host = resultado['n_host']
    candidatos = resultado['candidatos']
    n_candidatos = resultado['n_candidatos']

    # Mostrar top-N estados + todos los válidos
    max_barras = min(32, resultado['N_espacio'])
    top_estados = sorted(conteos, key=lambda s: -conteos[s])[:max_barras]
    estados_validos_str = {f"{i:0{n_qubits}b}" for i in validos}
    for s in estados_validos_str:
        if s not in top_estados:
            top_estados.append(s)

    frecuencias = [conteos.get(s, 0) / shots for s in top_estados]
    colores = ['#27ae60' if s in estados_validos_str else '#c0392b'
               for s in top_estados]

    fig, (ax_hist, ax_info) = plt.subplots(1, 2, figsize=(15, 5.5),
                                            gridspec_kw={'width_ratios': [3, 1]})
    fig.suptitle(
        f"Grover — Grafo de {n_host} nodos | {n_qubits} qubits | "
        f"{n_candidatos} candidatos | {resultado['k_sol']} soluciones",
        fontsize=11, fontweight='bold'
    )

    # Panel de histograma
    ax_hist.bar(range(len(top_estados)), frecuencias, color=colores,
                edgecolor='#2c3e50', linewidth=0.5)

    p_unif = 1 / resultado['N_espacio']
    ax_hist.axhline(y=p_unif, color='#7f8c8d', linestyle='--',
                    linewidth=1.3, alpha=0.85)
    ax_hist.text(len(top_estados) * 0.98, p_unif + 0.002,
                 f'Uniforme\n{p_unif:.2%}', fontsize=8, color='#7f8c8d', ha='right')

    ax_hist.set_xticks(range(len(top_estados)))
    ax_hist.set_xticklabels(top_estados, rotation=60, ha='right', fontsize=6.5)
    ax_hist.set_xlabel(f'Estado cuántico (top-{max_barras} + todos los válidos)', fontsize=10)
    ax_hist.set_ylabel('Probabilidad de medición', fontsize=10)
    ax_hist.set_title('Distribución tras iteraciones de Grover', fontsize=10)
    ax_hist.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda y, _: f'{y:.1%}')
    )
    leyenda = [
        mpatches.Patch(color='#27ae60', label='Mapeo válido (anillo de fraude)'),
        mpatches.Patch(color='#c0392b', label='Mapeo inválido'),
        plt.Line2D([0], [0], color='#7f8c8d', linestyle='--',
                   label=f'Uniforme (sin Grover) = {p_unif:.2%}'),
    ]
    ax_hist.legend(handles=leyenda, loc='upper right', fontsize=8.5)

    # Panel de métricas
    ax_info.axis('off')
    metricas = [
        ('Nodos host (N)', str(n_host)),
        ('Tamaño del ciclo (k)', str(resultado['k'])),
        ('', ''),
        ('Candidatos P(N,k)', f"{n_candidatos:,}"),
        ('Espacio cuántico 2ⁿ', f"{resultado['N_espacio']:,}"),
        ('Qubits necesarios', str(n_qubits)),
        ('Soluciones válidas', str(resultado['k_sol'])),
        ('', ''),
        ('Iteraciones Grover', str(resultado['n_iter'])),
        ('Éxito teórico', f"{resultado['p_teorico']:.1%}"),
        ('Éxito empírico', f"{resultado['p_empirica']:.1%}"),
        ('', ''),
        ('Consultas clásicas', f"~{n_candidatos//2:,}"),
        ('Evaluaciones Grover', str(resultado['n_iter'])),
        ('Speedup', f"~{n_candidatos // max(1, resultado['n_iter'])}×"),
        ('', ''),
        ('Profundidad circuito', str(resultado['profundidad'])),
        ('Puertas totales', str(resultado['n_puertas'])),
    ]
    y_pos = 0.97
    for label, valor in metricas:
        if not label:
            y_pos -= 0.035
            continue
        ax_info.text(0.05, y_pos, label + ':', fontsize=8.5, color='#555',
                     transform=ax_info.transAxes, va='top')
        ax_info.text(0.95, y_pos, valor, fontsize=8.5, fontweight='bold',
                     color='#2c3e50', transform=ax_info.transAxes, va='top', ha='right')
        y_pos -= 0.055

    plt.tight_layout()
    if output is None:
        output = f'histograma_N{n_host}_q{n_qubits}.png'
    try:
        plt.savefig(output, dpi=150, bbox_inches='tight')
        print(f"\nHistograma guardado: {output}")
    except Exception as e:
        print(f"Error guardando histograma: {e}")
    plt.close()
    return output


def graficar_sweep(resultados, k):
    """Curva de escalado clásico vs Grover."""
    ns = [r['n_host'] for r in resultados]
    clasico_prom = [r['n_candidatos'] // 2 for r in resultados]
    grover_iters = [r['n_iter'] for r in resultados]
    qubits = [r['n_qubits'] for r in resultados]
    speedups = [c // max(1, g) for c, g in zip(clasico_prom, grover_iters)]

    fig, axes = plt.subplots(1, 3, figsize=(17, 5))
    fig.suptitle(
        f"Escalado: Búsqueda de {k}-ciclo de Fraude — Clásico vs Grover",
        fontsize=12, fontweight='bold'
    )

    # ── Panel 1: consultas (escala log) ──────────────────────────────────
    ax = axes[0]
    ax.semilogy(ns, clasico_prom, 'o-', color='#e74c3c', linewidth=2.5,
                markersize=9, label=f'Clásico   O(P(N,{k})) promedio', zorder=3)
    ax.semilogy(ns, grover_iters, 's--', color='#27ae60', linewidth=2.5,
                markersize=9, label=f'Grover    O(√P(N,{k})) iteraciones', zorder=3)

    # Curva teórica suavizada
    ns_fine = np.linspace(min(ns), max(ns), 100)
    p_clasico_teorico = [np.prod([n - i for i in range(k)]) // 2 for n in ns_fine]
    p_grover_teorico = [int(np.ceil(np.pi / 4 * np.sqrt(np.prod([n - i for i in range(k)]))))
                        for n in ns_fine]
    ax.semilogy(ns_fine, p_clasico_teorico, '-', color='#e74c3c', linewidth=0.8,
                alpha=0.4, zorder=1)
    ax.semilogy(ns_fine, p_grover_teorico, '--', color='#27ae60', linewidth=0.8,
                alpha=0.4, zorder=1)

    ax.set_xlabel('Nodos del grafo host (N)', fontsize=11)
    ax.set_ylabel('Evaluaciones del oráculo', fontsize=11)
    ax.set_title('Consultas requeridas (escala log)', fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.35, which='both')
    ax.set_xticks(ns)

    # ── Panel 2: speedup ─────────────────────────────────────────────────
    ax2 = axes[1]
    barras = ax2.bar(ns, speedups, color='#8e44ad', edgecolor='#6c3483',
                     linewidth=0.7, width=0.6)
    for barra, s in zip(barras, speedups):
        ax2.text(barra.get_x() + barra.get_width() / 2,
                 barra.get_height() + max(speedups) * 0.01,
                 f'{s}×', ha='center', va='bottom', fontsize=10, fontweight='bold',
                 color='#6c3483')
    ax2.set_xlabel('Nodos del grafo host (N)', fontsize=11)
    ax2.set_ylabel('Speedup (consultas clásicas / iteraciones Grover)', fontsize=11)
    ax2.set_title('Aceleración cuántica por tamaño de grafo', fontsize=10)
    ax2.set_xticks(ns)
    ax2.grid(True, alpha=0.35, axis='y')

    # ── Panel 3: qubits ───────────────────────────────────────────────────
    ax3 = axes[2]
    barras3 = ax3.bar(ns, qubits, color='#2980b9', edgecolor='#1a5276',
                      linewidth=0.7, width=0.6)
    for barra, q in zip(barras3, qubits):
        ax3.text(barra.get_x() + barra.get_width() / 2,
                 barra.get_height() + 0.08,
                 str(q), ha='center', va='bottom', fontsize=11, fontweight='bold',
                 color='#1a5276')

    # Curva teórica: qubits = 3 * log2(N) (para k=3, P(N,3)~N³)
    q_teorico = [k * np.log2(n) for n in ns_fine]
    ax3_twin = ax3.twinx()
    ax3_twin.plot(ns_fine, q_teorico, 'k--', linewidth=1.2, alpha=0.5,
                  label=f'Teórico: k·log₂N = {k}·log₂N')
    ax3_twin.set_ylabel('Teórico: k·log₂(N)', fontsize=9, color='#555')
    ax3_twin.tick_params(axis='y', labelcolor='#555')
    ax3_twin.legend(fontsize=8, loc='upper left')

    ax3.set_xlabel('Nodos del grafo host (N)', fontsize=11)
    ax3.set_ylabel('Qubits = ⌈log₂(P(N,k))⌉', fontsize=11)
    ax3.set_title('Qubits necesarios (crece logarítmicamente)', fontsize=10)
    ax3.set_xticks(ns)
    ax3.grid(True, alpha=0.35, axis='y')

    plt.tight_layout()
    output = 'escalado_grover_fraude.png'
    try:
        plt.savefig(output, dpi=150, bbox_inches='tight')
        print(f"\nGráfico de escalado guardado: {output}")
    except Exception as e:
        print(f"Error guardando gráfico: {e}")
    plt.close()


# ──────────────────────────────────────────────────────────────────────────────
# 7. MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Grover escalable: isomorfismo de subgrafos en grafos de transacciones'
    )
    parser.add_argument('--host-nodes', type=int, default=6,
                        help='Nodos en el grafo host (default: 6, máx recomendado: 12)')
    parser.add_argument('--pattern-k', type=int, default=3,
                        help='Tamaño del ciclo de fraude buscado (default: 3)')
    parser.add_argument('--shots', type=int, default=1024,
                        help='Mediciones cuánticas (default: 1024)')
    parser.add_argument('--seed', type=int, default=42,
                        help='Semilla aleatoria (default: 42)')
    parser.add_argument('--gpu', action='store_true',
                        help='Intentar backend GPU (requiere qiskit-aer-gpu)')
    parser.add_argument('--sweep', action='store_true',
                        help='Ejecutar curva de escalado completa N=4..12')
    args = parser.parse_args()

    print("=" * 60)
    print("  ISOMORFISMO DE SUBGRAFOS ESCALABLE — GROVER")
    print("=" * 60)
    print(f"\nCodificación: cada candidato inyectivo f: P → G ocupa 1 estado cuántico")
    print(f"Qubits = ⌈log₂(P(N,{args.pattern_k}))⌉  →  crece O(log N³) = O(3·log N)")

    if args.sweep:
        ns = [4, 5, 6, 7, 8, 9, 10, 11, 12]
        resultados = sweep_escalado(ns, args.pattern_k, args.shots, args.seed, args.gpu)
        if resultados:
            print(f"\nConclusión: para N=4→12, las consultas clásicas crecen de "
                  f"{resultados[0]['n_candidatos']//2} a {resultados[-1]['n_candidatos']//2} "
                  f"(factor {resultados[-1]['n_candidatos']//resultados[0]['n_candidatos']}x), "
                  f"mientras Grover pasa de {resultados[0]['n_iter']} a "
                  f"{resultados[-1]['n_iter']} iteraciones.")
    else:
        print(f"\nCaso: N={args.host_nodes} nodos, buscando {args.pattern_k}-ciclo")
        r = ejecutar_caso(
            args.host_nodes, args.pattern_k, args.shots,
            args.seed, args.gpu, verbose=True
        )
        if r:
            graficar_histograma(r, args.shots)
            print(f"\n{'─'*55}")
            print(f"RESUMEN FINAL")
            print(f"{'─'*55}")
            print(f"  Anillo de fraude encontrado: nodos que forman "
                  f"un {args.pattern_k}-ciclo en el grafo de {args.host_nodes} cuentas")
            print(f"  Speedup cuántico demostrado: {r['n_candidatos']} consultas "
                  f"clásicas vs {r['n_iter']} evaluaciones de Grover")
            print(f"  Factor: ~{r['n_candidatos'] // max(1, r['n_iter'])}× menos consultas")


if __name__ == '__main__':
    main()
