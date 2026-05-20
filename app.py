import streamlit as st
import requests

st.set_page_config(page_title="FarmSense AI", page_icon="🌾", layout="wide")

st.title("🌾 FarmSense AI")
st.subheader("AI-based Loadshedding Farming Optimisation System")

st.divider()

# =========================
# LOADSHEDDING INPUT MODE
# =========================

st.header("⚡ Loadshedding Schedule Input")

mode = st.radio("Select Input Mode", ["Simple Mode", "Advanced Mode"])

if mode == "Simple Mode":
    stage = st.selectbox(
        "Loadshedding Stage",
        ["Stage 1", "Stage 2", "Stage 3", "Stage 4", "Stage 5", "Stage 6"]
    )
    blocks = []

else:
    st.write("Enter up to 3 loadshedding blocks")

    blocks = []

    for i in range(1, 4):
        col1, col2 = st.columns(2)
        with col1:
            start = st.text_input(f"Block {i} Start Time (e.g. 06:00)", key=f"start{i}")
        with col2:
            end = st.text_input(f"Block {i} End Time (e.g. 08:00)", key=f"end{i}")

        if start and end:
            blocks.append((start, end))

    stage = None  # not used in advanced mode

st.divider()

# =========================
# FARM PROFILE
# =========================

st.header("🚜 Farm Profile")

farm_type = st.selectbox(
    "Farm Type",
    ["Crop Farm", "Dairy Farm", "Poultry Farm", "Packhouse", "Cold Storage"]
)

farm_size = st.selectbox("Farm Size", ["Small", "Medium", "Large"])

crop_type = st.selectbox(
    "Crop Type (if applicable)",
    ["None", "Maize", "Vegetables", "Fruit", "Wheat"]
)

st.divider()

# =========================
# EQUIPMENT
# =========================

st.header("⚙️ Equipment Used")

irrigation = st.checkbox("Irrigation Pump")
cold_storage = st.checkbox("Cold Storage")
milking = st.checkbox("Milking Machine")
heating = st.checkbox("Heating System")
ventilation = st.checkbox("Ventilation System")
generator = st.checkbox("Generator Available")

st.divider()

# =========================
# ENVIRONMENT
# =========================

st.header("🌦️ Environmental Conditions")

temp = st.slider("Temperature (°C)", 0, 50, 25)
humidity = st.slider("Humidity (%)", 0, 100, 50)

weather = st.selectbox("Weather", ["Sunny", "Rainy", "Extreme Heat", "Cold"])

st.divider()

# =========================
# ECONOMIC INPUT
# =========================

st.header("💰 Cost Inputs")

electricity_cost = st.number_input("Electricity Cost (R/kWh)", value=2.50)
diesel_cost = st.number_input("Diesel Cost (R/litre)", value=20.0)
fuel_usage = st.number_input("Generator Fuel Usage (litres/hour)", value=2.0)

st.divider()

# =========================
# AI ENGINE
# =========================

def get_ai_advice(farm_type, stage, risk, weather, grid_cost, diesel_cost_total):

    api_key = "AIzaSyBadWkcuBB6fOyq0u7KFGUnqJqQYyb9QJI"

    prompt = f"""
    You are the CORE DECISION ENGINE of a farm optimisation system.

    You do NOT just explain results — you CREATE the operational plan.

    Your job is to generate a STRICT hour-by-hour schedule that the farm will follow.

    INPUTS:
    Farm type: {farm_type}
    Loadshedding stage: {stage}
    Weather: {weather}
    Risk score: {risk}/100

    Equipment available:
    - Irrigation: {irrigation}
    - Cold storage: {cold_storage}
    - Milking: {milking}
    - Heating: {heating}
    - Ventilation: {ventilation}
    - Generator: {generator}

    GRID COST: {grid_cost}
    DIESEL COST: {diesel_cost_total}

    HARD RULES:
    - Avoid doing irrigation, cooling, or milking during outages
    - Prioritise high-risk operations BEFORE outages
    - Minimise generator usage unless risk is high
    - Every hour must have a decision (no empty slots)

    OUTPUT FORMAT (STRICT - FOLLOW EXACTLY):

    Each hour must be separated by a blank line.

    Each entry must follow this structure:

    06:00  
    Action: <what happens>  
    Reason: <why this is done>  

    07:00  
    Action: <what happens>  
    Reason: <why this is done>  

    08:00  
    Action: <what happens>  
    Reason: <why this is done>  

    RULES:
    - ALWAYS include a blank line between hours
    - NEVER combine hours on one line
    - NEVER use pipes (|)
    - Keep each hour block visually separated
    ...

    Format must look like a professional farm operations report suitable for printing.

    Then:
    - Risk explanation (3 lines max)
    - Efficiency score (0–100)
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    response = requests.post(url, json=payload)
    data = response.json()

    # 🔍 DEBUG SAFETY CHECK (IMPORTANT)
    if "candidates" not in data:
        return f"AI Error: {data}"

    return data["candidates"][0]["content"]["parts"][0]["text"]

if st.button("Generate FarmSense AI Plan"):

    st.header("📊 AI Analysis Results")

    # -------------------------
    # RISK SCORE CALCULATION
    # -------------------------
    risk = 0

    # Loadshedding risk
    if stage in ["Stage 4", "Stage 5", "Stage 6"]:
        risk += 40
    elif stage in ["Stage 2", "Stage 3"]:
        risk += 20

    # Advanced mode penalty
    if mode == "Advanced Mode":
        risk += len(blocks) * 10

    # Farm type risk
    if farm_type == "Cold Storage":
        risk += 35
    elif farm_type == "Poultry Farm":
        risk += 30
    elif farm_type == "Dairy Farm":
        risk += 25
    elif farm_type == "Packhouse":
        risk += 20

    # Equipment risk
    if irrigation:
        risk += 10
    if cold_storage:
        risk += 20
    if milking:
        risk += 15
    if heating:
        risk += 10

    # Environmental risk
    if temp > 32:
        risk += 15
    if humidity > 75:
        risk += 10
    if weather == "Extreme Heat":
        risk += 15

    # Clamp risk
    risk = min(risk, 100)

    # -------------------------
    # DISPLAY RISK
    # -------------------------
    st.subheader("⚠️ Risk Score")
    st.metric("Farm Risk Level", f"{risk}/100")

    if risk >= 70:
        st.error("HIGH RISK: Immediate intervention required")
    elif risk >= 40:
        st.warning("MEDIUM RISK: Adjust operations")
    else:
        st.success("LOW RISK: Stable conditions")

    st.divider()

    # -------------------------
    # RECOMMENDATIONS
    # -------------------------
    st.subheader("⚡ Optimised Action Plan")

    if irrigation:
        st.write("• Run irrigation BEFORE outage blocks")

    if cold_storage:
        st.write("• Pre-cool storage systems before loadshedding")

    if milking:
        st.write("• Schedule milking during stable power windows")

    if heating:
        st.write("• Maintain backup heating systems for livestock")

    if generator:
        st.write("• Use generator strategically during peak outage blocks")

    if temp > 32:
        st.write("• Increase cooling measures due to heat stress")

    if humidity > 75:
        st.write("• Ventilation required to prevent disease risk")

    st.divider()

    # -------------------------
    # COST MODEL
    # -------------------------
    st.subheader("💰 Cost Estimation")

    grid_cost = electricity_cost * 10  # simplified model
    diesel_cost_total = diesel_cost * fuel_usage * len(blocks if mode == "Advanced Mode" else [1])

    st.write(f"Estimated Grid Cost: R{grid_cost:.2f}")
    st.write(f"Estimated Diesel Cost: R{diesel_cost_total:.2f}")

    if diesel_cost_total > grid_cost:
        st.warning("Grid power is more cost-effective (when available)")
    else:
        st.info("Generator usage is more cost-effective during outages")

    st.divider()

    # -------------------------
    # SCHEDULE OUTPUT
    # -------------------------
    st.subheader("📅 Suggested Operational Plan")

    st.write("• Prioritise energy-intensive tasks before outage periods")
    st.write("• Delay non-critical operations during loadshedding")
    st.write("• Monitor equipment during power transitions")

    if mode == "Advanced Mode":
        st.write("### Loadshedding Blocks:")
        for i, b in enumerate(blocks, 1):
            st.write(f"Block {i}: {b[0]} → {b[1]}")

    st.success("FarmSense AI plan generated successfully")

    # -------------------------
    # AI INSIGHT LAYER (NEW)
    # -------------------------
    st.divider()
    st.subheader("🤖 AI Farming Advisor")

    with st.spinner("Generating AI insight..."):
        ai_output = get_ai_advice(
            farm_type,
            stage,
            risk,
            weather,
            grid_cost,
            diesel_cost_total
        )

    st.write(ai_output)

st.divider()