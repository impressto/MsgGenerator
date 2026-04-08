#!/usr/bin/env python3
"""
Web Interface for MsgGenerator
Creates .msg files using a simple web interface
Uses only Python standard library - no external dependencies
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import os
import json
import urllib.parse

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>MSG File Generator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: bold;
        }
        input[type="text"],
        input[type="email"],
        textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
            font-size: 14px;
        }
        textarea {
            min-height: 120px;
            font-family: Arial, sans-serif;
            resize: vertical;
        }
        button {
            background-color: #0066cc;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
        }
        button:hover {
            background-color: #0052a3;
        }
        .message {
            padding: 15px;
            margin-top: 20px;
            border-radius: 4px;
            display: none;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📧 MSG File Generator</h1>
        <form id="msgForm">
            <div class="form-group">
                <label for="senderEmail">Sender Email:</label>
                <input type="email" id="senderEmail" name="senderEmail" value="dev@example.com" required>
            </div>
            
            <div class="form-group">
                <label for="senderName">Sender Name:</label>
                <input type="text" id="senderName" name="senderName" value="Linux Developer" required>
            </div>
            
            <div class="form-group">
                <label for="subject">Subject:</label>
                <input type="text" id="subject" name="subject" value="Generated Email" required>
            </div>
            
            <div class="form-group">
                <label for="recipientEmail">Recipient Email:</label>
                <input type="email" id="recipientEmail" name="recipientEmail" value="client@example.com" required>
            </div>
            
            <div class="form-group">
                <label for="recipientName">Recipient Name:</label>
                <input type="text" id="recipientName" name="recipientName" value="Client Name" required>
            </div>
            
            <div class="form-group">
                <label for="body">Email Body:</label>
                <textarea id="body" name="body" required>This .msg file was created on Linux without Outlook.</textarea>
            </div>
            
            <div class="form-group">
                <label for="outputFile">File Name:</label>
                <input type="text" id="outputFile" name="outputFile" value="Success.msg" required>
                <small style="color: #666;">Files will be saved to: msg_files/</small>
            </div>
            
            <button type="submit">Generate MSG File</button>
        </form>
        
        <div id="message" class="message"></div>
    </div>
    
    <script>
        document.getElementById('msgForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = {};
            formData.forEach((value, key) => data[key] = value);
            
            const messageDiv = document.getElementById('message');
            messageDiv.style.display = 'none';
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                messageDiv.className = 'message ' + (result.success ? 'success' : 'error');
                messageDiv.textContent = result.message;
                messageDiv.style.display = 'block';
                
            } catch (error) {
                messageDiv.className = 'message error';
                messageDiv.textContent = 'Failed to connect to server: ' + error.message;
                messageDiv.style.display = 'block';
            }
        });
    </script>
</body>
</html>
"""

class MsgGeneratorHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Serve the HTML form"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(HTML_TEMPLATE.encode())
    
    def do_POST(self):
        """Handle form submission"""
        if self.path == '/generate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode())
                
                # Extract form data
                sender_email = data.get('senderEmail', '').strip()
                sender_name = data.get('senderName', '').strip()
                subject = data.get('subject', '').strip()
                recipient_email = data.get('recipientEmail', '').strip()
                recipient_name = data.get('recipientName', '').strip()
                body = data.get('body', '').strip()
                output_file = data.get('outputFile', '').strip()
                
                # Validate
                if not all([sender_email, sender_name, subject, recipient_email, recipient_name, body, output_file]):
                    self.send_json_response({'success': False, 'message': 'All fields are required!'})
                    return
                
                # Get script directory
                script_dir = os.path.dirname(os.path.abspath(__file__))
                
                # Build command
                cmd = [
                    "dotnet", "run", "--project", script_dir, "--",
                    sender_email, sender_name, subject,
                    recipient_email, recipient_name, body, output_file
                ]
                
                # Run the C# program
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=script_dir
                )
                
                if result.returncode == 0:
                    self.send_json_response({
                        'success': True, 
                        'message': f'✅ MSG file created successfully!\n\n{result.stdout}'
                    })
                else:
                    self.send_json_response({
                        'success': False,
                        'message': f'❌ Failed to generate MSG file:\n\n{result.stderr}'
                    })
            
            except Exception as e:
                self.send_json_response({
                    'success': False,
                    'message': f'❌ Error: {str(e)}'
                })
        else:
            self.send_response(404)
            self.end_headers()
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.log_date_time_string()}] {format % args}")

def main():
    port = 8080
    server = HTTPServer(('localhost', port), MsgGeneratorHandler)
    print(f"🌐 MSG Generator Web Interface")
    print(f"🚀 Server running at: http://localhost:{port}")
    print(f"📂 Working directory: {os.getcwd()}")
    print(f"\n✨ Open http://localhost:{port} in your browser to create MSG files")
    print(f"🛑 Press Ctrl+C to stop the server\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
        server.shutdown()

if __name__ == "__main__":
    main()
