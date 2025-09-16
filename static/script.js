(function() {
    // Inject modern CSS with timestamp styling
    const styleTag = document.createElement('style');
    styleTag.textContent = `
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }
        
        .chat-wrapper {
            max-width: 400px;
            margin: 0 auto;
            padding: 20px;
            height: 650px;
            display: flex;
            flex-direction: column;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.2);
            overflow: hidden;
            animation: popupSlideIn 0.4s cubic-bezier(0.23, 1, 0.32, 1);
            transition: all 0.3s ease;
        }
        
        header {
            text-align: left;
            margin-bottom: 16px;
            padding-left: 4px;
            transition: all 0.3s ease;
        }
        
        header h1 {
            color: #1a1d29;
            font-weight: 600;
            font-size: 1.6rem;
            letter-spacing: -0.02em;
            margin-bottom: 6px;
            transition: color 0.3s ease;
        }
        
        header p {
            font-weight: 400;
            font-size: 0.9rem;
            color: #6b7280;
            opacity: 0.85;
            transition: all 0.3s ease;
        }
        
        #tabs-container {
            display: flex;
            gap: 4px;
            margin-bottom: 16px;
            background: rgba(255, 255, 255, 0.1);
            padding: 6px;
            border-radius: 16px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }
        
        .tab-btn {
            flex: 1;
            padding: 12px 16px;
            cursor: pointer;
            border: none;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transform: translateY(0);
        }
        
        .tab-active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #ffffff;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            transform: translateY(-1px);
        }
        
        .tab-inactive {
            background: rgba(255, 255, 255, 0.5);
            color: #6b7280;
        }
        
        .tab-inactive:hover {
            background: rgba(255, 255, 255, 0.8);
            transform: translateY(-1px);
        }
        
        .chat-container, .products-container {
            background: transparent;
            padding: 0;
            margin: 0;
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            transition: all 0.3s ease;
            opacity: 1;
        }
        
        .chat-container.fade-out, .products-container.fade-out {
            opacity: 0;
            transform: translateX(-10px);
        }
        
        .chat-container.fade-in, .products-container.fade-in {
            opacity: 1;
            transform: translateX(0);
        }
        
        #messages {
            flex: 1;
            min-height: 200px;
            max-height: 380px;
            overflow-y: auto;
            border-radius: 20px;
            padding: 16px;
            background: linear-gradient(145deg, #f8fafc, #e2e8f0);
            border: 1px solid rgba(148, 163, 184, 0.1);
            scroll-behavior: smooth;
            transition: all 0.3s ease;
            margin-bottom: 12px;
        }
        
        #messages::-webkit-scrollbar {
            width: 6px;
        }
        
        #messages::-webkit-scrollbar-track {
            background: transparent;
        }
        
        #messages::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 10px;
            transition: background 0.3s ease;
        }
        
        #messages::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
        }
        
        .message {
            margin-bottom: 16px;
            max-width: 85%;
            animation: slideIn 0.4s ease-out;
            transition: all 0.3s ease;
        }
        
        .message-content {
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 0.9rem;
            line-height: 1.4;
            margin-bottom: 4px;
        }
        
        .message-timestamp {
            font-size: 0.75rem;
            opacity: 0.7;
            transition: opacity 0.3s ease;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(15px) scale(0.95);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }
        
        .user-message .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .user-message {
            margin-left: auto;
            margin-right: 0;
            text-align: right;
            animation: slideInRight 0.4s ease-out;
        }
        
        .user-message .message-timestamp {
            color: rgba(255, 255, 255, 0.8);
            text-align: right;
        }
        
        .bot-message .message-content {
            background: #ffffff;
            color: #374151;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            border: 1px solid #f3f4f6;
        }
        
        .bot-message {
            margin-right: auto;
            margin-left: 0;
            text-align: left;
            animation: slideInLeft 0.4s ease-out;
        }
        
        .bot-message .message-timestamp {
            color: #9ca3af;
            text-align: left;
        }
        
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .intent-badge {
            display: inline-block;
            background: linear-gradient(90deg, #10b981, #059669);
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 500;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.02em;
            animation: fadeIn 0.3s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .input-container {
            display: flex;
            gap: 12px;
            margin-top: auto;
        }
        
        .input-container input {
            flex: 1;
            padding: 14px 18px;
            border: 2px solid transparent;
            border-radius: 22px;
            background: #f8fafc;
            font-size: 0.95rem;
            transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
            color: #374151;
        }
        
        .input-container input:focus {
            outline: none;
            background: #ffffff;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            transform: translateY(-1px);
        }
        
        .input-container input::placeholder {
            color: #9ca3af;
            transition: color 0.3s ease;
        }
        
        .input-container button {
            padding: 14px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 22px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .input-container button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        
        .input-container button:active {
            transform: translateY(0);
        }
        
        .input-container button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .products-container h2 {
            margin-bottom: 18px;
            font-weight: 600;
            color: #1f2937;
            font-size: 1.1rem;
            letter-spacing: -0.01em;
            transition: color 0.3s ease;
        }
        
        #searchInput {
            width: 100%;
            padding: 14px 18px;
            border-radius: 22px;
            border: 2px solid transparent;
            background: #f8fafc;
            font-size: 0.95rem;
            transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
            margin-bottom: 20px;
            color: #374151;
        }
        
        #searchInput:focus {
            outline: none;
            background: #ffffff;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            transform: translateY(-1px);
        }
        
        #products {
            flex: 1;
            overflow-y: auto;
            max-height: 380px;
        }
        
        #products::-webkit-scrollbar {
            width: 6px;
        }
        
        #products::-webkit-scrollbar-track {
            background: transparent;
        }
        
        #products::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 10px;
            transition: background 0.3s ease;
        }
        
        #products::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
        }
        
        .product {
            border-radius: 16px;
            padding: 18px;
            margin-bottom: 16px;
            background: #ffffff;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            border: 1px solid #f3f4f6;
            transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
            animation: productSlideIn 0.4s ease-out;
        }
        
        @keyframes productSlideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .product:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
        }
        
        .product h3 {
            font-weight: 600;
            font-size: 1rem;
            color: #111827;
            margin-bottom: 8px;
            letter-spacing: -0.01em;
            transition: color 0.3s ease;
        }
        
        .product-price {
            font-weight: 600;
            color: #059669;
            font-size: 1.05rem;
            margin-bottom: 6px;
            transition: color 0.3s ease;
        }
        
        .product-category {
            background: linear-gradient(90deg, #6b7280, #4b5563);
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 500;
            display: inline-block;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.02em;
            transition: all 0.3s ease;
        }
        
        /* ✅ NEW: Product Image Styles */
        .product img {
            transition: transform 0.3s ease;
            border-radius: 12px;
        }
        
        .product img:hover {
            transform: scale(1.02);
        }
        
        .product-status-badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-weight: 500;
        }
        
        .product-image-placeholder {
            background: linear-gradient(45deg, #f3f4f6, #e5e7eb);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            color: #9ca3af;
        }
        
        /* ✅ NEW: Clickable Product Styles */
        .clickable-product {
            cursor: pointer !important;
            transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1) !important;
            position: relative;
            overflow: hidden;
        }

        .clickable-product::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            transition: left 0.5s;
            z-index: 1;
        }

        .clickable-product:hover::before {
            left: 100%;
        }

        .clickable-product:hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15) !important;
        }

        .clickable-product:active {
            transform: translateY(-2px) !important;
        }

        .product-cta-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
            display: inline-block;
            transition: all 0.3s ease;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #6b7280;
            font-size: 0.9rem;
            animation: pulse 1.5s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .tab-icon {
            width: 16px;
            height: 16px;
            fill: currentColor;
            transition: transform 0.3s ease;
        }
        
        .send-icon {
            width: 16px;
            height: 16px;
            fill: currentColor;
            transition: transform 0.3s ease;
        }
        
        .close-icon {
            width: 18px;
            height: 18px;
            fill: currentColor;
            transition: transform 0.3s ease;
        }
        
        .chat-icon {
            width: 24px;
            height: 24px;
            fill: currentColor;
            transition: transform 0.3s ease;
        }
        
        @keyframes popupSlideIn {
            from {
                opacity: 0;
                transform: translateY(30px) scale(0.9);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }
        
        @keyframes popupSlideOut {
            from {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
            to {
                opacity: 0;
                transform: translateY(30px) scale(0.9);
            }
        }
        
        @media (max-height: 700px) {
            .chat-wrapper {
                height: calc(100vh - 40px);
                max-height: 650px;
            }
            #messages {
                max-height: 280px;
            }
            #products {
                max-height: 280px;
            }
        }
    `;
    
    document.head.appendChild(styleTag);

    // Create responsive popup wrapper with chat-wrapper class
    const wrapper = document.createElement('div');
    wrapper.id = 'chat-popup';
    wrapper.className = 'chat-wrapper';
    wrapper.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 420px;
        max-width: calc(100vw - 40px);
        display: none;
        z-index: 10000;
    `;

    // Insert the HTML with header above tabs and left-aligned text
    wrapper.innerHTML = `
        <header>
            <h1>WooCommerce AI Assistant</h1>
            <p>Your intelligent shopping companion</p>
        </header>
        
        <div id="tabs-container">
            <button class="tab-btn tab-active" data-tab="chat">
                <svg class="tab-icon" viewBox="0 0 20 20">
                    <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"/>
                    <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z"/>
                </svg>
                Chat
            </button>
            <button class="tab-btn tab-inactive" data-tab="products">
                <svg class="tab-icon" viewBox="0 0 20 20">
                    <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
                </svg>
                Products
            </button>
        </div>

        <div class="chat-container" id="chat-container">
            <div id="messages"></div>
            <div class="input-container">
                <input type="text" id="messageInput" placeholder="Ask me about products..." autocomplete="off">
                <button id="sendBtn">
                    <svg class="send-icon" viewBox="0 0 20 20">
                        <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"/>
                    </svg>
                </button>
            </div>
        </div>

        <div class="products-container" id="products-container" style="display: none;">
            <h2>Browse Products</h2>
            <input type="text" id="searchInput" placeholder="Search products...">
            <div id="products"></div>
        </div>
    `;

    document.body.appendChild(wrapper);

    // Create floating chat button
    const chatButton = document.createElement('div');
    chatButton.id = 'chat-button';
    chatButton.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
        z-index: 9999;
        border: 3px solid rgba(255, 255, 255, 0.2);
    `;

    chatButton.innerHTML = `
        <svg class="chat-icon" fill="white" viewBox="0 0 20 20">
            <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"/>
            <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z"/>
        </svg>
    `;

    document.body.appendChild(chatButton);

    // Event handlers
    let isPopupOpen = false;

    chatButton.addEventListener('mouseenter', () => {
        if (!isPopupOpen) {
            chatButton.style.transform = 'scale(1.1) translateY(-2px)';
            chatButton.style.boxShadow = '0 12px 40px rgba(0, 0, 0, 0.3)';
        }
    });

    chatButton.addEventListener('mouseleave', () => {
        if (!isPopupOpen) {
            chatButton.style.transform = 'scale(1) translateY(0)';
            chatButton.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.2)';
        }
    });

    chatButton.addEventListener('click', () => {
        if (isPopupOpen) {
            wrapper.style.animation = 'popupSlideOut 0.3s ease-out forwards';
            setTimeout(() => {
                wrapper.style.display = 'none';
                chatButton.style.display = 'flex';
                chatButton.style.transform = 'scale(1) translateY(0)';
                chatButton.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.2)';
            }, 300);
            isPopupOpen = false;
        } else {
            wrapper.style.display = 'flex';
            wrapper.style.animation = 'popupSlideIn 0.4s cubic-bezier(0.23, 1, 0.32, 1) forwards';
            chatButton.style.transform = 'scale(0.9) translateY(0)';
            chatButton.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.15)';
            isPopupOpen = true;
            
            // Load initial products when opening
            loadProducts();
            document.getElementById('messageInput').focus();
        }
    });

    // Tab switching functionality
    const tabBtns = wrapper.querySelectorAll('.tab-btn');
    const chatContainer = document.getElementById('chat-container');
    const productsContainer = document.getElementById('products-container');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.dataset.tab;
            
            // Update tab states
            tabBtns.forEach(b => {
                b.classList.remove('tab-active');
                b.classList.add('tab-inactive');
            });
            btn.classList.add('tab-active');
            btn.classList.remove('tab-inactive');

            // Switch containers with animation
            if (targetTab === 'chat') {
                productsContainer.classList.add('fade-out');
                setTimeout(() => {
                    productsContainer.style.display = 'none';
                    chatContainer.style.display = 'flex';
                    chatContainer.classList.remove('fade-out');
                    chatContainer.classList.add('fade-in');
                }, 150);
            } else {
                chatContainer.classList.add('fade-out');
                setTimeout(() => {
                    chatContainer.style.display = 'none';
                    productsContainer.style.display = 'flex';
                    productsContainer.classList.remove('fade-out');
                    productsContainer.classList.add('fade-in');
                    loadProducts(); // Load products when switching to products tab
                }, 150);
            }
        });
    });

    // Message handling
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const messages = document.getElementById('messages');
    
    function addMessage(content, isUser = false, intent = null, confidence = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = isUser ? 'message user-message' : 'message bot-message';
        
        const timestamp = new Date().toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        });

        let intentBadge = '';
        if (intent && !isUser) {
            intentBadge = `<div class="intent-badge">${intent} (${Math.round(confidence * 100)}%)</div>`;
        }

        messageDiv.innerHTML = `
            ${intentBadge}
            <div class="message-content">${content}</div>
            <div class="message-timestamp">${timestamp}</div>
        `;

        messages.appendChild(messageDiv);
        messages.scrollTop = messages.scrollHeight;
    }

    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        // Disable input while processing
        messageInput.disabled = true;
        sendBtn.disabled = true;

        // Add user message
        addMessage(message, true);
        messageInput.value = '';

        try {
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // ---------- NEW: improved handling of API response ----------
            const data = await response.json();

            // small html-escape helper
            function escapeHtml(str) {
                if (str === undefined || str === null) return '';
                return String(str)
                    .replace(/&/g, "&amp;")
                    .replace(/</g, "&lt;")
                    .replace(/>/g, "&gt;")
                    .replace(/"/g, "&quot;")
                    .replace(/'/g, "&#039;");
            }

            // build botResponse: product_finder (existing) OR sales_executive rich cards
            let botResponse = 'Sorry, I could not process your request.';

            if (data.intent === 'product_finder' && data.products && data.products.length > 0) {
                // keep current product_finder behavior (but render as HTML)
                const html = data.products.slice(0, 3).map(product => {
                    const productUrl = product.url || `https://newscnbnc.webserver9.com/product/${product.slug || product.id}`;
                    const imageHtml = product.image ? `<img src="${escapeHtml(product.image)}" alt="${escapeHtml(product.name)}" style="width:100%;height:120px;object-fit:cover;border-radius:10px;margin-bottom:8px;">` : `<div class="product-image-placeholder" style="width:100%;height:120px;border-radius:10px;margin-bottom:8px;">📷 No Image</div>`;
                    const price = product.price ? `<div class="product-price">$${escapeHtml(String(product.price))}</div>` : '';
                    const desc = product.description ? `<p style="font-size:0.85rem;color:#6b7280;margin:8px 0 0;">${escapeHtml(product.description)}</p>` : '';
                    return `<div class="product clickable-product" style="padding:12px;border-radius:12px;margin-bottom:10px;" onclick="openProduct('${escapeHtml(productUrl)}')">
                                ${imageHtml}
                                <h3 style="margin:6px 0 4px">${escapeHtml(product.name)}</h3>
                                ${price}
                                ${desc}
                            </div>`;
                }).join('');
                botResponse = `<div>${html}</div>`;
            } else if (data.response && Array.isArray(data.response.recommendations) && data.response.recommendations.length) {
                // New: render recommendations as rich product cards inside the chat bubble
                const pitchHtml = data.response.pitch ? `<div style="margin-bottom:8px;font-weight:600">${escapeHtml(data.response.pitch)}</div>` : '';
                const recsHtml = data.response.recommendations.slice(0, 5).map(r => {
                    const title = escapeHtml(r.title || '');
                    const idPart = r.id ? ` <span style="opacity:0.7">(#${escapeHtml(String(r.id))})</span>` : '';
                    const reason = r.reason ? `<div style="font-size:0.8rem;color:#9ca3af;margin-top:6px">${escapeHtml(r.reason)}</div>` : '';
                    const imageHtml = r.image ? `<img src="${escapeHtml(r.image)}" alt="${title}" style="width:100px;height:80px;object-fit:cover;border-radius:8px;margin-right:12px;">` : `<div class="product-image-placeholder" style="width:100px;height:80px;border-radius:8px;margin-right:12px;display:flex;align-items:center;justify-content:center;background:#f3f4f6">📷</div>`;
                    const priceHtml = r.price ? `<div style="font-weight:600;color:#059669;margin-top:6px">$${escapeHtml(String(r.price))}</div>` : '';
                    const url = r.url || (r.id ? `/product/${escapeHtml(String(r.id))}` : '#');
                    const desc = r.description ? `<div style="font-size:0.85rem;color:#6b7280;margin-top:6px">${escapeHtml(r.description)}</div>` : '';

                    return `<div class="chat-product" style="display:flex;gap:12px;align-items:flex-start;padding:10px 8px;border-radius:10px;border:1px solid #f3f4f6;margin-bottom:10px;">
                                <a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" style="display:inline-block;">${imageHtml}</a>
                                <div style="flex:1;">
                                    <a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" style="font-weight:600;color:#111827;text-decoration:none">${title}${idPart}</a>
                                    ${priceHtml}
                                    ${desc}
                                    ${reason}
                                </div>
                            </div>`;
                }).join('');

                botResponse = `<div>${pitchHtml}${recsHtml}</div>`;
            } else {
                // fallback: show pitch or raw response text
                if (data.response && typeof data.response === 'object' && data.response.pitch) {
                    botResponse = escapeHtml(data.response.pitch);
                } else if (typeof data.response === 'string') {
                    botResponse = escapeHtml(data.response);
                } else {
                    botResponse = escapeHtml(JSON.stringify(data.response || {}));
                }
            }

            // Add bot response with intent info.
            addMessage(botResponse, false, data.intent, data.confidence);

        } catch (error) {
            console.error('Error:', error);
            addMessage('Sorry, I encountered an error. Please try again.', false);
        } finally {
            // Re-enable input
            messageInput.disabled = false;
            sendBtn.disabled = false;
            messageInput.focus();
        }
    }

    // Event listeners for sending messages
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Product search functionality
    const searchInput = document.getElementById('searchInput');
    const productsDiv = document.getElementById('products');
    let searchTimeout;

    // ✅ ENHANCED: Updated displayProducts function with clickable products
    function displayProducts(products) {
        if (!products.length) {
            productsDiv.innerHTML = '<div class="loading">No products found. Try a different search term.</div>';
            return;
        }

        const productsHtml = products.map(product => {
            // Image handling
            const imageHtml = product.image ? 
                `<img src="${product.image}" alt="${product.name}" style="width: 100%; height: 150px; object-fit: cover; border-radius: 12px; margin-bottom: 12px;">` : 
                `<div class="product-image-placeholder" style="width: 100%; height: 150px; border-radius: 12px; margin-bottom: 12px;">📷 No Image</div>`;
            
            // Status badge
            const statusBadge = product.stock_status === 'instock' ? 
                `<span class="product-status-badge" style="background: #10b981; color: white; padding: 4px 8px; border-radius: 8px; font-size: 10px; font-weight: 500;">✅ In Stock</span>` :
                `<span class="product-status-badge" style="background: #ef4444; color: white; padding: 4px 8px; border-radius: 8px; font-size: 10px; font-weight: 500;">❌ Out of Stock</span>`;
            
            // ✅ NEW: Product URL handling
            const productUrl = product.url || `https://newscnbnc.webserver9.com/product/${product.slug || product.id}`;
            
            return `
                <div class="product clickable-product" onclick="openProduct('${productUrl}')" 
                     style="cursor: pointer; transition: all 0.3s ease;" 
                     onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 12px 35px rgba(0, 0, 0, 0.15)'" 
                     onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0, 0, 0, 0.06)'">
                    ${imageHtml}
                    <h3>${product.name}</h3>
                    <div class="product-price">$${product.price}</div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <div class="product-category">${product.category}</div>
                        ${statusBadge}
                    </div>
                    <p style="font-size: 0.85rem; color: #6b7280; line-height: 1.4; margin-bottom: 12px;">${product.description || 'No description available'}</p>
                    
                    <!-- ✅ NEW: Call-to-action button -->
                    <div style="text-align: center; padding-top: 8px; border-top: 1px solid #f3f4f6;">
                        <span class="product-cta-button">
                            🛒 View Product
                        </span>
                    </div>
                </div>
            `;
        }).join('');
        
        productsDiv.innerHTML = productsHtml;
    }

    // ✅ NEW: Function to handle product clicks
    function openProduct(url) {
        // Open in new tab to keep your chat widget accessible
        window.open(url, '_blank', 'noopener,noreferrer');
    }

    // ✅ ADD THIS LINE - Make function globally accessible
    window.openProduct = openProduct;

    async function loadProducts(query = '') {
        try {
            productsDiv.innerHTML = '<div class="loading">Loading products...</div>';
            
            const url = query 
                ? `/api/products/search?q=${encodeURIComponent(query)}&limit=20`
                : `/api/products/search?q=&limit=20`;
                
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const products = await response.json();
            displayProducts(products);
            
        } catch (error) {
            console.error('Error loading products:', error);
            productsDiv.innerHTML = '<div class="loading">Error loading products. Please try again.</div>';
        }
    }

    // Search input handler
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            loadProducts(e.target.value.trim());
        }, 300);
    });

    // Add welcome message
    setTimeout(() => {
        if (messages.children.length === 0) {
            addMessage('Hello! I\'m your AI shopping assistant. I can help you find products, answer questions, and assist with your shopping needs. What can I help you with today?', false);
        }
    }, 500);

})();







// ________________________________________







// (function() {
//     // Inject modern CSS with timestamp styling
//     const styleTag = document.createElement('style');
//     styleTag.textContent = `
//         @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
//         * {
//             margin: 0;
//             padding: 0;
//             box-sizing: border-box;
//             font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
//         }
        
//         body {
//             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
//             color: #333;
//         }
        
//         .chat-wrapper {
//             max-width: 400px;
//             margin: 0 auto;
//             padding: 20px;
//             height: 650px;
//             display: flex;
//             flex-direction: column;
//             background: rgba(255, 255, 255, 0.95);
//             backdrop-filter: blur(20px);
//             border-radius: 24px;
//             box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
//             border: 1px solid rgba(255, 255, 255, 0.2);
//             overflow: hidden;
//             animation: popupSlideIn 0.4s cubic-bezier(0.23, 1, 0.32, 1);
//             transition: all 0.3s ease;
//         }
        
//         header {
//             text-align: left;
//             margin-bottom: 16px;
//             padding-left: 4px;
//             transition: all 0.3s ease;
//         }
        
//         header h1 {
//             color: #1a1d29;
//             font-weight: 600;
//             font-size: 1.6rem;
//             letter-spacing: -0.02em;
//             margin-bottom: 6px;
//             transition: color 0.3s ease;
//         }
        
//         header p {
//             font-weight: 400;
//             font-size: 0.9rem;
//             color: #6b7280;
//             opacity: 0.85;
//             transition: all 0.3s ease;
//         }
        
//         #tabs-container {
//             display: flex;
//             gap: 4px;
//             margin-bottom: 16px;
//             background: rgba(255, 255, 255, 0.1);
//             padding: 6px;
//             border-radius: 16px;
//             backdrop-filter: blur(10px);
//             transition: all 0.3s ease;
//         }
        
//         .tab-btn {
//             flex: 1;
//             padding: 12px 16px;
//             cursor: pointer;
//             border: none;
//             border-radius: 12px;
//             font-size: 13px;
//             font-weight: 500;
//             transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
//             text-align: center;
//             display: flex;
//             align-items: center;
//             justify-content: center;
//             gap: 8px;
//             transform: translateY(0);
//         }
        
//         .tab-active {
//             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
//             color: #ffffff;
//             box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
//             transform: translateY(-1px);
//         }
        
//         .tab-inactive {
//             background: rgba(255, 255, 255, 0.5);
//             color: #6b7280;
//         }
        
//         .tab-inactive:hover {
//             background: rgba(255, 255, 255, 0.8);
//             transform: translateY(-1px);
//         }
        
//         .chat-container, .products-container {
//             background: transparent;
//             padding: 0;
//             margin: 0;
//             flex: 1;
//             display: flex;
//             flex-direction: column;
//             overflow: hidden;
//             transition: all 0.3s ease;
//             opacity: 1;
//         }
        
//         .chat-container.fade-out, .products-container.fade-out {
//             opacity: 0;
//             transform: translateX(-10px);
//         }
        
//         .chat-container.fade-in, .products-container.fade-in {
//             opacity: 1;
//             transform: translateX(0);
//         }
        
//         #messages {
//             flex: 1;
//             min-height: 200px;
//             max-height: 380px;
//             overflow-y: auto;
//             border-radius: 20px;
//             padding: 16px;
//             background: linear-gradient(145deg, #f8fafc, #e2e8f0);
//             border: 1px solid rgba(148, 163, 184, 0.1);
//             scroll-behavior: smooth;
//             transition: all 0.3s ease;
//             margin-bottom: 12px;
//         }
        
//         #messages::-webkit-scrollbar {
//             width: 6px;
//         }
        
//         #messages::-webkit-scrollbar-track {
//             background: transparent;
//         }
        
//         #messages::-webkit-scrollbar-thumb {
//             background: #cbd5e1;
//             border-radius: 10px;
//             transition: background 0.3s ease;
//         }
        
//         #messages::-webkit-scrollbar-thumb:hover {
//             background: #94a3b8;
//         }
        
//         .message {
//             margin-bottom: 16px;
//             max-width: 85%;
//             animation: slideIn 0.4s ease-out;
//             transition: all 0.3s ease;
//         }
        
//         .message-content {
//             padding: 12px 16px;
//             border-radius: 18px;
//             font-size: 0.9rem;
//             line-height: 1.4;
//             margin-bottom: 4px;
//         }
        
//         .message-timestamp {
//             font-size: 0.75rem;
//             opacity: 0.7;
//             transition: opacity 0.3s ease;
//         }
        
//         @keyframes slideIn {
//             from {
//                 opacity: 0;
//                 transform: translateY(15px) scale(0.95);
//             }
//             to {
//                 opacity: 1;
//                 transform: translateY(0) scale(1);
//             }
//         }
        
//         .user-message .message-content {
//             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
//             color: white;
//             box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
//         }
        
//         .user-message {
//             margin-left: auto;
//             margin-right: 0;
//             text-align: right;
//             animation: slideInRight 0.4s ease-out;
//         }
        
//         .user-message .message-timestamp {
//             color: rgba(255, 255, 255, 0.8);
//             text-align: right;
//         }
        
//         .bot-message .message-content {
//             background: #ffffff;
//             color: #374151;
//             box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
//             border: 1px solid #f3f4f6;
//         }
        
//         .bot-message {
//             margin-right: auto;
//             margin-left: 0;
//             text-align: left;
//             animation: slideInLeft 0.4s ease-out;
//         }
        
//         .bot-message .message-timestamp {
//             color: #9ca3af;
//             text-align: left;
//         }
        
//         @keyframes slideInRight {
//             from {
//                 opacity: 0;
//                 transform: translateX(20px);
//             }
//             to {
//                 opacity: 1;
//                 transform: translateX(0);
//             }
//         }
        
//         @keyframes slideInLeft {
//             from {
//                 opacity: 0;
//                 transform: translateX(-20px);
//             }
//             to {
//                 opacity: 1;
//                 transform: translateX(0);
//             }
//         }
        
//         .intent-badge {
//             display: inline-block;
//             background: linear-gradient(90deg, #10b981, #059669);
//             color: white;
//             padding: 4px 12px;
//             border-radius: 12px;
//             font-size: 10px;
//             font-weight: 500;
//             margin-bottom: 6px;
//             text-transform: uppercase;
//             letter-spacing: 0.02em;
//             animation: fadeIn 0.3s ease-out;
//         }
        
//         @keyframes fadeIn {
//             from { opacity: 0; }
//             to { opacity: 1; }
//         }
        
//         .input-container {
//             display: flex;
//             gap: 12px;
//             margin-top: auto;
//         }
        
//         .input-container input {
//             flex: 1;
//             padding: 14px 18px;
//             border: 2px solid transparent;
//             border-radius: 22px;
//             background: #f8fafc;
//             font-size: 0.95rem;
//             transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
//             color: #374151;
//         }
        
//         .input-container input:focus {
//             outline: none;
//             background: #ffffff;
//             border-color: #667eea;
//             box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
//             transform: translateY(-1px);
//         }
        
//         .input-container input::placeholder {
//             color: #9ca3af;
//             transition: color 0.3s ease;
//         }
        
//         .input-container button {
//             padding: 14px 20px;
//             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
//             color: white;
//             border: none;
//             border-radius: 22px;
//             cursor: pointer;
//             font-size: 0.9rem;
//             font-weight: 500;
//             transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
//             box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
//             display: flex;
//             align-items: center;
//             gap: 6px;
//         }
        
//         .input-container button:hover:not(:disabled) {
//             transform: translateY(-2px);
//             box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
//         }
        
//         .input-container button:active {
//             transform: translateY(0);
//         }
        
//         .input-container button:disabled {
//             opacity: 0.6;
//             cursor: not-allowed;
//             transform: none;
//         }
        
//         .products-container h2 {
//             margin-bottom: 18px;
//             font-weight: 600;
//             color: #1f2937;
//             font-size: 1.1rem;
//             letter-spacing: -0.01em;
//             transition: color 0.3s ease;
//         }
        
//         #searchInput {
//             width: 100%;
//             padding: 14px 18px;
//             border-radius: 22px;
//             border: 2px solid transparent;
//             background: #f8fafc;
//             font-size: 0.95rem;
//             transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
//             margin-bottom: 20px;
//             color: #374151;
//         }
        
//         #searchInput:focus {
//             outline: none;
//             background: #ffffff;
//             border-color: #667eea;
//             box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
//             transform: translateY(-1px);
//         }
        
//         #products {
//             flex: 1;
//             overflow-y: auto;
//             max-height: 380px;
//         }
        
//         #products::-webkit-scrollbar {
//             width: 6px;
//         }
        
//         #products::-webkit-scrollbar-track {
//             background: transparent;
//         }
        
//         #products::-webkit-scrollbar-thumb {
//             background: #cbd5e1;
//             border-radius: 10px;
//             transition: background 0.3s ease;
//         }
        
//         #products::-webkit-scrollbar-thumb:hover {
//             background: #94a3b8;
//         }
        
//         .product {
//             border-radius: 16px;
//             padding: 18px;
//             margin-bottom: 16px;
//             background: #ffffff;
//             box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
//             border: 1px solid #f3f4f6;
//             transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
//             animation: productSlideIn 0.4s ease-out;
//         }
        
//         @keyframes productSlideIn {
//             from {
//                 opacity: 0;
//                 transform: translateY(10px);
//             }
//             to {
//                 opacity: 1;
//                 transform: translateY(0);
//             }
//         }
        
//         .product:hover {
//             transform: translateY(-2px);
//             box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
//         }
        
//         .product h3 {
//             font-weight: 600;
//             font-size: 1rem;
//             color: #111827;
//             margin-bottom: 8px;
//             letter-spacing: -0.01em;
//             transition: color 0.3s ease;
//         }
        
//         .product-price {
//             font-weight: 600;
//             color: #059669;
//             font-size: 1.05rem;
//             margin-bottom: 6px;
//             transition: color 0.3s ease;
//         }
        
//         .product-category {
//             background: linear-gradient(90deg, #6b7280, #4b5563);
//             color: white;
//             padding: 4px 12px;
//             border-radius: 12px;
//             font-size: 10px;
//             font-weight: 500;
//             display: inline-block;
//             margin-bottom: 10px;
//             text-transform: uppercase;
//             letter-spacing: 0.02em;
//             transition: all 0.3s ease;
//         }
        
//         /* ✅ NEW: Product Image Styles */
//         .product img {
//             transition: transform 0.3s ease;
//             border-radius: 12px;
//         }
        
//         .product img:hover {
//             transform: scale(1.02);
//         }
        
//         .product-status-badge {
//             display: inline-flex;
//             align-items: center;
//             gap: 4px;
//             font-weight: 500;
//         }
        
//         .product-image-placeholder {
//             background: linear-gradient(45deg, #f3f4f6, #e5e7eb);
//             display: flex;
//             align-items: center;
//             justify-content: center;
//             font-size: 12px;
//             color: #9ca3af;
//         }
        
//         /* ✅ NEW: Clickable Product Styles */
//         .clickable-product {
//             cursor: pointer !important;
//             transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1) !important;
//             position: relative;
//             overflow: hidden;
//         }

//         .clickable-product::before {
//             content: '';
//             position: absolute;
//             top: 0;
//             left: -100%;
//             width: 100%;
//             height: 100%;
//             background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
//             transition: left 0.5s;
//             z-index: 1;
//         }

//         .clickable-product:hover::before {
//             left: 100%;
//         }

//         .clickable-product:hover {
//             transform: translateY(-4px) !important;
//             box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15) !important;
//         }

//         .clickable-product:active {
//             transform: translateY(-2px) !important;
//         }

//         .product-cta-button {
//             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
//             color: white;
//             padding: 8px 16px;
//             border-radius: 20px;
//             font-size: 12px;
//             font-weight: 500;
//             display: inline-block;
//             transition: all 0.3s ease;
//         }
        
//         .loading {
//             text-align: center;
//             padding: 20px;
//             color: #6b7280;
//             font-size: 0.9rem;
//             animation: pulse 1.5s ease-in-out infinite;
//         }
        
//         @keyframes pulse {
//             0%, 100% { opacity: 1; }
//             50% { opacity: 0.5; }
//         }
        
//         .tab-icon {
//             width: 16px;
//             height: 16px;
//             fill: currentColor;
//             transition: transform 0.3s ease;
//         }
        
//         .send-icon {
//             width: 16px;
//             height: 16px;
//             fill: currentColor;
//             transition: transform 0.3s ease;
//         }
        
//         .close-icon {
//             width: 18px;
//             height: 18px;
//             fill: currentColor;
//             transition: transform 0.3s ease;
//         }
        
//         .chat-icon {
//             width: 24px;
//             height: 24px;
//             fill: currentColor;
//             transition: transform 0.3s ease;
//         }
        
//         @keyframes popupSlideIn {
//             from {
//                 opacity: 0;
//                 transform: translateY(30px) scale(0.9);
//             }
//             to {
//                 opacity: 1;
//                 transform: translateY(0) scale(1);
//             }
//         }
        
//         @keyframes popupSlideOut {
//             from {
//                 opacity: 1;
//                 transform: translateY(0) scale(1);
//             }
//             to {
//                 opacity: 0;
//                 transform: translateY(30px) scale(0.9);
//             }
//         }
        
//         @media (max-height: 700px) {
//             .chat-wrapper {
//                 height: calc(100vh - 40px);
//                 max-height: 650px;
//             }
//             #messages {
//                 max-height: 280px;
//             }
//             #products {
//                 max-height: 280px;
//             }
//         }
//     `;
    
//     document.head.appendChild(styleTag);

//     // Create responsive popup wrapper with chat-wrapper class
//     const wrapper = document.createElement('div');
//     wrapper.id = 'chat-popup';
//     wrapper.className = 'chat-wrapper';
//     wrapper.style.cssText = `
//         position: fixed;
//         bottom: 20px;
//         right: 20px;
//         width: 420px;
//         max-width: calc(100vw - 40px);
//         display: none;
//         z-index: 10000;
//     `;

//     // Insert the HTML with header above tabs and left-aligned text
//     wrapper.innerHTML = `
//         <header>
//             <h1>WooCommerce AI Assistant</h1>
//             <p>Your intelligent shopping companion</p>
//         </header>
        
//         <div id="tabs-container">
//             <button class="tab-btn tab-active" data-tab="chat">
//                 <svg class="tab-icon" viewBox="0 0 20 20">
//                     <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"/>
//                     <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z"/>
//                 </svg>
//                 Chat
//             </button>
//             <button class="tab-btn tab-inactive" data-tab="products">
//                 <svg class="tab-icon" viewBox="0 0 20 20">
//                     <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
//                 </svg>
//                 Products
//             </button>
//         </div>

//         <div class="chat-container" id="chat-container">
//             <div id="messages"></div>
//             <div class="input-container">
//                 <input type="text" id="messageInput" placeholder="Ask me about products..." autocomplete="off">
//                 <button id="sendBtn">
//                     <svg class="send-icon" viewBox="0 0 20 20">
//                         <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"/>
//                     </svg>
//                 </button>
//             </div>
//         </div>

//         <div class="products-container" id="products-container" style="display: none;">
//             <h2>Browse Products</h2>
//             <input type="text" id="searchInput" placeholder="Search products...">
//             <div id="products"></div>
//         </div>
//     `;

//     document.body.appendChild(wrapper);

//     // Create floating chat button
//     const chatButton = document.createElement('div');
//     chatButton.id = 'chat-button';
//     chatButton.style.cssText = `
//         position: fixed;
//         bottom: 20px;
//         right: 20px;
//         width: 60px;
//         height: 60px;
//         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
//         border-radius: 50%;
//         display: flex;
//         align-items: center;
//         justify-content: center;
//         cursor: pointer;
//         box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
//         transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
//         z-index: 9999;
//         border: 3px solid rgba(255, 255, 255, 0.2);
//     `;

//     chatButton.innerHTML = `
//         <svg class="chat-icon" fill="white" viewBox="0 0 20 20">
//             <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"/>
//             <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z"/>
//         </svg>
//     `;

//     document.body.appendChild(chatButton);

//     // Event handlers
//     let isPopupOpen = false;

//     chatButton.addEventListener('mouseenter', () => {
//         if (!isPopupOpen) {
//             chatButton.style.transform = 'scale(1.1) translateY(-2px)';
//             chatButton.style.boxShadow = '0 12px 40px rgba(0, 0, 0, 0.3)';
//         }
//     });

//     chatButton.addEventListener('mouseleave', () => {
//         if (!isPopupOpen) {
//             chatButton.style.transform = 'scale(1) translateY(0)';
//             chatButton.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.2)';
//         }
//     });

//     chatButton.addEventListener('click', () => {
//         if (isPopupOpen) {
//             wrapper.style.animation = 'popupSlideOut 0.3s ease-out forwards';
//             setTimeout(() => {
//                 wrapper.style.display = 'none';
//                 chatButton.style.display = 'flex';
//                 chatButton.style.transform = 'scale(1) translateY(0)';
//                 chatButton.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.2)';
//             }, 300);
//             isPopupOpen = false;
//         } else {
//             wrapper.style.display = 'flex';
//             wrapper.style.animation = 'popupSlideIn 0.4s cubic-bezier(0.23, 1, 0.32, 1) forwards';
//             chatButton.style.transform = 'scale(0.9) translateY(0)';
//             chatButton.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.15)';
//             isPopupOpen = true;
            
//             // Load initial products when opening
//             loadProducts();
//             document.getElementById('messageInput').focus();
//         }
//     });

//     // Tab switching functionality
//     const tabBtns = wrapper.querySelectorAll('.tab-btn');
//     const chatContainer = document.getElementById('chat-container');
//     const productsContainer = document.getElementById('products-container');

//     tabBtns.forEach(btn => {
//         btn.addEventListener('click', () => {
//             const targetTab = btn.dataset.tab;
            
//             // Update tab states
//             tabBtns.forEach(b => {
//                 b.classList.remove('tab-active');
//                 b.classList.add('tab-inactive');
//             });
//             btn.classList.add('tab-active');
//             btn.classList.remove('tab-inactive');

//             // Switch containers with animation
//             if (targetTab === 'chat') {
//                 productsContainer.classList.add('fade-out');
//                 setTimeout(() => {
//                     productsContainer.style.display = 'none';
//                     chatContainer.style.display = 'flex';
//                     chatContainer.classList.remove('fade-out');
//                     chatContainer.classList.add('fade-in');
//                 }, 150);
//             } else {
//                 chatContainer.classList.add('fade-out');
//                 setTimeout(() => {
//                     chatContainer.style.display = 'none';
//                     productsContainer.style.display = 'flex';
//                     productsContainer.classList.remove('fade-out');
//                     productsContainer.classList.add('fade-in');
//                     loadProducts(); // Load products when switching to products tab
//                 }, 150);
//             }
//         });
//     });

//     // Message handling
//     const messageInput = document.getElementById('messageInput');
//     const sendBtn = document.getElementById('sendBtn');
//     const messages = document.getElementById('messages');
    
//     function addMessage(content, isUser = false, intent = null, confidence = null) {
//         const messageDiv = document.createElement('div');
//         messageDiv.className = isUser ? 'message user-message' : 'message bot-message';
        
//         const timestamp = new Date().toLocaleTimeString('en-US', {
//             hour: '2-digit',
//             minute: '2-digit',
//             hour12: false
//         });

//         let intentBadge = '';
//         if (intent && !isUser) {
//             intentBadge = `<div class="intent-badge">${intent} (${Math.round(confidence * 100)}%)</div>`;
//         }

//         messageDiv.innerHTML = `
//             ${intentBadge}
//             <div class="message-content">${content}</div>
//             <div class="message-timestamp">${timestamp}</div>
//         `;

//         messages.appendChild(messageDiv);
//         messages.scrollTop = messages.scrollHeight;
//     }

//     async function sendMessage() {
//         const message = messageInput.value.trim();
//         if (!message) return;

//         // Disable input while processing
//         messageInput.disabled = true;
//         sendBtn.disabled = true;

//         // Add user message
//         addMessage(message, true);
//         messageInput.value = '';

//         try {
//             const response = await fetch('/api/chat/', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                 },
//                 body: JSON.stringify({ message })
//             });

//             if (!response.ok) {
//                 throw new Error(`HTTP error! status: ${response.status}`);
//             }



//             const data = await response.json();

//             // helper: escape text for safe innerHTML
//             function escapeHtml(str) {
//                 if (str === undefined || str === null) return '';
//                 return String(str)
//                     .replace(/&/g, "&amp;")
//                     .replace(/</g, "&lt;")
//                     .replace(/>/g, "&gt;")
//                     .replace(/"/g, "&quot;")
//                     .replace(/'/g, "&#039;");
//             }

//             // format the assistant response object into readable HTML/text
//             function formatAssistantResponse(resp) {
//                 if (!resp) return 'Sorry, I could not process your request.';
//                 // if already a string, return it escaped
//                 if (typeof resp === 'string') return escapeHtml(resp);

//                 // prefer pitch + recommendations shape
//                 const pitch = resp.pitch ? escapeHtml(resp.pitch) : '';
//                 const recs = Array.isArray(resp.recommendations) ? resp.recommendations : [];

//                 let out = '';
//                 if (pitch) {
//                     out += `<div>${pitch}</div>`;
//                 }

//                 if (recs.length) {
//                     out += '<div style="margin-top:8px;"><strong>Recommendations</strong><ul style="margin:8px 0 0 18px; padding:0;">';
//                     recs.slice(0, 5).forEach(r => {
//                         const title = escapeHtml(r.title || r.name || '');
//                         const id = r.id ? ` <span style="opacity:0.7">(#${escapeHtml(String(r.id))})</span>` : '';
//                         const reason = r.reason ? ` <span style="opacity:0.7">— ${escapeHtml(r.reason)}</span>` : '';
//                         out += `<li style="margin-bottom:6px;">${title}${id}${reason}</li>`;
//                     });
//                     out += '</ul></div>';
//                 }

//                 // fallback to raw as debugging aid
//                 if (!out && resp.raw) {
//                     out = `<pre style="white-space:pre-wrap;font-size:0.9rem;">${escapeHtml(resp.raw)}</pre>`;
//                 }

//                 return out || escapeHtml(JSON.stringify(resp));
//             }

//             // ---------- use the formatter ----------
//             let botResponse;

//             // product_finder special formatting (keep existing behavior)
//             if (data.intent === 'product_finder' && data.products && data.products.length > 0) {
//                 let enhancedResponse = `Found ${data.products.length} products:\n\n`;

//                 data.products.slice(0, 3).forEach((product, index) => {
//                     const productUrl = product.url || `https://newscnbnc.webserver9.com/product/${product.slug || product.id}`;

//                     enhancedResponse += `${index + 1}. **${product.name}** - $${product.price}\n`;
//                     if (product.image) {
//                         enhancedResponse += `🖼️ [View Image](${product.image})\n`;
//                     }
//                     enhancedResponse += `🛒 [Buy Now](${productUrl})\n`;
//                     enhancedResponse += `📂 ${product.category} | ${product.stock_status === 'instock' ? '✅ In Stock' : '❌ Out of Stock'}\n\n`;
//                 });

//                 botResponse = escapeHtml(enhancedResponse).replace(/\n/g, '<br>');
//             } else {
//                 // format response object (handles sales_executive returning {pitch,recommendations,...})
//                 botResponse = formatAssistantResponse(data.response);
//             }

//             // Add bot response with intent info.
//             // Note: addMessage currently sets innerHTML with `${intentBadge}<div class="message-content">${content}</div>`
//             // We pass HTML content; it is escaped inside formatAssistantResponse, so innerHTML is safe.
//             addMessage(botResponse, false, data.intent, data.confidence);


//             // const data = await response.json();
            
//             // // ✅ ENHANCED: Handle products in response
//             // let botResponse = data.response || 'Sorry, I could not process your request.';
            
//             // if (data.intent === 'product_finder' && data.products && data.products.length > 0) {
//             //     let enhancedResponse = `Found ${data.products.length} products:\n\n`;
                
//             //     data.products.slice(0, 3).forEach((product, index) => {
//             //         const productUrl = product.url || `https://newscnbnc.webserver9.com/product/${product.slug || product.id}`;
                    
//             //         enhancedResponse += `${index + 1}. **${product.name}** - $${product.price}\n`;
//             //         if (product.image) {
//             //             enhancedResponse += `🖼️ [View Image](${product.image})\n`;
//             //         }
//             //         // ✅ ADD: Direct product link
//             //         enhancedResponse += `🛒 [Buy Now](${productUrl})\n`;
//             //         enhancedResponse += `📂 ${product.category} | ${product.stock_status === 'instock' ? '✅ In Stock' : '❌ Out of Stock'}\n\n`;
//             //     });
                
//             //     botResponse = enhancedResponse;
//             // }
            
//             // // Add bot response with intent info
//             // addMessage(botResponse, false, data.intent, data.confidence);

//         } catch (error) {
//             console.error('Error:', error);
//             addMessage('Sorry, I encountered an error. Please try again.', false);
//         } finally {
//             // Re-enable input
//             messageInput.disabled = false;
//             sendBtn.disabled = false;
//             messageInput.focus();
//         }
//     }

//     // Event listeners for sending messages
//     sendBtn.addEventListener('click', sendMessage);
//     messageInput.addEventListener('keypress', (e) => {
//         if (e.key === 'Enter') {
//             sendMessage();
//         }
//     });

//     // Product search functionality
//     const searchInput = document.getElementById('searchInput');
//     const productsDiv = document.getElementById('products');
//     let searchTimeout;

//     // ✅ ENHANCED: Updated displayProducts function with clickable products
//     function displayProducts(products) {
//         if (!products.length) {
//             productsDiv.innerHTML = '<div class="loading">No products found. Try a different search term.</div>';
//             return;
//         }

//         const productsHtml = products.map(product => {
//             // Image handling
//             const imageHtml = product.image ? 
//                 `<img src="${product.image}" alt="${product.name}" style="width: 100%; height: 150px; object-fit: cover; border-radius: 12px; margin-bottom: 12px;">` : 
//                 `<div class="product-image-placeholder" style="width: 100%; height: 150px; border-radius: 12px; margin-bottom: 12px;">📷 No Image</div>`;
            
//             // Status badge
//             const statusBadge = product.stock_status === 'instock' ? 
//                 `<span class="product-status-badge" style="background: #10b981; color: white; padding: 4px 8px; border-radius: 8px; font-size: 10px; font-weight: 500;">✅ In Stock</span>` :
//                 `<span class="product-status-badge" style="background: #ef4444; color: white; padding: 4px 8px; border-radius: 8px; font-size: 10px; font-weight: 500;">❌ Out of Stock</span>`;
            
//             // ✅ NEW: Product URL handling
//             const productUrl = product.url || `https://newscnbnc.webserver9.com/product/${product.slug || product.id}`;
            
//             return `
//                 <div class="product clickable-product" onclick="openProduct('${productUrl}')" 
//                      style="cursor: pointer; transition: all 0.3s ease;" 
//                      onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 12px 35px rgba(0, 0, 0, 0.15)'" 
//                      onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0, 0, 0, 0.06)'">
//                     ${imageHtml}
//                     <h3>${product.name}</h3>
//                     <div class="product-price">$${product.price}</div>
//                     <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
//                         <div class="product-category">${product.category}</div>
//                         ${statusBadge}
//                     </div>
//                     <p style="font-size: 0.85rem; color: #6b7280; line-height: 1.4; margin-bottom: 12px;">${product.description || 'No description available'}</p>
                    
//                     <!-- ✅ NEW: Call-to-action button -->
//                     <div style="text-align: center; padding-top: 8px; border-top: 1px solid #f3f4f6;">
//                         <span class="product-cta-button">
//                             🛒 View Product
//                         </span>
//                     </div>
//                 </div>
//             `;
//         }).join('');
        
//         productsDiv.innerHTML = productsHtml;
//     }

//     // ✅ NEW: Function to handle product clicks
//     function openProduct(url) {
//         // Open in new tab to keep your chat widget accessible
//         window.open(url, '_blank', 'noopener,noreferrer');
//     }

//     // ✅ ADD THIS LINE - Make function globally accessible
//     window.openProduct = openProduct;

//     async function loadProducts(query = '') {
//         try {
//             productsDiv.innerHTML = '<div class="loading">Loading products...</div>';
            
//             const url = query 
//                 ? `/api/products/search?q=${encodeURIComponent(query)}&limit=20`
//                 : `/api/products/search?q=&limit=20`;
                
//             const response = await fetch(url);
            
//             if (!response.ok) {
//                 throw new Error(`HTTP error! status: ${response.status}`);
//             }
            
//             const products = await response.json();
//             displayProducts(products);
            
//         } catch (error) {
//             console.error('Error loading products:', error);
//             productsDiv.innerHTML = '<div class="loading">Error loading products. Please try again.</div>';
//         }
//     }

//     // Search input handler
//     searchInput.addEventListener('input', (e) => {
//         clearTimeout(searchTimeout);
//         searchTimeout = setTimeout(() => {
//             loadProducts(e.target.value.trim());
//         }, 300);
//     });

//     // Add welcome message
//     setTimeout(() => {
//         if (messages.children.length === 0) {
//             addMessage('Hello! I\'m your AI shopping assistant. I can help you find products, answer questions, and assist with your shopping needs. What can I help you with today?', false);
//         }
//     }, 500);

// })();
