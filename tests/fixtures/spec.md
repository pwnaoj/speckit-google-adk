# Feature Specification: Guía educativa de Colombia

**Feature Branch**: `001-colombia-guide`
**Status**: Draft
**Input**: Agente educativo que responde preguntas sobre Colombia usando el MCP de API Colombia.

## User Scenarios & Testing

### User Story 1 - Información de un departamento (Priority: P1)

Un estudiante pregunta por datos básicos de un departamento y recibe una explicación clara basada en datos oficiales de API Colombia.

**Acceptance Scenarios**:

1. **Given** el agente está disponible, **When** el usuario pregunta qué ciudades tiene el departamento de Boyacá, **Then** el agente lista ciudades de Boyacá obtenidas de API Colombia y las explica en tono educativo.
2. **Given** el agente está disponible, **When** el usuario pregunta cuáles son los atractivos turísticos del departamento de Santander, **Then** el agente presenta atractivos turísticos de Santander obtenidos de API Colombia.

---

### User Story 2 - Datos generales del país (Priority: P2)

Un usuario curioso pregunta datos generales de Colombia (idioma, moneda, zona horaria).

**Acceptance Scenarios**:

1. **Given** el agente está disponible, **When** el usuario pregunta qué moneda y qué idiomas se usan en Colombia, **Then** el agente responde con la moneda y los idiomas obtenidos de API Colombia.

---

### User Story 3 - Preguntas fuera de alcance (Priority: P3)

El agente reconoce lo que no puede responder y no inventa datos.

**Acceptance Scenarios**:

1. **Given** el agente está disponible, **When** el usuario pregunta por el clima de mañana en Bogotá, **Then** el agente explica que no dispone de ese dato y sugiere temas que sí puede tratar, sin inventar información.

### Edge Cases

- El usuario escribe el nombre de un departamento sin tildes.
- La consulta a API Colombia no devuelve resultados.

## Requirements

### Functional Requirements

- **FR-001**: El agente MUST obtener los datos desde el MCP de API Colombia y no desde conocimiento propio.
- **FR-002**: El agente MUST responder en español con un tono educativo y claro.
- **FR-003**: El agente MUST declarar cuando no tiene un dato y no inventarlo.
- **FR-004**: El agente MUST poder consultar ciudades y atractivos turísticos por departamento, y datos generales del país.

## Success Criteria

- **SC-001**: Todos los escenarios de aceptación pasan en la evaluación automática.
