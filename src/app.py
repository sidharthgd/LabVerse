from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import io
from io import BytesIO
import pandas as pd  # Assuming you'll use pandas for your functionality

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

#allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


@app.post("/upload")
async def upload_file(query: str = Form(...), file: UploadFile = File(...)):
    # Read the uploaded file into a pandas DataFrame
    try:
        # Determine file type and read accordingly
        if file.filename.endswith('.csv'):
            # Read CSV file into DataFrame
            contents = await file.read()
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith('.xlsx'):
            # Read Excel file into DataFrame
            contents = await file.read()
            df = pd.read_excel(io.BytesIO(contents))
        else:
            return {"error": "Invalid file type. Only CSV and Excel files are supported."}

        # Get the first few rows of the dataframe (head)
        head_df = df.head()  # You can specify the number of rows, default is 5

        # Convert the head DataFrame to CSV or Excel
        if file.filename.endswith('.csv'):
            output = BytesIO()
            head_df.to_csv(output, index=False)
            output.seek(0)
            return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=head.csv"})
        
        elif file.filename.endswith('.xlsx'):
            output = BytesIO()
            head_df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=head.xlsx"})

    except Exception as e:
        return {"error": str(e)}

@app.post("/chat")
async def chat_endpoint(request: QueryRequest):  
    print ("Received chat request")
    try:
        query = request.query
        print(f"Received query: {query}")
        return JSONResponse(content={"message": f"Query received!: {query}", "query": query}, status_code=200)

    except Exception as e:
        print(f"Error processing file: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=400)