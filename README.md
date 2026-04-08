# MSG Generator

<img src="https://github.com/impressto/MsgGenerator/blob/master/assets/death-star.png" style="width:200px" />

A cross-platform tool for creating Outlook `.msg` email files on Linux without requiring Microsoft Outlook. Built with C# (.NET 8) and includes Python-based GUI interfaces.

## Features

- Create `.msg` files natively on Linux
- Multiple interface options:
  - Command-line interface
  - Desktop GUI (tkinter)
  - Web-based interface
- Customize sender, recipient, subject, and body
- No Microsoft Outlook required

## Prerequisites

### Required
- Ubuntu 20.04 or later (or compatible Linux distribution)
- .NET 8 SDK
- Python 3

### Optional (for desktop GUI)
- python3-tk

## Installation

### 1. Install .NET 8 SDK

```bash
# Add Microsoft package repository
wget https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
rm packages-microsoft-prod.deb

# Install .NET 8 SDK
sudo apt update
sudo apt install -y dotnet-sdk-8.0
```

Verify installation:
```bash
dotnet --version
```

### 2. Install Python 3 (usually pre-installed)

```bash
sudo apt update
sudo apt install -y python3
```

### 3. Install Python tkinter (Optional - for desktop GUI)

```bash
sudo apt install -y python3-tk
```

### 4. Build the Project

Navigate to the project directory and restore dependencies:

```bash
cd /path/to/MsgGenerator
dotnet build
```

## Usage

### Option 1: Command Line Interface

Run the program directly with command-line arguments:

```bash
dotnet run "sender@example.com" "Sender Name" "Email Subject" "recipient@example.com" "Recipient Name" "Email body text" "output.msg"
```

**Example:**
```bash
dotnet run "john@example.com" "John Doe" "Meeting Reminder" "jane@example.com" "Jane Smith" "Don't forget about our meeting tomorrow at 2 PM." "meeting-reminder.msg"
```

The file will be saved to `msg_files/meeting-reminder.msg`.

### Option 2: Web Interface (No extra dependencies)

<img src="https://github.com/impressto/MsgGenerator/blob/master/assets/webgui-interface.jpg" />


Start the web server:

```bash
python3 msg_generator_web.py
```

Then open your browser and navigate to:
```
http://localhost:8080
```

Fill out the form and click "Generate MSG File" to create your `.msg` file.

**To stop the server:** Press `Ctrl+C` in the terminal.

### Option 3: Desktop GUI (Requires python3-tk)

Launch the desktop GUI:

```bash
python3 msg_generator_gui.py
```

A window will open where you can:
- Enter sender and recipient information
- Write your email subject and body
- Specify the output filename
- Click "Generate MSG File" to create the file

## Output

All generated `.msg` files are saved to the `msg_files/` directory, which is created automatically if it doesn't exist.

## Project Structure

```
MsgGenerator/
├── Program.cs                  # Main C# application
├── MsgGenerator.csproj         # Project configuration
├── msg_generator_gui.py        # Desktop GUI interface (tkinter)
├── msg_generator_web.py        # Web-based interface
├── msg_files/                  # Output directory for .msg files
├── bin/                        # Compiled binaries
└── obj/                        # Build artifacts
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'tkinter'"

Install python3-tk:
```bash
sudo apt install python3-tk
```

### "It was not possible to find any installed .NET SDKs"

Make sure .NET 8 SDK is properly installed:
```bash
dotnet --list-sdks
```

If not installed, follow the installation steps above.

### Port 8080 already in use (Web Interface)

If port 8080 is already in use, you can modify the port in `msg_generator_web.py`:
```python
port = 8080  # Change this to another port like 8081, 8082, etc.
```

## Dependencies

- **MsgKit** - Library for creating Outlook MSG files
  - Automatically installed via NuGet when building the project

## License

This project uses the MsgKit library. Please refer to the MsgKit license for usage terms.

## Notes

- The generated `.msg` files are compatible with Microsoft Outlook and other email clients that support the MSG format
- Files are saved with proper Outlook-compatible formatting
- Works on Linux, macOS, and Windows (though particularly useful on Linux where Outlook isn't available)
