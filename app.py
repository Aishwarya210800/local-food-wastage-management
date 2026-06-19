import streamlit as st
import pymysql
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Food Wastage Management System",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1b5e20 0%, #2e7d32 50%, #388e3c 100%);
    color: white;
}
section[data-testid="stSidebar"] * { color: white !important; }
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.2); }
.hero {
    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 60%, #66bb6a 100%);
    border-radius: 14px; padding: 28px 36px; color: white; margin-bottom: 28px;
}
.hero h1 { font-size: 1.9rem; font-weight: 700; margin: 0 0 6px; }
.hero p  { margin: 0; opacity: 0.88; font-size: 0.95rem; }
.hero .pills { display: flex; gap: 10px; margin-top: 14px; flex-wrap: wrap; }
.pill {
    background: rgba(255,255,255,0.18); border: 1px solid rgba(255,255,255,0.35);
    border-radius: 20px; padding: 4px 14px; font-size: 0.78rem; font-weight: 600;
}
.kpi-row { display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
.kpi-card {
    flex: 1; min-width: 140px; background: white; border-radius: 12px;
    padding: 18px 20px; box-shadow: 0 2px 12px rgba(0,0,0,.07);
    border-top: 4px solid #2e7d32; text-align: center;
}
.kpi-card .num  { font-size: 2rem; font-weight: 700; color: #1b5e20; }
.kpi-card .lbl  { font-size: 0.8rem; color: #555; margin-top: 2px; }
.kpi-card .icon { font-size: 1.4rem; margin-bottom: 4px; }
.sec-head {
    font-size: 1.05rem; font-weight: 700; color: #1b5e20;
    border-left: 4px solid #4caf50; padding-left: 10px; margin: 24px 0 14px;
}
.alert-success { background:#e8f5e9; color:#1b5e20; border-radius:8px; padding:12px 16px; font-weight:600; margin:8px 0; border-left:4px solid #4caf50; }
.alert-error   { background:#ffebee; color:#b71c1c; border-radius:8px; padding:12px 16px; font-weight:600; margin:8px 0; border-left:4px solid #f44336; }
.alert-info    { background:#e3f2fd; color:#0d47a1; border-radius:8px; padding:12px 16px; font-weight:600; margin:8px 0; border-left:4px solid #1976d2; }
.expiry-soon { background:#fff8e1; border-left:4px solid #ffc107; border-radius:8px; padding:12px 16px; margin:8px 0; }
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATABASE - MySQL Connection
# ─────────────────────────────────────────────
@st.cache_resource
def get_conn():
    return pymysql.connect(
        host="tramway.proxy.rlwy.net",
        port=32241,
        user="root",
        password="HxOgIDRTrnnBsavCGsxOVawLZNgwrGGH",
        database="railway",
        cursorclass=pymysql.cursors.DictCursor
    )

def qdf(sql, params=None):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or [])
        rows = cur.fetchall()
        cur.close()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows)
    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        st.error(f"Query error: {e}")
        return pd.DataFrame()

def dml(sql, params=None):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or [])
        conn.commit()
        cur.close()
        return True, "OK"
    except Exception as e:
        conn.rollback()
        return False, str(e)

def scalar(sql, params=None):
    df = qdf(sql, params)
    if df.empty: return 0
    return df.iloc[0, 0]

# ─────────────────────────────────────────────
# SIDEBAR NAV
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🥗 Food Wastage MS")
    st.markdown("---")
    page = st.radio("Navigation", [
        "🏠  Dashboard",
        "🔍  SQL Query Explorer",
        "🔎  Filter & Search",
        "✏️  CRUD Operations",
        "📊  EDA & Charts",
        "📋  Provider / Receiver Info"
    ], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem;opacity:0.7;'>
    🗄️ MySQL · Streamlit<br>
    4 tables · 4,000 records<br>
    17 SQL queries
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────────
n_p = scalar("SELECT COUNT(*) FROM providers")
n_r = scalar("SELECT COUNT(*) FROM receivers")
n_f = scalar("SELECT COUNT(*) FROM food_listings")
n_c = scalar("SELECT COUNT(*) FROM claims")

st.markdown(f"""
<div class="hero">
  <h1>🥗 Local Food Wastage Management System</h1>
  <p>Connecting surplus food providers to those in need · Reducing food wastage through data</p>
  <div class="pills">
    <span class="pill">🏪 {n_p} Providers</span>
    <span class="pill">🤝 {n_r} Receivers</span>
    <span class="pill">🍱 {n_f} Listings</span>
    <span class="pill">📋 {n_c} Claims</span>
    <span class="pill">🗄️ MySQL</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  PAGE 1 — DASHBOARD
# ═══════════════════════════════════════════════════════════════
if "Dashboard" in page:

    total_qty = scalar("SELECT COALESCE(SUM(Quantity),0) FROM food_listings")
    completed = scalar("SELECT COUNT(*) FROM claims WHERE Status='Completed'")
    pending   = scalar("SELECT COUNT(*) FROM claims WHERE Status='Pending'")
    expiring  = scalar("SELECT COUNT(*) FROM food_listings WHERE Expiry_Date <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)")

    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi-card"><div class="icon">📦</div><div class="num">{total_qty:,}</div><div class="lbl">Total Food Units</div></div>
      <div class="kpi-card"><div class="icon">✅</div><div class="num">{completed}</div><div class="lbl">Completed Claims</div></div>
      <div class="kpi-card"><div class="icon">⏳</div><div class="num">{pending}</div><div class="lbl">Pending Claims</div></div>
      <div class="kpi-card"><div class="icon">⚠️</div><div class="num">{expiring}</div><div class="lbl">Expiring in 7 Days</div></div>
    </div>
    """, unsafe_allow_html=True)

    if expiring and expiring > 0:
        st.markdown(f'<div class="expiry-soon">⚠️ <b>{expiring} food listing(s)</b> expiring within 7 days — redistribute urgently!</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        df = qdf("SELECT Status, COUNT(*) AS cnt FROM claims GROUP BY Status")
        if not df.empty:
            fig = px.pie(df, values="cnt", names="Status", title="📋 Claims by Status",
                         color="Status",
                         color_discrete_map={"Completed":"#2e7d32","Pending":"#ff6f00","Cancelled":"#c62828"})
            fig.update_traces(textinfo="percent+label", hole=0.35)
            fig.update_layout(showlegend=False, margin=dict(t=40,b=10,l=10,r=10), height=280)
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        df = qdf("SELECT Food_Type, COUNT(*) AS cnt FROM food_listings GROUP BY Food_Type")
        if not df.empty:
            fig = px.pie(df, values="cnt", names="Food_Type", title="🥦 Listings by Food Type",
                         color_discrete_sequence=["#388e3c","#ff6f00","#0288d1"])
            fig.update_traces(textinfo="percent+label", hole=0.35)
            fig.update_layout(showlegend=False, margin=dict(t=40,b=10,l=10,r=10), height=280)
            st.plotly_chart(fig, use_container_width=True)

    with c3:
        df = qdf("""SELECT fl.Meal_Type, COUNT(c.Claim_ID) AS claims
                    FROM food_listings fl JOIN claims c ON fl.Food_ID=c.Food_ID
                    GROUP BY fl.Meal_Type ORDER BY claims DESC""")
        if not df.empty:
            fig = px.bar(df, x="Meal_Type", y="claims", title="🍽️ Claims by Meal Type",
                         color="claims", color_continuous_scale="Greens", text="claims")
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False, margin=dict(t=40,b=10,l=10,r=10), height=280, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    c4, c5 = st.columns([3,2])
    with c4:
        df = qdf("SELECT Provider_Type, SUM(Quantity) AS qty FROM food_listings GROUP BY Provider_Type ORDER BY qty DESC")
        if not df.empty:
            fig = px.bar(df, x="Provider_Type", y="qty", title="🏪 Food Quantity by Provider Type",
                         color="qty", color_continuous_scale="YlGn", text="qty")
            fig.update_traces(texttemplate="%{text:,}", textposition="outside")
            fig.update_layout(margin=dict(t=40,b=10), height=300, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    with c5:
        df = qdf("SELECT DATE_FORMAT(Timestamp,'%Y-%m') AS month, COUNT(*) AS claims FROM claims GROUP BY month ORDER BY month")
        if not df.empty:
            fig = px.line(df, x="month", y="claims", title="📅 Monthly Claim Volume",
                          markers=True, color_discrete_sequence=["#2e7d32"])
            fig.update_layout(margin=dict(t=40,b=10), height=300)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="sec-head">🏆 Top 5 Providers by Donation</div>', unsafe_allow_html=True)
    df = qdf("""SELECT p.Name, p.Type, p.City,
                       COUNT(fl.Food_ID) AS Listings, SUM(fl.Quantity) AS Total_Donated
                FROM providers p JOIN food_listings fl ON p.Provider_ID=fl.Provider_ID
                GROUP BY p.Provider_ID, p.Name, p.Type, p.City
                ORDER BY Total_Donated DESC LIMIT 5""")
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════
#  PAGE 2 — SQL QUERY EXPLORER
# ═══════════════════════════════════════════════════════════════
elif "SQL Query" in page:
    st.markdown('<div class="sec-head">🔍 SQL Query Explorer — All 17 Analytical Queries</div>', unsafe_allow_html=True)

    QUERIES = {
        "Q1 — Providers & Receivers per City": {
            "desc": "Count unique food providers and receivers in each city.",
            "sql": """SELECT p.City,
       COUNT(DISTINCT p.Provider_ID) AS Total_Providers,
       COUNT(DISTINCT r.Receiver_ID) AS Total_Receivers
FROM providers p
LEFT JOIN receivers r ON p.City = r.City
GROUP BY p.City ORDER BY Total_Providers DESC LIMIT 15"""
        },
        "Q2 — Provider Type Contribution": {
            "desc": "Which provider category contributes the largest food quantity?",
            "sql": """SELECT Provider_Type,
       COUNT(Food_ID) AS Total_Listings, SUM(Quantity) AS Total_Quantity
FROM food_listings GROUP BY Provider_Type ORDER BY Total_Quantity DESC"""
        },
        "Q3 — Provider Contacts in Top City": {
            "desc": "Contact details of providers in the most active city.",
            "sql": """SELECT Name, Type, Address, City, Contact FROM providers
WHERE City = (SELECT City FROM providers GROUP BY City ORDER BY COUNT(*) DESC LIMIT 1)
LIMIT 10"""
        },
        "Q4 — Receivers with Most Claims": {
            "desc": "Rank food receivers by number of claims.",
            "sql": """SELECT r.Name AS Receiver_Name, r.Type, r.City,
       COUNT(c.Claim_ID) AS Total_Claims
FROM receivers r JOIN claims c ON r.Receiver_ID = c.Receiver_ID
GROUP BY r.Receiver_ID, r.Name, r.Type, r.City
ORDER BY Total_Claims DESC LIMIT 10"""
        },
        "Q5 — Total Food Quantity Available": {
            "desc": "Total units, listing count, and average quantity per listing.",
            "sql": """SELECT SUM(Quantity) AS Total_Food_Quantity,
       COUNT(Food_ID) AS Total_Listings,
       ROUND(AVG(Quantity), 2) AS Avg_Quantity_Per_Listing
FROM food_listings"""
        },
        "Q6 — City with Highest Food Listings": {
            "desc": "Rank cities by volume of active food listings.",
            "sql": """SELECT Location AS City, COUNT(Food_ID) AS Total_Listings,
       SUM(Quantity) AS Total_Quantity
FROM food_listings GROUP BY Location ORDER BY Total_Listings DESC LIMIT 10"""
        },
        "Q7 — Most Common Food Items": {
            "desc": "Most frequently listed food items.",
            "sql": """SELECT Food_Name, Food_Type, COUNT(Food_ID) AS Listing_Count,
       SUM(Quantity) AS Total_Quantity
FROM food_listings GROUP BY Food_Name, Food_Type ORDER BY Listing_Count DESC LIMIT 10"""
        },
        "Q8 — Claims per Food Item": {
            "desc": "Number of claims per food item.",
            "sql": """SELECT fl.Food_Name, fl.Food_Type, fl.Meal_Type,
       COUNT(c.Claim_ID) AS Total_Claims
FROM food_listings fl LEFT JOIN claims c ON fl.Food_ID = c.Food_ID
GROUP BY fl.Food_Name, fl.Food_Type, fl.Meal_Type ORDER BY Total_Claims DESC LIMIT 10"""
        },
        "Q9 — Provider with Most Successful Claims": {
            "desc": "Providers whose food has the most Completed claims.",
            "sql": """SELECT p.Name AS Provider_Name, p.Type, p.City,
       COUNT(c.Claim_ID) AS Successful_Claims
FROM providers p
JOIN food_listings fl ON p.Provider_ID = fl.Provider_ID
JOIN claims c ON fl.Food_ID = c.Food_ID
WHERE c.Status = 'Completed'
GROUP BY p.Provider_ID, p.Name, p.Type, p.City
ORDER BY Successful_Claims DESC LIMIT 10"""
        },
        "Q10 — Claim Status Distribution (%)": {
            "desc": "Percentage breakdown of Completed / Pending / Cancelled claims.",
            "sql": """SELECT Status, COUNT(*) AS Total_Claims,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS Percentage
FROM claims GROUP BY Status ORDER BY Total_Claims DESC"""
        },
        "Q11 — Avg Quantity Claimed per Receiver": {
            "desc": "Average food quantity each receiver claims per transaction.",
            "sql": """SELECT r.Name AS Receiver_Name, r.Type,
       COUNT(c.Claim_ID) AS Total_Claims,
       ROUND(AVG(fl.Quantity), 2) AS Avg_Quantity_Claimed
FROM receivers r
JOIN claims c ON r.Receiver_ID = c.Receiver_ID
JOIN food_listings fl ON c.Food_ID = fl.Food_ID
GROUP BY r.Receiver_ID, r.Name, r.Type
ORDER BY Avg_Quantity_Claimed DESC LIMIT 10"""
        },
        "Q12 — Most Claimed Meal Type": {
            "desc": "Which meal type is distributed most?",
            "sql": """SELECT fl.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims,
       SUM(fl.Quantity) AS Total_Qty_Distributed
FROM food_listings fl JOIN claims c ON fl.Food_ID = c.Food_ID
GROUP BY fl.Meal_Type ORDER BY Total_Claims DESC"""
        },
        "Q13 — Total Food Donated per Provider": {
            "desc": "Cumulative quantity donated by each provider.",
            "sql": """SELECT p.Name AS Provider_Name, p.Type, p.City,
       COUNT(fl.Food_ID) AS Total_Listings, SUM(fl.Quantity) AS Total_Donated
FROM providers p JOIN food_listings fl ON p.Provider_ID = fl.Provider_ID
GROUP BY p.Provider_ID, p.Name, p.Type, p.City ORDER BY Total_Donated DESC LIMIT 10"""
        },
        "Q14 — Food Expiring Soon (Next 30 Days)": {
            "desc": "Urgent redistribution alerts — listings expiring within 30 days.",
            "sql": """SELECT fl.Food_Name, fl.Quantity, fl.Expiry_Date,
       fl.Location, fl.Food_Type, fl.Meal_Type, p.Name AS Provider, p.Contact
FROM food_listings fl JOIN providers p ON fl.Provider_ID = p.Provider_ID
WHERE fl.Expiry_Date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
ORDER BY fl.Expiry_Date ASC LIMIT 15"""
        },
        "Q15 — Food Type Split (Veg/Non-Veg/Vegan)": {
            "desc": "Percentage share of Vegetarian, Non-Vegetarian, and Vegan food.",
            "sql": """SELECT Food_Type, COUNT(Food_ID) AS Total_Listings,
       SUM(Quantity) AS Total_Quantity,
       ROUND(COUNT(Food_ID)*100.0/SUM(COUNT(Food_ID)) OVER(), 2) AS Percentage
FROM food_listings GROUP BY Food_Type ORDER BY Total_Listings DESC"""
        },
        "Q16 — Monthly Claims Trend": {
            "desc": "Month-by-month breakdown of claim volumes by status.",
            "sql": """SELECT DATE_FORMAT(Timestamp,'%Y-%m') AS Month,
       COUNT(Claim_ID) AS Total_Claims,
       COUNT(CASE WHEN Status='Completed' THEN 1 END) AS Completed,
       COUNT(CASE WHEN Status='Pending'   THEN 1 END) AS Pending,
       COUNT(CASE WHEN Status='Cancelled' THEN 1 END) AS Cancelled
FROM claims GROUP BY DATE_FORMAT(Timestamp,'%Y-%m') ORDER BY Month"""
        },
        "Q17 — Top Cities by Completed Claims": {
            "desc": "Rank cities by successfully completed food claims.",
            "sql": """SELECT r.City, COUNT(c.Claim_ID) AS Completed_Claims,
       SUM(fl.Quantity) AS Food_Received
FROM claims c
JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
JOIN food_listings fl ON c.Food_ID = fl.Food_ID
WHERE c.Status = 'Completed'
GROUP BY r.City ORDER BY Completed_Claims DESC LIMIT 10"""
        },
    }

    sel = st.selectbox("Select a query:", list(QUERIES.keys()))
    q   = QUERIES[sel]
    st.info(f"📌 {q['desc']}")

    col_a, col_b = st.columns([1,1])
    run_one = col_a.button("▶️ Run Selected Query", type="primary", use_container_width=True)
    run_all = col_b.button("🚀 Run All 17 Queries", use_container_width=True)

    with st.expander("📄 View SQL Statement", expanded=False):
        st.code(q["sql"], language="sql")

    if run_one:
        df = qdf(q["sql"])
        st.markdown(f'<div class="alert-success">✅ {len(df)} row(s) returned</div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
        num_cols = df.select_dtypes("number").columns.tolist()
        str_cols = df.select_dtypes("object").columns.tolist()
        if num_cols and str_cols and len(df) > 1:
            fig = px.bar(df.head(15), x=str_cols[0], y=num_cols[0],
                         title=f"Chart — {sel}", color=num_cols[0], color_continuous_scale="Greens")
            fig.update_layout(coloraxis_showscale=False, height=320)
            st.plotly_chart(fig, use_container_width=True)

    if run_all:
        st.markdown('<div class="sec-head">📊 Results for All 17 Queries</div>', unsafe_allow_html=True)
        for qname, qdata in QUERIES.items():
            with st.expander(f"**{qname}**"):
                df = qdf(qdata["sql"])
                if not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.caption(f"✅ {len(df)} row(s)")
                else:
                    st.info("No rows returned.")

# ═══════════════════════════════════════════════════════════════
#  PAGE 3 — FILTER & SEARCH
# ═══════════════════════════════════════════════════════════════
elif "Filter" in page:
    st.markdown('<div class="sec-head">🔎 Filter Food Listings</div>', unsafe_allow_html=True)

    cities     = qdf("SELECT DISTINCT Location FROM food_listings ORDER BY Location")["Location"].tolist()
    food_types = ["Vegetarian","Non-Vegetarian","Vegan"]
    meal_types = ["Breakfast","Lunch","Dinner","Snacks"]
    prov_types = ["Restaurant","Grocery Store","Supermarket","Catering Service"]

    col1, col2, col3, col4 = st.columns(4)
    sel_city = col1.selectbox("📍 City",          ["All"] + cities)
    sel_ft   = col2.selectbox("🥦 Food Type",     ["All"] + food_types)
    sel_mt   = col3.selectbox("🍽️ Meal Type",     ["All"] + meal_types)
    sel_pt   = col4.selectbox("🏪 Provider Type", ["All"] + prov_types)

    col5, col6 = st.columns(2)
    min_qty = col5.slider("Min Quantity", 0, 200, 0)
    search  = col6.text_input("🔍 Search food name")

    conds  = ["fl.Quantity >= %s"]
    params = [min_qty]
    if sel_city != "All": conds.append("fl.Location = %s");      params.append(sel_city)
    if sel_ft   != "All": conds.append("fl.Food_Type = %s");     params.append(sel_ft)
    if sel_mt   != "All": conds.append("fl.Meal_Type = %s");     params.append(sel_mt)
    if sel_pt   != "All": conds.append("fl.Provider_Type = %s"); params.append(sel_pt)
    if search:             conds.append("fl.Food_Name LIKE %s");  params.append(f"%{search}%")

    sql = f"""SELECT fl.Food_ID, fl.Food_Name, fl.Quantity, fl.Expiry_Date,
               fl.Location, fl.Food_Type, fl.Meal_Type, fl.Provider_Type,
               p.Name AS Provider, p.Contact
        FROM food_listings fl JOIN providers p ON fl.Provider_ID = p.Provider_ID
        WHERE {' AND '.join(conds)} ORDER BY fl.Quantity DESC"""
    df = qdf(sql, params)

    st.markdown(f'<div class="alert-info">🔍 <b>{len(df)}</b> listing(s) match your filters</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(df.head(15), x="Food_Name", y="Quantity",
                         color="Food_Type", title="Quantity by Food Name (top 15)",
                         color_discrete_map={"Vegetarian":"#2e7d32","Non-Vegetarian":"#ff6f00","Vegan":"#0288d1"})
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            grp = df.groupby("Meal_Type")["Quantity"].sum().reset_index()
            fig2 = px.pie(grp, values="Quantity", names="Meal_Type",
                          title="Quantity Split by Meal Type",
                          color_discrete_sequence=["#388e3c","#66bb6a","#ff6f00","#0288d1"])
            fig2.update_traces(hole=0.3)
            st.plotly_chart(fig2, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
#  PAGE 4 — CRUD OPERATIONS
# ═══════════════════════════════════════════════════════════════
elif "CRUD" in page:
    st.markdown('<div class="sec-head">✏️ CRUD — Create · Read · Update · Delete</div>', unsafe_allow_html=True)

    tab_add, tab_upd, tab_del, tab_view, tab_claim = st.tabs([
        "➕ Add Listing", "✏️ Update", "🗑️ Delete", "📋 View All", "📩 Add Claim"
    ])

    prov_df  = qdf("SELECT Provider_ID, Name FROM providers ORDER BY Name")
    prov_map = dict(zip(prov_df["Name"], prov_df["Provider_ID"]))
    food_df  = qdf("SELECT Food_ID, Food_Name FROM food_listings ORDER BY Food_ID")
    food_lbl = (food_df["Food_Name"] + " (ID:" + food_df["Food_ID"].astype(str) + ")").tolist()
    fid_map  = dict(zip(food_lbl, food_df["Food_ID"].tolist()))
    recv_df  = qdf("SELECT Receiver_ID, Name FROM receivers ORDER BY Name")
    recv_map = dict(zip(recv_df["Name"], recv_df["Receiver_ID"]))

    with tab_add:
        st.subheader("Add New Food Listing")
        with st.form("f_add"):
            c1, c2 = st.columns(2)
            food_name = c1.text_input("Food Name *")
            quantity  = c2.number_input("Quantity *", min_value=1, value=20)
            expiry    = c1.date_input("Expiry Date *", value=date.today()+timedelta(days=7))
            provider  = c2.selectbox("Provider *", list(prov_map.keys()))
            location  = c1.text_input("Location / City *")
            food_type = c2.selectbox("Food Type", ["Vegetarian","Non-Vegetarian","Vegan"])
            meal_type = c1.selectbox("Meal Type", ["Breakfast","Lunch","Dinner","Snacks"])
            prov_type = c2.selectbox("Provider Type", ["Restaurant","Grocery Store","Supermarket","Catering Service"])
            sub       = st.form_submit_button("➕ Add Listing", type="primary")
        if sub:
            if not food_name.strip() or not location.strip():
                st.markdown('<div class="alert-error">❌ Food Name and Location are required.</div>', unsafe_allow_html=True)
            else:
                nid = scalar("SELECT COALESCE(MAX(Food_ID),0)+1 FROM food_listings")
                ok, msg = dml("""INSERT INTO food_listings
                    (Food_ID,Food_Name,Quantity,Expiry_Date,Provider_ID,Provider_Type,Location,Food_Type,Meal_Type)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    [int(nid), food_name.strip(), quantity, expiry,
                     prov_map[provider], prov_type, location.strip(), food_type, meal_type])
                if ok:
                    st.markdown(f'<div class="alert-success">✅ "{food_name}" added successfully!</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="alert-error">❌ {msg}</div>', unsafe_allow_html=True)

    with tab_upd:
        st.subheader("Update a Food Listing")
        sel_lbl = st.selectbox("Select listing to update:", food_lbl)
        fid     = fid_map[sel_lbl]
        row_df  = qdf("SELECT * FROM food_listings WHERE Food_ID = %s", [int(fid)])
        if not row_df.empty:
            row = row_df.iloc[0]
            st.info(f"Current: **{row['Food_Name']}** · Qty: {row['Quantity']} · Expiry: {row['Expiry_Date']} · Location: {row['Location']}")
            with st.form("f_upd"):
                c1, c2 = st.columns(2)
                new_qty = c1.number_input("New Quantity", min_value=1, value=int(row["Quantity"]))
                new_exp = c2.date_input("New Expiry Date", value=row["Expiry_Date"])
                new_loc = c1.text_input("New Location", value=row["Location"])
                new_mt  = c2.selectbox("New Meal Type", ["Breakfast","Lunch","Dinner","Snacks"],
                                       index=["Breakfast","Lunch","Dinner","Snacks"].index(row["Meal_Type"]))
                upd = st.form_submit_button("💾 Save Changes", type="primary")
            if upd:
                ok, msg = dml("""UPDATE food_listings
                    SET Quantity=%s, Expiry_Date=%s, Location=%s, Meal_Type=%s
                    WHERE Food_ID=%s""", [new_qty, new_exp, new_loc, new_mt, int(fid)])
                if ok:
                    st.markdown('<div class="alert-success">✅ Listing updated!</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="alert-error">❌ {msg}</div>', unsafe_allow_html=True)

    with tab_del:
        st.subheader("Delete a Food Listing")
        st.markdown('<div class="alert-error">⚠️ Deleting a listing will also remove all associated claims.</div>', unsafe_allow_html=True)
        del_lbl = st.selectbox("Select listing to delete:", food_lbl)
        del_fid = fid_map[del_lbl]
        prev_df = qdf("SELECT * FROM food_listings WHERE Food_ID=%s", [int(del_fid)])
        st.dataframe(prev_df, use_container_width=True, hide_index=True)
        claim_cnt = scalar("SELECT COUNT(*) FROM claims WHERE Food_ID=%s", [int(del_fid)])
        if claim_cnt:
            st.warning(f"⚠️ This listing has {claim_cnt} associated claim(s) that will also be deleted.")
        confirm = st.checkbox("I understand and confirm deletion.")
        if st.button("🗑️ Delete Listing", type="primary"):
            if not confirm:
                st.warning("Please tick the confirmation checkbox first.")
            else:
                dml("DELETE FROM claims WHERE Food_ID=%s", [int(del_fid)])
                ok, msg = dml("DELETE FROM food_listings WHERE Food_ID=%s", [int(del_fid)])
                if ok:
                    st.markdown('<div class="alert-success">✅ Listing deleted.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="alert-error">❌ {msg}</div>', unsafe_allow_html=True)

    with tab_view:
        st.subheader("All Food Listings")
        view_df = qdf("""SELECT fl.Food_ID, fl.Food_Name, fl.Quantity, fl.Expiry_Date,
                   fl.Location, fl.Food_Type, fl.Meal_Type, fl.Provider_Type,
                   p.Name AS Provider, p.Contact
            FROM food_listings fl JOIN providers p ON fl.Provider_ID=p.Provider_ID
            ORDER BY fl.Food_ID""")
        st.caption(f"Total: {len(view_df)} listings")
        st.dataframe(view_df, use_container_width=True, hide_index=True, height=420)

    with tab_claim:
        st.subheader("Submit a New Claim")
        with st.form("f_claim"):
            c1, c2 = st.columns(2)
            claim_food = c1.selectbox("Food Item", food_lbl)
            claim_recv = c2.selectbox("Receiver", list(recv_map.keys()))
            claim_stat = c1.selectbox("Status", ["Pending","Completed","Cancelled"])
            add_c = st.form_submit_button("📩 Submit Claim", type="primary")
        if add_c:
            nid = scalar("SELECT COALESCE(MAX(Claim_ID),0)+1 FROM claims")
            ok, msg = dml("INSERT INTO claims(Claim_ID,Food_ID,Receiver_ID,Status,Timestamp) VALUES(%s,%s,%s,%s,NOW())",
                [int(nid), fid_map[claim_food], recv_map[claim_recv], claim_stat])
            if ok:
                st.markdown(f'<div class="alert-success">✅ Claim #{nid} submitted!</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-error">❌ {msg}</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  PAGE 5 — EDA & CHARTS
# ═══════════════════════════════════════════════════════════════
elif "EDA" in page:
    st.markdown('<div class="sec-head">📊 Exploratory Data Analysis</div>', unsafe_allow_html=True)
    tab_fl, tab_cl, tab_pr, tab_re = st.tabs(["🍱 Food Listings","📋 Claims","🏪 Providers","🤝 Receivers"])

    with tab_fl:
        c1, c2 = st.columns(2)
        df = qdf("SELECT Food_Type, COUNT(*) AS cnt, SUM(Quantity) AS qty FROM food_listings GROUP BY Food_Type")
        fig = px.pie(df, values="cnt", names="Food_Type", title="Distribution by Food Type",
                     color_discrete_sequence=["#2e7d32","#ff6f00","#0288d1"])
        fig.update_traces(hole=0.3, textinfo="percent+label")
        c1.plotly_chart(fig, use_container_width=True)

        df2 = qdf("SELECT Meal_Type, COUNT(*) AS cnt FROM food_listings GROUP BY Meal_Type ORDER BY cnt DESC")
        fig2 = px.bar(df2, x="Meal_Type", y="cnt", title="Listings by Meal Type",
                      color="cnt", color_continuous_scale="Greens", text="cnt")
        fig2.update_traces(textposition="outside")
        fig2.update_layout(coloraxis_showscale=False)
        c2.plotly_chart(fig2, use_container_width=True)

        df3 = qdf("SELECT Location, COUNT(*) AS cnt FROM food_listings GROUP BY Location ORDER BY cnt DESC LIMIT 15")
        fig3 = px.bar(df3, x="Location", y="cnt", title="Top 15 Cities by Listing Count",
                      color="cnt", color_continuous_scale="YlGn")
        fig3.update_layout(coloraxis_showscale=False, xaxis_tickangle=-35)
        st.plotly_chart(fig3, use_container_width=True)

        df4 = qdf("SELECT Food_Name, SUM(Quantity) AS qty FROM food_listings GROUP BY Food_Name ORDER BY qty DESC LIMIT 12")
        fig4 = px.bar(df4, x="qty", y="Food_Name", orientation="h",
                      title="Top 12 Foods by Total Quantity",
                      color="qty", color_continuous_scale="Greens")
        fig4.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig4, use_container_width=True)

        df5 = qdf("SELECT Provider_Type, Food_Type, SUM(Quantity) AS qty FROM food_listings GROUP BY Provider_Type, Food_Type")
        fig5 = px.bar(df5, x="Provider_Type", y="qty", color="Food_Type",
                      title="Food Type Breakdown per Provider Category", barmode="stack",
                      color_discrete_map={"Vegetarian":"#2e7d32","Non-Vegetarian":"#ff6f00","Vegan":"#0288d1"})
        st.plotly_chart(fig5, use_container_width=True)

    with tab_cl:
        c1, c2 = st.columns(2)
        df = qdf("SELECT Status, COUNT(*) AS cnt FROM claims GROUP BY Status")
        fig = px.pie(df, values="cnt", names="Status", title="Claim Status Distribution",
                     color="Status",
                     color_discrete_map={"Completed":"#2e7d32","Pending":"#ff6f00","Cancelled":"#c62828"})
        fig.update_traces(hole=0.35, textinfo="percent+label")
        c1.plotly_chart(fig, use_container_width=True)

        df2 = qdf("""SELECT fl.Meal_Type, COUNT(c.Claim_ID) AS claims
                     FROM food_listings fl JOIN claims c ON fl.Food_ID=c.Food_ID
                     GROUP BY fl.Meal_Type ORDER BY claims DESC""")
        fig2 = px.bar(df2, x="Meal_Type", y="claims", title="Claims by Meal Type",
                      color="claims", color_continuous_scale="Oranges", text="claims")
        fig2.update_traces(textposition="outside")
        fig2.update_layout(coloraxis_showscale=False)
        c2.plotly_chart(fig2, use_container_width=True)

        df3 = qdf("""SELECT DATE_FORMAT(Timestamp,'%Y-%m') AS month,
                     COUNT(CASE WHEN Status='Completed' THEN 1 END) AS Completed,
                     COUNT(CASE WHEN Status='Pending'   THEN 1 END) AS Pending,
                     COUNT(CASE WHEN Status='Cancelled' THEN 1 END) AS Cancelled
                     FROM claims GROUP BY DATE_FORMAT(Timestamp,'%Y-%m') ORDER BY month""")
        if not df3.empty:
            fig3 = go.Figure()
            for col, color in [("Completed","#2e7d32"),("Pending","#ff6f00"),("Cancelled","#c62828")]:
                fig3.add_trace(go.Bar(x=df3["month"], y=df3[col], name=col, marker_color=color))
            fig3.update_layout(barmode="stack", title="Monthly Claim Trend (Stacked)")
            st.plotly_chart(fig3, use_container_width=True)

        df4 = qdf("""SELECT fl.Food_Type, COUNT(c.Claim_ID) AS claims
                     FROM food_listings fl JOIN claims c ON fl.Food_ID=c.Food_ID GROUP BY fl.Food_Type""")
        fig4 = px.pie(df4, values="claims", names="Food_Type", title="Claims by Food Type",
                      color_discrete_map={"Vegetarian":"#2e7d32","Non-Vegetarian":"#ff6f00","Vegan":"#0288d1"})
        fig4.update_traces(hole=0.3)
        st.plotly_chart(fig4, use_container_width=True)

    with tab_pr:
        c1, c2 = st.columns(2)
        df = qdf("SELECT Type, COUNT(*) AS cnt FROM providers GROUP BY Type ORDER BY cnt DESC")
        fig = px.pie(df, values="cnt", names="Type", title="Providers by Type",
                     color_discrete_sequence=px.colors.sequential.Greens_r[:4])
        fig.update_traces(hole=0.3, textinfo="percent+label")
        c1.plotly_chart(fig, use_container_width=True)

        df2 = qdf("SELECT City, COUNT(*) AS cnt FROM providers GROUP BY City ORDER BY cnt DESC LIMIT 15")
        fig2 = px.bar(df2, x="City", y="cnt", title="Top 15 Cities by Provider Count",
                      color="cnt", color_continuous_scale="Greens")
        fig2.update_layout(coloraxis_showscale=False, xaxis_tickangle=-35)
        c2.plotly_chart(fig2, use_container_width=True)

        df3 = qdf("""SELECT p.Name, p.City, SUM(fl.Quantity) AS Total_Donated
                     FROM providers p JOIN food_listings fl ON p.Provider_ID=fl.Provider_ID
                     GROUP BY p.Provider_ID, p.Name, p.City ORDER BY Total_Donated DESC LIMIT 10""")
        fig3 = px.bar(df3, x="Total_Donated", y="Name", orientation="h",
                      title="Top 10 Providers by Total Quantity Donated",
                      color="Total_Donated", color_continuous_scale="Greens")
        fig3.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

    with tab_re:
        c1, c2 = st.columns(2)
        df = qdf("SELECT Type, COUNT(*) AS cnt FROM receivers GROUP BY Type ORDER BY cnt DESC")
        fig = px.pie(df, values="cnt", names="Type", title="Receivers by Type",
                     color_discrete_sequence=["#1565c0","#0288d1","#4fc3f7","#b3e5fc"])
        fig.update_traces(hole=0.3, textinfo="percent+label")
        c1.plotly_chart(fig, use_container_width=True)

        df2 = qdf("SELECT City, COUNT(*) AS cnt FROM receivers GROUP BY City ORDER BY cnt DESC LIMIT 15")
        fig2 = px.bar(df2, x="City", y="cnt", title="Top 15 Cities by Receiver Count",
                      color="cnt", color_continuous_scale="Blues")
        fig2.update_layout(coloraxis_showscale=False, xaxis_tickangle=-35)
        c2.plotly_chart(fig2, use_container_width=True)

        df3 = qdf("""SELECT r.Name, r.Type, r.City, COUNT(c.Claim_ID) AS Total_Claims
                     FROM receivers r JOIN claims c ON r.Receiver_ID=c.Receiver_ID
                     GROUP BY r.Receiver_ID, r.Name, r.Type, r.City
                     ORDER BY Total_Claims DESC LIMIT 10""")
        fig3 = px.bar(df3, x="Total_Claims", y="Name", orientation="h",
                      title="Top 10 Receivers by Total Claims",
                      color="Total_Claims", color_continuous_scale="Blues")
        fig3.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
#  PAGE 6 — PROVIDER / RECEIVER INFO
# ═══════════════════════════════════════════════════════════════
elif "Provider" in page:
    st.markdown('<div class="sec-head">📋 Provider & Receiver Directory</div>', unsafe_allow_html=True)
    tab_p, tab_r = st.tabs(["🏪 Food Providers", "🤝 Food Receivers"])

    with tab_p:
        st.subheader("Search Food Providers")
        cities_p = qdf("SELECT DISTINCT City FROM providers ORDER BY City")["City"].tolist()
        types_p  = ["Restaurant","Grocery Store","Supermarket","Catering Service"]
        c1, c2, c3 = st.columns(3)
        city_p = c1.selectbox("Filter by City", ["All"] + cities_p, key="pc")
        type_p = c2.selectbox("Filter by Type", ["All"] + types_p, key="pt")
        srch_p = c3.text_input("Search by Name", key="ps")

        conds_p, par_p = [], []
        if city_p != "All": conds_p.append("City = %s"); par_p.append(city_p)
        if type_p != "All": conds_p.append("Type = %s"); par_p.append(type_p)
        if srch_p:          conds_p.append("Name LIKE %s"); par_p.append(f"%{srch_p}%")
        where_p = ("WHERE " + " AND ".join(conds_p)) if conds_p else ""
        df_p = qdf(f"SELECT * FROM providers {where_p} ORDER BY Name LIMIT 50", par_p)
        st.success(f"🏪 {len(df_p)} provider(s) found")
        st.dataframe(df_p, use_container_width=True, hide_index=True)

        if not df_p.empty:
            fig = px.bar(df_p.groupby("Type").size().reset_index(name="count"),
                         x="Type", y="count", title="Type Breakdown",
                         color="count", color_continuous_scale="Greens")
            fig.update_layout(coloraxis_showscale=False, height=280)
            st.plotly_chart(fig, use_container_width=True)

    with tab_r:
        st.subheader("Search Food Receivers / NGOs")
        cities_r = qdf("SELECT DISTINCT City FROM receivers ORDER BY City")["City"].tolist()
        types_r  = ["NGO","Individual","Charity","Shelter"]
        c1, c2, c3 = st.columns(3)
        city_r = c1.selectbox("Filter by City", ["All"] + cities_r, key="rc")
        type_r = c2.selectbox("Filter by Type", ["All"] + types_r,  key="rt")
        srch_r = c3.text_input("Search by Name", key="rs")

        conds_r, par_r = [], []
        if city_r != "All": conds_r.append("City = %s"); par_r.append(city_r)
        if type_r != "All": conds_r.append("Type = %s"); par_r.append(type_r)
        if srch_r:          conds_r.append("Name LIKE %s"); par_r.append(f"%{srch_r}%")
        where_r = ("WHERE " + " AND ".join(conds_r)) if conds_r else ""
        df_r = qdf(f"SELECT * FROM receivers {where_r} ORDER BY Name LIMIT 50", par_r)
        st.success(f"🤝 {len(df_r)} receiver(s) found")
        st.dataframe(df_r, use_container_width=True, hide_index=True)

        if not df_r.empty:
            fig = px.bar(df_r.groupby("Type").size().reset_index(name="count"),
                         x="Type", y="count", title="Type Breakdown",
                         color="count", color_continuous_scale="Blues")
            fig.update_layout(coloraxis_showscale=False, height=280)
            st.plotly_chart(fig, use_container_width=True)
