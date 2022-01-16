import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

class Sender:
    def __init__(self):
        self.mail_host = "smtp.163.com"
        self.mail_user = "paradoxhzy_test@163.com"
        self.mail_pass = "ZZPOBUNVJNHLALKO"
        self.sender = 'paradoxhzy_test@163.com'
        self.receivers = []
        self.message = MIMEMultipart()

    def add_receivers(self, addr):
        self.receivers.append(addr)

    def get_message(self, url):
        self.att = MIMEText(open(url, 'r').read(), 'base64', 'utf-8')
        self.att["Content-Type"] = 'application/octet-stream'
        self.att["Content-Disposition"] = 'attachment; filename="result.txt"'

    def send(self):
        if self.receivers:
            self.message['From'] = Header("PassSite", 'utf-8')
            self.message['To'] = Header(",".join(self.receivers), 'utf-8')
            self.message['Subject'] = Header("训练结果", 'utf-8')
            self.message.attach(self.att)
            try:
                smtpObj = smtplib.SMTP()
                smtpObj.connect(self.mail_host, 25)
                smtpObj.login(self.mail_user, self.mail_pass)
                smtpObj.sendmail(self.sender, self.receivers, self.message.as_string())
                print("邮件发送成功")
            except smtplib.SMTPException:
                print("Error: 无法发送邮件")
        else:
            print("Error: 无有效收件人")
