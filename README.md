# Sistema de Controle de Marmitas (Django)

Este projeto implementa um sistema Web para registrar quais funcionários retiraram a marmita do dia, com:
- Login de administrador
- Cadastro de funcionários (com QR Code gerado pelo sistema)
- Leitura via câmera do celular (BarcodeDetector API) para QR Code / Códigos de barras
- Registro de retirada com data e hora
- Bloqueio de mais de uma retirada por funcionário no mesmo dia
- Relatório diário e mensal
- Exportação em JSON (diário ou mensal)

## Requisitos
- Python 3.10+
- Pip
- (Opcional) virtualenv

## Instalação
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configuração e execução
```bash
python manage.py migrate
python manage.py createsuperuser  # crie o usuário admin
python manage.py runserver
```
Acesse: http://127.0.0.1:8000/

Login: use as credenciais do superuser.

### Cadastro de funcionários
- Você pode cadastrar funcionários pelo menu **Funcionários** (CRUD simples) ou via **/admin** (Django Admin).
- Ao salvar um funcionário, o sistema gera automaticamente um `token` único.
- O QR Code pode ser baixado pela página do funcionário ou acessando `/funcionarios/<id>/qrcode/`.

### Registro via câmera (leitor)
- Acesse **/scanner/** no navegador do celular (Android/Chrome recomendado).
- Permita acesso à câmera. Aponte para o QR Code ou código de barras do funcionário.
- Ao detectar, o sistema envia o código e registra a retirada do dia.

### Regras
- Um funcionário só pode retirar **1 marmita por dia**. Tentativas extras no mesmo dia retornam aviso.
- O horário é registrado automaticamente na confirmação.

### Relatórios
- **/relatorios/dia?data=YYYY-MM-DD**: mostra o status do dia (retirou / não retirou) e exporta JSON.
- **/relatorios/mes?ano=YYYY&mes=MM**: resumo mensal e exporta JSON.
- Botões de exportação estão nas páginas correspondentes.

### Exportação JSON
- Em cada relatório há um botão **Exportar JSON** que baixa os registros no formato JSON simples.

### Observações sobre leitura de códigos
- O projeto usa a API **BarcodeDetector** do navegador para QR Codes e alguns formatos de barras.
- Funciona nativamente em Chrome moderno (Android e Desktop). Em browsers sem suporte, use o **input manual** exibido na tela do scanner.
- Você pode substituir por bibliotecas JS como ZXing ou jsQR se desejar, bastando trocar o arquivo `static/entregas/scanner.js`.

### Estrutura
- Projeto Django: `marmitas`
- App principal: `entregas`