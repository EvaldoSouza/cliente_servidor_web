import os
import mimetypes
from urllib.parse import quote, unquote #sera que pode usar? Vale a pena?
import socket

# Diretório base do servidor
base_directory = '/home/evaldo'

# Porta em que o servidor irá rodar
port = 8001

# Função para gerar a resposta HTTP
def generate_response(status, content_type, content):
    response = f"HTTP/1.1 {status}\r\n"
    response += f"Content-Type: {content_type}; charset= utf-8\r\n"
    response += f"Content-Length: {len(content)}\r\n"
    response += "\r\n"
    #algumas vezes vem binario, outras string...
    #perciso separar o que vier text/ do resto
    if isinstance(content, str):
        response += content
    elif content_type.__contains__("text"): 
        if content_type.__contains__("csv"):
            response = response.encode() + content
            return response
        else:
            #se for um text em binário, decodifica e concatena
            response += content.decode()
    else:
        #imagens e tals? o que fazer? vem em bytes
        response = response.encode() + content
        return response

    #esse encode faz umas coisas funcionar, e quebra outras...
    return response.encode()

# Função para listar os arquivos e pastas de um diretório
def list_files(directory):
    entries = os.listdir(directory)
    links = []
    for entry in entries:
        entry_path = os.path.join(directory, entry)
        if os.path.isfile(entry_path):
            link = f'<a href="{entry}">{entry}</a>'
            links.append(link)
        elif os.path.isdir(entry_path):
            link = f'<a href="{entry}/">{entry}/</a>'
            links.append(link)
    
    arquivos = "<br>".join(links)
    titulo = f'<head> <title> TP PARA O FLÁVIO </title> </head> <body> <header> TP PARA O FLÁVIO </br></header></body>'
    pagina = titulo + arquivos
    return pagina

# Função para tratar as solicitações HTTP
def handle_request(client_socket, request):
    request_lines = request.split("\r\n")

    # Verifica se a solicitação está completa
    if not request_lines[-1]:
        print("Processando request ", request_lines[0])
        request_method, request_path, _ = request_lines[0].split(" ")

        if request_method == "GET":
            if request_path == "/HEADER":
                # Retorna o cabeçalho HTTP da requisição
                response = generate_response("200 OK", "text/plain", str(request).encode()) #mantém esse encode?
            else:
                file_path = os.path.join(base_directory, unquote(request_path[1:]))

                if os.path.isdir(file_path):
                    # Lista o conteúdo do diretório
                    content = list_files(file_path)
                    response = generate_response("200 OK", "text/html", unquote(content))
                elif os.path.isfile(file_path):
                    # Verifica o tipo MIME do arquivo
                    content_type, _ = mimetypes.guess_type(file_path)
                    
                    if content_type == 'text/plain':
                    # Se for arquivo TXT, o tratamento é diferenciado
                        with open(file_path, 'r') as file:
                            content = file.read()
                    
                        response = generate_response("200 OK", content_type, content)
                    else:
                        with open(file_path, 'rb') as file:
                            content = file.read()
                        
                        response = generate_response("200 OK", content_type, content)
                else:
                    # Arquivo ou diretório não encontrado
                    response = generate_response("404 Not Found", "text/html", "<h1>404 Not Found</h1>")
        else:
            # Método não suportado
            response = generate_response("405 Method Not Allowed", "text/html", "<h1>405 Method Not Allowed</h1>")
    else:
        # Solicitação incompleta, aguarda próxima parte
        print("Solicitação incompleta!")
        response = b""  # Retorna uma resposta vazia por enquanto

    # Envia a resposta ao cliente
    client_socket.sendall(response)
    client_socket.close()

# Cria o socket do servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", port))
server_socket.listen(1)
print(f"Servidor rodando na porta {port}")

while True:
    # Aceita a conexão de um cliente
    client_socket, client_address = server_socket.accept()

    # Recebe a solicitação do cliente
    request = b""
    while True:
        data = client_socket.recv(1024)
        request += data
        if not request:
            print("request vazia")
            break
        if b"\r\n\r\n" in request:
            break

    # Trata a solicitação e envia a resposta
    if request:
        handle_request(client_socket, request.decode())
