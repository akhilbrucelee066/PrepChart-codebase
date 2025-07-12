# PrepChart - CSV-Based Progress Tracker  

**Live Demo:** [https://prep-chart.vercel.app/](https://prep-chart.vercel.app/)  

## Overview  
PrepChart is a Python Flask web application designed to visualize and track preparation progress using CSV files. It helps users monitor their tasks (like coding problems, study plans, or to-do lists) by breaking down data into difficulty levels and categories, providing a clear progress journey with checkpoints.  

## Features  
- **CSV Data Visualization:** Upload and view your progress in a structured table format (rows & columns).  
- **Progress Tracking:** Track completed and pending tasks with visual indicators.  
- **Difficulty/Category Breakdown:** Organize tasks by difficulty (Easy/Medium/Hard) or custom types.  
- **Chart Management:**  
  - **View Charts:** See all existing progress charts.  
  - **Add New Chart:** Upload a CSV file via drag-and-drop or file selection.  
- **Simple UI/UX:** Clean and intuitive interface for easy navigation.  

## Tech Stack  
- **Backend:** Python (Flask)  
- **Frontend:** HTML, CSS, JavaScript  
- **Deployment:** Vercel  

## Installation & Setup  
1. Clone the repository:  
   ```sh  
   git clone https://github.com/akhilbrucelee066/PrepChart-codebase.git  
   ```  
2. Navigate to the project directory:  
   ```sh  
   cd PrepChart-codebase  
   ```  
3. Install dependencies:  
   ```sh  
   pip install -r requirements.txt  
   ```  
4. Run the Flask application:  
   ```sh  
   python app.py  
   ```  
5. Open [http://localhost:5000](http://localhost:5000) in your browser.  

## Usage  
1. **Adding a Chart:**  
   - Go to the "Add Chart" section.  
   - Upload a CSV file (drag-and-drop or file selection).  
   - The system will parse and display your progress.  

2. **Viewing Charts:**  
   - The "Charts" section lists all existing progress charts.  
   - Click on a chart to see detailed breakdowns (difficulty/type-wise).  

## License  
This project is open-source under the [MIT License](LICENSE).

---  
Developed by [Pranay Akhil Jeedimalla](https://github.com/akhilbrucelee066)