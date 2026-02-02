// Exam Timer and Auto-save functionality
class ExamTimer {
    constructor(timeRemaining, examId, currentQuestionId) {
        this.timeRemaining = timeRemaining;
        this.examId = examId;
        this.currentQuestionId = currentQuestionId;
        this.timerInterval = null;
        this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    start() {
        this.updateDisplay();
        this.timerInterval = setInterval(() => {
            if (this.timeRemaining <= 0) {
                this.handleTimeout();
                return;
            }
            this.timeRemaining--;
            this.updateDisplay();
        }, 1000);
    }

    updateDisplay() {
        const hours = Math.floor(this.timeRemaining / 3600);
        const minutes = Math.floor((this.timeRemaining % 3600) / 60);
        const seconds = this.timeRemaining % 60;
        
        let timeString = '';
        if (hours > 0) {
            timeString = `${hours.toString().padStart(2, '0')}:`;
        }
        timeString += `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        const timerElement = document.getElementById('time-remaining');
        if (timerElement) {
            timerElement.textContent = timeString;
        }

        // Update timer styling based on remaining time
        const timerContainer = document.getElementById('timer');
        if (timerContainer) {
            if (this.timeRemaining <= 300) { // 5 minutes
                timerContainer.className = 'timer-display timer-danger';
            } else if (this.timeRemaining <= 600) { // 10 minutes
                timerContainer.className = 'timer-display timer-warning';
            }
        }
    }

    handleTimeout() {
        clearInterval(this.timerInterval);
        alert('Time is up! Your exam will be submitted automatically.');
        this.autoSubmitExam();
    }

    autoSubmitExam() {
        const form = document.getElementById('final-submit-form');
        if (form) {
            form.submit();
        }
    }

    saveAnswer(questionId, choiceId) {
        return fetch(`/student/exam/${this.examId}/save-answer/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken
            },
            body: JSON.stringify({
                question_id: questionId,
                choice_id: choiceId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                console.error('Failed to save answer:', data.error);
                if (data.error === 'Exam time expired') {
                    this.handleTimeout();
                }
            }
            return data.success;
        })
        .catch(error => {
            console.error('Error saving answer:', error);
            return false;
        });
    }
}

// Auto-save functionality
function selectChoice(choiceId) {
    // Update UI
    const choiceOptions = document.querySelectorAll('.choice-option');
    choiceOptions.forEach(option => {
        option.classList.remove('selected');
    });

    const radioButtons = document.querySelectorAll('input[type="radio"]');
    radioButtons.forEach(radio => {
        if (radio.value == choiceId) {
            radio.checked = true;
            radio.closest('.choice-option').classList.add('selected');
        } else {
            radio.checked = false;
        }
    });

    // Save answer if timer exists
    if (window.examTimer) {
        const currentQuestionId = window.currentQuestionId || null;
        if (currentQuestionId) {
            window.examTimer.saveAnswer(currentQuestionId, choiceId);
        }
    }

    // Update progress
    updateProgress();
}

function updateProgress() {
    const answeredButtons = document.querySelectorAll('.question-num-btn.answered').length;
    const currentIsAnswered = document.querySelector('input[type="radio"]:checked') ? 1 : 0;
    const currentButton = document.querySelector('.question-num-btn.current');
    
    // If current question is answered, mark the navigation button
    if (currentIsAnswered && currentButton) {
        currentButton.classList.add('answered');
    }
    
    const totalQuestions = document.querySelectorAll('.question-num-btn').length;
    const totalAnswered = answeredButtons + currentIsAnswered;
    
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    
    if (progressBar && progressText) {
        const percentage = (totalAnswered / totalQuestions) * 100;
        progressBar.style.width = percentage + '%';
        progressText.textContent = `${totalAnswered} of ${totalQuestions} answered`;
    }
}

function submitExam() {
    if (confirm('Are you sure you want to submit the exam? You cannot make changes after submission.')) {
        document.getElementById('final-submit-form').submit();
    }
}

// Prevent accidental page navigation
window.addEventListener('beforeunload', function(e) {
    if (window.examTimer && window.examTimer.timeRemaining > 0) {
        e.preventDefault();
        e.returnValue = 'Your exam is in progress. Are you sure you want to leave?';
    }
});