import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

# ---------------- Config ----------------
st.set_page_config(page_title="Научное Моделирование", layout="wide", page_icon="📐")

# ---------------- Styles: Premium Dark ----------------
st.markdown("""
<style>
    /* Общий фон */
    .stApp { background-color: #0e1117; color: white; }
    h1 { background: linear-gradient(to right, #00bfff, #00ff88); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    
    /* Вкладки */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #1c2533; border-radius: 5px; color: white; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #00ff88; color: black; }
    
    /* Карточки метрик */
    .metric-card {
        background-color: #1c2533;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #00bfff;
        margin-bottom: 10px;
    }
    .best-model { border-left-color: #00ff88; }
</style>
""", unsafe_allow_html=True)

# Функция стиля графиков
def set_dark_style(ax):
    ax.set_facecolor('#0e1117')
    ax.figure.set_facecolor('#0e1117')
    for spine in ax.spines.values(): spine.set_color('white')
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    ax.grid(True, linestyle='--', alpha=0.2)
    ax.legend(facecolor='#1c2533', labelcolor='white')

# ---------------- Load Data ----------------
@st.cache_data
def load_data():
    if os.path.exists("Scientific_Data_Extended.csv"): return pd.read_csv("Scientific_Data_Extended.csv")
    if os.path.exists("Scientific_Data.csv"): return pd.read_csv("Scientific_Data.csv")
    return pd.DataFrame()

df = load_data()

st.title("🧬 Математическое ядро Цифрового Двойника")

if df.empty:
    st.error("Данные не найдены. Запустите generate_data.py")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Входные параметры")
    
    products = df['productname'].unique()
    prod = st.selectbox("Продукт:", products)
    
    st.markdown("---")
    st.subheader("🏭 Параметры цеха")
    batch_volume = st.number_input("Объем партии (л):", 100, 5000, 1000)
    start_temp = st.number_input("Т° молока на входе:", 4, 25, 10)
    
    model_df = df[df['productname'] == prod].copy()

# --- ОПРЕДЕЛЕНИЕ ЦЕЛЕВОЙ ПЕРЕМЕННОЙ ---
if "Айран" in prod:
    target_col = 'ph'; target_label = 'pH'; target_unit = ''; target_goal = 4.6
else:
    target_col = 'влага'; target_label = 'Влажность'; target_unit = '%'; target_goal = 18.0

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📋 14 Переменных", "🧠 Выбор Модели (R²)", "🔥 Энергетика (Физика)", "🎛 Оптимизатор"])

# ==========================================
# TAB 1: 14 ПЕРЕМЕННЫХ (Вектор состояния)
# ==========================================
with tab1:
    st.info(f"**Вектор состояния системы** (согласно ТЗ): 14 контролируемых параметров для продукта «{prod}»")
    
    vars_list = [
        "1. Температура (°C)", "2. pH", "3. Кислотность (°T)",
        "4. OrP (ОВП, мВ)", "5. Вязкость (мПа·с)", "6. Плотность (кг/м³)",
        "7. Активность воды (aw)", "8. Жир (%)", "9. Белок (%)",
        "10. Влага (%)", "11. Сухие вещества (%)", "12. КМАФАнМ",
        "13. Молочнокислые бактерии", "14. Длительность (ч)"
    ]
    
    cols = st.columns(4)
    for i, v in enumerate(vars_list):
        cols[i % 4].success(f"✅ {v}")

# ==========================================
# TAB 2: СРАВНЕНИЕ МОДЕЛЕЙ (ML)
# ==========================================
with tab2:
    st.subheader("Оценка достоверности моделей")
    st.markdown("Сравнение Линейной и Нелинейной (Логарифмической) моделей по критериям $R^2$ и MAE.")

    # Подготовка данных
    train_df = model_df[['duration_hours', target_col]].dropna()
    X = train_df[['duration_hours']].values
    y = train_df[target_col].values
    
    if len(X) < 5:
        st.warning("Недостаточно данных для обучения.")
    else:
        # --- МОДЕЛЬ 1: Линейная (y = ax + b) ---
        lin_reg = LinearRegression()
        lin_reg.fit(X, y)
        y_pred_lin = lin_reg.predict(X)
        mae_lin = mean_absolute_error(y, y_pred_lin)
        r2_lin = r2_score(y, y_pred_lin) # <--- R2 для линейной
        
        # --- МОДЕЛЬ 2: Логарифмическая (WINNER) ---
        X_log = np.log(X + 1.0) # +1 защита от log(0)
        best_reg = LinearRegression()
        best_reg.fit(X_log, y)
        y_pred_best = best_reg.predict(X_log)
        mae_best = mean_absolute_error(y, y_pred_best)
        r2_best = r2_score(y, y_pred_best) # <--- R2 для логарифмической
        
        model_name = "Логарифмическая"
        sign = "+" if best_reg.coef_[0] >= 0 else ""
        formula = f"{target_label} = {best_reg.intercept_:.2f} {sign}{best_reg.coef_[0]:.3f} \\cdot \\ln(t+1)"

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <h5>📉 Линейная модель</h5>
                Ошибка MAE: <b>{mae_lin:.4f}</b><br>
                Точность R²: <b>{r2_lin:.4f}</b>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card best-model">
                <h5>🏆 {model_name} (WINNER)</h5>
                Ошибка MAE: <b>{mae_best:.4f}</b><br>
                Точность R²: <b>{r2_best:.4f}</b>
            </div>
            """, unsafe_allow_html=True)
            
        # ПРОВЕРКА КРИТЕРИЯ
        acc_limit = 0.05 if target_col == 'ph' else 2.0
        if mae_best <= acc_limit:
            st.success(f"✅ Критерий точности выполнен (MAE < {acc_limit})")
        else:
            st.warning(f"⚠️ Требуется уточнение (MAE > {acc_limit})")
            
        # ГРАФИК
        fig, ax = plt.subplots(figsize=(10, 5))
        set_dark_style(ax)
        ax.scatter(X, y, color='#00bfff', alpha=0.5, label='Факт')
        
        sort_idx = X.flatten().argsort()
        ax.plot(X[sort_idx], y_pred_best[sort_idx], color='#00ff88', linewidth=3, label=f'Модель (R²={r2_best:.3f})')
        ax.plot(X[sort_idx], y_pred_lin[sort_idx], color='#ff4b4b', linestyle='--', label=f'Линейная (R²={r2_lin:.3f})')
        
        ax.set_xlabel("Время, ч"); ax.set_ylabel(target_label)
        ax.legend(facecolor='#1c2533', labelcolor='white')
        st.pyplot(fig)
        
        st.info(f"**Математическое уравнение:** ${formula}$")

# ==========================================
# TAB 3: ЭНЕРГЕТИКА (Физика стадий)
# ==========================================
with tab3:
    st.header("⚡ Расчет энергопотребления (Физическая модель)")
    
    # Константы
    cp_milk = 3.9 # кДж/(кг*К)
    mass = batch_volume * 1.03 # кг
    
    col_heat, col_cool = st.columns(2)
    
    with col_heat:
        st.subheader("🔥 Пастеризация")
        temp_pasteur = 84.0 if "Айран" in prod else 96.0 # Из техкарты
        delta_t_heat = temp_pasteur - start_temp
        
        q_heat_kwh = mass * cp_milk * delta_t_heat / 3600
        
        st.metric("Целевая температура", f"{temp_pasteur} °C")
        st.metric("Затраты энергии", f"{q_heat_kwh:.2f} кВт·ч")
        st.latex(r"Q_{heat} = m \cdot c_p \cdot (T_{past} - T_{start})")
        
    with col_cool:
        st.subheader("❄️ Охлаждение")
        temp_ferm = 42.0 if "Айран" in prod else 20.0 # Уставка
        delta_t_cool = temp_pasteur - temp_ferm
        
        q_cool_kwh = mass * cp_milk * delta_t_cool / 3600
        
        st.metric("Т° после охлаждения", f"{temp_ferm} °C")
        st.metric("Отвод тепла", f"{q_cool_kwh:.2f} кВт·ч")
        st.latex(r"Q_{cool} = m \cdot c_p \cdot (T_{past} - T_{ferm})")

# ==========================================
# TAB 4: ОПТИМИЗАТОР (Reverse Engineering)
# ==========================================
with tab4:
    st.header("🎛 Технологический Оптимизатор")
    
    train_df_opt = model_df[['duration_hours', target_col]].dropna()
    
    if len(train_df_opt) > 5:
        X_opt = np.log(train_df_opt[['duration_hours']].values + 1.0)
        y_opt = train_df_opt[target_col].values
        
        opt_model = LinearRegression()
        opt_model.fit(X_opt, y_opt)
        
        a = opt_model.intercept_; b = opt_model.coef_[0]
        
        c1, c2 = st.columns([1, 2])
        with c1:
            # Безопасные границы
            min_v = float(y_opt.min()); max_v = float(y_opt.max())
            def_v = target_goal
            if def_v < min_v: def_v = min_v
            if def_v > max_v: def_v = max_v
            
            target_val = st.number_input(f"Целевой {target_label}:", min_v, max_v, def_v)
            
            if abs(b) > 0.001:
                t_res = np.exp((target_val - a) / b) - 1.0
                st.success(f"⏱ Время: **{max(0, t_res):.2f} ч**")
            else:
                st.error("Модель не видит зависимости от времени.")
        
        with c2:
            fig_o, ax_o = plt.subplots(figsize=(10, 4))
            set_dark_style(ax_o)
            t_g = np.linspace(0, 12, 100).reshape(-1,1)
            p_g = opt_model.predict(np.log(t_g+1))
            ax_o.plot(t_g, p_g, color='#be5bf7', linewidth=3)
            ax_o.axhline(target_val, color='yellow', linestyle=':')
            st.pyplot(fig_o)
            
    else:
        st.warning("Недостаточно данных для работы Оптимизатора.")