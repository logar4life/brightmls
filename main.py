from fastapi import FastAPI, HTTPException
from brightmls import run_brightmls_scraper
import os
import openai
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel

app = FastAPI(title="BrightMLS Minimal API", version="1.0.0")

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CSV_FILE = "brightmls_data.csv"

class ChatRequest(BaseModel):
    message: str
    include_csv_sample: bool = False
    max_rows: int = 10

class ChatResponse(BaseModel):
    response: str
    csv_sample: str = None
    row_count: int

@app.post("/scrape")
async def start_scrape():
    """Run the BrightMLS scraper and save CSV."""
    try:
        print("🚀 Starting BrightMLS scraper...")
        result = run_brightmls_scraper()
        
        if result['success']:
            print(f"✅ Scraper completed successfully: {result['message']}")
            return {
                "status": "success",
                "message": result['message'],
                "row_count": result['row_count'],
                "new_data": result['new_data'],
                "timestamp": result['timestamp']
            }
        else:
            print(f"❌ Scraper failed: {result['message']}")
            return {
                "status": "error",
                "message": result['message'],
                "row_count": result['row_count'],
                "new_data": result['new_data'],
                "timestamp": result['timestamp']
            }
    except KeyboardInterrupt:
        print("🛑 Scraper interrupted by user")
        return {
            "status": "interrupted",
            "message": "Scraper was interrupted by user",
            "row_count": 0,
            "new_data": False,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        print(f"❌ Fatal scraper error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scraper error: {str(e)}")

@app.post("/stop")
async def stop_scraper():
    """Stop the running scraper process."""
    try:
        # This is a placeholder - in a real implementation you'd need to track the scraper process
        # For now, we'll just return a message indicating the endpoint exists
        return {
            "status": "stopped",
            "message": "Scraper stop requested. Note: This endpoint is a placeholder - implement process tracking for full functionality.",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping scraper: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_with_csv(request: ChatRequest):
    """Chat with CSV data using OpenAI."""
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    if not os.path.exists(CSV_FILE):
        raise HTTPException(status_code=404, detail="CSV file not found. Please run the scraper first.")
    try:
        df = pd.read_csv(CSV_FILE)
        csv_sample = None
        if request.include_csv_sample:
            sample_df = df.head(request.max_rows)
            csv_sample = sample_df.to_csv(index=False)
            csv_data = f"Sample data (first {request.max_rows} rows):\n{csv_sample}\n\nTotal rows in dataset: {len(df)}"
        else:
            csv_data = df.to_csv(index=False)
        prompt = f"""
You are a helpful assistant that analyzes real estate data from BrightMLS.\n\nUser Question: {request.message}\n\nHere is the CSV data to analyze:\n{csv_data}\n\nPlease provide a detailed, helpful response based on the data above. If the question cannot be answered from the available data, please say so explicitly and suggest what additional information might be needed.\n\nFormat your response in a clear, professional manner with proper formatting where appropriate.
"""
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a real estate data analyst assistant. Provide clear, accurate analysis based on the provided CSV data."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        ai_response = response.choices[0].message.content
        return ChatResponse(
            response=ai_response,
            csv_sample=csv_sample,
            row_count=len(df)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
