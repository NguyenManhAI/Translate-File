 Translate file 

- Install library:  pip install -r requirements.txt

- Run app:  uvicorn app:app --host 0.0.0.0 --port 5000 --reload

- Run app without interrupting when closing the terminal:   nohup uvicorn app:app --host 0.0.0.0 --port 5000 --reload > uvicorn.log 2>&1 &

- Replace openai api_key before running app
