# Sistema de Lembretes de Reuniões

Um aplicativo desktop em Python para gerenciar compromissos e enviar lembretes automáticos por WhatsApp e e-mail.

## 📋 Descrição

O Sistema de Lembretes de Reuniões é uma ferramenta desenvolvida em Python com interface gráfica Tkinter que permite o cadastro de clientes e seus compromissos, enviando lembretes automáticos via WhatsApp e e-mail 3 dias e 1 dia antes da data agendada.

## ✨ Funcionalidades

- Cadastro de clientes com nome, telefone, e-mail e data da reunião
- Envio automático de lembretes via WhatsApp e e-mail
- Verificação horária de compromissos próximos
- Interface gráfica intuitiva para gerenciamento de compromissos
- Criptografia de dados sensíveis
- Sistema de logs para monitoramento de atividades
- Testes de envio de mensagens

## 🔧 Tecnologias Utilizadas

- Python 3.x
- Tkinter para interface gráfica
- SQLite para armazenamento de dados
- Twilio API para envio de mensagens WhatsApp
- SMTP para envio de e-mails
- Bibliotecas: cryptography, threading, re, json, logging

## 📦 Dependências

```
tkinter
sqlite3
twilio
cryptography
```

## 🚀 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/sistema-lembretes-reunioes.git
cd sistema-lembretes-reunioes
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o programa:
```bash
python main.py
```

## ⚙️ Configuração

Antes de utilizar o sistema, é necessário configurar os serviços de notificação:

1. Acesse o menu "Configurações" > "Configurar Serviços"
2. Preencha com suas credenciais da Twilio:
   - Account SID
   - Auth Token
   - Número do WhatsApp (formato internacional, ex: +5511999887766)
   - Template SID para mensagens WhatsApp

3. Configure seu e-mail para envio de notificações:
   - Endereço de e-mail
   - Senha do e-mail (recomendamos criar uma senha de app específica)

## 🔐 Segurança

O sistema utiliza criptografia para proteger informações sensíveis:
- As senhas de e-mail são armazenadas de forma criptografada
- Uma chave única é gerada para cada instalação

## 📝 Como Usar

1. **Cadastrar um cliente**:
   - Preencha os campos com nome, telefone, e-mail e data da reunião
   - Clique em "Adicionar Cliente"

2. **Verificar lembretes**:
   - Clique em "Verificar Lembretes" para forçar a verificação manual
   - O sistema verifica automaticamente a cada hora

3. **Testar envio**:
   - Preencha pelo menos nome e telefone
   - Clique em "Testar Envio" para enviar uma mensagem de teste

## 📊 Logs

O sistema mantém registros de todas as operações no arquivo `lembretes.log`, facilitando o monitoramento e a resolução de problemas.

## 📱 Templates do WhatsApp

Para utilizar os templates do WhatsApp:
1. Crie um template no console da Twilio
2. O template deve incluir variáveis para nome ({{1}}), data ({{2}}) e hora ({{3}})
3. Aguarde a aprovação da Meta (pode levar alguns dias)
4. Copie o SID do template aprovado para as configurações do sistema

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes.

---

Desenvolvido por Renan Matheus
