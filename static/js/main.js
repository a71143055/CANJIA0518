// CANJIA Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => {
                alert.remove();
            }, 150);
        }, 5000);
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.animation = `fadeIn 0.5s ease-in ${index * 0.1}s forwards`;
    });

    // Confirm delete actions
    const deleteForms = document.querySelectorAll('form[action*="delete"]');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('정말 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
                e.preventDefault();
            }
        });
    });

    // Character counter for textareas
    const textareas = document.querySelectorAll('textarea[maxlength]');
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        const charCount = document.createElement('small');
        charCount.className = 'text-muted char-counter';
        charCount.textContent = `0 / ${maxLength}`;
        textarea.parentNode.appendChild(charCount);

        textarea.addEventListener('input', function() {
            const currentLength = this.value.length;
            charCount.textContent = `${currentLength} / ${maxLength}`;
            
            if (currentLength >= maxLength) {
                charCount.classList.add('text-danger');
            } else {
                charCount.classList.remove('text-danger');
            }
        });
    });

    // Auto-save draft for document editing (optional enhancement)
    const documentForm = document.querySelector('form[action*="document"]');
    if (documentForm) {
        const titleInput = documentForm.querySelector('#title');
        const contentTextarea = documentForm.querySelector('#content');
        
        if (titleInput && contentTextarea) {
            // Load saved draft if exists
            const savedDraft = localStorage.getItem('document_draft');
            if (savedDraft && !titleInput.value) {
                const draft = JSON.parse(savedDraft);
                titleInput.value = draft.title || '';
                contentTextarea.value = draft.content || '';
            }

            // Auto-save draft every 30 seconds
            setInterval(() => {
                if (titleInput.value || contentTextarea.value) {
                    const draft = {
                        title: titleInput.value,
                        content: contentTextarea.value,
                        timestamp: new Date().toISOString()
                    };
                    localStorage.setItem('document_draft', JSON.stringify(draft));
                }
            }, 30000);

            // Clear draft on form submit
            documentForm.addEventListener('submit', function() {
                localStorage.removeItem('document_draft');
            });
        }
    }

    // Field card hover effects
    const fieldCards = document.querySelectorAll('.field-card');
    fieldCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });

    // Mobile menu handling
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            setTimeout(() => {
                if (navbarCollapse.classList.contains('show')) {
                    document.body.style.overflow = 'hidden';
                } else {
                    document.body.style.overflow = '';
                }
            }, 300);
        });
    }

    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (navbarCollapse && navbarCollapse.classList.contains('show')) {
            if (!navbarCollapse.contains(e.target) && !navbarToggler.contains(e.target)) {
                navbarToggler.click();
            }
        }
    });

    // Add loading state to buttons
    const buttons = document.querySelectorAll('button[type="submit"]');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 처리 중...';
        });
    });

    // Search functionality (if search input exists)
    const searchInput = document.querySelector('#search');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const searchTerm = this.value.toLowerCase();
                const items = document.querySelectorAll('.searchable-item');
                
                items.forEach(item => {
                    const text = item.textContent.toLowerCase();
                    if (text.includes(searchTerm)) {
                        item.style.display = '';
                    } else {
                        item.style.display = 'none';
                    }
                });
            }, 300);
        });
    }

    console.log('CANJIA application loaded successfully!');
});
