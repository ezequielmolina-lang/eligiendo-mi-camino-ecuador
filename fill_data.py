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
# 1) OCCUPATION SALARIES  (Peru S/ -> Ecuador USD)
# ============================================================
SBU = 482
def soles(s):
    m = re.search(r'[\d,]+', s)
    return int(m.group(0).replace(',', '')) if m else None
def usd(v):
    return f"${v:,}"
def r10(v):
    return int(round(v / 10.0) * 10)

# Researched anchors (junior, senior) USD — salary agent (Computrabajo/INEC/MSP/
# Magisterio/Multitrabajos 2025-26). Applied by name substring; longest keys win.
OVERRIDES = {
    'Medicina': (1100, 2600),
    'Ingeniería de Sistemas': (700, 2000),
    'Ciencias de la Computación': (750, 2200),
    'Ingeniería de Telecomunicaciones': (700, 1800),
    'Ingeniería Minera': (950, 2600),
    'Geología': (900, 2400),
    'Ingeniería Civil': (650, 1450),
    'Ingeniería Industrial': (800, 1900),
    'Ingeniería Eléctrica': (850, 2000),
    'Ingeniería Electrónica': (800, 1900),
    'Derecho': (650, 1600),
    'Economía': (700, 1800),
    'Administración de Empresas': (600, 1400),
    'Contabilidad y Finanzas': (520, 1100),
    'Marketing': (580, 1400),
    'Psicología': (620, 1400),
    'Odontología': (650, 1500),
    'Obstetricia': (1000, 1700),
    'Veterinaria': (560, 1200),
    'Arquitectura y Urbanismo': (520, 1200),
    'Agronegocios': (700, 1600),
    'Estadística': (800, 2400),
    'Diseño': (470, 950),
    'Periodismo y Locución': (560, 1300),
    'Ciencias de la Comunicación': (560, 1250),
}
def anchor(name):
    best = None
    for k, v in OVERRIDES.items():
        if k in name and (best is None or len(k) > len(best[0])):
            best = (k, v)
    return best[1] if best else None

def rebase_j(p):
    lo_p, hi_p, lo_e, hi_e = 1500, 6300, 480, 1250
    p = max(lo_p, min(hi_p, p))
    return max(SBU, r10(lo_e + (p - lo_p) / (hi_p - lo_p) * (hi_e - lo_e)))
def rebase_s(p):
    lo_p, hi_p, lo_e, hi_e = 2200, 12100, 700, 3000
    p = max(lo_p, min(hi_p, p))
    return max(620, r10(lo_e + (p - lo_p) / (hi_p - lo_p) * (hi_e - lo_e)))

_conv = {'n': 0}
def conv(m):
    name, sal, grow, rng, rngA = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
    if sal == 'Variable':
        return m.group(0)
    pj, ps = soles(sal), soles(grow)
    ov = anchor(name)
    if ov:
        j, s = ov
    else:
        j = rebase_j(pj)
        s = rebase_s(ps) if ps else rebase_j(pj) + 400
    if s <= j:
        s = j + 300
    _conv['n'] += 1
    out = f"name:'{name}',salary:'{usd(j)}',growth:'{usd(s)}'"
    if rng is not None:
        out += f",range:'{usd(max(SBU, r10(j*0.8)))} – {usd(r10(j*1.35))}'"
    if rngA is not None:
        out += f",rangeAdult:'{usd(r10(s*0.7))} – {usd(r10(s*1.6))}'"
    return out

resub(r"name:'([^']*)',salary:'([^']*)',growth:'([^']*)'(?:,range:'([^']*)')?(?:,rangeAdult:'([^']*)')?",
      conv, 'occupation salaries', min_n=120)
log.append(f"   -> {_conv['n']} salaried occupations converted to USD")

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

io.open(DST, 'w', encoding='utf-8').write(src)
print('\n'.join(log))
if errors:
    print('\n--- ERRORS ---\n' + '\n'.join(errors)); sys.exit(1)
print(f"\nfill_data OK — {len(log)} ops.")
