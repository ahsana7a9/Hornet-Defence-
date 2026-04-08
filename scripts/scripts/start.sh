#!/bin/bash

echo "Starting Hornet Defence..."

cd backend && uvicorn main:app --reload &
cd frontend && npm run dev
