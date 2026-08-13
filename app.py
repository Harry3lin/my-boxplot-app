import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(layout="wide")  # 讓網頁變寬，方便左右並排兩張圖
st.title("機台測試最終數值箱形圖分析器")

uploaded_file = st.file_uploader("請上傳您的 Excel 檔案", type=["xlsx", "xls"])

if uploaded_file is not None:
  try:
    # 1. 讀取原始 Excel 數據
    df = pd.read_excel(uploaded_file)

    # 2. 強制轉換特定欄位型態
    df["Pressure(Pa)"] = pd.to_numeric(df["Pressure(Pa)"], errors="coerce")
    df["Leak"] = pd.to_numeric(df["Leak"], errors="coerce")
    df["Step"] = pd.to_numeric(df["Step"], errors="coerce")

    # 3. 核心過濾邏輯：找出每台 SN 的最大 Step 的「最後一筆資料」
    final_records = []

    # 依 SN 分組處理
    for sn, sn_group in df.groupby("SN"):
      if pd.isna(sn):
        continue

      # 找到該 SN 的最大 Step 數值
      max_step = sn_group["Step"].max()

      # 篩選出屬於該最大 Step 的所有數據
      max_step_data = sn_group[sn_group["Step"] == max_step]

      if not max_step_data.empty:
        # 取出這個最大 Step 裡面的「最後一筆」（即最終完工值，如 7074 和 -0.74）
        final_row = max_step_data.iloc[-1]
        final_records.append(final_row)

    # 將過濾出來的最終資料組合成新的 DataFrame
    filtered_df = pd.DataFrame(final_records)

    if not filtered_df.empty:
      # 🌟 建立控制開關：預設不勾選（自動過濾極端值，讓圖表好看）
      # 勾選時才顯示所有極端值
      show_outliers = st.checkbox(
          "顯示所有極端值 (outlier)",
          value=False,
          help="不勾選時，系統會自動剔除 Pressure < 5000 且 Leak > 5 的明顯異常數據，以便放大觀看正常箱子分佈。",
      )

      # 🌟 根據開關狀態決定是否過濾數據
      if not show_outliers:
        # 只保留正常範圍的數據：Pressure >= 5000 且 Leak <= 5
        plot_df = filtered_df[
            (filtered_df["Pressure(Pa)"] >= 5000) & (filtered_df["Leak"] <= 5)
        ]
      else:
        plot_df = filtered_df

      # 數據預覽與統計資訊
      st.subheader(f"📊 當前圖表分析共包含 {len(plot_df)} 台 SN 的數據")

      # 使用 Streamlit 的欄位組件，將網頁切成左右兩半
      col1, col2 = st.columns(2)

      with col1:
        st.write("### Pressure(Pa) 最終值分佈")
        # 繪製 Pressure 箱形圖
        fig_pressure = px.box(
            plot_df,
            y="Pressure(Pa)",
            points="all",  # 顯示數據點
            hover_data=["SN", "Step"],  # 滑鼠移上去顯示詳細資訊
            title="各機台最大 Step 的 Pressure 最終值",
        )
        fig_pressure.update_traces(marker_color="#1f77b4", boxmean=True)
        fig_pressure.update_layout(height=600)
        st.plotly_chart(fig_pressure, use_container_width=True)

      with col2:
        st.write("### Leak 最終值分佈")
        # 繪製 Leak 箱形圖
        fig_leak = px.box(
            plot_df,
            y="Leak",
            points="all",
            hover_data=["SN", "Step"],
            title="各機台最大 Step 的 Leak 最終值",
        )
        fig_leak.update_traces(marker_color="#ff7f0e", boxmean=True)
        fig_leak.update_layout(height=600)
        st.plotly_chart(fig_leak, use_container_width=True)

      # 在下方附帶顯示過濾後的數據清單，供你對帳確認
      with st.expander("點擊查看當前圖表數據明細"):
        st.dataframe(
            plot_df[["SN", "Step", "Pressure(Pa)", "Leak"]].reset_index(
                drop=True
            )
        )

    else:
      st.error("無法從 Excel 檔案中成功解析出 SN、Step、Pressure 或 Leak 數據！")

  except Exception as e:
    st.error(f"執行邏輯時出錯了：{e}")
