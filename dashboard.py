"""Premium Streamlit demo dashboard for the agentic-client-guardian MVP."""

from __future__ import annotations

import html
import os
from datetime import datetime
from typing import Any

import httpx
import streamlit as st

DEFAULT_API_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


st.set_page_config(
    page_title="Guardian | Agentic Client Guardian",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles() -> None:
    """Apply the editorial fintech visual system inspired by the Stitch export."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');

        :root {
            --background: #f6f8fc;
            --surface-low: rgba(242, 246, 251, 0.82);
            --surface: rgba(255, 255, 255, 0.84);
            --surface-high: rgba(234, 238, 244, 0.88);
            --surface-strong: rgba(227, 232, 239, 0.95);
            --ink: #151a22;
            --muted: #4b5565;
            --outline: rgba(194, 198, 217, 0.32);
            --primary: #004bca;
            --primary-soft: #0061ff;
            --tertiary: #6b21dc;
            --error: #ba1a1a;
            --warning: #b45309;
            --success: #047857;
            --shadow: 0 26px 80px rgba(0, 45, 120, 0.08);
            --blur-blue: rgba(0, 97, 255, 0.16);
            --blur-blue-soft: rgba(0, 75, 202, 0.08);
        }

        html, body, [class*="css"] {
            font-family: "Inter", sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 88% 12%, rgba(0, 97, 255, 0.16), transparent 18%),
                radial-gradient(circle at 78% 32%, rgba(0, 75, 202, 0.10), transparent 22%),
                radial-gradient(circle at 12% 92%, rgba(107, 33, 220, 0.06), transparent 16%),
                var(--background);
            color: var(--ink);
        }

        .stApp::before,
        .stApp::after {
            content: "";
            position: fixed;
            inset: auto;
            pointer-events: none;
            z-index: 0;
            filter: blur(72px);
            border-radius: 999px;
        }

        .stApp::before {
            width: 22rem;
            height: 22rem;
            top: 5rem;
            right: 10rem;
            background: radial-gradient(circle, var(--blur-blue), transparent 68%);
        }

        .stApp::after {
            width: 16rem;
            height: 16rem;
            bottom: 5rem;
            left: 24rem;
            background: radial-gradient(circle, rgba(0, 75, 202, 0.10), transparent 70%);
        }

        #MainMenu, footer, header[data-testid="stHeader"] {
            visibility: hidden;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(244, 247, 251, 0.92) 0%, rgba(239, 243, 248, 0.92) 100%);
            border-right: none;
            backdrop-filter: blur(24px);
            box-shadow: 32px 0 64px rgba(25, 28, 29, 0.05);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.25rem;
        }

        [data-testid="stSidebar"] .stTextInput input,
        [data-testid="stSidebar"] div[data-baseweb="select"] > div,
        [data-testid="stSidebar"] .stButton button {
            border-radius: 1rem;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1440px;
            position: relative;
            z-index: 1;
        }

        .brand-lockup {
            margin-bottom: 1.1rem;
        }

        .brand-name {
            font-size: 2rem;
            font-weight: 900;
            letter-spacing: -0.04em;
            line-height: 0.95;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-soft) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .brand-tagline {
            color: var(--muted);
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.24em;
            text-transform: uppercase;
            margin-top: 0.28rem;
        }

        .nav-shell {
            display: grid;
            gap: 0.65rem;
            margin: 1.4rem 0 2rem;
        }

        .nav-item,
        .nav-item-active {
            display: block;
            padding: 0.92rem 1rem;
            border-radius: 1rem;
            font-size: 0.96rem;
            font-weight: 650;
            letter-spacing: -0.01em;
        }

        .nav-item {
            color: var(--muted);
            background: transparent;
        }

        .nav-item-active {
            color: var(--primary);
            background: rgba(255, 255, 255, 0.96);
            box-shadow: 0 10px 26px rgba(25, 28, 29, 0.05);
        }

        .sidebar-section-label,
        .eyebrow {
            color: var(--muted);
            font-size: 0.68rem;
            font-weight: 850;
            letter-spacing: 0.18em;
            text-transform: uppercase;
        }

        .status-chip,
        .inline-chip,
        .signal-chip,
        .priority-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            border-radius: 999px;
            padding: 0.46rem 0.85rem;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: -0.01em;
        }

        .status-chip {
            background: linear-gradient(135deg, rgba(0, 75, 202, 0.12) 0%, rgba(0, 97, 255, 0.08) 100%);
            color: var(--primary);
            border: 1px solid rgba(0, 75, 202, 0.10);
        }

        .status-chip.offline {
            background: rgba(186, 26, 26, 0.08);
            color: var(--error);
        }

        .dot,
        .mini-dot {
            width: 0.5rem;
            height: 0.5rem;
            border-radius: 50%;
            background: currentColor;
            display: inline-block;
        }

        .topbar {
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.70) 0%, rgba(247, 249, 252, 0.84) 100%);
            backdrop-filter: blur(28px);
            border: 1px solid rgba(255, 255, 255, 0.52);
            border-radius: 1.75rem;
            padding: 1.1rem 1.25rem 0.9rem;
            box-shadow: 0 18px 50px rgba(0, 55, 145, 0.06);
            margin-bottom: 1.35rem;
        }

        .topbar-title {
            font-size: 1.08rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            color: var(--ink);
        }

        .hero {
            display: grid;
            gap: 0.35rem;
            margin-bottom: 1.5rem;
        }

        .hero-title {
            font-size: 3.25rem;
            font-weight: 900;
            letter-spacing: -0.05em;
            line-height: 0.9;
            color: var(--ink);
        }

        .hero-copy {
            color: var(--muted);
            font-size: 1.06rem;
            line-height: 1.72;
            max-width: 58rem;
        }

        .panel,
        .priority-row,
        .analysis-card,
        .message-shell,
        .glass-card {
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.88) 0%, rgba(250, 252, 255, 0.78) 100%);
            border: 1px solid var(--outline);
            border-radius: 1.8rem;
            backdrop-filter: blur(22px);
            box-shadow: var(--shadow);
        }

        .panel,
        .analysis-card,
        .message-shell,
        .glass-card {
            padding: 1.35rem 1.45rem;
        }

        .metric-panel {
            min-height: 9.25rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            border-radius: 2rem;
            padding: 1.5rem;
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.92) 0%, rgba(247, 250, 253, 0.84) 100%);
            backdrop-filter: blur(18px);
            border: 1px solid rgba(255, 255, 255, 0.58);
            box-shadow: 0 24px 56px rgba(25, 28, 29, 0.05);
        }

        .metric-panel.alert {
            border-left: 4px solid rgba(186, 26, 26, 0.16);
        }

        .metric-panel.tertiary {
            background:
                radial-gradient(circle at top right, rgba(255,255,255,0.18), transparent 24%),
                linear-gradient(135deg, var(--tertiary) 0%, #8545f6 100%);
            color: white;
        }

        .metric-label {
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-weight: 800;
            color: var(--muted);
        }

        .metric-panel.tertiary .metric-label {
            color: rgba(255, 255, 255, 0.78);
        }

        .metric-value {
            font-size: 3rem;
            line-height: 0.95;
            letter-spacing: -0.06em;
            font-weight: 900;
        }

        .metric-subcopy {
            color: var(--muted);
            font-size: 0.97rem;
            line-height: 1.55;
        }

        .metric-panel.tertiary .metric-subcopy {
            color: rgba(255, 255, 255, 0.85);
        }

        .priority-row {
            padding: 1.2rem 1.35rem;
            margin-bottom: 0.95rem;
            min-height: 100%;
        }

        .priority-row.selected {
            border-color: rgba(0, 75, 202, 0.28);
            box-shadow: 0 26px 58px rgba(0, 75, 202, 0.12);
        }

        .avatar-badge {
            width: 3rem;
            height: 3rem;
            border-radius: 1rem;
            background: rgba(0, 75, 202, 0.08);
            color: var(--primary);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            letter-spacing: -0.02em;
        }

        .priority-name {
            font-size: 1.05rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            color: var(--ink);
        }

        .priority-observation {
            color: #343d49;
            font-size: 0.96rem;
            line-height: 1.65;
        }

        .priority-label {
            color: #5a6574;
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.18em;
            font-weight: 850;
        }

        .priority-score {
            font-size: 2rem;
            font-weight: 900;
            letter-spacing: -0.05em;
            line-height: 0.95;
        }

        .priority-chip.urgent {
            background: rgba(186, 26, 26, 0.08);
            color: var(--error);
        }

        .priority-chip.high {
            background: rgba(180, 83, 9, 0.10);
            color: var(--warning);
        }

        .priority-chip.medium {
            background: rgba(0, 75, 202, 0.08);
            color: var(--primary);
        }

        .priority-chip.low {
            background: rgba(4, 120, 87, 0.08);
            color: var(--success);
        }

        .client-header {
            display: grid;
            gap: 0.35rem;
        }

        .client-name {
            font-size: 3.1rem;
            line-height: 0.92;
            font-weight: 900;
            letter-spacing: -0.05em;
        }

        .client-meta {
            color: #46515f;
            font-size: 0.98rem;
            line-height: 1.6;
        }

        .gauge-shell {
            text-align: center;
            padding-top: 0.5rem;
        }

        .gauge-ring {
            width: 11rem;
            height: 11rem;
            margin: 0 auto 1rem;
            border-radius: 50%;
            background:
                radial-gradient(closest-side, white 68%, transparent 70% 100%),
                conic-gradient(var(--gauge-color) calc(var(--gauge-value) * 1%), rgba(231, 232, 233, 0.95) 0);
            display: grid;
            place-items: center;
            box-shadow: inset 0 0 0 1px rgba(194, 198, 217, 0.18);
        }

        .gauge-value {
            font-size: 2rem;
            font-weight: 900;
            letter-spacing: -0.05em;
            color: var(--gauge-color);
        }

        .message-block {
            background:
                radial-gradient(circle at top right, rgba(0, 97, 255, 0.10), transparent 26%),
                linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(243, 247, 252, 0.88) 100%);
            border-radius: 1.5rem;
            padding: 1.35rem 1.4rem;
            color: var(--ink);
            font-size: 1.14rem;
            line-height: 1.92;
            letter-spacing: -0.02em;
            min-height: 13rem;
            border: 1px solid rgba(255, 255, 255, 0.65);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
        }

        .mini-card {
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.90) 0%, rgba(248, 250, 253, 0.82) 100%);
            border: 1px solid var(--outline);
            border-radius: 1.2rem;
            padding: 1rem 1.05rem;
            backdrop-filter: blur(12px);
        }

        .list-stack {
            display: grid;
            gap: 0.85rem;
        }

        .muted-copy {
            color: #46515f;
            line-height: 1.72;
        }

        .spotlight-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 1rem;
            margin-top: 1.25rem;
        }

        .spotlight-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.88) 0%, rgba(244,247,252,0.78) 100%);
            border: 1px solid var(--outline);
            border-radius: 1.4rem;
            padding: 1rem 1.05rem;
            box-shadow: 0 18px 38px rgba(0, 75, 202, 0.05);
            backdrop-filter: blur(18px);
        }

        .spotlight-value {
            color: var(--ink);
            font-size: 1.15rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            margin-top: 0.3rem;
            line-height: 1.35;
        }

        .spotlight-copy {
            color: var(--muted);
            font-size: 0.86rem;
            line-height: 1.55;
            margin-top: 0.25rem;
        }

        .empty-shell {
            padding: 2rem;
            border-radius: 1.8rem;
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.78) 0%, rgba(242, 246, 251, 0.74) 100%);
            border: 1px dashed rgba(194, 198, 217, 0.48);
            color: var(--muted);
            backdrop-filter: blur(18px);
        }

        .stTextInput input {
            background: linear-gradient(180deg, rgba(235, 239, 245, 0.92) 0%, rgba(228, 233, 240, 0.92) 100%);
            border: none;
            color: var(--ink);
            border-radius: 999px;
            padding-left: 1rem;
            min-height: 3rem;
            font-size: 0.97rem;
        }

        .stTextInput input:focus {
            box-shadow: 0 0 0 1px rgba(0, 75, 202, 0.28), 0 0 0 6px rgba(0, 75, 202, 0.08);
        }

        .stButton button {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-soft) 100%);
            color: white;
            border: none;
            border-radius: 1rem;
            font-weight: 800;
            letter-spacing: -0.01em;
            padding: 0.78rem 1rem;
            min-height: 3rem;
            box-shadow: 0 18px 32px rgba(0, 75, 202, 0.20);
        }

        .stButton button:hover {
            filter: brightness(1.02);
        }

        .stButton button[kind="secondary"] {
            background: white;
            color: var(--ink);
            box-shadow: 0 10px 20px rgba(25, 28, 29, 0.06);
        }

        div[data-baseweb="select"] > div,
        .stRadio > div {
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid var(--outline);
        }

        .stRadio > div {
            border-radius: 999px;
            padding: 0.28rem;
        }

        .stRadio label {
            border-radius: 999px;
            padding: 0.18rem 0.7rem;
        }

        .stAlert {
            border-radius: 1rem;
            border: 1px solid var(--outline);
        }

        @media (max-width: 1200px) {
            .spotlight-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        @media (max-width: 720px) {
            .hero-title {
                font-size: 2.5rem;
            }

            .client-name {
                font-size: 2.35rem;
            }

            .spotlight-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def api_request(
    path: str,
    *,
    method: str,
    base_url: str,
    payload: dict[str, Any] | None = None,
) -> Any:
    """Call the API and return JSON with consistent error handling."""
    url = f"{base_url.rstrip('/')}{path}"

    try:
        with httpx.Client(timeout=25.0) as client:
            response = client.request(method, url, json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError as exc:
        raise RuntimeError(
            "Nao foi possivel conectar na API. Inicie o FastAPI com "
            "`uvicorn app.main:app --reload`."
        ) from exc
    except httpx.HTTPStatusError as exc:
        detail = extract_error(exc.response)
        raise RuntimeError(detail) from exc
    except httpx.HTTPError as exc:
        raise RuntimeError("Falha de comunicacao com a API configurada.") from exc
    except ValueError as exc:
        raise RuntimeError("A API retornou uma resposta invalida.") from exc


def extract_error(response: httpx.Response) -> str:
    """Extract a human-friendly error string from the API response."""
    try:
        data = response.json()
    except ValueError:
        return "Erro inesperado ao consultar a API."

    if isinstance(data, dict):
        detail = data.get("detail")
        if isinstance(detail, str) and detail.strip():
            return detail

    return "Erro inesperado ao consultar a API."


@st.cache_data(show_spinner=False, ttl=30)
def get_health(base_url: str) -> dict[str, Any]:
    """Fetch the API health payload."""
    data = api_request("/health", method="GET", base_url=base_url)
    return data if isinstance(data, dict) else {}


@st.cache_data(show_spinner=False, ttl=30)
def get_clients(base_url: str) -> list[dict[str, Any]]:
    """Fetch the fake clients list."""
    data = api_request("/clients", method="GET", base_url=base_url)
    return data if isinstance(data, list) else []


@st.cache_data(show_spinner=False, ttl=30)
def get_daily_priorities(base_url: str) -> list[dict[str, Any]]:
    """Fetch the daily priorities queue."""
    data = api_request("/daily-priorities", method="GET", base_url=base_url)
    return data if isinstance(data, list) else []


@st.cache_data(show_spinner=False, ttl=30)
def get_interactions(client_id: str, base_url: str) -> list[dict[str, Any]]:
    """Fetch recent interactions for one client."""
    data = api_request(
        f"/clients/{client_id}/interactions",
        method="GET",
        base_url=base_url,
    )
    return data if isinstance(data, list) else []


def get_analysis(client_id: str, *, base_url: str) -> dict[str, Any]:
    """Execute the full analysis for one client."""
    data = api_request(
        f"/clients/{client_id}/analyze",
        method="POST",
        base_url=base_url,
        payload={},
    )
    return data if isinstance(data, dict) else {}


def clear_api_caches() -> None:
    """Reset all cached API reads."""
    get_health.clear()
    get_clients.clear()
    get_daily_priorities.clear()
    get_interactions.clear()


def format_currency(value: float | int | None) -> str:
    """Format numbers to a BRL-style compact value."""
    amount = float(value or 0)
    text = f"{amount:,.2f}"
    return "R$ " + text.replace(",", "X").replace(".", ",").replace("X", ".")


def format_timestamp(value: str | None) -> str:
    """Convert ISO timestamps to a shorter readable format."""
    if not value:
        return "-"

    normalized = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError:
        return value

    return dt.strftime("%d %b %Y, %H:%M")


def initials(name: str) -> str:
    """Build a compact avatar label from a client name."""
    parts = [part for part in name.strip().split() if part]
    if not parts:
        return "GC"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def score_color(score: int) -> str:
    """Pick an accent color according to score severity."""
    if score >= 75:
        return "#ba1a1a"
    if score >= 50:
        return "#b45309"
    if score >= 25:
        return "#004bca"
    return "#047857"


def priority_class(level: str | None) -> str:
    """Map priority labels to CSS classes."""
    normalized = (level or "low").strip().lower()
    if normalized in {"urgent", "high", "medium", "low"}:
        return normalized
    return "low"


def escape(value: Any) -> str:
    """Escape arbitrary values for HTML rendering."""
    return html.escape(str(value if value is not None else "-"))


def find_client(clients: list[dict[str, Any]], client_id: str) -> dict[str, Any] | None:
    """Find one client in a list of dictionaries."""
    for client in clients:
        if client.get("id") == client_id:
            return client
    return None


def ensure_session_state(clients: list[dict[str, Any]]) -> None:
    """Initialize the dashboard state safely."""
    if "selected_client_id" not in st.session_state:
        st.session_state["selected_client_id"] = clients[0]["id"] if clients else None

    if "analysis_result" not in st.session_state:
        st.session_state["analysis_result"] = None

    if "search_query" not in st.session_state:
        st.session_state["search_query"] = ""


def render_sidebar(
    *,
    base_url: str,
    clients: list[dict[str, Any]],
    health: dict[str, Any] | None,
) -> tuple[str, bool, bool]:
    """Render the left navigation rail and controls."""
    with st.sidebar:
        st.markdown(
            """
            <div class="brand-lockup">
                <div class="brand-name">Guardian</div>
                <div class="brand-tagline">AI Fintech Engine</div>
            </div>
            <div class="nav-shell">
                <span class="nav-item-active">Dashboard</span>
                <span class="nav-item">Clients</span>
                <span class="nav-item">Insights</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        status_ok = (health or {}).get("status") == "ok"
        status_class = "status-chip" if status_ok else "status-chip offline"
        status_text = "API online" if status_ok else "API indisponivel"
        st.markdown(
            f"""
            <div class="{status_class}">
                <span class="dot"></span>
                <span>{escape(status_text)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='sidebar-section-label'>Workspace Controls</div>",
            unsafe_allow_html=True,
        )

        api_url = st.text_input(
            "API Base URL",
            value=base_url,
            help="Altere apenas se a API FastAPI estiver em outro host.",
        )

        client_options = {client["id"]: client for client in clients}
        selected_client_id = st.selectbox(
            "Client Focus",
            options=list(client_options),
            format_func=lambda item: f"{client_options[item]['name']} ({item})",
            index=max(
                0,
                list(client_options).index(st.session_state["selected_client_id"])
                if st.session_state["selected_client_id"] in client_options
                else 0,
            ),
        )
        st.session_state["selected_client_id"] = selected_client_id

        refresh_requested = st.button("Refresh Feed", use_container_width=True)
        run_analysis = st.button("Run Full Analysis", use_container_width=True)
        clear_selection = st.button("New Analysis", use_container_width=True, type="secondary")

        if clear_selection:
            st.session_state["analysis_result"] = None

        st.markdown("<div style='height: 1.1rem'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="panel">
                <div class="sidebar-section-label">Demo Notes</div>
                <div style="height: 0.65rem"></div>
                <div class="muted-copy">
                    Dados simulados, motor de scoring explicavel e fallback local quando o Gemini
                    nao estiver disponivel.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return api_url, refresh_requested, run_analysis


def render_topbar(health: dict[str, Any] | None) -> str:
    """Render the shared application top bar."""
    left_col, right_col = st.columns([2.7, 1.1], gap="large")

    with left_col:
        st.markdown(
            """
            <div class="topbar">
                <div class="topbar-title">Agentic Client Guardian</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        status = "Connected" if (health or {}).get("status") == "ok" else "Offline"
        st.markdown(
            f"""
            <div class="topbar">
                <div class="sidebar-section-label">Environment</div>
                <div style="height:0.35rem"></div>
                <div class="topbar-title">{escape(status)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    search_query = st.text_input(
        "Search clients or priorities",
        value=st.session_state.get("search_query", ""),
        placeholder="Search clients by name, segment, action or reason...",
        label_visibility="collapsed",
    )
    st.session_state["search_query"] = search_query
    return search_query


def render_hero() -> None:
    """Render the main page heading."""
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">Daily Priorities</div>
            <div class="hero-copy">
                Focus on the highest-impact interventions curated for the advisor. The interface
                combines operational urgency, client context and message preparation in one premium
                demo flow.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(
    clients: list[dict[str, Any]],
    priorities: list[dict[str, Any]],
) -> None:
    """Render the three top-level KPI cards."""
    total_clients = len(clients)
    high_risk = sum(
        1 for item in priorities if str(item.get("churn_level", "")).lower() == "high"
    )
    actions_today = sum(
        1
        for item in priorities
        if str(item.get("priority_level", "")).lower() in {"urgent", "high"}
    )

    metric_cols = st.columns(3, gap="large")
    with metric_cols[0]:
        st.markdown(
            f"""
            <div class="metric-panel">
                <div class="metric-label">Total Clients</div>
                <div class="metric-value">{total_clients}</div>
                <div class="metric-subcopy">Simulated accounts available in the MVP.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with metric_cols[1]:
        st.markdown(
            f"""
            <div class="metric-panel alert">
                <div class="metric-label">High-Risk Clients</div>
                <div class="metric-value" style="color: var(--error);">{high_risk}</div>
                <div class="metric-subcopy">Accounts with elevated churn exposure.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with metric_cols[2]:
        st.markdown(
            f"""
            <div class="metric-panel tertiary">
                <div class="metric-label">Actions Needed Today</div>
                <div class="metric-value">{actions_today}</div>
                <div class="metric-subcopy">High-priority interventions ready for action.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def filter_priorities(
    priorities: list[dict[str, Any]],
    clients: list[dict[str, Any]],
    *,
    search_query: str,
    selected_filter: str,
) -> list[dict[str, Any]]:
    """Apply dashboard search and severity filters."""
    selected_lookup = {item["id"]: item for item in clients}
    query = search_query.strip().lower()

    filtered = []
    for item in priorities:
        client = selected_lookup.get(item.get("client_id"))
        if client is None:
            continue

        priority_level = str(item.get("priority_level", "")).lower()
        if selected_filter != "All" and priority_level != selected_filter.lower():
            continue

        haystack = " ".join(
            [
                str(client.get("name", "")),
                str(client.get("segment", "")),
                str(item.get("main_reason", "")),
                str(item.get("suggested_action", "")),
                str(item.get("suggested_channel", "")),
            ]
        ).lower()

        if query and query not in haystack:
            continue

        filtered.append(item)

    return filtered


def render_priority_list(
    priorities: list[dict[str, Any]],
    clients: list[dict[str, Any]],
    *,
    base_url: str,
) -> None:
    """Render the priority queue and allow selecting a client analysis."""
    st.markdown(
        """
        <div style="height: 0.5rem"></div>
        <div class="eyebrow">Advisor Queue</div>
        <div class="muted-copy" style="margin-top:0.4rem; margin-bottom:0.7rem;">
            Ordene a operacao do dia por urgencia, motivo principal e proximo canal de contato.
        </div>
        """,
        unsafe_allow_html=True,
    )

    filter_choice = st.radio(
        "Priority filter",
        options=["All", "Urgent", "High", "Medium", "Low"],
        horizontal=True,
        label_visibility="collapsed",
    )

    filtered = filter_priorities(
        priorities,
        clients,
        search_query=st.session_state.get("search_query", ""),
        selected_filter=filter_choice,
    )

    if not filtered:
        st.markdown(
            """
            <div class="empty-shell">
                Nenhum cliente corresponde ao filtro atual. Ajuste a busca ou reveja o corte de
                prioridade.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    for item in filtered:
        client = find_client(clients, str(item.get("client_id")))
        if client is None:
            continue

        selected = st.session_state.get("selected_client_id") == item.get("client_id")
        row_class = "priority-row selected" if selected else "priority-row"
        row_cols = st.columns([2.25, 1.05, 2.4, 1.8, 1.15], gap="medium")

        with row_cols[0]:
            st.markdown(
                f"""
                <div class="{row_class}">
                    <div style="display:flex; gap:1rem; align-items:center;">
                        <div class="avatar-badge">{escape(initials(str(client.get('name', ''))))}</div>
                        <div>
                            <div class="priority-name">{escape(client.get("name"))}</div>
                            <div style="height:0.3rem"></div>
                            <span class="priority-chip {priority_class(str(item.get("priority_level")))}">
                                {escape(str(item.get("priority_level", "low")).upper())}
                            </span>
                            <div class="spotlight-copy" style="margin-top:0.5rem;">
                                {escape(str(client.get("segment", "")).replace("_", " "))}
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with row_cols[1]:
            st.markdown(
                f"""
                <div class="{row_class}">
                    <div class="priority-label">Churn Score</div>
                    <div style="height:0.4rem"></div>
                    <div class="priority-score" style="color:{score_color(int(item.get("churn_score", 0)))};">
                        {escape(item.get("churn_score"))}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with row_cols[2]:
            st.markdown(
                f"""
                <div class="{row_class}">
                    <div class="priority-label">Observation</div>
                    <div style="height:0.35rem"></div>
                    <div class="priority-observation">{escape(item.get("main_reason"))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with row_cols[3]:
            st.markdown(
                f"""
                <div class="{row_class}">
                    <div class="priority-label">Suggested Action</div>
                    <div style="height:0.35rem"></div>
                    <div class="priority-observation">
                        <strong style="color: var(--primary);">{escape(item.get("suggested_action"))}</strong>
                        <br/>
                        via {escape(item.get("suggested_channel"))}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with row_cols[4]:
            if st.button(
                "Open Analysis",
                key=f"open-analysis-{item['client_id']}",
                use_container_width=True,
            ):
                st.session_state["selected_client_id"] = item["client_id"]
                with st.spinner("Executando analise completa..."):
                    st.session_state["analysis_result"] = get_analysis(
                        item["client_id"],
                        base_url=base_url,
                    )
                st.rerun()


def render_client_header(
    client: dict[str, Any],
    analysis: dict[str, Any] | None,
    interpretation_source: str | None,
    used_fallback: bool,
) -> None:
    """Render the selected client hero section."""
    chips = []
    chips.append(
        f'<span class="inline-chip" style="background: rgba(107, 33, 220, 0.10); color: var(--tertiary);">'
        f'{escape(str(client.get("segment", "")).replace("_", " ").upper())}'
        f"</span>"
    )
    chips.append(
        f'<span class="inline-chip" style="background: rgba(0, 75, 202, 0.08); color: var(--primary);">'
        f"{escape(client.get('risk_profile', '-'))}</span>"
    )

    if interpretation_source:
        chips.append(
            f'<span class="inline-chip" style="background: rgba(255, 255, 255, 0.9); color: var(--muted);">'
            f"{escape(interpretation_source)}</span>"
        )

    if used_fallback:
        chips.append(
            '<span class="inline-chip" style="background: rgba(186, 26, 26, 0.08); color: var(--error);">'
            "fallback active</span>"
        )

    assets = format_currency(client.get("simulated_assets"))
    last_contact_days = client.get("last_contact_days", "-")
    client_since = "Simulated portfolio"
    suggested_channel = "-"
    suggested_action = "-"
    if analysis and analysis.get("interactions"):
        client_since = f"{len(analysis['interactions'])} recent interactions"
    if analysis and analysis.get("churn_analysis"):
        suggested_channel = analysis["churn_analysis"].get("suggested_channel", "-")
        suggested_action = analysis["churn_analysis"].get("suggested_action", "-")

    st.markdown(
        f"""
        <div class="client-header">
            <div class="eyebrow">Client Deep-Dive</div>
            <div class="client-name">{escape(client.get("name"))}</div>
            <div style="display:flex; gap:0.6rem; flex-wrap:wrap; margin-top:0.15rem;">
                {"".join(chips)}
            </div>
            <div class="client-meta">
                {escape(client_since)} | Managed assets {escape(assets)} | Last contact {escape(last_contact_days)} days ago
            </div>
            <div class="spotlight-grid">
                <div class="spotlight-card">
                    <div class="priority-label">Risk Profile</div>
                    <div class="spotlight-value">{escape(client.get("risk_profile"))}</div>
                    <div class="spotlight-copy">Perfil operacional atual do cliente simulado.</div>
                </div>
                <div class="spotlight-card">
                    <div class="priority-label">Suggested Channel</div>
                    <div class="spotlight-value">{escape(suggested_channel)}</div>
                    <div class="spotlight-copy">Canal com melhor encaixe para o toque inicial.</div>
                </div>
                <div class="spotlight-card">
                    <div class="priority-label">Recommended Move</div>
                    <div class="spotlight-value">{escape(suggested_action)}</div>
                    <div class="spotlight-copy">Proximo passo sugerido pela analise consolidada.</div>
                </div>
                <div class="spotlight-card">
                    <div class="priority-label">Client Note</div>
                    <div class="spotlight-value">{escape(client.get("notes"))}</div>
                    <div class="spotlight-copy">Contexto sintetico usado como base para a leitura operacional.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_analysis_view(
    client: dict[str, Any],
    analysis_result: dict[str, Any] | None,
    interactions: list[dict[str, Any]],
) -> None:
    """Render the detailed analysis experience."""
    if analysis_result is None:
        render_client_header(client, None, None, False)
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="empty-shell">
                <div class="eyebrow">Ready To Run</div>
                <div style="height:0.65rem"></div>
                Selecione <strong>{escape(client.get("name"))}</strong> como foco e clique em
                <strong>Run Full Analysis</strong> para gerar scoring, contexto consolidado e a
                mensagem personalizada.
                <div style="height:0.8rem"></div>
                <div class="muted-copy">
                    O layout ja antecipa o contexto principal com foco em leitura: nota do cliente,
                    perfil, ultimo contato e canais recomendados aparecerao de forma condensada
                    assim que a analise for executada.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if interactions:
            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            st.markdown("<div class='eyebrow'>Latest Interactions</div>", unsafe_allow_html=True)
            for interaction in interactions[:3]:
                st.markdown(
                    f"""
                    <div class="mini-card" style="margin-top:0.75rem;">
                        <div class="priority-label">{escape(interaction.get("channel"))} | {escape(format_timestamp(interaction.get("created_at")))}</div>
                        <div style="height:0.35rem"></div>
                        <div class="muted-copy">{escape(interaction.get("content"))}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        return

    churn = analysis_result.get("churn_analysis", {})
    interpretation = analysis_result.get("context_interpretation", {})
    signals = analysis_result.get("consolidated_signals", {})
    warning = analysis_result.get("warning")
    score = int(churn.get("churn_score", 0))
    priority_score = int(churn.get("priority_score", 0))
    gauge_color = score_color(score)

    render_client_header(
        client,
        analysis_result,
        str(analysis_result.get("interpretation_source") or "-"),
        bool(analysis_result.get("used_fallback")),
    )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    analysis_cols = st.columns([1.1, 1.55, 1.15], gap="large")

    with analysis_cols[0]:
        st.markdown(
            f"""
            <div class="analysis-card">
                <div class="priority-label">Churn Risk Index</div>
                <div class="gauge-shell">
                    <div class="gauge-ring" style="--gauge-value:{score}; --gauge-color:{gauge_color};">
                        <div class="gauge-value">{score}%</div>
                    </div>
                    <span class="priority-chip {priority_class(str(churn.get("priority_level")))}">
                        {escape(churn.get("priority_level", "-"))}
                    </span>
                </div>
                <div style="height:1rem"></div>
                <div class="mini-card">
                    <div class="priority-label">Priority Score</div>
                    <div style="height:0.3rem"></div>
                    <div class="priority-score" style="color: var(--ink);">{priority_score}/100</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with analysis_cols[1]:
        st.markdown(
            f"""
            <div class="analysis-card">
                <div class="eyebrow" style="color: var(--tertiary);">Guardian AI Deep-Dive</div>
                <div style="height:0.65rem"></div>
                <div class="muted-copy" style="font-size:1.08rem; line-height:1.8;">
                    "{escape(interpretation.get("short_summary") or churn.get("main_reason"))}"
                </div>
                <div style="height:1rem"></div>
                <div class="list-stack">
                    <div class="mini-card">
                        <div class="priority-label">Main Reason</div>
                        <div style="height:0.3rem"></div>
                        <div>{escape(churn.get("main_reason"))}</div>
                    </div>
                    <div class="mini-card">
                        <div class="priority-label">Suggested Action</div>
                        <div style="height:0.3rem"></div>
                        <div><strong>{escape(churn.get("suggested_action"))}</strong> via {escape(churn.get("suggested_channel"))}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with analysis_cols[2]:
        life_event = "Detected" if interpretation.get("life_event_detected") else "Not detected"
        financial_flag = (
            "Sensitive"
            if interpretation.get("financial_insecurity_detected")
            else "Stable"
        )
        st.markdown(
            f"""
            <div class="analysis-card">
                <div class="eyebrow">Detected Risk Signals</div>
                <div style="height:0.75rem"></div>
                <div class="list-stack">
                    <div class="mini-card">
                        <div class="priority-label">Sentiment</div>
                        <div style="height:0.25rem"></div>
                        <div>{escape(interpretation.get("detected_sentiment", "-"))}</div>
                    </div>
                    <div class="mini-card">
                        <div class="priority-label">Life Event</div>
                        <div style="height:0.25rem"></div>
                        <div>{escape(life_event)}</div>
                    </div>
                    <div class="mini-card">
                        <div class="priority-label">Financial Security</div>
                        <div style="height:0.25rem"></div>
                        <div>{escape(financial_flag)}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    lower_cols = st.columns([1.0, 1.55], gap="large")

    with lower_cols[0]:
        st.markdown(
            f"""
            <div class="analysis-card">
                <div class="eyebrow">Strategic Intervention Path</div>
                <div style="height:0.8rem"></div>
                <div class="list-stack">
                    <div class="mini-card">
                        <div class="priority-label">Client Context Note</div>
                        <div style="height:0.3rem"></div>
                        <div class="muted-copy">{escape(client.get("notes"))}</div>
                    </div>
                    <div class="mini-card">
                        <div class="priority-label">Recommended Action</div>
                        <div style="height:0.3rem"></div>
                        <div><strong>{escape(churn.get("suggested_action"))}</strong></div>
                    </div>
                    <div class="mini-card">
                        <div class="priority-label">Preferred Channel</div>
                        <div style="height:0.3rem"></div>
                        <div>{escape(churn.get("suggested_channel"))}</div>
                    </div>
                    <div class="mini-card">
                        <div class="priority-label">Key Operational Signals</div>
                        <div style="height:0.4rem"></div>
                        <div class="muted-copy">
                            Days without contact: {escape(signals.get("days_without_contact"))}<br/>
                            Contribution drop: {escape(signals.get("contribution_drop_pct"))}%<br/>
                            Maturity days: {escape(signals.get("maturity_days"))}
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if interactions:
            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            st.markdown(
                """
                <div class="analysis-card">
                    <div class="eyebrow">Latest Interactions</div>
                """,
                unsafe_allow_html=True,
            )
            for interaction in interactions[:4]:
                st.markdown(
                    f"""
                    <div class="mini-card" style="margin-top:0.8rem;">
                        <div class="priority-label">
                            {escape(interaction.get("channel"))} | {escape(format_timestamp(interaction.get("created_at")))}
                        </div>
                        <div style="height:0.35rem"></div>
                        <div class="muted-copy">{escape(interaction.get("content"))}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

    with lower_cols[1]:
        st.markdown(
            f"""
            <div class="message-shell">
                <div class="eyebrow" style="color: var(--tertiary);">AI Generated Script</div>
                <div style="height:0.8rem"></div>
                <div class="muted-copy" style="margin-bottom:0.85rem;">
                    Mensagem pronta para revisao humana, com tom consultivo e sem promessas financeiras.
                </div>
                <div class="message-block">{escape(churn.get("generated_message") or "Mensagem nao disponivel.")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tip_cols = st.columns([1.15, 1.0], gap="large")
        with tip_cols[0]:
            st.markdown(
                """
                <div class="glass-card" style="background: rgba(234, 221, 255, 0.30);">
                    <div class="eyebrow" style="color: var(--tertiary);">Intelligence Tip</div>
                    <div style="height:0.5rem"></div>
                    <div class="muted-copy">
                        Use um tom consultivo e direto. Evite promessas financeiras e mantenha a
                        conversa focada no momento do cliente e no proximo passo sugerido.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with tip_cols[1]:
            st.markdown(
                f"""
                <div class="glass-card">
                    <div class="priority-label">Conversion Probability</div>
                    <div style="height:0.5rem"></div>
                    <div class="priority-score" style="color:{gauge_color};">{100 - score}%</div>
                    <div class="muted-copy">Indicador ilustrativo com base no risco calculado.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if warning:
        st.warning(str(warning))


def main() -> None:
    """Render the full premium demo dashboard."""
    inject_styles()

    base_url = st.session_state.get("api_base_url", DEFAULT_API_URL)

    try:
        health = get_health(base_url)
        clients = get_clients(base_url)
    except RuntimeError as exc:
        st.error(str(exc))
        st.info("Depois de iniciar a API, atualize a URL e recarregue a demo.")
        return

    if not clients:
        st.warning("Nenhum cliente foi retornado pela API.")
        return

    ensure_session_state(clients)
    st.session_state["api_base_url"] = base_url

    sidebar_base_url, refresh_requested, run_analysis_requested = render_sidebar(
        base_url=base_url,
        clients=clients,
        health=health,
    )

    if sidebar_base_url != base_url:
        st.session_state["api_base_url"] = sidebar_base_url
        clear_api_caches()
        st.rerun()

    if refresh_requested and sidebar_base_url == base_url:
        clear_api_caches()
        st.rerun()

    if run_analysis_requested and sidebar_base_url == base_url:
        clear_api_caches()
        if st.session_state.get("selected_client_id"):
            with st.spinner("Executando analise completa..."):
                st.session_state["analysis_result"] = get_analysis(
                    st.session_state["selected_client_id"],
                    base_url=base_url,
                )
        st.rerun()

    search_query = render_topbar(health)
    render_hero()

    try:
        priorities = get_daily_priorities(base_url)
    except RuntimeError as exc:
        st.error(str(exc))
        return

    render_metrics(clients, priorities)
    st.markdown("<div style='height:1.1rem'></div>", unsafe_allow_html=True)
    render_priority_list(priorities, clients, base_url=base_url)

    selected_client = find_client(clients, str(st.session_state.get("selected_client_id")))
    if selected_client is None:
        st.warning("Cliente selecionado nao encontrado.")
        return

    current_analysis = st.session_state.get("analysis_result")
    if current_analysis and current_analysis.get("client", {}).get("id") != selected_client.get("id"):
        current_analysis = None

    try:
        interactions = (
            current_analysis.get("interactions", [])
            if current_analysis
            else get_interactions(str(selected_client.get("id")), base_url)
        )
    except RuntimeError as exc:
        st.error(str(exc))
        return

    st.markdown("<div style='height:1.65rem'></div>", unsafe_allow_html=True)
    render_analysis_view(selected_client, current_analysis, interactions)

    if search_query:
        st.caption(f"Filtering priorities by: {search_query}")


if __name__ == "__main__":
    main()
