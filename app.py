# app.py
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
from algorithms.closest_pair import parse_points_file_content, closest_pair
from algorithms.karatsuba import parse_integers_file_content, karatsuba_steps


st.set_page_config(page_title="D&C Visualizer", layout="wide")

# ----- Sidebar / Header styling -----
st.markdown(
    """
    <style>
    /* Import Poppins font from Google Fonts - more distinctive and modern */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Apply Poppins font to all elements */
    * {
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    /* Enhanced gradient background for the whole page - more visible */
    .stApp {
        background: linear-gradient(135deg, #1F1B18 0%, #2A2521 25%, #3A332E 50%, #2A2521 75%, #1F1B18 100%);
        background-size: 200% 200%;
        animation: gradientShift 15s ease infinite;
        color: #E8DCC2;
        font-family: 'Poppins', sans-serif !important;
    }
    
    @keyframes gradientShift {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }
    
    .sidebar .sidebar-content { 
        background-color: #2A2521; 
        font-family: 'Poppins', sans-serif !important;
    }
    
    .css-1d391kg { 
        color:#E8DCC2;
        font-family: 'Poppins', sans-serif !important;
    } /* headers */
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    /* Button animations */
    .stButton > button {
        transition: all 0.3s ease;
        transform: translateY(0);
        font-family: 'Poppins', sans-serif !important;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(203, 178, 138, 0.3);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Container animations */
    [data-testid="stFileUploader"] {
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        transform: scale(1.02);
    }
    
    /* Radio button animations */
    .stRadio > div > label {
        transition: all 0.2s ease;
        font-family: 'Poppins', sans-serif !important;
    }
    
    .stRadio > div > label:hover {
        color: #FFD580;
        transform: translateX(5px);
    }
    
    /* Checkbox animations */
    .stCheckbox > label {
        transition: all 0.2s ease;
        font-family: 'Poppins', sans-serif !important;
    }
    
    .stCheckbox > label:hover {
        color: #FFD580;
    }
    
    /* Slider animations */
    .stSlider {
        transition: all 0.3s ease;
    }
    
    /* Text area animations */
    .stTextArea > div > div > textarea {
        transition: all 0.3s ease;
        font-family: 'Poppins', sans-serif !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        transform: scale(1.01);
        box-shadow: 0 0 10px rgba(203, 178, 138, 0.3);
    }
    
    /* Input fields */
    input, select, textarea {
        font-family: 'Poppins', sans-serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# App title
st.markdown("<h1 style='font-family: Poppins, sans-serif; font-weight: 600; color:#E8DCC2; letter-spacing: 0.5px;'>Divide & Conquer Visualizer</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#CBB28A; font-family: Poppins, sans-serif;'>visual explanation of Closest Pair & Karatsuba Multiplication.</p>", unsafe_allow_html=True)

# Main layout: left controls, right visualization
left_col, right_col = st.columns([1,2], gap="large")

with left_col:
    st.subheader("Input Options")
    upload = st.file_uploader("Option 01: Upload input file (txt)", type=['txt'])
    st.write("Supported formats:")
    st.markdown("""
    - **Closest Pair**: lines `x y` or first line `N` then `N` lines of `x y`  
    - **Integer Multiplication**: lines `a b` or a single line `a b`  
    """, unsafe_allow_html=True)

    algo = st.radio("Choose algorithm", ("Closest Pair (points)", "Integer Multiplication (Karatsuba)"),
                    index=0, key="algo_choice")

    run_button = st.button("Begin Visualization", use_container_width=True)

    st.markdown("---")
    st.subheader("Display Options")
    show_steps = st.checkbox("Show textual steps while visualizing", value=True)
    delay = st.slider("Animation delay (seconds/frame)", 0.05, 1.0, 0.25, 0.05)

    st.markdown("---")
    st.markdown("**Sample files**: Option 02: Paste text below and press Begin.")
    contents_box = st.text_area("Paste input file content (optional)", height=160)

    # helper to read uploaded or pasted content
    def get_file_content():
        if upload is not None:
            try:
                raw = upload.read().decode('utf-8')
                return raw
            except Exception as e:
                st.error("Could not read file. Paste content in the box instead.")
                return None
        else:
            return contents_box if contents_box.strip() else None

with right_col:
    st.subheader("Visualization")
    viz_placeholder = st.empty()
    steps_placeholder = st.empty()
    info_placeholder = st.empty()

# Utility: small plotting helpers
def plot_points(points, highlights=None, split_x=None, title=None):
    fig, ax = plt.subplots(figsize=(6,6))
    ax.set_facecolor("#F5E6D3")  
    ax.tick_params(colors="#6B4C3B")  
    ax.spines['bottom'].set_color('#6B4C3B')  
    ax.spines['left'].set_color('#6B4C3B')
    ax.spines['top'].set_color('#F5E6D3')  
    ax.spines['right'].set_color('#F5E6D3')  
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    ax.scatter(xs, ys, s=30, c='#CBB28A', edgecolors='#8C6A4A', linewidths=0.6)
    if highlights:
        ax.scatter([highlights[0][0], highlights[1][0]],
                   [highlights[0][1], highlights[1][1]],
                   s=80, c='#FFD580', edgecolors='#D4A373', linewidths=1.2)
        ax.plot([highlights[0][0], highlights[1][0]], [highlights[0][1], highlights[1][1]], color='#FFD580', linewidth=1.5)
    if split_x is not None:
        ax.axvline(split_x, color='#6B4C3B', linestyle='--', linewidth=1)
    if title:
        ax.set_title(title, color="#6B4C3B", fontfamily='Poppins', fontweight=500) 
    plt.tight_layout()
    return fig

def visualize_closest_pair(content: str, visualize=False):
    pts = parse_points_file_content(content)
    if len(pts) < 2:
        st.warning("Need at least 2 points.")
        return

    # Option to subsample if file too large for animation
    max_points = 200
    if len(pts) > max_points:
        st.info(f"Too many points for step-by-step animation ({len(pts)}). Subsampling to {max_points}.")
        pts = pts[:max_points]

    gen = closest_pair(pts, visualize=True)

    last_highlight = None
    # step loop
    for step in gen:
        if show_steps:
            steps_placeholder.markdown("### Steps")
        if step['type'] == 'split':
            # plot points and split line
            fig = plot_points(pts, highlights=None, split_x=step['x'], title=f"Splitting at x={step['x']:.2f}")
            viz_placeholder.pyplot(fig)
            if show_steps:
                steps_placeholder.write(f"Split at x = **{step['x']:.3f}** into left ({len(step['left'])}) / right ({len(step['right'])})")
        elif step['type'] == 'bruteforce':
            fig = plot_points(step['points'], title="Brute force block (small set)")
            viz_placeholder.pyplot(fig)
            if show_steps:
                steps_placeholder.write(f"Brute force on {len(step['points'])} points. Best = **{step['best']:.4f}**")
        elif step['type'] == 'compare':
            fig = plot_points(pts, highlights=step['pair'], title=f"Comparing pair dist={step['dist']:.4f}")
            viz_placeholder.pyplot(fig)
            if show_steps:
                steps_placeholder.write(f"Comparing points: {step['pair'][0]} and {step['pair'][1]} → d = **{step['dist']:.4f}**")
        elif step['type'] == 'strip':
            fig = plot_points(pts, highlights=step['pair'], split_x=step['x'], title=f"Strip check, best = {step['best']:.4f}")
            viz_placeholder.pyplot(fig)
            if show_steps:
                steps_placeholder.write(f"Strip around x={step['x']:.3f}, strip size={len(step['strip'])}, current best={step['best']:.4f}")
        elif step['type'] == 'result':
            fig = plot_points(pts, highlights=step['pair'], title=f"Final: d={step['best']:.4f}")
            viz_placeholder.pyplot(fig)
            if show_steps:
                steps_placeholder.write(f"**Result**: closest pair = {step['pair']} with distance **{step['best']:.4f}**")
        else:
            # fallback
            viz_placeholder.write(step)
        time.sleep(delay)

    info_placeholder.markdown("### Visualization complete")

def visualize_karatsuba(content, viz_placeholder, steps_placeholder, info_placeholder, delay):
    try:
        x, y = parse_integers_file_content(content)
    except Exception as e:
        st.error(f"Error parsing input: {e}")
        return

    viz_placeholder.markdown(f"### Visualizing Karatsuba: **{x} × {y}**")

    gen = karatsuba_steps(x, y)
    history = []

    for step in gen:

        if step["type"] == "base":
            viz_placeholder.markdown(
                f"**Base case:** {step['x']} × {step['y']} = **{step['product']}**"
            )

        elif step["type"] == "split":
            viz_placeholder.markdown(
                f"**Split Step:**<br>"
                f"x={step['x']} → ({step['high_x']}, {step['low_x']})<br>"
                f"y={step['y']} → ({step['high_y']}, {step['low_y']})",
                unsafe_allow_html=True
            )

        elif step["type"] == "combine":
            viz_placeholder.markdown(
                f"**Combine Step:**<br>"
                f"z2={step['z2']}, z1={step['z1']}, z0={step['z0']} → product={step['product']}",
                unsafe_allow_html=True
            )

        history.append(step)
        if steps_placeholder:
            steps_placeholder.write(history)

        time.sleep(delay)

    info_placeholder.markdown(f"### Final product: **{x * y}**")

# -------------------- MAIN EVENT HANDLER --------------------

if run_button:
    content = get_file_content()

    if not content:
        st.error("Please upload a file or paste the content.")
    else:
        if algo == "Closest Pair (points)":
            visualize_closest_pair(content)

        elif algo == "Integer Multiplication (Karatsuba)":
            visualize_karatsuba(
                content,
                viz_placeholder,
                steps_placeholder,
                info_placeholder,
                delay
            )

