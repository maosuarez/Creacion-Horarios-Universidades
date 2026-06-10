# API – Generador de Horarios con Preferencias y Tiempo Libre

Esta API procesa un conjunto de preferencias académicas y restricciones de tiempo libre para generar combinaciones de horarios válidos. Su propósito es ayudar a construir posibles agendas de clases basadas en materias, profesores preferidos, códigos de curso permitidos y bloques horarios que el usuario desea mantener libres.

## Objetivo General

Tomar un **payload JSON** que contiene preferencias detalladas por materia y horarios de tiempo libre, luego devolver una **lista de posibles horarios completos**, filtrados y construidos según las reglas definidas por el usuario.

---

## Flujo de Funcionamiento

### 1. Recepción del Payload

La API recibe un JSON con dos secciones principales:

### `preferencias`

Define restricciones por materia. Cada materia puede incluir:

* **profesores**: lista opcional de profesores permitidos para esa materia.
* **codes**: lista opcional de códigos de curso permitidos.

Ejemplo:

```json
"preferencias": {
  "Cálculo I": {
    "profesores": ["Dr. Juan Pérez"],
    "codes": []
  },
  "Física I": {
    "profesores": [],
    "codes": [2001, 2002]
  },
  "Programación I": {
    "profesores": [],
    "codes": []
  }
}
```

Interpretación:

* Cálculo I solo puede dictarlo **Juan Pérez**.
* Física I debe seleccionarse exclusivamente entre los cursos **2001** y **2002**.
* Programación I no presenta restricciones.

---

### `freetime`

Define bloques horarios que deben quedar completamente libres. Cada día es una lista de horas bloqueadas:

```json
"freetime": {
  "monday": [12, 13, 14],
  "wednesday": [12, 13, 14],
  "friday": [16, 17, 18]
}
```

Interpretación:

* Lunes y miércoles de 12 a 14 están bloqueados.
* Viernes de 16 a 18 está bloqueado.

---

## 2. Carga de la Base de Datos de Cursos

La API consulta las entidades `Course`, `Teacher`, y `Schedule` o equivalentes para encontrar:

* Materias disponibles.
* Cursos ofrecidos por cada materia.
* Horarios específicos por curso.
* Profesor que dicta el curso.

---

## 3. Filtro por Preferencias

La API descarta automáticamente todos los cursos que no cumplan:

* El profesor solicitado (si existe restricción).
* El código permitido (si existe restricción).

Si una materia no tiene restricciones, se consideran todos los cursos posibles.

---

## 4. Filtro por Tiempo Libre

Para cada curso restante:

* Se inspeccionan todos sus bloques horarios.
* Se valida que **ningún bloque se cruce** con las horas marcadas como libres.
* Los cursos que chocan con el tiempo libre se eliminan.

---

## 5. Construcción de Combinaciones Posibles

Con los cursos válidos por cada materia, la API genera:

* Todas las posibles combinaciones entre materias.
* Filtra únicamente aquellas en las que **ningún curso se solapa** con otro.

Este proceso produce un conjunto de horarios que cumplen:

1. Todas las preferencias.
2. Todos los bloques de tiempo libre.
3. Ningún cruce de clases.

---

## 6. Respuesta Final

La API devuelve una **lista de horarios posibles**, donde cada horario contiene:

* Materias seleccionadas.
* Cursos específicos elegidos.
* Profesor asignado.
* Bloques horarios completos.

Ejemplo conceptual (no literal):

```json
[
  {
    "Cálculo I": { "code": 1010, "profesor": "Dr. Juan Pérez", "schedule": [...] },
    "Física I": { "code": 2001, "profesor": "Dra. López", "schedule": [...] },
    "Programación I": { "code": 3005, "profesor": "Ing. Torres", "schedule": [...] }
  },
  ...
]
```

---

## Endpoints Sugeridos

| Endpoint    | Método | Descripción                                                                           |
| ----------- | ------ | ------------------------------------------------------------------------------------- |
| `/health`   | GET    | Verificación simple de estado del servicio.                                           |

---

## Requisitos del Payload

* Debe incluir siempre las claves `preferencias` y `freetime`.
* Las materias usadas deben existir en el sistema.
* Los profesores o codes proporcionados deben estar en la base de datos; de lo contrario serán ignorados o filtrarán todos los cursos.

---

## Casos de Uso Comunes

* Generación de horarios académicos personalizados.
* Filtrado automático de cursos según disponibilidad del usuario.
* Planificación de semestres con restricciones estrictas.
* Construcción rápida de múltiples alternativas de horario.

---

## Beneficios

* Ahorra tiempo al evitar la construcción manual de horarios.
* Asegura cumplimiento de profesores preferidos y códigos permitidos.
* Garantiza respeto de horarios libres.
* Devuelve múltiples combinaciones válidas optimizadas por compatibilidad.
