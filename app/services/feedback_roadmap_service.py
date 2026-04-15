# from __future__ import annotations

# import json
# import re
# from datetime import datetime, timezone
# from typing import Any

# import requests
# from sqlalchemy.orm import Session

# from app.core.config import settings
# from app.models.perfil_estudiante import PerfilEstudiante
# from app.models.postulacion import Postulacion
# from app.models.retroalimentacion import Retroalimentacion
# from app.models.vacante import Vacante
# from app.schemas.retroalimentacion import RoadmapData


# SYSTEM_PROMPT = """Eres un mentor profesional especializado en empleabilidad, desarrollo de habilidades y preparación de estudiantes para el mercado laboral.

# Tu tarea es analizar la retroalimentación proporcionada por una empresa, junto con el contexto de la vacante y el perfil del estudiante, para generar un roadmap personalizado, claro, estructurado y accionable que le ayude a mejorar para futuras postulaciones.

# Analiza cuidadosamente la siguiente información:

# RETROALIMENTACION_EMPRESA
# - campos_mejora: {campos_mejora}
# - sugerencias_perfil: {sugerencias_perfil}

# PERFIL_ESTUDIANTE
# - nivel_academico: {nivel_academico}
# - institucion_educativa: {institucion_educativa}
# - ubicacion: {ubicacion}
# - modalidad_preferida: {modalidad_preferida}
# - habilidades_actuales: {habilidades_actuales}
# - resumen_perfil: {resumen_perfil}

# VACANTE
# - titulo: {vacante_titulo}
# - descripcion: {vacante_descripcion}
# - requisitos: {vacante_requisitos}
# - modalidad: {vacante_modalidad}
# - ubicacion: {vacante_ubicacion}

# POSTULACION
# - source: {postulacion_source}
# - estado: {postulacion_estado}

# INSTRUCCIONES:
# 1. Identifica la brecha entre el perfil actual del estudiante y lo que exigía la vacante.
# 2. Prioriza mejoras que aumenten su empleabilidad real en futuras postulaciones similares.
# 3. No repitas literalmente la retroalimentación: tradúcela en un plan práctico.
# 4. Si la retroalimentación es vaga, usa el perfil y la vacante para inferir mejoras razonables sin inventar datos irrelevantes.
# 5. Adapta el roadmap a un estudiante con poca o nula experiencia laboral.

# Genera un roadmap personalizado que incluya:
# - habilidades
# - acciones
# - recursos
# - tiempo_estimado
# - prioridad
# - roadmap_detallado

# REGLAS IMPORTANTES:
# - Responde ÚNICAMENTE en JSON válido.
# - No incluyas texto fuera del JSON.
# - Sé específico y práctico.
# - Las acciones deben ser ejecutables y medibles.
# - Los recursos deben ser realistas y no inventar enlaces.
# - Enfócate en empleabilidad real.
# - Si falta información, usa solo lo disponible y no inventes experiencia.
# - Usa español neutro.

# FORMATO:
# {{
#   "habilidades": ["string"],
#   "acciones": ["string"],
#   "recursos": ["string"],
#   "tiempo_estimado": "string",
#   "prioridad": "string",
#   "roadmap_detallado": [
#     {{
#       "semana": "string",
#       "objetivo": "string",
#       "tareas": ["string"]
#     }}
#   ]
# }}"""


# KNOWN_SKILL_TEMPLATES = {
#     "sql": {
#         "skill": "SQL aplicado a vacantes reales",
#         "actions": [
#             "Resolver 15 ejercicios de consultas con JOIN, GROUP BY y subconsultas.",
#             "Construir una base de datos pequeña para un proyecto personal y documentar 10 consultas útiles.",
#         ],
#         "resources": ["SQLBolt", "Mode SQL Tutorial", "LeetCode SQL"],
#     },
#     "python": {
#         "skill": "Python orientado a resolución de problemas",
#         "actions": [
#             "Resolver 3 ejercicios semanales de estructuras de datos y manejo de archivos en Python.",
#             "Desarrollar un script automatizado con validaciones y manejo de errores.",
#         ],
#         "resources": ["Exercism Python", "Docs oficiales de Python", "Kaggle Learn Python"],
#     },
#     "fastapi": {
#         "skill": "Desarrollo backend con APIs",
#         "actions": [
#             "Crear una API CRUD con FastAPI, validaciones y documentación automática.",
#             "Publicar el proyecto en GitHub con instrucciones de ejecución y ejemplos de requests.",
#         ],
#         "resources": ["Documentación de FastAPI", "Repositorio personal en GitHub", "Postman"],
#     },
#     "django": {
#         "skill": "Desarrollo backend con Django",
#         "actions": [
#             "Construir un proyecto CRUD con autenticación básica en Django.",
#             "Desplegar una demo funcional y documentar las decisiones técnicas.",
#         ],
#         "resources": ["Documentación de Django", "Railway o Render", "GitHub Projects"],
#     },
#     "backend": {
#         "skill": "Desarrollo de proyectos backend demostrables",
#         "actions": [
#             "Construir un proyecto backend pequeño con autenticación, persistencia y documentación.",
#             "Agregar README técnico con arquitectura, endpoints y decisiones de diseño.",
#         ],
#         "resources": ["GitHub", "Postman", "Render o Railway"],
#     },
#     "frontend": {
#         "skill": "Presentación de proyectos frontend",
#         "actions": [
#             "Construir una interfaz responsive que consuma una API real o simulada.",
#             "Documentar capturas, decisiones de UX y mejoras futuras en el repositorio.",
#         ],
#         "resources": ["MDN", "Frontend Mentor", "GitHub Pages"],
#     },
#     "portafolio": {
#         "skill": "Presentación técnica del portafolio",
#         "actions": [
#             "Subir al menos 2 proyectos con README claro, stack, capturas y aprendizajes.",
#             "Destacar el problema, la solución y el resultado de cada proyecto.",
#         ],
#         "resources": ["GitHub", "Notion", "README templates"],
#     },
#     "perfil": {
#         "skill": "Optimización del perfil profesional",
#         "actions": [
#             "Reescribir la biografía resaltando habilidades, herramientas y tipo de vacantes objetivo.",
#             "Actualizar el perfil con 5 habilidades concretas y evidencia de proyectos.",
#         ],
#         "resources": ["LinkedIn", "GitHub", "Plantilla de CV ATS"],
#     },
#     "cv": {
#         "skill": "Mejora de CV orientado a empleabilidad",
#         "actions": [
#             "Actualizar el CV para incluir logros medibles, stack tecnológico y proyectos relevantes.",
#             "Ajustar el CV para que el resumen profesional coincida con vacantes similares.",
#         ],
#         "resources": ["Canva CV", "Plantilla ATS", "Overleaf"],
#     },
#     "entrevista": {
#         "skill": "Preparación para entrevistas técnicas",
#         "actions": [
#             "Practicar 2 simulaciones de entrevista explicando proyectos, decisiones y resultados.",
#             "Preparar respuestas cortas sobre fortalezas, áreas de mejora y experiencia académica.",
#         ],
#         "resources": ["Pramp", "YouTube entrevistas técnicas", "Notas personales"],
#     },
# }


# def generate_roadmap_for_postulacion(db: Session, postulacion_id: int) -> Retroalimentacion | None:
#     retroalimentacion = (
#         db.query(Retroalimentacion)
#         .filter(Retroalimentacion.postulacion_id == postulacion_id)
#         .first()
#     )
#     if not retroalimentacion:
#         return None
#     return generate_roadmap_for_retroalimentacion(db, retroalimentacion)


# def generate_roadmap_for_retroalimentacion(
#     db: Session,
#     retroalimentacion: Retroalimentacion,
# ) -> Retroalimentacion:
#     postulacion = db.query(Postulacion).filter(Postulacion.id == retroalimentacion.postulacion_id).first()
#     if not postulacion:
#         retroalimentacion.roadmap_estado = "error"
#         retroalimentacion.roadmap_error = "Postulacion no encontrada"
#         db.flush()
#         return retroalimentacion

#     perfil = (
#         db.query(PerfilEstudiante)
#         .filter(PerfilEstudiante.usuario_id == postulacion.estudiante_id)
#         .first()
#     )
#     vacante = db.query(Vacante).filter(Vacante.id == postulacion.vacante_id).first()

#     context = _build_context_payload(retroalimentacion, postulacion, perfil, vacante)
#     retroalimentacion.roadmap_json = None
#     retroalimentacion.roadmap_generado_en = None
#     retroalimentacion.roadmap_error = None
#     retroalimentacion.roadmap_estado = "pendiente"

#     try:
#         roadmap_dict = _generate_roadmap_payload(context)
#         roadmap = RoadmapData.model_validate(roadmap_dict)
#         retroalimentacion.roadmap_json = roadmap.model_dump()
#         retroalimentacion.roadmap_estado = "generado"
#         retroalimentacion.roadmap_generado_en = datetime.now(timezone.utc)
#         retroalimentacion.roadmap_error = None
#     except Exception as exc:
#         retroalimentacion.roadmap_json = None
#         retroalimentacion.roadmap_estado = "error"
#         retroalimentacion.roadmap_generado_en = None
#         retroalimentacion.roadmap_error = str(exc)

#     db.flush()
#     return retroalimentacion


# def _build_context_payload(
#     retroalimentacion: Retroalimentacion,
#     postulacion: Postulacion,
#     perfil: PerfilEstudiante | None,
#     vacante: Vacante | None,
# ) -> dict[str, Any]:
#     habilidades = perfil.habilidades if perfil and perfil.habilidades else []
#     if isinstance(habilidades, str):
#         habilidades_texto = habilidades
#     else:
#         habilidades_texto = ", ".join(str(item) for item in habilidades) if habilidades else "No especificadas"

#     return {
#         "campos_mejora": retroalimentacion.campos_mejora or "No especificado",
#         "sugerencias_perfil": retroalimentacion.sugerencias_perfil or "No especificado",
#         "nivel_academico": perfil.nivel_academico if perfil and perfil.nivel_academico else "No especificado",
#         "institucion_educativa": perfil.institucion_educativa if perfil and perfil.institucion_educativa else "No especificado",
#         "ubicacion": perfil.ubicacion if perfil and perfil.ubicacion else "No especificado",
#         "modalidad_preferida": (
#             perfil.modalidad_preferida if perfil and perfil.modalidad_preferida else "No especificada"
#         ),
#         "habilidades_actuales": habilidades_texto,
#         "resumen_perfil": perfil.biografia if perfil and perfil.biografia else "No especificado",
#         "vacante_titulo": vacante.titulo if vacante and vacante.titulo else "No especificado",
#         "vacante_descripcion": vacante.descripcion if vacante and vacante.descripcion else "No especificado",
#         "vacante_requisitos": vacante.requisitos if vacante and vacante.requisitos else "No especificado",
#         "vacante_modalidad": vacante.modalidad if vacante and vacante.modalidad else "No especificada",
#         "vacante_ubicacion": vacante.ubicacion if vacante and vacante.ubicacion else "No especificada",
#         "postulacion_source": postulacion.source,
#         "postulacion_estado": postulacion.estado,
#     }


# def _generate_roadmap_payload(context: dict[str, Any]) -> dict[str, Any]:
#     if settings.ROADMAP_AI_MODE.lower() == "openai" and settings.ROADMAP_AI_API_KEY:
#         try:
#             return _generate_with_openai(context)
#         except Exception:
#             return _generate_heuristic(context)
#     return _generate_heuristic(context)


# def _generate_with_openai(context: dict[str, Any]) -> dict[str, Any]:
#     response = requests.post(
#         settings.ROADMAP_AI_BASE_URL,
#         headers={
#             "Authorization": f"Bearer {settings.ROADMAP_AI_API_KEY}",
#             "Content-Type": "application/json",
#         },
#         json={
#             "model": settings.ROADMAP_AI_MODEL,
#             "temperature": 0.3,
#             "response_format": {"type": "json_object"},
#             "messages": [
#                 {
#                     "role": "system",
#                     "content": SYSTEM_PROMPT.format(**context),
#                 }
#             ],
#         },
#         timeout=settings.ROADMAP_AI_TIMEOUT_SECONDS,
#     )
#     response.raise_for_status()
#     data = response.json()
#     content = data["choices"][0]["message"]["content"]
#     if not isinstance(content, str):
#         raise ValueError("La respuesta del proveedor de IA no contiene texto JSON")
#     return json.loads(_strip_code_fences(content))


# def _strip_code_fences(value: str) -> str:
#     cleaned = value.strip()
#     cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.IGNORECASE)
#     cleaned = re.sub(r"^```\s*", "", cleaned)
#     cleaned = re.sub(r"\s*```$", "", cleaned)
#     return cleaned.strip()


# def _generate_heuristic(context: dict[str, Any]) -> dict[str, Any]:
#     student_skills = _tokenize(context["habilidades_actuales"])
#     focus_areas = _extract_focus_areas(context)
#     skills: list[str] = []
#     actions: list[str] = []
#     resources: list[str] = []

#     for area in focus_areas:
#         template = _match_template(area)
#         if template:
#             skills.append(template["skill"])
#             actions.extend(template["actions"])
#             resources.extend(template["resources"])
#         else:
#             normalized = area.strip().capitalize()
#             skills.append(normalized)
#             actions.append(f"Practicar {area.strip()} con un entregable concreto alineado a vacantes similares.")
#             actions.append(f"Documentar avances semanales sobre {area.strip()} en GitHub o portafolio personal.")
#             resources.extend(["GitHub", "LinkedIn", "Cursos introductorios del tema"])

#     if not skills:
#         skills = [
#             "Comunicación clara del perfil profesional",
#             "Presentación de proyectos alineados a la vacante",
#         ]
#         actions = [
#             "Actualizar la biografía del perfil para describir stack, intereses y tipo de vacantes objetivo.",
#             "Publicar al menos 2 proyectos con README técnico, capturas y aprendizajes.",
#         ]
#         resources = ["GitHub", "LinkedIn", "Plantilla ATS"]

#     if "github" not in {item.lower() for item in resources}:
#         resources.append("GitHub")

#     missing_from_vacancy = [
#         token for token in _tokenize(context["vacante_requisitos"]) if token not in student_skills
#     ]
#     if missing_from_vacancy:
#         skill_label = f"Refuerzo de {missing_from_vacancy[0].upper()} aplicado a la vacante"
#         if skill_label not in skills:
#             skills.append(skill_label)
#             actions.append(
#                 f"Crear una evidencia práctica donde uses {missing_from_vacancy[0].upper()} en un proyecto corto relacionado con la vacante."
#             )

#     skills = _unique_list(skills, limit=5)
#     actions = _unique_list(actions, limit=8)
#     resources = _unique_list(resources, limit=6)

#     roadmap_steps = [
#         {
#             "semana": "Semana 1",
#             "objetivo": "Cerrar brechas técnicas principales detectadas en la retroalimentación.",
#             "tareas": _unique_list(actions[:3], limit=3),
#         },
#         {
#             "semana": "Semana 2",
#             "objetivo": "Convertir la práctica en evidencia visible para futuras postulaciones.",
#             "tareas": _unique_list(actions[3:6] or actions[:3], limit=3),
#         },
#         {
#             "semana": "Semana 3",
#             "objetivo": "Ajustar perfil, CV y portafolio para vacantes similares.",
#             "tareas": [
#                 "Actualizar el perfil con habilidades verificables y proyectos relevantes.",
#                 "Revisar el CV para alinear resumen, stack y experiencia académica.",
#                 "Preparar una nueva postulación adaptando el perfil a requisitos similares.",
#             ],
#         },
#     ]

#     return {
#         "habilidades": skills,
#         "acciones": actions,
#         "recursos": resources,
#         "tiempo_estimado": "3 semanas",
#         "prioridad": "Alta",
#         "roadmap_detallado": roadmap_steps,
#     }


# def _extract_focus_areas(context: dict[str, Any]) -> list[str]:
#     text = " ".join(
#         [
#             str(context.get("campos_mejora", "")),
#             str(context.get("sugerencias_perfil", "")),
#             str(context.get("vacante_titulo", "")),
#             str(context.get("vacante_requisitos", "")),
#         ]
#     )
#     candidates = re.split(r"[,\n;/]| y | e ", text, flags=re.IGNORECASE)
#     cleaned = []
#     for candidate in candidates:
#         item = candidate.strip(" .:-")
#         if len(item) < 3:
#             continue
#         cleaned.append(item)
#     return _unique_list(cleaned, limit=6)


# def _match_template(area: str) -> dict[str, Any] | None:
#     normalized = area.lower()
#     for keyword, template in KNOWN_SKILL_TEMPLATES.items():
#         if keyword in normalized:
#             return template
#     return None


# def _tokenize(value: Any) -> list[str]:
#     if value is None:
#         return []
#     if isinstance(value, list):
#         text = " ".join(str(item) for item in value)
#     else:
#         text = str(value)
#     return re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{1,20}", text.lower())


# def _unique_list(items: list[str], limit: int) -> list[str]:
#     result: list[str] = []
#     seen: set[str] = set()
#     for item in items:
#         normalized = item.strip()
#         if not normalized:
#             continue
#         key = normalized.lower()
#         if key in seen:
#             continue
#         seen.add(key)
#         result.append(normalized)
#         if len(result) >= limit:
#             break
#     return result


from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any

import google.generativeai as genai
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.perfil_estudiante import PerfilEstudiante
from app.models.postulacion import Postulacion
from app.models.retroalimentacion import Retroalimentacion
from app.models.vacante import Vacante
from app.schemas.retroalimentacion import RoadmapData

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Eres un mentor profesional especializado en empleabilidad, desarrollo de habilidades y preparación de estudiantes para el mercado laboral.

Tu tarea es analizar la retroalimentación proporcionada por una empresa, junto con el contexto de la vacante y el perfil del estudiante, para generar un roadmap personalizado, claro, estructurado y accionable que le ayude a mejorar para futuras postulaciones.

Analiza cuidadosamente la siguiente información:

RETROALIMENTACION_EMPRESA
- campos_mejora: {campos_mejora}
- sugerencias_perfil: {sugerencias_perfil}

PERFIL_ESTUDIANTE
- nivel_academico: {nivel_academico}
- institucion_educativa: {institucion_educativa}
- ubicacion: {ubicacion}
- modalidad_preferida: {modalidad_preferida}
- habilidades_actuales: {habilidades_actuales}
- resumen_perfil: {resumen_perfil}

VACANTE
- titulo: {vacante_titulo}
- descripcion: {vacante_descripcion}
- requisitos: {vacante_requisitos}
- modalidad: {vacante_modalidad}
- ubicacion: {vacante_ubicacion}

POSTULACION
- source: {postulacion_source}
- estado: {postulacion_estado}

INSTRUCCIONES:
1. Identifica la brecha entre el perfil actual del estudiante y lo que exigía la vacante.
2. Prioriza mejoras que aumenten su empleabilidad real en futuras postulaciones similares.
3. No repitas literalmente la retroalimentación: tradúcela en un plan práctico.
4. Si la retroalimentación es vaga, usa el perfil y la vacante para inferir mejoras razonables sin inventar datos irrelevantes.
5. Adapta el roadmap a un estudiante con poca o nula experiencia laboral.

Genera un roadmap personalizado que incluya:
- habilidades
- acciones
- recursos
- tiempo_estimado
- prioridad
- roadmap_detallado

REGLAS IMPORTANTES:
- Responde ÚNICAMENTE en JSON válido.
- No incluyas texto fuera del JSON.
- Sé específico y práctico.
- Las acciones deben ser ejecutables y medibles.
- Los recursos deben ser realistas y no inventar enlaces.
- Enfócate en empleabilidad real.
- Si falta información, usa solo lo disponible y no inventes experiencia.
- Usa español neutro.

FORMATO:
{{
  "habilidades": ["string"],
  "acciones": ["string"],
  "recursos": ["string"],
  "tiempo_estimado": "string",
  "prioridad": "string",
  "roadmap_detallado": [
    {{
      "semana": "string",
      "objetivo": "string",
      "tareas": ["string"]
    }}
  ]
}}"""


KNOWN_SKILL_TEMPLATES = {
    "sql": {
        "skill": "SQL aplicado a vacantes reales",
        "actions": [
            "Resolver 15 ejercicios de consultas con JOIN, GROUP BY y subconsultas.",
            "Construir una base de datos pequena para un proyecto personal y documentar 10 consultas utiles.",
        ],
        "resources": ["SQLBolt", "Mode SQL Tutorial", "LeetCode SQL"],
    },
    "python": {
        "skill": "Python orientado a resolucion de problemas",
        "actions": [
            "Resolver 3 ejercicios semanales de estructuras de datos y manejo de archivos en Python.",
            "Desarrollar un script automatizado con validaciones y manejo de errores.",
        ],
        "resources": ["Exercism Python", "Docs oficiales de Python", "Kaggle Learn Python"],
    },
    "fastapi": {
        "skill": "Desarrollo backend con APIs",
        "actions": [
            "Crear una API CRUD con FastAPI, validaciones y documentacion automatica.",
            "Publicar el proyecto en GitHub con instrucciones de ejecucion y ejemplos de requests.",
        ],
        "resources": ["Documentacion de FastAPI", "Repositorio personal en GitHub", "Postman"],
    },
    "django": {
        "skill": "Desarrollo backend con Django",
        "actions": [
            "Construir un proyecto CRUD con autenticacion basica en Django.",
            "Desplegar una demo funcional y documentar las decisiones tecnicas.",
        ],
        "resources": ["Documentacion de Django", "Railway o Render", "GitHub Projects"],
    },
    "backend": {
        "skill": "Desarrollo de proyectos backend demostrables",
        "actions": [
            "Construir un proyecto backend pequeno con autenticacion, persistencia y documentacion.",
            "Agregar README tecnico con arquitectura, endpoints y decisiones de diseno.",
        ],
        "resources": ["GitHub", "Postman", "Render o Railway"],
    },
    "frontend": {
        "skill": "Presentacion de proyectos frontend",
        "actions": [
            "Construir una interfaz responsive que consuma una API real o simulada.",
            "Documentar capturas, decisiones de UX y mejoras futuras en el repositorio.",
        ],
        "resources": ["MDN", "Frontend Mentor", "GitHub Pages"],
    },
    "portafolio": {
        "skill": "Presentacion tecnica del portafolio",
        "actions": [
            "Subir al menos 2 proyectos con README claro, stack, capturas y aprendizajes.",
            "Destacar el problema, la solucion y el resultado de cada proyecto.",
        ],
        "resources": ["GitHub", "Notion", "README templates"],
    },
    "perfil": {
        "skill": "Optimizacion del perfil profesional",
        "actions": [
            "Reescribir la biografia resaltando habilidades, herramientas y tipo de vacantes objetivo.",
            "Actualizar el perfil con 5 habilidades concretas y evidencia de proyectos.",
        ],
        "resources": ["LinkedIn", "GitHub", "Plantilla de CV ATS"],
    },
    "cv": {
        "skill": "Mejora de CV orientado a empleabilidad",
        "actions": [
            "Actualizar el CV para incluir logros medibles, stack tecnologico y proyectos relevantes.",
            "Ajustar el CV para que el resumen profesional coincida con vacantes similares.",
        ],
        "resources": ["Canva CV", "Plantilla ATS", "Overleaf"],
    },
    "entrevista": {
        "skill": "Preparacion para entrevistas tecnicas",
        "actions": [
            "Practicar 2 simulaciones de entrevista explicando proyectos, decisiones y resultados.",
            "Preparar respuestas cortas sobre fortalezas, areas de mejora y experiencia academica.",
        ],
        "resources": ["Pramp", "YouTube entrevistas tecnicas", "Notas personales"],
    },
}


def generate_roadmap_for_postulacion(db: Session, postulacion_id: int) -> Retroalimentacion | None:
    retroalimentacion = (
        db.query(Retroalimentacion)
        .filter(Retroalimentacion.postulacion_id == postulacion_id)
        .first()
    )
    if not retroalimentacion:
        return None
    return generate_roadmap_for_retroalimentacion(db, retroalimentacion)

def generate_roadmap_for_retroalimentacion(
    db: Session,
    retroalimentacion: Retroalimentacion,
) -> Retroalimentacion:
    postulacion = db.query(Postulacion).filter(Postulacion.id == retroalimentacion.postulacion_id).first()
    if not postulacion:
        retroalimentacion.roadmap_estado = "error"
        retroalimentacion.roadmap_error = "Postulacion no encontrada"
        db.flush()
        return retroalimentacion

    perfil = (
        db.query(PerfilEstudiante)
        .filter(PerfilEstudiante.usuario_id == postulacion.estudiante_id)
        .first()
    )
    vacante = db.query(Vacante).filter(Vacante.id == postulacion.vacante_id).first()

    context = _build_context_payload(retroalimentacion, postulacion, perfil, vacante)

    retroalimentacion.roadmap_json = None
    retroalimentacion.roadmap_generado_en = None
    retroalimentacion.roadmap_error = None
    retroalimentacion.roadmap_estado = "pendiente"

    try:
        roadmap_dict = _generate_roadmap_payload(context)
        roadmap = RoadmapData.model_validate(roadmap_dict)
        retroalimentacion.roadmap_json = roadmap.model_dump()
        retroalimentacion.roadmap_estado = "generado"
        retroalimentacion.roadmap_generado_en = datetime.now(timezone.utc)
        retroalimentacion.roadmap_error = None
        logger.info(
            "Roadmap generado correctamente para postulacion_id=%s usando modo=%s",
            postulacion.id,
            settings.ROADMAP_AI_MODE,
        )
    except Exception as exc:
        error_detail = str(exc)
        retroalimentacion.roadmap_json = None
        retroalimentacion.roadmap_estado = "error"
        retroalimentacion.roadmap_error = error_detail
        logger.error(
            "Error generando roadmap para postulacion_id=%s | modo=%s | modelo=%s | error: %s",
            postulacion.id,
            settings.ROADMAP_AI_MODE,
            settings.ROADMAP_AI_MODEL,
            error_detail,
            exc_info=True,
        )

    db.flush()
    return retroalimentacion

def _build_context_payload(
    retroalimentacion: Retroalimentacion,
    postulacion: Postulacion,
    perfil: PerfilEstudiante | None,
    vacante: Vacante | None,
) -> dict[str, Any]:
    # Limpieza básica de habilidades para el prompt
    habilidades = perfil.habilidades if perfil and perfil.habilidades else []
    habilidades_texto = ", ".join(habilidades) if isinstance(habilidades, list) else str(habilidades)

    return {
        "campos_mejora": retroalimentacion.campos_mejora or "No especificado",
        "sugerencias_perfil": retroalimentacion.sugerencias_perfil or "No especificado",
        "nivel_academico": perfil.nivel_academico if perfil else "No especificado",
        "institucion_educativa": perfil.institucion_educativa if perfil else "No especificado",
        "habilidades_actuales": habilidades_texto,
        "resumen_perfil": perfil.biografia if perfil else "No especificado",
        "vacante_titulo": vacante.titulo if vacante else "No especificado",
        "vacante_descripcion": vacante.descripcion if vacante else "No especificado",
        "vacante_requisitos": vacante.requisitos if vacante else "No especificado",
        "postulacion_estado": postulacion.estado,
        "postulacion_source": postulacion.source,
        "ubicacion": perfil.ubicacion if perfil else "No especificada",
        "modalidad_preferida": perfil.modalidad_preferida if perfil else "No especificada",
        "vacante_modalidad": vacante.modalidad if vacante else "No especificada",
        "vacante_ubicacion": vacante.ubicacion if vacante else "No especificada",
    }

def _generate_with_gemini(context: dict[str, Any]) -> dict[str, Any]:
    """
    Genera el roadmap usando el SDK nativo de Google Generative AI.
    """
    if not settings.ROADMAP_AI_API_KEY:
        raise ValueError("ROADMAP_AI_API_KEY no está configurada")

    logger.info(
        "Llamando a Gemini SDK | modelo=%s | timeout=%ss",
        settings.ROADMAP_AI_MODEL,
        settings.ROADMAP_AI_TIMEOUT_SECONDS,
    )

    genai.configure(api_key=settings.ROADMAP_AI_API_KEY)

    model = genai.GenerativeModel(
        model_name=settings.ROADMAP_AI_MODEL,
        system_instruction=SYSTEM_PROMPT.format(**context),
    )

    response = model.generate_content(
        "Genera el roadmap personalizado en JSON según las instrucciones del sistema.",
        generation_config=genai.GenerationConfig(temperature=0.3),
        request_options={"timeout": settings.ROADMAP_AI_TIMEOUT_SECONDS},
    )

    logger.info("Respuesta de Gemini SDK recibida | finish_reason=%s", response.candidates[0].finish_reason)

    content = response.text
    clean_content = _strip_code_fences(content)
    return json.loads(clean_content)


def _generate_roadmap_payload(context: dict[str, Any]) -> dict[str, Any]:
    if settings.ROADMAP_AI_MODE.lower() == "heuristic":
        logger.info("Modo heurístico activo (ROADMAP_AI_MODE=heuristic)")
        return _generate_heuristic(context)

    logger.info("Intentando generación con Gemini SDK (ROADMAP_AI_MODE=%s)", settings.ROADMAP_AI_MODE)
    return _generate_with_gemini(context)

def _strip_code_fences(value: str) -> str:
    cleaned = value.strip()
    cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def _generate_heuristic(context: dict[str, Any]) -> dict[str, Any]:
    student_skills = _tokenize(context["habilidades_actuales"])
    focus_areas = _extract_focus_areas(context)
    skills: list[str] = []
    actions: list[str] = []
    resources: list[str] = []

    for area in focus_areas:
        template = _match_template(area)
        if template:
            skills.append(template["skill"])
            actions.extend(template["actions"])
            resources.extend(template["resources"])
        else:
            normalized = area.strip().capitalize()
            skills.append(normalized)
            actions.append(f"Practicar {area.strip()} con un entregable concreto alineado a vacantes similares.")
            actions.append(f"Documentar avances semanales sobre {area.strip()} en GitHub o portafolio personal.")
            resources.extend(["GitHub", "LinkedIn", "Cursos introductorios del tema"])

    if not skills:
        skills = [
            "Comunicacion clara del perfil profesional",
            "Presentacion de proyectos alineados a la vacante",
        ]
        actions = [
            "Actualizar la biografia del perfil para describir stack, intereses y tipo de vacantes objetivo.",
            "Publicar al menos 2 proyectos con README tecnico, capturas y aprendizajes.",
        ]
        resources = ["GitHub", "LinkedIn", "Plantilla ATS"]

    if "github" not in {item.lower() for item in resources}:
        resources.append("GitHub")

    missing_from_vacancy = [
        token for token in _tokenize(context["vacante_requisitos"]) if token not in student_skills
    ]
    if missing_from_vacancy:
        skill_label = f"Refuerzo de {missing_from_vacancy[0].upper()} aplicado a la vacante"
        if skill_label not in skills:
            skills.append(skill_label)
            actions.append(
                f"Crear una evidencia practica donde uses {missing_from_vacancy[0].upper()} en un proyecto corto relacionado con la vacante."
            )

    skills = _unique_list(skills, limit=5)
    actions = _unique_list(actions, limit=8)
    resources = _unique_list(resources, limit=6)

    roadmap_steps = [
        {
            "semana": "Semana 1",
            "objetivo": "Cerrar brechas tecnicas principales detectadas en la retroalimentacion.",
            "tareas": _unique_list(actions[:3], limit=3),
        },
        {
            "semana": "Semana 2",
            "objetivo": "Convertir la practica en evidencia visible para futuras postulaciones.",
            "tareas": _unique_list(actions[3:6] or actions[:3], limit=3),
        },
        {
            "semana": "Semana 3",
            "objetivo": "Ajustar perfil, CV y portafolio para vacantes similares.",
            "tareas": [
                "Actualizar el perfil con habilidades verificables y proyectos relevantes.",
                "Revisar el CV para alinear resumen, stack y experiencia academica.",
                "Preparar una nueva postulacion adaptando el perfil a requisitos similares.",
            ],
        },
    ]

    return {
        "habilidades": skills,
        "acciones": actions,
        "recursos": resources,
        "tiempo_estimado": "3 semanas",
        "prioridad": "Alta",
        "roadmap_detallado": roadmap_steps,
    }


def _extract_focus_areas(context: dict[str, Any]) -> list[str]:
    text = " ".join(
        [
            str(context.get("campos_mejora", "")),
            str(context.get("sugerencias_perfil", "")),
            str(context.get("vacante_titulo", "")),
            str(context.get("vacante_requisitos", "")),
        ]
    )
    candidates = re.split(r"[,\n;/]| y | e ", text, flags=re.IGNORECASE)
    cleaned = []
    for candidate in candidates:
        item = candidate.strip(" .:-")
        if len(item) < 3:
            continue
        cleaned.append(item)
    return _unique_list(cleaned, limit=6)


def _match_template(area: str) -> dict[str, Any] | None:
    normalized = area.lower()
    for keyword, template in KNOWN_SKILL_TEMPLATES.items():
        if keyword in normalized:
            return template
    return None


def _tokenize(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        text = " ".join(str(item) for item in value)
    else:
        text = str(value)
    return re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{1,20}", text.lower())


def _unique_list(items: list[str], limit: int) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        normalized = item.strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(normalized)
        if len(result) >= limit:
            break
    return result
