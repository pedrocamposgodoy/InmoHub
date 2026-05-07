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
    ("👤", "Clientes"),
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

    # Siempre recargar leads frescos desde Supabase
    leads_data = cargar_leads()

    nuevos      = [l for l in leads_data if l.get("estado") == "nuevo"]
    contactados = [l for l in leads_data if l.get("estado") == "contactado"]
    cerrados    = [l for l in leads_data if l.get("estado") == "cerrado"]

    # ── TOTALES ──────────────────────────────────────────────────
    st.markdown(f"""
    <div style='display:flex;gap:1rem;margin-bottom:1.5rem;'>
        <div style='flex:1;background:{CARD};border-radius:10px;padding:1rem;
            text-align:center;border-top:3px solid {ACCENT};'>
            <div style='font-size:1.8rem;font-weight:700;color:{ACCENT};'>{len(leads_data)}</div>
            <div style='font-size:0.7rem;color:{TEXT2};text-transform:uppercase;'>Total leads</div>
        </div>
        <div style='flex:1;background:{CARD};border-radius:10px;padding:1rem;
            text-align:center;border-top:3px solid {RED};'>
            <div style='font-size:1.8rem;font-weight:700;color:{RED};'>{len(nuevos)}</div>
            <div style='font-size:0.7rem;color:{TEXT2};text-transform:uppercase;'>🔴 Nuevos</div>
        </div>
        <div style='flex:1;background:{CARD};border-radius:10px;padding:1rem;
            text-align:center;border-top:3px solid {AMBER};'>
            <div style='font-size:1.8rem;font-weight:700;color:{AMBER};'>{len(contactados)}</div>
            <div style='font-size:0.7rem;color:{TEXT2};text-transform:uppercase;'>🟡 Contactados</div>
        </div>
        <div style='flex:1;background:{CARD};border-radius:10px;padding:1rem;
            text-align:center;border-top:3px solid {ACCENT};'>
            <div style='font-size:1.8rem;font-weight:700;color:{ACCENT};'>{len(cerrados)}</div>
            <div style='font-size:0.7rem;color:{TEXT2};text-transform:uppercase;'>✅ Cerrados</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KANBAN 3 COLUMNAS ─────────────────────────────────────────
    st.markdown(f"""
    <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;
        background:{BORDER};border-radius:12px;overflow:hidden;margin-bottom:1rem;'>
        <div style='background:{CARD};padding:0.75rem 1rem;text-align:center;
            font-weight:700;color:{RED};font-size:0.85rem;'>
            🔴 NUEVOS — {len(nuevos)}
        </div>
        <div style='background:{CARD};padding:0.75rem 1rem;text-align:center;
            font-weight:700;color:{AMBER};font-size:0.85rem;'>
            🟡 CONTACTADOS — {len(contactados)}
        </div>
        <div style='background:{CARD};padding:0.75rem 1rem;text-align:center;
            font-weight:700;color:{ACCENT};font-size:0.85rem;'>
            ✅ CERRADOS — {len(cerrados)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_n, col_c, col_x = st.columns(3)

    def _lead_mini(lead, col, accion_label, accion_estado, accion_key, color_btn,
                   accion2_label=None, accion2_estado=None, accion2_key=None):
        """Renderiza una tarjeta de lead en el kanban con su botón de acción."""
        id_real = lead.get("_id_real", lead.get("id",""))
        score   = lead.get("ia_score", 0)
        color_score = RED if score >= 75 else (AMBER if score >= 50 else TEXT2)
        with col:
            st.markdown(f"""
            <div style='background:#1A2F4A;border:1px solid {BORDER};border-radius:10px;
                padding:0.85rem;margin-bottom:0.75rem;'>
                <div style='display:flex;justify-content:space-between;align-items:center;
                    margin-bottom:0.4rem;'>
                    <span style='font-size:0.7rem;color:{TEXT2};'>{lead.get("id","")}</span>
                    <span style='font-size:0.85rem;font-weight:700;color:{color_score};'>{score}%</span>
                </div>
                <div style='font-weight:700;font-size:0.82rem;color:#fff;margin-bottom:0.3rem;'>
                    {lead.get("perfil","—")}
                </div>
                <div style='font-size:0.75rem;color:{TEXT2};margin-bottom:0.3rem;'>
                    📍 CP {lead.get("cp","—")} · 💶 {lead.get("precio_lead",45)}€
                </div>
                <div style='font-size:0.75rem;color:#ccc;margin-bottom:0.5rem;'>
                    👤 {lead.get("nombre","—")}
                </div>
                <div style='font-size:0.72rem;color:{TEXT2};'>
                    📧 {lead.get("email","—")}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(accion_label, key=accion_key, use_container_width=True):
                ok = supabase_patch(f"leads_inmobiliarias?id=eq.{id_real}", {"estado": accion_estado})
                if ok:
                    st.toast(f"✅ Lead → {accion_estado}", icon="✅")
                else:
                    st.toast("⚠️ Error al actualizar en Supabase", icon="❌")
                st.rerun()
            if accion2_label:
                if st.button(accion2_label, key=accion2_key, use_container_width=True):
                    ok = supabase_patch(f"leads_inmobiliarias?id=eq.{id_real}", {"estado": accion2_estado})
                    if ok:
                        st.toast(f"Lead → {accion2_estado}", icon="↩️")
                    st.rerun()

    # COLUMNA NUEVOS
    if not nuevos:
        with col_n:
            st.markdown(f"<div style='color:{TEXT2};font-size:0.8rem;text-align:center;"
                        f"padding:2rem;'>Sin leads nuevos</div>", unsafe_allow_html=True)
    else:
        for i, lead in enumerate(nuevos):
            _lead_mini(lead, col_n,
                       accion_label="📞 Marcar Contactado",
                       accion_estado="contactado",
                       accion_key=f"n_cont_{i}",
                       color_btn=AMBER,
                       accion2_label="⛔ Descartar",
                       accion2_estado="descartado",
                       accion2_key=f"n_desc_{i}")

    # COLUMNA CONTACTADOS
    if not contactados:
        with col_c:
            st.markdown(f"<div style='color:{TEXT2};font-size:0.8rem;text-align:center;"
                        f"padding:2rem;'>Sin leads en seguimiento</div>", unsafe_allow_html=True)
    else:
        for i, lead in enumerate(contactados):
            _lead_mini(lead, col_c,
                       accion_label="✅ Cerrar trato",
                       accion_estado="cerrado",
                       accion_key=f"c_cerr_{i}",
                       color_btn=ACCENT,
                       accion2_label="↩️ Reabrir",
                       accion2_estado="nuevo",
                       accion2_key=f"c_reab_{i}")

    # COLUMNA CERRADOS
    if not cerrados:
        with col_x:
            st.markdown(f"<div style='color:{TEXT2};font-size:0.8rem;text-align:center;"
                        f"padding:2rem;'>Sin tratos cerrados</div>", unsafe_allow_html=True)
    else:
        for i, lead in enumerate(cerrados):
            _lead_mini(lead, col_x,
                       accion_label="↩️ Reabrir",
                       accion_estado="nuevo",
                       accion_key=f"x_reab_{i}",
                       color_btn=TEXT2)

    # ── EXPORTAR CSV ──────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    if leads_data:
        df_export = pd.DataFrame([
            {k:v for k,v in l.items() if not k.startswith("_")}
            for l in leads_data
        ])
        csv = df_export.to_csv(index=False)
        st.download_button(
            "📥 Exportar todos los leads a CSV",
            data=csv,
            file_name=f"leads_inmohub_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ================================================================
# PÁGINA 4 — FIDELIZACIÓN
# ================================================================
elif menu == "Clientes":
    section_header("👤 Clientes", "Accede al patrimonio de tus clientes propietarios")

    # ── FUNCIONES AUXILIARES ─────────────────────────────────────
    def buscar_cliente_por_codigo(codigo):
        """Busca propietario por código de acceso."""
        try:
            # 1. Buscar propietario_id por código
            url = f"{SUPA_URL}/rest/v1/accesos_asesor?codigo=eq.{codigo}&activo=eq.true&select=propietario_id"
            r = requests.get(url, headers=_headers(), timeout=8)
            data = r.json()
            if not data:
                return None
            propietario_id = data[0]["propietario_id"]

            # 2. Leer inmuebles del propietario directamente
            ri = requests.get(
                f"{SUPA_URL}/rest/v1/inmuebles?user_id=eq.{propietario_id}&select=nombre,renta,renta_mercado,comunidad,cp,tipo,inquilino,valor_construccion,ibi_anual,seguro_anual,fecha_inicio_contrato,fecha_vencimiento_contrato,tipo_arrendamiento&order=id.asc",
                headers=_headers(), timeout=8
            )
            inmuebles = ri.json() if ri.status_code == 200 else []

            # 3. Leer nombre y email desde accesos_asesor directamente
            ra = requests.get(
                f"{SUPA_URL}/rest/v1/accesos_asesor?codigo=eq.{codigo}&activo=eq.true&select=email,nombre",
                headers=_headers(), timeout=8
            )
            acceso_data = ra.json() if ra.status_code == 200 else []
            if acceso_data and acceso_data[0].get("email"):
                email  = acceso_data[0]["email"]
                nombre = acceso_data[0].get("nombre") or email.split("@")[0].title()
            else:
                nombre = f"Propietario {propietario_id[:8]}"
                email  = ""

            return {
                "propietario_id": propietario_id,
                "nombre": nombre,
                "email": email,
                "inmuebles": inmuebles
            }
        except Exception as e:
            st.session_state["_debug_error"] = str(e)
            return None

    def safe_num(val, default=0.0):
        try: return float(val or default)
        except: return default

    # ── SESSION STATE ─────────────────────────────────────────────
    if "clientes_lista" not in st.session_state:
        st.session_state["clientes_lista"] = []
    if "cliente_sel" not in st.session_state:
        st.session_state["cliente_sel"] = None

    # ── AÑADIR CLIENTE ────────────────────────────────────────────
    st.markdown(f"""
    <div style='background:{CARD};border:1px solid {BORDER};border-radius:10px;padding:1rem;margin-bottom:1rem;'>
        <div style='font-weight:700;color:#fff;margin-bottom:0.5rem;'>➕ Añadir cliente por código</div>
        <div style='font-size:0.8rem;color:{TEXT2};'>Pide a tu cliente que genere un código en Nolasco Capital → Compartir con Asesor</div>
    </div>
    """, unsafe_allow_html=True)

    col_cod, col_btn = st.columns([3, 1])
    with col_cod:
        codigo_input = st.text_input("Código de 6 dígitos", placeholder="847291",
                                      max_chars=6, label_visibility="collapsed")
    with col_btn:
        if st.button("Añadir", use_container_width=True, type="primary"):
            if codigo_input and len(codigo_input) == 6:
                with st.spinner("Buscando..."):
                    cliente = buscar_cliente_por_codigo(codigo_input)
                # Mostrar debug temporal
                if "_debug_codigo" in st.session_state:
                    st.error(f"🔧 DEBUG: {st.session_state['_debug_codigo']}")
                if cliente:
                    # Comprobar si ya está en la lista
                    ids_existentes = [c["propietario_id"] for c in st.session_state["clientes_lista"]]
                    if cliente["propietario_id"] not in ids_existentes:
                        st.session_state["clientes_lista"].append(cliente)
                        st.toast(f"✅ Cliente añadido: {cliente['nombre']}", icon="✅")
                    else:
                        st.warning("Este cliente ya está en tu lista.")
                else:
                    st.error("Código no válido o expirado. Pide al cliente que genere uno nuevo.")
            else:
                st.warning("El código debe tener 6 dígitos.")

    # ── LISTA DE CLIENTES ─────────────────────────────────────────
    clientes = st.session_state["clientes_lista"]
    if not clientes:
        st.markdown(f"""
        <div style='background:{CARD};border:1px dashed {BORDER};border-radius:10px;
            padding:2rem;text-align:center;margin-top:1rem;'>
            <div style='font-size:2rem;margin-bottom:0.5rem;'>👤</div>
            <div style='color:{TEXT2};font-size:0.9rem;'>Sin clientes añadidos todavía.</div>
            <div style='color:{TEXT2};font-size:0.8rem;margin-top:4px;'>
                Introduce el código que te facilite tu cliente para ver su patrimonio.
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        for i, cliente in enumerate(clientes):
            n_inmuebles = len(cliente.get("inmuebles", []))
            ingresos = sum(safe_num(inm.get("renta")) * 12 for inm in cliente.get("inmuebles", []))
            col_cl, col_btn2 = st.columns([4, 1])
            with col_cl:
                if st.button(
                    f"👤 **{cliente['nombre']}** — {cliente['email']} · {n_inmuebles} inmuebles · {ingresos:,.0f} €/año",
                    key=f"cl_{i}", use_container_width=True
                ):
                    st.session_state["cliente_sel"] = i
                    st.rerun()
            with col_btn2:
                if st.button("✕", key=f"rm_{i}", use_container_width=True):
                    st.session_state["clientes_lista"].pop(i)
                    if st.session_state["cliente_sel"] == i:
                        st.session_state["cliente_sel"] = None
                    st.rerun()

    # ── FICHA DEL CLIENTE SELECCIONADO ───────────────────────────
    if st.session_state["cliente_sel"] is not None:
        idx = st.session_state["cliente_sel"]
        if idx < len(clientes):
            cliente = clientes[idx]
            inmuebles = cliente.get("inmuebles", [])

            st.markdown("---")
            # Nombre cliente destacado
            st.markdown(f"""
            <div style='background:{CARD};border-left:4px solid {ACCENT};border-radius:8px;
                padding:1rem 1.5rem;margin-bottom:1.5rem;'>
                <div style='font-size:1.3rem;font-weight:700;color:#fff;'>
                    👤 {cliente['nombre']}
                </div>
                <div style='font-size:0.8rem;color:{TEXT2};'>{cliente['email']} · {len(inmuebles)} inmuebles</div>
            </div>
            """, unsafe_allow_html=True)

            # ── TORRE DE CONTROL (solo lectura) ──────────────────
            st.markdown(f"<div style='font-weight:700;font-size:1rem;color:#fff;margin-bottom:0.75rem;'>📊 Torre de Control</div>", unsafe_allow_html=True)

            ingresos_tot = sum(safe_num(i.get("renta")) * 12 for i in inmuebles)
            gastos_tot   = sum(safe_num(i.get("comunidad")) * 12 + safe_num(i.get("ibi_anual")) +
                               safe_num(i.get("seguro_anual")) for i in inmuebles)
            beneficio    = ingresos_tot - gastos_tot
            rent_media   = (beneficio / ingresos_tot * 100) if ingresos_tot > 0 else 0

            kc1, kc2, kc3, kc4 = st.columns(4)
            def kpi_card(col, label, valor, color):
                col.markdown(f"""
                <div style='background:{CARD};border:1px solid {BORDER};border-radius:10px;
                    padding:1rem;text-align:center;border-top:3px solid {color};'>
                    <div style='font-size:1.5rem;font-weight:700;color:{color};'>{valor}</div>
                    <div style='font-size:0.7rem;color:{TEXT2};text-transform:uppercase;'>{label}</div>
                </div>""", unsafe_allow_html=True)

            kpi_card(kc1, "Ingresos anuales",  f"{ingresos_tot:,.0f} €", ACCENT)
            kpi_card(kc2, "Gastos anuales",     f"{gastos_tot:,.0f} €",   RED)
            kpi_card(kc3, "Beneficio neto",     f"{beneficio:,.0f} €",    AMBER)
            kpi_card(kc4, "Rentabilidad media", f"{rent_media:.1f}%",     ACCENT)

            # ── PANEL DE ALERTAS ──────────────────────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-weight:700;font-size:1rem;color:#fff;margin-bottom:0.75rem;'>🚨 Alertas Activas</div>", unsafe_allow_html=True)

            from datetime import datetime as _dt, date as _date
            alertas = []
            for inm in inmuebles:
                nombre_inm = inm.get("nombre", "—")
                renta_act  = safe_num(inm.get("renta"))
                renta_mkt  = safe_num(inm.get("renta_mercado"))
                brecha_mes = renta_mkt - renta_act

                # Alerta vencimiento contrato
                fecha_venc_raw = inm.get("fecha_vencimiento_contrato")
                if fecha_venc_raw and str(fecha_venc_raw) not in ["None","nan",""]:
                    try:
                        fecha_venc = _dt.strptime(str(fecha_venc_raw)[:10], "%Y-%m-%d").date()
                        dias_restantes = (fecha_venc - _date.today()).days
                        if dias_restantes < 0:
                            alertas.append({"tipo": "🔴 URGENTE", "color": RED,
                                "texto": f"{nombre_inm}: Contrato VENCIDO hace {abs(dias_restantes)} días",
                                "accion": "Contactar propietario para renovación inmediata"})
                        elif dias_restantes <= 30:
                            alertas.append({"tipo": "🔴 CRÍTICO", "color": RED,
                                "texto": f"{nombre_inm}: Contrato vence en {dias_restantes} días ({fecha_venc.strftime('%d/%m/%Y')})",
                                "accion": "Ventana de acción inmediata — contactar ahora"})
                        elif dias_restantes <= 60:
                            alertas.append({"tipo": "🟡 ATENCIÓN", "color": AMBER,
                                "texto": f"{nombre_inm}: Contrato vence en {dias_restantes} días ({fecha_venc.strftime('%d/%m/%Y')})",
                                "accion": "Iniciar conversación sobre renovación"})
                        elif dias_restantes <= 90:
                            alertas.append({"tipo": "🟡 SEGUIMIENTO", "color": AMBER,
                                "texto": f"{nombre_inm}: Contrato vence en {dias_restantes} días ({fecha_venc.strftime('%d/%m/%Y')})",
                                "accion": "Planificar contacto próximo"})
                    except:
                        pass

                # Alerta rentabilidad baja
                if brecha_mes > 150:
                    alertas.append({"tipo": "🔴 PÉRDIDA ALTA", "color": RED,
                        "texto": f"{nombre_inm}: Renta {renta_act:,.0f}€ vs mercado {renta_mkt:,.0f}€ → pierde {brecha_mes*12:,.0f}€/año",
                        "accion": "Proponer actualización de renta al vencimiento"})
                elif brecha_mes > 50:
                    alertas.append({"tipo": "🟡 PÉRDIDA MEDIA", "color": AMBER,
                        "texto": f"{nombre_inm}: Renta por debajo de mercado → pierde {brecha_mes*12:,.0f}€/año",
                        "accion": "Evaluar actualización IPC/IRAV"})

                # Alerta sin inquilino
                if not inm.get("inquilino") or str(inm.get("inquilino","")).strip() in ["","—","None"]:
                    alertas.append({"tipo": "🔴 VACÍO", "color": RED,
                        "texto": f"{nombre_inm}: Sin inquilino registrado",
                        "accion": "Oportunidad de captación para alquiler"})

            if alertas:
                for alerta in alertas:
                    st.markdown(f"""
                    <div style='background:{CARD};border-left:4px solid {alerta["color"]};
                        border-radius:8px;padding:0.75rem 1rem;margin-bottom:0.5rem;'>
                        <div style='display:flex;justify-content:space-between;align-items:center;'>
                            <div>
                                <span style='font-size:0.75rem;font-weight:700;color:{alerta["color"]};'>
                                    {alerta["tipo"]}
                                </span>
                                <div style='font-size:0.85rem;color:#fff;margin-top:2px;'>
                                    {alerta["texto"]}
                                </div>
                                <div style='font-size:0.75rem;color:{TEXT2};margin-top:2px;'>
                                    💡 {alerta["accion"]}
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background:{CARD};border:1px solid {BORDER};border-radius:8px;
                    padding:1rem;text-align:center;color:{TEXT2};font-size:0.85rem;'>
                    ✅ Sin alertas activas — patrimonio en buen estado
                </div>
                """, unsafe_allow_html=True)

            # ── ESTADO DE CONTRATOS ───────────────────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-weight:700;font-size:1rem;color:#fff;margin-bottom:0.75rem;'>📅 Estado de Contratos</div>", unsafe_allow_html=True)

            # Header tabla
            st.markdown(f"""
            <div style='display:grid;grid-template-columns:2fr 1.5fr 1.5fr 1fr;
                gap:0.5rem;padding:0.4rem 1rem;margin-bottom:0.2rem;'>
                <div style='font-size:0.7rem;color:{TEXT2};text-transform:uppercase;'>Inmueble</div>
                <div style='font-size:0.7rem;color:{TEXT2};text-transform:uppercase;'>Inquilino</div>
                <div style='font-size:0.7rem;color:{TEXT2};text-transform:uppercase;'>Tipo</div>
                <div style='font-size:0.7rem;color:{TEXT2};text-transform:uppercase;'>Vencimiento</div>
            </div>
            """, unsafe_allow_html=True)
            # Renderizar cada contrato individualmente
            for inm in inmuebles:
                nombre_inm = inm.get("nombre","—")
                fecha_venc_raw = inm.get("fecha_vencimiento_contrato")
                tipo_arr = inm.get("tipo_arrendamiento", "—")
                inquilino = inm.get("inquilino","Sin inquilino")
                dias_txt = "—"
                color_dias = TEXT2
                semaforo = "⚪"
                try:
                    if fecha_venc_raw and str(fecha_venc_raw) not in ["None","nan",""]:
                        fecha_venc = _dt.strptime(str(fecha_venc_raw)[:10], "%Y-%m-%d").date()
                        dias = (fecha_venc - _date.today()).days
                        if dias < 0:
                            dias_txt = f"Vencido hace {abs(dias)}d"
                            color_dias = RED; semaforo = "🔴"
                        elif dias <= 30:
                            dias_txt = f"{dias} días"
                            color_dias = RED; semaforo = "🔴"
                        elif dias <= 90:
                            dias_txt = f"{dias} días"
                            color_dias = AMBER; semaforo = "🟡"
                        else:
                            dias_txt = f"{dias} días"
                            color_dias = ACCENT; semaforo = "🟢"
                except:
                    dias_txt = "Sin fecha"
                st.markdown(f"""
                <div style='display:grid;grid-template-columns:2fr 1.5fr 1.5fr 1fr;
                    gap:0.5rem;background:{CARD};border:1px solid {BORDER};
                    border-radius:8px;padding:0.75rem 1rem;margin-bottom:0.4rem;
                    align-items:center;'>
                    <div style='font-weight:700;color:#fff;font-size:0.85rem;'>{semaforo} {nombre_inm}</div>
                    <div style='font-size:0.8rem;color:{TEXT2};'>{inquilino}</div>
                    <div style='font-size:0.8rem;color:{TEXT2};'>{tipo_arr}</div>
                    <div style='font-weight:700;color:{color_dias};font-size:0.8rem;'>{dias_txt}</div>
                </div>
                """, unsafe_allow_html=True)

            # ── FICHAS INMUEBLES (solo lectura) ──────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-weight:700;font-size:1rem;color:#fff;margin-bottom:0.75rem;'>🏠 Fichas de Rentabilidad</div>", unsafe_allow_html=True)

            for inm in inmuebles:
                renta_actual = safe_num(inm.get("renta"))
                renta_mercado = safe_num(inm.get("renta_mercado"))
                brecha = renta_mercado - renta_actual
                brecha_anual = brecha * 12
                color_brecha = RED if brecha > 100 else (AMBER if brecha > 50 else ACCENT)
                rent_bruta = (renta_actual * 12 / safe_num(inm.get("valor_construccion"), 1) * 100) if safe_num(inm.get("valor_construccion")) > 0 else 0

                st.markdown(f"""
                <div style='background:{CARD};border:1px solid {BORDER};border-radius:10px;
                    padding:1rem;margin-bottom:0.75rem;'>
                    <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;'>
                        <div style='font-weight:700;font-size:0.95rem;color:#fff;'>
                            🏠 {inm.get("nombre","—")}
                        </div>
                        <div style='font-size:0.8rem;color:{TEXT2};'>CP {inm.get("cp","—")} · {inm.get("tipo","—")}</div>
                    </div>
                    <div style='display:flex;gap:2rem;flex-wrap:wrap;'>
                        <div>
                            <div style='font-size:0.7rem;color:{TEXT2};'>Renta actual</div>
                            <div style='font-weight:700;color:{ACCENT};'>{renta_actual:,.0f} €/mes</div>
                        </div>
                        <div>
                            <div style='font-size:0.7rem;color:{TEXT2};'>Renta mercado</div>
                            <div style='font-weight:700;color:#fff;'>{renta_mercado:,.0f} €/mes</div>
                        </div>
                        <div>
                            <div style='font-size:0.7rem;color:{TEXT2};'>Lucro cesante</div>
                            <div style='font-weight:700;color:{color_brecha};'>{brecha_anual:+,.0f} €/año</div>
                        </div>
                        <div>
                            <div style='font-size:0.7rem;color:{TEXT2};'>Rentabilidad bruta</div>
                            <div style='font-weight:700;color:{ACCENT};'>{rent_bruta:.1f}%</div>
                        </div>
                        <div>
                            <div style='font-size:0.7rem;color:{TEXT2};'>Inquilino</div>
                            <div style='font-weight:700;color:#fff;'>{inm.get("inquilino","—")}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style='font-size:0.75rem;color:{TEXT2};margin-top:1rem;text-align:center;'>
            🔒 Vista de solo lectura · El cliente puede revocar este acceso desde Nolasco Capital
            </div>
            """, unsafe_allow_html=True)

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
