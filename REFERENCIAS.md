# Referencias

> **Nota sobre verificación:** Todas las referencias de este documento fueron verificadas
> contra bases de datos académicas (MDPI, arXiv, ACM DL, ResearchGate) en junio de 2026.
> Se indican explícitamente las correcciones realizadas sobre las citas originales del trabajo.

---

## Referencias Verificadas

### Algoritmos y Teoría Cuántica

**Grover, L. K. (1996).** A fast quantum mechanical algorithm for database search.
*Proceedings of the 28th Annual ACM Symposium on Theory of Computing (STOC)*, 212–219.
https://doi.org/10.1145/237814.237866

> Artículo fundacional. Demuestra la ventaja cuadrática O(√N) para búsqueda no estructurada.
> Verificado: publicación clásica de la ACM, ampliamente citada.

---

**Nielsen, M. A., & Chuang, I. L. (2010).** *Quantum Computation and Quantum Information.*
Cambridge University Press.
ISBN: 978-1-107-00217-3

> Referencia estándar del campo. Verificado: publicación de Cambridge University Press.

---

**Hidary, J. D. (2021).** *Quantum Computing: An Applied Approach* (2nd ed.).
Springer.
https://doi.org/10.1007/978-3-030-83274-2

> Verificado: publicación de Springer, incluye implementaciones en Qiskit y Cirq.

---

### Isomorfismo de Subgrafos

**Ullmann, J. R. (1976).** An algorithm for subgraph isomorphism.
*Journal of the ACM (JACM)*, 23(1), 31–42.
https://doi.org/10.1145/321921.321925

> Demostración seminal de la complejidad NP-Completa del problema. Verificado: publicación
> clásica de la ACM con más de 3000 citas.

---

### Ingeniería de Software Cuántico (QSRE)

**Sepúlveda, S., Cravero, A., Fonseca, G., & Antonelli, L. (2024).** Systematic Review on
Requirements Engineering in Quantum Computing: Insights and Future Directions.
*Electronics*, 13(15), 2989.
https://doi.org/10.3390/electronics13152989

> Verificado: publicado el 29 de julio de 2024 en MDPI Electronics (ISSN 2079-9292).
> Estudio sistemático de 105 papers (2017–2024). DOI activo y acceso abierto confirmados.

---

**Piattini, M., Peterssen, G., & Hevia, J. L. (2022).** *Ingeniería del Software Cuántico &
QuantumPath®.* aQuantum Software Engineering.
ISBN: 979-8-362-11764-1

> Verificado: disponible en Amazon (ASIN B0BMZP8RBQ) y en el sitio oficial de aQuantum
> (https://www.aquantum.es). Nota: el orden canónico de autores en la portada es
> Peterssen–Hevia–Piattini, aunque la autoría es equivalente.

---

**Sepúlveda, S. (2026).** *Apunte Complementario: Casos de aplicación de QSE y QRE.*
Universidad de La Frontera, Magíster en Ingeniería Informática. Material de curso EMI307.

**Sepúlveda, S. (2026).** *Apunte Complementario: Introducción algebraico-matemática al qubit.*
Universidad de La Frontera, Magíster en Ingeniería Informática. Material de curso EMI307.

> Material docente interno. No verificable externamente, pero producido por el autor
> en el contexto del programa y curso referenciados.

---

### Isomorfismo de Subgrafos Cuántico

**Mariella, N., & Simonetto, A. (2023).** A Quantum Algorithm for the Sub-graph Isomorphism
Problem.
*ACM Transactions on Quantum Computing*, 4(2), Article 13, pp. 1–34.
https://doi.org/10.1145/3569095
arXiv:2111.09732

> Verificado: publicado en ACM TQC, febrero 2023. DOI activo en ACM Digital Library.
> IBM Research lista este paper en su portal de publicaciones. Código disponible en
> github.com/qiskit-community/subgraph-isomorphism.
> **Referencia central del trabajo**: propone un método variacional cuántico para
> isomorfismo de subgrafos usando codificación logarítmica de qubits (⌈log₂ N⌉),
> idéntico al enfoque descrito en REQ-HIB-01 y REQ-HIB-02 de este análisis.

---

### Detección de Fraude en Grafos

**Blanuša, J., Cravero Baraja, M., Anghel, A., von Niederhäusern, L., Altman, E.,
Pozidis, H., & Atasu, K. (2024).** Graph Feature Preprocessor: Real-time Subgraph-based
Feature Extraction for Financial Crime Detection.
*Proceedings of the 5th ACM International Conference on AI in Finance (ICAIF '24).*
arXiv preprint arXiv:2402.08593.
https://doi.org/10.1145/3677052.3698674

> Verificado: paper publicado en ACM ICAIF 2024. arXiv:2402.08593 activo y accesible.
>
> ⚠️ **CORRECCIÓN IMPORTANTE:** La presentación original de este trabajo citó erróneamente
> este paper con los autores "Shirakawa, M., Suzumura, T., & Kanezashi, H." — esos nombres
> NO corresponden a este artículo. Los autores reales son los indicados arriba
> (verificado en arXiv y ACM Digital Library).

---

**Innan, N., Sawaika, A., Dhor, A., Dutta, S., Thota, S., Gokal, H., Patel, N.,
Khan, M. A.-Z., Theodonis, I., & Bennai, M. (2024).** Financial Fraud Detection using
Quantum Graph Neural Networks.
*Quantum Machine Intelligence*, 6(1).
https://doi.org/10.1007/s42484-024-00143-6
arXiv:2309.01127

> Verificado: publicado en Quantum Machine Intelligence (Springer), febrero 2024.
> DOI activo en SpringerLink y paper accesible en arXiv.
> Propone QGNNs (Quantum Graph Neural Networks) con Variational Quantum Circuits para
> detección de fraude financiero; comparado contra GNNs clásicos en datasets reales.

---

**Wang, Y. J., Yang, X., Ju, C., Zhang, Y., Zhang, J., Xu, Q., Wang, Y., Gao, X.,
Cao, X., Ma, Y., & Wu, J. (2024).** Quantum Computing in Community Detection for
Anti-Fraud Applications.
*Entropy*, 26(12), 1026.
https://doi.org/10.3390/e26121026

> Verificado: publicado el 27 de noviembre de 2024 en MDPI Entropy (ISSN 1099-4300).
> DOI activo. Indexado en PubMed (PMC11727351) y acceso abierto confirmado.
> Usa un Coherent Ising Machine (CIM) para resolver el modelo QUBO de detección de
> comunidades en grafos de transacciones con 308 nodos.

---

**Vlasic, A., & Pham, A. (2025).** Scoring Anomalous Vertices Through Quantum Walks.
*Annalen der Physik*, 537(5), Article 2400282.
https://doi.org/10.1002/andp.202400282
arXiv:2311.09855

> Verificado: publicado el 16 de febrero de 2025 en Annalen der Physik (Wiley Online Library).
> DOI activo. Primer algoritmo cuántico para calcular el puntaje de anomalía de cada nodo
> de un grafo mediante caminatas cuánticas continuas. Contempla el contexto NISQ.

---

**Doost, M., & Manthouri, M. (2025).** Quantum Topological Graph Neural Networks for
Detecting Complex Fraud Patterns.
arXiv:2512.03696.
https://arxiv.org/abs/2512.03696

> Verificado: preprint en arXiv (diciembre 2025), accesible y activo.
> Propone el framework QTGNN: embedding cuántico con entrelazamiento, convoluciones
> variacionales cuánticas y análisis topológico de datos. Evaluado sobre PaySim y Elliptic.
> Incluye garantías de convergencia para hardware NISQ.

---

## Referencias No Confirmadas (Eliminadas)

La siguiente referencia apareció en versiones anteriores del trabajo pero **no pudo ser
verificada con los datos proporcionados** y se elimina para evitar citar una fuente falsa:

> ~~Sun, Z., et al. (2024). Algorithmic and Learning-based Approaches to Subgraph Matching
> and Counting: A Survey. TechRxiv. https://doi.org/10.36227/techrxiv.176739510~~

Si bien existe al menos un preprint en TechRxiv sobre este tema, el autor "Sun, Z." y el DOI
exacto no pudieron confirmarse. Para temas de survey sobre subgraph matching, se recomienda
citar en su lugar:

**Zhang, Z., Lu, Y., Zheng, W., & Lin, X. (2024).** A Comprehensive Survey and Experimental
Study of Subgraph Matching: Trends, Unbiasedness, and Interaction.
*Proceedings of the ACM on Management of Data*, 2(1).
https://doi.org/10.1145/3639315

> Verificado: publicado en SIGMOD/PODS 2024. ACM Digital Library confirma DOI y autores.

---

## Resumen de Correcciones

| Referencia original | Problema | Corrección |
|--------------------|----------|-----------|
| Shirakawa, M. et al. (2024) | Autores completamente incorrectos para arXiv:2402.08593 | Reemplazado por Blanuša, J. et al. (2024) con autores verificados |
| Sun, Z. et al. (2024). TechRxiv | Autores y DOI no confirmados | Eliminado; se sugiere Zhang et al. (2024) como alternativa verificada |

## Referencias Nuevas Incorporadas

| Paper | Relevancia para el trabajo |
|-------|--------------------------|
| Mariella & Simonetto (2023). ACM TQC | **Directa**: algoritmo cuántico para isomorfismo de subgrafos exactamente |
| Vlasic & Pham (2025). Annalen der Physik | Caminatas cuánticas para detección de anomalías en grafos |
| Wang et al. (2024). Entropy | Quantum computing aplicado a detección de fraude en redes de transacciones |
| Innan et al. (2024). Quantum Machine Intelligence | QGNNs híbridos para fraude financiero |
| Doost & Manthouri (2025). arXiv | QTGNN: framework cuántico-topológico para fraude complejo |
