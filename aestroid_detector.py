import streamlit as st
import requests
from datetime import datetime, timedelta
import plotly.graph_objects as go
import math

st.set_page_config(page_title="Asteroid Detector", page_icon="☄️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Exo+2:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'Exo 2', sans-serif; background-color: #05070f; color: #e0e8ff; }
.stApp { background: radial-gradient(ellipse at 20% 20%, rgba(255,100,0,0.08), transparent 50%), radial-gradient(ellipse at 80% 80%, rgba(100,0,255,0.08), transparent 50%), #05070f; }
h1, h2, h3 { font-family: 'Orbitron', monospace !important; color: #ff9944 !important; letter-spacing: 2px; }
.asteroid-card { background: rgba(255,255,255,0.03); border-radius: 14px; padding: 16px; margin: 8px 0; border-left: 4px solid; }
.safe { border-color: #44ff88; }
.caution { border-color: #ffcc00; }
.hazard { border-color: #ff4444; }
.stat { font-family: 'Orbitron', monospace; font-size: 22px; color: #ff9944; }
.label { font-size: 11px; color: rgba(224,232,255,0.5); font-family: Orbitron; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)

st.markdown("# ☄️ ASTEROID DETECTOR")
st.markdown("<p style='color:rgba(255,153,68,0.6);font-family:Orbitron;font-size:10px;letter-spacing:3px;'>POWERED BY NASA NEOWS API · REAL-TIME NEAR EARTH OBJECTS</p>", unsafe_allow_html=True)

API_KEY = "R4F7iqYocSnbZUk1NbkNNOvlxuJtdOnwL5lG0c9Q"
st.sidebar.markdown("[Get free key →](https://api.nasa.gov)", unsafe_allow_html=True)
st.sidebar.divider()
st.sidebar.markdown("**About**")
st.sidebar.markdown("Real asteroid data from NASA's Near Earth Object Web Service. Tracks asteroids passing close to Earth.")

def get_danger_level(miss_km, is_hazardous):
    if is_hazardous or miss_km < 500000:
        return "hazard", "🔴 HAZARDOUS", "#ff4444"
    elif miss_km < 2000000:
        return "caution", "🟡 CAUTION", "#ffcc00"
    else:
        return "safe", "🟢 SAFE", "#44ff88"

def fetch_asteroids(start_date, end_date, api_key):
    url = f"https://api.nasa.gov/neo/rest/v1/feed"
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "api_key": api_key
    }
    response = requests.get(url, params=params)
    return response.json()

tab1, tab2, tab3 = st.tabs(["☄️ Live Tracker", "📊 Analysis", "🌍 Orbit Visualizer"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.today())
    with col2:
        end_date = st.date_input("End Date", datetime.today() + timedelta(days=2))

    if st.button("🔍 Detect Asteroids", use_container_width=True):
        if not API_KEY:
            st.error("⚠️ Please enter your NASA API key in the sidebar!")
        else:
            with st.spinner("🛸 Scanning for near-Earth objects..."):
                try:
                    data = fetch_asteroids(
                        start_date.strftime("%Y-%m-%d"),
                        end_date.strftime("%Y-%m-%d"),
                        API_KEY
                    )

                    if "near_earth_objects" not in data:
                        st.error("Error fetching data. Check your API key.")
                    else:
                        all_asteroids = []
                        for date_str, asteroids in data["near_earth_objects"].items():
                            for ast in asteroids:
                                close = ast["close_approach_data"][0]
                                miss_km = float(close["miss_distance"]["kilometers"])
                                speed_kmh = float(close["relative_velocity"]["kilometers_per_hour"])
                                diam_min = float(ast["estimated_diameter"]["meters"]["estimated_diameter_min"])
                                diam_max = float(ast["estimated_diameter"]["meters"]["estimated_diameter_max"])
                                diam_avg = (diam_min + diam_max) / 2
                                is_hazardous = ast["is_potentially_hazardous_asteroid"]
                                level, label, color = get_danger_level(miss_km, is_hazardous)
                                all_asteroids.append({
                                    "name": ast["name"],
                                    "date": close["close_approach_date"],
                                    "miss_km": miss_km,
                                    "speed_kmh": speed_kmh,
                                    "diam_avg": diam_avg,
                                    "is_hazardous": is_hazardous,
                                    "level": level,
                                    "label": label,
                                    "color": color,
                                    "id": ast["id"]
                                })

                        all_asteroids.sort(key=lambda x: x["miss_km"])
                        st.session_state.asteroids = all_asteroids

                        total = len(all_asteroids)
                        hazardous = sum(1 for a in all_asteroids if a["is_hazardous"])
                        closest = all_asteroids[0]["miss_km"] if all_asteroids else 0

                        m1, m2, m3 = st.columns(3)
                        with m1:
                            st.markdown(f"""
                            <div style="text-align:center;background:rgba(255,153,68,0.1);border:1px solid rgba(255,153,68,0.3);border-radius:12px;padding:16px">
                                <div class="label">TOTAL DETECTED</div>
                                <div class="stat">{total}</div>
                            </div>""", unsafe_allow_html=True)
                        with m2:
                            st.markdown(f"""
                            <div style="text-align:center;background:rgba(255,68,68,0.1);border:1px solid rgba(255,68,68,0.3);border-radius:12px;padding:16px">
                                <div class="label">POTENTIALLY HAZARDOUS</div>
                                <div class="stat" style="color:#ff4444">{hazardous}</div>
                            </div>""", unsafe_allow_html=True)
                        with m3:
                            st.markdown(f"""
                            <div style="text-align:center;background:rgba(68,255,136,0.1);border:1px solid rgba(68,255,136,0.3);border-radius:12px;padding:16px">
                                <div class="label">CLOSEST (km)</div>
                                <div class="stat" style="color:#44ff88">{closest:,.0f}</div>
                            </div>""", unsafe_allow_html=True)

                        st.divider()
                        st.markdown(f"### Found {total} Near-Earth Objects")

                        for ast in all_asteroids:
                            moon_dist = ast["miss_km"] / 384400
                            st.markdown(f"""
                            <div class="asteroid-card {ast['level']}">
                                <div style="display:flex;justify-content:space-between;align-items:center">
                                    <div>
                                        <div style="font-family:Orbitron;font-size:15px;color:#e0e8ff">{ast['name']}</div>
                                        <div style="font-size:12px;color:rgba(224,232,255,0.5);margin-top:2px">📅 {ast['date']}</div>
                                    </div>
                                    <div style="font-size:13px;font-family:Orbitron;color:{ast['color']}">{ast['label']}</div>
                                </div>
                                <div style="display:flex;gap:20px;margin-top:12px;flex-wrap:wrap">
                                    <div>
                                        <div class="label">MISS DISTANCE</div>
                                        <div style="color:#e0e8ff;font-size:14px">{ast['miss_km']:,.0f} km</div>
                                        <div style="color:rgba(224,232,255,0.4);font-size:11px">{moon_dist:.2f}x Moon distance</div>
                                    </div>
                                    <div>
                                        <div class="label">SPEED</div>
                                        <div style="color:#e0e8ff;font-size:14px">{ast['speed_kmh']:,.0f} km/h</div>
                                    </div>
                                    <div>
                                        <div class="label">DIAMETER</div>
                                        <div style="color:#e0e8ff;font-size:14px">{ast['diam_avg']:.1f} m</div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error: {str(e)}")

with tab2:
    st.markdown("### 📊 Asteroid Analysis")
    if "asteroids" not in st.session_state or not st.session_state.asteroids:
        st.info("👈 Run the detector first to see analysis!")
    else:
        asteroids = st.session_state.asteroids
        names = [a["name"][:20] for a in asteroids[:10]]
        distances = [a["miss_km"]/1000000 for a in asteroids[:10]]
        speeds = [a["speed_kmh"]/1000 for a in asteroids[:10]]
        sizes = [a["diam_avg"] for a in asteroids[:10]]
        colors = [a["color"] for a in asteroids[:10]]

        col1, col2 = st.columns(2)
        with col1:
            fig1 = go.Figure(go.Bar(
                x=distances, y=names, orientation='h',
                marker_color=colors,
                text=[f"{d:.2f}M km" for d in distances],
                textposition='outside'
            ))
            fig1.update_layout(
                title="Miss Distance (Million km)",
                paper_bgcolor='#05070f', plot_bgcolor='#05070f',
                font=dict(color='#e0e8ff'),
                xaxis=dict(showgrid=False, color='#e0e8ff'),
                yaxis=dict(showgrid=False, color='#e0e8ff'),
                height=400, margin=dict(l=0,r=0,t=40,b=0)
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = go.Figure(go.Scatter(
                x=distances, y=speeds,
                mode='markers+text',
                marker=dict(size=[max(5, s/10) for s in sizes], color=colors, opacity=0.8),
                text=[a["name"][:10] for a in asteroids[:10]],
                textposition='top center',
                textfont=dict(color='#e0e8ff', size=9)
            ))
            fig2.update_layout(
                title="Distance vs Speed (marker size = asteroid size)",
                paper_bgcolor='#05070f', plot_bgcolor='#05070f',
                font=dict(color='#e0e8ff'),
                xaxis=dict(title="Distance (Million km)", showgrid=False, color='#e0e8ff'),
                yaxis=dict(title="Speed (1000 km/h)", showgrid=False, color='#e0e8ff'),
                height=400, margin=dict(l=0,r=0,t=40,b=0)
            )
            st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.markdown("### 🌍 Orbit Visualizer")
    if "asteroids" not in st.session_state or not st.session_state.asteroids:
        st.info("👈 Run the detector first to see orbits!")
    else:
        asteroids = st.session_state.asteroids
        fig = go.Figure()

        # Sun
        fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers+text',
            marker=dict(size=20, color='#FDB813'),
            text=['☀️'], textposition='top center',
            textfont=dict(size=16), name='Sun'))

        # Earth orbit
        theta = [i * 2 * math.pi / 100 for i in range(101)]
        fig.add_trace(go.Scatter(
            x=[math.cos(t) for t in theta],
            y=[math.sin(t) for t in theta],
            mode='lines', line=dict(color='#4fa3e0', width=1, dash='dot'),
            name='Earth Orbit', opacity=0.5))

        # Earth
        fig.add_trace(go.Scatter(x=[1], y=[0], mode='markers+text',
            marker=dict(size=12, color='#4fa3e0'),
            text=['🌍'], textposition='top center',
            textfont=dict(size=14), name='Earth'))

        # Asteroids
        for i, ast in enumerate(asteroids[:8]):
            angle = (i / 8) * 2 * math.pi
            dist_au = ast["miss_km"] / 149597870.7 + 1
            dist_au = min(dist_au, 3.0)
            ax = dist_au * math.cos(angle)
            ay = dist_au * math.sin(angle)
            color = ast["color"]
            fig.add_trace(go.Scatter(
                x=[ax], y=[ay], mode='markers+text',
                marker=dict(size=max(6, ast["diam_avg"]/50), color=color),
                text=[ast["name"][:10]], textposition='top center',
                textfont=dict(color=color, size=9),
                name=ast["name"][:15],
                hovertemplate=f'<b>{ast["name"]}</b><br>Miss: {ast["miss_km"]:,.0f} km<br>Speed: {ast["speed_kmh"]:,.0f} km/h<extra></extra>'
            ))
            # Line from Earth to asteroid
            fig.add_trace(go.Scatter(
                x=[1, ax], y=[0, ay], mode='lines',
                line=dict(color=color, width=1, dash='dot'),
                opacity=0.3, showlegend=False, hoverinfo='skip'))

        fig.update_layout(
            paper_bgcolor='#05070f', plot_bgcolor='#05070f',
            xaxis=dict(range=[-3.5,3.5], showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(range=[-3.5,3.5], showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x"),
            height=550, margin=dict(l=0,r=0,t=0,b=0),
            legend=dict(font=dict(color='#e0e8ff', size=9), bgcolor='rgba(5,7,15,0.8)')
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("📏 Distances are approximate and scaled for visualization")

st.markdown("""
<div style='text-align:center;color:rgba(255,153,68,0.3);font-family:Orbitron;font-size:10px;letter-spacing:2px;margin-top:8px;'>
    DATA PROVIDED BY NASA NEOWS API · FOR EDUCATIONAL PURPOSES
</div>
""", unsafe_allow_html=True)
