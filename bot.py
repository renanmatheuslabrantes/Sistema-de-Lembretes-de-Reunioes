import sqlite3
from tkinter import *
from tkinter import messagebox
from datetime import datetime, timedelta
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
import json
import os
import re
import threading
from cryptography.fernet import Fernet
import logging

# Configuração de logs
logging.basicConfig(filename='lembretes.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Caminho do arquivo de configuração
CONFIG_FILE = 'config.json'

# Chave de criptografia (gerar uma nova se não existir)
KEY_FILE = 'key.key'
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)
else:
    with open(KEY_FILE, 'rb') as key_file:
        key = key_file.read()
cipher_suite = Fernet(key)

# Função para criptografar dados
def encrypt(data):
    return cipher_suite.encrypt(data.encode()).decode()

# Função para descriptografar dados
def decrypt(data):
    return cipher_suite.decrypt(data.encode()).decode()

# Inicialização do banco de dados
def inicializar_banco():
    conn = sqlite3.connect('lembretes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clientes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  nome TEXT NOT NULL,
                  telefone TEXT NOT NULL,
                  email TEXT NOT NULL,
                  data_reuniao TEXT NOT NULL)''')
    conn.commit()
    return conn, c

# Inicializa a conexão com o banco de dados
conn, c = inicializar_banco()

# Função para validar e-mail
def validar_email(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None

# Função para validar telefone
def validar_telefone(telefone):
    regex = r'^\+?[0-9]{10,15}$'
    return re.match(regex, telefone) is not None

# Função para carregar as configurações
def carregar_configuracoes():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Descriptografar senha
            if 'email_password' in config:
                config['email_password'] = decrypt(config['email_password'])
            return config
    return {}

# Função para salvar as configurações
def salvar_configuracoes():
    config = {
        'twilio_account_sid': entry_twilio_sid.get(),
        'twilio_auth_token': entry_twilio_token.get(),
        'twilio_whatsapp_number': entry_twilio_numero.get(),
        'whatsapp_template_sid': entry_template_sid.get(),
        'email_address': entry_email.get(),
        'email_password': encrypt(entry_senha.get())  # Criptografar senha
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)
    messagebox.showinfo("Configurações", "Configurações salvas com sucesso!")
    janela_config.destroy()

# Função para abrir a janela de configuração
def abrir_configuracao():
    global janela_config, entry_twilio_sid, entry_twilio_token, entry_twilio_numero, entry_template_sid, entry_email, entry_senha

    janela_config = Toplevel(root)
    janela_config.title("Configurações do Sistema")
    janela_config.geometry("450x350")

    Label(janela_config, text="Configurações de Serviços", font=("Helvetica", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

    Label(janela_config, text="Twilio Account SID:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_twilio_sid = Entry(janela_config, width=35)
    entry_twilio_sid.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    Label(janela_config, text="Twilio Auth Token:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_twilio_token = Entry(janela_config, width=35)
    entry_twilio_token.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    Label(janela_config, text="Número do WhatsApp:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_twilio_numero = Entry(janela_config, width=35)
    entry_twilio_numero.grid(row=3, column=1, padx=10, pady=5, sticky="w")
    
    Label(janela_config, text="WhatsApp Template SID:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    entry_template_sid = Entry(janela_config, width=35)
    entry_template_sid.grid(row=4, column=1, padx=10, pady=5, sticky="w")
    
    # Botão de ajuda para o Template SID
    Button(janela_config, text="?", command=mostrar_ajuda_template, width=2).grid(row=4, column=2)

    Label(janela_config, text="E-mail para notificações:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    entry_email = Entry(janela_config, width=35)
    entry_email.grid(row=5, column=1, padx=10, pady=5, sticky="w")

    Label(janela_config, text="Senha do E-mail:").grid(row=6, column=0, padx=10, pady=5, sticky="e")
    entry_senha = Entry(janela_config, width=35, show="*")
    entry_senha.grid(row=6, column=1, padx=10, pady=5, sticky="w")

    Button(janela_config, text="Salvar Configurações", command=salvar_configuracoes, width=20).grid(row=7, column=0, columnspan=2, pady=15)
    
    # Aviso sobre formatação
    Label(janela_config, text="Nota: O número do WhatsApp deve estar no formato internacional", 
          font=("Helvetica", 8), fg="gray").grid(row=8, column=0, columnspan=2)
    Label(janela_config, text="Exemplo: +5511999887766 (sem espaços ou caracteres especiais)", 
          font=("Helvetica", 8), fg="gray").grid(row=9, column=0, columnspan=2)

    # Carregar configurações existentes
    config = carregar_configuracoes()
    entry_twilio_sid.insert(0, config.get('twilio_account_sid', ''))
    entry_twilio_token.insert(0, config.get('twilio_auth_token', ''))
    entry_twilio_numero.insert(0, config.get('twilio_whatsapp_number', ''))
    entry_template_sid.insert(0, config.get('whatsapp_template_sid', 'HXb5b62575e6e4ff6129ad7c8efe1f983e'))
    entry_email.insert(0, config.get('email_address', ''))
    entry_senha.insert(0, config.get('email_password', ''))

# Função para mostrar ajuda sobre o Template SID
def mostrar_ajuda_template():
    ajuda = Toplevel(root)
    ajuda.title("Ajuda - WhatsApp Template SID")
    ajuda.geometry("500x350")
    
    Label(ajuda, text="Como encontrar o WhatsApp Template SID", font=("Helvetica", 12, "bold")).pack(pady=10)
    
    texto_ajuda = """
1. Acesse o Dashboard da Twilio (www.twilio.com/console)
2. Navegue até 'Messaging' → 'Content Editor' → 'Templates'
3. Selecione ou crie um template para lembretes de compromisso
4. Após aprovação pela Meta, você verá o SID no formato "HXxxxxx..."
5. Copie este SID e cole no campo de configuração

O template deve ter variáveis para:
- Nome do cliente: {{1}}
- Data do compromisso: {{2}}
- Horário do compromisso: {{3}}

Exemplo de template: "Olá {{1}}, seu compromisso está agendado para {{2}} às {{3}}. Confirme sua presença respondendo esta mensagem."

Nota: Os templates precisam ser aprovados pela Meta antes de 
poderem ser utilizados, o que pode levar alguns dias.
    """
    
    text_widget = Text(ajuda, wrap=WORD, width=60, height=15)
    text_widget.pack(padx=20, pady=10, fill=BOTH, expand=True)
    text_widget.insert(END, texto_ajuda)
    text_widget.config(state=DISABLED)
    
    Button(ajuda, text="Fechar", command=ajuda.destroy, width=10).pack(pady=10)

# Função para enviar mensagem no WhatsApp usando templates
def enviar_whatsapp(telefone, nome, data, hora):
    config = carregar_configuracoes()
    
    if not validar_telefone(telefone):
        messagebox.showerror("Telefone Inválido", "O número de telefone está em um formato inválido.")
        return False
    
    try:
        client = Client(config['twilio_account_sid'], config['twilio_auth_token'])
        
        message = client.messages.create(
            from_=f"whatsapp:{config['twilio_whatsapp_number']}",
            content_sid=config.get('whatsapp_template_sid', 'HXb5b62575e6e4ff6129ad7c8efe1f983e'),
            content_variables=json.dumps({
                "1": nome,
                "2": data,
                "3": hora
            }),
            to=f'whatsapp:{telefone}'
        )
        logging.info(f"Mensagem enviada para {telefone}: {message.sid}")
        atualizar_status(f"Mensagem enviada para {nome} em {datetime.now().strftime('%H:%M:%S')}")
        return True
    except Exception as e:
        logging.error(f"Erro ao enviar WhatsApp: {e}")
        messagebox.showerror("Erro de Comunicação", f"Não foi possível enviar a mensagem via WhatsApp: {e}")
        return False

# Função para enviar e-mail
def enviar_email(email, assunto, mensagem):
    config = carregar_configuracoes()
    if not validar_email(email):
        messagebox.showerror("E-mail Inválido", "O e-mail fornecido é inválido.")
        return False
    
    try:
        msg = MIMEText(mensagem)
        msg['Subject'] = assunto
        msg['From'] = config['email_address']
        msg['To'] = email

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(config['email_address'], config['email_password'])
            server.sendmail(config['email_address'], [email], msg.as_string())
        logging.info(f"E-mail enviado para {email}")
        atualizar_status(f"E-mail enviado para {email}")
        return True
    except Exception as e:
        logging.error(f"Erro ao enviar e-mail: {e}")
        messagebox.showerror("Erro de Comunicação", f"Não foi possível enviar o e-mail: {e}")
        return False

# Função para atualizar a barra de status
def atualizar_status(mensagem):
    status_bar.config(text=mensagem)
    root.update_idletasks()

# Função para verificar e enviar lembretes
def verificar_lembretes():
    hoje = datetime.now()
    tres_dias = hoje + timedelta(days=3)
    um_dia = hoje + timedelta(days=1)
    
    atualizar_status("Verificando lembretes agendados...")
    
    status = {"sucesso": 0, "falha": 0}

    c.execute("SELECT * FROM clientes")
    clientes = c.fetchall()

    for cliente in clientes:
        id_cliente, nome, telefone, email, data_reuniao = cliente
        data_reuniao = datetime.strptime(data_reuniao, '%Y-%m-%d %H:%M:%S')
        
        data_formatada = data_reuniao.strftime('%d/%m/%Y')
        hora_formatada = data_reuniao.strftime('%H:%M')

        if data_reuniao.date() == tres_dias.date():
            mensagem = f"Olá {nome}, você tem uma reunião agendada para {data_formatada} às {hora_formatada}. Não se esqueça!"
            
            if enviar_whatsapp(telefone, nome, data_formatada, hora_formatada):
                status["sucesso"] += 1
            else:
                status["falha"] += 1

            if enviar_email(email, "Lembrete de Reunião", mensagem):
                status["sucesso"] += 1
            else:
                status["falha"] += 1

        if data_reuniao.date() == um_dia.date():
            mensagem = f"Olá {nome}, você tem uma reunião agendada para amanhã às {hora_formatada}. Prepare-se!"
            
            if enviar_whatsapp(telefone, nome, "amanhã", hora_formatada):
                status["sucesso"] += 1
            else:
                status["falha"] += 1

            if enviar_email(email, "Lembrete de Reunião", mensagem):
                status["sucesso"] += 1
            else:
                status["falha"] += 1

    if status["sucesso"] > 0 or status["falha"] > 0:
        messagebox.showinfo("Resumo de Envios", f"Lembretes: {status['sucesso']} enviados com sucesso, {status['falha']} falhas.")
    else:
        messagebox.showinfo("Verificação Concluída", "Não há lembretes para enviar no momento.")
    
    atualizar_status("Sistema pronto - Última verificação: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

# Função para agendar verificações automáticas
def agendar_verificacoes():
    threading.Timer(3600, agendar_verificacoes).start()  # Verifica a cada hora
    verificar_lembretes()

# Função para adicionar cliente
def adicionar_cliente():
    nome = entry_nome.get()
    telefone = entry_telefone.get()
    email = entry_email_cliente.get()
    data_reuniao = entry_data.get()

    if nome and telefone and email and data_reuniao:
        if not validar_email(email):
            messagebox.showerror("E-mail Inválido", "Por favor, insira um e-mail válido.")
            return
        if not validar_telefone(telefone):
            messagebox.showerror("Telefone Inválido", "Por favor, insira um número de telefone válido.")
            return
        try:
            data_reuniao = datetime.strptime(data_reuniao, '%d/%m/%Y %H:%M')
            c.execute("INSERT INTO clientes (nome, telefone, email, data_reuniao) VALUES (?, ?, ?, ?)",
                      (nome, telefone, email, data_reuniao.strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            messagebox.showinfo("Cliente Adicionado", f"Cliente {nome} adicionado com sucesso!")
            entry_nome.delete(0, END)
            entry_telefone.delete(0, END)
            entry_email_cliente.delete(0, END)
            entry_data.delete(0, END)
            atualizar_lista_clientes()
            atualizar_status(f"Cliente {nome} adicionado ao sistema")
        except ValueError:
            messagebox.showerror("Formato Inválido", "Formato de data inválido! Use DD/MM/AAAA HH:MM")
    else:
        messagebox.showerror("Campos Obrigatórios", "Todos os campos são obrigatórios para cadastrar um cliente!")

# Função para atualizar a lista de clientes
def atualizar_lista_clientes():
    lista_clientes.delete(0, END)
    c.execute("SELECT * FROM clientes ORDER BY data_reuniao")
    clientes = c.fetchall()
    for cliente in clientes:
        data_reuniao = datetime.strptime(cliente[4], '%Y-%m-%d %H:%M:%S')
        lista_clientes.insert(END, f"{cliente[1]} - {data_reuniao.strftime('%d/%m/%Y %H:%M')}")
def testar_envio():
    telefone = entry_telefone.get()
    nome = entry_nome.get()
    
    if not telefone or not nome:
        messagebox.showerror("Dados Insuficientes", "Preencha pelo menos nome e telefone para testar!")
        return
        
    hoje = datetime.now()
    data_formatada = hoje.strftime('%d/%m/%Y')
    hora_formatada = hoje.strftime('%H:%M')
    
    atualizar_status("Enviando mensagem de teste...")
    
    if enviar_whatsapp(telefone, nome, data_formatada, hora_formatada):
        messagebox.showinfo("Teste Concluído", "Mensagem de teste enviada com sucesso!")
    else:
        fallback = messagebox.askyesno("Falha no Template", "Falha ao enviar mensagem utilizando template. Deseja tentar o método simples?")
        if fallback:
            mensagem = f"Olá {nome}, este é um teste do sistema de lembretes de reuniões. Mensagem enviada em {data_formatada} às {hora_formatada}."
            if enviar_whatsapp_simples(telefone, mensagem):
                messagebox.showinfo("Teste Concluído", "Mensagem simples enviada com sucesso!")
def enviar_whatsapp_simples(telefone, mensagem):
    """
    Envia uma mensagem simples via WhatsApp usando a API da Twilio.
    :param telefone: Número de telefone no formato internacional (ex: +5511999999999).
    :param mensagem: Texto da mensagem a ser enviada.
    :return: True se a mensagem foi enviada com sucesso, False caso contrário.
    """
    config = carregar_configuracoes()
    
    # Garantir que o telefone esteja no formato correto
    if not telefone.startswith('+'):
        telefone = '+' + telefone.strip()
        
    try:
        client = Client(config['twilio_account_sid'], config['twilio_auth_token'])
        message = client.messages.create(
            body=mensagem,
            from_=f"whatsapp:{config['twilio_whatsapp_number']}",
            to=f'whatsapp:{telefone}'
        )
        logging.info(f"Mensagem simples enviada para {telefone}: {message.sid}")
        atualizar_status(f"Mensagem simples enviada em {datetime.now().strftime('%H:%M:%S')}")
        return True
    except Exception as e:
        logging.error(f"Erro ao enviar WhatsApp simples: {e}")
        messagebox.showerror("Erro de Comunicação", f"Não foi possível enviar a mensagem via WhatsApp: {e}")
        return False
# Interface gráfica principal
root = Tk()
root.title("Sistema de Lembretes de Reuniões")
root.geometry("650x580")

# Frame para melhorar a organização
frame_main = Frame(root, padx=20, pady=10)
frame_main.pack(fill="both", expand=True)

# Menu de configuração
menu_bar = Menu(root)
root.config(menu=menu_bar)
menu_config = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Configurações", menu=menu_config)
menu_config.add_command(label="Configurar Serviços", command=abrir_configuracao)
menu_help = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Ajuda", menu=menu_help)
menu_help.add_command(label="Sobre o WhatsApp Template", command=mostrar_ajuda_template)

# Título
Label(frame_main, text="Sistema de Lembretes de Reuniões", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=15)

# Frame para cadastro de clientes
frame_cadastro = LabelFrame(frame_main, text="Cadastro de Cliente", padx=10, pady=10, font=("Helvetica", 10, "bold"))
frame_cadastro.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

# Campos de entrada
Label(frame_cadastro, text="Nome do Cliente:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_nome = Entry(frame_cadastro, width=40)
entry_nome.grid(row=0, column=1, padx=10, pady=5, sticky="w")

Label(frame_cadastro, text="Telefone (com DDD):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_telefone = Entry(frame_cadastro, width=40)
entry_telefone.grid(row=1, column=1, padx=10, pady=5, sticky="w")

Label(frame_cadastro, text="E-mail:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
entry_email_cliente = Entry(frame_cadastro, width=40)
entry_email_cliente.grid(row=2, column=1, padx=10, pady=5, sticky="w")

Label(frame_cadastro, text="Data da Reunião:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
entry_data = Entry(frame_cadastro, width=40)
entry_data.grid(row=3, column=1, padx=10, pady=5, sticky="w")
Label(frame_cadastro, text="Formato: DD/MM/AAAA HH:MM", font=("Helvetica", 8), fg="gray").grid(row=4, column=1, sticky="w", padx=10)

# Frame para botões
frame_botoes = Frame(frame_main)
frame_botoes.grid(row=2, column=0, columnspan=2, pady=15)

# Botões
Button(frame_botoes, text="Adicionar Cliente", command=adicionar_cliente, width=15, bg="#e6f2ff").grid(row=0, column=0, padx=5)
Button(frame_botoes, text="Verificar Lembretes", command=verificar_lembretes, width=15, bg="#e6f2ff").grid(row=0, column=1, padx=5)
Button(frame_botoes, text="Testar Envio", command=testar_envio, width=15, bg="#e6f2ff").grid(row=0, column=2, padx=5)

# Frame para lista de clientes
frame_lista = LabelFrame(frame_main, text="Clientes Agendados", padx=10, pady=10, font=("Helvetica", 10, "bold"))
frame_lista.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
frame_main.grid_rowconfigure(3, weight=1)
frame_main.grid_columnconfigure(0, weight=1)

# Lista de clientes
lista_clientes = Listbox(frame_lista, width=60, height=15, font=("Helvetica", 10))
lista_clientes.pack(fill="both", expand=True)
scrollbar = Scrollbar(lista_clientes)
scrollbar.pack(side=RIGHT, fill=Y)
lista_clientes.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=lista_clientes.yview)

# Informação de lembretes
Label(frame_main, text="⚠️ Os lembretes são enviados automaticamente 3 dias e 1 dia antes da reunião", 
      font=("Helvetica", 9), fg="gray").grid(row=4, column=0, columnspan=2, pady=(10,0))

# Status bar
status_bar = Label(root, text="Sistema pronto", bd=1, relief=SUNKEN, anchor=W, font=("Helvetica", 9))
status_bar.pack(side=BOTTOM, fill=X)

# Atualizar lista de clientes
atualizar_lista_clientes()

# Iniciar agendamento automático
agendar_verificacoes()

# Iniciar a interface
root.mainloop()

# Fechar conexão com o banco de dados ao sair
conn.close()