@echo off
echo "Starting..."

REM 檢查並安裝 virtualenv 工具
pip install virtualenv

REM 創建虛擬環境，啟動並安裝依賴
virtualenv III-KNITMATCH_full-venv
call III-KNITMATCH_full-venv\Scripts\activate.bat

REM 在虛擬環境中升級 pip，安裝依賴並運行 Streamlit 應用
pip install --upgrade pip
pip install -r requirements.txt
streamlit run main.py


echo "Done..."
