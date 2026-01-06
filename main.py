# Главная.py
# ============================================
# ВЕРСИЯ: FINAL DIGITAL TWIN DASHBOARD
# ============================================

import os
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# ---------------- Page config ----------------
st.set_page_config(page_title="Мониторинг Производства", layout="wide", page_icon="🧬")

# ---------------- Styles: PREMIUM DARK THEME ----------------
st.markdown(
    """
    <style>
    /* Основной фон */
    .stApp {
        background-color: #0e1117;
        background-image: radial-gradient(circle at 50% 0%, #1c2533 0%, #0e1117 60%);
    }
    
    /* Заголовки */
    h1 {
        background: linear-gradient(to right, #00bfff, #00ff88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800 !important;
        letter-spacing: -1px;
    }
    
    /* --- KPI КАРТОЧКА --- */
    .kpi-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        border-color: #58a6ff;
    }
    .kpi-icon {
        font-size: 24px;
        margin-bottom: 10px;
        display: inline-block;
        padding: 10px;
        border-radius: 50%;
        background: rgba(255,255,255,0.05);
    }
    .kpi-title {
        color: #8b949e;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .kpi-value {
        color: #f0f6fc;
        font-size: 32px;
        font-weight: 700;
        margin-top: 5px;
    }
    .kpi-unit {
        font-size: 16px;
        color: #8b949e;
        font-weight: 400;
    }
    
    /* Таблица Технологии */
    .tech-container {
        background-color: #161b22;
        border-radius: 12px;
        border: 1px solid #30363d;
        overflow: hidden;
    }
    .tech-table {
        width: 100%;
        border-collapse: collapse;
        color: #c9d1d9;
        font-family: 'Segoe UI', sans-serif;
    }
    .tech-table th {
        background-color: #21262d;
        color: #58a6ff;
        padding: 15px;
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid #30363d;
    }
    .tech-table td {
        padding: 15px;
        border-bottom: 1px solid #21262d;
        transition: background 0.2s;
    }
    .tech-table tr:hover td {
        background-color: #1f242c;
        color: #fff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🧬 Цифровой Паспорт Продукта")
st.markdown("<div style='margin-bottom: 30px; color: #8b949e;'>Система мониторинга качества и технологических параметров</div>", unsafe_allow_html=True)

# ---------------- Data Loading ----------------
@st.cache_data
def load_data():
    # Приоритет: расширенная база (с новой химией) -> обычная -> пустая
    if os.path.exists("Scientific_Data_Extended.csv"):
        df = pd.read_csv("Scientific_Data_Extended.csv")
    elif os.path.exists("Scientific_Data.csv"):
        df = pd.read_csv("Scientific_Data.csv")
    else:
        return pd.DataFrame()
    
    # Нормализация имен колонок
    df.columns = [c.lower().strip() for c in df.columns]
    return df

df = load_data()

if df.empty:
    st.error("⚠️ Данные не найдены. Запустите генератор данных (generate_data.py).")
    st.stop()

# ---------------- Helpers ----------------
def display_kpi(col, title, value, unit, color, icon):
    html = f"""
    <div class="kpi-card" style="border-left: 4px solid {color};">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <div class="kpi-title">{title}</div>
                <div class="kpi-value" style="text-shadow: 0 0 20px {color}40;">
                    {value} <span class="kpi-unit">{unit}</span>
                </div>
            </div>
            <div class="kpi-icon" style="color: {color};">{icon}</div>
        </div>
    </div>
    """
    col.markdown(html, unsafe_allow_html=True)

# ---------------- UI Logic ----------------

# SIDEBAR
with st.sidebar:
    st.markdown("### ⚙️ Настройки")
    
    prod_col = 'productname' if 'productname' in df.columns else 'product_name'
    
    if prod_col in df.columns:
        products = sorted(df[prod_col].unique())
        # Айран по умолчанию
        def_idx = 0
        for i, p in enumerate(products):
            if 'Айран' in str(p): def_idx = i
            
        product = st.selectbox("Выберите продукт:", products, index=def_idx)
        
        # Фильтр данных по продукту
        sub_df = df[df[prod_col] == product].copy()
        
        # Фильтр по типу эксперимента (если есть)
        if 'experiment_type' in sub_df.columns:
            exp_types = ['Все партии'] + sorted(sub_df['experiment_type'].unique().tolist())
            selected_exp = st.selectbox("Партия / Опыт:", exp_types)
            
            if selected_exp != 'Все партии':
                sub_df = sub_df[sub_df['experiment_type'] == selected_exp]
        
        st.markdown("---")
        st.info(f"📦 Анализ по **{len(sub_df)}** точкам данных")
    else:
        st.error("Ошибка структуры данных: нет колонки productname")
        st.stop()

# MAIN CONTENT
# Берем средние значения для отображения KPI
means = sub_df.mean(numeric_only=True)

# --- 1. БЛОК KPI ---
st.markdown(f"### 📊 Показатели качества: {product}")

# Конфигурация KPI (адаптирована под новые данные)
kpi_config = []

if "Айран" in str(product):
    kpi_config = [
        ('ph', 'pH (Активная)', '', '#00ff88', '🧪'),
        ('кислотность', 'Кислотность', '°T', '#ffbb00', '🍋'),
        ('viscosity_mpa_s', 'Вязкость', 'mPa·s', '#be5bf7', '💧'), # Новое!
        ('fat_pct', 'Жир', '%', '#00bfff', '🥛'),
        ('protein_pct', 'Белок', '%', '#ff9f43', '🧬'),
        ('kmafanm', 'КМАФАнМ', 'КОЕ', '#ff4444', '🦠')
    ]
else: # Сары ірімшік
    kpi_config = [
        ('влага', 'Влажность', '%', '#00bfff', '💧'),
        ('сухие_вещества', 'Сухие вещества', '%', '#ffbb00', '🧱'),
        ('fat_pct', 'Жир', '%', '#ff9f43', '🧀'),
        ('protein_pct', 'Белок', '%', '#ff6b6b', '🧬'),
        ('ph', 'pH', '', '#a0aec0', '🧪'),
        ('density_kg_m3', 'Плотность', 'кг/м³', '#be5bf7', '⚖️')
    ]

# Отрисовка KPI
rows = [kpi_config[i:i + 3] for i in range(0, len(kpi_config), 3)]

for row in rows:
    cols = st.columns(3)
    for i, (key, title, unit, color, icon) in enumerate(row):
        val = means.get(key, 0)
        # Форматирование
        fmt_val = f"{val:,.0f}".replace(",", " ") if val > 1000 else f"{val:.2f}"
        display_kpi(cols[i], title, fmt_val, unit, color, icon)

# --- 2. ТЕХНОЛОГИЧЕСКИЙ БЛОК + AI СИМУЛЯТОР ---
st.markdown("---")
c_tech, c_sim = st.columns([2, 1])

with c_tech:
    st.markdown("### 📋 Технологический журнал")
    
    # Выбираем колонки для таблицы
    target_cols = {
        'process_stage': 'Этап',
        'duration_hours': 'Время (ч)',
        'temperature_c': 'Темп. (°C)',
        'ph': 'pH',
        'влага': 'Влага %'
    }
    
    # Оставляем только те, что есть в данных
    avail_cols = [c for c in target_cols.keys() if c in sub_df.columns]
    
    if avail_cols:
        # Группируем по этапу или показываем среднее
        if 'process_stage' in sub_df.columns:
            td = sub_df.groupby('process_stage')[avail_cols].mean(numeric_only=True).reset_index()
        else:
            td = sub_df[avail_cols].mean(numeric_only=True).to_frame().T
            td['process_stage'] = 'Производство'
            
        # Красивое переименование
        display_cols = {k: v for k, v in target_cols.items() if k in avail_cols}
        td = td.rename(columns=display_cols).round(2)
        
        # HTML таблица
        html_table = td.to_html(classes='tech-table', index=False, border=0)
        st.markdown(f'<div class="tech-container">{html_table}</div>', unsafe_allow_html=True)
    else:
        st.info("Нет данных для отображения журнала")

with c_sim:
    # === AI СИМУЛЯТОР (С УЛУЧШЕННОЙ МАТЕМАТИКОЙ) ===
    st.markdown("### 🔮 Прогноз")
    with st.container():
        st.markdown("**Симулятор условий (Digital Twin)**")
        time_input = st.slider("Время процесса (ч)", 0.0, 10.0, 5.0)
        
        # Настройка целей
        is_ayran = "Айран" in str(product)
        target_col = 'ph' if is_ayran else 'влага'
        label = "Прогноз pH" if is_ayran else "Прогноз Влаги %"
        color = "#00ff88" if is_ayran else "#00bfff"
        
        prediction_val = 0
        model_trained = False
        
        # Обучение модели
        if target_col in sub_df.columns and 'duration_hours' in sub_df.columns:
            train_data = sub_df[['duration_hours', target_col]].dropna()
            
            if len(train_data) > 5:
                X = train_data[['duration_hours']].values
                y = train_data[target_col].values
                
                # !!! ВАЖНО: Используем Логарифмическую модель для физической точности !!!
                # Для Айрана (падение pH) и Иримшика (сушка) логарифм подходит лучше прямой
                try:
                    X_log = np.log(X + 1.0) # +1 чтобы избежать log(0)
                    model = LinearRegression()
                    model.fit(X_log, y)
                    
                    # Предсказание
                    prediction_val = model.predict([[np.log(time_input + 1.0)]])[0]
                    model_trained = True
                except:
                    pass
        
        # Если модель не обучилась (мало данных), используем формулу из генератора
        if not model_trained:
            if is_ayran:
                # Формула из генератора: Start 5.98 -> End ~4.2
                prediction_val = 5.98 - 0.7 * np.log(time_input + 1.0)
            else:
                # Иримшик: Start 75 -> End 18
                prediction_val = 18.0 + (75.0 - 18.0) * np.exp(-0.3 * time_input)
            st.caption("⚠️ Используется теоретическая модель")

        # Визуализация
        st.markdown(f"""
        <div style="margin-top: 20px; text-align: center;">
            <div style="color: #8b949e; font-size: 14px;">{label}</div>
            <div style="color: {color}; font-size: 48px; font-weight: bold; text-shadow: 0 0 20px {color}40;">
                {prediction_val:.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Контроль качества (Светофор)
        status = "✅ НОРМА"
        status_color = "green"
        
        if is_ayran:
            if prediction_val < 4.0: status = "⚠️ ПЕРЕКИСАНИЕ"; status_color = "red"
            elif prediction_val > 5.0 and time_input > 6: status = "⚠️ НЕДОКВАС"; status_color = "orange"
        else:
            if prediction_val < 15.0: status = "⚠️ ПЕРЕСУШКА"; status_color = "red"
        
        st.markdown(f"<div style='text-align:center; color:{status_color}; font-weight:bold;'>{status}</div>", unsafe_allow_html=True)