using MsgKit;

// Check if command-line arguments are provided
if (args.Length < 6)
{
    Console.WriteLine("Usage: MsgGenerator <sender-email> <sender-name> <subject> <recipient-email> <recipient-name> <body> [output-file]");
    Console.WriteLine("Example: MsgGenerator dev@example.com \"Linux Dev\" \"Test Subject\" client@example.com \"Client Name\" \"Email body text\" output.msg");
    return;
}

string senderEmail = args[0];
string senderName = args[1];
string subject = args[2];
string recipientEmail = args[3];
string recipientName = args[4];
string body = args[5];
string outputFile = args.Length > 6 ? args[6] : "Success.msg";

// Ensure msg_files directory exists
string msgDirectory = "msg_files";
if (!Directory.Exists(msgDirectory))
{
    Directory.CreateDirectory(msgDirectory);
}

// Combine with msg_files directory
string fullPath = Path.Combine(msgDirectory, outputFile);

// Define the email structure
using (var email = new Email(
    new Sender(senderEmail, senderName),
    subject))
{
    email.Recipients.AddTo(recipientEmail, recipientName);
    email.BodyText = body;
    
    // Save to the specified output file
    email.Save(fullPath);
}

Console.WriteLine($"Success: {fullPath} has been generated.");