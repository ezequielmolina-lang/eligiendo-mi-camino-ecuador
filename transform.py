# -*- coding: utf-8 -*-
"""
Transform eligiendo-mi-camino (Peru) -> Ecuador edition.

Design: reads the PRISTINE Peru source and writes the Ecuador copy, so it is
fully re-runnable (no double-application). Every replacement asserts its hit
count, so a missed/expanded match fails loudly and the run is auditable.

Ordering matters:
  1) whole-block array rewrites (myths, routes, home stats) -- match pristine
  2) specific multi-word string swaps (footers, counseling box, badges)
  3) per-field swaps (companies, institutions, study texts, durations)
  4) generic token cleanups LAST (any leftover bare 'MTPE', etc.)
"""
import io, os, sys

SRC = os.path.join('..', 'eligiendo-mi-camino', 'index.html')
DST = 'index.html'

src = io.open(SRC, encoding='utf-8').read()
log, errors = [], []

def rep(old, new, n=1, label=''):
    global src
    found = src.count(old)
    if found != n:
        errors.append(f"[{label or old[:55]}] expected {n}, found {found}")
        return
    src = src.replace(old, new)
    log.append(f"ok x{n}: {label or old[:55]}")

def rep_all(old, new, min_n=1, label=''):
    global src
    found = src.count(old)
    if found < min_n:
        errors.append(f"[{label or old[:55]}] expected >={min_n}, found {found}")
        return
    src = src.replace(old, new)
    log.append(f"ok x{found}: {label or old[:55]}")

# ============================================================
# SECTION A — BRANDING / FRAMING
# ============================================================
rep('<title>Eligiendo Mi Camino — Programa Educativo</title>',
    '<title>Eligiendo Mi Camino Ecuador — Programa Educativo</title>', 1, 'title')
rep('Para estudiantes de 5to de secundaria en Lima',
    'Para estudiantes de 3ro de bachillerato en Ecuador', 1, 'audience')
rep('>Datos reales del Ministerio de Trabajo<',
    '>Datos reales del INEC y SENESCYT<', 1, 'welcome badge')

# ============================================================
# SECTION B — MASCOT: "Gallito de las Rocas" (ave nacional del Perú)
#   -> "Gallo de la Peña" (nombre ecuatoriano de la misma especie,
#      Rupicola peruvianus, de los bosques nublados de Mindo).
#   Same art; only the user-facing species name changes.
#   Chat persona keeps the friendly diminutive "Gallito".
# ============================================================
rep('alt="Gallito de las Rocas"', 'alt="Gallo de la Peña"', 1, 'mascot alt big')
rep_all('alt="Gallito"', 'alt="Gallo de la Peña"', 1, 'mascot alt mini')

# ============================================================
# SECTION C — INSTITUTION RENAMES (agencies)
#   Order: longest/most-specific first. These DO appear in myth sources
#   and footers, but those whole blocks are rewritten in fill_data.py
#   (run after the research numbers land), so here we only touch the
#   occupation 'where' chips and study texts, which fill_data does not.
# ============================================================
# -- where-chips (each is a unique quoted list) --
rep("'Empresas mineras','INGEMMET (Instituto Geológico, Minero y Metalúrgico)','Consultoras'",
    "'Empresas mineras','IIGE (Instituto de Investigación Geológico y Energético)','Consultoras'", 1, 'INGEMMET chip')
rep("'Bancos','INEI (Instituto Nacional de Estadística e Informática)','Consultoras'",
    "'Bancos','INEC (Instituto Nacional de Estadística y Censos)','Consultoras'", 1, 'INEI chip')
rep("'Agroexportadoras','INIA','Minagri'",
    "'Agroexportadoras','INIAP','Ministerio de Agricultura (MAG)'", 1, 'INIA/Minagri chip')
rep("'SERFOR','Empresas forestales','ONGs'",
    "'Ministerio del Ambiente (MAATE)','Empresas forestales','ONGs'", 1, 'SERFOR chip')
rep("'Empresas pesqueras','IMARPE','Exportadoras'",
    "'Pesqueras y camaroneras','IPIAP (Instituto de Acuicultura y Pesca)','Exportadoras'", 1, 'IMARPE chip')
rep("'MINAM','Consultoras','Mineras'",
    "'Ministerio del Ambiente (MAATE)','Consultoras','Mineras'", 1, 'MINAM chip')
rep("'Universidades','Laboratorios','SERNANP'",
    "'Universidades','Laboratorios','Ministerio del Ambiente (MAATE)'", 1, 'SERNANP chip')
rep("'BCR','MEF','Bancos','Consultoras'",
    "'Banco Central del Ecuador','Ministerio de Economía y Finanzas','Bancos','Consultoras'", 1, 'BCR/MEF chip')
rep("'IGN','Consultoras','Municipalidades'",
    "'IGM (Instituto Geográfico Militar)','Consultoras','Municipios'", 1, 'IGN chip')
rep("'EsSalud','MINSA','Clínicas'",
    "'IESS','Ministerio de Salud Pública (MSP)','Clínicas'", 1, 'EsSalud tec chip')
rep("'EsSalud','MINSA','Clínicas privadas'",
    "'IESS','Ministerio de Salud Pública (MSP)','Clínicas privadas'", 1, 'EsSalud uni chip')
rep("'SEDAPAL','Municipios','Consultoras'",
    "'EPMAPS / Interagua','Municipios','Consultoras'", 1, 'SEDAPAL chip')
rep("'Astilleros','SIMA','Aerolineas'",
    "'Astilleros (ASTINAVE)','Fuerzas Armadas','Aerolíneas'", 1, 'SIMA chip')
rep("'ENEL','Electroperu','Osinergmin'",
    "'Empresa Eléctrica Quito','CELEC','CNEL'", 1, 'electric uni chip')
rep("'ENEL','Luz del Sur','Constructoras'",
    "'Empresa Eléctrica Quito','CNEL','Constructoras'", 1, 'electric tec chip')
rep("'Clínicas','SENASA','Agroindustrias'",
    "'Clínicas','Agrocalidad','Agroindustrias'", 1, 'SENASA vet chip')
rep("'Granjas','Empresas pecuarias','SENASA'",
    "'Granjas','Empresas pecuarias','Agrocalidad'", 1, 'SENASA zoo chip')
# -- agencies that appear in several where-chips / footers (generic) --
rep_all('Ministerio de Educación (MINEDU)', 'Ministerio de Educación del Ecuador', 1, 'MINEDU generic')
rep_all('SUNAT', 'SRI', 1, 'SUNAT->SRI')
# -- routes COMPARE-tab source footer (distinct from the data tab) --
rep_all('Ministerio de Trabajo (MTPE)', 'Ministerio del Trabajo del Ecuador', 1, 'MTPE short')
rep_all('Encuesta Nacional de Hogares (ENAHO) 2024', 'la Encuesta ENEMDU del INEC (2025)', 1, 'ENAHO generic')

# ============================================================
# SECTION D — COMPANY RENAMES (where-to-work chips)
# ============================================================
rep("'Antamina','Southern','Cerro Verde','Las Bambas'",
    "'Lundin Gold (Fruta del Norte)','EcuaCorriente (Mirador)','Petroecuador','Contratistas mineros'", 1, 'mineria secu')
rep("'Antamina','Southern Copper','Cerro Verde','Las Bambas'",
    "'Lundin Gold (Fruta del Norte)','EcuaCorriente (Mirador)','Petroecuador','Adventus-Curipamba'", 1, 'mineria tec')
rep("'Antamina','Southern Copper','Buenaventura'",
    "'Lundin Gold','EcuaCorriente','Petroecuador'", 1, 'mineria uni')
rep("'BCP','IBM','Startups','Bancos'",
    "'Banco Pichincha','Kushki','Startups','Bancos'", 1, 'comp tec')
rep("'Google','Microsoft','BCP','Interbank'",
    "'Google','Microsoft','Banco Pichincha','Produbanco'", 1, 'sistemas uni')
rep("'Claro','Movistar','Entel'", "'Claro','Movistar','CNT'", 1, 'telecom tec')
rep("'Telefonica','Claro','America Movil'", "'CNT','Claro','Movistar'", 1, 'telecom uni')
rep("'COSAPI','Graña y Montero','JJC'",
    "'Hidalgo e Hidalgo','Panavial','Constructoras locales'", 1, 'construc tec')
rep("'COSAPI','Graña y Montero','GyM'",
    "'Hidalgo e Hidalgo','Panavial','Herdoíza Crespo'", 1, 'construc uni')
rep("'Fábricas textiles','Gamarra'", "'Fábricas textiles','Talleres de Atuntaqui'", 1, 'textil')
rep("'Camposol','Danper','Viru','Agroexportadoras'",
    "'Reybanpac','Pronaca','Florícolas','Agroexportadoras'", 1, 'agro secu')
rep("'Camposol','Danper','Viru'",
    "'Reybanpac','Pronaca','Santa Priscila'", 1, 'agro tec')
rep("'Agroexportadoras','Camposol','Danper'",
    "'Agroexportadoras','Reybanpac','Santa Priscila'", 1, 'agronegocios uni')
rep("'Alicorp','Gloria','Laive','Molitalia'",
    "'La Fabril','Nestlé Ecuador','Pronaca','Industrias Toni'", 1, 'alimentos secu')
rep("'Alicorp','Gloria','Nestle'",
    "'La Fabril','Pronaca','Nestlé Ecuador'", 1, 'alimentos uni')
rep("'Restaurantes','Pollerias','Chifas','Hoteles'",
    "'Restaurantes','Asaderos','Chifas','Hoteles'", 1, 'cocinero')
rep("'Starbucks','Cafeterias','Restaurantes'",
    "'Sweet & Coffee','Juan Valdez','Cafeterías'", 1, 'barista')
rep("'Saga','Ripley','Oechsle','Tiendas de mall'",
    "'De Prati','Etafashion','Marathon','Tiendas de mall'", 1, 'retail')
rep("'Atento','Konecta','Teleperformance'",
    "'Konecta','Atento','Call centers'", 1, 'call center')
rep("'Inkafarma','Mifarma','Boticas'",
    "'Fybeca','Pharmacys','Cruz Azul'", 1, 'farmacias')
rep("'Prosegur','Securitas','G4S','Edificios'",
    "'G4S','Prosegur','Empresas de seguridad','Edificios'", 1, 'seguridad')
rep("'Rappi','PedidosYa','Glovo','Restaurantes'",
    "'Rappi','PedidosYa','Tipti','Restaurantes'", 1, 'delivery')

# ============================================================
# SECTION E — SECTOR DESCRIPTIONS
# ============================================================
rep("desc:'Perú es líder mundial en exportación de arándanos, paltas y espárragos.'",
    "desc:'Ecuador es líder mundial en banano y camarón, y top en cacao, flores y café.'", 1, 'agro desc')
rep("desc:'Perú es potencia gastronómica y turística mundial.'",
    "desc:'Galápagos, Andes, Amazonía y Costa hacen de Ecuador un destino turístico mundial.'", 1, 'turismo desc')
rep("desc:'Sector con alta demanda, especialmente en Lima.'",
    "desc:'Sector con alta demanda, especialmente en Quito y Guayaquil.'", 1, 'servicios desc')
rep("desc:'Sector con alta remuneración promedio en el país, dependiendo del rol, la experiencia y la región.'",
    "desc:'La nueva minería ecuatoriana (Fruta del Norte, Mirador) y el petróleo ofrecen de los mejores salarios técnicos del país.'", 1, 'mineria desc')
rep("desc:'Sector relacionado con construcción, obras públicas y desarrollo de infraestructura en distintas regiones del país.'",
    "desc:'Construcción, obras públicas y vías en las provincias del Ecuador (carreteras, hidroeléctricas, vivienda).'", 1, 'infra desc')
rep("desc:'Todas las empresas necesitan administradores y contadores.'",
    "desc:'Toda empresa en Ecuador necesita administración, ventas, contabilidad y comercio exterior.'", 1, 'admin desc')
rep("desc:'El sector salud siempre tiene demanda laboral.'",
    "desc:'Salud con demanda constante en el MSP, el IESS y clínicas privadas de todo el país.'", 1, 'salud desc')
rep("desc:'Formación de las nuevas generaciones del país.'",
    "desc:'Docencia con escala salarial del Magisterio fiscal y alta demanda en todo el Ecuador.'", 1, 'educacion desc')
rep("desc:'El boom del e-commerce impulsa la logística.'",
    "desc:'El comercio electrónico y los puertos (Guayaquil, Manta) impulsan la logística y el transporte.'", 1, 'logistica desc')

# ============================================================
# SECTION F — STUDY-TEXT SWAPS (institutos + universidades + país)
# ============================================================
rep('institutos como TECSUP o Senati (3 años)',
    'institutos tecnológicos como el Central Técnico o el SECAP (2-3 años)', 1, 'study mineria inst')
rep('institutos como IDAT, Cibertec o Senati (2-3 años)',
    'institutos como el Cordillera (ITSCO) o el Sudamericano (2-3 años)', 1, 'study comp inst')
rep('en TECSUP o Senati (2-3 años)',
    'en institutos tecnológicos públicos o privados (2-3 años)', 1, 'study electr inst')
rep_all('historia del Perú', 'historia del Ecuador', 1, 'historia')
rep('(5 años en universidades como UNI, UNSA, PUCP)',
    '(4-5 años en universidades como la EPN, ESPOL o UCE)', 1, 'study minas uni')
rep('(5 años en UNI, UNMSM, UNSA)', '(4-5 años en la EPN, UCE o ESPOL)', 1, 'study geologia')
rep('(5 años en UNI, PUCP, UPC, UNMSM)', '(4-5 años en la EPN, ESPOL, USFQ o UCE)', 1, 'study sistemas')
rep('(5 años en UTEC, PUCP, UNI)', '(4-5 años en la USFQ, Yachay Tech o EPN)', 1, 'study cs')
rep_all('(5 años en UNI, PUCP, UNMSM)', '(4-5 años en la EPN, ESPOL o UCE)', 2, 'study telecom+')
rep_all('(5 años en UNI, PUCP, UPC)', '(4-5 años en la EPN, ESPE o UDLA)', 2, 'study electr uni+')
rep_all('(5 años en UNMSM, UNI, PUCP)', '(4-5 años en la EPN, UCE o ESPOL)', 2, 'study stats+mate')

# -- comprehensive token sweep for every remaining Peru institution name in
#    study texts (universities + institutos). Word-boundary, longest-first.
#    Each Peru school -> truest Ecuador analogue; lists stay article-free.
import re
INSTITUTION_MAP = [
    # multi-word / must-precede-substrings first
    (r'Toulouse Lautrec', 'UArtes'),
    (r'Bellas Artes', 'UArtes'),
    (r'\bUNALM\b', 'ESPOCH'),          # Agraria La Molina -> ESPOCH (agro/vet)
    (r'\bUNMSM\b', 'UCE'),             # San Marcos -> Universidad Central
    (r'\bUNFV\b', 'UCE'),
    (r'\bUPCH\b', 'USFQ'),             # Cayetano Heredia (medicina) -> USFQ  [before UPC]
    (r'\bCayetano\b', 'USFQ'),
    (r'\bULIMA\b', 'UTE'),             # [before UP / generic]
    (r'\bUTEC\b', 'Yachay Tech'),
    (r'\bPUCP\b', 'PUCE'),             # Católica PE -> Católica EC (paralelo directo)
    (r'\bUNSA\b', 'ESPOL'),
    (r'\bUPC\b', 'UDLA'),
    (r'\bUNI\b', 'EPN'),               # Ing. -> Politécnica Nacional
    (r'\bUP\b', 'UEES'),               # Pacífico (negocios) -> UEES  [after UPC/UPCH]
    # institutos tecnológicos
    (r'\bSenati\b', 'SECAP'),
    (r'\bTECSUP\b', 'Central Técnico'),
    (r'\bCibertec\b', 'Sudamericano'),
    (r'\bIDAT\b', 'Cordillera'),
]
_before = src
for pat, repl in INSTITUTION_MAP:
    src = re.sub(pat, repl, src)
log.append(f"ok: institution token sweep ({len(INSTITUTION_MAP)} patterns)")

# ============================================================
# SECTION G — TIER LABELS + DURATIONS (CETPRO -> SECAP, 5 -> 4-5 años)
# ============================================================
rep('CETPRO = formación técnica corta · Instituto/Técnico = formación profesional (2-3 años) · Universidad = carrera universitaria (5 años)',
    'Cursos cortos / SECAP = formación rápida · Instituto/Tecnológico = formación profesional (2-3 años) · Universidad = carrera de tercer nivel (4-5 años)', 1, 'tier legend')
rep('tracking-wider mb-1">CETPRO</p>', 'tracking-wider mb-1">Cursos cortos / SECAP</p>', 1, 'CETPRO badge')
rep_all("'Universidad (5 años)'", "'Universidad (4-5 años)'", 2, 'uni duration labels')
rep_all('Secundaria completa', 'Bachillerato completo', 2, 'secundaria->bachillerato label')
rep('Carrera técnica (2-3 años)', 'Carrera técnica / tecnológica (2-3 años)', 1, 'tecnica label')

# ============================================================
# SECTION H — "DONDE TRABAJAR" / SOURCE FOOTERS that mention MTPE / Mi Carrera
#   (done here explicitly so the later generic MTPE cleanup is a no-op)
# ============================================================
rep('Fuente: Portal Mi Carrera — Ministerio de Trabajo y Promoción del Empleo (MTPE), 2025 · Lima Metropolitana',
    'Fuente: INEC — Encuesta ENEMDU y guías salariales de mercado (Multitrabajos, Computrabajo), 2025', 1, 'explore footer')
rep('Fuente: Portal Mi Carrera — Ministerio de Trabajo y Promoción del Empleo (MTPE), 2025',
    'Fuente: INEC — Encuesta ENEMDU y guías salariales de mercado (Multitrabajos, Computrabajo), 2025', 1, 'careerdetail footer')
rep_all('Sin datos del Ministerio de Trabajo', 'Sin datos oficiales', 1, 'no-data chip')
rep('El Ministerio de Trabajo no cuenta con datos salariales formales para esta ocupación.',
    'No hay datos salariales formales para esta ocupación.', 1, 'no-data career detail')

out = io.open(DST, 'w', encoding='utf-8')
out.write(src)
out.close()

print('\n'.join(log))
if errors:
    print('\n--- ERRORS ---')
    print('\n'.join(errors))
    sys.exit(1)
print(f"\nOK — {len(log)} replacement groups applied to {DST}.")
