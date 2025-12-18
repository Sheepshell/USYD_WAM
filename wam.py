import streamlit as st
import pandas as pd
import PyPDF2
import re
import matplotlib.pyplot as plt

# --- 语言配置 ---
LANG_DICT = {
    "zh": {
        "title": "🎓 悉尼大学工程学院 WAM & EIHWAM 助手",
        "description": "按学期精准统计你的学业表现，已修正精度显示问题。",
        "rules": "1. **WAM**: 普通加权平均分。\n2. **EIHWAM**: 荣誉加权平均分 (Wi: 1000级=0, 2000级=2, 3000级=3, 4000级+=4, Thesis=8)。",
        "upload_label": "请上传你的 Academic Transcript (PDF) 从Sydneystudent → My studies → Assessment → View academic transcript → Printable version",
        "sidebar_lang": "选择语言",
        "result_wam": "当前总 WAM",
        "result_hwam": "当前总 EIHWAM",
        "chart_title": "学期表现趋势",
        "chart_legend_sem_wam": "Sem Avg",
        "chart_legend_cum_wam": "Cum. WAM",
        "chart_legend_cum_eihwam": "Cum. EIHWAM",
        "table_header": "课程数据详情",
        "footer": "注：计算结果及绘图仅供参考，最终学位等级请以学校官方为准。"
    },
    "en": {
        "title": "🎓 USYD Engineering WAM & EIHWAM Assistant",
        "description": "Semester-by-semester tracking with precision fix.",
        "rules": "1. **WAM**: Weighted Average Mark.\n2. **EIHWAM**: Honours WAM (Wi: 1000=0, 2000=2, 3000=3, 4000+=4, Thesis=8).",
        "upload_label": "Upload Academic Transcript (PDF) from Sydneystudent → My studies → Assessment → View academic transcript → Printable version",
        "sidebar_lang": "Select Language",
        "result_wam": "Total WAM",
        "result_hwam": "Total EIHWAM",
        "chart_title": "Semester Trends",
        "chart_legend_sem_wam": "Sem Avg",
        "chart_legend_cum_wam": "Cum. WAM",
        "chart_legend_cum_eihwam": "Cum. EIHWAM",
        "table_header": "Course Details",
        "footer": "Note: Results are for reference only."
    }
}

def extract_data_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    full_text = ""
    for page in pdf_reader.pages:
        full_text += page.extract_text() + "\n"
    
    # 正则匹配课程行
    pattern = re.compile(r'(\d{4})\s+([S\d]\d[A-Z])\s+([A-Z]{4}\d{4})\s+(.*?)\s+(\d{1,3}\.\d|)\s*([A-Z]{2})\s+(\d+)')
    rows = []
    for m in pattern.findall(full_text):
        session_raw = m[1]
        sem_norm = "S1" if ("S1" in session_raw or "51" in session_raw) else "S2"
        rows.append({
            "Year": int(m[0]),
            "Semester": sem_norm,
            "Display_Label": f"{m[0]} {sem_norm}",
            "Code": m[2],
            "Name": m[3].strip(),
            "Mark": float(m[4]) if m[4] else None,
            "Grade": m[5],
            "CP": int(m[6])
        })
    return pd.DataFrame(rows)

def calculate_metrics(df):
    excluded_grades = ['CN', 'DC', 'DF', 'SR', 'UC']
    df = df.dropna(subset=['Mark']).copy()
    df = df[~df['Grade'].isin(excluded_grades)]
    
    # 按照官方 Wi 规则
    def get_weight(row):
        code, name = row['Code'], row['Name'].lower()
        level = code[4]
        if 'thesis' in name or 'project' in name: return 8
        weights = {'1': 0, '2': 2, '3': 3}
        return weights.get(level, 4)

    df['Wi'] = df.apply(get_weight, axis=1)
    
    sem_map = {"S1": 1, "S2": 2}
    df['SortKey'] = df['Year'] * 10 + df['Semester'].map(sem_map)
    df = df.sort_values('SortKey')
    
    history = []
    unique_sems = df['SortKey'].unique()
    
    for skey in unique_sems:
        current_sem_df = df[df['SortKey'] == skey]
        cumulative_df = df[df['SortKey'] <= skey]
        
        sem_wam = (current_sem_df['Mark'] * current_sem_df['CP']).sum() / current_sem_df['CP'].sum()
        cum_wam = (cumulative_df['Mark'] * cumulative_df['CP']).sum() / cumulative_df['CP'].sum()
        
        # EIHWAM 公式
        eih_num = (cumulative_df['Mark'] * cumulative_df['CP'] * cumulative_df['Wi']).sum()
        eih_den = (cumulative_df['CP'] * cumulative_df['Wi']).sum()
        cum_eihwam = eih_num / eih_den if eih_den != 0 else 0
        
        history.append({
            "Label": current_sem_df['Display_Label'].iloc[0],
            "Sem_Avg": round(float(sem_wam), 4),
            "Cum_WAM": round(float(cum_wam), 4),
            "Cum_EIHWAM": round(float(cum_eihwam), 4)
        })
    
    return pd.DataFrame(history), df

# --- UI 展示 ---
st.set_page_config(page_title="USYD Precision WAM", layout="wide")
lang_choice = st.sidebar.selectbox("Language / 语言", ["中文", "English"])
t = LANG_DICT["zh"] if lang_choice == "中文" else LANG_DICT["en"]

st.title(t["title"])
uploaded_file = st.file_uploader(t["upload_label"], type="pdf")

if uploaded_file:
    df_raw = extract_data_from_pdf(uploaded_file)
    if not df_raw.empty:
        hist_df, full_data = calculate_metrics(df_raw)
        
        latest = hist_df.iloc[-1]
        c1, c2 = st.columns(2)
        c1.metric(t["result_wam"], f"{latest['Cum_WAM']:.2f}")
        c2.metric(t["result_hwam"], f"{latest['Cum_EIHWAM']:.2f}")

        st.subheader(t["chart_title"])
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x_labels = hist_df['Label']
        lines = [
            (hist_df['Sem_Avg'], t["chart_legend_sem_wam"], 'o--', '#BDBDBD'),
            (hist_df['Cum_WAM'], t["chart_legend_cum_wam"], 's-', '#3498DB'),
            (hist_df['Cum_EIHWAM'], t["chart_legend_cum_eihwam"], 'D-', '#E74C3C')
        ]

        for data, label, style, color in lines:
            # 逻辑：如果是荣誉累计均分，且数据点多于2个，则从第3个点（索引2）开始画
            if label == t["chart_legend_cum_eihwam"] and len(data) > 2:
                plot_x = x_labels[2:]
                plot_y = data[2:]
            else:
                plot_x = x_labels
                plot_y = data

            ax.plot(plot_x, plot_y, style, label=label, color=color, markersize=8, linewidth=2)
            
            for i, val in enumerate(plot_y):
                # 获取对应的 X 轴标签（通过重置后的索引或 .iloc）
                ax.annotate(f"{val:.2f}", 
                            (plot_x.iloc[i], val), 
                            xytext=(0, 8), 
                            textcoords='offset points', 
                            ha='center', 
                            fontweight='bold', 
                            color=color)

        ax.set_ylim(min(hist_df['Sem_Avg'].min(), 60) - 5, 100)
        ax.grid(True, axis='y', linestyle=':', alpha=0.5)
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        st.pyplot(fig)
    else:
        st.error("Data Extraction Failed.")
