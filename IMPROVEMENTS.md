# Project Improvements and New Features

## Design and Functional Inconsistencies

1. **Admin Interface Duplication**  
	- There is both Django’s default admin (`/admin/`) and a custom admin panel (`/admin-panel/`). This is intentional, but can be confusing. Consider:
	  - Adding clearer separation in the UI (e.g., “System Admin” vs “Exam Admin”).
	  - Or gradually moving more management tasks into Django admin and using the custom panel mainly as a friendlier reporting/overview layer.

2. **User Roles and Permissions**  
	- Currently, `is_staff` is used as the only check in `admin_views.is_staff`.  
	- Improvement:
	  - Define explicit groups: `Student`, `ExamAdmin`.  
	  - Restrict admin-panel views with `user_passes_test` checking group membership.  
	  - Optionally expose a simple UI in Django admin to assign these roles.

3. **Exam Flow / Navigation**  
	- Flow is: dashboard → exam detail → start confirmation → take exam → result.  
	- Improvements:
	  - Add a “Review answers” step before final submit (show list of questions with answered/unanswered status and quick links).  
	  - On the student dashboard, show a more explicit “Attempts” section listing last N attempts with direct links to results.

4. **URL Usage**  
	- Most templates correctly use named URLs (e.g. `student:exam_detail`, `admin-panel:exam_list`).  
	- A few places still use hardcoded URLs, e.g. `/admin/` button in `templates/admin/dashboard.html`.  
	- Replace these with `{% url 'admin:index' %}` or other named patterns to keep routing consistent.

5. **Mix of Student and Admin Context in Base Layout**  
	- `templates/base.html` navbar shows both student and admin links when an admin is logged in.  
	- Consider:
	  - Making the visual distinction stronger (e.g., separate “Admin” dropdown).  
	  - Or rendering a lighter student-only header on student pages and a different layout for admin pages.

6. **AJAX + Standard Submit Behavior**  
	- `submit_exam` endpoint is used both for final submit and for AJAX save; this is convenient but conflates responsibilities.  
	- Consider splitting into: `save_answer` (AJAX-only) and `submit_exam` (finalization), which will simplify error handling and logging.

## Suggested New Features

1. **Exam Categories/Tags**  
	- Add a `Category` model (or `tags` ManyToMany) to `Exam` so exams can be filtered (e.g., “Math”, “Programming”, “Mock Test”).  
	- Expose filters on the student dashboard and in the admin exam list.

2. **Per-Question Time Limits (Optional)**  
	- Extend `Question` with an optional `time_limit_seconds`.  
	- When set, the JS timer could show a secondary countdown per question and auto-move to the next question when it reaches zero.

3. **Answer Explanations**  
	- Add an `explanation` field to `Question` or `Choice`.  
	- After completion (and only after submit), show explanations alongside the correct/incorrect status for each question in `result_detail.html`.

4. **Advanced Reporting for Admins**  
	- Extra admin views (or Django admin pages) with:
	  - Per-exam statistics (average score, pass rate, attempt count).  
	  - Per-question difficulty (percentage of students answering correctly).  
	  - Student progress over time.

5. **Student Profile & History Page**  
	- Dedicated page under `/student/profile/` summarizing:  
	  - Basic account info.  
	  - List of all attempts with status and score.  
	  - Quick links to result details.

6. **Email Notifications (Optional)**  
	- Send email when:  
	  - A new exam is published (to all or selected students).  
	  - A student completes an exam (confirmation + result summary).  
	- Could be implemented with Django signals or simple calls in views.

7. **Better Mobile Experience**  
	- Overall design already uses Bootstrap and is responsive, but specific improvements:  
	  - Ensure the question navigation panel in `take_exam.html` behaves well on very small screens (e.g., collapsible panel).  
	  - Use larger hit areas for question number buttons and options on mobile.

8. **Testing & QA Improvements**  
	- Add unit tests for:  
	  - Exam availability logic (start/end time checks).  
	  - One-attempt-per-exam enforcement.  
	  - Score calculation + pass/fail thresholds.  
	- Add a few Selenium/Playwright-style smoke tests for login, take exam, and view results.
