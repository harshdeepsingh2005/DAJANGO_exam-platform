# Django Online Examination Platform

A complete online examination platform built with Django, featuring separate interfaces for students and administrators. This is a production-ready MVP designed for educational institutions.

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