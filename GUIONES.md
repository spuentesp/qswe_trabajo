# Guiones de Presentación — Diapositiva por Diapositiva

> Trabajo de Cierre — EMI307: Especificación de Requerimientos  
> Universidad de La Frontera · Magíster en Ingeniería Informática  
> Alumno: Sebastián Eduardo Puentes Prieto · Docente: Dr. Samuel Sepúlveda  
> Mayo 2026

Cada guion está pensado para una duración aproximada de **1,5 a 2,5 minutos** por diapositiva
(~30 minutos totales + 5–10 min de preguntas). Incluye **qué decir**, **qué señalar**, **pausas
sugeridas** y **transiciones** entre diapositivas.

Convención:
- **[SEÑALAR]** indica un elemento visual que debe ser apuntado o destacado en pantalla.
- **[PAUSA 2s]** marca una respiración intencional.
- **[TRANSICIÓN]** indica el puente hacia la siguiente diapositiva.

---

## Diapositiva 1 — Portada

**Objetivo de la diapositiva:** Dar identidad al trabajo, equipo y contexto académico.

**Guion:**

> Buenas tardes. Mi nombre es Sebastián Puentes Prieto, estudiante del Magíster en
> Ingeniería Informática de la Universidad de La Frontera. Hoy les presento mi trabajo de
> cierre del Módulo 2 de la asignatura EMI307 — Especificación de Requerimientos,
> dictada por el Dr. Samuel Sepúlveda.
>
> El título del trabajo es: **"Búsqueda Cuántica de Subgrafos: Detección de Fraude
> Circular"**. La pregunta de fondo es si es factible —hoy, en 2026— incorporar
> computación cuántica como coprocesador de una base de datos de grafos empresarial,
> acotado a un problema computacional concreto: encontrar patrones de fraude circular en
> grafos transaccionales de millones de nodos.
>
> A lo largo de los próximos 30 minutos recorreremos once bloques: partiremos por el
> problema de negocio, definiremos formalmente el problema computacional, veremos por qué
> es NP-Completo, qué ofrece lo cuántico, cómo se traduce esto a una arquitectura de
> software concreta, los resultados empíricos con Qiskit, las restricciones del hardware
> actual, y cerraremos con el veredicto QSRE y las referencias verificadas.
>
> ¿Me acompañan?

**[SEÑALAR]** el título, el subtítulo y el bloque de autor. **[TRANSICIÓN]** Comencemos
viendo el recorrido de la presentación. *(Avanzar a D2)*

---

## Diapositiva 2 — Qué vamos a ver

**Objetivo:** Dar al oyente un mapa mental de la presentación.

**Guion:**

> Esta es la hoja de ruta. Dividí el trabajo en **once bloques** numerados del 00 al 10
> para que sea fácil seguirlo y también para que ustedes, si tienen que referirse a una
> sección concreta durante las preguntas, puedan localizarla de inmediato.
>
> **[SEÑALAR]** la columna izquierda: bloques 00 a 05 — la mitad teórica del trabajo.
> Cubren el problema de negocio, la definición formal de isomorfismo de subgrafos, la
> complejidad NP-Completa, la ventaja cuántica y la arquitectura de la solución.
>
> **[SEÑALAR]** la columna derecha: bloques 06 a 10 — la mitad empírica y de cierre.
> Metodología de prueba con Qiskit, la prueba de concepto con 4 nodos, el barrido de
> escalado hasta 12 nodos, las limitaciones actuales del hardware NISQ, y el veredicto
> final de factibilidad junto con las referencias bibliográficas.
>
> **[PAUSA 2s]**
>
> Una cosa que quiero dejar clara desde ya: este trabajo **no propone reemplazar** los
> motores de bases de datos clásicos. La propuesta es una **arquitectura híbrida** donde
> el componente cuántico actúa como coprocesador asíncrono para consultas profundas, no
> para reemplazar a Neo4j.
>
> **[TRANSICIÓN]** Empecemos por el bloque cero: el problema de negocio que motiva
> todo. *(Avanzar a D3)*

---

## Diapositiva 3 — Por qué nos importa este problema

**Objetivo:** Anclar el problema en un dominio de aplicación real, con cifras.

**Guion:**

> ¿Por qué nos importa este problema? Porque el **lavado de activos** es uno de los
> delitos financieros más difíciles de perseguir y, a la vez, de mayor impacto económico.
> La Oficina de las Naciones Unidas contra la Droga y el Delito — la **UNODC** —
> estima que el lavado de dinero representa entre el **2% y el 5% del PIB mundial
> cada año**, es decir, entre **800 mil millones y 2 billones de dólares**.
>
> **[SEÑALAR]** la card de la derecha, "Qué pasa hoy en la práctica".
>
> En Chile, la **UAF** — Unidad de Análisis Financiero, creada por la Ley 19.913 —
> exige a los bancos reportar operaciones sospechosas en plazos cortos. El estándar
> internacional lo marca el **GAFI / FATF** con sus 40 recomendaciones.
>
> Ahora bien, ¿qué pasa hoy en la industria? El motor de reglas tradicional — que es
> con lo que trabaja un banco típico — **degrada** cuando le pides buscar ciclos de 3 o
> más saltos sobre grafos de millones de cuentas. Y eso lo vemos en producción: las
> investigaciones manuales toman horas por caso, hay **miles de casos** acumulados al
> mes, las reglas rígidas generan más del **90% de falsos positivos**, y la ventana
> de detección se mide en **días, no en minutos**.
>
> **[PAUSA 2s]**
>
> Esa demora es la que aprovecharon los esquemas de "fraude circular": el dinero rota
> por varias cuentas y termina volviendo al origen, intentando borrar el rastro antes de
> salir del sistema financiero formal.
>
> **[TRANSICIÓN]** Bien — ese es el problema de negocio. Ahora definamos el problema
> computacional que esto esconde. *(Avanzar a D4)*

---

## Diapositiva 4 — El problema, explicado

**Objetivo:** Traducir el problema de negocio a un problema formal de teoría de grafos.

**Guion:**

> El problema computacional detrás del fraude circular se llama **isomorfismo de
> subgrafos**. Formalmente, dados dos grafos dirigidos: el **grafo host** **G**, que
> contiene todos los nodos del banco, millones de cuentas; y el **grafo patrón**
> **P**, que es el anillo de fraude que estamos buscando — típicamente un ciclo
> dirigido de 3 nodos.
>
> Buscamos una función **inyectiva** **f** que mapee cada nodo del patrón a un nodo
> del host, con la condición fundamental: **[SEÑALAR la fórmula central]** *cada
> arista del patrón debe existir en el host bajo ese mapeo*.
>
> Esta es la definición formal que importó al trabajo. Es la misma independientemente
> del dominio: detección de fraude, análisis de redes sociales, bioinformática,
> coincidencia de patrones en imágenes.
>
> **[SEÑALAR]** el patrón de la derecha: **A → B → C → A**. Tres cuentas, tres
> transferencias formando un anillo. Eso es **fraude circular**. Estamos buscando todas
> las tripletas de cuentas del banco que materialicen exactamente ese patrón.
>
> **[PAUSA 2s]**
>
> Un detalle importante: el número de mapeos candidatos a evaluar crece **factorialmente**
> con el tamaño del grafo host. Eso, en N grande, es lo que hace que el problema sea
> intratable por fuerza bruta. Veamos por qué.
>
> **[TRANSICIÓN]** *(Avanzar a D5)*

---

## Diapositiva 5 — Qué es un problema NP-Completo

**Objetivo:** Justificar formalmente la imposibilidad de un algoritmo clásico polinomial.

**Guion:**

> El isomorfismo de subgrafos es un **problema de decisión**: ¿existe un mapeo que
> satisfaga el patrón? Y ocurre algo curioso: **verificar** una solución candidata es
> rápido — basta con comprobar las aristas del patrón, eso toma **O(k)** para un
> patrón de k aristas. Pero **encontrar** esa solución requiere explorar el espacio
> completo de mapeos.
>
> Esa asimetría — verificar rápido, resolver presumiblemente exponencial — es la
> definición misma de la **clase NP**.
>
> **[SEÑALAR]** la card "La prueba de Ullmann (1976)".
>
> En 1976, **Julian Ullmann** demostró la **NP-Completitud** del problema mediante
> una reducción polinomial desde el problema de la **clique** — que también es
> NP-Completo. Toda instancia de clique se puede transformar en una instancia de
> isomorfismo de subgrafos sin soplar el presupuesto polinomial.
>
> **[PAUSA 2s]**
>
> La consecuencia práctica es demoledora: si alguien descubriera un algoritmo clásico
> polinomial para este problema, **resolvería todo NP en tiempo polinomial** —
> probaría que **P = NP**. Y eso es algo que 50 años de investigación no han podido
> ni demostrar ni refutar.
>
> La industria no espera esa prueba. Lo que hace hoy es usar **heurísticas** — VF2,
> poda por grado — que en promedio funcionan razonablemente pero degradan en el peor
> caso. **Y el peor caso es exactamente el que más nos importa: los anillos de
> fraude bien disimulados**, los que están pensados para evadir reglas simples.
>
> **[TRANSICIÓN]** Veamos ahora qué tan rápido cae la heurística clásica cuando
> crecemos el grafo. *(Avanzar a D6)*

---

## Diapositiva 6 — Cuántas opciones hay que revisar

**Objetivo:** Cuantificar el cuello de botella clásico con cifras.

**Guion:**

> Bajemos a tierra. Para el caso concreto del patrón de fraude circular de **3 nodos**
> sobre un host de **N** cuentas, el número de mapeos candidatos a evaluar es la
> permutación P(N, k) = **N! / (N − k)!**.
>
> **[SEÑALAR]** la fórmula grande. Hagamos una cuenta rápida: si el host tiene
> **un millón** de cuentas y el patrón tiene **5 nodos** — pensando ya en patrones más
> complejos, anillos de 5 cuentas, no solo 3 — el espacio de búsqueda es
> aproximadamente **10 a la 30** mapeos candidatos. Eso es **imposible** de evaluar
> por fuerza bruta, literalmente más que el número de átomos en un gramo de materia.
>
> **[SEÑALAR]** la card "Síntomas en producción".
>
> ¿Qué pasa hoy en una implementación clásica de esto? Tomemos una escala realista:
> un banco con **10 millones de cuentas** y **50 millones de transacciones**,
> buscando anillos de 3 nodos. Si usamos un grafo de propiedades como **Neo4j** con
> el algoritmo **VF2**, el peor caso es **O(N³)**, es decir **10 a la 21
> operaciones**. Y los síntomas que ven los ingenieros en producción son exactamente
> los que aparecen listados: latencias de más de 30 segundos, **saturación de RAM**
> porque el árbol de búsqueda explota, **timeouts** cuando Neo4j intenta traversiones
> de más de 5 saltos, y por tanto **no hay análisis en tiempo real** del fraude.
>
> **[PAUSA 2s]**
>
> Entonces la pregunta natural es: ¿qué tiene el cómputo cuántico que pueda romper
> este techo?
>
> **[TRANSICIÓN]** *(Avanzar a D7)*

---

## Diapositiva 7 — Qué cambia con lo cuántico

**Objetivo:** Diferenciar lo que es propaganda cuántica de lo que es realmente nuevo.

**Guion:**

> Quiero detenerme aquí para aclarar algo importante, porque es una confusión que se
> repite en divulgación. **[SEÑALAR]** la card izquierda, cómputo clásico:
> una computadora clásica evalúa los candidatos **uno a la vez**, o como mucho en
> paralelo si tiene N procesadores físicos. Representar el espacio completo de N
> candidatos requiere **N registros** distintos en algún momento.
>
> **[SEÑALAR]** la card derecha, cómputo cuántico.
>
> Lo que cambia con lo cuántico es que podemos codificar **N candidatos** en un
> registro cuántico de **logaritmo en base 2 de N qubits**. Es una estructura
> exponencial ocupando espacio logarítmico. El **oráculo** aplica una única operación
> unitaria sobre todos los estados a la vez — y aquí viene la aclaración importante:
> esto **no es probar todo en paralelo mágicamente**. Lo que hace el oráculo es
> **invertir la fase** de los estados que satisfacen la condición. Después, el
> **difusor de Grover** usa **interferencia** de amplitudes para amplificar las
> soluciones válidas y cancelar el resto, sin enumeración explícita.
>
> **[SEÑALAR]** la nota al pie.
>
> En resumen: Grover **no** evalúa todo el espacio de golpe como una búsqueda
> paralela ilimitada; usa interferencia cuántica para **sesgar la probabilidad de
> medición** hacia las soluciones. La consecuencia neta es la complejidad
> **O(√N)** consultas en lugar de **O(N)**.
>
> **[TRANSICIÓN]** Veamos cómo se materializa esto en el circuito concreto de
> Grover. *(Avanzar a D8)*

---

## Diapositiva 8 — El algoritmo de Grover

**Objetivo:** Describir los tres componentes del circuito cuántico.

**Guion:**

> El algoritmo que vamos a usar fue propuesto por **Lov Grover en 1996** en el
> contexto de búsqueda no estructurada en bases de datos. La ganancia — y esto es lo
> que lo vuelve interesante — es que baja la complejidad de **O(N) a O(√N)**, una
> **aceleración cuadrática**.
>
> **[SEÑALAR]** la fórmula: |ψ₀⟩ = (1/√N) Σ |f⟩.
>
> Cada mapeo candidato **f** se codifica como un estado cuántico |f⟩. Con **n** qubits,
> podemos representar **2 a la n** candidatos simultáneamente en lo que se llama una
> **superposición**. Si inicializamos el sistema con **n compuertas Hadamard** en
> paralelo, obtenemos una superposición **uniforme** sobre todo el espacio de
> búsqueda.
>
> **[SEÑALAR]** la card de los tres componentes:
>
> 1. La **inicialización** crea la superposición uniforme mediante Hadamards.
> 2. El **oráculo O** es una función que invierte la fase — cambia el signo — de los
>    estados cuyo mapeo es un isomorfismo válido. En el caso de nuestro problema,
>    verifica las restricciones de adyacencia usando la **Matriz Laplaciana** del
>    subgrafo.
> 3. El **difusor D** es una reflexión respecto a la media de amplitudes. Aumenta
>    la amplitud de los estados marcados por el oráculo y disminuye el resto.
>
> **[PAUSA 2s]**
>
> La magia es que **oráculo + difusor** se aplica de forma iterada — se repite
> aproximadamente **(π/4) · √(N/t)** veces, donde **t** es el número de soluciones.
> Tras esas iteraciones, la probabilidad de medir un isomorfismo válido supera el
> **90%**. Esa es la ventaja cuadrática.
>
> **[TRANSICIÓN]** Veamos las cifras concretas en una tabla comparativa.
> *(Avanzar a D9)*

---

## Diapositiva 9 — Cuánto más rápido es

**Objetivo:** Mostrar el speedup con cifras concretas.

**Guion:**

> Esta tabla es la fotografía de la ventaja. **[SEÑALAR]** la fila del peor caso:
> la columna clásica dice **O(N)** consultas, la cuántica dice **O(√N)**.
>
> Para que se entienda con números pequeños: con **N = 8 candidatos**, en el peor
> caso clásico necesitamos **8 evaluaciones**; con Grover, **2,83 evaluaciones**. Ya
> acá la diferencia se nota.
>
> Pero la ventaja crece con N. Con **N = 1.024 candidatos** — un caso mediano —
> clásico: **1.024 consultas**; cuántico: **~32**. Y cuando llegamos al caso
> interesante, **N = 10⁶ candidatos**, el clásico necesita **un millón de
> evaluaciones**, y el algoritmo de Grover solo necesita aproximadamente **mil**.
>
> **[SEÑALAR]** el número grande en rojo: **1.000**.
>
> Búsqueda en un millón de elementos con apenas mil evaluaciones del oráculo. Eso
> es la promesa de la aceleración cuadrática.
>
> **[PAUSA 2s]**
>
> Ahora — y esto es importante — **esto no es gratis**. El algoritmo cuántico
> requiere un *backend* cuántico, qubits estables, y una capa de traducción del
> problema clásico al cuántico. La pregunta de ingeniería es: ¿cómo se inserta esto
> en un sistema productivo sin romper lo que ya funciona?
>
> **[TRANSICIÓN]** *(Avanzar a D10)*

---

## Diapositiva 10 — Cómo encaja en un sistema real

**Objetivo:** Mostrar dónde encaja el coprocesador cuántico en el sistema.

**Guion:**

> La respuesta es una **arquitectura híbrida en tres capas**. **[SEÑALAR]** capa
> por capa de izquierda a derecha:
>
> La **capa clásica** sigue siendo el motor principal — usa **Neo4j** para todo lo
> que ya sabe hacer bien: ingesta, índices, consultas transaccionales estándar de
> hasta 3 saltos. Solo las consultas profundas — más de 3 saltos — se derivan al
> coprocesador cuántico.
>
> La **capa de traducción** — que es el aporte central de este trabajo — toma el
> subgrafo candidato que extrajo Neo4j, calcula la **Matriz Laplaciana L = D − A**
> y la transpila a un circuito cuántico compatible con el backend. Si la latencia
> de compilación o de cola cuántica supera **500 ms**, hay un fallback automático a
> un solver heurístico clásico.
>
> La **capa cuántica** es donde corre Grover. Puede ser una **QPU en la nube**
> (IBM Quantum, Amazon Braket) o un **simulador local** (AerSimulator de Qiskit con
> soporte GPU vía cuStateVec).
>
> **[PAUSA 2s]**
>
> La idea clave, **[SEÑALAR]** la nota al pie, es que el sistema cuántico **no
> reemplaza** a Neo4j — es un **coprocesador asíncrono** para una clase acotada de
> consultas. La base de datos principal nunca se toca.
>
> **[TRANSICIÓN]** Esa arquitectura se traduce en requerimientos concretos de
> ingeniería. Veamos la tabla QSRE. *(Avanzar a D11)*

---

## Diapositiva 11 — Qué se necesita para construirlo

**Objetivo:** Trazar el puente entre la arquitectura y la especificación formal.

**Guion:**

> Aquí está la traducción de esa arquitectura a **requerimientos formales**, usando
> el marco **QSRE** — Ingeniería de Requerimientos para Software Cuántico.
>
> **[SEÑALAR]** las filas funcionales:
>
> - **REQ-CLA-01 / 02**: la capa clásica conserva sus responsabilidades — Neo4j
>   gestiona ingesta y consultas estándar, la API recibe y devuelve resultados.
> - **REQ-HIB-01**: la capa híbrida extrae el subgrafo candidato y construye la
>   Laplaciana en estricto presupuesto de tiempo.
> - **REQ-HIB-02**: la transpilación debe respetar las **puertas nativas** del
>   hardware cuántico objetivo, no cualquier puerta genérica.
> - **REQ-HIB-03**: el **timeout de 500 ms** es el interruptor de seguridad — si la
>   cola cuántica o la compilación tarda más, derivamos al solver clásico sin
>   bloquear al usuario.
> - **REQ-CUA-01**: el circuito se ejecuta un **número definido de shots** — entre
>   1.024 y 4.096 — para construir una distribución estadísticamente confiable,
>   porque los resultados cuánticos son probabilísticos.
>
> **[SEÑALAR]** la última fila, **RNF-01, 02, 03**: los no funcionales.
> Sobrecosto de QRAM acotado, tolerancia a ruido NISQ, y acceso a QPU nube solo
> cuando la heurística clásica determina que el subgrafo es demasiado denso para
> resolver por fuerza bruta.
>
> **[PAUSA 2s]**
>
> Ahora: ¿cómo validamos empíricamente que esta arquitectura tiene sentido?
> Veamos la metodología.
>
> **[TRANSICIÓN]** *(Avanzar a D12)*

---

## Diapositiva 12 — Cómo probé que esto funciona

**Objetivo:** Mostrar el protocolo experimental usado para validar la PoC.

**Guion:**

> La herramienta principal es **AerSimulator**, el simulador de vector de estado de
> **Qiskit**. Ejecuta el circuito cuántico exacto — sin el ruido del hardware real —
> y permite muestrear la distribución de probabilidad resultante mediante lo que se
> llama **"shots"**. Es el banco de pruebas estándar en la disciplina.
>
> **[SEÑALAR]** la tabla de configuración del backend. Por defecto corre en CPU con
> `AerSimulator()`. Si se dispone de GPU y la librería `qiskit-aer-gpu` instalada,
> se puede acelerar el cálculo de amplitudes con `cuStateVec`. Cada ejecución
> muestrea entre **1.024 y 4.096 shots** con semilla fija para **reproducibilidad**.
>
> **[SEÑALAR]** la card con los 5 pasos del protocolo:
>
> 1. **Generar** un grafo host con semilla fija, donde haya un anillo de fraude
>    garantizado.
> 2. **Enumerar** la **verdad fundamental** por fuerza bruta clásica — todos los
>    mapeos que satisfacen el patrón. Esto es lo que sabemos que Grover debería
>    encontrar.
> 3. **Construir y ejecutar** el circuito de Grover en AerSimulator.
> 4. **Comparar** los top-k estados más medidos contra la verdad fundamental del
>    paso 2.
> 5. **Repetir** el barrido completo para **N = 4, 5, 6... hasta 12 nodos**.
>
> El resultado global del barrido — **[SEÑALAR]** la nota al pie — fue un éxito
> empírico del **99 a 100%** en todos los tamaños probados, consistente con la
> probabilidad teórica del algoritmo.
>
> **[TRANSICIÓN]** Comencemos por el caso más pequeño, el **toy problem**.
> *(Avanzar a D13)*

---

## Diapositiva 13 — El primer experimento: un caso simple

**Objetivo:** Mostrar el caso más simple donde Grover demuestra empíricamente la ventaja.

**Guion:**

> El caso mínimo que implemente tiene un host de **4 cuentas** — los nodos 0, 1, 2
> y 3 — con las aristas que ven a la izquierda. **[SEÑALAR]** la tabla.
> Codificamos el espacio de búsqueda en **3 qubits**, lo que da exactamente
> **8 candidatos**. De esos 8, **3 son soluciones válidas** — las tres rotaciones
> del ciclo único **0 → 1 → 2 → 0**.
>
> Para N=8 y k=3 soluciones, el número óptimo de iteraciones de Grover es
> **1 sola iteración**. La probabilidad teórica de éxito por ejecución es del
> **84,4%**.
>
> **[SEÑALAR]** la imagen de la derecha, el histograma.
>
> Lo que muestra el histograma es exactamente la firma del algoritmo de Grover: los
> **3 estados válidos** aparecen amplificados del **12,5% inicial** (que sería la
> distribución uniforme) hasta aproximadamente el **28% cada uno**. Mientras tanto,
> los 5 estados inválidos caen a apenas ~1,5% cada uno. Esa separación de amplitudes
> es la que permite medir una solución correcta con alta probabilidad.
>
> **[PAUSA 2s]**
>
> Es un caso chiquito, sí — pero demuestra de forma empírica que la **capa de
> traducción** funciona: la Laplaciana del subgrafo realmente se traduce a un
> circuito, y ese circuito realmente amplifica las soluciones. Ahora veamos si
> esto escala.
>
> **[TRANSICIÓN]** *(Avanzar a D14)*

---

## Diapositiva 14 — Qué pasa si el grafo crece

**Objetivo:** Mostrar cómo crece la ventaja cuántica al aumentar el tamaño del problema.

**Guion:**

> Esta es la **prueba de escalabilidad**, que es donde la promesa del cómputo
> cuántico se separa del ruido. **[SEÑALAR]** la tabla de la izquierda.
>
> Repitiendo el mismo protocolo — el mismo circuito de Grover, solo cambiando el
> tamaño del grafo host — barrí desde **N=4 nodos** hasta **N=12 nodos**. Lo
> importante es la columna de qubits: pasa de **5** a **11**. Es un crecimiento
> **logarítmico**, aproximadamente **3 · log₂(N)** qubits por cada triplete de
> nodos que se agrega al host.
>
> Mientras tanto, los **candidatos clásicos** que un algoritmo de fuerza bruta
> tendría que evaluar explotan: **24, 120, 336, 720, 1.320** mapeos. Y la última
> columna — el **speedup** — pasa de **12× a 264×** a medida que N crece.
>
> **[SEÑALAR]** la curva de la derecha. La curva sube. **Eso** es la aceleración
> cuadrática.
>
> **[PAUSA 2s]**
>
> Todos los puntos del barrido conservan un éxito empírico del **99–100%**. La
> codificación logarítmica + Grover es estable en el rango probado. Ahora bien,
> necesito mostrarles una imagen intermedia de esto, en concreto cómo se ve el
> histograma en el caso de **N=8, 9 qubits** — donde ya estamos hablando de
> **336 candidatos**.
>
> **[TRANSICIÓN]** *(Avanzar a D15)*

---

## Diapositiva 15 — Un caso intermedio: 8 cuentas

**Objetivo:** Visualizar la firma de Grover en un caso de escala media.

**Guion:**

> Esta imagen corresponde a una corrida con **N=8 nodos** en el host, codificada
> en **9 qubits**. El espacio de búsqueda tiene **336 mapeos candidatos** — ya no
> estamos en el caso trivial. **[SEÑALAR]** el histograma.
>
> Lo que ven en pantalla es el resultado de **medir el circuito muchas veces**
> (1.024 shots) y contar cuántas veces colapsó a cada estado. Las barras son
> exhaustivas: las **soluciones verdaderas** — los mapeos que satisfacen el anillo
> — aparecen con amplitudes claramente amplificadas, mientras que los mapeos que no
> cumplen el patrón quedan con amplitudes casi residuales.
>
> El **éxito empírico** de esta corrida ronda el **99%**, consistente con la
> probabilidad teórica de Grover para N=8, k pequeño.
>
> **[PAUSA 2s]**
>
> Ahora — antes de las conclusiones, hay que ser honestos sobre lo que **no**
> podemos hacer todavía. Eso nos lleva al bloque de limitaciones.
>
> **[TRANSICIÓN]** *(Avanzar a D16)*

---

## Diapositiva 16 — Qué no podemos hacer todavía

**Objetivo:** Poner los pies en la tierra: qué impide hoy el salto a producción.

**Guion:**

> **NISQ** significa "Noisy Intermediate-Scale Quantum" — el hardware cuántico
> ruidoso de escala intermedia en el que estamos hoy. Las tarjetas de la diapositiva
> resumen sus dos grandes limitaciones.
>
> **[SEÑALAR]** "Cuello de botella QRAM".
>
> El **QRAM** es el problema menos visible y más decisivo: inicializar un estado
> cuántico que codifica la matriz de adyacencia del grafo cuesta **O(N)** operaciones
> **clásicas**. Esa carga de datos puede **neutralizar** completamente la ventaja
> algorítmica de O(√N) cuando N es grande. Hoy, para grafos de millones de nodos,
> este cuello de botella hace que el sistema cuántico **sea más lento end-to-end**
> que un solver clásico optimizado. Es el límite operativo más difícil.
>
> **[SEÑALAR]** "Hardware limitado".
>
> Por el lado del hardware: cada compuerta cuántica tiene una **tasa de error del
> 0,1–1%**. Los circuitos profundos colapsan por decoherencia antes de completar las
> iteraciones de Grover. Hay **menos de 1.000 qubits lógicos** disponibles, lo que
> nos restringe a grafos pequeños — menos de ~512 candidatos codificables. Los
> tiempos de coherencia se miden en **microsegundos**, y las **colas en la nube**
> para acceder a una QPU real tardan **minutos** — incompatible con análisis en
> tiempo real.
>
> **[SEÑALAR]** la nota al pie.
>
> Además, los resultados cuánticos son **probabilísticos** — necesitamos entre
> **1.024 y 4.096 shots** por ejecución para obtener una distribución
> estadísticamente confiable.
>
> **[TRANSICIÓN]** Todo esto confluye en el veredicto final de factibilidad.
> *(Avanzar a D17)*

---

## Diapositiva 17 — El veredicto

**Objetivo:** Cerrar la discusión con un veredicto honesto y accionable.

**Guion:**

> Tomemos las **seis dimensiones de QSRE** y evaluémoslas una por una.
>
> **[SEÑALAR]** fila por fila:
>
> - La **correctitud algorítmica** es **demostrada**: Grover provee ventaja
>   cuadrática con prueba formal y verificación experimental propia.
> - La **arquitectura de integración** es **sólida**: la delegación aislada protege
>   el sistema productivo — Neo4j nunca está en riesgo.
> - La **capa de traducción** está **validada**: la prueba de concepto es
>   ejecutable y los resultados son reproducibles.
> - El **hardware NISQ actual** es **limitante**: no alcanza para grafos de
>   producción.
> - El **cuello de botella QRAM** está **sin solución madura** y neutraliza la
>   ventaja a gran escala.
> - La **disponibilidad operativa** es **condicional**: el fallback clásico a 500 ms
>   garantiza que el sistema **no se cae** si la cuántica falla.
>
> **[PAUSA 2s]**
>
> El veredicto es, en una sola línea: **"Parcialmente factible / exploratorio"**.
>
> **[TRANSICIÓN]** ¿Qué hago con esto? Mi recomendación es de **dos horizontes**:
>
> - **Corto plazo**: implementar la arquitectura usando simuladores tensoriales
>   locales — GPU con AerSimulator. Útil para subgrafos candidatos extraídos por
>   Neo4j donde la densidad crítica justifique delegar.
> - **Medio plazo**: migrar a QPU real cuando los dispositivos superen los
>   **~1.000 qubits lógicos** con corrección de errores — lo que la disciplina llama
>   **FTQC**, Fault-Tolerant Quantum Computing.
> - Y **no se recomienda** reemplazar el motor de base de datos clásico. El valor
>   está en la delegación selectiva, no en la sustitución.
>
> **[TRANSICIÓN]** Cierro con las referencias. *(Avanzar a D18)*

---

## Diapositiva 18 — Las referencias

**Objetivo:** Dejar respaldo bibliográfico claro y recordar el estándar de verificación.

**Guion:**

> Esta es una **selección** de las referencias del trabajo; la lista completa con
> notas de verificación está en el archivo `REFERENCIAS.md` del repositorio.
>
> **[SEÑALAR]** la columna izquierda:
>
> - **Grover, 1996** — el paper fundacional del algoritmo de búsqueda cuántica.
> - **Ullmann, 1976** — la demostración de NP-Completitud del isomorfismo de
>   subgrafos.
> - **Mariella y Simonetto, 2023** — el paper central de este trabajo: un
>   algoritmo cuántico específicamente para isomorfismo de subgrafos, publicado en
>   ACM Transactions on Quantum Computing.
> - **Sepúlveda et al., 2024** — la revisión sistemática sobre ingeniería de
>   requisitos para software cuántico, en MDPI Electronics. Es el paper que da el
>   marco QSRE.
>
> **[SEÑALAR]** la columna derecha:
>
> - **Blanuša et al., 2024** — Graph Feature Preprocessor, publicado en ACM ICAIF,
>   sobre extracción de sub-grafos en tiempo real para detección de crimen
>   financiero.
> - **Innan et al., 2024** — Quantum Graph Neural Networks aplicados a detección
>   de fraude financiero, en Quantum Machine Intelligence.
> - **Wang et al., 2024** — uso de Coherent Ising Machines para detección de
>   comunidades en grafos antifraude, en MDPI Entropy.
> - **Vlasic y Pham, 2025** — scoring de anomalías mediante caminatas cuánticas, en
>   Annalen der Physik.
>
> **[PAUSA 2s]**
>
> Quiero destacar algo: en versiones anteriores del trabajo hubo **dos referencias
> con datos incorrectos** — autores mal asignados y un DOI no verificable. Ambas
> fueron **corregidas o eliminadas** y reemplazadas por fuentes verificadas contra
> arXiv, ACM Digital Library y las páginas de los publishers. La transparencia
> sobre esa corrección está documentada en el archivo `REFERENCIAS.md`.
>
> **[TRANSICIÓN]** Con esto cierro el cuerpo del trabajo. *(Avanzar a D19)*

---

## Diapositiva 19 — Gracias / Cierre

**Objetivo:** Cerrar con un agradecimiento claro y abrir la conversación a preguntas.

**Guion:**

> Con esto cierro la presentación. Resumiendo en una frase: **Grover ofrece una
> aceleración cuadrática teórica real, la capa de traducción clásico-cuántica
> funciona empíricamente, pero la era NISQ actual — por QRAM y por escala de
> qubits — la deja en estado exploratorio, no productivo**.
>
> **[PAUSA 2s]**
>
> Agradezco al **Dr. Samuel Sepúlveda** por la guía durante el módulo, y a
> ustedes por el tiempo y la atención.
>
> Quedo abierto a **preguntas, comentarios y observaciones**.
>
> ¿Qué les gustaría discutir primero?

**[SEÑALAR]** los badges con el nombre y el código del curso. Mantener una postura
abierta, tomar notas de las preguntas que no se puedan responder en el momento y
ofrecer seguimiento por correo. Si la pregunta es profundamente técnica y la
audiencia lo permite, derivar al repositorio y a `REFERENCIAS.md` para más detalle.

---

## Material de apoyo — Cómo leer las visualizaciones

**Cuándo usar este bloque:** no es parte del recorrido principal de 19 diapositivas.
Es material de respaldo para dos momentos: (a) durante la sesión de preguntas, si
alguien pide "¿pero cómo se lee exactamente este gráfico?", o (b) después del cierre,
si el profesor quiere profundizar en la evidencia empírica antes de calificar. Cada
imagen del repositorio (`demo/*.png`) tiene su propio guion corto de 3 elementos:
**qué es**, **cómo leerlo**, **qué conclusión saca de ahí**.

### A. Grafos de transacciones (host + anillo de fraude)

**Imágenes:** `demo/grafo_host_N5.png`, `grafo_host_N6.png`, `grafo_host_N7.png`
(generadas con `grover_subgraph_scaled.py --host-nodes {5,6,7}`), y el panel derecho
de `resultados_grover_fraude.png` para el caso original de 4 nodos.

> Cada círculo numerado es una cuenta bancaria; cada flecha es una transacción
> dirigida. **[SEÑALAR]** los tres nodos rojos y las flechas rojas gruesas: ese es
> el anillo de fraude garantizado, siempre construido como **0 → 1 → … → (k−1) → 0**
> — en nuestro caso, un ciclo de 3 cuentas. **[SEÑALAR]** el resto de nodos y
> aristas en gris: son transacciones legítimas generadas aleatoriamente con semilla
> fija, que existen únicamente para que el patrón no sea trivial de encontrar a
> simple vista.
>
> **[PAUSA 2s]**
>
> La disposición circular no es casualidad: al aumentar N de 5 a 7 nodos, ustedes
> pueden ver que el anillo rojo **se mantiene igual de compacto y reconocible**,
> mientras el ruido gris alrededor crece. Esa es la intuición visual de por qué el
> problema se vuelve más difícil clásicamente sin cambiar su naturaleza — el patrón
> que buscamos no crece, pero el pajar donde se esconde sí.

### B. Histogramas de probabilidad de Grover

**Imágenes:** `histograma_N5_q6.png`, `histograma_N6_q7.png`, `histograma_N7_q8.png`,
`histograma_N8_q9.png`, y el panel izquierdo de `resultados_grover_fraude.png`.

> El eje horizontal enumera los estados cuánticos medidos — cada barra es un mapeo
> candidato distinto. El eje vertical es la probabilidad de medición tras ejecutar
> el circuito miles de veces (shots). **[SEÑALAR]** las barras **verdes**: son los
> mapeos que sí forman el anillo de fraude. Las **rojas** son mapeos que no lo
> forman. La línea punteada horizontal marca la **distribución uniforme** — lo que
> se vería si no hubiera Grover, es decir, un candidato al azar.
>
> **[PAUSA 2s]**
>
> La lectura clave es la **separación entre verde y rojo**: mientras más alta la
> barra verde por sobre la línea punteada, más fuerte fue la amplificación. En el
> panel de métricas de la derecha (solo en los histogramas escalables) está además
> el número exacto de iteraciones usadas y el éxito empírico logrado — esa cifra es
> la que se compara contra la probabilidad teórica de Grover para confirmar que la
> implementación es correcta, no solo que "dio un número bonito".

### C. Diagrama del circuito cuántico

**Imagen:** `demo/circuito_grover.png` (generado con `qc.draw('mpl')` sobre el
circuito de 3 qubits, 1 iteración, del demo mínimo).

> Cada línea horizontal es un qubit (**q₀, q₁, q₂**); el tiempo avanza de izquierda
> a derecha. **[SEÑALAR]** los tres bloques que se repiten:
>
> 1. Los cuadros **rosados con H** al inicio son compuertas Hadamard — crean la
>    superposición uniforme sobre los 8 candidatos.
> 2. Las **barreras grises** con etiqueta (`O|000⟩`, `O|101⟩`, `O|110⟩`) marcan el
>    oráculo: dentro de cada una hay compuertas X (azul oscuro) que voltean bits, y
>    un círculo con una cruz — una Toffoli controlada — que invierte la fase del
>    estado marcado. Son tres bloques porque hay tres soluciones válidas que marcar.
> 3. La barrera **"Difusor"** al final agrupa las compuertas que reflejan la
>    amplitud respecto al promedio — el paso que efectivamente "empuja" la
>    probabilidad hacia los estados marcados por el oráculo.
> 4. Los medidores grises al final colapsan cada qubit a un bit clásico (fila `c`).
>
> **[PAUSA 2s]**
>
> La idea para el profesor: **el circuito no "busca" nada explícitamente** — no hay
> ningún paso que recorra los 8 candidatos uno por uno. Cada compuerta se aplica
> una sola vez sobre los tres qubits en superposición. Toda la ventaja viene de que
> el oráculo y el difusor actúan sobre **todos los estados a la vez**, y es la
> interferencia entre sus amplitudes la que deja la probabilidad concentrada en los
> estados correctos al momento de medir.

**Síntesis para cerrar el bloque:** el grafo define el problema, el circuito es la
implementación exacta de Grover para ese problema, y el histograma es la prueba
empírica de que el circuito funcionó. Mostrar los tres juntos —grafo, circuito,
histograma— para el mismo caso (por ejemplo N=6) es la forma más directa de
demostrar de punta a punta que la capa de traducción clásico-cuántica es real y
ejecutable, no solo teoría.

---

## Notas para el expositor

- **Tiempo total objetivo**: 28–32 minutos + 5–10 minutos de preguntas.
- **Apoyo visual**: siempre que sea posible, **señalar con el cursor o el puntero**
  las fórmulas y palabras clave que se están mencionando (las fórmulas centrales,
  los números grandes, las palabras marcadas en negrita en las cards).
- **Pausa dramática**: cuando se llegue a un número fuerte (10^30, 10^21, 1.000
  iteraciones, 99% de éxito), hacer **una pausa intencional de 2 segundos** antes
  de continuar. Refuerza el impacto.
- **Manejo de preguntas difíciles**: si alguien pregunta por cosas que exceden el
  alcance (corrección de errores cuánticos, criptografía post-cuántica, etc.),
  responder: *"Eso excede el alcance de este trabajo, pero es exactamente la
  dirección donde la disciplina apunta. Anoto la referencia para la sección de
  trabajos futuros."*
- **Backup del computador**: tener el PDF de la presentación y los scripts de
  Python accesibles aunque el proyector falle. La presentación está generada
  desde `slides.html` con assets PNG locales.

---

> Última revisión: julio 2026.
