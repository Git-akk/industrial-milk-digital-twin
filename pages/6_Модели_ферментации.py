import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# ---------------- Config ----------------
st.set_page_config(page_title="3D Моделирование", layout="wide", page_icon="🧊")

# ---------------- Styles: Premium Dark ----------------
st.markdown("""
<style>
    /* Общий фон */
    .stApp { background-color: #0e1117; color: white; }
    
    /* Заголовки */
    h1 { 
        background: linear-gradient(to right, #00bfff, #00ff88); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
    }
    
    /* Вкладки */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #1c2533; border-radius: 5px; color: white; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #00ff88; color: black; }
    
    /* Блоки */
    .metric-box {
        background-color: #1c2533;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
        text-align: center;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- Helper Functions ----------------

def set_dark_2d_style(ax, title, xlabel, ylabel):
    """Стиль для 2D (темный)"""
    ax.set_facecolor('#0e1117')
    ax.figure.set_facecolor('#0e1117')
    for spine in ax.spines.values(): spine.set_color('white')
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    ax.set_title(title, fontsize=12, pad=10)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle='--', alpha=0.2)
    ax.legend(facecolor='#1c2533', labelcolor='white')

def set_teacher_style_3d(ax, title, xlabel, ylabel, zlabel):
    """Стиль преподавателя: Белый фон + Шкала Справа + Инверсия"""
    ax.set_facecolor('white')
    ax.figure.set_facecolor('white')
    
    # Убираем заливку стенок
    ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    
    # Черные подписи и оси
    ax.tick_params(axis='x', colors='black')
    ax.tick_params(axis='y', colors='black')
    ax.tick_params(axis='z', colors='black', pad=10)
    
    # Подписи с отступами
    ax.set_xlabel(xlabel, linespacing=1.5, color='black', labelpad=10)
    ax.set_ylabel(ylabel, linespacing=1.5, color='black', labelpad=10)
    ax.set_zlabel(zlabel, linespacing=1.5, color='black', labelpad=15, rotation=90)
    
    ax.set_title(title, color='black', pad=20, fontsize=14, fontweight='bold')
    
    # !!! ИНВЕРСИЯ ОСЕЙ (Чтобы 0 был в нужном углу) !!!
    ax.invert_xaxis()
    ax.invert_yaxis()

# ---------------- Main App ----------------

st.title("🧊 3D Моделирование: Поверхности отклика")
st.markdown("Визуализация влияния дозировок добавок на процесс.")

# Данные моделей (2D для сравнения)
t = np.linspace(2, 10, 100)
ph_control = 4.605 - 0.125 * np.log(t)
ph_exp1 = 4.535 - 0.102 * np.log(t) 
ph_exp2 = 4.506 - 0.125 * np.log(t) 

# Вкладки продуктов
tab_ayran, tab_irimshik = st.tabs(["🥛 Айран (Ферментация)", "🧀 Сары ірімшік (Уваривание)"])

# ==========================================
# 1. АЙРАН
# ==========================================
with tab_ayran:
    st.header("1. Моделирование ферментации Айрана")
    
    subtab1, subtab2, subtab3 = st.tabs(["📊 Сравнение 2D", "🧪 Опыт 1 (Сухая)", "🔥 Опыт 2 (Сироп)"])
    
    with subtab1:
        # 2D График
        col1, col2 = st.columns([2, 1])
        with col1:
            fig, ax = plt.subplots(figsize=(10, 6))
            set_dark_2d_style(ax, "Динамика сквашивания", "Время (ч)", "pH")
            ax.plot(t, ph_control, '--', color='#00bfff', label='Контроль')
            ax.plot(t, ph_exp1, '-', color='#00ff88', linewidth=2, label='Опыт 1 (Сухая)')
            ax.plot(t, ph_exp2, '-.', color='#ff4b4b', linewidth=2, label='Опыт 2 (Сироп)')
            ax.axhline(4.6, color='yellow', alpha=0.3, label='pH 4.6 (Норма)')
            ax.legend(facecolor='#1c2533', labelcolor='white')
            st.pyplot(fig)
        with col2:
            st.markdown('<div class="metric-box">Опыт 1 замедляет падение pH.<br>Опыт 2 ускоряет процесс.</div>', unsafe_allow_html=True)

    # 3D ОПЫТ 1
    with subtab2:
        st.subheader("Поверхность отклика: Опыт 1")
        
        t_3d = np.linspace(2, 10, 40)
        dose_3d = np.linspace(1, 3, 40)
        T, D = np.meshgrid(t_3d, dose_3d)
        
        Z_ph = 4.8 - (0.12 * np.log(T)) - (0.02 * D) + (0.01 * T * D/10)
        
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        surf = ax.plot_surface(D, T, Z_ph, cmap='jet', edgecolor='k', linewidth=0.2, alpha=0.9)
        
        set_teacher_style_3d(ax, "Реконструкция модели (pH справа)", "\nДоза, %", "\nВремя, ч", "\npH")
        ax.view_init(elev=20, azim=135)
        
        cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, pad=0.1)
        cbar.set_label('pH')
        st.pyplot(fig)

    # 3D ОПЫТ 2
    with subtab3:
        st.subheader("Поверхность отклика: Опыт 2")
        
        dose_3d_2 = np.linspace(1, 4, 40)
        T2, D2 = np.meshgrid(t_3d, dose_3d_2)
        Z_ph_2 = 4.8 - (0.13 * np.log(T2)) - (0.05 * D2) 
        
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        surf = ax.plot_surface(D2, T2, Z_ph_2, cmap='jet', edgecolor='k', linewidth=0.2, alpha=0.9)
        
        set_teacher_style_3d(ax, "Модель ускорения (pH справа)", "\nДоза, %", "\nВремя, ч", "\npH")
        ax.view_init(elev=20, azim=135)
        
        cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, pad=0.1)
        cbar.set_label('pH')
        st.pyplot(fig)

# ==========================================
# 2. САРЫ ІРІМШІК
# ==========================================
with tab_irimshik:
    st.header("2. Моделирование Сары ірімшік")
    
    # ТРИ Вкладки: Сравнение, Опыт 4%, Опыт 5%
    subtab_ir1, subtab_ir2, subtab_ir3 = st.tabs(["📊 Сравнение 2D", "🧀 Опыт 1 (4%)", "🧀 Опыт 2 (5%)"])
    
    # Данные для 2D
    t_ir = np.linspace(0, 5, 100)
    w_control = 20 + (75 - 20) * np.exp(-0.3 * t_ir)
    w_exp4 = 18 + (70 - 18) * np.exp(-(0.3 + 0.04*4) * t_ir) # Доза 4%
    w_exp5 = 18 + (70 - 18) * np.exp(-(0.3 + 0.04*5) * t_ir) # Доза 5%
    
    with subtab_ir1:
        col1, col2 = st.columns([2, 1])
        with col1:
            fig2d, ax2d = plt.subplots(figsize=(10, 6))
            set_dark_2d_style(ax2d, "Кривые сушки (Уваривание)", "Время (ч)", "Влажность %")
            
            ax2d.plot(t_ir, w_control, color="#00bfff", linewidth=2, label="Контроль (0%)")
            ax2d.plot(t_ir, w_exp4, color="#ffaa00", linewidth=2, linestyle='--', label="Опыт 1 (4%)") # Желтый
            ax2d.plot(t_ir, w_exp5, color="#ff4b4b", linewidth=2, label="Опыт 2 (5%)") # Красный
            
            ax2d.axhline(18, color='white', linestyle=':', label='Цель (18%)')
            ax2d.legend(facecolor='#1c2533', labelcolor='white')
            st.pyplot(fig2d)
        with col2:
             st.markdown('<div class="metric-box">Сравнение эффективности:<br>5% добавка обеспечивает наиболее быстрое удаление влаги.</div>', unsafe_allow_html=True)
             
    # 3D МОДЕЛЬ ОПЫТ 1 (до 4%)
    with subtab_ir2:
        st.subheader("Поверхность отклика: Опыт 1 (Доза до 4%)")
        st.info("Влияние добавки в концентрации до 4% на влажность.")
        
        # Сетка до 4%
        t_ir_3d = np.linspace(0, 5, 40)
        dose_ir_3d = np.linspace(0, 4, 40)
        T_ir, D_ir = np.meshgrid(t_ir_3d, dose_ir_3d)
        
        # Формула
        W_start = 75.0 - D_ir
        k_speed = 0.3 + (0.04 * D_ir)
        Moisture = 18.0 + (W_start - 18.0) * np.exp(-k_speed * T_ir)
        
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # X=Dose, Y=Time
        surf = ax.plot_surface(D_ir, T_ir, Moisture, cmap='jet', edgecolor='k', linewidth=0.2, alpha=0.9)
        
        set_teacher_style_3d(ax, "Опыт 1: Умеренное уваривание", "\nДоза, %", "\nВремя, ч", "\nВлажность, %")
        ax.view_init(elev=20, azim=135)
        
        cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, pad=0.1)
        cbar.set_label('Влажность %')
        st.pyplot(fig)

    # 3D МОДЕЛЬ ОПЫТ 2 (до 5%)
    with subtab_ir3:
        st.subheader("Поверхность отклика: Опыт 2 (Доза до 5%)")
        st.warning("Влияние максимальной концентрации добавки (5%).")
        
        # Сетка до 5%
        dose_ir_3d_5 = np.linspace(0, 5, 40)
        T_ir_5, D_ir_5 = np.meshgrid(t_ir_3d, dose_ir_3d_5)
        
        # Формула
        W_start_5 = 75.0 - D_ir_5
        k_speed_5 = 0.3 + (0.04 * D_ir_5)
        Moisture_5 = 18.0 + (W_start_5 - 18.0) * np.exp(-k_speed_5 * T_ir_5)
        
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # X=Dose, Y=Time
        surf = ax.plot_surface(D_ir_5, T_ir_5, Moisture_5, cmap='jet', edgecolor='k', linewidth=0.2, alpha=0.9)
        
        set_teacher_style_3d(ax, "Опыт 2: Интенсивное уваривание", "\nДоза, %", "\nВремя, ч", "\nВлажность, %")
        ax.view_init(elev=20, azim=135)
        
        cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, pad=0.1)
        cbar.set_label('Влажность %')
        st.pyplot(fig)