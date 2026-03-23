"""
Streamlit Dashboard for Cross-Platform Algorithm Comparison
Supports: Search, RNG, and Game algorithms
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys
import time
import matplotlib.pyplot as plt

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import config
from core.comparator import ExperimentComparator
from utils.helpers import get_device_info, set_seed

# Page configuration
st.set_page_config(
    page_title="Algo Comparison",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #3498db 0%, #2ecc71 50%, #e74c3c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
    }
    .metric-card {
        padding: 1rem;
        border-radius: 8px;
        background-color: #f0f2f6;
        border-left: 5px solid #3498db;
    }
    .stButton>button {
        width: 100%;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'results_history' not in st.session_state:
    st.session_state.results_history = []
if 'last_result' not in st.session_state:
    st.session_state.last_result = None

def display_sidebar():
    """Display sidebar controls"""
    st.sidebar.title("⚙️ Experiment Settings")
    
    # System Info
    st.sidebar.markdown("### 💻 System Info")
    device_info = get_device_info()
    st.sidebar.markdown(f"**CPU:** {device_info.get('cpu_count')} Threads")
    if device_info.get('gpu_available'):
        backend = device_info.get('gpu_backend', 'CUDA')
        st.sidebar.markdown(f"**GPU:** {device_info.get('gpu_name')} `({backend})`")
        if device_info.get('gpu_vram_mb'):
            st.sidebar.markdown(f"**VRAM:** {device_info.get('gpu_vram_mb')} MB")
    else:
        st.sidebar.warning("GPU not available (Using CPU fallback)")
        
    st.sidebar.markdown("---")
    
    # Algorithm Selection
    st.sidebar.markdown("### 🧠 Algorithm")
    algorithm = st.sidebar.selectbox(
        "Select Algorithm",
        ["Search", "RNG", "Game"],
        index=0
    )
    
    params = {'algorithm': algorithm}
    
    if algorithm == "Search":
        st.sidebar.markdown("### 🔍 Search Params")
        params['size'] = st.sidebar.select_slider(
            "Database Size (N)",
            options=[100, 500, 1000, 5000, 10000, 50000, 100000, 500000],
            value=1000
        )
        params['target'] = st.sidebar.number_input(
            "Target Position (Optional)",
            min_value=0, max_value=params['size']-1, value=None, placeholder="Random"
        )
        
    elif algorithm == "RNG":
        st.sidebar.markdown("### 🎲 RNG Params")
        params['count'] = st.sidebar.select_slider(
            "Numbers to Generate",
            options=[100, 1000, 5000, 10000, 50000, 100000, 500000],
            value=1000
        )
        params['qubits'] = st.sidebar.slider("Qubits (Range 2^n)", 2, 10, 5)
        
    elif algorithm == "Game":
        st.sidebar.markdown("### 🎮 Game Params")
        params['games'] = st.sidebar.slider("Number of Games", 1, 50, 10)
        params['shots'] = st.sidebar.slider("Quantum Shots", 100, 2048, 1024)
        
    params['seed'] = st.sidebar.number_input("Random Seed", value=42)
    
    return params

def run_experiment(params):
    """Run experiment based on params"""
    set_seed(params['seed'])
    
    algorithm = params['algorithm']
    results = {}
    
    status = st.empty()
    progress = st.progress(0)
    
    if algorithm == "Search":
        from algorithms.search_algorithm import SearchAlgorithm
        status.text(f"Running Search (N={params['size']})...")
        progress.progress(20)
        
        runner = SearchAlgorithm(database_size=params['size'], target_position=params['target'])
        results = runner.run_comparison(monitor=True)
        results['type'] = 'Search'
        
    elif algorithm == "RNG":
        from algorithms.rng_algorithm import RNGAlgorithm
        status.text(f"Running RNG (Count={params['count']})...")
        progress.progress(20)
        
        runner = RNGAlgorithm(count=params['count'], num_qubits=params['qubits'])
        results = runner.run_comparison()
        results['type'] = 'RNG'
        
    elif algorithm == "Game":
        from algorithms.game_algorithm import GameAlgorithm
        status.text(f"Running Tic-Tac-Toe ({params['games']} games)...")
        progress.progress(20)
        
        runner = GameAlgorithm(num_games=params['games'], shots=params['shots'])
        results = runner.run_comparison()
        results['type'] = 'Game'
    
    progress.progress(100)
    status.text("Completed!")
    time.sleep(0.5)
    status.empty()
    progress.empty()
    
    return results

def create_chart(results, metric_type="Time"):
    """Create chart for specific metric"""
    platforms_data = results.get('platforms', {})
    data = []
    
    algo_type = results.get('type')
    
    for platform, res in platforms_data.items():
        if 'error' in res: continue
        
        val = 0
        if metric_type == "Time":
            val = res.get('search_time') or res.get('generation_time') or res.get('time_seconds') or 0
            y_label = "Time (seconds) [Lower is Better]"
            title = f"{algo_type} Execution Time"
            
        elif metric_type == "Memory":
            # For QPU, convert Qubits to a representative value if MB is missing, but bars usually MB
            val = res.get('peak_memory_mb') or res.get('memory_used_mb') or 0
            if val == 0 and 'num_qubits' in res: val = res['num_qubits'] # fallback for bar
            
            y_label = "Memory (MB/Qubits) [Lower is Better]"
            title = f"{algo_type} Memory Usage"
            
        elif metric_type == "Performance":
            val = res.get('items_per_second') or res.get('numbers_per_second') or res.get('games_per_second') or 0
            # For QPU rate calc if missing
            if val == 0 and 'time_seconds' in res and res['time_seconds'] > 0:
                if algo_type == 'Game': val = res.get('games_played', 0) / res['time_seconds']
                
            if algo_type == 'Search': y_label = "Items / Second [Higher is Better]"
            elif algo_type == 'RNG': y_label = "Numbers / Second [Higher is Better]"
            elif algo_type == 'Game': y_label = "Games / Second [Higher is Better]"
            title = f"{algo_type} Throughput"
            
        data.append({'Platform': platform, 'Metric': val})
        
    if not data: return None
    
    df = pd.DataFrame(data)
    fig = px.bar(df, x='Platform', y='Metric', title=title,
                 color='Platform', text_auto='.4s')
    fig.update_layout(yaxis_title=y_label)
    return fig

def display_results(results):
    """Display experiment results"""
    if not results: return

    st.markdown(f"### 📊 {results.get('type', 'Experiment')} Results")
    
    platforms = results.get('platforms', {})
    cpu = platforms.get('CPU', {})
    gpu = platforms.get('GPU', {})
    qpu = platforms.get('QPU', {})
    
    # Metric Extraction Helpers
    def get_val(data, keys, fmt="{:.4f}"):
        if 'error' in data: return "Error"
        for k in keys:
            if k in data and data[k] is not None: return fmt.format(data[k])
        return "N/A"

    def get_algo_desc(platform, algo_type):
        if algo_type == 'Search':
            return "Linear Search" if platform == 'CPU' else "Parallel Search" if platform == 'GPU' else "Grover's Search"
        elif algo_type == 'RNG':
            return "Pseudo-RNG" if platform == 'CPU' else "Parallel RNG" if platform == 'GPU' else "True Quantum RNG"
        elif algo_type == 'Game':
            return "Classical Random" if platform == 'CPU' else "Parallel Sim" if platform == 'GPU' else "Quantum Move"
        return ""
    
    # 1. Cards View
    c1, c2, c3 = st.columns(3)
    
    metrics_map = {
        'Time': ['search_time', 'generation_time', 'time_seconds'],
        'Memory': ['peak_memory_mb', 'memory_used_mb'],
        'Rate': ['items_per_second', 'numbers_per_second', 'games_per_second']
    }
    
    with c1:
        st.markdown(f"#### 🖥️ CPU: {get_algo_desc('CPU', results['type'])}")
        if 'error' in cpu: st.error(cpu['error'])
        else:
            st.metric("Time", get_val(cpu, metrics_map['Time'], "{:.5f}s"))
            st.metric("Memory", get_val(cpu, metrics_map['Memory'], "{:.1f} MB"))
            st.metric("Performance", get_val(cpu, metrics_map['Rate'], "{:,.0f}/s"))
                
    with c2:
        st.markdown(f"#### 🎮 GPU: {get_algo_desc('GPU', results['type'])}")
        if 'error' in gpu: st.error(gpu['error'])
        else:
            st.metric("Time", get_val(gpu, metrics_map['Time'], "{:.5f}s"))
            st.metric("Memory", get_val(gpu, metrics_map['Memory'], "{:.1f} MB"))
            st.metric("Performance", get_val(gpu, metrics_map['Rate'], "{:,.0f}/s"))
            
    with c3:
        st.markdown(f"#### ⚛️ QPU: {get_algo_desc('QPU', results['type'])}")
        if 'error' in qpu: st.error(qpu['error'])
        else:
            st.metric("Time", get_val(qpu, metrics_map['Time'], "{:.5f}s"))
            
            # Universal rate display for QPU
            rate_val_raw = qpu.get('items_per_second') or qpu.get('numbers_per_second') or qpu.get('games_per_second')
            if rate_val_raw is None or rate_val_raw == 0:
                # Fallback calculation
                duration = qpu.get('search_time') or qpu.get('generation_time') or qpu.get('time_seconds') or 0
                count = qpu.get('database_size') or qpu.get('count') or qpu.get('games_played') or 0
                rate_val_raw = count / duration if duration > 0 else 0
            
            st.metric("Performance", f"{rate_val_raw:,.1f}/s" if rate_val_raw > 0 else "N/A")
            
            # Qubits for Memory
            if 'num_qubits' in qpu:
                 st.metric("Memory", f"{qpu['num_qubits']} Qubits")
            elif 'qubits' in qpu: 
                 st.metric("Memory", f"{qpu['qubits']} Qubits")
            else:
                 st.metric("Memory", get_val(qpu, metrics_map['Memory'], "{:.1f} MB"))
            
            if results['type'] == 'Search':
                st.caption(f"Prob: {qpu.get('success_probability', 0):.1%}")

    st.markdown("---")
    
    # 2. Charts View with Tabs
    st.markdown("### 📈 Visual Comparison")
    
    tab1, tab2, tab3 = st.tabs(["⏱️ Time", "💾 Memory", "🚀 Performance"])
    
    with tab1:
        fig1 = create_chart(results, "Time")
        if fig1: st.plotly_chart(fig1, use_container_width=True)
        
    with tab2:
        fig2 = create_chart(results, "Memory")
        if fig2: st.plotly_chart(fig2, use_container_width=True)
        else: st.info("No memory usage data available for this run.")
        
    with tab3:
        fig3 = create_chart(results, "Performance")
        if fig3: st.plotly_chart(fig3, use_container_width=True)
        
    # Raw Data
    with st.expander("View Raw JSON Data"):
        st.json(results)

def main():
    """Main application"""
    
    # Header
    st.markdown('<h1 class="main-header">⚡ Cross-Platform Algorithm Comparison</h1>', unsafe_allow_html=True)
    st.markdown("Compare **CPU** vs **GPU** vs **QPU** Performance across different algorithms")
    
    params = display_sidebar()
    
    if st.sidebar.button("🚀 Run Comparison", type="primary"):
        results = run_experiment(params)
        st.session_state.last_result = results
        st.session_state.results_history.append(results)
        
    if st.session_state.last_result:
        display_results(st.session_state.last_result)
    else:
        st.info("👈 Select an **Algorithm** and configure settings in the sidebar.")
        
        st.markdown("---")
        st.markdown("### 📚 Algorithms")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("#### 🔍 Search")
            st.markdown("Find item in unstructured list.")
            st.markdown("*CPU: O(N) | GPU: O(N/P) | QPU: O(√N)*")
        with c2:
            st.markdown("#### 🎲 RNG")
            st.markdown("Generate random numbers.")
            st.markdown("*Classical vs Parallel vs True Quantum*")
        with c3:
            st.markdown("#### 🎮 Game")
            st.markdown("Tic-Tac-Toe Move Selection.")
            st.markdown("*Random vs Simulation vs Quantum Logic*")

if __name__ == "__main__":
    main()
