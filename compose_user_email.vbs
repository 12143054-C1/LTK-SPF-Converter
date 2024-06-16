' compose_user_email.vbs

Option Explicit

Dim OutlookApp, MailItem

' Create an instance of Outlook application
Set OutlookApp = CreateObject("Outlook.Application")

' Create a new mail item
Set MailItem = OutlookApp.CreateItem(0)  ' 0 corresponds to MailItem

' Set the properties of the email
MailItem.Subject = "LTK SPF Converter - User email"
MailItem.To = "sivan.zusin@intel.com"

' Display the email to the user
MailItem.Display

' Clean up
Set MailItem = Nothing
Set OutlookApp = Nothing
