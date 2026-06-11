# -*- coding: utf-8 -*-
"""
SECOND pass: fill Ecuador DATA into index.html (already structurally localized
by transform.py). Handles the numeric blocks the research agents produced:
 - 130 occupation salaries: Peru soles -> Ecuador USD (rebased + anchored to
   Computrabajo/INEC figures, floored at the 2026 SBU = $482)
 - youth-pathway chart (real ENEMDU 2025 microdata partition, ages 15-24)
 - higher-ed access card, salary-premium block, key facts
 - routes comparison (rts) and myths arrays
 - Plan-section counseling box (DECE / SENESCYT / Encuentra Empleo)

Run AFTER transform.py. Operates in place on index.html.
"""
import io, re, sys

DST = 'index.html'
src = io.open(DST, encoding='utf-8').read()
log, errors = [], []

def rep(old, new, n=1, label=''):
    global src
    c = src.count(old)
    if c != n:
        errors.append(f"[{label or old[:50]}] expected {n}, found {c}")
        return
    src = src.replace(old, new)
    log.append(f"ok x{n}: {label or old[:50]}")

def rep_all(old, new, min_n=1, label=''):
    global src
    c = src.count(old)
    if c < min_n:
        errors.append(f"[{label or old[:50]}] expected >={min_n}, found {c}")
        return
    src = src.replace(old, new)
    log.append(f"ok x{c}: {label or old[:50]}")

def resub(pat, repl, label, flags=re.S, min_n=1):
    global src
    new, n = re.subn(pat, repl, src, flags=flags)
    if n < min_n:
        errors.append(f"[{label}] regex matched {n} (<{min_n})")
        return
    src = new
    log.append(f"ok x{n}: {label}")

# ============================================================
# 1) OCCUPATION SALARIES — explicit Ecuador USD per occupation
#    (junior, senior) anchored to the salary research: Computrabajo EC,
#    Multitrabajos Index, INEC-ENEMDU, MSP & Magisterio public scales,
#    sectoral minimums. SBU 2026 = $482 floor. Keyed by (level, name).
# ============================================================
SBU = 482
def usd(v): return f"${v:,}"
def r10(v): return int(round(v / 10.0) * 10)

ECU_SAL = {
  # --- MINERÍA ---
  ('secundaria','Peón de mina'):(500,640),
  ('secundaria','Ayudante de perforación'):(520,720),
  ('tecnica','Técnico en Minería, Metalurgia y Petróleo'):(950,1900),
  ('universitaria','Ingeniería Minera, Metalurgia y Petróleo'):(1000,2800),
  ('universitaria','Geología'):(900,2400),
  # --- TECNOLOGÍA ---
  ('tecnica','Técnico en Ciencias de la Computación'):(590,1200),
  ('tecnica','Técnico de Telecomunicaciones'):(550,1100),
  ('tecnica','Técnico Electrónica'):(500,950),
  ('universitaria','Ingeniería de Sistemas y Cómputo'):(700,2000),
  ('universitaria','Ciencias de la Computación'):(750,2300),
  ('universitaria','Ingeniería de Telecomunicaciones'):(700,1800),
  ('universitaria','Ingeniería Electrónica'):(800,1900),
  ('universitaria','Estadística'):(800,2400),
  ('universitaria','Matemática'):(700,1700),
  ('universitaria','Física'):(700,1500),
  # --- INFRAESTRUCTURA ---
  ('secundaria','Peón de obra / Ayudante de albañil'):(500,560),
  ('secundaria','Pintor de obra'):(480,650),
  ('secundaria','Gasfitero / Ayudante'):(490,700),
  ('secundaria','Soldador'):(530,900),
  ('secundaria','Ayudante de electricista'):(490,650),
  ('secundaria','Operario de fábrica'):(440,600),
  ('tecnica','Técnico Civil'):(600,1100),
  ('tecnica','Técnico Electricista'):(501,1100),
  ('tecnica','Técnico Mecánica'):(520,1000),
  ('tecnica','Técnico Industrial'):(650,1500),
  ('tecnica','Arquitectura y Urbanismo'):(500,900),
  ('tecnica','Textil y Confecciónes'):(470,750),
  ('universitaria','Ingeniería Civil'):(650,1500),
  ('universitaria','Ingeniería Eléctrica'):(850,2000),
  ('universitaria','Ingeniería Mecánica'):(800,2100),
  ('universitaria','Ingeniería Industrial'):(800,1900),
  ('universitaria','Arquitectura y Urbanismo'):(550,1300),
  ('universitaria','Ingeniería Sanitaria'):(750,1800),
  ('universitaria','Ingeniería Naval y Aeronáutica'):(800,2000),
  ('universitaria','Ingeniería Textil y Confecciónes'):(700,1500),
  ('universitaria','Otras Ingenierías'):(750,1800),
  # --- AGRONEGOCIOS ---
  ('secundaria','Operario agrícola'):(482,600),
  ('secundaria','Trabajador de planta de empaque'):(470,620),
  ('secundaria','Operario de planta de alimentos'):(470,650),
  ('tecnica','Agropecuaria'):(500,1000),
  ('tecnica','Técnico en Industrias Alimentarias'):(550,1100),
  ('universitaria','Agronegocios'):(700,1800),
  ('universitaria','Agropecuaria'):(650,1500),
  ('universitaria','Zootecnia'):(600,1300),
  ('universitaria','Veterinaria'):(560,1300),
  ('universitaria','Ingeniería en Agroindustria'):(650,1500),
  ('universitaria','Ingeniería en Industrias Alimentarias'):(700,1600),
  ('universitaria','Ciencias Forestales'):(650,1300),
  ('universitaria','Ingeniería Pesquera'):(700,1500),
  # --- TURISMO ---
  ('secundaria','Mozo / Mesero'):(446,650),
  ('secundaria','Cocinero'):(480,850),
  ('secundaria','Auxiliar de cocina'):(470,650),
  ('secundaria','Recepcionista de hotel'):(440,700),
  ('secundaria','Housekeeping / Limpieza de cuartos'):(460,600),
  ('secundaria','Barista'):(460,650),
  ('tecnica','Administración de Servicios Turisticos, Hotelería y Gastronomía'):(550,1200),
  ('tecnica','Turismo'):(480,1000),
  ('universitaria','Administración de Servicios Turisticos, Hotelería y Gastronomía'):(600,1500),
  # --- ADMINISTRACIÓN ---
  ('secundaria','Vendedor de tienda'):(501,750),
  ('secundaria','Cajero'):(460,650),
  ('secundaria','Promotor / Impulsador'):(460,650),
  ('secundaria','Recepcionista'):(450,700),
  ('secundaria','Call center / Teleoperador'):(470,750),
  ('tecnica','Administración de Empresas'):(500,950),
  ('tecnica','Negocios Internacionales'):(550,1200),
  ('tecnica','Secretariado'):(480,850),
  ('tecnica','Técnico en Marketing'):(520,1100),
  ('tecnica','Técnico en Contabilidad y Finanzas'):(470,900),
  ('universitaria','Economía'):(700,2000),
  ('universitaria','Administración de Empresas'):(600,1600),
  ('universitaria','Marketing'):(600,1600),
  ('universitaria','Contabilidad y Finanzas'):(520,1200),
  ('universitaria','Derecho'):(650,1800),
  ('universitaria','Negocios Internacionales'):(600,1500),
  ('universitaria','Otras Carreras de Administración'):(600,1400),
  ('universitaria','Administración Pública'):(700,1500),
  ('universitaria','Investigación Operativa'):(750,1800),
  ('universitaria','Ciencias Políticas'):(600,1400),
  # --- SALUD ---
  ('secundaria','Auxiliar de farmacia'):(470,650),
  ('tecnica','Enfermeria'):(520,1000),
  ('tecnica','Técnico en Farmacia y Bioquímica'):(490,800),
  ('tecnica','Técnico en Tecnología Médica'):(520,900),
  ('universitaria','Medicina'):(1100,2800),
  ('universitaria','Enfermeria'):(1000,1800),
  ('universitaria','Psicología'):(620,1500),
  ('universitaria','Odontología'):(650,1500),
  ('universitaria','Obstetricia'):(1000,1800),
  ('universitaria','Farmacia y Bioquímica'):(700,1600),
  ('universitaria','Tecnología Médica'):(650,1300),
  ('universitaria','Nutrición'):(600,1300),
  ('universitaria','Trabajo Social'):(550,1200),
  ('universitaria','Servicios Sociales y Asistenciales'):(550,1100),
  # --- EDUCACIÓN (escala Magisterio fiscal $817-2034; privado menor) ---
  ('tecnica','Educación Inicial'):(500,900),
  ('tecnica','Educación Primaria'):(520,950),
  ('tecnica','Educación Secundaria'):(540,1000),
  ('universitaria','Educación Inicial'):(700,1400),
  ('universitaria','Educación Primaria'):(750,1500),
  ('universitaria','Educación Secundaria'):(800,1600),
  ('universitaria','Educación Física'):(700,1400),
  ('universitaria','Educación Especial'):(750,1500),
  ('universitaria','Educación Tecnológica'):(750,1500),
  ('universitaria','Idiomas'):(700,1500),
  ('universitaria','Otras Carreras de Educación'):(700,1400),
  # --- COMUNICACIÓN Y DISEÑO ---
  ('tecnica','Ciencias de la Comunicación'):(550,1100),
  ('tecnica','Técnico en Diseño'):(460,900),
  ('universitaria','Ciencias de la Comunicación'):(560,1300),
  ('universitaria','Diseño'):(500,1300),
  ('universitaria','Periodismo y Locución'):(560,1300),
  ('universitaria','Artes'):(500,1100),
  ('universitaria','Bibliotecología y Archivo'):(550,1100),
  ('universitaria','Lingüistica y Literatura'):(550,1100),
  ('universitaria','Historia'):(550,1100),
  ('universitaria','Teología y Filosofía'):(500,1000),
  ('universitaria','Antropología y Arqueología'):(550,1200),
  ('universitaria','Geografía'):(600,1300),
  # --- CIENCIAS Y MEDIO AMBIENTE ---
  ('tecnica','Química'):(550,1000),
  ('universitaria','Química'):(650,1400),
  ('universitaria','Biología'):(650,1500),
  ('universitaria','Ecología y Medio Ambiente'):(600,1400),
  # --- SERVICIOS Y SEGURIDAD ---
  ('secundaria','Vigilante / Agente de seguridad'):(517,750),
  ('secundaria','Personal de limpieza'):(460,580),
  ('secundaria','Cuidador de adultos mayores'):(460,650),
  ('secundaria','Trabajador del hogar'):(460,580),
  ('secundaria','Peluquero / Barbero'):(470,900),
  ('secundaria','Costurera / Sastre'):(460,750),
  # --- LOGÍSTICA Y TRANSPORTE ---
  ('secundaria','Auxiliar de almacén'):(458,750),
  ('secundaria','Repartidor / Delivery'):(442,650),
  ('secundaria','Chofer / Conductor'):(591,900),
  ('secundaria','Estibador / Cargador'):(486,650),
  ('secundaria','Operador de montacargas'):(500,800),
}

# level of an occupation = the most recent secundaria:/tecnica:/universitaria: marker
_markers = [(mm.start(), mm.group(1)) for mm in
            re.finditer(r'(secundaria|tecnica|universitaria):\[', src)]
def level_at(pos):
    lvl = 'universitaria'
    for p, l in _markers:
        if p < pos: lvl = l
        else: break
    return lvl

_missing = []
def conv(m):
    name = m.group(1)
    lvl = level_at(m.start())
    if (lvl, name) in ECU_SAL:
        j, s = ECU_SAL[(lvl, name)]
    else:
        _missing.append((lvl, name))
        j, s = {'secundaria': (482, 650), 'tecnica': (550, 1100),
                'universitaria': (650, 1500)}[lvl]
    return (f"name:'{name}',salary:'{usd(j)}',growth:'{usd(s)}'"
            f",range:'{usd(max(SBU, r10(j*0.8)))} – {usd(r10(j*1.3))}'"
            f",rangeAdult:'{usd(r10(s*0.7))} – {usd(r10(s*1.6))}'")

resub(r"name:'([^']*)',salary:'(?:S/[^']*|Variable)',growth:'[^']*'(?:,range:'[^']*')?(?:,rangeAdult:'[^']*')?",
      conv, 'occupation salaries', min_n=120)
if _missing:
    errors.append('UNMAPPED occupations: ' + '; '.join(f'{l}/{n}' for l, n in _missing))
log.append(f"   -> {len(ECU_SAL)} occupations priced in USD (0 unmapped)" if not _missing
           else f"   -> {len(_missing)} UNMAPPED")

# ============================================================
# 2) HOME — youth pathway (real ENEMDU 15-24 partition) + access
# ============================================================
NEW_HOME = """{/* Youth pathway visual */}
        <div className="bg-white rounded-2xl border-2 border-cream-200 p-5 sm:p-6 mb-6">
          <h3 className="font-black text-navy-700 mb-1">De cada 100 jóvenes ecuatorianos (15 a 24 años)...</h3>
          <p className="text-navy-400 text-xs mb-4">¿Qué están haciendo hoy?</p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
            {[
              {n:29,label:'Solo trabajan',icon:'💼',color:'bg-green-500',bg:'bg-green-50 border-green-200'},
              {n:44,label:'Solo estudian',icon:'📚',color:'bg-purple-500',bg:'bg-purple-50 border-purple-200'},
              {n:9,label:'Estudian y trabajan',icon:'⚡',color:'bg-blue-500',bg:'bg-blue-50 border-blue-200'},
              {n:18,label:'NiNis',icon:'⚠️',color:'bg-red-500',bg:'bg-red-50 border-red-200'},
            ].map((d,i)=>(<div key={i} className={`${d.bg} border-2 rounded-xl p-3 text-center`}>
              <span className="text-2xl block">{d.icon}</span>
              <p className="text-2xl sm:text-3xl font-black text-navy-700 mt-1">{d.n}</p>
              <p className="text-[10px] sm:text-xs text-navy-500 font-bold mt-0.5">{d.label}</p>
            </div>))}
          </div>
          <div className="w-full h-6 rounded-full overflow-hidden flex">
            <div className="bg-green-500 h-full" style={{width:'29%'}}/>
            <div className="bg-purple-500 h-full" style={{width:'44%'}}/>
            <div className="bg-blue-500 h-full" style={{width:'9%'}}/>
            <div className="bg-red-400 h-full" style={{width:'18%'}}/>
          </div>
          <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2 text-[10px] text-navy-400">
            <span className="flex items-center gap-1"><span className="w-2 h-2 bg-green-500 rounded-full"/>Solo trabajan (29%)</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 bg-purple-500 rounded-full"/>Solo estudian (44%)</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 bg-blue-500 rounded-full"/>Ambos (9%)</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 bg-red-400 rounded-full"/>NiNis (18%)</span>
          </div>
          <p className="text-[10px] text-navy-300 mt-2">Fuente: INEC — Encuesta Nacional de Empleo (ENEMDU) 2025, cálculo propio sobre microdatos. NiNi = ni estudian ni trabajan; las mujeres jóvenes son las más afectadas (28% vs 10% de los hombres).</p>
        </div>
        {/* Education access breakdown */}
        <div className="bg-brand-50 border-2 border-brand-200 rounded-2xl p-5 mb-8">
          <div className="flex gap-3 items-start mb-3">
            <OwlMascot size={48} expression="surprised"/>
            <div>
              <p className="font-bold text-navy-700">Solo ~18 de cada 100 jóvenes (18 a 24 años) asisten a la educación superior</p>
              <p className="text-navy-500 text-sm mt-1">Se divide así: <strong className="text-purple-600">16% en la universidad</strong> y <strong className="text-blue-600">2% en institutos/tecnológicos</strong>. La pública es <strong>gratuita</strong>, pero los cupos son limitados.</p>
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-center">
            <div className="bg-white rounded-lg p-2.5"><p className="text-xs text-navy-400">Universidad</p><p className="text-lg font-black text-purple-600">16%</p></div>
            <div className="bg-white rounded-lg p-2.5"><p className="text-xs text-navy-400">Instituto/Tecnológico</p><p className="text-lg font-black text-blue-600">2%</p></div>
            <div className="bg-white rounded-lg p-2.5"><p className="text-xs text-navy-400">No accede a superior</p><p className="text-lg font-black text-navy-600">82%</p><p className="text-[9px] text-navy-400 mt-0.5">de ~350 mil bachilleres/año, 4 de 10 no logran cupo público</p></div>
          </div>
          <p className="text-[10px] text-navy-300 mt-2">Fuente: INEC — Encuesta ENEMDU 2025; SENESCYT.</p>
        </div>
        """
resub(r"\{/\* Youth pathway visual \*/\}[\s\S]*?(?=\{/\* Ikigai roadmap \*/\})",
      lambda m: NEW_HOME, 'home pathway+access region', min_n=1)

# ============================================================
# 3) ROUTES "Datos clave" tab — salary premium + pathway + access + key facts
# ============================================================
NEW_ROUTESDATA = """{/* Salary context */}
          <div className="bg-gradient-to-r from-navy-700 to-navy-600 rounded-2xl p-4 sm:p-6 text-white mb-6 relative overflow-hidden">
            <div className="absolute right-4 top-4 opacity-10 hidden sm:block"><OwlMascot size={100}/></div>
            <h3 className="font-bold text-base sm:text-lg mb-1">¿Cuánto gana la gente al mes en Ecuador?</h3>
            <p className="text-white/50 text-xs mb-3 sm:mb-4">Ingreso laboral promedio (incluye empleo formal e informal)</p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {[{label:'Solo bachillerato',val:'$390',pct:51,color:'bg-green-400',info:''},
                {label:'Técnico / Tecnólogo',val:'$709',pct:93,color:'bg-brand-400',info:'+82% vs bachillerato'},
                {label:'Universidad',val:'$760',pct:100,color:'bg-purple-400',info:'+95% vs bachillerato'}
              ].map((d,i)=>(
                <div key={i} className="bg-white/10 rounded-xl p-4 backdrop-blur-sm">
                  <p className="text-white/70 text-xs mb-1">{d.label}</p>
                  <p className="text-2xl font-black">{d.val}</p>
                  <div className="mt-2 h-2 bg-white/20 rounded-full"><div className={`h-full ${d.color} rounded-full`} style={{width:`${d.pct}%`}}/></div>
                  <p className="text-white/60 text-[11px] mt-1">{d.info}</p>
                </div>
              ))}
            </div>
            <p className="text-white/30 text-[11px] mt-3">Fuente: INEC — Encuesta ENEMDU 2025. La mediana es menor ($400 / $550 / $600) por la alta informalidad.</p>
          </div>

          {/* Youth pathway visual */}
          <div className="bg-white rounded-2xl border-2 border-navy-200 p-5 mb-6">
            <h3 className="font-black text-navy-700 text-sm mb-1">De cada 100 jóvenes ecuatorianos (15 a 24 años):</h3>
            <p className="text-navy-400 text-[10px] mb-4">¿Qué están haciendo hoy?</p>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
              {[
                {n:29,label:'Solo trabajan',icon:'💼',bg:'bg-green-50 border-green-200'},
                {n:44,label:'Solo estudian',icon:'📚',bg:'bg-purple-50 border-purple-200'},
                {n:9,label:'Estudian y trabajan',icon:'⚡',bg:'bg-blue-50 border-blue-200'},
                {n:18,label:'NiNis',icon:'⚠️',bg:'bg-red-50 border-red-200'},
              ].map((d,i)=>(<div key={i} className={`${d.bg} border-2 rounded-xl p-3 text-center`}>
                <span className="text-xl block">{d.icon}</span>
                <p className="text-2xl font-black text-navy-700 mt-1">{d.n}</p>
                <p className="text-[10px] text-navy-500 font-bold">{d.label}</p>
              </div>))}
            </div>
            <div className="w-full h-5 rounded-full overflow-hidden flex">
              <div className="bg-green-500 h-full" style={{width:'29%'}}/>
              <div className="bg-purple-500 h-full" style={{width:'44%'}}/>
              <div className="bg-blue-500 h-full" style={{width:'9%'}}/>
              <div className="bg-red-400 h-full" style={{width:'18%'}}/>
            </div>
            <p className="text-[10px] text-navy-300 mt-2">INEC — Encuesta ENEMDU 2025 (cálculo propio). NiNi = ni estudian ni trabajan; mujeres 28% vs hombres 10%.</p>
          </div>

          {/* Education access */}
          <div className="bg-purple-50 border-2 border-purple-200 rounded-2xl p-5 mb-6">
            <p className="font-bold text-navy-700 text-sm mb-3">Solo ~18 de cada 100 jóvenes (18 a 24 años) asisten a la educación superior</p>
            <div className="grid grid-cols-3 gap-2 text-center mb-3">
              <div className="bg-white rounded-lg p-3"><p className="text-2xl font-black text-purple-600">16%</p><p className="text-[10px] text-navy-400 font-bold">Universidad</p></div>
              <div className="bg-white rounded-lg p-3"><p className="text-2xl font-black text-blue-600">2%</p><p className="text-[10px] text-navy-400 font-bold">Inst./Tecnológico</p></div>
              <div className="bg-white rounded-lg p-3"><p className="text-2xl font-black text-navy-600">82%</p><p className="text-[10px] text-navy-400 font-bold">No accede</p><p className="text-[8px] text-navy-400">la pública es gratis; faltan cupos</p></div>
            </div>
            <p className="text-[10px] text-navy-300 mt-1">INEC — Encuesta ENEMDU 2025; SENESCYT.</p>
          </div>

          {/* Key facts */}
          <div className="space-y-3 mb-6">
            {[
              {icon:'🎓',title:'~350 mil bachilleres al año, ~213 mil cupos públicos',detail:'4 de cada 10 que postulan a la universidad pública no consiguen cupo. La pública es gratuita (gratuidad), pero los cupos son limitados y cada universidad toma su propio examen de admisión.',color:'bg-brand-50 border-brand-200'},
              {icon:'📉',title:'46% con solo bachillerato trabaja en la informalidad',detail:'Sin contrato ni seguro. Con educación superior baja al 19%, y el empleo adecuado sube del 30% al 60%.',color:'bg-red-50 border-red-200'},
              {icon:'💰',title:'La carrera importa tanto como el nivel',detail:'Un tecnólogo gana en promedio $709/mes, casi igual que un universitario ($760). En software o minería puede ganar más. Elegir bien el área es clave.',color:'bg-brand-50 border-brand-200'},
              {icon:'⚠️',title:'Casi 1 de cada 5 jóvenes (15-24) ni estudia ni trabaja',detail:'Las mujeres jóvenes son las más afectadas (28% vs 10% de los hombres). Es la situación que este programa busca prevenir.',color:'bg-amber-50 border-amber-200'},
              {icon:'🔄',title:'1 de cada 5 cambia de carrera y ~20% abandona',detail:'La deserción universitaria es del 20% (más alta en universidades privadas). Elegir con información reduce el riesgo de empezar y dejar.',color:'bg-green-50 border-green-200'},
              {icon:'🌱',title:'Sectores con más demanda en Ecuador',detail:'Banano y camarón (Ecuador es #1 del mundo), minería (Fruta del Norte, Mirador), tecnología y software, y siempre salud y educación.',color:'bg-blue-50 border-blue-200'},
            ].map((d,i)=>(<div key={i} className={`${d.color} border-2 rounded-2xl p-4 flex gap-3 items-start animate-slide-up`} style={{animationDelay:`${i*.06}s`}}>
              <span className="text-2xl shrink-0">{d.icon}</span>
              <div>
                <p className="font-bold text-navy-700 text-sm">{d.title}</p>
                <p className="text-navy-500 text-xs mt-1 leading-relaxed">{d.detail}</p>
              </div>
            </div>))}
          </div>
          <p className="text-[10px] text-navy-300 text-center mb-4">Fuentes: INEC — Encuesta ENEMDU 2025; SENESCYT; Ministerio del Trabajo del Ecuador.</p>"""
resub(r"\{/\* Salary context \*/\}[\s\S]*?Cámara de Comercio de Lima \(CCL\)</p>",
      lambda m: NEW_ROUTESDATA, 'routes data tab region', min_n=1)

# ============================================================
# 4) ROUTES comparison array (rts)
# ============================================================
NEW_RTS = """const rts=[
    {icon:I.grad,name:"Universidad",time:"4-5 años",salary:"$760",color:"from-purple-500 to-indigo-600",inf:"19%",
      example:"Un economista junior gana ~$700/mes; con experiencia, un ingeniero de software o de minas supera los $2,000/mes.",
      study:"Puedes retomar estudios si empiezas por otra ruta",canWork:"Prácticas desde 3er o 4to año",
      pros:["Mayor ingreso promedio (+95% vs solo bachillerato)","En la universidad pública es GRATIS (gratuidad constitucional)","Red profesional amplia y acceso a posgrados"],
      cons:["Pocos cupos: 4 de cada 10 que postulan no entran a la pública","Dura 4-5 años sin ingreso fijo","En privada cuesta ~$4,000-13,000 al año","No garantiza empleo automático"],
      real:"En Ecuador la universidad pública es gratuita, pero el cuello de botella es el cupo: hay ~350,000 bachilleres al año y solo ~213,000 cupos públicos. Elegir con información y tener un Plan B marca la diferencia."},
    {icon:I.bolt,name:"Técnico / Instituto",time:"2-3 años",salary:"$709",color:"from-brand-400 to-brand-300",inf:"19%",
      example:"Un tecnólogo en software gana ~$600-700 al inicio; un técnico de soporte o electricista con experiencia llega a $1,200/mes.",
      study:"Puedes continuar a la universidad después (homologación de créditos)",canWork:"Desde el 2do año en muchos institutos",
      pros:["Más rápido y práctico (2 a 2.5 años)","En institutos públicos es GRATIS","Alta demanda en software, salud, electricidad y mantenimiento","Algunos tecnólogos ganan casi lo mismo que un universitario ($709 vs $760)"],
      cons:["Techo salarial algo más bajo en promedio","Menos red de contactos que la universidad","Los cupos públicos también son limitados"],
      real:"Un tecnólogo gana en promedio $709/mes, casi lo mismo que un universitario ($760). En áreas como software o minería puede ganar más. La carrera importa tanto como el nivel."},
    {icon:I.home,name:"Trabajo Directo",time:"Inmediato",salary:"$390",color:"from-green-500 to-emerald-600",inf:"46%",
      example:"Puedes empezar como auxiliar de bodega o vendedor (~$460-500) y capacitarte para crecer. Muchos combinan trabajo con cursos del SECAP o estudio nocturno.",
      study:"Cursos cortos del SECAP, institutos nocturnos, fines de semana y a distancia",canWork:"Desde ya",
      pros:["Ingresos inmediatos","Experiencia real desde el día 1","Puedes estudiar después o en paralelo (la pública es gratis)","Independencia económica temprana"],
      cons:["Menor ingreso inicial (cerca del salario básico, $482)","Alta informalidad (46%)","Menos crecimiento sin capacitación"],
      real:"El salario básico 2026 es $482. Con solo bachillerato el ingreso promedio es ~$390 y casi la mitad trabaja de manera informal. Capacitarte (SECAP, instituto o universidad) abre mejores puertas."},
  ];"""
resub(r"const rts=\[[\s\S]*?\n  \];", lambda m: NEW_RTS, 'rts array', min_n=1)

# ============================================================
# 5) MYTHS array
# ============================================================
NEW_MYTHS = """const mythsData=[
  {statement:"Solo puedes ganar bien si tienes un título universitario",isMyth:true,cat:"Salarios",
   explanation:"Un tecnólogo gana en promedio $709/mes, casi igual que un universitario ($760), con solo 2 a 2.5 años de estudio. En software o minería, un técnico puede ganar más que muchos universitarios.",source:"INEC — Encuesta Nacional de Empleo (ENEMDU) 2025"},
  {statement:"La mayoría de personas con solo bachillerato trabaja de manera informal",isMyth:false,cat:"Empleo",
   explanation:"El 46% de quienes tienen solo bachillerato trabaja en la informalidad, sin contrato ni seguro. Con educación superior baja al 19%, y el empleo adecuado sube del 30% al 60%.",source:"INEC — Encuesta Nacional de Empleo (ENEMDU) 2025"},
  {statement:"Si empiezas a trabajar después del colegio, ya no puedes estudiar",isMyth:true,cat:"Trayectorias",
   explanation:"Existen institutos nocturnos, a distancia y de fin de semana, además de cursos cortos del SECAP. Y la universidad pública es gratuita. La trayectoria no es lineal.",source:"SENESCYT / Ministerio de Educación del Ecuador"},
  {statement:"En Ecuador la mayor demanda está en banano, camarón, minería y tecnología",isMyth:false,cat:"Mercado",
   explanation:"Ecuador es el mayor exportador de banano y camarón del mundo; la minería (Fruta del Norte, Mirador) crece con fuerza y la tecnología se expande. Pero también hay demanda constante en salud, educación y servicios.",source:"INEC / Banco Central del Ecuador — exportaciones 2025"},
  {statement:"Elegir una carrera a los 17 años es una decisión definitiva",isMyth:true,cat:"Decisión",
   explanation:"1 de cada 5 estudiantes cambia de carrera en el primer año y cerca del 20% abandona la universidad. Las trayectorias no son lineales: siempre puedes reorientarte y seguir actualizándote.",source:"SENESCYT (deserción 2023) / estudios regionales"},
  {statement:"Mientras más años estudies, siempre vas a ganar más",isMyth:true,cat:"Salarios",
   explanation:"No es solo cuántos años estudias, sino QUÉ estudias y para qué mercado. Un tecnólogo en software (2.5 años) puede ganar más que un licenciado en un área con poca demanda. La carrera importa tanto como el nivel.",source:"INEC — ENEMDU 2025 / Computrabajo Ecuador 2026"},
  {statement:"Solo carreras como medicina, derecho e ingeniería pagan bien",isMyth:true,cat:"Opciones",
   explanation:"Tecnología y software ($1,500+ con experiencia), minería ($2,500+), ciencia de datos ($2,500-4,500) y las especialidades de salud están muy bien pagadas. Hay muchas opciones además de las tradicionales.",source:"Computrabajo / Multitrabajos Ecuador 2026"},
];"""
resub(r"const mythsData=\[[\s\S]*?\n\];", lambda m: NEW_MYTHS, 'myths array', min_n=1)

# ============================================================
# 6) PLAN — counseling box (DECE / SENESCYT / Encuentra Empleo)
# ============================================================
NEW_PLAN = """{/* Ecuador free guidance */}
      <div className="bg-gradient-to-r from-teal-50 to-cyan-50 border-2 border-teal-200 rounded-2xl p-5 mb-6">
        <div className="flex items-start gap-3 sm:gap-4">
          <div className="w-10 h-10 sm:w-12 sm:h-12 bg-teal-100 rounded-xl flex items-center justify-center shrink-0"><span className="text-xl sm:text-2xl">🎓</span></div>
          <div className="flex-1">
            <h4 className="font-bold text-navy-700 text-xs sm:text-sm mb-1">Orientación gratuita y pasos para postular en Ecuador</h4>
            <p className="text-sm text-navy-500 mb-3">En tu colegio, el <strong>DECE</strong> (Departamento de Consejería Estudiantil) ofrece orientación vocacional gratuita. Y antes de postular a una universidad o instituto público, ten en cuenta estos pasos:</p>
            <div className="bg-white rounded-xl p-3 mb-3 text-xs text-navy-500 space-y-1">
              <p><strong>1.</strong> Verifica que la universidad o instituto sea legal en infoeducacionsuperior.gob.ec</p>
              <p><strong>2.</strong> Haz el Registro Nacional en la plataforma de admisión (admision.educacion.gob.ec)</p>
              <p><strong>3.</strong> Revisa las becas de manutención de la SENESCYT (ej.: "Jóvenes del Nuevo Ecuador")</p>
              <p><strong>4.</strong> Si buscas trabajo, usa Encuentra Empleo del Ministerio del Trabajo</p>
            </div>
            <a href="https://www.infoeducacionsuperior.gob.ec/" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 px-4 py-2 bg-teal-500 text-white rounded-lg font-bold text-sm hover:bg-teal-600 transition">
              Verificar instituciones y carreras <span>→</span>
            </a>
          </div>
        </div>
      </div>"""
resub(r"\{/\* MTPE Free Counseling \*/\}[\s\S]*?</a>\s*</div>\s*</div>\s*</div>",
      lambda m: NEW_PLAN, 'plan counseling box', min_n=1)

# ============================================================
# 7) Small text swaps (intro, chat, notebook source mentions)
# ============================================================
rep('📊 Aquí encontrarás datos reales sobre educación y trabajo en el Perú.',
    '📊 Aquí encontrarás datos reales sobre educación y trabajo en el Ecuador.', 1, 'data intro')
rep('Todos los datos provienen del Instituto Nacional de Estadística e Informática (INEI), la Encuesta Nacional de Hogares (ENAHO) y el Ministerio de Trabajo y Promoción del Empleo (MTPE).',
    'Todos los datos provienen del INEC (Encuesta Nacional de Empleo, ENEMDU), la SENESCYT y el Ministerio del Trabajo del Ecuador.', 1, 'data intro src')
rep('Explorar sectores y carreras con salarios verificados',
    'Explorar sectores y carreras con datos del mercado laboral', 1, 'chat bullet')
rep_all('Ministerio de Trabajo, universidades, institutos, becas',
        'el INEC, universidades, institutos, la SENESCYT y becas', 1, 'notebook sources')
# route-finder quiz: replace Peru "tuition cost" logic (in Ecuador public study is free) ---
rep('Mis padres pueden apoyarme con los estudios',
    'Puedo dedicarme a estudiar a tiempo completo', 1, 'quiz econ opt1')
rep('Necesito algo accesible o una beca',
    'La pública es gratis; quizás necesite una beca de manutención', 1, 'quiz econ opt2')
rep('Necesito aportar a la casa',
    'Necesito trabajar y aportar en casa ya', 1, 'quiz econ opt3')
# privada cost reference already in Ecuador USD inside rts; nothing else to change here.

io.open(DST, 'w', encoding='utf-8').write(src)
print('\n'.join(log))
if errors:
    print('\n--- ERRORS ---\n' + '\n'.join(errors)); sys.exit(1)
print(f"\nfill_data OK — {len(log)} ops.")
