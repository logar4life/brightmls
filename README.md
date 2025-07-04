# BrightMLS Scraper API

This project provides a FastAPI-based web service to scrape real estate data from BrightMLS, save it as a CSV, and serve the data via API endpoints. It is designed for easy integration with automation tools like n8n and AI services like OpenAI.

## Features
- Scrapes real estate data from BrightMLS and saves it to `brightmls_data.csv`.
- Provides API endpoints to trigger scraping and download the CSV.
- Ready for integration with n8n workflows and OpenAI for data-driven automation and Q&A.

---

## Setup Instructions

### 1. Clone the Repository
```
git clone <your-repo-url>
cd brightmls
```

### 2. Install Dependencies
It is recommended to use a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the API Server
```
uvicorn brightmls_api:app --reload
```
The API will be available at `http://localhost:8000` by default.

---

## API Endpoints

### `POST /scrape`
- **Description:** Triggers the BrightMLS scraping process. Scraped data is saved to `brightmls_data.csv`.
- **Response:** JSON with scrape status and row count.

### `GET /csv`
- **Description:** Downloads the latest CSV file with the scraped data.
- **Response:** CSV file download.

### `GET /`
- **Description:** Welcome message and API status.

---

## Using with n8n

### Example Workflow
1. **HTTP Request Node**
   - **Method:** POST
   - **URL:** `http://localhost:8000/scrape`
   - **Description:** Triggers the scraper.

2. **HTTP Request Node** (after scrape completes)
   - **Method:** GET
   - **URL:** `http://localhost:8000/csv`
   - **Description:** Downloads the CSV file.
   - **Response Format:** File

3. **Read Binary File Node** (if needed)
   - Parse the CSV for further processing.

4. **OpenAI Node**
   - Use the parsed CSV data as input for OpenAI prompts (e.g., "What is the average price?", "List all properties in city X.").

### Tips
- Use n8n's built-in CSV and data transformation nodes to process the CSV.
- Use the OpenAI node to ask questions about the data, passing relevant CSV rows as context.

---

## Using with OpenAI
- After downloading and parsing the CSV in n8n, you can send relevant data to the OpenAI node as part of your prompt.
- Example prompt: `"Given the following property data: <CSV_ROWS>, what is the average price in Philadelphia?"`

---

## Troubleshooting
- If you get a `Permission denied` error when saving the CSV, make sure the file is not open in another program (like Excel).
- Ensure Chrome is installed for Selenium to work.
- Update credentials in `brightmls.py` as needed.

---

## License
MIT 