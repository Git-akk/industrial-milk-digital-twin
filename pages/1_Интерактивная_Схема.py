# 1_Интерактивная_Схема.py
# ============================================
# ВЕРСИЯ: SCADA FINAL (Исправлен pH для Сары ірімшік)
# ============================================

import os
import streamlit as st
import pandas as pd
import numpy as np
from streamlit.components.v1 import html as st_html

# ---------------- Page config ----------------
st.set_page_config(page_title="SCADA: Технологическая Линия", layout="wide", page_icon="🏭")

# ---------------- Load Data ----------------
@st.cache_data
def load_data():
    # Пытаемся загрузить расширенный файл (с новой физикой), если нет - обычный
    if os.path.exists("Scientific_Data_Extended.csv"):
        df = pd.read_csv("Scientific_Data_Extended.csv")
    elif os.path.exists("Scientific_Data.csv"):
        df = pd.read_csv("Scientific_Data.csv")
    else:
        return pd.DataFrame()
        
    # Приводим названия колонок к нижнему регистру
    df.columns = [c.lower().strip() for c in df.columns]
    return df

df = load_data()

# ---------------- Main Interface ----------------
st.title("🏭 Цифровой Двойник: SCADA Система")

if df.empty:
    st.error("⚠️ Файлы данных не найдены (Scientific_Data_Extended.csv). Запустите generate_data.py")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("🎛 Панель Диспетчера")
    
    # Ищем колонку с названием продукта
    prod_col = 'productname' if 'productname' in df.columns else 'product_name'
    if prod_col not in df.columns:
        st.error("Ошибка: в данных нет колонки productname")
        st.stop()
        
    products = sorted(df[prod_col].unique())
    # Ставим Айран по умолчанию
    def_idx = 0
    for i, p in enumerate(products):
        if 'Айран' in str(p): def_idx = i
        
    selected_product = st.selectbox("Линия:", products, index=def_idx)
    
    st.divider()
    
    # Слайдер времени
    prod_df = df[df[prod_col] == selected_product].sort_values('duration_hours')
    max_t = prod_df['duration_hours'].max() if not prod_df.empty else 12.0
    
    current_time = st.slider("Время процесса (ч):", 0.0, float(max_t), 0.0, 0.1)
    
    # Получаем строку данных для текущего времени
    row = None
    if not prod_df.empty:
        idx = (prod_df['duration_hours'] - current_time).abs().idxmin()
        row = prod_df.loc[idx]
            
    if row is not None:
        exp_type = row.get('experiment_type', 'Стандарт')
        stage_name = row.get('process_stage', 'Производство')
        st.info(f"**Партия:** #{int(current_time*100)+1000}\n\n**Тип:** {exp_type}\n\n**Этап:** {stage_name}")

# ---------------- HTML/CSS GENERATION ----------------

styles = """
<style>
    body { background-color: transparent; font-family: sans-serif; }
    .scada-container { 
        display: flex; flex-wrap: wrap; justify-content: center; 
        align-items: flex-start; padding: 20px; gap: 30px; 
    }
    .unit-card {
        background-color: #161b22; border: 1px solid #30363d; border-radius: 4px;
        width: 260px; min-height: 200px; box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        position: relative; transition: all 0.3s ease; color: #e6edf3;
    }
    .unit-header {
        background-color: #21262d; padding: 10px 15px; border-bottom: 1px solid #30363d;
        display: flex; justify-content: space-between; align-items: center;
    }
    .unit-title {
        color: #e6edf3; font-family: monospace; font-weight: bold; font-size: 14px; text-transform: uppercase;
    }
    .status-indicator { width: 12px; height: 12px; border-radius: 50%; background-color: #333; }
    .status-on { background-color: #00ff88; box-shadow: 0 0 10px #00ff88; }
    .status-heat { background-color: #ff4b4b; box-shadow: 0 0 10px #ff4b4b; animation: blink 1s infinite; }
    .status-off { background-color: #ff4b4b; }
    .status-idle { background-color: #555; }
    
    @keyframes blink { 50% { opacity: 0.5; } }

    .unit-body { padding: 15px; }
    .tag-row {
        display: flex; justify-content: space-between; margin-bottom: 8px;
        font-family: monospace; font-size: 13px; border-bottom: 1px dashed #30363d;
    }
    .tag-name { color: #8b949e; }
    .tag-value { color: #58a6ff; font-weight: bold; }
    .tag-unit { color: #8b949e; font-size: 11px; margin-left: 5px; }
    .active-unit { border-color: #00ff88; box-shadow: 0 0 15px rgba(0, 255, 136, 0.15); }
    
    .pipe-connection { display: flex; align-items: center; justify-content: center; width: 40px; height: 100%; align-self: center; }
    .flow-arrow { color: #30363d; font-size: 24px; }
    .flow-active { color: #00ff88; animation: flowPulse 1s infinite; }
    @keyframes flowPulse { 0% { opacity: 0.3; } 50% { opacity: 1; } 100% { opacity: 0.3; } }
</style>
"""

def render_scada_unit(title, status, tags, is_active):
    status_cls = "status-idle"
    if status == "RUN": status_cls = "status-on"
    elif status == "HEAT": status_cls = "status-heat"
    elif status == "OFF": status_cls = "status-off"
    
    active_card_cls = "active-unit" if is_active else ""
    
    tags_html = ""
    for k, (val, unit) in tags.items():
        # Форматирование значения
        if isinstance(val, (int, float)):
            val_str = f"{val:.2f}" if val < 100 else f"{val:.1f}"
        else:
            val_str = str(val)
            
        tags_html += f"""
        <div class="tag-row">
            <span class="tag-name">{k}</span>
            <div><span class="tag-value">{val_str}</span><span class="tag-unit">{unit}</span></div>
        </div>
        """

    return f"""
    <div class="unit-card {active_card_cls}">
        <div class="unit-header">
            <span class="unit-title">{title}</span>
            <div class="status-indicator {status_cls}"></div>
        </div>
        <div class="unit-body">{tags_html}</div>
    </div>
    """

def render_pipe(is_active):
    cls = "flow-active" if is_active else ""
    return f'<div class="pipe-connection"><div class="flow-arrow {cls}">➤</div></div>'

# === ГЕНЕРАЦИЯ СХЕМЫ ===
html_content = '<div class="scada-container">'

# Данные для отображения (с защитой от отсутствия колонок)
def get_val(col, default):
    return row[col] if (row is not None and col in row) else default

# Извлекаем параметры из базы
temp = get_val('temperature_c', 20.0)
ph = get_val('ph', 6.6)
moist = get_val('влага', 88.0)
press = get_val('pressure_mpa', 0.0)
visc = get_val('viscosity_mpa_s', 1.5)
fat = get_val('fat_pct', 3.2)
if "Айран" in str(selected_product):
    # ЛОГИКА ЭТАПОВ (АЙРАН)
    s1 = (0.0 <= current_time < 0.5) # Приемка
    s2 = (0.5 <= current_time < 1.0) # Гомогенизация
    s3 = (1.0 <= current_time < 1.5) # Пастеризация
    s4 = (2.0 <= current_time < 8.0) # Ферментация (Брожение)
    s5 = (current_time >= 8.0)       # Розлив
    
    # 1. Танк Нормализации
    # Данные: Уровень (эмуляция расхода), Температура (уставка), Жир (из базы)
    t_norm = 42.0 if s1 else (65.0 if s2 else 20.0)
    html_content += render_scada_unit("Танк Нормализации", "RUN" if s1 else "OFF", {
        "Уровень": (85 - current_time*2, "%"), 
        "Температура": (t_norm, "°C"), 
        "Жирность": (fat, "%"),
        "Мешалка": ("ВКЛ" if s1 else "ВЫКЛ", "")
    }, s1)
    html_content += render_pipe(s1)
    
    # 2. Гомогенизатор
    # Данные: Давление (из базы или 12.5 МПа по стандарту), Мощность (эмуляция)
    p_disp = press if s2 and press > 0 else (12.5 if s2 else 0)
    html_content += render_scada_unit("Гомогенизатор", "RUN" if s2 else "OFF", {
        "Давление": (p_disp, "МПа"), 
        "Температура": (65.0 if s2 else 40.0, "°C"), 
        "Мощность": (45 if s2 else 0, "кВт")
    }, s2)
    html_content += render_pipe(s2)
    
    # 3. Пастеризатор
    # Данные: Температура выхода (84°C по схеме), Подача пара (клапан %)
    html_content += render_scada_unit("Пастеризатор", "RUN" if s3 else "OFF", {
        "Т_Выход": (84.0 if s3 else 65.0, "°C"), 
        "Клапан пара": (85 if s3 else 0, "%"), 
        "Поток": (5000 if s3 else 0, "л/ч")
    }, s3)
    html_content += render_pipe(s3)
    
    # 4. Ферментатор (Бродильный танк)
    # Данные: pH (из базы!), Кислотность (расчет), Вязкость (из базы!)
    acid_t = get_val('кислотность', (7 - ph) * 40)
    html_content += render_scada_unit("Танк Ферментации", "RUN" if s4 else "OFF", {
        "pH Продукта": (ph, ""), 
        "Кислотность": (acid_t, "°T"), 
        "Температура": (temp, "°C"), 
        "Вязкость": (visc, "мПа·с")
    }, s4)
    html_content += render_pipe(s5)
    
    # 5. Линия Розлива
    # Данные: Скорость (эмуляция), Счетчик (эмуляция)
    html_content += render_scada_unit("Линия Розлива", "RUN" if s5 else "OFF", {
        "Скорость": (6000 if s5 else 0, "бут/ч"), 
        "Счетчик": (int(current_time*1200) if s5 else 0, "шт"),
        "Т_Продукта": (4.0 if s5 else 20.0, "°C")
    }, s5)

else:
    # ЛОГИКА ЭТАПОВ (ИРИМШИК)
    s1 = (current_time < 1.0)        # Смесь
    s2 = (1.0 <= current_time < 5.0) # Варка
    s3 = (5.0 <= current_time < 6.0) # Пресс
    s4 = (current_time >= 6.0)       # Сушка
    
    # 1. Ванна (Свертывание)
    # pH берем из базы (он падает с 5.98)
    html_content += render_scada_unit("Сыродельная Ванна", "RUN" if s1 else "OFF", {
        "Т_Смеси": (34.0 if s1 else 20.0, "°C"), 
        "pH Молока": (ph, ""), 
        "Фермент": ("ВНЕСЕН" if current_time > 0.2 else "ОЖИДАНИЕ", "")
    }, s1)
    html_content += render_pipe(s1)
    
    # 2. Варочный Котел
    # Температура 96.5°C (кипение), Цвет меняется
    t_cook = 96.5 if s2 else (34.0 if s1 else 80.0)
    status_cook = "HEAT" if s2 else "OFF"
    html_content += render_scada_unit("Варочный Котел", status_cook, {
        "Т_Продукта": (t_cook, "°C"), 
        "Давление пара": (0.6 if s2 else 0, "МПа"), 
        "Датчик Цвета": ("ЖЕЛТЫЙ" if current_time > 3 else "БЕЛЫЙ", "")
    }, s2)
    html_content += render_pipe(s2)
    
    # 3. Пресс
    html_content += render_scada_unit("Пресс-Тележка", "RUN" if s3 else "OFF", {
        "Усилие": (2.5 if s3 else 0, "бар"), 
        "Слив сывор.": (50 if s3 else 0, "л/мин")
    }, s3)
    html_content += render_pipe(s3)
    
    # 4. Сушка
    # Влага берется из базы (падает до 18%)
    html_content += render_scada_unit("Сушильная Камера", "RUN" if s4 else "OFF", {
        "Т_Воздуха": (45.0 if s4 else 20.0, "°C"), 
        "Влажность": (moist, "%"), 
        "Цель": (18.0, "%")
    }, s4)
html_content += '</div>'

# ВЫВОД НА ЭКРАН (Стили + HTML)
st_html(styles + html_content, height=1000, scrolling=True)

# --- ГРАФИКИ ВНИЗУ ---
st.markdown("---")
c1, c2 = st.columns([3, 1])

with c1:
    st.subheader("📈 Тренд процесса")
    if row is not None:
        chart_df = df[df[prod_col] == selected_product].copy()
        
        target = 'ph' if "Айран" in str(selected_product) else 'влага'
        if target in chart_df.columns:
            color = '#00ff88' if "Айран" in str(selected_product) else '#00bfff'
            st.line_chart(chart_df, x='duration_hours', y=target, color=color, height=250)
        else:
            st.warning(f"Нет данных по параметру '{target}' для графика")

with c2:
    st.subheader("📊 KPI")
    if row is not None:
        if "Айран" in str(selected_product):
            acid_val = get_val('кислотность', (7-ph)*40)
            st.metric("Кислотность", f"{acid_val:.0f} °T", "+2°T")
        else:
            st.metric("Выход продукта", "18.5 %", "+0.5%")
            
        st.metric("Энергопотр.", "125 кВт")