# Planteamiento del Problema: Isomorfismo de Subgrafos en Grafos Masivos

> **Contexto académico:** EMI307 — Especificación de Requerimientos (Módulo 2)  
> Universidad de La Frontera · Magíster en Ingeniería Informática  
> Docente: Dr. Samuel Sepúlveda

---

## 1. Definición Formal del Problema

### 1.1 Isomorfismo de Subgrafos

Dados dos grafos dirigidos:
- **Grafo host** G = (V_G, E_G): el grafo grande (ej. millones de transacciones bancarias)
- **Grafo patrón** P = (V_P, E_P): el subgrafo buscado (ej. un ciclo de fraude de 3 nodos)

El problema de **isomorfismo de subgrafos** consiste en encontrar una función inyectiva f: V_P → V_G tal que:

```
∀(u,v) ∈ E_P  →  (f(u), f(v)) ∈ E_G
```

Es decir: cada arista del patrón debe existir en el grafo host bajo el mapeo f.

### 1.2 Instancia Concreta: Fraude Circular (Circular Trading)

En el dominio de Anti-Lavado de Dinero (AML), el "fraude circular" es un esquema donde fondos ilegales circulan entre múltiples cuentas antes de regresar al origen, dificultando el rastreo.

**Patrón P buscado:** ciclo dirigido de 3 nodos

```
A ──→ B
↑       ↓
└── C ←─┘

P tiene aristas: (A→B), (B→C), (C→A)
```

**Grafo host G** (ejemplo de 4 cuentas bancarias):

```
     0 ────→ 1
     ↑  ↘    ↓
     │   3   2
     └───────┘
         ↑
    (no forma ciclo)

Aristas: (0→1), (1→2), (2→0), (0→3)
```

**Solución buscada:** todas las funciones f: {A,B,C} → {0,1,2,3} que satisfacen el patrón.

En este caso: f = {A→0, B→1, C→2} y sus rotaciones, representando el ciclo `0 → 1 → 2 → 0`.

---

## 2. Por Qué el Software Clásico No Escala

### 2.1 Complejidad NP-Completa

El problema de isomorfismo de subgrafos fue demostrado NP-Completo por Ullmann (1976). Esto implica que **no existe algoritmo clásico polinomial conocido** para el caso general.

Para un grafo host con N nodos y un patrón de k nodos, el número de mapeos inyectivos posibles a evaluar es:

```
|Candidatos| = N! / (N-k)!  =  N × (N-1) × ... × (N-k+1)
```

Para N=1.000.000 nodos y k=5 (patrón de 5 nodos):

```
Candidatos ≈ 10^30  →  imposible por fuerza bruta
```

### 2.2 El Muro Algorítmico en la Práctica

Los algoritmos clásicos de state-of-the-art (VF2, QuickSI, TurboISO) usan heurísticas de poda para reducir el espacio de búsqueda, pero en el peor caso siguen siendo exponenciales. Los síntomas en producción son:

| Síntoma | Causa |
|---------|-------|
| Latencia > 30 segundos en consultas profundas | Explosión de ramas en DFS/BFS |
| Saturación de RAM | Almacenamiento de estados intermedios del árbol de búsqueda |
| Timeouts en Neo4j para traversiones > 5 saltos | Sin acotamiento efectivo del espacio de búsqueda |
| Imposibilidad de análisis en tiempo real | El costo crece más rápido que el hardware |

### 2.3 Cuantificación del Cuello de Botella

Para una consulta de detección de anillos de fraude en un grafo bancario con:
- 10 millones de cuentas (nodos)
- 50 millones de transacciones (aristas)
- Patrón: ciclo de 3 nodos

Un motor clásico (Neo4j + algoritmo VF2) debe explorar un árbol de profundidad 3 con factor de ramificación O(N). El tiempo de peor caso es **O(N³)**, con N=10^7 → **10^21 operaciones**. Incluso con heurísticas que reducen esto en órdenes de magnitud, el análisis completo de grafos densos tarda días, no milisegundos.

---

## 3. Solución con Hardware Cuántico: Algoritmo de Grover

### 3.1 Principio Fundamental

El Algoritmo de Grover (1996) resuelve el problema de **búsqueda no estructurada** en un espacio de N elementos con exactamente O(√N) evaluaciones del oráculo, comparado con O(N) clásico.

Para el isomorfismo de subgrafos, codificamos cada mapeo candidato f como un estado cuántico |f⟩. El registro cuántico de n qubits puede representar 2^n candidatos en **superposición simultánea**:

```
|ψ₀⟩ = (1/√N) × Σ|f⟩    (todos los candidatos a la vez)
```

### 3.2 Estructura del Algoritmo

El circuito de Grover tiene tres componentes:

#### Inicialización
```
|0...0⟩ ──[H⊗n]──→ superposición uniforme sobre todos los candidatos
```

#### Oráculo (O)
Función que identifica mapeos válidos y aplica un cambio de fase:
```
O|f⟩ = { -|f⟩   si f es un isomorfismo válido (verifica todas las aristas del patrón)
        {  |f⟩   en caso contrario
```

El oráculo verifica matemáticamente las restricciones de adyacencia usando la matriz Laplaciana del subgrafo.

#### Difusor de Grover (D)
Reflexión respecto a la media de amplitudes. Aumenta la amplitud de estados marcados y disminuye los no marcados:
```
D = 2|ψ₀⟩⟨ψ₀| - I
```

#### Iteraciones
Después de k ≈ (π/4)√(N/t) iteraciones (donde t = número de soluciones), la probabilidad de medir un isomorfismo válido supera el 90%.

### 3.3 Complejidad y Ventaja

| Métrica | Clásico | Cuántico (Grover) |
|---------|---------|-------------------|
| Peor caso | O(N) consultas | O(√N) consultas |
| Con N=8 candidatos | 8 consultas | ~2.8 consultas |
| Con N=1024 candidatos | 1024 consultas | ~32 consultas |
| Con N=10^6 candidatos | 10^6 consultas | ~1000 consultas |

La aceleración es cuadrática: **búsqueda en 10^6 elementos con solo 1000 evaluaciones**.

### 3.4 Codificación del Problema

El paso crítico es la **Capa de Traducción**: transformar el subgrafo candidato en un circuito cuántico.

```
1. Neo4j extrae subgrafo candidato (matriz de adyacencia)
         ↓
2. Capa de Traducción calcula la Matriz Laplaciana L = D - A
         ↓
3. Se construye el operador unitario U = e^(iLt)
         ↓
4. Se transpila a puertas cuánticas nativas del hardware
         ↓
5. Oráculo verifica: ¿el mapeo f satisface todas las aristas del patrón?
```

Número de qubits necesarios para codificar N candidatos:

```
n_qubits = ⌈log₂(|V_P|! / (|V_G| - |V_P|)!)⌉
```

---

## 4. Arquitectura Híbrida Clásico-Cuántica

La solución no reemplaza Neo4j. El sistema cuántico actúa como **coprocesador asíncrono** para consultas de alta profundidad.

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA CLÁSICA                              │
│                                                             │
│   Usuario ──→ API REST/gRPC ──→ Orquestador                 │
│                                     │                       │
│                          ┌──────────┴──────────┐            │
│                          ↓                     ↓            │
│                   Consulta simple        Consulta profunda   │
│                   (≤ 3 saltos)           (> 3 saltos)        │
│                          ↓                     ↓            │
│                      Neo4j               Extracción del     │
│                    responde              subgrafo candidato  │
└─────────────────────────────────────────────────────────────┘
                                               ↓
┌─────────────────────────────────────────────────────────────┐
│               CAPA DE TRADUCCIÓN (Módulo QSRE)              │
│                                                             │
│  Subgrafo ──→ Matriz Laplaciana ──→ Circuito Cuántico       │
│              n_qubits = ⌈log₂(candidatos)⌉                 │
│                                                             │
│  [Timeout 500ms]: si supera límite → fallback clásico local  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              COPROCESADOR CUÁNTICO                          │
│                                                             │
│  Opción A: QPU en nube (IBM Quantum, Amazon Braket)         │
│  Opción B: Simulador GPU local (AerSimulator + cuStateVec)  │
│  Opción C: Simulador CPU (AerSimulator, para desarrollo)    │
│                                                             │
│  Grover: superposición → oráculo → difusor → medición       │
│                          ↓                                  │
│           Vector de probabilidades (amplitudes)              │
└─────────────────────────────────────────────────────────────┘
                          ↓
                 Post-proceso clásico:
                 extraer top-k estados,
                 verificar y devolver al usuario
```

### Requerimientos QSRE

| ID | Tipo | Descripción |
|----|------|-------------|
| REQ-CLA-01 | Funcional | Neo4j gestiona ingesta, índices y consultas transaccionales estándar |
| REQ-CLA-02 | Funcional | API recibe consultas y devuelve resultados renderizados |
| REQ-HIB-01 | Funcional | Extracción del subgrafo candidato y generación de Matriz Laplaciana en < T ms |
| REQ-HIB-02 | Funcional | Transpilación de la Laplaciana a puertas cuánticas compatibles con el hardware objetivo |
| REQ-HIB-03 | Funcional | Si latencia de compilación o cola cuántica > 500 ms → derivar a solver heurístico clásico |
| REQ-CUA-01 | Funcional | Ejecución del circuito por un número definido de shots estadísticos |
| RNF-01 | No Funcional | Sobrecosto de I/O (QRAM) no debe superar la ganancia algorítmica esperada |
| RNF-02 | No Funcional | Sistema debe tolerar altas tasas de error NISQ; profundidad máxima de circuito acotada |
| RNF-03 | No Funcional | Acceso a QPU nube solo cuando la heurística clásica determina que el subgrafo es demasiado denso |

---

## 5. Limitaciones Actuales (Era NISQ)

### 5.1 Cuello de Botella QRAM

El mayor obstáculo no es el algoritmo sino la **carga de datos**: inicializar un estado cuántico que codifica la Matriz de Adyacencia requiere O(N) operaciones clásicas (preparación del estado), lo que puede neutralizar la ventaja de O(√N) en la búsqueda.

Para grafos con millones de nodos, este cuello de botella hace que el sistema cuántico sea actualmente más lento end-to-end que un solver clásico optimizado.

### 5.2 Restricciones de Hardware NISQ

| Limitación | Impacto |
|-----------|---------|
| Qubits ruidosos (error ~0.1-1% por puerta) | Circuitos profundos colapsan por decoherencia |
| Qubits lógicos disponibles (< 1000) | Solo grafos pequeños (< ~512 candidatos) |
| Tiempos de coherencia (microsegundos) | Limita el número de iteraciones de Grover |
| Colas de espera en QPU nube | Latencia de minutos, inaceptable para tiempo real |

### 5.3 Naturaleza Estocástica

Los resultados son probabilísticos. Se requieren múltiples shots (típicamente 1024-4096) para obtener una distribución estadísticamente confiable, lo que multiplica el tiempo de ejecución.

---

## 6. Análisis de Factibilidad (QSRE)

### Veredicto: **Parcialmente Factible / Exploratorio**

| Dimensión | Estado | Notas |
|-----------|--------|-------|
| Correctitud algorítmica | ✓ Demostrada | Grover provee ventaja cuadrática teórica |
| Arquitectura de integración | ✓ Sólida | Delegación aislada protege el sistema productivo |
| Capa de traducción | ✓ Validada | Prueba de concepto implementada (ver `demo/`) |
| Hardware actual (NISQ) | ✗ Limitante | Qubits insuficientes para grafos de producción |
| Cuello de botella QRAM | ✗ Sin solución madura | Neutraliza la ventaja en grafos masivos |
| Disponibilidad operativa | ⚠ Condicional | Fallback clásico garantiza uptime |

### Recomendación

1. **Corto plazo:** Implementar la arquitectura híbrida con simuladores tensoriales locales (GPU + AerSimulator). Usar para subgrafos candidatos de densidad crítica extraídos por Neo4j.
2. **Medio plazo:** Migrar a QPU cuando los dispositivos superen ~1000 qubits lógicos con corrección de errores (FTQC).
3. **No recomendado:** Reemplazar el motor de base de datos clásico. El valor está en la delegación selectiva, no en la sustitución.

---

## 7. Prueba de Concepto: Toy Problem

La implementación en `demo/grover_subgraph_search.py` modela el siguiente caso:

- **Host G:** 4 cuentas {0,1,2,3}, aristas: (0→1), (1→2), (2→0), (0→3)
- **Patrón P:** ciclo dirigido de 3 nodos (anillo de fraude)
- **Espacio de búsqueda:** 8 mapeos candidatos (3 qubits)
- **Soluciones:** 3 estados válidos (rotaciones del ciclo 0→1→2→0)
- **Iteraciones Grover:** 1 (óptimo para k=3, N=8)
- **Probabilidad de éxito teórica:** 84.8% por iteración
- **Backend:** Qiskit AerSimulator (CPU por defecto, GPU opcional)

El script demuestra empíricamente que el difusor de Grover amplifica los 3 estados válidos desde 12.5% (distribución uniforme) hasta ~28% cada uno, mientras los 5 estados inválidos caen a ~1.5%.
