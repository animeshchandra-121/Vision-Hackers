// Chatbot functionality
let chatbotOpen = false;

function toggleChatbot() {
    const chatbot = document.getElementById('chatbot');
    const chatbotWindow = document.getElementById('chatbot-window');
    
    chatbotOpen = !chatbotOpen;
    
    if (chatbotOpen) {
        chatbotWindow.style.display = 'block';
        chatbot.classList.add('open');
        document.getElementById('chatbot-input').focus();
        
        // Ensure messages are scrolled to bottom when opening
        setTimeout(() => {
            const messagesContainer = document.getElementById('chatbot-messages');
            if (messagesContainer) {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        }, 100);
    } else {
        chatbotWindow.style.display = 'none';
        chatbot.classList.remove('open');
    }
}

function sendQuickMessage(message) {
    document.getElementById('chatbot-input').value = message;
    sendChatbotMessage();
}

function handleChatbotKeypress(event) {
    if (event.key === 'Enter') {
        sendChatbotMessage();
    }
}

function sendChatbotMessage() {
    const input = document.getElementById('chatbot-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to UI
    addMessage(message, 'user');
    input.value = '';
    
    // Get bot response
    const botResponse = getChatbotResponse(message);
    addMessage(botResponse, 'bot');
}

function addMessage(content, sender) {
    const messagesContainer = document.getElementById('chatbot-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chatbot-message ${sender}`;
    
    if (sender === 'user') {
        messageDiv.innerHTML = `
            <i class="fas fa-user"></i>
            <div class="message-content">
                <p>${content}</p>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <i class="fas fa-robot"></i>
            <div class="message-content">
                <p>${content}</p>
            </div>
        `;
    }
    
    messagesContainer.appendChild(messageDiv);
    // Ensure smooth scrolling to bottom
    setTimeout(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 10);
}

function getChatbotResponse(message) {
    const lowerMessage = message.toLowerCase();
    
    // Welcome and greeting responses
    if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('hey')) {
        return "Hello! I'm your AI assistant for the AI Talent Manager platform. How can I help you today?";
    }
    
    if (lowerMessage.includes('help')) {
        return "I can help you with information about our AI Talent Manager platform. You can ask me about features, pricing, how to get started, or any other questions you might have!";
    }
    
    // Feature-related responses
    if (lowerMessage.includes('feature') || lowerMessage.includes('what can') || lowerMessage.includes('capabilities')) {
        return "Our AI Talent Manager platform offers several key features:\n\n• Smart Matching: AI-driven resource allocation\n• Automation: Automated conflict detection & resolution\n• Insights & Transparency: Real-time analytics for better decision-making\n\nWould you like to know more about any specific feature?";
    }
    
    if (lowerMessage.includes('matching') || lowerMessage.includes('smart matching')) {
        return "Smart Matching uses advanced AI algorithms to match the right talent to the right project. It analyzes skills, availability, project requirements, and team dynamics to ensure optimal resource allocation and project success.";
    }
    
    if (lowerMessage.includes('automation') || lowerMessage.includes('automated')) {
        return "Our automation features include:\n\n• Automatic conflict detection between projects\n• Resource availability monitoring\n• Intelligent scheduling suggestions\n• Automated notifications and alerts\n\nThis helps prevent scheduling conflicts and ensures smooth project execution.";
    }
    
    if (lowerMessage.includes('insight') || lowerMessage.includes('analytics') || lowerMessage.includes('transparency')) {
        return "Our Insights & Transparency features provide:\n\n• Real-time project status updates\n• Resource utilization analytics\n• Performance metrics and KPIs\n• Detailed reporting dashboards\n\nThis gives you complete visibility into your team's productivity and project progress.";
    }
    
    // Pricing-related responses
    if (lowerMessage.includes('price') || lowerMessage.includes('cost') || lowerMessage.includes('pricing')) {
        return "We offer flexible pricing plans to suit teams of all sizes. For detailed pricing information, please visit our Pricing page or contact our sales team. We also offer a free trial to get you started!";
    }
    
    // Getting started responses
    if (lowerMessage.includes('get started') || lowerMessage.includes('sign up') || lowerMessage.includes('register')) {
        return "Getting started is easy! You can:\n\n1. Click the 'Get Started Free' button in the header\n2. Create your account with your email\n3. Set up your team and projects\n4. Start using our AI-powered matching features\n\nWould you like me to guide you through any specific step?";
    }
    
    if (lowerMessage.includes('demo') || lowerMessage.includes('book a demo')) {
        return "Great! You can book a demo by clicking the 'Book a Demo' button on our homepage. Our team will show you how the platform works and answer any questions you might have. The demo typically takes about 30 minutes.";
    }
    
    // Contact and support responses
    if (lowerMessage.includes('contact') || lowerMessage.includes('support') || lowerMessage.includes('help')) {
        return "You can reach us through:\n\n• Email: support@aitalentmanager.com\n• Phone: 1-800-AI-TALENT\n• Live chat: Available on our website\n• Contact form: Available on our Contact page\n\nWe're here to help you succeed!";
    }
    
    // About the company
    if (lowerMessage.includes('about') || lowerMessage.includes('company') || lowerMessage.includes('who are you')) {
        return "AI Talent Manager is a cutting-edge platform that uses artificial intelligence to optimize project-resource mapping. We help teams match the right talent to the right project every time, preventing conflicts and accelerating success.";
    }
    
    // Default response
    return "I'm here to help you learn more about our AI Talent Manager platform! You can ask me about our features, pricing, how to get started, or anything else you'd like to know. What would you like to explore?";
}