# 🚀 AI-Driven Talent Management System - Quick Start

## ⚡ One-Command Setup & Run

### Option 1: Direct Python (Recommended)
```bash
python app.py
```

### Option 2: Windows Batch File
```bash
run.bat
```

### Option 3: Linux/Mac Shell Script
```bash
chmod +x run.sh
./run.sh
```

## 🌐 Access the Application

Once running, open your browser and go to:
**http://localhost:5000**

## 📋 What You Get

### 🏠 **Landing Page** (`/`)
- Professional title page with "Get Started" button
- Key features showcase
- Statistics and animations
- Smooth navigation

### 📊 **Dashboard** (`/dashboard`)
- Real-time statistics
- Key features overview
- How it works workflow
- Future roadmap with progress indicators

### 🔧 **Prototype Page** (`/prototype`)
- Drag & drop file upload interface
- CSV file validation
- Real-time data preview
- Upload progress indicators

### 📈 **Results Page** (`/results`)
- **Overview Tab**: Charts, graphs, top 10 ranked employees
- **Recommendations Tab**: Top 3 employee recommendations per project
- **Analytics Tab**: Skill analysis, proficiency distribution
- **Detailed Results Tab**: Complete matching table with filtering

## 🎯 Key Features

✅ **Intelligent AI Matching** - Multi-criteria optimization algorithm
✅ **Real-time Analytics** - Interactive charts and visualizations
✅ **Dynamic Data Loading** - Automatic Excel to CSV conversion
✅ **Responsive Design** - Works on all devices
✅ **Professional UI/UX** - Modern, clean interface
✅ **Complete Documentation** - Comprehensive guides and help

## 📊 Sample Data

The application automatically creates sample data if no CSV files are found:
- **10 Sample Employees** with diverse skills and roles
- **5 Sample Projects** across different domains
- **Realistic matching scenarios** for demonstration

## 🔧 Technical Details

- **Backend**: Python Flask with AI algorithms
- **Frontend**: HTML5, CSS3, JavaScript (Chart.js)
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **Matching Algorithm**: TF-IDF + Cosine Similarity + Multi-criteria optimization

## 📁 Project Structure

```
Techolution/
├── app.py                 # Main application (run this!)
├── requirements.txt       # Python dependencies
├── run.bat               # Windows batch file
├── run.sh                # Linux/Mac shell script
├── README.md             # Full documentation
├── QUICK_START.md        # This file
├── templates/            # HTML templates
├── static/               # CSS & JavaScript
└── datasets/             # Data storage
```

## 🚨 Troubleshooting

1. **Port 5000 in use**: The app will show an error if port 5000 is busy
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **Browser issues**: Try refreshing the page or clearing cache
4. **Data upload issues**: Ensure CSV files have correct column names

## 🎉 Success!

When you see this message, you're ready to go:
```
✅ Application ready!
🌐 Open your browser and go to: http://localhost:5000
```

**That's it! Your AI-Driven Talent Management System is now running!** 🎊
