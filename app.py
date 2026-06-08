import streamlit as st
import pandas as pd
import time
import random
import os
import json
import math
from src.data_generator import TransactionGenerator
from src.fraud_engine import FraudDetector
import plotly.express as px
import plotly.graph_objects as go

# Setup
st.set_page_config(page_title="Digital Twin Fraud Detection", layout="wide")

# Antigravity Theme: Deep Charcoal, Glowing Accents
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* Main App Background (Deep Charcoal) */
    .stApp {
        background-color: #0B0B0B;
        color: #F0F0F0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Background (Deep Charcoal) */
    [data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 1px solid #1F1F1F;
    }
    
    /* Glowing Headers & Title */
    .glow-title {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        letter-spacing: -1px;
        text-shadow: 0 0 10px #7B61FF, 0 0 20px #7B61FF66;
        font-size: 2.5rem;
        margin-bottom: 5px;
    }
    
    .glow-text {
        text-shadow: 0 0 8px #7B61FF;
    }
    
    /* Metrics & Brain Section Containers */
    [data-testid="stMetric"] {
        background-color: #161616;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #2A2A2A;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        min-height: 110px;
    }
    
    /* DNA Card Styling */
    .dna-card {
        background-color: #161616;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #2A2A2A;
        min-height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }

    .dna-card-title {
        font-size: 0.75rem;
        font-weight: 700;
        color: #888;
        margin-bottom: 10px;
        text-transform: uppercase;
    }

    /* Persona Card: Antigravity Glow */
    .persona-card {
        padding: 20px;
        border-radius: 16px;
        background: linear-gradient(135deg, #1A1A1A 0%, #111111 100%);
        border: 1px solid #7B61FF44;
        margin-bottom: 25px;
        box-shadow: 0 0 15px rgba(123, 97, 255, 0.15);
    }

    /* Live Activity Cards */
    .activity-card {
        padding: 14px; 
        border-radius: 10px; 
        background-color: #161616; 
        margin-bottom: 12px; 
        border: 1px solid #232323;
        transition: all 0.1s ease;
    }
    .activity-card:hover {
        border-color: #7B61FF88;
        transform: translateY(-2px);
    }

    .dna-icon {
        color: #7B61FF;
        width: 16px;
        height: 16px;
    }

    /* Buttons */

    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #7B61FF 0%, #5E5CE6 100%);
        border: none;
        color: white;
    }
    .stButton>button[kind="secondary"] {
        background-color: transparent;
        border: 1px solid #3A3A3A;
        color: #BBBBBB;
    }
    .stButton>button[kind="secondary"]:hover {
        border-color: #7B61FF;
        color: #7B61FF;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #111111;
        border-radius: 4px 4px 0 0;
        color: #888 !important;
        padding: 8px 16px;
        border: 1px solid #222;
    }
    .stTabs [aria-selected="true"] {
        color: #7B61FF !important;
        border-bottom: 2px solid #7B61FF !important;
        background-color: #161616;
    }

    /* Expander styling */
    .stExpander {
        background-color: #111111 !important;
        border: 1px solid #222 !important;
        border-radius: 8px !important;
    }

    .icon-teal { color: #00E5FF; }
    .icon-amber { color: #FFAA00; }
    .icon-red { color: #FF3B30; }

    /* Material Icon Scaling */
    .material-symbols-outlined {
        font-size: 20px;
        vertical-align: middle;
        margin-right: 8px;
        color: #7B61FF;
    }
    .icon-small {
        font-size: 16px;
        margin-right: 4px;
    }
</style>

<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
<script src="https://unpkg.com/lucide@latest"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        lucide.createIcons();
    });
    // Re-run lucide on Streamlit re-renders
    window.parent.postMessage({type: 'streamlit:render'}, '*');
</script>
""", unsafe_allow_html=True)

# Main Title with Glow
st.markdown('<h1 class="glow-title">Digital Twin AI: Fraud Detection</h1>', unsafe_allow_html=True)
st.markdown("<p style='color: #7B61FF; font-weight: 600; font-size: 1.1rem; margin-top: -15px;'>Behavioral Intelligence Ledger</p>", unsafe_allow_html=True)

# Initialize Session State
if "detector" not in st.session_state:
    st.session_state.detector = FraudDetector()
    st.session_state.generator = TransactionGenerator()
    st.session_state.user_persona = st.session_state.generator.generate_user_profile()
    st.session_state.history = []

# Sidebar - Controls
with st.sidebar:
    st.header("Active Persona")
    
    # Antigravity Styled Persona Card with Glowing Name & Icons
    st.markdown(f"""
    <div class="persona-card">
        <h2 style="margin:0; color: #FFFFFF; font-size: 1.4rem;" class="glow-text">
            <span class="material-symbols-outlined">person</span>{st.session_state.user_persona['name']}
        </h2>
        <p style="margin:8px 0; color: #888; font-size: 0.9rem; display: flex; align-items: center;">
            <span class="material-symbols-outlined icon-small">location_on</span>{st.session_state.user_persona['home_city']}, {st.session_state.user_persona['home_country']}
        </p>
        <div style="padding: 4px 10px; background: #7B61FF22; border: 1px solid #7B61FF44; border-radius: 6px; display: flex; align-items: center; width: fit-content;">
            <span class="material-symbols-outlined icon-small">fingerprint</span>
            <code style="color: #7B61FF; font-weight: 700; font-size: 0.8rem;">ID: {str(st.session_state.user_persona['user_id'])[-12:]}</code>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Data Bootstrapping", expanded=True):
        st.write("Train AI with historical behavioral data.")
        if st.button("Train Model from CSV", use_container_width=True):
            try:
                df_history = pd.read_csv("data/user_history.csv")
                df_history['timestamp'] = pd.to_datetime(df_history['timestamp'])
                
                persona_path = "data/persona.json"
                if os.path.exists(persona_path):
                    with open(persona_path, 'r') as f:
                        st.session_state.user_persona = json.load(f)
                
                df_fraud = pd.read_csv("data/global_fraud_patterns.csv")
                
                num_local = st.session_state.detector.batch_train_local(df_history)
                num_global = st.session_state.detector.batch_train_global(df_fraud)
                
                st.success(f"System Optimized: {num_local} nodes updated.")
                st.rerun()
            except FileNotFoundError:
                st.error("Data source missing.")

    st.subheader("Simulation")
    bank_name = "SBI Terminal" if st.session_state.detector.bank_id == "SBI_INDIA" else "HDFC Terminal"
    st.caption(f"Active Node: **{bank_name}**")

    if st.button("Generate Legit Transaction", type="primary", use_container_width=True):
        tx = st.session_state.generator.generate_transaction(st.session_state.user_persona, is_fraud=False)
        tx["user_id"] = st.session_state.user_persona["user_id"]
        result = st.session_state.detector.analyze_transaction(tx)
        st.session_state.history.insert(0, {**tx, **result})

    if st.button("Generate FRAUD Transaction", type="secondary", use_container_width=True):
        wisdom = st.session_state.detector.ledger.get_global_wisdom()
        tx = st.session_state.generator.generate_transaction(st.session_state.user_persona, is_fraud=True)
        
        # DEMO TIP: Diversified Federated Alarms
        if random.random() < 0.5:
             # Randomly choose which federated indicator to push (or both)
             scenario = random.choice(["high_amount", "night_txn", "both"])
             if scenario in ["high_amount", "both"]:
                  tx["amount"] = random.uniform(10500.0, 18500.0)
             if scenario in ["night_txn", "both"]:
                  tx["is_night_txn"] = True
             elif scenario == "high_amount": # Ensure it's not night if only high amount chosen
                  tx["is_night_txn"] = False
            
        tx["user_id"] = st.session_state.user_persona["user_id"]
        result = st.session_state.detector.analyze_transaction(tx)
        st.session_state.history.insert(0, {**tx, **result})

    st.markdown("---")
    st.subheader("Global Sync")
    st.session_state.detector.bfl_enabled = st.toggle("Blockchain Network", value=True)
    
    with st.expander("Sister Bank (HDFC)"):
        if st.button("Trigger Attack at HDFC", use_container_width=True):
            fake_user = st.session_state.generator.generate_user_profile()
            fraud_tx = st.session_state.generator.generate_transaction(fake_user, is_fraud=True)
            # DIVERSIFIED HDFC ATTACK: Randomize amount and time
            fraud_tx["amount"] = random.uniform(15000.0, 30000.0)
            fraud_tx["is_night_txn"] = random.choice([True, False, True]) # Weighted slightly towards night
            from src.fraud_engine import FraudDetector as FD
            hdfc_detector = FD(bank_id="HDFC_BANK")
            hdfc_detector.publish_knowledge(fraud_tx)
            st.success("Network Alert: HDFC published a new block.")
            st.rerun()

    if st.button("Wipe Global Ledger", type="secondary", use_container_width=True):
        st.session_state.detector.ledger.reset_ledger()
        st.rerun()

    st.button("Reset Environment", key="reset_env", on_click=lambda: st.session_state.update({"history": [], "detector": FraudDetector()}))

# Main Dashboard
col1, col2 = st.columns([1.8, 1.2], gap="large")

with col1:
    st.subheader("Live Transaction Feed")
    
    if st.session_state.history:
        for idx, row in enumerate(st.session_state.history):
            if row["decision"] == "APPROVED":
                color = "#00E5FF"
                icon = "shield"
                icon_class = "icon-teal"
            elif row["decision"] == "REVIEW":
                color = "#FFAA00"
                icon = "search"
                icon_class = "icon-amber"
            else:
                color = "#FF3B30"
                icon = "gpp_maybe"
                icon_class = "icon-red"
            
            txn_html = f"""<div class="activity-card" style="border-left: 4px solid {color};">
<div style="display: flex; justify-content: space-between; align-items: flex-start;">
    <div style="display: flex; align-items: flex-start;">
        <span class="material-symbols-outlined {icon_class}" style="margin-top: 4px;">{icon}</span>
        <div>
            <div style="font-weight: 700; color: #FFFFFF; font-size: 1.1rem;">{row['merchant']}</div>
            <div style="font-size: 0.8rem; color: #BBB; margin-top: 2px; display: flex; align-items: center;">
                {row['category']} 
                <span style="margin: 0 8px;">•</span>
                {row['city']}, {row['country']}
            </div>
        </div>
    </div>
    <div style="text-align: right;">
        <div style="font-family: monospace; font-weight: 700; color: #FFFFFF; font-size: 1.1rem;">₹{row['amount']:.2f}</div>
        <div style="font-size: 0.75rem; font-weight: 800; color: {color}; letter-spacing: 0.5px; text-transform: uppercase;">{row['decision']}</div>
    </div>
</div>
</div>"""
            st.markdown(txn_html, unsafe_allow_html=True)
                
            if row.get("rule_based_reasons"):
                with st.expander("Analysis Details"):
                    if row.get("rule_based_reasons"):
                        for r in (row["rule_based_reasons"] if isinstance(row["rule_based_reasons"], list) else [row["rule_based_reasons"]]):
                            color = "#7B61FF" if "Federated" in r else "#AAA"
                            st.markdown(f'<div style="color:{color}; font-size:0.85rem; border-left: 2px solid {color}; padding-left: 8px; margin-bottom: 4px;">• {r}</div>', unsafe_allow_html=True)
    else:
        st.info("System Ready. Generate activity to begin monitoring.")

with col2:
    st.subheader("Digital Twin Brain")
    twin = st.session_state.detector.get_or_create_twin(st.session_state.user_persona["user_id"])
    
    with st.container():
        m1, m2 = st.columns(2)
        m1.metric("Local IQ", f"{min(100, twin.profile['transaction_count']*5)}%", help="Confidence based on your local history")
        m2.metric("Global Wisdom", "Synced", delta="ACTIVE", help="Connected to Blockchain Federated Network")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Behavior", "Sequence", "Ledger", "Network"])
    
    with tab1:
        st.markdown('### <span class="material-symbols-outlined">psychology</span> Behavioral Identity Profile', unsafe_allow_html=True)
        
        if not st.session_state.history:
            st.info("Twin is in 'Observation Mode'. Generate transactions to see real-time analysis.")


        # 2. Financial DNA (Spend & Volatility)
        avg_amt = twin.profile.get('avg_amount', 0)
        std_dev = twin.profile.get('std_dev_amount', 0)
        tx_count = twin.profile.get('transaction_count', 0)
        
        if tx_count == 0:
            volatility = "Learning"
        elif tx_count == 1:
            volatility = "Stable"
        else:
            volatility = "Stable" if std_dev < avg_amt * 0.4 else "Dynamic"
        
        st.markdown("**🛡️ Financial Profile**")
        i1, i2 = st.columns(2)
        i1.metric("AVERAGE SPENDING", f"₹{avg_amt:.0f}")
        i2.metric("SPENDING VOLATILITY", volatility, delta=f"Index: {std_dev:.1f}" if tx_count > 0 else None)

        st.markdown("---")

        # 4. Category DNA (Distribution)
        st.markdown("**📊 Category Distribution**")
        if twin.profile.get('frequent_categories'):
            st.bar_chart(twin.profile['frequent_categories'], color="#7B61FF")
        else:
            st.info("Twin is populating categorical spending patterns...")
        
    with tab2:
        st.markdown('### <span class="material-symbols-outlined">account_tree</span> Sequence Insights', unsafe_allow_html=True)
        if twin.transition_probs:
            habit_stories = []
            
            for src, targets_dict in twin.transition_probs.items():
                total_for_src = sum(targets_dict.values())
                for target, count in targets_dict.items():
                    # Store data for habit analysis
                    prob = (count / total_for_src) * 100
                    if prob > 30 and total_for_src > 2:
                         habit_stories.append((src, target, prob))

            # Behavioral Habits (Story Telling Section)
            if habit_stories:
                 # Sort by probability
                 habit_stories.sort(key=lambda x: x[2], reverse=True)
                 for src, dest, prob in habit_stories[:3]:
                      st.markdown(f"""
                      <div style="background-color: #7B61FF11; border-left: 3px solid #7B61FF; padding: 12px; margin-bottom: 12px; border-radius: 8px;">
                      <div style="display: flex; align-items: center; margin-bottom: 4px;">
                        <span class="material-symbols-outlined icon-small" style="margin-right: 8px;">history</span>
                        <span style="color: #888; font-size: 0.8rem;">RECURRING HABIT</span>
                      </div>
                      <span style="font-size: 1.1rem; color: #FFFFFF;"><b>{src.upper()}</b> <span class="material-symbols-outlined icon-small" style="color: #888;">east</span> <b>{dest.upper()}</b></span>
                      <br><span style="color: #7B61FF; font-size: 0.9rem;">{prob:.0f}% likelihood of this sequence</span>
                      </div>
                      """, unsafe_allow_html=True)
            else:
                 st.info("The Digital Twin is currently observing your transactions to map behavioral sequences. Keep generating activity to see learning results.")
        else:
            st.info("No sequences recorded. The Digital Twin requires more transaction history to identify your behavioral habits.")

    with tab3:
        st.markdown('### <span class="material-symbols-outlined">storage</span> Global Knowledge Ledger', unsafe_allow_html=True)
        
        # Federated Wisdom Visualization
        wisdom = st.session_state.detector.ledger.get_global_wisdom(bft_mechanism="median")
        if wisdom.get("behavior"):
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1A1A1A 0%, #111111 100%); border: 1px solid #7B61FF44; border-radius: 12px; padding: 20px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(123, 97, 255, 0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <div style="display: flex; align-items: center;">
                        <span class="material-symbols-outlined" style="color: #7B61FF; margin-right: 10px;">public</span>
                        <h4 style="margin: 0; color: #FFFFFF; font-size: 1.1rem; letter-spacing: 0.5px;">FEDERATED GLOBAL WISDOM</h4>
                    </div>
                    <div style="background-color: #00E5FF22; border: 1px solid #00E5FF; padding: 3px 10px; border-radius: 12px; display: flex; align-items: center;">
                        <span class="material-symbols-outlined icon-small" style="color: #00E5FF; font-size: 14px;">verified_user</span>
                        <span style="color: #00E5FF; font-size: 0.7rem; font-weight: 800; letter-spacing: 0.5px;">BFT SECURED</span>
                    </div>
                </div>
                <p style="color: #AAAAAA; font-size: 0.8rem; margin-top: -5px; margin-bottom: 15px;"><i>Weights strictly aggregated via <b>Byzantine Fault Tolerance (Median)</b> to automatically reject Model Poisoning attacks.</i></p>
            """, unsafe_allow_html=True)
            
            for feature, weight in wisdom["behavior"].items():
                label = feature.replace("_", " ").title()
                percentage = weight * 100
                st.markdown(f"""
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span style="color: #BBBBBB; font-size: 0.85rem; font-weight: 600;">{label}</span>
                        <span style="color: #7B61FF; font-weight: 800; font-size: 0.9rem;">{percentage:.0f}% Risk Boost</span>
                    </div>
                    <div style="background-color: #222; height: 6px; border-radius: 3px; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, #7B61FF 0%, #00E5FF 100%); width: {percentage}%; height: 100%; border-radius: 3px; box-shadow: 0 0 10px #7B61FF66;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        ledger_data = st.session_state.detector.ledger.read_all_blocks()
        if ledger_data:
            for block in reversed(ledger_data):
                with st.container(border=True):
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; padding-bottom: 8px; margin-bottom: 8px;">
                        <span style="color: #888; font-size: 0.8rem;"><span class="material-symbols-outlined icon-small">inventory_2</span> Block #{block['index']}</span>
                        <span style="color: #7B61FF; font-weight: 700;">{block['bank_id']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    summary = "• Shared Behavioral Intelligence:\n"
                    if "model_weights" in block:
                        for feature, val in block["model_weights"].items():
                            feature_name = feature.replace("_", " ").title()
                            summary += f"  - {feature_name}: {val*100:.0f}%\n"
                    else:
                        summary += "  - Knowledge sync complete"
                    
                    st.code(summary.strip(), language="text")
        else:
            st.info("Ledger synchronized.")

    with tab4:
        st.markdown('### <span class="material-symbols-outlined">hub</span> Social Trust Network', unsafe_allow_html=True)
        
        # Explain weighted risk
        with st.expander("How does this work?", expanded=False):
            st.info("""
            **Weighted Risk Scoring:**
            In the real world, you pay new people often. The Digital Twin knows this! 
            
            Being a 'New Recipient' only adds **+0.4** to the risk score. For a transaction to be actually 'Declined' (Score > 0.8), *other* things must also be wrong (e.g., unusual amount or impossible travel).
            """)

        # Generate Graph Data
        trusted = list(twin.trusted_recipients)
        nodes_x = [0] # Self at center
        nodes_y = [0]
        node_text = ["<b>YOU</b>"]
        node_colors = ["#7B61FF"]
        
        edge_x = []
        edge_y = []
        
        # Add trusted nodes in a circle
        for i, tid in enumerate(trusted[:10]): # Limit to top 10 for clarity
            angle = (i / min(len(trusted), 10)) * 2 * math.pi
            x, y = math.cos(angle), math.sin(angle)
            nodes_x.append(x)
            nodes_y.append(y)
            node_text.append(f"Trusted ID: ...{str(tid)[-6:]}")
            node_colors.append("#00E5FF")
            
            edge_x.extend([0, x, None])
            edge_y.extend([0, y, None])
            
        fig = go.Figure()
        
        # Add Edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#333'),
            hoverinfo='none',
            mode='lines'
        ))
        
        # Add Nodes
        fig.add_trace(go.Scatter(
            x=nodes_x, y=nodes_y,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            hoverinfo='text',
            marker=dict(
                size=[30] + [15]*len(trusted),
                color=node_colors,
                line_width=2,
                line_color='#FFF'
            )
        ))
        
        fig.update_layout(
            showlegend=False,
            margin=dict(b=0,l=0,r=0,t=0),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=300
        )
        
        st.plotly_chart(fig, width="stretch")
        st.caption(f"Currently tracking {len(trusted)} trusted transfer relationships.")
