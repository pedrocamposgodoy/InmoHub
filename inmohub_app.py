# ================================================================
# INMOHUB — B2B Real Estate Intelligence Platform
# App Streamlit para inmobiliarias de Granada
# Conectada a Supabase (misma BD que Nolasco Capital)
# ================================================================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import json
from datetime import datetime, date, timedelta
import random

st.set_page_config(
    page_title="InmoHub | B2B Real Estate Intelligence",
    layout="wide",
    page_icon="🏢",
    initial_sidebar_state="expanded"
)

# ================================================================
# CREDENCIALES SUPABASE
# ================================================================
SUPA_URL  = "https://odxixtgqcyddfqaapqgi.supabase.co"
ANON_KEY  = "sb_publishable_Obgti7yMfXw8wCUL2FbTtA_EWeyHuM9"

def _headers(token=None):
    h = {
        "apikey": ANON_KEY,
        "Content-Type": "application/json",
    }
    t = token or st.session_state.get("inmo_token")
    if t:
        h["Authorization"] = f"Bearer {t}"
    else:
        h["Authorization"] = f"Bearer {ANON_KEY}"
    return h

def supabase_get(path, params=""):
    try:
        r = requests.get(f"{SUPA_URL}/rest/v1/{path}{params}",
                         headers=_headers(), timeout=8)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

def supabase_patch(path, payload):
    try:
        r = requests.patch(f"{SUPA_URL}/rest/v1/{path}",
                           headers={**_headers(), "Prefer": "return=minimal"},
                           json=payload, timeout=8)
        return r.status_code in (200, 204)
    except Exception:
        return False

# ================================================================
# COLORES Y ESTILO
# ================================================================
BG        = "#0D1B2A"
SIDEBAR   = "#0F2744"
CARD      = "#1A2F4A"
CARD2     = "#142638"
ACCENT    = "#00C9A7"
RED       = "#FF4B4B"
AMBER     = "#FFB347"
BLUE      = "#4A9EFF"
TEXT      = "#FFFFFF"
TEXT2     = "#8899AA"
BORDER    = "#2A3F55"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

* {{ box-sizing: border-box; }}
html, body, [class*="css"] {{
    font-family: 'Space Grotesk', sans-serif !important;
    background-color: {BG} !important;
    color: {TEXT} !important;
}}
.block-container {{ padding-top: 1rem !important; padding-bottom: 0 !important; }}
[data-testid="stSidebar"] {{
    background: {SIDEBAR} !important;
    border-right: 1px solid {BORDER} !important;
    min-width: 260px !important;
}}
[data-testid="stSidebar"] .stButton>button {{
    background: transparent !important;
    border: none !important;
    color: {TEXT2} !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.85rem !important;
    text-align: left !important;
    padding: 0.6rem 1.2rem !important;
    border-radius: 0 8px 8px 0 !important;
    width: 100% !important;
    border-left: 3px solid transparent !important;
    transition: all 0.15s ease !important;
}}
[data-testid="stSidebar"] .stButton>button:hover {{
    background: rgba(0,201,167,0.08) !important;
    color: {ACCENT} !important;
    border-left: 3px solid {ACCENT} !important;
}}
.stButton>button {{
    background: #1E3A5A !important;
    border: 1px solid #4A7FA5 !important;
    color: #FFFFFF !important;
    font-family: 'Space Grotesk', sans-serif !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}}
.stButton>button:hover {{
    border-color: {ACCENT} !important;
    color: {ACCENT} !important;
    background: #1E4A6A !important;
}}
button[kind="primary"] {{
    background: {ACCENT} !important;
    color: {BG} !important;
    border: none !important;
    font-weight: 700 !important;
}}
button[kind="primary"]:hover {{
    background: #00A88A !important;
}}
.stTextInput>div>div>input, .stTextInput>div>div {{
    background: #1E3A5A !important;
    color: #FFFFFF !important;
    border: 1px solid #4A7FA5 !important;
    border-radius: 8px !important;
}}
.stTextInput>div>div>input::placeholder {{
    color: {TEXT2} !important;
}}
label, .stTextInput label, .stSelectbox label, [data-testid="stWidgetLabel"] p {{
    color: #CCDDEE !important;
    font-size: 0.88rem !important;
}}
.stTextInput {{ margin-bottom: 0.5rem; }}
div[data-baseweb="select"] > div {{
    background: #1E3A5A !important;
    border: 1px solid #4A7FA5 !important;
    color: #FFFFFF !important;
}}
div[data-baseweb="select"] span {{ color: #FFFFFF !important; }}
[data-testid="stMetricValue"] {{ color: {ACCENT} !important; font-family: 'Space Grotesk', sans-serif !important; }}
[data-testid="stMetricLabel"] {{ color: {TEXT2} !important; }}
.stDataFrame {{ background: {CARD} !important; }}
div[data-testid="stHorizontalBlock"] {{ gap: 1rem; }}
#MainMenu, footer, header {{ visibility: hidden; }}
hr {{ border-color: {BORDER} !important; opacity: 0.3; }}
.stTabs [data-baseweb="tab-list"] {{ background: {CARD} !important; border-radius: 8px; gap: 4px; padding: 4px; }}
.stTabs [data-baseweb="tab"] {{ background: transparent !important; color: {TEXT2} !important; border-radius: 6px !important; }}
.stTabs [aria-selected="true"] {{ background: {ACCENT} !important; color: {BG} !important; font-weight: 600 !important; }}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ================================================================
# DATOS MOCK — cuando Supabase está vacío o para demo
# ================================================================
ZONA_STATS_MOCK = [
    {"cp":"18001","num_propietarios":45,"brecha_pct_media":18.5,"brecha_renta_media":165,"contratos_vencen_90d":32,"lucro_cesante_total":7425,"precio_m2_medio":12.5,"rentabilidad_media":6.2},
    {"cp":"18005","num_propietarios":38,"brecha_pct_media":22.8,"brecha_renta_media":205,"contratos_vencen_90d":45,"lucro_cesante_total":7790,"precio_m2_medio":11.2,"rentabilidad_media":5.8},
    {"cp":"18008","num_propietarios":29,"brecha_pct_media":15.2,"brecha_renta_media":125,"contratos_vencen_90d":18,"lucro_cesante_total":3625,"precio_m2_medio":10.4,"rentabilidad_media":6.8},
    {"cp":"18003","num_propietarios":22,"brecha_pct_media":11.4,"brecha_renta_media":98, "contratos_vencen_90d":12,"lucro_cesante_total":2156,"precio_m2_medio":10.2,"rentabilidad_media":7.1},
    {"cp":"18004","num_propietarios":31,"brecha_pct_media":8.7, "brecha_renta_media":72, "contratos_vencen_90d":9, "lucro_cesante_total":2232,"precio_m2_medio":10.8,"rentabilidad_media":7.4},
    {"cp":"18010","num_propietarios":18,"brecha_pct_media":6.2, "brecha_renta_media":48, "contratos_vencen_90d":6, "lucro_cesante_total":864, "precio_m2_medio":9.8, "rentabilidad_media":7.8},
    {"cp":"18009","num_propietarios":14,"brecha_pct_media":24.1,"brecha_renta_media":188,"contratos_vencen_90d":21,"lucro_cesante_total":2632,"precio_m2_medio":8.2, "rentabilidad_media":5.4},
    {"cp":"18006","num_propietarios":26,"brecha_pct_media":13.8,"brecha_renta_media":112,"contratos_vencen_90d":15,"lucro_cesante_total":2912,"precio_m2_medio":10.0,"rentabilidad_media":6.5},
    {"cp":"18007","num_propietarios":19,"brecha_pct_media":9.3, "brecha_renta_media":78, "contratos_vencen_90d":8, "lucro_cesante_total":1482,"precio_m2_medio":9.5, "rentabilidad_media":7.2},
    {"cp":"18012","num_propietarios":12,"brecha_pct_media":7.1, "brecha_renta_media":55, "contratos_vencen_90d":4, "lucro_cesante_total":660, "precio_m2_medio":9.6, "rentabilidad_media":7.6},
]

LEADS_MOCK = [
    {"id":"LH-442","cp":"18005","perfil":"INVERSOR EN ESTRÉS","ia_score":85,"brecha_euros":396,"motivo_texto":"Rentabilidad 4.2% vs mercado 7.8%. Reforma pendiente 9 años. Contrato vencido hace 15 días.","argumentario":"Sr. propietario, su activo está rindiendo un 46% menos que el mercado. Llevamos detectados 9 años sin reforma y el contrato lleva 15 días vencido. Podemos ayudarle a recuperar 396€/mes.","estado":"nuevo","precio_lead":45,"exportado_inmohub":True},
    {"id":"LH-439","cp":"18001","perfil":"UPGRADE ESTÉTICO","ia_score":71,"brecha_euros":165,"motivo_texto":"Renta 15% bajo mercado. Contrato vence en 47 días. Inmueble sin reformar desde 2015.","argumentario":"Su piso en CP 18001 tiene potencial de subida del 15% en la próxima renovación. El contrato vence en 47 días — momento ideal para actuar.","estado":"nuevo","precio_lead":35,"exportado_inmohub":True},
    {"id":"LH-441","cp":"18009","perfil":"FATIGA DEL PROPIETARIO","ia_score":78,"brecha_euros":188,"motivo_texto":"ROE 3.1% con Euríbor al 4.2%. Hipoteca variable cuesta más que lo que rinde el activo.","argumentario":"El activo en CP 18009 tiene un ROE del 3.1% con una hipoteca al 5%. Está perdiendo dinero cada mes que lo mantiene. Venta o refinanciación urgente.","estado":"contactado","precio_lead":45,"exportado_inmohub":True},
    {"id":"LH-438","cp":"18005","perfil":"CONTRATO VENCIENDO","ia_score":62,"brecha_euros":120,"motivo_texto":"Contrato vence en 22 días. Renta actual 850€ vs mercado 970€.","argumentario":"Contrato en CP 18005 vence en 22 días. Oportunidad de renegociar a precio de mercado: +120€/mes. Primer agente que contacte tiene ventaja.","estado":"nuevo","precio_lead":35,"exportado_inmohub":True},
    {"id":"LH-437","cp":"18008","perfil":"INVERSOR EN ESTRÉS","ia_score":88,"brecha_euros":245,"motivo_texto":"Rentabilidad 4.8% vs mercado 7.3%. Tres incidencias de mantenimiento en 6 meses.","argumentario":"Propietario en CP 18008 con ROE crítico (4.8%) y fatiga de gestión documentada. Alta probabilidad de venta o traspaso de gestión.","estado":"nuevo","precio_lead":55,"exportado_inmohub":True},
]

CLIENTES_MOCK = [
    {"nombre":"Juan Pérez","inmuebles":3,"rent_actual":5.8,"rent_mercado":7.5,"perdida_mes":205,"alertas":["⚠️ Euríbor sube → ROE cae a 2.5%","⚠️ Contrato C/Recogidas vence en 45 días","✅ Deducción IRPF no aplicada: +1.200€"]},
    {"nombre":"María García","inmuebles":2,"rent_actual":6.9,"rent_mercado":7.8,"perdida_mes":98, "alertas":["🔔 Seguro 40% más caro que media zona","✅ Potencial reforma → +15% renta"]},
    {"nombre":"Carlos Ruiz", "inmuebles":5,"rent_actual":5.2,"rent_mercado":7.5,"perdida_mes":380,"alertas":["⚠️ 2 contratos vencen en 60 días","⚠️ 3 activos con rentabilidad crítica (<5%)","✅ Candidato a reestructuración de cartera"]},
]

# ================================================================
# AUTENTICACIÓN
# ================================================================
def login_inmobiliaria(email, password):
    try:
        r = requests.post(
            f"{SUPA_URL}/auth/v1/token?grant_type=password",
            headers={"apikey": ANON_KEY, "Content-Type": "application/json"},
            json={"email": email, "password": password},
            timeout=8
        )
        data = r.json()
        if r.status_code == 200 and "access_token" in data:
            return {"success": True, "token": data["access_token"], "email": email}
        return {"success": False, "error": data.get("error_description", "Credenciales incorrectas")}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ── Session state ────────────────────────────────────────────────
for k, v in [
    ("inmo_logged", False), ("inmo_token", None),
    ("inmo_email", None),   ("inmo_menu", "Dashboard"),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ================================================================
# LOGIN SCREEN
# ================================================================
if not st.session_state.inmo_logged:
    # CSS específico para login
    st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(135deg, #0A1628 0%, #0D1B2A 50%, #091422 100%) !important; }}
    </style>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        st.markdown("<br><br><br>", unsafe_allow_html=True)

        # Logo
        st.markdown(f"""
        <div style='text-align:center;margin-bottom:2.5rem;'>
            <div style='font-size:3rem;font-weight:700;color:{ACCENT};
                font-family:"Space Grotesk",sans-serif;letter-spacing:-2px;'>
                InmoHub
            </div>
            <div style='font-size:0.72rem;letter-spacing:0.3em;text-transform:uppercase;
                color:{TEXT2};margin-top:6px;'>B2B · Real Estate Intelligence · Granada</div>
        </div>
        """, unsafe_allow_html=True)

        # Card contenedor — solo visual, sin meter inputs dentro del HTML
        st.markdown(f"""
        <div style='background:#132035;border:1px solid #1E3A5A;border-radius:16px;
            padding:2rem 2rem 0.5rem;box-shadow:0 20px 60px rgba(0,0,0,0.5);'>
            <div style='font-size:0.7rem;letter-spacing:0.2em;text-transform:uppercase;
                color:{TEXT2};margin-bottom:1.5rem;text-align:center;'>
                Acceso para inmobiliarias
            </div>
        </div>
        """, unsafe_allow_html=True)

        email    = st.text_input("Email", placeholder="tu@inmobiliaria.com", key="login_email", label_visibility="collapsed")
        password = st.text_input("Contraseña", placeholder="Contraseña", type="password", key="login_pass", label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Acceder al panel →", use_container_width=True, type="primary"):
            if email and password:
                with st.spinner("Verificando..."):
                    result = login_inmobiliaria(email, password)
                if result["success"]:
                    st.session_state.inmo_logged = True
                    st.session_state.inmo_token  = result["token"]
                    st.session_state.inmo_email  = result["email"]
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
            else:
                st.warning("Completa email y contraseña")

        st.markdown(f"""
        <div style='text-align:center;margin-top:1rem;font-size:0.72rem;color:{TEXT2};'>
            ¿No tienes cuenta? Contacta con Nolasco Capital
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🎯 Entrar en modo demo", use_container_width=True):
            st.session_state.inmo_logged = True
            st.session_state.inmo_email  = "demo@inmohub.es"
            st.rerun()

    st.stop()

# ================================================================
# CARGAR DATOS REALES DE SUPABASE (con fallback a mock)
# ================================================================
@st.cache_data(ttl=60)
def cargar_zona_stats():
    data = supabase_get("zona_stats", "?order=brecha_pct_media.desc")
    return data if data else ZONA_STATS_MOCK

def cargar_leads():
    # Leer leads reales de Supabase — excluye descartados de vista activa
    data = supabase_get("leads_inmobiliarias",
                        "?order=created_at.desc&select=*,inmobiliarias(nombre)&estado=neq.descartado")
    if data and isinstance(data, list) and len(data) > 0:
        leads = []
        for l in data:
            uuid_completo = str(l.get("id", ""))  # UUID completo — NUNCA truncar
            leads.append({
                "id":           f"LH-{uuid_completo[:8].upper()}",  # Solo display
                "_id_real":     uuid_completo,                        # UUID completo para PATCH
                "cp":           l.get("cp", "18001"),
                "perfil":       _clasificar_perfil(l),
                "ia_score":     _calcular_score(l),
                "brecha_euros": float(l.get("rentabilidad_mercado", 0) or 0),
                "motivo_texto": l.get("motivo_texto", ""),
                "argumentario": l.get("argumentario", ""),
                "estado":       l.get("estado", "nuevo"),
                "precio_lead":  _calcular_precio(l),
                "exportado_inmohub": l.get("exportado_inmohub", False),
                "nombre":       l.get("nombre", "—"),
                "email":        l.get("email", "—"),
                "telefono":     l.get("telefono", "—"),
                "inmobiliaria": l.get("inmobiliarias", {}).get("nombre", "—") if isinstance(l.get("inmobiliarias"), dict) else "—",
            })
        return leads
    return LEADS_MOCK

def _clasificar_perfil(lead):
    motivo = (lead.get("motivo_texto") or "").lower()
    rent_act = float(lead.get("rentabilidad_actual") or 0)
    rent_mer = float(lead.get("rentabilidad_mercado") or 0)
    if "venc" in motivo or "contrato" in motivo:
        return "CONTRATO VENCIENDO"
    if "reforma" in motivo:
        return "UPGRADE ESTÉTICO"
    if rent_act > 0 and rent_mer > 0 and (rent_mer - rent_act) / max(rent_mer, 1) > 0.3:
        return "INVERSOR EN ESTRÉS"
    return "FATIGA DEL PROPIETARIO"

def _calcular_score(lead):
    score = 50
    rent_act = float(lead.get("rentabilidad_actual") or 0)
    rent_mer = float(lead.get("rentabilidad_mercado") or 0)
    motivo = (lead.get("motivo_texto") or "").lower()
    if rent_act > 0 and rent_mer > rent_act:
        score += min(int((rent_mer - rent_act) / max(rent_mer, 1) * 100), 30)
    if "venc" in motivo: score += 15
    if "reforma" in motivo: score += 10
    if "euribor" in motivo or "hipoteca" in motivo: score += 10
    return min(score, 99)

def _calcular_precio(lead):
    score = _calcular_score(lead)
    if score >= 80: return 55
    if score >= 65: return 45
    return 35

zona_stats = cargar_zona_stats()
leads_data  = cargar_leads()

# KPIs globales calculados
total_leads     = len(leads_data)
leads_nuevos    = len([l for l in leads_data if l.get("estado") == "nuevo"])
lucro_total     = sum(z.get("lucro_cesante_total", 0) for z in zona_stats)
contratos_90d   = sum(z.get("contratos_vencen_90d", 0) for z in zona_stats)
ia_scores_altos = len([l for l in leads_data if l.get("ia_score", 0) >= 75])
es_datos_reales = leads_data != LEADS_MOCK

# ================================================================
# SIDEBAR
# ================================================================
PAGES = [
    ("📊", "Dashboard"),
    ("📡", "Radar de Mercado"),
    ("🛒", "Lead Marketplace"),
    ("👥", "Fidelización"),
    ("🤖", "AI Advisory"),
    ("⚙️", "Configuración"),
]

with st.sidebar:
    # Logo
    st.markdown(f"""
    <div style='padding:1.5rem 1.2rem 1rem;'>
        <div style='display:flex;align-items:center;gap:10px;'>
            <div style='background:{ACCENT};border-radius:8px;padding:6px 10px;
                font-size:1.1rem;font-weight:700;color:{BG};'>IH</div>
            <div>
                <div style='font-size:1.2rem;font-weight:700;color:{TEXT};
                    font-family:"Space Grotesk",sans-serif;letter-spacing:-0.5px;'>
                    InmoHub <span style='color:{TEXT2};font-weight:400;font-size:0.8rem;'>| B2B</span>
                </div>
                <div style='font-size:0.6rem;letter-spacing:0.15em;text-transform:uppercase;
                    color:{TEXT2};'>Real Estate Intelligence</div>
            </div>
        </div>
    </div>
    <hr style='border:0;border-top:1px solid {BORDER};margin:0 0 0.8rem;'>
    """, unsafe_allow_html=True)

    # Usuario
    st.markdown(f"""
    <div style='padding:0.5rem 1rem;background:rgba(0,201,167,0.08);border-radius:8px;
        margin:0 0.8rem 1rem;border:1px solid rgba(0,201,167,0.2);'>
        <div style='font-size:0.65rem;color:{TEXT2};text-transform:uppercase;
            letter-spacing:0.1em;'>Inmobiliaria</div>
        <div style='font-size:0.82rem;color:{ACCENT};font-weight:500;margin-top:2px;'>
            {st.session_state.inmo_email}</div>
    </div>
    """, unsafe_allow_html=True)

    # Navegación
    st.markdown(f"<div style='font-size:0.6rem;letter-spacing:0.15em;text-transform:uppercase;color:{TEXT2};padding:0 1rem 0.4rem;'>Navegación</div>", unsafe_allow_html=True)

    for icon, page in PAGES:
        is_active = st.session_state.inmo_menu == page
        if is_active:
            st.markdown(f"""
            <div style='background:rgba(0,201,167,0.12);border-left:3px solid {ACCENT};
                padding:0.6rem 1.2rem;border-radius:0 8px 8px 0;margin-bottom:2px;
                display:flex;align-items:center;gap:10px;'>
                <span>{icon}</span>
                <span style='font-size:0.88rem;font-weight:600;color:{ACCENT};'>{page}</span>
            </div>""", unsafe_allow_html=True)
        else:
            if st.button(f"{icon}  {page}", key=f"nav_{page}", use_container_width=True):
                st.session_state.inmo_menu = page
                st.rerun()

    st.markdown(f"<hr style='border:0;border-top:1px solid {BORDER};margin:1rem 0 0.5rem;'>", unsafe_allow_html=True)

    # LIVE feed indicator
    st.markdown(f"""
    <div style='padding:0.5rem 1rem;display:flex;align-items:center;gap:8px;'>
        <div style='width:7px;height:7px;border-radius:50%;background:{ACCENT};
            box-shadow:0 0 6px {ACCENT};animation:pulse 2s infinite;'></div>
        <span style='font-size:0.72rem;color:{TEXT2};'>LIVE · Nolasco Capital</span>
    </div>
    <style>@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.4}}}}</style>
    """, unsafe_allow_html=True)

    if st.button("🚪 Cerrar sesión", use_container_width=True):
        st.session_state.inmo_logged = False
        st.session_state.inmo_token  = None
        st.session_state.inmo_email  = None
        st.rerun()

menu = st.session_state.inmo_menu

# ================================================================
# HELPERS UI
# ================================================================
def kpi_card(label, value, sub="", color=ACCENT, icon=""):
    return f"""
    <div style='background:{CARD};border:1px solid {BORDER};border-radius:12px;
        padding:1.2rem 1.4rem;position:relative;overflow:hidden;'>
        <div style='position:absolute;top:0;left:0;right:0;height:3px;background:{color};'></div>
        <div style='font-size:0.65rem;letter-spacing:0.12em;text-transform:uppercase;
            color:{TEXT2};margin-bottom:0.5rem;'>{label}</div>
        <div style='font-size:2rem;font-weight:700;color:{color};line-height:1;
            font-family:"Space Grotesk",sans-serif;'>{value} {icon}</div>
        <div style='font-size:0.72rem;color:{TEXT2};margin-top:0.3rem;'>{sub}</div>
    </div>"""

def lead_card(lead, preview=False):
    score = lead.get("ia_score", lead.get("rentabilidad_actual", 70))
    perfil = lead.get("perfil", "PROPIETARIO")
    cp = lead.get("cp", "18001")
    precio = lead.get("precio_lead", 45)
    brecha = lead.get("brecha_euros", lead.get("rentabilidad_mercado", 100))
    estado = lead.get("estado", "nuevo")
    score_color = RED if score >= 80 else (AMBER if score >= 60 else TEXT2)
    estado_color = ACCENT if estado == "nuevo" else (AMBER if estado == "contactado" else TEXT2)
    lid = lead.get("id", f"LH-{random.randint(400,499)}")

    # Cabecera siempre visible
    st.markdown(f"""
    <div style='background:{CARD};border:1px solid {BORDER};border-radius:12px;
        padding:1.1rem 1.2rem;margin-bottom:0.3rem;'>
        <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
            <div>
                <div style='font-size:0.72rem;color:{TEXT2};margin-bottom:4px;'>
                    ID: <span style='color:{TEXT};font-family:"DM Mono",monospace;'>{lid}</span>
                    &nbsp;|&nbsp; CP <strong style='color:{BLUE};'>{cp}</strong>
                    &nbsp;|&nbsp; <span style='color:{estado_color};'>● {estado.upper()}</span>
                </div>
                <div style='font-size:0.95rem;font-weight:600;color:{TEXT};'>{perfil}</div>
                <div style='font-size:0.82rem;color:{TEXT2};margin-top:4px;'>
                    Brecha: <strong style='color:{RED};'>-{brecha:,.0f}€/mes</strong>
                </div>
            </div>
            <div style='text-align:right;'>
                <div style='font-size:1.3rem;font-weight:700;color:{score_color};'>{score}%</div>
                <div style='font-size:0.62rem;color:{TEXT2};'>IA Score</div>
                <div style='margin-top:6px;background:{ACCENT};color:{BG};padding:4px 10px;
                    border-radius:6px;font-size:0.75rem;font-weight:700;'>€{precio}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Datos de contacto y argumentario (solo en vista completa)
    if not preview:
        nombre = lead.get("nombre", "—")
        email  = lead.get("email", "—")
        tel    = lead.get("telefono", "—")
        arg    = lead.get("argumentario", "Sin argumentario")
        st.markdown(f"""
        <div style='background:{CARD};border:1px solid {BORDER};border-top:none;
            border-radius:0 0 12px 12px;padding:0.8rem 1.2rem;margin-bottom:0.8rem;'>
            <div style='font-size:0.72rem;color:{TEXT2};margin-bottom:6px;
                text-transform:uppercase;letter-spacing:0.08em;'>Contacto</div>
            <div style='font-size:0.85rem;color:{TEXT};margin-bottom:0.8rem;'>
                👤 {nombre} &nbsp;·&nbsp; 📧 {email} &nbsp;·&nbsp; 📞 {tel}
            </div>
            <div style='background:rgba(0,201,167,0.08);border-radius:8px;
                padding:0.7rem;border-left:3px solid {ACCENT};'>
                <div style='font-size:0.68rem;color:{ACCENT};text-transform:uppercase;
                    letter-spacing:0.1em;margin-bottom:4px;'>Argumentario IA</div>
                <div style='font-size:0.82rem;color:{TEXT};font-style:italic;'>{arg}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def section_header(title, subtitle=""):
    st.markdown(f"""
    <div style='margin-bottom:1.5rem;'>
        <h2 style='font-size:1.5rem;font-weight:700;color:{TEXT};margin:0;
            font-family:"Space Grotesk",sans-serif;letter-spacing:-0.5px;'>{title}</h2>
        {"<div style='font-size:0.82rem;color:"+TEXT2+";margin-top:4px;'>"+subtitle+"</div>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)

# ================================================================
# PÁGINA 1 — DASHBOARD
# ================================================================
if menu == "Dashboard":
    # Header
    st.markdown(f"""
    <div style='display:flex;justify-content:space-between;align-items:center;
        margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid {BORDER};'>
        <div>
            <h1 style='font-size:1.6rem;font-weight:700;margin:0;color:{TEXT};
                font-family:"Space Grotesk",sans-serif;'>
                Granada <span style='color:{TEXT2};font-weight:400;'>|</span>
                Panel Global de Inteligencia Real Estate
            </h1>
            <div style='font-size:0.78rem;color:{TEXT2};margin-top:4px;'>
                {datetime.now().strftime("%A, %d %B %Y · %H:%M")}
            </div>
        </div>
        <div style='font-size:0.72rem;color:{TEXT2};text-align:right;'>
            <span style='color:{ACCENT};'>●</span> LIVE · Última actualización: hace 1 min
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("New Leads", leads_nuevos, "↗ Pendientes de revisar", ACCENT, "↗"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Potential Market Profit", f"€{lucro_total/1000:.0f}k", "Zona Granada · lucro cesante total", AMBER), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Active Portfolio Monitoring", contratos_90d, "Contratos vencen en 90 días", BLUE), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("Sale Propensity Scores (IA)", ia_scores_altos, "Leads con score ≥ 75%", RED), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Main content — mapa + ranking | fidelización
    col_main, col_right = st.columns([2.2, 1])

    with col_main:
        # Mapa de calor Granada por CP
        st.markdown(f"""
        <div style='background:{CARD};border:1px solid {BORDER};border-radius:12px;
            padding:1rem;margin-bottom:1rem;'>
            <div style='font-size:0.75rem;font-weight:600;color:{TEXT2};
                text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.8rem;'>
                🗺️ Mapa de Calor — Brecha de Renta por Zona (Granada)
            </div>
        """, unsafe_allow_html=True)

        # Mapa con Plotly usando scatter_mapbox
        df_mapa = pd.DataFrame(zona_stats)
        # Coordenadas aproximadas de CPs de Granada
        coords = {
            "18001": (37.178, -3.600), "18002": (37.182, -3.610),
            "18003": (37.170, -3.620), "18004": (37.168, -3.595),
            "18005": (37.174, -3.588), "18006": (37.160, -3.598),
            "18007": (37.155, -3.608), "18008": (37.185, -3.622),
            "18009": (37.195, -3.630), "18010": (37.188, -3.585),
            "18012": (37.148, -3.592),
        }
        df_mapa["lat"] = df_mapa["cp"].map(lambda c: coords.get(c, (37.17, -3.60))[0])
        df_mapa["lon"] = df_mapa["cp"].map(lambda c: coords.get(c, (37.17, -3.60))[1])
        df_mapa["color_val"] = df_mapa["brecha_pct_media"]
        df_mapa["label"] = df_mapa.apply(
            lambda r: f"CP {r['cp']}<br>Brecha: {r['brecha_pct_media']:.1f}%<br>€{r['brecha_renta_media']:.0f}/mes<br>{r['num_propietarios']} propietarios",
            axis=1
        )
        df_mapa["size"] = df_mapa["num_propietarios"].clip(10, 50)

        # Color por brecha — calculado manualmente para evitar bug colorbar Plotly
        def color_brecha(b):
            if b > 20: return "#FF4B4B"
            elif b > 10: return "#FFB347"
            else: return "#00C9A7"

        df_mapa["color_hex"] = df_mapa["brecha_pct_media"].apply(color_brecha)

        fig_map = go.Figure()
        # Añadir un trace por color para la leyenda
        for color, label in [("#FF4B4B","Brecha >20%"),("#FFB347","Brecha 10-20%"),("#00C9A7","Brecha <10%")]:
            mask = df_mapa["color_hex"] == color
            if mask.any():
                sub = df_mapa[mask]
                fig_map.add_trace(go.Scattermapbox(
                    lat=sub["lat"], lon=sub["lon"],
                    mode="markers+text",
                    name=label,
                    marker=dict(size=sub["size"], color=color, opacity=0.85),
                    text=sub["cp"],
                    textfont=dict(color="white", size=9),
                    textposition="middle center",
                    hovertext=sub["label"],
                    hoverinfo="text",
                ))
        fig_map.update_layout(
            mapbox=dict(
                style="carto-positron",
                center=dict(lat=37.174, lon=-3.601),
                zoom=12.5,
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            height=340,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(
                font=dict(size=10),
                bgcolor="rgba(13,27,42,0.8)",
                bordercolor=BORDER,
                x=0.01, y=0.99,
            ),
            showlegend=True,
        )
        # Leyenda manual
        st.markdown(f"""
        <div style='display:flex;gap:1rem;font-size:0.72rem;margin-bottom:0.5rem;'>
            <span><span style='color:{RED};'>●</span> ROJO: Brecha >20% (máx oportunidad)</span>
            <span><span style='color:{AMBER};'>●</span> AMARILLO: 10-20%</span>
            <span><span style='color:{ACCENT};'>●</span> VERDE: &lt;10%</span>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

        # Featured Leads
        st.markdown(f"""
        <div style='background:{CARD};border:1px solid {BORDER};border-radius:12px;padding:1rem;'>
            <div style='font-size:0.75rem;font-weight:600;color:{TEXT2};
                text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.8rem;'>
                ⚡ Featured Leads & Opportunities
            </div>
        """, unsafe_allow_html=True)
        for lead in leads_data[:3]:
            lead_card(lead, preview=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        # Ranking CPs
        st.markdown(f"""
        <div style='background:{CARD};border:1px solid {BORDER};border-radius:12px;
            padding:1rem;margin-bottom:1rem;'>
            <div style='font-size:0.75rem;font-weight:600;color:{TEXT2};
                text-transform:uppercase;letter-spacing:0.1em;margin-bottom:1rem;'>
                🏆 Ranking CPs por Oportunidad
            </div>
        """, unsafe_allow_html=True)
        for z in sorted(zona_stats, key=lambda x: x["brecha_pct_media"], reverse=True)[:6]:
            brecha = z["brecha_pct_media"]
            pct = min(brecha / 25 * 100, 100)
            color = RED if brecha > 20 else (AMBER if brecha > 10 else ACCENT)
            st.markdown(f"""
            <div style='margin-bottom:0.9rem;'>
                <div style='display:flex;justify-content:space-between;
                    font-size:0.82rem;margin-bottom:4px;'>
                    <span style='font-weight:600;color:{TEXT};'>CP {z["cp"]}</span>
                    <span style='color:{color};font-weight:700;'>{brecha:.1f}%</span>
                </div>
                <div style='font-size:0.72rem;color:{TEXT2};margin-bottom:4px;'>
                    €{z["brecha_renta_media"]:.0f}/mes · {z["contratos_vencen_90d"]} contratos 90d
                </div>
                <div style='background:{BORDER};border-radius:4px;height:4px;'>
                    <div style='background:{color};border-radius:4px;
                        height:4px;width:{pct:.0f}%;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Fidelización & AI Advisory
        st.markdown(f"""
        <div style='background:{CARD};border:1px solid {BORDER};border-radius:12px;padding:1rem;'>
            <div style='font-size:0.75rem;font-weight:600;color:{TEXT2};
                text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.8rem;'>
                🤖 Fidelización & AI Advisory
            </div>
        """, unsafe_allow_html=True)
        for cliente in CLIENTES_MOCK[:2]:
            alerta = next((a for a in cliente["alertas"] if "⚠️" in a), cliente["alertas"][0])
            st.markdown(f"""
            <div style='background:{CARD2};border-radius:8px;padding:0.8rem;
                margin-bottom:0.6rem;border-left:3px solid {AMBER};'>
                <div style='font-size:0.8rem;font-weight:600;color:{TEXT};margin-bottom:4px;'>
                    {cliente["nombre"]}
                </div>
                <div style='font-size:0.75rem;color:{AMBER};margin-bottom:4px;'>{alerta}</div>
                <div style='font-size:0.72rem;color:{TEXT2};'>
                    ROE: {cliente["rent_actual"]}% vs {cliente["rent_mercado"]}% mercado
                    · -{cliente["perdida_mes"]}€/mes
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Gráfico evolución rentabilidad
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background:{CARD};border:1px solid {BORDER};border-radius:12px;padding:1rem;'>
        <div style='font-size:0.75rem;font-weight:600;color:{TEXT2};
            text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem;'>
            📈 Evolución Rentabilidad vs. Mercado (Granada, 6m)
        </div>
    """, unsafe_allow_html=True)
    meses = ["Nov", "Dic", "Ene", "Feb", "Mar", "Abr"]
    rent_cartera = [6.1, 5.9, 5.8, 5.7, 5.8, 5.9]
    rent_mercado_line = [7.2, 7.3, 7.5, 7.6, 7.5, 7.8]
    fig_evo = go.Figure()
    fig_evo.add_trace(go.Bar(
        x=meses, y=rent_cartera, name="Tu cartera",
        marker_color=ACCENT, opacity=0.8,
    ))
    fig_evo.add_trace(go.Scatter(
        x=meses, y=rent_mercado_line, name="Mercado Granada",
        line=dict(color=RED, width=2, dash="dash"),
        mode="lines+markers",
        marker=dict(size=5),
    ))
    fig_evo.update_layout(
        height=220, margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
    )
    fig_evo.update_xaxes(gridcolor="#2A3F55", tickfont=dict(size=10, color="#8899AA"))
    fig_evo.update_yaxes(gridcolor="#2A3F55", tickfont=dict(size=10, color="#8899AA"))
    st.plotly_chart(fig_evo, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# ================================================================
# PÁGINA 2 — RADAR DE MERCADO (Capa 1)
# ================================================================
elif menu == "Radar de Mercado":
    section_header("📡 Radar de Mercado", "Capa 1 — Inteligencia agregada por zona · Sin datos personales")

    df_zona = pd.DataFrame(zona_stats)

    # Filtros
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        umbral_brecha = st.slider("Mostrar CPs con brecha >", 0, 25, 0, 1, format="%d%%")
    with col_f2:
        orden = st.selectbox("Ordenar por", ["Brecha % (mayor primero)",
                                              "Lucro cesante total",
                                              "Contratos vencen 90d",
                                              "Nº propietarios"], index=0)

    # Ordenar
    orden_col = {"Brecha % (mayor primero)": "brecha_pct_media",
                 "Lucro cesante total": "lucro_cesante_total",
                 "Contratos vencen 90d": "contratos_vencen_90d",
                 "Nº propietarios": "num_propietarios"}[orden]
    df_filtrado = df_zona[df_zona["brecha_pct_media"] >= umbral_brecha].sort_values(
        orden_col, ascending=False)

    # Tabla de zonas
    st.markdown(f"""
    <div style='background:{CARD};border:1px solid {BORDER};border-radius:12px;
        padding:1rem;margin-bottom:1.5rem;'>
        <div style='font-size:0.75rem;font-weight:600;color:{TEXT2};
            text-transform:uppercase;letter-spacing:0.1em;margin-bottom:1rem;'>
            📊 Tabla de Zonas — {len(df_filtrado)} CPs
        </div>
    """, unsafe_allow_html=True)

    for _, z in df_filtrado.iterrows():
        brecha = z["brecha_pct_media"]
        color  = RED if brecha > 20 else (AMBER if brecha > 10 else ACCENT)
        oportu = "MUY ALTA" if brecha > 20 else ("ALTA" if brecha > 10 else "MEDIA")
        pct_bar = min(brecha / 25 * 100, 100)
        st.markdown(f"""
        <div style='background:{CARD2};border-radius:10px;padding:0.9rem 1.1rem;
            margin-bottom:0.5rem;border:1px solid {BORDER};'>
            <div style='display:flex;justify-content:space-between;align-items:center;'>
                <div style='flex:1;'>
                    <div style='display:flex;align-items:center;gap:12px;margin-bottom:6px;'>
                        <span style='font-size:1rem;font-weight:700;color:{TEXT};'>CP {z["cp"]}</span>
                        <span style='background:{color}22;color:{color};padding:2px 8px;
                            border-radius:4px;font-size:0.68rem;font-weight:700;
                            letter-spacing:0.05em;'>{oportu}</span>
                    </div>
                    <div style='display:flex;gap:1.5rem;font-size:0.78rem;color:{TEXT2};'>
                        <span>👥 {int(z["num_propietarios"])} propietarios</span>
                        <span>📉 {brecha:.1f}% brecha</span>
                        <span>💸 €{z["brecha_renta_media"]:.0f}/mes</span>
                        <span>🔔 {int(z["contratos_vencen_90d"])} contratos/90d</span>
                        <span>📍 €{z["precio_m2_medio"]:.1f}/m²</span>
                    </div>
                    <div style='background:{BORDER};border-radius:4px;height:3px;margin-top:8px;'>
                        <div style='background:{color};border-radius:4px;
                            height:3px;width:{pct_bar:.0f}%;'></div>
                    </div>
                </div>
                <div style='text-align:right;margin-left:1.5rem;'>
                    <div style='font-size:1.4rem;font-weight:700;color:{color};'>
                        €{z["lucro_cesante_total"]:,.0f}
                    </div>
                    <div style='font-size:0.68rem;color:{TEXT2};'>lucro cesante total/mes</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Gráfico comparativo
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        fig_brecha = go.Figure(go.Bar(
            x=df_filtrado["cp"], y=df_filtrado["brecha_pct_media"],
            marker_color=[RED if b > 20 else AMBER if b > 10 else ACCENT
                          for b in df_filtrado["brecha_pct_media"]],
            text=df_filtrado["brecha_pct_media"].apply(lambda x: f"{x:.1f}%"),
            textposition="outside", textfont=dict(color=TEXT, size=10),
        ))
        fig_brecha.update_layout(
            title=dict(text="Brecha % por CP", font=dict(size=12)),
            height=280, margin=dict(l=0,r=0,t=30,b=0),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        fig_brecha.update_xaxes(gridcolor="#2A3F55", tickfont=dict(size=10, color="#8899AA"))
        fig_brecha.update_yaxes(gridcolor="#2A3F55", tickfont=dict(size=10, color="#8899AA"))
        st.plotly_chart(fig_brecha, use_container_width=True, config={"displayModeBar": False})

    with col_g2:
        fig_lucro = go.Figure(go.Bar(
            x=df_filtrado["cp"], y=df_filtrado["lucro_cesante_total"],
            marker_color=ACCENT, opacity=0.8,
            text=df_filtrado["lucro_cesante_total"].apply(lambda x: f"€{x:,.0f}"),
            textposition="outside", textfont=dict(color=TEXT, size=9),
        ))
        fig_lucro.update_layout(
            title=dict(text="Lucro Cesante Total €/mes por CP", font=dict(size=12)),
            height=280, margin=dict(l=0,r=0,t=30,b=0),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        fig_lucro.update_xaxes(gridcolor="#2A3F55", tickfont=dict(size=10, color="#8899AA"))
        fig_lucro.update_yaxes(gridcolor="#2A3F55", tickfont=dict(size=10, color="#8899AA"))
        st.plotly_chart(fig_lucro, use_container_width=True, config={"displayModeBar": False})

    # Radar de vencimientos
    st.markdown(f"""
    <div style='background:{CARD};border:1px solid {BORDER};border-radius:12px;padding:1rem;'>
        <div style='font-size:0.75rem;font-weight:600;color:{TEXT2};
            text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.8rem;'>
            🔔 Radar de Vencimientos — Contratos próximos 90 días
        </div>
        <div style='font-size:0.82rem;color:{TEXT2};margin-bottom:0.8rem;'>
            Contacta al propietario <strong style='color:{ACCENT};'>ANTES</strong>
            que la competencia. Cada día cuenta.
        </div>
    """, unsafe_allow_html=True)
    top_venc = sorted(zona_stats, key=lambda x: x["contratos_vencen_90d"], reverse=True)[:5]
    for z in top_venc:
        urgencia = "🔴" if z["contratos_vencen_90d"] > 30 else ("🟡" if z["contratos_vencen_90d"] > 15 else "🟢")
        st.markdown(f"""
        <div style='display:flex;justify-content:space-between;padding:0.5rem 0;
            border-bottom:1px solid {BORDER};font-size:0.85rem;'>
            <span>{urgencia} <strong>CP {z["cp"]}</strong></span>
            <span style='color:{TEXT2};'>{int(z["contratos_vencen_90d"])} contratos</span>
            <span style='color:{AMBER};'>Brecha media: {z["brecha_pct_media"]:.1f}%</span>
            <span style='color:{ACCENT};'>€{z["brecha_renta_media"]:.0f}/mes potencial</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ================================================================
# PÁGINA 3 — LEAD MARKETPLACE (Capa 2)
# ================================================================
elif menu == "Lead Marketplace":
    section_header("🛒 Lead Marketplace", "Capa 2 — Solo propietarios que autorizaron compartir sus datos (RGPD)")

    # KPIs por estado
    nuevos     = [l for l in leads_data if l.get("estado") == "nuevo"]
    contactados = [l for l in leads_data if l.get("estado") == "contactado"]
    cerrados   = [l for l in leads_data if l.get("estado") == "cerrado"]

    # KPI cards clickables — filtran la lista al pulsar
    if "crm_filtro" not in st.session_state:
        st.session_state["crm_filtro"] = "Nuevos 🔴"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        sel_todos = st.session_state["crm_filtro"] == "Todos"
        borde_todos = f"3px solid {ACCENT}" if sel_todos else f"3px solid {ACCENT}33"
        if st.button(f"**{len(leads_data)}**\nTODOS", key="kpi_todos", use_container_width=True):
            st.session_state["crm_filtro"] = "Todos"
            st.rerun()
        st.markdown(f"""<div style='margin-top:-8px;text-align:center;font-size:0.7rem;
            color:{ACCENT if sel_todos else TEXT2};text-transform:uppercase;'>Total leads</div>""",
            unsafe_allow_html=True)
    with c2:
        sel_nv = st.session_state["crm_filtro"] == "Nuevos 🔴"
        if st.button(f"**{len(nuevos)}**\n🔴 NUEVOS", key="kpi_nuevos", use_container_width=True):
            st.session_state["crm_filtro"] = "Nuevos 🔴"
            st.rerun()
        st.markdown(f"""<div style='margin-top:-8px;text-align:center;font-size:0.7rem;
            color:{RED if sel_nv else TEXT2};text-transform:uppercase;'>Pendientes</div>""",
            unsafe_allow_html=True)
    with c3:
        sel_ct = st.session_state["crm_filtro"] == "Contactados 🟡"
        if st.button(f"**{len(contactados)}**\n🟡 CONTACTADOS", key="kpi_contactados", use_container_width=True):
            st.session_state["crm_filtro"] = "Contactados 🟡"
            st.rerun()
        st.markdown(f"""<div style='margin-top:-8px;text-align:center;font-size:0.7rem;
            color:{AMBER if sel_ct else TEXT2};text-transform:uppercase;'>En seguimiento</div>""",
            unsafe_allow_html=True)
    with c4:
        sel_cr = st.session_state["crm_filtro"] == "Cerrados ✅"
        if st.button(f"**{len(cerrados)}**\n✅ CERRADOS", key="kpi_cerrados", use_container_width=True):
            st.session_state["crm_filtro"] = "Cerrados ✅"
            st.rerun()
        st.markdown(f"""<div style='margin-top:-8px;text-align:center;font-size:0.7rem;
            color:#00C9A7 if sel_cr else {TEXT2};text-transform:uppercase;'>Tratos ganados</div>""",
            unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Filtros — el estado se sincroniza con los KPI cards
    col_f1, col_f2, col_f3 = st.columns(3)
    opciones_estado = ["Nuevos 🔴","Contactados 🟡","Cerrados ✅","Todos"]
    idx_actual = opciones_estado.index(st.session_state["crm_filtro"]) if st.session_state["crm_filtro"] in opciones_estado else 0
    with col_f1:
        filtro_estado = st.selectbox("Estado", opciones_estado, index=idx_actual,
                                     key="sel_estado_crm",
                                     on_change=lambda: st.session_state.update({"crm_filtro": st.session_state["sel_estado_crm"]}))
    with col_f2:
        filtro_perfil = st.selectbox("Perfil", ["Todos","INVERSOR EN ESTRÉS","UPGRADE ESTÉTICO","CONTRATO VENCIENDO","FATIGA DEL PROPIETARIO"])
    with col_f3:
        filtro_score = st.selectbox("IA Score", ["Todos",">80%","60-80%","<60%"])
    
    filtro_estado = st.session_state["crm_filtro"]

    # Aplicar filtros
    estado_map = {"Nuevos 🔴":"nuevo","Contactados 🟡":"contactado","Cerrados ✅":"cerrado","Todos":None}
    estado_fil = estado_map[filtro_estado]
    leads_filtrados = leads_data[:]
    if estado_fil:
        leads_filtrados = [l for l in leads_filtrados if l.get("estado") == estado_fil]
    if filtro_perfil != "Todos":
        leads_filtrados = [l for l in leads_filtrados if filtro_perfil in l.get("perfil","")]
    if filtro_score == ">80%":
        leads_filtrados = [l for l in leads_filtrados if l.get("ia_score",0) > 80]
    elif filtro_score == "60-80%":
        leads_filtrados = [l for l in leads_filtrados if 60 <= l.get("ia_score",0) <= 80]
    elif filtro_score == "<60%":
        leads_filtrados = [l for l in leads_filtrados if l.get("ia_score",0) < 60]

    st.markdown("<br>", unsafe_allow_html=True)

    if not leads_filtrados:
        st.markdown(f"""
        <div style='background:{CARD};border:1px solid {BORDER};border-radius:12px;
            padding:2rem;text-align:center;'>
            <div style='font-size:2rem;margin-bottom:0.5rem;'>📭</div>
            <div style='color:{TEXT2};font-size:0.9rem;'>No hay leads en este estado.</div>
            <div style='color:{TEXT2};font-size:0.8rem;margin-top:4px;'>
                Los leads aparecen cuando propietarios de Nolasco Capital solicitan asesoramiento.
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        for lead in leads_filtrados:
            estado_actual = lead.get("estado","nuevo")
            lid = lead.get("id","")
            id_real = lead.get("_id_real", lid)
            # Si id_real es igual a lid (mock) o está vacío, no hay UUID real
            es_real = id_real and id_real != lid

            col_card, col_actions = st.columns([4, 1])
            with col_card:
                lead_card(lead, preview=False)
            with col_actions:
                st.markdown("<br><br><br>", unsafe_allow_html=True)
                if estado_actual == "nuevo":
                    if st.button("📞 Contactado", key=f"cont_{lid}", use_container_width=True):
                        ok = supabase_patch(f"leads_inmobiliarias?id=eq.{id_real}", {"estado":"contactado"})
                        if ok:
                            st.toast("✅ Lead marcado como Contactado", icon="📞")
                            st.session_state["crm_filtro"] = "Contactados 🟡"
                        else:
                            st.toast("⚠️ Error al actualizar", icon="❌")
                        st.rerun()
                    if st.button("⛔ Descartar", key=f"desc_{lid}", use_container_width=True):
                        ok = supabase_patch(f"leads_inmobiliarias?id=eq.{id_real}", {"estado":"descartado"})
                        if ok:
                            st.toast("Lead descartado — no aparecerá más en el panel", icon="⛔")
                        else:
                            st.toast("⚠️ Error al actualizar", icon="❌")
                        st.rerun()
                elif estado_actual == "contactado":
                    if st.button("✅ Cerrar trato", key=f"cerr_{lid}", use_container_width=True):
                        ok = supabase_patch(f"leads_inmobiliarias?id=eq.{id_real}", {"estado":"cerrado"})
                        if ok:
                            st.toast("🎉 ¡Trato cerrado! Lead archivado.", icon="✅")
                            st.session_state["crm_filtro"] = "Cerrados ✅"
                        else:
                            st.toast("⚠️ Error al actualizar", icon="❌")
                        st.rerun()
                    if st.button("↩️ Reabrir", key=f"reab_{lid}", use_container_width=True):
                        ok = supabase_patch(f"leads_inmobiliarias?id=eq.{id_real}", {"estado":"nuevo"})
                        if ok:
                            st.toast("Lead reabierto como Nuevo", icon="↩️")
                            st.session_state["crm_filtro"] = "Nuevos 🔴"
                        st.rerun()
                elif estado_actual == "cerrado":
                    st.markdown(f"""
                    <div style='font-size:0.75rem;color:#888;text-align:center;
                        padding:0.5rem;background:{CARD};border-radius:8px;margin-bottom:4px;'>
                        ✅ Trato cerrado
                    </div>""", unsafe_allow_html=True)
                    if st.button("↩️ Reabrir", key=f"reab2_{lid}", use_container_width=True):
                        ok = supabase_patch(f"leads_inmobiliarias?id=eq.{id_real}", {"estado":"nuevo"})
                        if ok:
                            st.toast("Lead reabierto como Nuevo", icon="↩️")
                        st.rerun()

    # Exportar CSV
    st.markdown("<br>", unsafe_allow_html=True)
    if leads_filtrados:
        df_export = pd.DataFrame([
            {k:v for k,v in l.items() if not k.startswith("_")}
            for l in leads_filtrados
        ])
        csv = df_export.to_csv(index=False)
        st.download_button(
            "📥 Exportar leads a CSV",
            data=csv,
            file_name=f"leads_inmohub_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ================================================================
# PÁGINA 4 — FIDELIZACIÓN
# ================================================================
elif menu == "Fidelización":
    section_header("👥 Fidelización de Clientes", "Family Office — Tu cliente nunca te abandona")

    cliente_sel = st.selectbox("Seleccionar cliente",
                               [c["nombre"] for c in CLIENTES_MOCK])
    cliente = next(c for c in CLIENTES_MOCK if c["nombre"] == cliente_sel)

    # Header cliente
    rent_diff = cliente["rent_mercado"] - cliente["rent_actual"]
    st.markdown(f"""
    <div style='background:{CARD};border:1px solid {BORDER};border-radius:12px;
        padding:1.2rem;margin-bottom:1rem;'>
        <div style='display:flex;justify-content:space-between;align-items:center;'>
            <div>
                <div style='font-size:1.2rem;font-weight:700;color:{TEXT};'>{cliente["nombre"]}</div>
                <div style='font-size:0.8rem;color:{TEXT2};margin-top:4px;'>
                    {cliente["inmuebles"]} inmuebles gestionados
                </div>
            </div>
            <div style='display:flex;gap:2rem;'>
                <div style='text-align:center;'>
                    <div style='font-size:1.4rem;font-weight:700;color:{AMBER};'>
                        {cliente["rent_actual"]}%
                    </div>
                    <div style='font-size:0.68rem;color:{TEXT2};'>ROE Actual</div>
                </div>
                <div style='text-align:center;'>
                    <div style='font-size:1.4rem;font-weight:700;color:{ACCENT};'>
                        {cliente["rent_mercado"]}%
                    </div>
                    <div style='font-size:0.68rem;color:{TEXT2};'>Mercado</div>
                </div>
                <div style='text-align:center;'>
                    <div style='font-size:1.4rem;font-weight:700;color:{RED};'>
                        -€{cliente["perdida_mes"]}
                    </div>
                    <div style='font-size:0.68rem;color:{TEXT2};'>Pérdida/mes</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Alertas activas
    st.markdown(f"""
    <div style='background:{CARD};border:1px solid {BORDER};border-radius:12px;padding:1rem;margin-bottom:1rem;'>
        <div style='font-size:0.75rem;font-weight:600;color:{TEXT2};
            text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.8rem;'>
            🚨 Alertas Activas
        </div>
    """, unsafe_allow_html=True)
    for alerta in cliente["alertas"]:
        color_a = RED if "⚠️" in alerta else (ACCENT if "✅" in alerta else AMBER)
        st.markdown(f"""
        <div style='background:{CARD2};border-left:3px solid {color_a};
            border-radius:6px;padding:0.6rem 1rem;margin-bottom:0.4rem;
            font-size:0.85rem;color:{TEXT};'>
            {alerta}
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Benchmark gastos
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.markdown(f"""
        <div style='background:{CARD};border:1px solid {BORDER};border-radius:12px;padding:1rem;'>
            <div style='font-size:0.75rem;font-weight:600;color:{TEXT2};
                text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.8rem;'>
                💰 Benchmark Gastos Operativos
            </div>
            <div style='font-size:0.82rem;'>
                <div style='display:flex;justify-content:space-between;padding:5px 0;
                    border-bottom:1px solid {BORDER};'>
                    <span style='color:{TEXT2};'>IBI anual</span>
                    <span>450€ <span style='color:{ACCENT};font-size:0.72rem;'>✅ OK</span></span>
                </div>
                <div style='display:flex;justify-content:space-between;padding:5px 0;
                    border-bottom:1px solid {BORDER};'>
                    <span style='color:{TEXT2};'>Seguro</span>
                    <span>300€ <span style='color:{RED};font-size:0.72rem;'>↑40% sobre media</span></span>
                </div>
                <div style='display:flex;justify-content:space-between;padding:5px 0;'>
                    <span style='color:{TEXT2};'>Comunidad/mes</span>
                    <span>120€ <span style='color:{ACCENT};font-size:0.72rem;'>✅ OK</span></span>
                </div>
            </div>
            <div style='margin-top:0.8rem;background:rgba(255,75,75,0.1);
                border-radius:6px;padding:0.5rem;font-size:0.78rem;color:{RED};'>
                Ahorro potencial en seguro: <strong>85€/mes = 1.020€/año</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b2:
        st.markdown(f"""
        <div style='background:{CARD};border:1px solid {BORDER};border-radius:12px;padding:1rem;'>
            <div style='font-size:0.75rem;font-weight:600;color:{TEXT2};
                text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.8rem;'>
                📊 Ingeniería Financiera ROE vs Deuda
            </div>
            <div style='font-size:0.82rem;'>
                <div style='display:flex;justify-content:space-between;padding:5px 0;
                    border-bottom:1px solid {BORDER};'>
                    <span style='color:{TEXT2};'>Euríbor actual</span>
                    <span style='color:{AMBER};'>4.2%</span>
                </div>
                <div style='display:flex;justify-content:space-between;padding:5px 0;
                    border-bottom:1px solid {BORDER};'>
                    <span style='color:{TEXT2};'>Hipoteca (E+0.8%)</span>
                    <span style='color:{RED};'>5.0%</span>
                </div>
                <div style='display:flex;justify-content:space-between;padding:5px 0;'>
                    <span style='color:{TEXT2};'>ROE inmueble</span>
                    <span style='color:{AMBER};'>{cliente["rent_actual"]}%</span>
                </div>
            </div>
            <div style='margin-top:0.8rem;background:rgba(255,75,75,0.1);
                border-radius:6px;padding:0.5rem;font-size:0.78rem;color:{RED};'>
                ⚠️ Hipoteca cuesta más que lo que rinde el activo.<br>
                <strong>Sugerido: amortizar parcialmente o vender y reinvertir.</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Acciones
    st.markdown("<br>", unsafe_allow_html=True)
    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        st.button("📄 Generar Informe Patrimonial PDF", use_container_width=True)
    with col_a2:
        st.button("📊 Simulador de Reinversión", use_container_width=True)
    with col_a3:
        st.button("📅 Programar Reunión", use_container_width=True)

# ================================================================
# PÁGINA 5 — AI ADVISORY
# ================================================================
elif menu == "AI Advisory":
    section_header("🤖 AI Advisory", "Inteligencia artificial aplicada al patrimonio inmobiliario")

    # Disponible en MVP
    st.markdown(f"""
    <div style='background:{CARD};border:1px solid {BORDER};border-radius:12px;
        padding:1.2rem;margin-bottom:1rem;border-top:3px solid {ACCENT};'>
        <div style='font-size:0.75rem;font-weight:600;color:{ACCENT};
            text-transform:uppercase;letter-spacing:0.1em;margin-bottom:1rem;'>
            ✅ Disponible en MVP
        </div>
    """, unsafe_allow_html=True)

    # Generador de argumentarios
    st.markdown(f"<div style='font-size:0.9rem;font-weight:600;color:{TEXT};margin-bottom:0.5rem;'>🗣️ Generador de Argumentarios NLP</div>", unsafe_allow_html=True)
    lead_sel = st.selectbox("Selecciona un lead", [l.get("id","") for l in leads_data], key="arg_lead")
    lead_obj = next((l for l in leads_data if l.get("id") == lead_sel), leads_data[0])
    if st.button("⚡ Generar argumentario", key="gen_arg"):
        arg = lead_obj.get("argumentario", "Sin argumentario disponible")
        st.markdown(f"""
        <div style='background:{CARD2};border-left:3px solid {ACCENT};border-radius:8px;
            padding:1rem;margin-top:0.5rem;font-size:0.9rem;font-style:italic;color:{TEXT};'>
            "{arg}"
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # IA Score
    st.markdown(f"<div style='font-size:0.9rem;font-weight:600;color:{TEXT};margin-bottom:0.5rem;'>📊 IA Score de Venta — Distribución</div>", unsafe_allow_html=True)
    scores = [l.get("ia_score", 70) for l in leads_data]
    fig_score = go.Figure(go.Histogram(
        x=scores, nbinsx=10, marker_color=ACCENT, opacity=0.8,
    ))
    fig_score.update_layout(
        height=180, margin=dict(l=0,r=0,t=0,b=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    fig_score.update_xaxes(gridcolor="#2A3F55", tickfont=dict(size=10, color="#8899AA"))
    fig_score.update_yaxes(gridcolor="#2A3F55", tickfont=dict(size=10, color="#8899AA"))
    st.plotly_chart(fig_score, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

    # Coming Soon
    coming_soon = [
        ("⚖️", "Legal-Audit (Contratos)", "Extracción automática de cláusulas IPC no aplicadas y seguros de impago no reclamados."),
        ("📸", "Visual-Score (Fotos)", "Clasificación IA de calidad del inmueble por foto para detectar activos infravalorados."),
        ("🔨", "Simulador CAPEX", "Reforma mínima recomendada con estimación de subida de renta tras la mejora."),
        ("😓", "Detector Fatiga del Propietario", "Predice quién va a querer vender pronto basándose en estrés financiero y logístico."),
    ]
    st.markdown(f"""
    <div style='background:{CARD};border:1px solid {BORDER};border-radius:12px;
        padding:1.2rem;margin-top:1rem;border-top:3px solid {TEXT2};'>
        <div style='font-size:0.75rem;font-weight:600;color:{TEXT2};
            text-transform:uppercase;letter-spacing:0.1em;margin-bottom:1rem;'>
            🔜 Próximamente
        </div>
    """, unsafe_allow_html=True)
    for icon, titulo, desc in coming_soon:
        st.markdown(f"""
        <div style='background:{CARD2};border-radius:8px;padding:0.8rem 1rem;
            margin-bottom:0.5rem;opacity:0.6;border:1px solid {BORDER};'>
            <div style='font-size:0.88rem;font-weight:600;color:{TEXT};margin-bottom:3px;'>
                {icon} {titulo}
                <span style='background:{BORDER};color:{TEXT2};padding:1px 7px;
                    border-radius:4px;font-size:0.65rem;margin-left:8px;'>COMING SOON</span>
            </div>
            <div style='font-size:0.78rem;color:{TEXT2};'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ================================================================
# PÁGINA 6 — CONFIGURACIÓN
# ================================================================
elif menu == "Configuración":
    section_header("⚙️ Configuración", "Gestión de tu cuenta InmoHub")

    st.markdown(f"""
    <div style='background:{CARD};border:1px solid {BORDER};border-radius:12px;padding:1.2rem;margin-bottom:1rem;'>
        <div style='font-size:0.75rem;font-weight:600;color:{TEXT2};
            text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.8rem;'>
            👤 Tu cuenta
        </div>
        <div style='font-size:0.9rem;'>
            <strong>Email:</strong> {st.session_state.inmo_email}<br>
            <strong>Plan:</strong> <span style='color:{ACCENT};'>MVP Demo</span><br>
            <strong>Conexión Nolasco Capital:</strong>
            <span style='color:{ACCENT};'>● Activa</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background:{CARD};border:1px solid {BORDER};border-radius:12px;padding:1.2rem;'>
        <div style='font-size:0.75rem;font-weight:600;color:{TEXT2};
            text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.8rem;'>
            📦 Pricing
        </div>
        <div style='font-size:0.85rem;'>
            <div style='display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid {BORDER};'>
                <span>Radar de Mercado (Capa 1)</span>
                <span style='color:{ACCENT};font-weight:700;'>199€/mes</span>
            </div>
            <div style='display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid {BORDER};'>
                <span>Lead Marketplace (Capa 2)</span>
                <span style='color:{ACCENT};font-weight:700;'>35–150€/lead</span>
            </div>
            <div style='display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid {BORDER};'>
                <span>Fidelización Premium</span>
                <span style='color:{ACCENT};font-weight:700;'>99€/mes adicional</span>
            </div>
            <div style='display:flex;justify-content:space-between;padding:6px 0;'>
                <span>Informe Patrimonial PDF</span>
                <span style='color:{ACCENT};font-weight:700;'>49€/informe</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ================================================================
# FOOTER LIVE
# ================================================================
st.markdown(f"""
<div style='position:fixed;bottom:0;left:260px;right:0;
    background:{CARD};border-top:1px solid {BORDER};
    padding:0.4rem 1.5rem;display:flex;justify-content:space-between;
    align-items:center;z-index:999;'>
    <div style='font-size:0.72rem;color:{TEXT2};display:flex;align-items:center;gap:6px;'>
        <div style='width:6px;height:6px;border-radius:50%;background:{ACCENT};
            box-shadow:0 0 5px {ACCENT};'></div>
        LIVE Feed from Nolasco Capital
    </div>
    <div style='font-size:0.72rem;color:{TEXT2};'>
        Last Update: {datetime.now().strftime("%H:%M")}
    </div>
</div>
""", unsafe_allow_html=True)
