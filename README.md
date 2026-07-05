# Búsqueda Cuántica de Subgrafos — Detección de Fraude Circular

Trabajo de Cierre — Módulo 2, EMI307: Especificación de Requerimientos  
**Universidad de La Frontera · Magíster en Ingeniería Informática**

| Campo | Valor |
|-------|-------|
| Estudiante | Sebastián Eduardo Puentes Prieto |
| Docente | Dr. Samuel Sepúlveda |
| Fecha de entrega | 20/05/2026 |

---

## Resumen

Este repositorio contiene el análisis de factibilidad para incorporar computación cuántica como coprocesador en bases de datos de grafos empresariales, acotado específicamente al problema de **isomorfismo de subgrafos**: encontrar un patrón estructural (anillo de fraude circular) dentro de un grafo masivo de transacciones financieras.

El enfoque aplica los principios de **Ingeniería de Requisitos para Software Cuántico (QSRE)** y demuestra empíricamente la viabilidad de la capa de traducción clásico-cuántica mediante una implementación ejecutable con Qiskit.

---

## Problema Central

Dado un grafo de transacciones G con millones de nodos y un patrón P (ciclo dirigido de 3 nodos = "fraude circular"), encontrar todas las ocurrencias de P en G.

- **Complejidad clásica:** NP-Completo — O(2^N) en el peor caso (Ullmann, 1976)
- **Complejidad cuántica (Grover):** O(√N) — reducción cuadrática demostrada

---

## Archivos

```
├── README.md              ← este archivo
├── PROBLEMA.md            ← planteamiento formal, análisis clásico vs cuántico,
│                             arquitectura híbrida y factibilidad QSRE
├── REFERENCIAS.md         ← referencias verificadas con notas sobre fuentes corregidas
└── demo/
    ├── grover_subgraph_search.py   ← demo original: 4 nodos, 3 qubits, caso mínimo
    ├── grover_subgraph_scaled.py   ← versión escalable: N nodos parametrizable, sweep N=4..12
    └── requirements.txt            ← dependencias Python
```

---

## Ejecución Rápida

```bash
cd demo
pip install -r requirements.txt

# Demo mínimo: 4 nodos, 3 qubits (original)
python grover_subgraph_search.py

# Versión escalable: N nodos parametrizables
python grover_subgraph_scaled.py --host-nodes 6    # 7 qubits, 24x speedup
python grover_subgraph_scaled.py --host-nodes 8    # 9 qubits, 67x speedup
python grover_subgraph_scaled.py --host-nodes 12   # 11 qubits, 264x speedup

# Curva de escalado completa N=4..12 (genera escalado_grover_fraude.png)
python grover_subgraph_scaled.py --sweep

# Con GPU (requiere qiskit-aer-gpu)
python grover_subgraph_scaled.py --host-nodes 10 --gpu
```

El script original imprime el análisis en consola y genera `resultados_grover_fraude.png` con el histograma de probabilidades y la visualización del grafo de transacciones. La versión escalable genera `histograma_N{N}_q{qubits}.png` y `grafo_host_N{N}.png` (grafo de transacciones con el anillo de fraude resaltado) por cada ejecución, y `escalado_grover_fraude.png` con la curva de speedup al usar `--sweep`. `circuito_grover.png` es un diagrama de referencia del circuito de Grover (3 qubits, 1 iteración) generado con `qc.draw('mpl')`.

Ver `GUIONES.md` → sección "Material de apoyo" para el guion detallado de cómo leer cada uno de estos gráficos (grafos, histogramas y el circuito).

---

## Resultado Esperado

### Demo mínimo (4 nodos, 3 qubits)

```
=== BÚSQUEDA CUÁNTICA (Algoritmo de Grover) ===
Qubits: 3  |  Estados: N=8  |  Soluciones: k=3
Iteraciones de Grover óptimas: 1
Probabilidad teórica de éxito: ~84.8%
Complejidad cuántica: O(√8) ≈ 2.83 consultas
Complejidad clásica:  O(N)  = 8 consultas (peor caso)

=== RESULTADOS DE LA MEDICIÓN ===
  |000⟩ = (0,1,2): ~580 shots  (28.3%)  ← ANILLO DE FRAUDE ✓
  |101⟩ = (1,2,0): ~579 shots  (28.3%)  ← ANILLO DE FRAUDE ✓
  |110⟩ = (2,0,1): ~573 shots  (28.0%)  ← ANILLO DE FRAUDE ✓
  |001⟩ = (0,1,3):  ~30 shots   (1.5%)
  ...
```

Los 3 estados amplificados son rotaciones del mismo ciclo único `0 → 1 → 2 → 0`.

### Curva de escalado (sweep N=4..12, patrón k=3)

La codificación logarítmica (⌈log₂ P(N,k)⌉ qubits para P(N,k) mapeos inyectivos posibles)
hace que el número de qubits crezca muy lentamente frente al espacio de búsqueda clásico:

| N (nodos host) | Qubits | Candidatos P(N,3) | Speedup (N/√N) | Éxito empírico |
|---:|---:|---:|---:|---:|
| 4  | 5  | 24   | 12×   | 100% |
| 6  | 7  | 120  | 24×   | ~99% |
| 8  | 9  | 336  | 67×   | 99%  |
| 10 | 10 | 720  | 180×  | 99%  |
| 12 | 11 | 1320 | 264×  | 100% |

El crecimiento de qubits es logarítmico (~3·log₂N) mientras que la ventaja cuántica
(speedup) crece con √N, ilustrando la separación asintótica entre el enfoque clásico
de fuerza bruta y la búsqueda amplificada por Grover.

---

## Veredicto QSRE

**Parcialmente Factible / Exploratorio** en el estado actual de la tecnología (era NISQ).

La ventaja algorítmica existe y la arquitectura de delegación aislada es sólida. La limitación principal es el cuello de botella de carga de datos clásicos al espacio cuántico (problema QRAM) para grafos de escala de producción. La recomendación es mantener el esquema híbrido con simuladores tensoriales locales mientras madura el hardware cuántico tolerante a fallos (FTQC).
