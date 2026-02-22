"""
SEC 13F Institutional Holdings Chat
A free public web app to explore hedge fund holdings using natural language
Powered by Snowflake Cortex Agent
"""

import streamlit as st
import snowflake.connector
import pandas as pd
import json
import re
from datetime import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="SEC 13F Chat | Hedge Fund Holdings",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS - PROFESSIONAL FINANCIAL DESIGN
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=Source+Code+Pro:wght@400;500&display=swap');
    
    /* ===== MAIN BACKGROUND ===== */
    .stApp {
        background: linear-gradient(180deg, #0a0a0a 0%, #111827 50%, #0a0a0a 100%);
    }
    
    /* ===== HEADER STYLING ===== */
    .main-header {
        font-family: 'Inter', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.25rem;
        padding: 0.5rem 0;
        letter-spacing: -0.5px;
    }
    
    .main-header span.gold {
        background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 50%, #f59e0b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .sub-header {
        font-family: 'Inter', sans-serif;
        text-align: center;
        color: #9ca3af;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    
    /* ===== CHAT MESSAGES - HIGH CONTRAST ===== */
    .stChatMessage {
        background: transparent !important;
        padding: 0.75rem 0 !important;
    }
    
    [data-testid="stChatMessageContent"] {
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 1rem !important;
        line-height: 1.7 !important;
    }
    
    /* User message - Gold accent */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%) !important;
        color: #f9fafb !important;
        border-radius: 16px 16px 4px 16px !important;
        padding: 1rem 1.25rem !important;
        border-left: 4px solid #f59e0b !important;
        font-weight: 500 !important;
    }
    
    /* Assistant message - Clean white on dark */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
        background: linear-gradient(135deg, #18181b 0%, #1f1f23 100%) !important;
        color: #f4f4f5 !important;
        border-radius: 16px 16px 16px 4px !important;
        padding: 1.25rem 1.5rem !important;
        border: 1px solid #27272a !important;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4) !important;
    }
    
    /* Make markdown text readable */
    [data-testid="stChatMessageContent"] p {
        color: #e4e4e7 !important;
        margin-bottom: 0.75rem !important;
    }
    
    [data-testid="stChatMessageContent"] strong {
        color: #fbbf24 !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stChatMessageContent"] li {
        color: #e4e4e7 !important;
        margin-bottom: 0.5rem !important;
    }
    
    [data-testid="stChatMessageContent"] ul, [data-testid="stChatMessageContent"] ol {
        padding-left: 1.5rem !important;
    }
    
    /* ===== CHAT INPUT ===== */
    [data-testid="stChatInput"] {
        background: #ffffff !important;
        border: 2px solid #f59e0b !important;
        border-radius: 16px !important;
        padding: 0.5rem 1rem !important;
        margin-top: 1.5rem !important;
        box-shadow: 0 8px 32px rgba(245, 158, 11, 0.15) !important;
    }
    
    [data-testid="stChatInput"] > div {
        background: #ffffff !important;
    }
    
    [data-testid="stChatInput"] textarea {
        color: #111827 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
        background: #ffffff !important;
        min-height: 44px !important;
        line-height: 1.5 !important;
        caret-color: #f59e0b !important;
    }
    
    [data-testid="stChatInput"] textarea::placeholder {
        color: #6b7280 !important;
    }
    
    [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        border-radius: 12px !important;
    }
    
    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #0f172a 100%) !important;
        border-right: 1px solid #1f2937 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #d1d5db !important;
    }
    
    .sidebar-title {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        font-weight: 600;
        color: #f59e0b;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #374151;
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%) !important;
        color: #f9fafb !important;
        border: 1px solid #4b5563 !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        transition: all 0.2s ease !important;
        text-align: left !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #374151 0%, #4b5563 100%) !important;
        border-color: #f59e0b !important;
        transform: translateX(4px) !important;
    }
    
    /* ===== DATA TABLES ===== */
    [data-testid="stDataFrame"] {
        background: #18181b !important;
        border-radius: 12px !important;
        border: 1px solid #27272a !important;
        overflow: hidden !important;
    }
    
    [data-testid="stDataFrame"] th {
        background: #27272a !important;
        color: #fbbf24 !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    [data-testid="stDataFrame"] td {
        color: #e4e4e7 !important;
        font-family: 'Source Code Pro', monospace !important;
        font-size: 0.9rem !important;
    }
    
    /* ===== EXPANDERS ===== */
    [data-testid="stExpander"] {
        background: #1f1f23 !important;
        border: 1px solid #27272a !important;
        border-radius: 10px !important;
    }
    
    [data-testid="stExpander"] summary {
        color: #9ca3af !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* ===== CODE BLOCKS ===== */
    code {
        background: #27272a !important;
        color: #fbbf24 !important;
        padding: 0.2rem 0.5rem !important;
        border-radius: 4px !important;
        font-family: 'Source Code Pro', monospace !important;
    }
    
    pre {
        background: #18181b !important;
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    /* ===== STATUS INDICATOR ===== */
    .status-connected {
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #22c55e;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
        70% { box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }
        100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }
    
    /* ===== DOWNLOAD BUTTON ===== */
    [data-testid="stDownloadButton"] button {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 500 !important;
    }
    
    /* ===== HIDE STREAMLIT BRANDING ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #18181b;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #3f3f46;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #52525b;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# CONFIGURATION
# ============================================
CORTEX_AGENT = "SEC_13F_ANALYTICS.SEMANTIC_LAYER.FINAL_SEC_FILING_AGENT"
WAREHOUSE = "SEC_13F_WAREHOUSE"

# ============================================
# SNOWFLAKE CONNECTION (WITH KEY PAIR SUPPORT)
# ============================================
@st.cache_resource
def get_snowflake_connection():
    """Create Snowflake connection with Key Pair authentication (secure, no password)"""
    try:
        # Check if using Key Pair Authentication
        if "SNOWFLAKE_PRIVATE_KEY" in st.secrets:
            # Load private key
            private_key_pem = st.secrets["SNOWFLAKE_PRIVATE_KEY"]
            
            # Handle key format
            if isinstance(private_key_pem, str):
                private_key_bytes = private_key_pem.encode()
            else:
                private_key_bytes = private_key_pem
            
            # Load the private key
            private_key = serialization.load_pem_private_key(
                private_key_bytes,
                password=None,
                backend=default_backend()
            )
            
            # Get private key bytes for Snowflake
            private_key_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            conn = snowflake.connector.connect(
                user=st.secrets["SNOWFLAKE_USER"],
                account=st.secrets["SNOWFLAKE_ACCOUNT"],
                private_key=private_key_bytes,
                warehouse=st.secrets.get("SNOWFLAKE_WAREHOUSE", WAREHOUSE),
                database=st.secrets.get("SNOWFLAKE_DATABASE", "SEC_13F_ANALYTICS"),
                schema=st.secrets.get("SNOWFLAKE_SCHEMA", "SEMANTIC_LAYER"),
                role=st.secrets.get("SNOWFLAKE_ROLE", None)
            )
        else:
            # Key pair authentication required - no password fallback for security
            st.error("❌ SNOWFLAKE_PRIVATE_KEY not configured. Key pair authentication required.")
            return None
        
        # Enable Snowflake result cache and set session params for performance
        try:
            cursor = conn.cursor()
            cursor.execute("ALTER SESSION SET USE_CACHED_RESULT = TRUE")
            cursor.execute("ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 120")
        except:
            pass
        
        return conn
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

def safe_dataframe(rows, columns=None):
    """Create DataFrame safely - handles column/data mismatches gracefully"""
    try:
        if not rows:
            return pd.DataFrame()
        if columns and len(columns) == len(rows[0]):
            return pd.DataFrame(rows, columns=columns)
        else:
            return pd.DataFrame(rows)
    except Exception:
        try:
            return pd.DataFrame(rows)
        except Exception:
            return pd.DataFrame()

def run_query(conn, sql):
    """Execute SQL query"""
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        return safe_dataframe(data, columns)
    except Exception as e:
        return f"Error: {e}"

# ============================================
# CORTEX AGENTS REST API
# https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-run
# https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-rest-api
# ============================================
import requests
import hashlib
import base64
import time as time_module

def get_jwt_token(account, user, private_key_pem):
    """Generate JWT token for Snowflake authentication"""
    import jwt
    
    # Load private key
    if isinstance(private_key_pem, str):
        private_key_bytes = private_key_pem.encode()
    else:
        private_key_bytes = private_key_pem
    
    private_key = serialization.load_pem_private_key(
        private_key_bytes,
        password=None,
        backend=default_backend()
    )
    
    # Get public key fingerprint for JWT
    public_key = private_key.public_key()
    public_key_der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    sha256_hash = hashlib.sha256(public_key_der).digest()
    fingerprint = "SHA256:" + base64.b64encode(sha256_hash).decode('utf-8')
    
    # Build qualified username (ACCOUNT.USER format)
    account_id = account.upper().split('.')[0]
    qualified_user = f"{account_id}.{user.upper()}"
    
    # Create JWT token
    now = int(time_module.time())
    payload = {
        "iss": f"{qualified_user}.{fingerprint}",
        "sub": qualified_user,
        "iat": now,
        "exp": now + 3600
    }
    jwt_token = jwt.encode(payload, private_key, algorithm="RS256")
    
    return jwt_token

def call_cortex_agent_api(account, user, private_key_pem, database, schema, agent_name, 
                          question, thread_id=None, parent_message_id=None, stream=False, 
                          conversation_history=None):
    """
    Call Cortex Agent via REST API
    https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-run
    
    Endpoint: POST /api/v2/databases/{db}/schemas/{schema}/agents/{name}:run
    """
    try:
        # Use full account identifier with region (e.g., myaccount.us-east-1)
        account_url = account.lower()
        
        # Get JWT token
        jwt_token = get_jwt_token(account, user, private_key_pem)
        
        # Cortex Agent REST API endpoint
        api_url = f"https://{account_url}.snowflakecomputing.com/api/v2/databases/{database}/schemas/{schema}/agents/{agent_name}:run"
        
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream" if stream else "application/json",
            "X-Snowflake-Authorization-Token-Type": "KEYPAIR_JWT"
        }
        
        # Build request body
        # Build messages array with conversation history for context
        messages = []
        
        # Include conversation history if provided (for multi-turn context)
        # EXCLUDE the current question from history to avoid duplication
        if conversation_history:
            # Get all messages EXCEPT the last one (which is the current question)
            history_to_send = conversation_history[:-1] if len(conversation_history) > 0 else []
            for msg in history_to_send[-10:]:  # Last 10 messages for context
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role in ["user", "assistant"] and content:
                    messages.append({
                        "role": role,
                        "content": [{"type": "text", "text": str(content)[:2000]}]  # Limit content length
                    })
        
        # Add current question (the new one)
        messages.append({
            "role": "user",
            "content": [{"type": "text", "text": question}]
        })
        
        request_body = {
            "messages": messages,
            "stream": stream
        }
        
        # Add thread support for conversation continuity
        if thread_id is not None:
            request_body["thread_id"] = thread_id
            request_body["parent_message_id"] = parent_message_id or 0
        
        if stream:
            # Return streaming response object
            response = requests.post(api_url, headers=headers, json=request_body, timeout=120, stream=True)
            if response.status_code == 200:
                return {"success": True, "stream": response, "status_code": response.status_code}
            else:
                return {"success": False, "error": f"API {response.status_code}", "details": response.text[:1000], "status_code": response.status_code}
        else:
            response = requests.post(api_url, headers=headers, json=request_body, timeout=120)
            if response.status_code == 200:
                result = response.json()
                return {"success": True, "data": result, "status_code": response.status_code}
            else:
                return {"success": False, "error": f"API {response.status_code}", "details": response.text[:1000], "status_code": response.status_code}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def stream_cortex_response(response_stream, placeholder):
    """
    Stream Cortex Agent response - EXACTLY like Snowflake Intelligence
    Also extracts thread_id and message_id for conversation continuity
    """
    full_text = ""
    sql_query = None
    result_data = None
    all_result_rows = []  # Collect ALL rows from multiple result_sets
    result_columns = None
    result_metadata = None
    chart_specs = []
    current_event = None
    last_status = ""
    all_text_content = []
    query_count = 0
    
    # For conversation continuity
    response_thread_id = None
    response_message_id = None
    
    # Create the Snowflake Intelligence-style layout
    response_container = placeholder.container()
    
    # Thinking status (like Snowflake's "Thinking completed ✅ 1 verified query")
    thinking_status = response_container.empty()
    thinking_status.markdown("""
<div style="display: flex; align-items: center; gap: 8px; padding: 12px 16px; background: #1e293b; border-radius: 8px; margin-bottom: 16px;">
    <div class="thinking-spinner"></div>
    <span style="color: #94a3b8; font-family: 'Inter', sans-serif; font-size: 14px;">Thinking...</span>
</div>
<style>
.thinking-spinner {
    width: 16px; height: 16px;
    border: 2px solid #334155;
    border-top: 2px solid #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
""", unsafe_allow_html=True)
    
    # Text content area
    text_area = response_container.empty()
    
    try:
        for line in response_stream.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                
                if line_str.startswith('event:'):
                    current_event = line_str[6:].strip()
                    continue
                
                if line_str.startswith('data:'):
                    data_str = line_str[5:].strip()
                    if not data_str or data_str == '[DONE]':
                        continue
                    
                    try:
                        data = json.loads(data_str)
                        
                        # TEXT STREAMING - word by word like Snowflake Intelligence
                        if current_event == "response.text.delta":
                            delta = data.get("text", "")
                            full_text += delta
                            # Update with typing cursor
                            text_area.markdown(full_text + "▌")
                        
                        elif current_event == "response.text":
                            text_content = data.get("text", "")
                            if text_content:
                                all_text_content.append(text_content)
                                full_text = "\n\n".join(all_text_content)
                                text_area.markdown(full_text + "▌")
                        
                        # STATUS - Update thinking indicator
                        elif current_event == "response.status":
                            status_msg = data.get("message", "")
                            if status_msg and status_msg != last_status:
                                last_status = status_msg
                                thinking_status.markdown(f"""
<div style="display: flex; align-items: center; gap: 8px; padding: 12px 16px; background: #1e293b; border-radius: 8px; margin-bottom: 16px;">
    <div class="thinking-spinner"></div>
    <span style="color: #94a3b8; font-family: 'Inter', sans-serif; font-size: 14px;">{status_msg}</span>
</div>
<style>
.thinking-spinner {{
    width: 16px; height: 16px;
    border: 2px solid #334155;
    border-top: 2px solid #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
</style>
""", unsafe_allow_html=True)
                        
                        # TOOL RESULTS - Extract data and charts
                        elif current_event == "response.tool_result":
                            query_count += 1
                            content_list = data.get("content", [])
                            
                            for content_item in content_list:
                                item_type = content_item.get("type", "")
                                
                                if item_type == "text":
                                    tool_text = content_item.get("text", "")
                                    if tool_text and tool_text not in all_text_content:
                                        all_text_content.append(tool_text)
                                        full_text = "\n\n".join(all_text_content)
                                        text_area.markdown(full_text + "▌")
                                
                                elif item_type == "json":
                                    json_data = content_item.get("json", {})
                                    
                                    # Capture SQL query (key for fetching full data)
                                    if "sql" in json_data:
                                        sql_query = json_data["sql"]
                                    
                                    # Also try to get any result_set data from API
                                    if "result_set" in json_data:
                                        rs = json_data["result_set"]
                                        if isinstance(rs, dict) and "data" in rs:
                                            all_result_rows.extend(rs["data"])
                                        if result_metadata is None and "resultSetMetaData" in rs:
                                            result_metadata = rs["resultSetMetaData"]
                                            if "rowType" in result_metadata:
                                                result_columns = [col.get("name") for col in result_metadata["rowType"]]
                                    
                                    if "explanation" in json_data:
                                        exp_text = json_data["explanation"]
                                        if exp_text and exp_text not in all_text_content:
                                            all_text_content.append(exp_text)
                                            full_text = "\n\n".join(all_text_content)
                                    
                                    if "charts" in json_data:
                                        for chart_str in json_data["charts"]:
                                            try:
                                                chart_spec = json.loads(chart_str) if isinstance(chart_str, str) else chart_str
                                                chart_specs.append(chart_spec)
                                            except:
                                                pass
                        
                        elif current_event == "response.thinking.delta":
                            thinking_text = data.get("text", "")
                            if thinking_text:
                                thinking_status.markdown(f"""
<div style="display: flex; align-items: center; gap: 8px; padding: 12px 16px; background: #1e293b; border-radius: 8px; margin-bottom: 16px;">
    <div class="thinking-spinner"></div>
    <span style="color: #94a3b8; font-family: 'Inter', sans-serif; font-size: 14px;">{thinking_text[:80]}...</span>
</div>
<style>
.thinking-spinner {{
    width: 16px; height: 16px;
    border: 2px solid #334155;
    border-top: 2px solid #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
</style>
""", unsafe_allow_html=True)
                        
                        # Extract thread_id and message_id for conversation continuity
                        elif current_event in ["response.done", "message.complete", "response.message"]:
                            if "thread_id" in data:
                                response_thread_id = data["thread_id"]
                            if "message_id" in data:
                                response_message_id = data["message_id"]
                            if "id" in data:  # Sometimes message_id is just "id"
                                response_message_id = data["id"]
                        
                    except json.JSONDecodeError:
                        pass
        
        # FINAL - Show "Thinking completed" like Snowflake Intelligence
        query_text = f"{query_count} verified query" if query_count == 1 else f"{query_count} verified queries"
        if query_count == 0:
            query_text = "completed"
        
        thinking_status.markdown(f"""
<div style="display: flex; align-items: center; gap: 8px; padding: 12px 16px; background: #0f172a; border-radius: 8px; margin-bottom: 16px; border: 1px solid #1e293b;">
    <span style="color: #10b981; font-size: 16px;">✓</span>
    <span style="color: #e2e8f0; font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 500;">Thinking completed</span>
    <span style="color: #64748b; font-family: 'Inter', sans-serif; font-size: 14px;">•</span>
    <span style="color: #10b981; font-family: 'Inter', sans-serif; font-size: 14px;">{query_text}</span>
</div>
""", unsafe_allow_html=True)
        
        # Final text without cursor
        if full_text:
            text_area.markdown(full_text)
        
    except Exception as e:
        thinking_status.markdown(f"""
<div style="display: flex; align-items: center; gap: 8px; padding: 12px 16px; background: #450a0a; border-radius: 8px; margin-bottom: 16px;">
    <span style="color: #ef4444;">⚠️</span>
    <span style="color: #fca5a5; font-family: 'Inter', sans-serif; font-size: 14px;">Error: {str(e)}</span>
</div>
""", unsafe_allow_html=True)
    
    # Combine all collected result rows into final result_data
    if all_result_rows:
        result_data = {
            "data": all_result_rows,
            "resultSetMetaData": result_metadata or {}
        }
        if result_columns:
            result_data["resultSetMetaData"]["rowType"] = [{"name": col} for col in result_columns]
    
    return {
        "text": full_text or "Query executed successfully.",
        "sql": sql_query,
        "data": result_data,
        "charts": chart_specs,
        "thread_id": response_thread_id,
        "message_id": response_message_id
    }

def parse_agent_api_response(api_response):
    """
    Parse the Cortex Agent API response
    https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-run#non-streaming-response-stream-false
    
    Response contains content array with types: text, tool_use, tool_result, thinking, etc.
    """
    if not api_response.get("success"):
        return {"error": api_response.get("error", "Unknown error"), "details": api_response.get("details", "")}
    
    data = api_response.get("data", {})
    content_items = data.get("content", [])
    
    text_response = ""
    sql_query = None
    result_data = None
    
    for item in content_items:
        item_type = item.get("type")
        
        if item_type == "text":
            # Direct text response
            text_response += item.get("text", "")
        
        elif item_type == "tool_result":
            # Tool result (e.g., from cortex_analyst_text_to_sql)
            tool_result = item.get("tool_result", {})
            tool_content = tool_result.get("content", [])
            
            for tc in tool_content:
                if tc.get("type") == "json":
                    json_data = tc.get("json", {})
                    
                    # Extract SQL if present
                    if "sql" in json_data:
                        sql_query = json_data["sql"]
                    
                    # Extract text explanation
                    if "text" in json_data:
                        text_response += json_data["text"] + "\n"
                    
                    # Extract result set
                    if "result_set" in json_data:
                        result_set = json_data["result_set"]
                        if "data" in result_set:
                            result_data = result_set["data"]
                            # Get column names if available
                            metadata = result_set.get("resultSetMetaData", {})
                            if "rowType" in metadata:
                                columns = [col.get("name") for col in metadata["rowType"]]
                                result_data = {"data": result_data, "columns": columns}
        
        elif item_type == "thinking":
            # Agent's reasoning (optional to show)
            thinking = item.get("thinking", {})
            # Can log or display thinking if needed
            pass
    
    return {
        "text": text_response.strip() if text_response else "Query processed successfully.",
        "sql": sql_query,
        "data": result_data
    }

# ============================================
# CORTEX AGENT - USES CORTEX AGENTS REST API WITH STREAMING
# https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-run
# ============================================
def call_cortex_agent_streaming(conn, user_question, response_placeholder, conversation_history=None):
    """
    Call Snowflake Cortex Agent via REST API with STREAMING
    https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-run
    """
    
    try:
        cursor = conn.cursor()
        cursor.execute(f"USE WAREHOUSE {WAREHOUSE}")
        
        # Get thread_id from session state for conversation continuity
        thread_id = st.session_state.get("cortex_thread_id", None)
        parent_message_id = st.session_state.get("cortex_parent_message_id", 0)
        
        # === USE CORTEX AGENT REST API WITH STREAMING ===
        if "SNOWFLAKE_PRIVATE_KEY" in st.secrets:
            # Parse agent name from CORTEX_AGENT config
            agent_parts = CORTEX_AGENT.split('.')
            if len(agent_parts) == 3:
                db, schema, agent_name = agent_parts
            else:
                db, schema, agent_name = "SEC_13F_ANALYTICS", "SEMANTIC_LAYER", "FINAL_SEC_FILING_AGENT"
            
            # Call the Cortex Agent API with streaming
            # Pass conversation history for context (multi-turn support)
            api_result = call_cortex_agent_api(
                account=st.secrets["SNOWFLAKE_ACCOUNT"],
                user=st.secrets["SNOWFLAKE_USER"],
                private_key_pem=st.secrets["SNOWFLAKE_PRIVATE_KEY"],
                database=db,
                schema=schema,
                agent_name=agent_name,
                question=user_question,
                thread_id=thread_id,
                parent_message_id=parent_message_id,
                stream=True,
                conversation_history=st.session_state.messages  # Pass chat history for context
            )
            
            # Check if streaming API worked
            if api_result.get("success") and "stream" in api_result:
                # Stream the response
                result = stream_cortex_response(api_result["stream"], response_placeholder)
                
                text = result.get("text", "")
                sql = result.get("sql")
                data = result.get("data")
                charts = result.get("charts", [])
                
                # UPDATE CONVERSATION CONTEXT - This is key for memory!
                new_thread_id = result.get("thread_id")
                new_message_id = result.get("message_id")
                if new_thread_id:
                    st.session_state.cortex_thread_id = new_thread_id
                if new_message_id:
                    st.session_state.cortex_parent_message_id = new_message_id
                
                # Show table data from either Agent response OR SQL execution
                df = None
                show_data_table = False
                
                # FIRST: Check if Agent returned data in result_set
                if data and isinstance(data, dict):
                    rows = data.get("data", [])
                    metadata = data.get("resultSetMetaData", {})
                    
                    if rows and len(rows) > 0:
                        # Agent returned data - show it!
                        if "rowType" in metadata:
                            columns = [col.get("name") for col in metadata["rowType"]]
                            df = safe_dataframe(rows, columns)
                        else:
                            df = safe_dataframe(rows)
                        show_data_table = True
                
                # SECOND: If no agent data, try executing SQL ourselves
                if df is None and sql and sql.strip().upper().startswith("SELECT"):
                    try:
                        cursor.execute(sql)
                        results = cursor.fetchall()
                        columns = [desc[0] for desc in cursor.description]
                        df = safe_dataframe(results, columns)
                        show_data_table = True
                    except Exception as sql_err:
                        df = None
                        show_data_table = False
                
                return {
                    "text": text or "Agent processed your request.",
                    "data": df if show_data_table else None,  # Only include data if complete
                    "sql": sql,
                    "charts": charts
                }
            else:
                # Streaming failed, try non-streaming
                api_result = call_cortex_agent_api(
                    account=st.secrets["SNOWFLAKE_ACCOUNT"],
                    user=st.secrets["SNOWFLAKE_USER"],
                    private_key_pem=st.secrets["SNOWFLAKE_PRIVATE_KEY"],
                    database=db,
                    schema=schema,
                    agent_name=agent_name,
                    question=user_question,
                    thread_id=thread_id,
                    parent_message_id=parent_message_id,
                    stream=False,
                    conversation_history=st.session_state.messages
                )
                
                if api_result.get("success"):
                    parsed = parse_agent_api_response(api_result)
                    if "error" not in parsed:
                        text = parsed.get("text", "")
                        sql = parsed.get("sql")
                        data = parsed.get("data")
                        
                        # Stream the text manually
                        streamed_text = ""
                        for char in text:
                            streamed_text += char
                            response_placeholder.markdown(streamed_text + "▌")
                            time_module.sleep(0.005)
                        response_placeholder.markdown(text)
                        
                        if sql and sql.strip().upper().startswith("SELECT") and not data:
                            try:
                                cursor.execute(sql)
                                results = cursor.fetchall()
                                columns = [desc[0] for desc in cursor.description]
                                df = safe_dataframe(results, columns)
                                return {"text": text or f"✅ Found {len(df)} results:", "data": df, "sql": sql}
                            except:
                                pass
                        
                        return {"text": text, "data": data, "sql": sql}
        
        # === FALLBACK: Use Cortex Complete ===
        response_placeholder.markdown("🔄 Using fallback method...")
        
        context_text = ""
        if conversation_history and len(conversation_history) > 0:
            recent_history = conversation_history[-10:]
            context_parts = []
            for msg in recent_history:
                role = "User" if msg.get("role") == "user" else "Assistant"
                content = msg.get("content", "")[:500]
                context_parts.append(f"{role}: {content}")
            context_text = "\n".join(context_parts)
        
        prompt = """You are an expert Snowflake SQL analyst for SEC 13F hedge fund holdings data.

TABLE: SEC_13F_ANALYTICS.SEMANTIC_LAYER.HOLDINGS_DENORMALIZED

COLUMNS:
- HEDGE_FUND_NAME: Institution name. ALWAYS use ILIKE with wildcards: ILIKE '%BERKSHIRE%'
- HEDGE_FUND_CIK: Unique fund ID
- COMPANY_NAME: Stock name (e.g., 'APPLE INC', 'NVIDIA CORPORATION')
- CUSIP: Stock identifier
- SECURITY_TYPE: 'STOCK', 'ETF', or 'OPTION' - ALWAYS filter for 'STOCK' when asking about stocks!
- "2025-Q3_VALUE": Q3 2025 value in USD (use double quotes!)
- "2025-Q3_SHARES": Q3 2025 shares
- "2025-Q2_VALUE", "2025-Q2_SHARES": Q2 2025 data
- "2025-Q1_VALUE", "2024-Q4_VALUE": Earlier quarters

RULES:
1. ALWAYS use double quotes for column names with hyphens
2. ALWAYS use ILIKE with % wildcards for name matching  
3. ALWAYS filter SECURITY_TYPE = 'STOCK' when asking about stocks (not ETFs)
4. Use ORDER BY DESC NULLS LAST
5. Default LIMIT 25 unless specified

""" + (f"""CONVERSATION CONTEXT:
{context_text}

""" if context_text else "") + f"""QUESTION: {user_question}

Return ONLY the SQL query. No explanation. No markdown."""
        
        escaped_prompt = prompt.replace("'", "''")
        complete_sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large', '{escaped_prompt}') AS response"
        cursor.execute(complete_sql)
        result = cursor.fetchone()
        
        if result and result[0]:
            generated_sql = result[0].strip()
            
            if "```" in generated_sql:
                match = re.search(r'```(?:sql)?\s*(SELECT.*?)```', generated_sql, re.IGNORECASE | re.DOTALL)
                if match:
                    generated_sql = match.group(1).strip()
            
            generated_sql = generated_sql.strip().rstrip(";")
            
            if generated_sql.upper().startswith("SELECT"):
                # Stream "Executing query..." message
                response_placeholder.markdown("✅ Executing query...")
                
                cursor.execute(generated_sql)
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                df = safe_dataframe(results, columns)
                
                response_placeholder.markdown(f"✅ Found {len(df)} results:")
                return {"text": f"✅ Found {len(df)} results:", "data": df, "sql": generated_sql, "fallback": True}
        
        response_placeholder.markdown("⚠️ Could not process your question.")
        return {"error": "Could not process your question. Please try rephrasing."}
        
    except Exception as e:
        response_placeholder.markdown(f"⚠️ Error: {str(e)}")
        return {"error": str(e)}

def parse_agent_result(result):
    """Parse result from agent call"""
    if isinstance(result, str):
        try:
            # Try to parse as JSON
            parsed = json.loads(result)
            if isinstance(parsed, dict):
                text = parsed.get("text", parsed.get("message", parsed.get("answer", "")))
                data = parsed.get("data", parsed.get("results", parsed.get("sql_results", None)))
                sql = parsed.get("sql", parsed.get("generated_sql", None))
                
                # Convert data to DataFrame if it's a list
                if isinstance(data, list) and len(data) > 0:
                    data = safe_dataframe(data)
                
                return {"text": text or str(parsed), "data": data, "sql": sql}
            return {"text": str(parsed), "data": None}
        except json.JSONDecodeError:
            return {"text": result, "data": None}
    return {"text": str(result), "data": None}

def display_snowflake_style_results(df, charts=None, key_prefix="results", page_size=15):
    """
    Display results EXACTLY like Snowflake Intelligence:
    - Chart/Table toggle
    - Pagination (1 of X)
    - Clean white container
    - No SQL shown by default
    """
    if df is None and not charts:
        return
    
    # Container with Snowflake Intelligence styling
    st.markdown("""
<div style="background: #ffffff; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin: 16px 0; overflow: hidden;">
""", unsafe_allow_html=True)
    
    # Header with Chart/Table toggle
    view_key = f"{key_prefix}_view"
    if view_key not in st.session_state:
        st.session_state[view_key] = "chart" if charts else "table"
    
    col1, col2, col3 = st.columns([4, 2, 1])
    
    with col2:
        if charts and df is not None and len(df) > 0:
            view_options = st.radio(
                "View",
                ["Chart", "Table"],
                index=0 if st.session_state[view_key] == "chart" else 1,
                horizontal=True,
                key=f"{key_prefix}_toggle",
                label_visibility="collapsed"
            )
            st.session_state[view_key] = view_options.lower()
    
    # Show Chart or Table based on selection
    if st.session_state[view_key] == "chart" and charts:
        for i, chart_spec in enumerate(charts):
            try:
                # Style the chart like Snowflake Intelligence (blue bars)
                if isinstance(chart_spec, dict):
                    # Ensure consistent styling
                    if "config" not in chart_spec:
                        chart_spec["config"] = {}
                    chart_spec["config"]["view"] = {"stroke": "transparent"}
                    chart_spec["config"]["axis"] = {"labelColor": "#374151", "titleColor": "#111827"}
                    
                st.vega_lite_chart(chart_spec, use_container_width=True)
            except Exception as e:
                st.caption(f"Chart error: {e}")
    
    elif df is not None and len(df) > 0:
        total_rows = len(df)
        total_pages = (total_rows + page_size - 1) // page_size
        
        # Page state
        page_key = f"{key_prefix}_page"
        if page_key not in st.session_state:
            st.session_state[page_key] = 0
        
        current_page = st.session_state[page_key]
        start_idx = current_page * page_size
        end_idx = min(start_idx + page_size, total_rows)
        
        # Display dataframe
        st.dataframe(
            df.iloc[start_idx:end_idx],
            use_container_width=True,
            height=min(500, (end_idx - start_idx + 1) * 35 + 50)
        )
        
        # Pagination footer like Snowflake Intelligence
        if total_pages > 1:
            st.markdown(f"""
<div style="display: flex; align-items: center; justify-content: center; gap: 16px; padding: 12px; background: #f8fafc; border-top: 1px solid #e2e8f0;">
    <span style="color: #64748b; font-family: 'Inter', sans-serif; font-size: 14px;">
        <strong style="color: #1e293b;">{current_page + 1}</strong> of <strong style="color: #1e293b;">{total_pages}</strong>
    </span>
</div>
""", unsafe_allow_html=True)
            
            # Navigation buttons
            nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
            with nav_col1:
                if st.button("◀ Previous", key=f"{key_prefix}_prev", disabled=current_page == 0, use_container_width=True):
                    st.session_state[page_key] = current_page - 1
                    st.rerun()
            with nav_col3:
                if st.button("Next ▶", key=f"{key_prefix}_next", disabled=current_page >= total_pages - 1, use_container_width=True):
                    st.session_state[page_key] = current_page + 1
                    st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Download button (subtle)
    if df is not None and len(df) > 0:
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            csv,
            "sec13f_results.csv",
            "text/csv",
            key=f"{key_prefix}_download"
        )


def parse_agent_response(response):
    """Parse agent response and extract text, data, sql, and charts"""
    if response is None:
        return "No response received.", None, None, None
    
    if isinstance(response, dict):
        if "error" in response:
            return f"⚠️ Error: {response['error']}", None, None, None
        
        # Extract text response
        text = response.get("text", response.get("message", response.get("content", "")))
        
        # Extract data/results if present
        data = response.get("data", response.get("results", response.get("sql_results", None)))
        
        # Extract SQL if present
        sql = response.get("sql", response.get("generated_sql", response.get("query", None)))
        
        # Extract charts if present
        charts = response.get("charts", [])
        
        # If data is a list of dicts, convert to DataFrame
        if isinstance(data, list) and len(data) > 0:
            try:
                data = safe_dataframe(data)
            except:
                pass
        
        # Check for fallback flag
        if response.get("fallback"):
            text = "ℹ️ " + text
        
        return text if text else "Response received.", data, sql, charts
    
    return str(response), None, None, None

# ============================================
# MAIN APP
# ============================================

# Header - Professional Financial Design
st.markdown('''
<div style="text-align: center; padding: 1rem 0 0.5rem 0;">
    <h1 class="main-header">
        <span class="gold">13F</span> Institutional Holdings Terminal
    </h1>
    <p class="sub-header">
        AI-Powered Analysis of SEC 13F Filings from Institutional Investors
    </p>
    <div style="display: flex; justify-content: center; margin-top: 0.5rem;">
        <span style="color: #6b7280; font-size: 0.85rem;">❄️ <span style="color: #9ca3af;">Powered by Snowflake Cortex</span></span>
    </div>
</div>
''', unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize Cortex Agent thread state for conversation continuity
if "cortex_thread_id" not in st.session_state:
    st.session_state.cortex_thread_id = None
if "cortex_parent_message_id" not in st.session_state:
    st.session_state.cortex_parent_message_id = 0

# Get connection
conn = get_snowflake_connection()


# Sidebar - Professional Financial Design
with st.sidebar:
    # Logo/Brand section
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0; border-bottom: 1px solid #374151; margin-bottom: 1.5rem;">
        <div style="font-size: 1.5rem; font-weight: 700; color: #fbbf24; letter-spacing: -0.5px;">13F Terminal</div>
        <div style="font-size: 0.75rem; color: #6b7280; margin-top: 0.25rem; text-transform: uppercase; letter-spacing: 1px;">Institutional Analytics</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Connection status
    if conn:
        st.markdown('''
        <div style="background: linear-gradient(135deg, #064e3b 0%, #065f46 100%); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <span class="status-connected"></span>
            <span style="color: #a7f3d0; font-size: 0.85rem; font-weight: 500;">Connected to Snowflake</span>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.error("❌ Not connected")
    
    # Creator info (no "Developer" label)
    st.markdown("""
    <div style="background: #1f2937; padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 3px solid #f59e0b;">
        <div style="font-size: 0.95rem; color: #f9fafb; font-weight: 600;">Sameer Shahzad</div>
        <a href="https://www.linkedin.com/in/sameer-shahzad-87808954" target="_blank" style="color: #60a5fa; text-decoration: none; font-size: 0.8rem;">LinkedIn →</a>
    </div>
    """, unsafe_allow_html=True)
    
    # Data Coverage & Technology (integrated, no headings)
    st.markdown("""
    <div style="font-size: 0.8rem; color: #9ca3af; line-height: 1.9; margin-bottom: 1rem;">
        <div>📊 <a href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=13F&company=&dateb=&owner=include&count=40" target="_blank" style="color: #60a5fa; text-decoration: none;">SEC EDGAR 13F Filings</a></div>
        <div>📅 Q4 2024 · Q1 · Q2 · Q3 2025</div>
        <div>📁 13M+ holdings · 8,300+ institutions</div>
        <div>💰 Institutions >$100M AUM</div>
    </div>
    <div style="font-size: 0.75rem; color: #6b7280; line-height: 1.6; margin-bottom: 1rem;">
        ❄️ Snowflake Cortex · 🤖 Text-to-SQL · 🔗 REST API
    </div>
    """, unsafe_allow_html=True)
    
    # Clickable quarter explanation
    with st.expander("ℹ️ What do these quarters mean?"):
        st.markdown("""
        **13F filings report holdings at quarter-end:**
        
        | Quarter | Holdings As Of | Filed By |
        |---------|----------------|----------|
        | **Q4 2024** | Dec 31, 2024 | Feb 14, 2025 |
        | **Q1 2025** | Mar 31, 2025 | May 15, 2025 |
        | **Q2 2025** | Jun 30, 2025 | Aug 14, 2025 |
        | **Q3 2025** | Sep 30, 2025 | Nov 14, 2025 |
        
        *Example: Q2 2025 shows positions held on June 30, 2025*
        """, unsafe_allow_html=True)
    
    st.markdown('<p class="sidebar-title">Common Prompts</p>', unsafe_allow_html=True)
    
    # Verified example prompts
    example_prompts = [
        "In the last two quarters, what are the top 5 stocks on which the maximum number of hedge funds increased their positions consecutively?",
        "In the last four quarters (Q4 2024 to Q3 2025), what are the top 10 stocks on which hedge funds increased their portfolio consecutively?",
        "What are the top 5 stocks in which Berkshire Hathaway has continuously been increasing its holding position in the last four quarters (Q4 2024 to Q3 2025)?",
        "Which funds are constantly increasing their Snowflake stock holdings in the last three quarters?",
        "Which stocks had a 10x increase in institutional holders in one quarter?",
        "As per the latest filing of Q3 2025, what is the total AUM in Billions for each of the top 10 institutional managers (Hedge Funds)?",
        "As per the latest filings, what are the top 10 most widely held stocks?",
        "Which companies have the highest number of institutional investors holding their stock?",
    ]
    
    for i, prompt in enumerate(example_prompts):
        if st.button(prompt, key=f"ex_{i}", use_container_width=True):
            st.session_state.pending_question = prompt
    
    st.markdown("---")
    
    if st.button("🔄 New Session", use_container_width=True):
        st.session_state.messages = []
        st.session_state.cortex_thread_id = None
        st.session_state.cortex_parent_message_id = 0
        st.rerun()

# Chat container - scrollable area for messages
chat_container = st.container()

# Display chat history in the container
with chat_container:
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"], avatar="🧑‍💼" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])
            
            # Show results like Snowflake Intelligence (Chart/Table toggle, no SQL)
            msg_charts = message.get("charts", [])
            msg_data = message.get("data")
            if msg_data is not None or msg_charts:
                display_snowflake_style_results(msg_data, msg_charts, key_prefix=f"hist_{i}")

# Fixed chat input at bottom (Streamlit's native chat_input)
user_input = st.chat_input("Ask about hedge fund holdings... e.g., What are the top 10 holdings of Berkshire Hathaway?")

# Handle pending questions from sidebar
if "pending_question" in st.session_state:
    user_input = st.session_state.pending_question
    del st.session_state.pending_question

# Process question with streaming
if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message immediately
    with chat_container:
        with st.chat_message("user", avatar="🧑‍💼"):
            st.markdown(user_input)
    
    if not conn:
        with chat_container:
            with st.chat_message("assistant", avatar="🤖"):
                st.error("❌ Unable to connect to database. Please check configuration.")
        st.session_state.messages.append({
            "role": "assistant",
            "content": "❌ Unable to connect to database.",
            "data": None,
            "sql": None
        })
    else:
        # Display assistant response with REAL-TIME STREAMING
        with chat_container:
            with st.chat_message("assistant", avatar="🤖"):
                # Create placeholder for streaming response
                response_placeholder = st.empty()
                response_placeholder.markdown("🤔 Thinking...")
                
                # Call the Cortex Agent with STREAMING
                response = call_cortex_agent_streaming(
                    conn, 
                    user_input, 
                    response_placeholder,
                    st.session_state.messages
                )
        
        # Parse the response
                text, data, sql, charts = parse_agent_response(response)
        
                # Show results like Snowflake Intelligence (Chart/Table toggle, no SQL)
                if data is not None or (charts and len(charts) > 0):
                    display_snowflake_style_results(data, charts, key_prefix="latest")
        
        # Save to session state
        st.session_state.messages.append({
            "role": "assistant",
            "content": text,
            "data": data,
            "sql": sql,
            "charts": charts
        })

    st.rerun()

