document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('ticketForm');
    const generateBtn = document.getElementById('generateBtn');
    const generateText = document.getElementById('generateText');
    const generateSpinner = document.getElementById('generateSpinner');
    
    const previewSection = document.getElementById('previewSection');
    const previewSummary = document.getElementById('previewSummary');
    const previewDescription = document.getElementById('previewDescription');
    const charCounter = document.querySelector('.char-counter');
    
    const editAgainBtn = document.getElementById('editAgainBtn');
    const createTicketBtn = document.getElementById('createTicketBtn');
    const createText = document.getElementById('createText');
    const createSpinner = document.getElementById('createSpinner');
    
    const resultDiv = document.getElementById('result');
    const projectSelect = document.getElementById('project');
    const softpackAdminCheckbox = document.getElementById('softpackAdmin');

    let currentFormData = null;

    // Handle initial form submission for preview generation
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Get form data
        const formData = new FormData(form);
        currentFormData = {
            username: formData.get('username').trim(),
            project: formData.get('project'),
            prompt: formData.get('prompt').trim(),
            softpackAdmin: formData.get('softpackAdmin') === 'on',
            userStory: formData.get('userStory') === 'on'
        };

        // Validate form data
        if (!currentFormData.username || !currentFormData.prompt) {
            showResult({
                success: false,
                error: 'Please fill in all required fields.'
            });
            return;
        }

        // Show loading state
        setGenerateLoadingState(true);
        hideResult();

        try {
            // Make API call to generate preview
            const response = await fetch('/preview-ticket', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(currentFormData)
            });

            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || 'Failed to generate preview');
            }

            if (result.success && result.generated_content) {
                showPreview(result.generated_content);
            } else {
                throw new Error(result.error || 'Failed to generate content');
            }

        } catch (error) {
            console.error('Error:', error);
            showResult({
                success: false,
                error: `Failed to generate preview: ${error.message}`
            });
        } finally {
            setGenerateLoadingState(false);
        }
    });

    // Handle "Edit Request" button
    editAgainBtn.addEventListener('click', function() {
        hidePreview();
        hideResult();
        // Focus back on the prompt field
        document.getElementById('prompt').focus();
    });

    // Handle "Create JIRA Ticket" button
    createTicketBtn.addEventListener('click', async function() {
        const ticketData = {
            username: currentFormData.username,
            project: currentFormData.project,
            summary: previewSummary.value.trim(),
            description: previewDescription.value.trim(),
            softpackAdmin: currentFormData.softpackAdmin,
            userStory: currentFormData.userStory
        };

        // Validate
        if (!ticketData.summary || !ticketData.description) {
            showResult({
                success: false,
                error: 'Please ensure both summary and description are filled.'
            });
            return;
        }

        if (ticketData.summary.length > 100) {
            showResult({
                success: false,
                error: 'Summary must be 100 characters or less.'
            });
            return;
        }

        // Show loading state
        setCreateLoadingState(true);
        hideResult();

        try {
            // Make API call to create ticket
            const response = await fetch('/create-ticket', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(ticketData)
            });

            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || 'Failed to create ticket');
            }

            showResult(result);
            
            // Hide preview and reset form if successful
            if (result.success) {
                hidePreview();
                form.reset();
                currentFormData = null;
            }

        } catch (error) {
            console.error('Error:', error);
            showResult({
                success: false,
                error: `Failed to create ticket: ${error.message}`
            });
        } finally {
            setCreateLoadingState(false);
        }
    });

    // Character counter for summary
    previewSummary.addEventListener('input', function() {
        const length = this.value.length;
        const maxLength = 100;
        charCounter.textContent = `${length}/${maxLength} characters`;
        
        charCounter.className = 'char-counter';
        if (length > maxLength * 0.8) {
            charCounter.classList.add('warning');
        }
        if (length > maxLength) {
            charCounter.classList.add('error');
        }
    });

    // Auto-resize textareas
    const textareas = [document.getElementById('prompt'), previewDescription];
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });

    // Handle project selection change
    projectSelect.addEventListener('change', function() {
        const selectedProject = this.value;
        const isHIProject = selectedProject === 'HI';
        
        // Enable/disable softpack admin checkbox based on project selection
        softpackAdminCheckbox.disabled = !isHIProject;
        
        // If not HI project, uncheck the softpack admin checkbox
        if (!isHIProject) {
            softpackAdminCheckbox.checked = false;
        }
        
        // Update checkbox styling
        updateCheckboxStyling();
    });

    // Function to update checkbox styling based on disabled state
    function updateCheckboxStyling() {
        const checkboxLabel = softpackAdminCheckbox.closest('.checkbox-label');
        
        if (softpackAdminCheckbox.disabled) {
            checkboxLabel.classList.add('disabled');
        } else {
            checkboxLabel.classList.remove('disabled');
        }
    }

    // Initialize checkbox state on page load
    updateCheckboxStyling();

    function setGenerateLoadingState(isLoading) {
        if (isLoading) {
            generateBtn.disabled = true;
            generateText.style.display = 'none';
            generateSpinner.style.display = 'inline';
        } else {
            generateBtn.disabled = false;
            generateText.style.display = 'inline';
            generateSpinner.style.display = 'none';
        }
    }

    function setCreateLoadingState(isLoading) {
        if (isLoading) {
            createTicketBtn.disabled = true;
            createText.style.display = 'none';
            createSpinner.style.display = 'inline';
        } else {
            createTicketBtn.disabled = false;
            createText.style.display = 'inline';
            createSpinner.style.display = 'none';
        }
    }

    function showPreview(content) {
        previewSummary.value = content.summary;
        previewDescription.value = content.description;
        
        // Trigger character counter update
        previewSummary.dispatchEvent(new Event('input'));
        
        // Auto-resize description
        previewDescription.style.height = 'auto';
        previewDescription.style.height = (previewDescription.scrollHeight) + 'px';
        
        previewSection.style.display = 'block';
        
        // Scroll to preview
        previewSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Focus on summary for immediate editing
        setTimeout(() => previewSummary.focus(), 300);
    }

    function hidePreview() {
        previewSection.style.display = 'none';
    }

    function hideResult() {
        resultDiv.style.display = 'none';
        resultDiv.className = 'result';
    }

    function showResult(result) {
        resultDiv.style.display = 'block';
        
        if (result.success) {
            resultDiv.className = 'result success';
            resultDiv.innerHTML = `
                <h3>Ticket Created Successfully</h3>
                <p><strong>JIRA Key:</strong> ${result.jira_key}</p>
                <p><strong>URL:</strong> <a href="${result.jira_url}" target="_blank" rel="noopener noreferrer">${result.jira_url}</a></p>
                <p>Your ticket has been created and is ready for review.</p>
            `;
        } else {
            resultDiv.className = 'result error';
            resultDiv.innerHTML = `
                <h3>Error</h3>
                <p>${result.error || 'An unknown error occurred'}</p>
                <p>Please try again or contact support if the problem persists.</p>
            `;
        }

        // Scroll to result
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}); 