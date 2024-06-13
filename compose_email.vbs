' Get arguments from command line
Dim ToEmail
Dim Subject
Dim Body
Dim Attachments
Dim Args, Arg

Set Args = WScript.Arguments

ToEmail = Args(0)
Subject = Args(1)
Body = Args(2)
Attachments = Args(3)

Set Outlook = CreateObject("Outlook.Application")
Set Mail = Outlook.CreateItem(0)

Mail.To = ToEmail
Mail.Subject = Subject
Mail.Body = Body

' Handle attachments; expecting a string with paths separated by a semicolon
If Attachments <> "" Then
    Dim AttachmentPaths
    AttachmentPaths = Split(Attachments, ";")
    Dim Path
    For Each Path In AttachmentPaths
        If Path <> "" Then
            Mail.Attachments.Add(Path)
        End If
    Next
End If

Mail.Display ' To show the email
Set Mail = Nothing
Set Outlook = Nothing
