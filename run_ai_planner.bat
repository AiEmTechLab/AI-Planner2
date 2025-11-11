@echo off
cd /d "C:\Users\ryousif\Projects\AI-Planner"
call pip install -r requirements.txt
start http://localhost:8504
streamlit run app.py --server.port 8504
pause
