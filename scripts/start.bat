@echo off

echo Starting Hornet Defence...

cd backend
start cmd /k uvicorn main:app --reload

cd ../frontend
start cmd /k npm run dev
