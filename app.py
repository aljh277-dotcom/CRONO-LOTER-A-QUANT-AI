import streamlit as st
import random
import math
from datetime import datetime
import itertools

try:
    from google import genai
    from google.genai import types
    GENAI_DISPONIBLE = True
except ImportError:
    GENAI_DISPONIBLE = False

st.set_page_config(
    page_title="Crono-Lotería Quant AI",
    page_icon="🔬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top, #131b2e 0%, #090d16 100%);
        color: #e2e8f0;
    }
    .hero-box {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.85), rgba(15, 23, 42, 0.95));
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
    }
    .hero-title {
        font-size: 26px;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #f59e0b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: 0.5px;
    }
    .hero-sub {
        font-size: 12px;
        color: #94a3b8;
        margin-top: 6px;
    }
    .bolilla {
        display: inline-block;
        padding: 0 14px;
        min-width: 44px;
        height: 44px;
        line-height: 44px;
        border-radius: 22px;
        font-size: 17px;
        font-weight: 800;
        color: #ffffff;
        text-align: center;
        background: linear-gradient(145deg, #1e3a8a, #3b82f6);
        border: 1px solid rgba(147, 197, 253, 0.45);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        margin: 4px;
    }
    .bolilla-oro {
        background: linear-gradient(145deg, #b45309, #f59e0b);
        border: 1px solid rgba(253, 230, 138, 0.55);
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
    }
    .tarjeta-boleto {
        background: rgba(30, 41, 59, 0.65);
        backdrop-filter: blur(12px);
        padding: 16px;
        border-radius: 14px;
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-left: 4px solid #38bdf8;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    .metrica-tag {
        font-size: 11px;
        background-color: rgba(15, 23, 42, 0.9);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.35);
        padding: 3px 8px;
        border-radius: 6px;
        margin-right: 6px;
        font-family: monospace;
    }
    .disclaimer-box {
        font-size: 11px;
        color: #64748b;
        text-align: center;
        margin-top: 20px;
        padding: 10px;
        border-top: 1px solid rgba(148, 163, 184, 0.15);
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-box">
    <div class="hero-title">🔬 CRONO-LOTERÍA QUANT AI</div>
    <div class="hero-sub">Laboratorio Estocástico • Análisis Matemático & Simbólico • Proyección Experimental</div>
</div>
""", unsafe_allow_html=True)

tipo_loteria = st.selectbox(
    "🌎 Selecciona el Sorteo a Analizar:",
    [
        "🇵🇦 Lotería Nacional de Panamá (Billetes 4 cifras / Chances 00-99)",
        "🇨🇷 Tiempos Costa Rica / Chances (2 cifras: 00-99)",
        "🌐 Lotto Internacional (6 bolillas del 01 al 49)"
    ]
)

def calcular_entropia_shannon(numeros):
    decenas = [n // 10 for n in numeros]
    total = len(decenas)
    conteos = {d: decenas.count(d) for d in set(decenas)}
    entropia = -sum((c / total) * math.log2(c / total) for c in conteos.values())
    return round(entropia, 3)

def indice_anti_popularidad(numeros):
    altos = sum(1 for n in numeros if n > 31)
    return round((altos / len(numeros)) * 100, 1)

def matriz_markov_transicion(historial, modulo):
    if len(historial) < 2:
        return [random.randint(0, modulo - 1) for _ in range(5)]
    deltas = [(historial[i] - historial[i+1]) % modulo for i in range(len(historial)-1)]
    proyecciones = []
    ultimo = historial[0]
    for d in deltas:
        proyecciones.append((ultimo + d) % modulo)
        proyecciones.append((ultimo - d) % modulo)
    return list(dict.fromkeys(proyecciones))

def chi_cuadrado_desviacion(historial, modulo):
    conteo = {i: historial.count(i) for i in range(modulo)}
    esperado = max(len(historial) / modulo, 0.1)
    rezagados = sorted(
        [k for k, v in conteo.items() if v <= esperado],
        key=lambda x: ((conteo[x] - esperado) ** 2) / esperado,
        reverse=True
    )
    return rezagados[:15]

tab_motor, tab_chat = st.tabs(["⚙️ Motor Cuantitativo", "🤖 Oráculo & Analista IA"])

with tab_motor:
    modelo_cientifico = st.selectbox(
        "📐 Enfoque de Análisis:",
        [
            "🔗 Cadenas de Márkov (Matriz de Transición de Estados)",
            "📊 Prueba Chi-Cuadrado χ² (Desviación y Sesgo de Frecuencia)",
            "🧬 Entropía de Shannon + Gauss (Filtro de Caos Estructural)",
            "💎 Optimización Valor Esperado EV (Teoría de Juegos Anti-Popularidad)",
            "🔮 Simetría Espejo & Armonía Numerológica (Enfoque Simbólico)"
        ]
    )

    col_f, col_c = st.columns([1, 1])
    with col_f:
        fecha_seleccionada = st.date_input("📅 Fecha del sorteo:", datetime.now())
    with col_c:
        cantidad_jugadas = st.slider("🎟️ Jugadas:", min_value=1, max_value=8, value=4)

    if "Panamá" in tipo_loteria:
        c1, c2 = st.columns(2)
        with c1:
            s1_txt = st.text_input("Último Sorteo (1°, 2°, 3°):", value="4582, 1934, 7021")
        with c2:
            s2_txt = st.text_input("Penúltimo Sorteo (1°, 2°, 3°):", value="3109, 8412, 5590")

        if st.button("🚀 Ejecutar Análisis", use_container_width=True, type="primary"):
            s1 = [int(x.strip()) for x in s1_txt.split(",") if x.strip().isdigit()] or [4582, 1934, 7021]
            s2 = [int(x.strip()) for x in s2_txt.split(",") if x.strip().isdigit()] or [3109, 8412, 5590]
            historial = s1 + s2
            resultados = []

            if "Márkov" in modelo_cientifico:
                resultados = matriz_markov_transicion(historial, 10000)
            elif "Chi-Cuadrado" in modelo_cientifico:
                digitos_hist = [int(d) for num in historial for d in f"{num:04d}"]
                digitos_frios = sorted(range(10), key=lambda d: digitos_hist.count(d))
                for _ in range(cantidad_jugadas * 2):
                    num = int("".join(str(random.choice(digitos_frios[:5])) for _ in range(4)))
                    resultados.append(num)
            elif "Entropía" in modelo_cientifico:
                intentos = 0
                while len(resultados) < cantidad_jugadas and intentos < 500:
                    cand = random.randint(0, 9999)
                    digs = [int(d) for d in f"{cand:04d}"]
                    if calcular_entropia_shannon(digs) >= 1.5 and 12 <= sum(digs) <= 24:
                        resultados.append(cand)
                    intentos += 1
            elif "Simetría" in modelo_cientifico:
                vib_fecha = (fecha_seleccionada.day * 101 + fecha_seleccionada.month * 11) % 10000
                for base in historial:
                    espejo = (9999 - base + vib_fecha) % 10000
                    resultados.append(espejo)
            else:
                for base in historial:
                    cand = (9999 - base + random.choice([137, 273, 419])) % 10000
                    if not (1930 <= cand <= 2030) and cand % 100 != 0:
                        resultados.append(cand)

            resultados = list(dict.fromkeys(resultados))
            while len(resultados) < cantidad_jugadas:
                extra = random.randint(100, 9899)
                if extra not in resultados:
                    resultados.append(extra)

            st.session_state["ultimos_resultados"] = [f"{n:04d}" for n in resultados[:cantidad_jugadas]]

            for i, num in enumerate(resultados[:cantidad_jugadas], 1):
                billete = f"{num:04d}"
                chance = billete[-2:]
                digs = [int(d) for d in billete]
                ent = calcular_entropia_shannon(digs)
                raiz = sum(digs)
                while raiz > 9:
                    raiz = sum(int(d) for d in str(raiz))
                st.markdown(f"""
                <div class="tarjeta-boleto">
                    <div style="margin-bottom: 8px;">
                        <b style="color:#f8fafc;">Matriz #{i}</b> 
                        <span class="metrica-tag">H(X): {ent} bits</span>
                        <span class="metrica-tag">Σ: {sum(digs)}</span>
                        <span class="metrica-tag">Raíz Num: {raiz}</span>
                    </div>
                    <div>
                        <span class="bolilla">Billete: {billete}</span>
                        <span class="bolilla bolilla-oro">Chance: {chance}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    elif "Costa Rica" in tipo_loteria:
        c1, c2 = st.columns(2)
        with c1:
            s1_txt = st.text_input("Últimos resultados:", value="14, 68, 92")
        with c2:
            s2_txt = st.text_input("Resultados anteriores:", value="35, 41, 77")

        if st.button("🚀 Ejecutar Análisis", use_container_width=True, type="primary"):
            s1 = [int(x.strip()) for x in s1_txt.split(",") if x.strip().isdigit()] or [14, 68, 92]
            s2 = [int(x.strip()) for x in s2_txt.split(",") if x.strip().isdigit()] or [35, 41, 77]
            historial = s1 + s2

            if "Márkov" in modelo_cientifico:
                resultados = matriz_markov_transicion(historial, 100)
            elif "Chi-Cuadrado" in modelo_cientifico:
                resultados = chi_cuadrado_desviacion(historial, 100)
            elif "Simetría" in modelo_cientifico:
                resultados = [(99 - n + fecha_seleccionada.day) % 100 for n in historial]
            elif "Entropía" in modelo_cientifico:
                resultados = [n for n in range(100) if (n // 10) != (n % 10) and 6 <= ((n // 10) + (n % 10)) <= 13]
                random.shuffle(resultados)
            else:
                resultados = [n for n in range(32, 100) if n not in historial]
                random.shuffle(resultados)

            resultados = list(dict.fromkeys(resultados))[:cantidad_jugadas]
            st.session_state["ultimos_resultados"] = [f"{n:02d}" for n in resultados]
            bols_html = "".join([f'<span class="bolilla">{n:02d}</span>' for n in resultados])
            st.markdown(f'<div class="tarjeta-boleto">{bols_html}</div>', unsafe_allow_html=True)

    else:
        c1, c2 = st.columns(2)
        with c1:
            s1_txt = st.text_input("Último Sorteo (6 bolillas):", value="04, 12, 21, 30, 40, 48")
        with c2:
            s2_txt = st.text_input("Penúltimo Sorteo (6 bolillas):", value="07, 15, 22, 31, 41, 46")

        if st.button("🚀 Ejecutar Análisis", use_container_width=True, type="primary"):
            s1 = [int(x.strip()) for x in s1_txt.split(",") if x.strip().isdigit()][:6] or [4, 12, 21, 30, 40, 48]
            s2 = [int(x.strip()) for x in s2_txt.split(",") if x.strip().isdigit()][:6] or [7, 15, 22, 31, 41, 46]
            historial = s1 + s2

            if "Márkov" in modelo_cientifico:
                pool = [((x - 1) % 49) + 1 for x in matriz_markov_transicion(historial, 49)]
            elif "Chi-Cuadrado" in modelo_cientifico:
                pool = [((x - 1) % 49) + 1 for x in chi_cuadrado_desviacion(historial, 49)]
            elif "Simetría" in modelo_cientifico:
                pool = [((50 - x) % 49) + 1 for x in historial]
            elif "Valor Esperado" in modelo_cientifico:
                pool = list(range(32, 50)) + [n for n in range(1, 32) if n not in historial]
            else:
                pool = list(range(1, 50))

            pool = list(dict.fromkeys(pool))
            while len(pool) < 18:
                r = random.randint(1, 49)
                if r not in pool:
                    pool.append(r)

            combinaciones = list(itertools.combinations(pool[:16], 6))
            validas = [
                c for c in combinaciones
                if 115 <= sum(c) <= 185 and calcular_entropia_shannon(c) >= 1.75
            ] or combinaciones

            muestra = random.sample(validas, min(cantidad_jugadas, len(validas)))
            st.session_state["ultimos_resultados"] = ["-".join(f"{n:02d}" for n in sorted(c)) for c in muestra]

            for i, comb in enumerate(muestra, 1):
                c_ord = sorted(list(comb))
                ent = calcular_entropia_shannon(c_ord)
                ev_score = indice_anti_popularidad(c_ord)
                bols_html = "".join([f'<span class="bolilla">{n:02d}</span>' for n in c_ord])
                st.markdown(f"""
                <div class="tarjeta-boleto">
                    <div style="margin-bottom: 8px;">
                        <b style="color:#f8fafc;">Matriz #{i}</b>
                        <span class="metrica-tag">H(X): {ent}</span>
                        <span class="metrica-tag">Σ: {sum(c_ord)}</span>
                        <span class="metrica-tag">EV: {ev_score}%</span>
                    </div>
                    <div>{bols_html}</div>
                </div>
                """, unsafe_allow_html=True)

with tab_chat:
    st.markdown("### 🤖 Analista Estocástico & Oráculo Simbólico")
    st.caption(f"Contexto activo: **{tipo_loteria}**")

    with st.expander("🔑 Configurar API Key de Gemini (Opcional para IA Generativa completa)"):
        api_key_usuario = st.text_input("Pega tu Gemini API Key:", type="password", placeholder="AIzaSy...")

    SYSTEM_PROMPT = f"""
    Eres el 'Analista Cuantitativo y Oráculo Simbólico' de Crono-Lotería Quant AI.
    El usuario está analizando actualmente el sorteo: {tipo_loteria}.
    Tus conocimientos abarcan tres pilares maestros:
    1. CIENCIA Y MATEMÁTICAS DEL AZAR: Cadenas de Márkov, Entropía de Shannon, Chi-Cuadrado, Valor Esperado (EV anti-popularidad).
    2. CURIOSIDADES HISTÓRICAS: Stefan Mandel, Voltaire y La Condamine, sorteo de Bulgaria 2009.
    3. MISTICISMO Y NUMEROLOGÍA: Numerología pitagórica, raíz digital, números espejo, cábala de los sueños.
    """

    st.markdown("**💡 Preguntas rápidas para probar al bot:**")
    b1, b2, b3 = st.columns(3)
    prompt_rapido = None
    if b1.button("🎲 Curiosidad histórica", use_container_width=True):
        prompt_rapido = f"Cuéntame una curiosidad histórica real sobre alguien que usó matemáticas para vencer una lotería y cómo se relaciona con {tipo_loteria}."
    if b2.button("🔮 Numerología vs Ciencia", use_container_width=True):
        prompt_rapido = "Explícame la diferencia entre las pirámides/numerología pitagórica y la Entropía de Shannon."
    if b3.button("🧐 Analiza mi jugada", use_container_width=True):
        nums = st.session_state.get("ultimos_resultados", [])
        if nums:
            prompt_rapido = f"Analiza estos números que acabo de generar ({', '.join(nums)}) desde el punto de vista matemático y numerológico."
        else:
            prompt_rapido = f"Dame un ejemplo de combinación ideal para {tipo_loteria} explicando su base matemática y su vibración numerológica."

    if "mensajes_bot" not in st.session_state:
        st.session_state.mensajes_bot = [
            {
                "role": "assistant",
                "content": f"Bienvenido al laboratorio. Estoy calibrado para **{tipo_loteria}**. Pregúntame sobre modelos matemáticos, historias reales de ganadores o numerología."
            }
        ]

    for msg in st.session_state.mensajes_bot:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    entrada_chat = st.chat_input("Pregunta sobre matemáticas del azar, curiosidades o numerología...")
    pregunta_final = prompt_rapido or entrada_chat

    if pregunta_final:
        st.session_state.mensajes_bot.append({"role": "user", "content": pregunta_final})
        with st.chat_message("user"):
            st.markdown(pregunta_final)

        with st.chat_message("assistant"):
            if GENAI_DISPONIBLE and api_key_usuario:
                try:
                    client = genai.Client(api_key=api_key_usuario)
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=pregunta_final,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT,
                            temperature=0.7
                        )
                    )
                    respuesta_texto = response.text
                except Exception as e:
                    respuesta_texto = f"⚠️ Error conectando con la API de Gemini: `{e}`."
            else:
                q = pregunta_final.lower()
                if "curiosidad" in q or "historia" in q or "mandel" in q:
                    respuesta_texto = (
                        "**📜 Caso Real — Stefan Mandel y Voltaire:**\n"
                        "Stefan Mandel ganó 14 loterías globales usando reducción combinatoria. Voltaire y La Condamine ganaron en la lotería de París en 1729 explotando un fallo matemático en los premios."
                    )
                elif "pirámide" in q or "numerología" in q or "misticismo" in q:
                    respuesta_texto = (
                        "**🔮 Misticismo vs. Ciencia:**\n"
                        "La numerología usa reducción teosófica y sincronicidad. La ciencia (Entropía y EV) busca optimizar la dispersión para no repetir patrones humanos comunes."
                    )
                else:
                    respuesta_texto = (
                        f"**🧠 Análisis para {tipo_loteria}:**\n"
                        "Usa las pestañas del motor cuantitativo para generar combinaciones optimizadas y explora las métricas de entropía y valor esperado."
                    )

            st.markdown(respuesta_texto)
            st.session_state.mensajes_bot.append({"role": "assistant", "content": respuesta_texto})

st.markdown("""
<div class="disclaimer-box">
    ⚠️ Herramienta de análisis estadístico, simulación estocástica y exploración simbólica.<br>
    Uso estrictamente experimental y educativo.
</div>
""", unsafe_allow_html=True)
