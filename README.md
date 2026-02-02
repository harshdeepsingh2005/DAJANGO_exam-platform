# NovaExam  Django Online Examination Platform

NovaExam is a complete online examination platform built with Django, featuring separate interfaces for students and administrators. This is a production-ready MVP designed for educational institutions.

## Features

### For Students
- ✅ User registration and authentication
- ✅ View available exams with status indicators
- ✅ Take MCQ exams with real-time timer
- ✅ Auto-save answers during exam
- ✅ Question navigation with progress tracking
- ✅ Auto-submit when time expires
- ✅ View detailed results after completion
- ✅ Responsive design for mobile and desktop

### For Administrators
- ✅ Admin dashboard with statistics
- ✅ Create and manage exams
- ✅ Add MCQ questions with 4 choices each
- ✅ Publish/unpublish exams
- ✅ View student attempts and scores
- ✅ Manage exam timing and availability
- ✅ Django admin integration

### Technical Features
- ✅ Secure exam timer with server-side validation
- ✅ One attempt per exam per student
- ✅ AJAX-based answer auto-saving
- ✅ Page refresh persistence
- ✅ Mobile-responsive Bootstrap UI
- ✅ Clean, academic-focused design
- ✅ SQLite database (easily upgradable)

## Technology Stack

- **Backend**: Django 5.1+
- **Frontend**: Django Templates + Bootstrap 5.1
- **Database**: SQLite (development)
- **JavaScript**: Vanilla JS (timer, auto-save)
- **Styling**: Bootstrap + Custom CSS
- **Authentication**: Django built-in auth

## Quick Start

### 1. Clone and Setup

```bash
# Navigate to project directory
cd exam_platform

# Virtual environment is already configured
# Install dependencies (Django is already installed)
```

### 2. Setup Database

```bash
# Apply migrations
python manage.py migrate

# Create sample data (optional)
python manage.py create_sample_data
```

### 3. Create Superuser (if not using sample data)

```bash
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

## Running Tests

### Unit tests

Use Django's test runner:

```bash
python manage.py test
```

### Browser-based tests (Selenium)

There is an optional end-to-end browser test that uses Selenium and Chrome/Chromium:

1. Install test-only dependencies:

```bash
pip install -r requirements-test.txt
```

2. Ensure you have Chrome/Chromium installed and a matching `chromedriver` on your `PATH`.

3. Run the browser tests (they are included in the normal test run):

```bash
python manage.py test tests.test_browser_flow
```

## Default Login Credentials (Sample Data)

- **Admin**: `admin` / `admin123`
- **Student**: `student` / `student123`

## Project Structure

```
exam_platform/
│
├── accounts/           # User authentication
├── exams/             # Exam management & student interface  
├── attempts/          # Exam attempt tracking
├── results/           # Result display
├── templates/         # HTML templates
├── static/           # CSS, JS, images
├── exam_platform/    # Main project settings
└── manage.py         # Django management script
```

## App Breakdown

### 🔐 accounts/
- User registration and login
- Uses Django's built-in authentication
- Simple registration form

### 📝 exams/
- **Models**: Exam, Question, Choice
- **Student Views**: Dashboard, exam taking interface
- **Admin Views**: Exam and question management
- **Templates**: Student and admin interfaces

### 📊 attempts/
- **Models**: Attempt, Answer  
- Tracks student exam attempts
- AJAX answer saving endpoint
- One attempt per exam per student

### 📈 results/
- Display exam results to students
- Score calculation and pass/fail status
- Detailed performance statistics

## Key Models

### Exam
```python
- title, description
- duration_minutes  
- start_time, end_time
- is_published
```

### Question  
```python
- exam (ForeignKey)
- text, marks
```

### Choice
```python
- question (ForeignKey)
- text, is_correct
```

### Attempt
```python
- student, exam (ForeignKeys)
- start_time, end_time
- is_submitted, score
```

## Core Exam Rules

1. **MCQ Only**: All questions are multiple choice with 4 options
2. **One Attempt**: Students can only attempt each exam once
3. **Timed Exams**: Server-side timer enforcement
4. **Auto-save**: Answers saved automatically via AJAX
5. **Auto-submit**: Exam submits automatically when time expires
6. **Page Refresh Safe**: Answers persist across page reloads
7. **Read-only Results**: No changes after submission

## URL Structure

```
/                          → Student Dashboard
/accounts/login/           → Student/Admin Login
/accounts/register/        → Student Registration
/student/                  → Student Dashboard
/student/exam/<id>/        → Exam Details
/student/exam/<id>/take/   → Take Exam
/admin-panel/              → Admin Dashboard
/admin-panel/exams/        → Manage Exams
/admin/                    → Django Admin
```

## NovaExam Portal  Page Flow & Route Structure

### `/` (Landing Page)

- Hero + CTAs
	- **Login**  `/accounts/login/`
	- **Register**  `/accounts/register/`
	- **Get Started**
		- Not authenticated  `/accounts/register/`
		- Authenticated
			- Student  `/student/`
			- Admin  `/admin-panel/`
- How It Works / Features (Student & Admin)
- Role-based CTAs
	- Student Dashboard  `/student/`
	- Admin Panel  `/admin-panel/`
- Footer: Login, Register, Terms, Support

### Authentication

- `/accounts/login/`
	- Student login  `/student/`
- `/accounts/register/`
	- New user registration  `/student/`
- `/accounts/login/?next=/admin-panel/`
	- Admin login  `/admin-panel/`

### Student Flow

- `/student/` (Dashboard)
	- Exam lists: Available / In Progress / Completed
	- Recent attempts
	- Navbar: Profile  `/student/profile/`

- `/student/exam/<exam_id>/` (Exam Detail)
	- Start Exam  confirmation  `/student/exam/<exam_id>/start/`
		- Creates attempt, starts timer, redirects to Take Exam

- `/student/exam/<exam_id>/start/` (Start Exam)
	- Confirmation and attempt creation
	- Redirects to `take` route

- `/student/exam/<exam_id>/take/?q=N` (Take Exam)
	- One question at a time
	- Next / Previous navigation
	- Question navigator sidebar
	- Auto-save answers
	- Persistent timer
	- **Review & Submit**  `/student/exam/<exam_id>/review/`

- `/student/exam/<exam_id>/review/` (Review Answers)
	- Question table: Answered / Unanswered / Marked
	- Go-to-question links
	- **Submit Exam**
		- Locks attempt
		- Auto-grades
		- Redirects to Result

- `/results/result/<attempt_id>/` (Result Page)
	- Score, pass/fail, time taken
	- Per-question breakdown and answer review

- `/student/profile/`
	- User details
	- Attempt history
	- Performance stats

### Admin Flow (Custom Admin Panel)

- `/admin-panel/` (Admin Dashboard)
	- Metrics: total students, exams, attempts
	- Recent attempts table
	- Quick actions:
		- Create Exam  `/admin-panel/exams/create/`
		- Manage Exams  `/admin-panel/exams/`
		- Django Admin  `/admin/`
		- Student View  `/student/`

- `/admin-panel/exams/` (Manage Exams)
	- Per-exam actions:
		- Manage Questions  `/admin-panel/exams/<id>/questions/`
		- View Attempts  `/admin-panel/exams/<id>/attempts/`
			- Attempt detail  `/results/result/<attempt_id>/`
		- View Analytics  `/admin-panel/exams/<id>/stats/`
		- Edit Exam  `/admin-panel/exams/<id>/edit/`
		- Publish / Unpublish  `/admin-panel/exams/<id>/toggle-publish/`

- `/admin-panel/exams/create/`
	- Create new exam

- `/admin-panel/exams/<id>/questions/`
	- List / add / edit / delete questions

- `/admin-panel/exams/<id>/attempts/`
	- Attempts list
	- Links to result detail

- `/admin-panel/exams/<id>/stats/`
	- Average score, attempt distribution
	- Question accuracy, time analytics

### System Admin (Django)

- `/admin/`
	- Users, groups & permissions
	- Exams, questions, choices
	- Attempts, answers

### Global Guards & Rules

- **Auth guard**
	- Not logged in  `/accounts/login/?next=<requested_url>`
- **Role guard**
	- Student  `/student/`
	- Admin  `/admin-panel/`
- **Exam state guard**
	- Available  start allowed
	- In Progress  resume only
	- Completed  result view only

## Customization

### Styling
- Edit `static/css/style.css` for custom styles
- Bootstrap variables in `templates/base.html`
- Color scheme defined in CSS variables

### Exam Settings
- Pass percentage: 60% (configurable in `results/views.py`)
- Timer warnings: 10min & 5min (configurable in JS)
- Question marks: Default 1 (configurable per question)

### Business Logic
- Modify exam rules in `attempts/models.py`
- Customize scoring in `Attempt.calculate_score()`
- Adjust timer behavior in `static/js/exam.js`

## Deployment Considerations

### For Production:
1. **Database**: Switch to PostgreSQL/MySQL
2. **Settings**: Update `ALLOWED_HOSTS`, `SECRET_KEY`
3. **Static Files**: Configure `STATIC_ROOT` and collect static files
4. **Security**: Enable HTTPS, set secure cookie settings
5. **Email**: Configure email backend for notifications
6. **Caching**: Add Redis for session caching
7. **Media**: Configure file upload handling if needed

### Environment Variables:
```python
# In production settings.py
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
```

## Browser Compatibility

- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+  
- ✅ Edge 80+
- ✅ Mobile browsers

## License

MIT License - Feel free to use for educational purposes.

## Support

This is a complete, working Django application following best practices:

- Clean architecture with proper app separation
- Security considerations built-in
- Mobile-responsive design  
- Comprehensive error handling
- Production-ready structure

Perfect for:
- College projects
- Educational institutions
- Learning Django development
- MVP for exam platforms
- Portfolio demonstration

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

**Built with ❤️ using Django & Bootstrap**