import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- Config ----------------
st.set_page_config(page_title="Анализ экспериментов", layout="wide", page_icon="🔬")

# ---------------- Styles: Dark Theme ----------------
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    h1 { background: linear-gradient(to right, #00bfff, #be5bf7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    h2, h3 { color: #e6e6e6; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #1c2533; border-radius: 5px; color: white; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #00bfff; color: black; }
    
    .metric-box {
        background-color: #1c2533;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #00bfff;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Функция для настройки темных графиков
def set_dark_plot_style(ax, title, xlabel, ylabel):
    ax.set_facecolor('#0e1117')
    ax.figure.set_facecolor('#0e1117')
    ax.spines['bottom'].set_color('#ffffff')
    ax.spines['top'].set_color('#ffffff') 
    ax.spines['right'].set_color('#ffffff')
    ax.spines['left'].set_color('#ffffff')
    ax.tick_params(axis='x', colors='#ffffff')
    ax.tick_params(axis='y', colors='#ffffff')
    ax.yaxis.label.set_color('#ffffff')
    ax.xaxis.label.set_color('#ffffff')
    ax.title.set_color('#ffffff')
    ax.set_title(title, fontsize=12, pad=10)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle='--', alpha=0.2)
    ax.legend(facecolor='#1c2533', labelcolor='white', framealpha=1)

# ---------------- Main App ----------------
st.title("🔬 Сравнительный Анализ Экспериментов")

st.markdown("""
<div class="metric-box">
    <b>Цель анализа:</b> Сравнение динамики сквашивания (pH) для трех групп: 
    <b>Контроль</b> (традиционная технология), 
    <b>Опыт 1</b> (Добавка 1 до 3%) и 
    <b>Опыт 2</b> (Добавка 2 до 4%).
</div>
""", unsafe_allow_html=True)

# --- Данные и уравнения (из Отчета) ---
t = np.linspace(2, 10, 100)

# Уравнения регрессии
ph_control = 4.605 - 0.125 * np.log(t)
ph_exp1 = 4.535 - 0.102 * np.log(t)
ph_exp2 = 4.506 - 0.125 * np.log(t)

# --- Вкладки ---
tab1, tab2, tab3 = st.tabs(["📊 Общее сравнение", "🧪 Опыт 1 (Стабилизация)", "🔥 Опыт 2 (Ускорение)"])

# === TAB 1: СРАВНЕНИЕ ===
with tab1:
    st.header("Динамика pH: Контроль vs Опыты")
    
    col_gr, col_txt = st.columns([2, 1])
    
    with col_gr:
        fig, ax = plt.subplots(figsize=(10, 6))
        set_dark_plot_style(ax, "Кривые сквашивания", "Время (ч)", "pH")
        
        ax.plot(t, ph_control, label="Контроль", color="#00bfff", linewidth=2.5) # Синий
        ax.plot(t, ph_exp1, label="Опыт 1 (Добавка 1)", color="#00ff88", linewidth=2.5, linestyle="--") # Зеленый
        ax.plot(t, ph_exp2, label="Опыт 2 (Добавка 2)", color="#ff4b4b", linewidth=2.5, linestyle="-.") # Красный
        
        # Линия готовности
        ax.axhline(y=4.6, color='yellow', alpha=0.5, linestyle=':', label='pH = 4.6 (Конец)')
        ax.legend(facecolor='#1c2533', labelcolor='white')
        
        st.pyplot(fig)
        
    with col_txt:
        st.subheader("Выводы")
        st.info("🔹 **Контроль:** Стандартная динамика. Умеренное снижение pH.")
        st.success("🌿 **Опыт 1 (Зеленая):** Более плавное падение. Добавка «смягчает» процесс, позволяя точнее поймать точку готовности.")
        st.error("🔥 **Опыт 2 (Красная):** Резкое падение. Добавка ускоряет закисление. Требует строгого контроля времени.")

    st.markdown("---")
    st.subheader("📋 Расчетная таблица (Прогноз)")
    
    # Генерируем таблицу динамически по формулам
    check_points = [2, 4, 6, 8, 10]
    data_table = []
    for h in check_points:
        log_t = np.log(h)
        data_table.append({
            "Время (ч)": h,
            "Контроль pH": round(4.605 - 0.125 * log_t, 3),
            "Опыт 1 pH": round(4.535 - 0.102 * log_t, 3),
            "Опыт 2 pH": round(4.506 - 0.125 * log_t, 3)
        })
    
    st.dataframe(pd.DataFrame(data_table), use_container_width=True)

# === TAB 2: ОПЫТ 1 ===
with tab2:
    st.header("Опыт 1: Добавка 1 (до 3%)")
    st.caption("Эффект: Стабилизация кислотности")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Регрессионная модель")
        st.latex(r"pH = 4.535 - 0.102 \cdot \ln(t)")
        st.metric("R² (Точность)", "0.973")
        st.success("✅ Модель подтверждает более пологий наклон кривой (коэф. -0.102 против -0.125 у контроля).")
        
    with c2:
        # Индивидуальный график
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        set_dark_plot_style(ax2, "Модель Опыта 1", "Время", "pH")
        ax2.plot(t, ph_exp1, color="#00ff88", linewidth=3)
        ax2.fill_between(t, ph_exp1, 4.2, color="#00ff88", alpha=0.1)
        st.pyplot(fig2)

# === TAB 3: ОПЫТ 2 ===
with tab3:
    st.header("Опыт 2: Добавка 2 (до 4%)")
    st.caption("Эффект: Интенсификация процесса")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Регрессионная модель")
        st.latex(r"pH = 4.506 - 0.125 \cdot \ln(t)")
        st.metric("R² (Точность)", "0.997")
        st.error("⚡ Самая высокая скорость ферментации. Целевой pH достигается быстрее.")
        
    with c2:
        # Индивидуальный график
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        set_dark_plot_style(ax3, "Модель Опыта 2", "Время", "pH")
        ax3.plot(t, ph_exp2, color="#ff4b4b", linewidth=3)
        ax3.fill_between(t, ph_exp2, 4.2, color="#ff4b4b", alpha=0.1)
        st.pyplot(fig3)