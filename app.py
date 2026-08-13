import pandas as pd
import plotly.express as px
import streamlit as st

st.title("Excel 箱形圖分析器")

# 1. 建立檔案上傳組件
uploaded_file = st.file_uploader("請上傳您的 Excel 檔案", type=["xlsx", "xls"])

if uploaded_file is not None:
  try:
    # 2. 讀取 Excel 數據
    df = pd.read_excel(uploaded_file)

    # 顯示前五筆數據讓用戶確認
    st.write("數據預覽：")
    st.dataframe(df.head())

    # 強制將所有欄位嘗試轉換為數字
    for col in df.columns:
      converted = pd.to_numeric(df[col], errors="coerce")
      if converted.notna().sum() > (len(df) * 0.5):
        df[col] = converted

    # 3. 篩選出所有「數字型態」的欄位（畫圖用）
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()

    # 4. 篩選出適合用來「分組」的欄位（包含文字、或種類較少的數字）
    all_columns = df.columns.tolist()

    if len(numeric_columns) > 0:
      col1, col2, col3 = st.columns(3)

      with col1:
        selected_col = st.selectbox(
            "請選擇要畫箱形圖的欄位：", numeric_columns
        )

      with col2:
        # 讓用戶選擇要依據哪一欄來分組（例如 Step 或 Phase），預設不分組
        group_col = st.selectbox(
            "請選擇分組欄位（選填）：", ["無"] + all_columns
        )

      with col3:
        # 讓用戶自由控制要不要顯示那麼多密集的點
        point_option = st.selectbox(
            "原始數據點顯示方式：",
            ["outliers", "none", "all"],
            index=0,  # 預設改為 outliers（只顯示極端值），圖表才會乾淨
            format_func=lambda x: {
                "outliers": "僅顯示離群值 (推薦)",
                "none": "不顯示數據點",
                "all": "顯示所有數據點",
            }[x],
        )

      # 5. 根據用戶選擇決定分組參數
      x_param = None if group_col == "無" else group_col
      color_param = None if group_col == "無" else group_col

      # 6. 畫圖並呈現
      fig = px.box(
          df,
          x=x_param,
          y=selected_col,
          color=color_param,
          points=point_option,
          title=f"欄位【{selected_col}】的箱形圖分析結果",
      )

      # 稍微把圖表縮小一點，避免左右拉太寬
      fig.update_layout(boxmode="group", width=800, height=600)

      st.plotly_chart(fig)

    else:
      st.error(
          "這個 Excel 檔案裡面似乎沒有任何數字欄位，或無法成功轉換為數字喔！"
      )

  except Exception as e:
    st.error(f"讀取檔案時出錯了：{e}")

