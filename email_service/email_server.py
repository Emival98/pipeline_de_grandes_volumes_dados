import logging
import os
import smtplib
from email.message import EmailMessage

from config.settings import MINHA_SENHA_GMAIL


def send_email(
    fonte: str,
    destinatarios: list[str],
    assunto: str,
    mensagem: str,
    copia: list[str] | None = None,
):
    # 1. Validação robusta de destinatários
    if not destinatarios:
        logging.error("Falha no envio: Lista de destinatários está vazia ou é inválida.")
        return None

    msg = EmailMessage()
    msg["Subject"] = assunto
    msg["From"] = fonte
    msg["To"] = ", ".join(destinatarios)

    if copia:
        msg["Cc"] = ", ".join(copia)

    # Define o corpo em texto plano
    msg.set_content(mensagem)
    msg.add_alternative(mensagem, subtype="html")

    # 2. Consolida todos os destinatários (To + Cc) para o envelope SMTP
    envelope_recipients = list(destinatarios)
    if copia:
        envelope_recipients.extend(copia)

    try:
        logging.info("Conectando ao servidor SMTP GMAIL...")

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(fonte, MINHA_SENHA_GMAIL)

            # 3. Passar to_addrs explicitamente garante que os comandos MAIL FROM e RCPT TO
            # sejam executados na ordem exata exigida pelo protocolo RFC 5321.
            server.send_message(msg, from_addr=fonte, to_addrs=envelope_recipients)

            logging.info("Enviando para (Para): %s", ", ".join(destinatarios))
            if copia:
                logging.info("Enviando para (Cópia): %s", ", ".join(copia))

            logging.info("E-mail enviado com sucesso!")

    except Exception as e:
        logging.error("Falha ao enviar e-mail: %s", e)