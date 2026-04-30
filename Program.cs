using MsgKit;

// Check if command-line arguments are provided
if (args.Length < 6)
{
    Console.WriteLine("Usage: MsgGenerator <sender-email> <sender-name> <subject> <recipient-email> <recipient-name> <body> [output-file] [attachment-file]");
    Console.WriteLine("Example: MsgGenerator dev@example.com \"Linux Dev\" \"Test Subject\" client@example.com \"Client Name\" \"Email body text\" output.msg report.csv");
    return;
}

string senderEmail = args[0];
string senderName = args[1];
string subject = args[2];
string recipientEmail = args[3];
string recipientName = args[4];
string body = args[5];
string outputFile = args.Length > 6 ? args[6] : "Success.msg";
string? attachmentFile = args.Length > 7 ? args[7] : null;

// Ensure msg_files directory exists
string msgDirectory = "msg_files";
if (!Directory.Exists(msgDirectory))
{
    Directory.CreateDirectory(msgDirectory);
}

// Combine with msg_files directory
string fullPath = Path.Combine(msgDirectory, outputFile);

// Define the email structure with enhanced properties
using (var email = new Email(
    new Sender(senderEmail, senderName),
    new Representing(senderEmail, senderName),
    subject))
{
    // Set timestamps
    email.SentOn = DateTime.Now;
    email.ReceivedOn = DateTime.Now;
    
    // Add recipient
    email.Recipients.AddTo(recipientEmail, recipientName);
    
    // Set both plain text and HTML body for better compatibility
    email.BodyText = body;
    email.BodyHtml = $"<html><body><p>{System.Net.WebUtility.HtmlEncode(body).Replace("\n", "<br>")}</p></body></html>";
    
    // Set RTF body for better compatibility with Outlook
    email.BodyRtf = @"{\rtf1\ansi\deff0 {\fonttbl {\f0 Arial;}} \f0\fs20 " + body.Replace("\n", "\\par ") + "}";
    
    // Set importance to normal
    email.Importance = MsgKit.Enums.MessageImportance.IMPORTANCE_NORMAL;
    
    // Set icon index (for proper display in email clients)
    email.IconIndex = MsgKit.Enums.MessageIconIndex.NewMail;

    // Add optional single attachment when a valid file path is provided
    if (!string.IsNullOrWhiteSpace(attachmentFile))
    {
        if (!File.Exists(attachmentFile))
        {
            Console.WriteLine($"Error: Attachment file not found: {attachmentFile}");
            return;
        }

        email.Attachments.Add(attachmentFile);
    }
    
    // Save to the specified output file
    email.Save(fullPath);
}

Console.WriteLine($"Success: {fullPath} has been generated.");