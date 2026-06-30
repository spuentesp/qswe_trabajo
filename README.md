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
    ├── grover_subgraph_search.py   ← script ejecutable (Qiskit + AerSimulator)
    └── requirements.txt            ← dependencias Python
```

---

## Ejecución Rápida

```bash
cd demo
pip install -r requirements.txt

# Simulación en CPU (por defecto)
python grover_subgraph_search.py

# Con más shots para mejor estadística
python grover_subgraph_search.py --shots 4096

# Intentar aceleración GPU (requiere qiskit-aer-gpu instalado)
python grover_subgraph_search.py --gpu
```

El script imprime el análisis en consola y genera `resultados_grover_fraude.png` con el histograma de probabilidades y la visualización del grafo de transacciones.

---

## Resultado Esperado

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

---

## Veredicto QSRE

**Parcialmente Factible / Exploratorio** en el estado actual de la tecnología (era NISQ).

La ventaja algorítmica existe y la arquitectura de delegación aislada es sólida. La limitación principal es el cuello de botella de carga de datos clásicos al espacio cuántico (problema QRAM) para grafos de escala de producción. La recomendación es mantener el esquema híbrido con simuladores tensoriales locales mientras madura el hardware cuántico tolerante a fallos (FTQC).
