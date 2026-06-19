# Hallazgos del análisis

## 1. Resumen del conjunto analizado

El Data Warehouse contiene:

* **96,195 observaciones de control lechero**.
* **13,829 ovejas diferentes**.
* Controles registrados entre el **10 de marzo y el 29 de junio de 2016**.
* Fechas de parto entre el **15 de septiembre de 2014 y el 26 de febrero de 2016**.
* **213,848.17 litros** registrados en el conjunto completo de observaciones.

La producción total por control presentó:

| Indicador | Resultado |
| --------- | --------: |
| Media     |  2.2231 L |
| Mediana   |  2.1100 L |
| Mínimo    |  0.1000 L |
| Máximo    |  6.6900 L |

La media fue ligeramente superior a la mediana, lo que indica cierta asimetría hacia observaciones de producción elevada.

---

## 2. Producción según días en lactancia

El promedio más alto se observó en el intervalo de **31 a 60 días en lactancia**, con una producción promedio de **2.6931 litros por control**.

| Etapa          | Observaciones | Ovejas |    Media |  Mediana |
| -------------- | ------------: | -----: | -------: | -------: |
| 0–30 días      |         4,195 |    681 | 2.5103 L | 2.4900 L |
| 31–60 días     |        19,917 |  1,974 | 2.6931 L | 2.6700 L |
| 61–90 días     |        20,419 |  8,757 | 2.5433 L | 2.5100 L |
| 91–120 días    |        22,037 |  2,079 | 2.1519 L | 2.1000 L |
| 121–180 días   |        20,870 |  2,606 | 1.7797 L | 1.6900 L |
| 181–270 días   |         8,305 |    661 | 1.4958 L | 1.4400 L |
| 271–365 días   |           342 |     31 | 1.7516 L | 1.7750 L |
| 366 días o más |           110 |      4 | 1.4882 L | 1.4000 L |

### Interpretación

Entre los primeros 30 días y el intervalo de 31–60 días, la producción promedio aumentó aproximadamente **7.3%**.

Después del intervalo 31–60 días se observa una disminución progresiva:

* 61–90 días: **5.6% menor** que el máximo de 31–60 días.
* 91–120 días: **20.1% menor**.
* 121–180 días: **33.9% menor**.
* 181–270 días: **44.5% menor**.

El intervalo 271–365 días presenta una media ligeramente superior al intervalo anterior, pero contiene únicamente **342 observaciones y 31 ovejas**, por lo que no debe interpretarse como una recuperación general de la producción.

La categoría de 366 días o más contiene solamente **110 observaciones correspondientes a cuatro ovejas**. Sus resultados deben considerarse exploratorios y no comparables directamente con las etapas de mayor tamaño.

### Hallazgo principal

> La producción observada alcanza su promedio máximo entre los 31 y 60 días en lactancia y disminuye de manera marcada en los intervalos posteriores.

Este resultado describe el conjunto disponible. No constituye por sí solo una estimación causal ni una curva biológica universal.

---

## 3. Diferencias observadas entre contextos de manejo

Las combinaciones con mayor producción promedio fueron:

| Espacio de grupo | Corral | Observaciones | Ovejas |    Media |
| ---------------- | -----: | ------------: | -----: | -------: |
| Group space 4    |      4 |        10,780 |  3,016 | 2.9668 L |
| Group space 2    |      2 |        10,982 |  3,175 | 2.9357 L |
| Group space 4    |      8 |         8,800 |  2,380 | 2.8827 L |
| Group space 4    |      1 |        10,505 |    392 | 2.6500 L |
| Group space 4    |      7 |         8,415 |    316 | 2.4952 L |

Las combinaciones con menor promedio fueron:

| Espacio de grupo | Corral | Observaciones | Ovejas |    Media |
| ---------------- | -----: | ------------: | -----: | -------: |
| Group space 1    |     10 |         9,405 |    357 | 1.6256 L |
| Group space 3    |      5 |         8,195 |  2,208 | 1.3225 L |
| Group space 3    |     66 |         7,590 |    286 | 1.1948 L |

El corral 4 del espacio de grupo 4 presentó un promedio de **2.9668 litros**, aproximadamente **33.5% por encima** del promedio global de 2.2231 litros.

El corral 66 del espacio de grupo 3 presentó un promedio de **1.1948 litros**, aproximadamente **46.3% por debajo** del promedio global.

La diferencia entre la combinación de mayor y menor promedio fue de aproximadamente **1.772 litros por control**.

### Limitación fundamental

No se puede afirmar que el corral o el espacio de grupo sean la causa de esas diferencias.

Los grupos pueden diferir simultáneamente en:

* días en lactancia;
* composición de ovejas;
* cantidad de observaciones por oveja;
* periodo temporal;
* condiciones climáticas;
* posibles variables biológicas no disponibles.

Por tanto, este resultado identifica segmentos que merecen revisión, pero no demuestra efectos causales del manejo.

### Hallazgo de gestión

> Existen diferencias descriptivas amplias entre combinaciones de espacio de grupo y corral. Las combinaciones Group space 4–corral 4 y Group space 2–corral 2 presentan los mayores promedios observados, mientras que Group space 3–corral 66 presenta el menor.

---

## 4. Evolución temporal de la producción

Los cinco días con mayor producción promedio fueron:

| Fecha      | Observaciones |    Media |
| ---------- | ------------: | -------: |
| 2016-03-30 |           869 | 2.5902 L |
| 2016-03-31 |           869 | 2.5787 L |
| 2016-03-23 |           869 | 2.5704 L |
| 2016-04-02 |           869 | 2.5537 L |
| 2016-04-06 |           869 | 2.5462 L |

Los cinco días con menor producción promedio fueron:

| Fecha      | Observaciones |    Media |
| ---------- | ------------: | -------: |
| 2016-06-12 |           880 | 1.6948 L |
| 2016-06-13 |           880 | 1.7041 L |
| 2016-06-28 |           880 | 1.7204 L |
| 2016-06-16 |           880 | 1.7219 L |
| 2016-06-27 |           880 | 1.7259 L |

La diferencia entre el día de mayor y menor promedio fue de **0.8954 litros por control**.

El promedio del día más bajo fue aproximadamente **34.6% menor** que el promedio del día más alto.

Los máximos aparecen principalmente entre finales de marzo e inicios de abril, mientras que los mínimos aparecen durante junio.

### Interpretación

La evolución temporal coincide parcialmente con el avance general de las ovejas hacia etapas posteriores de lactancia. Por ello, la caída temporal no debe atribuirse automáticamente al clima o a una fecha específica.

---

## 5. Relación observada con las condiciones climáticas

### Condiciones del día del control

| Variable          | Correlación con producción |
| ----------------- | -------------------------: |
| THI               |                    -0.2304 |
| Temperatura media |                    -0.2352 |
| Humedad media     |                     0.1645 |
| Precipitación     |                     0.0790 |
| Radiación         |                    -0.1815 |

### Condiciones del día anterior

| Variable                   | Correlación con producción |
| -------------------------- | -------------------------: |
| THI anterior               |                    -0.2327 |
| Temperatura media anterior |                    -0.2389 |
| Humedad media anterior     |                     0.1633 |
| Precipitación anterior     |                     0.0676 |

### Interpretación

Las correlaciones observadas son pequeñas o moderadas en magnitud.

Los resultados indican:

* asociación negativa débil entre producción y THI;
* asociación negativa débil entre producción y temperatura;
* asociación positiva débil con humedad;
* asociación muy débil con precipitación;
* asociación negativa débil con radiación.

Las variables del día anterior presentan resultados muy similares a las del día del control. La temperatura del día anterior mostró la correlación negativa de mayor magnitud, con **r = -0.2389**.

### Precaución analítica

Estas correlaciones no controlan por:

* etapa de lactancia;
* identidad de la oveja;
* manejo;
* fecha;
* repetición de observaciones;
* otras variables biológicas.

Además, la producción disminuye a lo largo del periodo observado mientras algunas variables climáticas cambian estacionalmente. Esto puede producir correlaciones parcialmente confundidas por el tiempo y los días en lactancia.

### Hallazgo climático

> En el conjunto analizado, temperaturas y valores de THI más altos están asociados con una producción ligeramente menor, pero la magnitud de las correlaciones es insuficiente para atribuirles un efecto causal independiente.

---

## 6. Cobertura longitudinal de las ovejas

La distribución de observaciones por animal es altamente desigual:

| Indicador                      | Resultado |
| ------------------------------ | --------: |
| Ovejas totales                 |    13,829 |
| Mínimo de observaciones        |         1 |
| Media de observaciones         |      6.96 |
| Mediana de observaciones       |         1 |
| Máximo de observaciones        |        97 |
| Ovejas con una observación     |    12,925 |
| Porcentaje con una observación |    93.46% |

Aunque la media es de 6.96 controles por oveja, la mediana es solamente uno. Esto ocurre porque un grupo pequeño de animales tiene muchos controles y la gran mayoría tiene uno solo.

### Implicación

> El 93.46% de las ovejas no dispone de seguimiento longitudinal, por lo que el proyecto es más sólido para análisis agregados que para evaluar trayectorias individuales.

Las visualizaciones por animal deben:

* mostrar el número de observaciones;
* evitar rankings basados en una sola medición;
* filtrar un mínimo de controles cuando se estudien tendencias individuales.

---

## 7. Calidad de los datos

| Estado                    | Observaciones | Porcentaje |
| ------------------------- | ------------: | ---------: |
| Completo                  |        96,177 |   99.9813% |
| Espacio de grupo faltante |            18 |    0.0187% |

El nivel de completitud de las variables modeladas es muy alto.

Las 18 observaciones con espacio de grupo faltante se conservaron y fueron asociadas con una categoría explícita de calidad, en lugar de eliminarse.

También se verificó que:

* las 96,195 filas de origen llegaron a la tabla de hechos;
* `source_row_number` es único;
* no existen balances inválidos entre ordeño matutino, vespertino y total;
* todas las claves foráneas tienen correspondencia;
* la reejecución del ETL no duplica registros.

### Hallazgo de calidad

> El 99.9813% de las observaciones está completo para los atributos utilizados en el modelo, y los registros incompletos fueron preservados con trazabilidad explícita.

---

## 8. Conclusiones principales

1. La producción promedio global fue de **2.2231 litros por control**.

2. El intervalo de **31–60 días en lactancia** presentó la mayor producción promedio, con **2.6931 litros**.

3. Después de los 60 días se observa una disminución sostenida de la producción promedio, que alcanza aproximadamente **1.4958 litros** entre 181 y 270 días.

4. Las diferencias entre contextos de manejo son amplias, pero deben interpretarse como segmentación descriptiva y no como efectos causales.

5. La temperatura y el THI presentan asociaciones negativas débiles con la producción, tanto para el día del control como para el día anterior.

6. El periodo observado muestra producciones más altas a finales de marzo e inicios de abril y más bajas durante junio.

7. El análisis individual está limitado porque **93.46% de las ovejas tiene una sola observación**.

8. La calidad técnica del dataset procesado es alta: **99.9813% de los registros está completo**, sin pérdida de observaciones durante el ETL.

---

## 9. Limitaciones

* El análisis es descriptivo y exploratorio.
* Las correlaciones no implican causalidad.
* No se dispone de edad, raza, número de parto, salud o genética.
* La composición de animales varía entre grupos de manejo.
* La mayoría de las ovejas tiene una sola observación.
* El periodo de control cubre aproximadamente cuatro meses de un solo año.
* Los rangos de lactancia son agrupaciones operativas del proyecto.
* Las comparaciones no ajustan simultáneamente por clima, manejo, fecha y etapa de lactancia.

---

## 10. Posibles extensiones

* Construir comparaciones ajustadas por días en lactancia.
* Analizar únicamente ovejas con múltiples controles.
* Incorporar modelos de efectos mixtos con oveja como efecto aleatorio.
* Normalizar comparaciones entre corrales por etapa de lactancia.
* Añadir atributos biológicos y reproductivos.
* Extender el periodo a múltiples años.
* Crear alertas de producción atípica.
* Implementar cargas incrementales si se incorporan nuevos controles.
