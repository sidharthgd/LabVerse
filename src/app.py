from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import io
import pandas as pd  # Assuming you'll use pandas for your functionality

app = FastAPI()

#allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


@app.post("/upload")
async def upload_file(query: str = Form(...), file: Optional[UploadFile] = File(None)):  
    print ("Received request")
    try:

        #no file provided
        if (file is None):
            return JSONResponse(content={"message": f"Query received! No File.", "query": query}, status_code=200)
        
        else:
            #print(f"Received query: {query}")
            print(f"Received file: {file.filename}")

            file_content = await file.read()
            file_like_object = io.BytesIO(file_content)

            df = pd.read_csv(file_like_object)

            # Now you can perform any data processing on df
            result = df.head()  # Example: get the first few rows of the dataframe

            response_data = {"message": f"File {file.filename} processed successfully!", "query": query, "data": result.to_dict()}
            return JSONResponse(content=response_data, status_code=200)

    except Exception as e:
        print(f"Error processing file: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=400)
