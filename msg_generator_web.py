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
import mimetypes
import cgi
import tempfile

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
        .form-row {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }
        .form-row .form-group {
            flex: 1;
            margin-bottom: 0;
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
        .download-btn {
            display: inline-block;
            margin-top: 10px;
            padding: 10px 20px;
            background-color: #28a745;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
        }
        .download-btn:hover {
            background-color: #218838;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>MSG File Generator</h1>
        <form id="msgForm">
            <div class="form-row">
                <div class="form-group">
                    <label for="senderEmail">Sender Email:</label>
                    <input type="email" id="senderEmail" name="senderEmail" value="dev@example.com" required>
                </div>
                
                <div class="form-group">
                    <label for="senderName">Sender Name:</label>
                    <input type="text" id="senderName" name="senderName" value="Linux Developer" required>
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="recipientEmail">Recipient Email:</label>
                    <input type="email" id="recipientEmail" name="recipientEmail" value="client@example.com" required>
                </div>
                
                <div class="form-group">
                    <label for="recipientName">Recipient Name:</label>
                    <input type="text" id="recipientName" name="recipientName" value="Client Name" required>
                </div>
            </div>
            
            <div class="form-group">
                <label for="subject">Subject:</label>
                <input type="text" id="subject" name="subject" value="Generated Email" required>
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

            <div class="form-group">
                <label for="attachmentFile">Attachment (Optional):</label>
                <input type="file" id="attachmentFile" name="attachmentFile" accept=".csv,.txt,.pdf,.doc,.docx,.xlsx,.xls,.png,.jpg,.jpeg,.zip,*/*">
                <small style="color: #666;">You can attach a CSV or any file type.</small>
            </div>
            
            <button type="submit">Generate MSG File</button>
        </form>
        
        <div id="message" class="message"></div>
    </div>
    
    <script>
        document.getElementById('msgForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            
            const messageDiv = document.getElementById('message');
            messageDiv.style.display = 'none';
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                messageDiv.className = 'message ' + (result.success ? 'success' : 'error');
                messageDiv.innerHTML = result.message;
                
                // Add download button if successful
                if (result.success && result.filename) {
                    const downloadLink = document.createElement('a');
                    downloadLink.href = '/download?file=' + encodeURIComponent(result.filename);
                    downloadLink.className = 'download-btn';
                    downloadLink.textContent = 'Download ' + result.filename;
                    downloadLink.download = result.filename;
                    messageDiv.appendChild(document.createElement('br'));
                    messageDiv.appendChild(downloadLink);
                }
                
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
        """Serve the HTML form or download files"""
        if self.path.startswith('/download'):
            self.handle_download()
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode())
    
    def do_POST(self):
        """Handle form submission"""
        if self.path == '/generate':
            try:
                content_type = self.headers.get('Content-Type', '')

                if content_type.startswith('multipart/form-data'):
                    form = cgi.FieldStorage(
                        fp=self.rfile,
                        headers=self.headers,
                        environ={
                            'REQUEST_METHOD': 'POST',
                            'CONTENT_TYPE': content_type,
                        },
                    )

                    sender_email = form.getvalue('senderEmail', '').strip()
                    sender_name = form.getvalue('senderName', '').strip()
                    subject = form.getvalue('subject', '').strip()
                    recipient_email = form.getvalue('recipientEmail', '').strip()
                    recipient_name = form.getvalue('recipientName', '').strip()
                    body = form.getvalue('body', '').strip()
                    output_file = form.getvalue('outputFile', '').strip()
                    attachment_field = form['attachmentFile'] if 'attachmentFile' in form else None
                else:
                    content_length = int(self.headers.get('Content-Length', '0'))
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data.decode())

                    sender_email = data.get('senderEmail', '').strip()
                    sender_name = data.get('senderName', '').strip()
                    subject = data.get('subject', '').strip()
                    recipient_email = data.get('recipientEmail', '').strip()
                    recipient_name = data.get('recipientName', '').strip()
                    body = data.get('body', '').strip()
                    output_file = data.get('outputFile', '').strip()
                    attachment_field = None
                
                # Validate
                if not all([sender_email, sender_name, subject, recipient_email, recipient_name, body, output_file]):
                    self.send_json_response({'success': False, 'message': 'All fields are required!'})
                    return
                
                # Get script directory
                script_dir = os.path.dirname(os.path.abspath(__file__))
                
                temp_attachment_path = None

                # Save optional uploaded attachment to a temporary file
                if attachment_field is not None and getattr(attachment_field, 'filename', None):
                    uploaded_filename = os.path.basename(attachment_field.filename)
                    temp_dir = os.path.join(script_dir, 'tmp_uploads')
                    os.makedirs(temp_dir, exist_ok=True)

                    fd, temp_attachment_path = tempfile.mkstemp(prefix='msg_attach_', suffix='_' + uploaded_filename, dir=temp_dir)
                    with os.fdopen(fd, 'wb') as temp_file:
                        temp_file.write(attachment_field.file.read())

                # Build command
                cmd = [
                    "dotnet", "run", "--project", script_dir, "--",
                    sender_email, sender_name, subject,
                    recipient_email, recipient_name, body, output_file
                ]

                if temp_attachment_path:
                    cmd.append(temp_attachment_path)
                
                # Run the C# program
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=script_dir
                )

                if temp_attachment_path and os.path.exists(temp_attachment_path):
                    os.remove(temp_attachment_path)
                
                if result.returncode == 0:
                    self.send_json_response({
                        'success': True, 
                        'message': f'Success! MSG file created successfully!',
                        'filename': output_file
                    })
                else:
                    self.send_json_response({
                        'success': False,
                        'message': f'Error: Failed to generate MSG file:\n\n{result.stderr}'
                    })
            
            except Exception as e:
                # Best effort cleanup for a partially processed upload
                try:
                    if 'temp_attachment_path' in locals() and temp_attachment_path and os.path.exists(temp_attachment_path):
                        os.remove(temp_attachment_path)
                except Exception:
                    pass

                self.send_json_response({
                    'success': False,
                    'message': f'Error: {str(e)}'
                })
        else:
            self.send_response(404)
            self.end_headers()
    
    def handle_download(self):
        """Handle file download requests"""
        # Parse query string
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if 'file' not in params:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Missing file parameter')
            return
        
        filename = params['file'][0]
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'msg_files', filename)
        
        # Security check - ensure the file is within msg_files directory
        if not os.path.abspath(file_path).startswith(os.path.join(script_dir, 'msg_files')):
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b'Access denied')
            return
        
        # Check if file exists
        if not os.path.exists(file_path):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'File not found')
            return
        
        # Send file
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.ms-outlook')
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f'Error reading file: {str(e)}'.encode())
    
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
    print(f"MSG Generator Web Interface")
    print(f"Server running at: http://localhost:{port}")
    print(f"Working directory: {os.getcwd()}")
    print(f"\nOpen http://localhost:{port} in your browser to create MSG files")
    print(f"Press Ctrl+C to stop the server\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped. Goodbye!")
        server.shutdown()

if __name__ == "__main__":
    main()
