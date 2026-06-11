# Eligiendo Mi Camino — Ecuador

Orientación vocacional para estudiantes de **3ro de bachillerato** en Ecuador.
Adaptación de la plataforma [Eligiendo Mi Camino](https://ezequielmolina-lang.github.io/eligiendo-mi-camino/)
(Perú · Banco Mundial × uDocz) con datos del sistema educativo y laboral ecuatoriano.

App de una sola página (React + Tailwind vía CDN). Para verla localmente:

```bash
python -m http.server 8753
# abre http://localhost:8753
```

## Qué cambia respecto a la versión de Perú

- **Marco institucional**: SENESCYT, CES, CACES, INEC, SECAP, MAATE, MSP/IESS, SRI, IIGE… (en lugar de SUNEDU, INEI, MINEDU, MTPE, etc.)
- **Rutas post-bachillerato**: universidad (4–5 años, **gratuita en la pública**), institutos técnicos/tecnológicos (2–2.5 años), SECAP/formación artesanal, Fuerzas Armadas/Policía (ESMIL, ESSUNA, ESMA), y trabajo directo.
- **Admisión**: ya no hay examen nacional único (eliminado en 2023); cada universidad pública define su proceso tras el **Registro Nacional** de la SENESCYT.
- **Salarios en USD** (Ecuador está dolarizado); piso de referencia **SBU 2026 = $482**.
- **130 ocupaciones** con estimaciones de ingreso joven/experimentado en USD.
- Mascota: **Gallo de la Peña** (*Rupicola peruvianus*), ave de los bosques nublados del Ecuador (Mindo).

## Fuentes de datos (2025–2026)

- **INEC – Encuesta Nacional de Empleo (ENEMDU) anual 2025**: ingreso laboral por nivel
  educativo, informalidad, empleo adecuado, NiNis y la partición de actividad juvenil
  (cálculo propio sobre microdatos).
- **SENESCYT / CES / CACES**: cupos, gratuidad, deserción, becas, registro de instituciones
  (verificación en `infoeducacionsuperior.gob.ec`).
- **Ministerio del Trabajo**: SBU 2026 ($482); Encuentra Empleo.
- **Guías salariales de mercado**: Computrabajo Ecuador, Multitrabajos Index, escalas
  públicas (MSP, Magisterio) y prensa especializada.

> Nota: Ecuador **no** cuenta con un portal oficial de salarios por carrera (a diferencia
> de "Ponte en Carrera" en Perú), por lo que las cifras por ocupación son **estimaciones de
> mercado** redondeadas, no un registro oficial.

## Reproducir la adaptación

El contenido se genera de forma auditable a partir del HTML original de la versión de Perú:

```bash
python transform.py    # renombra instituciones, empresas, universidades, mascota, etc.
python fill_data.py     # inyecta datos de Ecuador: salarios USD, estadísticas, rutas, mitos
```

Cada reemplazo verifica su número de coincidencias y falla en voz alta si algo no calza.

---

Banco Mundial × uDocz · `<AIdea>` · Powered by Anthropic
