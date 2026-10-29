---
scope: reusable user prompt for migrating target project instructions to globally loaded shared guidance
load_when: the user requests the same instruction migration in another project
depends_on: []
---
# Project Instruction Migration Prompt

Document type: Reusable prompt.
Status: Active task artifact, 2026-10-26; not runtime policy.
Scope: Copy the text below as a user request in the target project's chat.

The prompt deliberately does not identify the shared guidance package. The active global instructions supply its identity and loading contract.

## Prompt to copy

```text
Implementa en este proyecto la separación entre instrucciones comunes cargadas globalmente e instrucciones específicas del repositorio.

Objetivo:
- El AGENTS.md global debe ser un cargador estable de una sola referencia a la entrada de las instrucciones comunes. No debe copiar reglas, enumerar documentos internos ni fijar versiones o commits.
- El AGENTS.md del proyecto y sus guías activas no deben conocer el nombre, repositorio, ruta, versión ni estructura de la fuente de instrucciones comunes. Deben contener únicamente las particularidades del proyecto.

Procedimiento:
1. Inspecciona las instrucciones globales efectivamente aplicables, sus posibles overrides, el contrato de carga común, las instrucciones del proyecto, su índice documental y los cambios locales.
2. Si el cargador global ya es correcto, reutilízalo sin modificarlo. Si necesita ajustes, prepara el contenido mínimo y usa el mecanismo de permisos disponible; no sobrescribas preferencias o políticas existentes.
3. Inventaría las reglas actuales. Conserva arquitectura, plataforma, compilación, datos, seguridad específica, selectores, localización, comandos, pruebas y demás contratos propios del proyecto.
4. Retira del proyecto únicamente las reglas comunes cuyo reemplazo canónico esté comprobado y las referencias operativas a su fuente. Conserva las reglas únicas o de clasificación dudosa hasta resolverlas. No copies reglas comunes a otro archivo del proyecto.
5. Actualiza los AGENTS.md aplicables, archivos de instrucciones de herramientas, configuraciones especialistas, índices y guías afectados. Conserva los registros históricos con su alcance y evidencia, marcando como histórico el mecanismo anterior.
6. No modifiques código de aplicación, bases de datos, infraestructura ni cambios ajenos. No actualices automáticamente la fuente común ni hagas commit, push o despliegue.
7. Comprueba conservación de reglas específicas, ausencia de referencias activas a la fuente común, enlaces, dependencias, índices, formato y diferencias. Respeta las restricciones de compilación del proyecto.
8. Cuando sea posible, verifica la carga en una sesión nueva de solo lectura y la independencia de actualización mediante una fixture aislada. Si no puedes ejecutar alguna comprobación, declara exactamente lo pendiente.

La autorización de esta solicitud cubre la migración de instrucciones y la actualización de su documentación, incluidos los ajustes necesarios del cargador global descritos arriba. Respeta la jerarquía efectiva y los límites técnicos del entorno.

Entrega los archivos cambiados, las reglas retiradas y su dueño canónico, las reglas específicas conservadas, las comprobaciones realizadas y cualquier limitación pendiente.
```
