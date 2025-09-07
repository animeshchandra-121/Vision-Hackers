# AI-Driven Talent Management System

An intelligent resource allocation system that matches employees to projects using advanced AI algorithms.

## Features

- **Intelligent Matching**: AI-powered algorithms match employees to projects based on skills, proficiency, availability, and capacity
- **Real-time Analytics**: Comprehensive dashboards with interactive visualizations and performance metrics
- **Dynamic Adaptation**: Real-time re-planning when projects change or new requirements arise
- **Conflict Resolution**: Automatic detection and resolution of resource conflicts
- **Transparency & Audit**: Complete audit trail and explainable AI decisions
- **Conversational Interface**: Natural language queries and commands (future feature)

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python app.py
   ```

3. **Access the Application**:
   Open your browser and go to `http://localhost:5000`

## Usage

### 1. Upload Data
- Navigate to the Prototype page
- Upload your Employees.csv and Projects.csv files
- The system will automatically process and validate the data

### 2. Perform Matching
- Click the "MATCH" button to run the AI matching algorithm
- The system will analyze skills, proficiency, availability, and capacity
- Results will be displayed with detailed explanations

### 3. View Results
- Interactive dashboard with multiple views:
  - **Overview**: Charts and graphs showing data distribution
  - **Recommendations**: Top 3 employee recommendations per project
  - **Analytics**: Detailed skill and proficiency analysis
  - **Detailed Results**: Complete matching results with filtering options

## Data Format

### Employees.csv
Required columns:
- `Emp ID`: Employee identifier
- `Name`: Employee name
- `Skills`: Comma-separated list of skills
- `Role`: Intern, Full Time, or Senior
- `Capacity per week (hrs)`: Weekly capacity in hours
- `Previous Project Description`: Description of previous work
- `Proficiency`: Beginner, Intermediate, or Senior
- `Available Date`: When the employee becomes available
- `Location`: Employee location

### Projects.csv
Required columns:
- `ID`: Project identifier
- `Project_Title`: Project name
- `Domain`: Project domain/technology area
- `Eligibility`: Required employee types
- `Duration`: Project duration in weeks
- `Proficiency`: Required proficiency level
- `Conflicts`: Project conflicts
- `Hard_Deadline`: Project deadline
- `Experience_years`: Required years of experience

## Algorithm Details

The matching algorithm uses multiple criteria:

1. **Skill Match (40%)**: Jaccard similarity between employee skills and project requirements
2. **Proficiency Match (30%)**: Alignment between employee and project proficiency levels
3. **Availability Match (20%)**: Timing compatibility between employee availability and project start
4. **Capacity Match (10%)**: Utilization of employee capacity

## API Endpoints

- `GET /`: Main landing page
- `GET /dashboard`: Dashboard with features and roadmap
- `GET /prototype`: Upload interface
- `GET /results`: Results visualization
- `POST /api/upload`: Upload CSV files
- `POST /api/match`: Perform resource matching
- `GET /api/data`: Get current data status
- `GET /api/results`: Get matching results

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **AI/ML**: TF-IDF vectorization, cosine similarity

## Future Enhancements

- Conversational AI interface
- Voice input/output
- Cost-aware optimization
- Multi-tenant architecture
- Advanced reporting
- API integrations

## Troubleshooting

1. **Port Already in Use**: Change the port in `app.py` (line 200)
2. **Missing Dependencies**: Run `pip install -r requirements.txt`
3. **File Upload Issues**: Ensure CSV files have the correct column names
4. **No Results**: Check that both employee and project data are uploaded

## Support

For issues or questions, please check the console output for error messages or contact the development team.
