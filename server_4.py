import os
import http.server
import socketserver
from pathlib import Path
import mimetypes

# Diretório base do servidor
base_directory = '/home/evaldo'

# Porta em que o servidor irá rodar
port = 8000

# Classe que trata as requisições do servidor
class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def list_files(self, directory):
        # Obtém a lista de arquivos e pastas do diretório
        entries = os.listdir(directory)

        # Cria uma lista de links para os arquivos e pastas
        links = []
        for entry in entries:
            entry_path = os.path.join(directory, entry)
            if os.path.isfile(entry_path):
                # Se for um arquivo, adiciona um link para download
                link = f'<a href="{entry}">{entry}</a>'
                links.append(link)
            elif os.path.isdir(entry_path):
                # Se for uma pasta, adiciona um link para explorar a pasta
                link = f'<a href="{entry}/">{entry}/</a>'
                links.append(link)

        # Retorna a lista de arquivos e pastas como uma página HTML
        return '<br>'.join(links)

    def do_GET(self):
        if self.path == '/HEADER':
            # Retorna o cabeçalho HTTP da requisição
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(str(self.headers).encode())
        else:
            file_path = os.path.join(base_directory, self.path[1:])

            # Verifica se o caminho é um diretório
            if os.path.isdir(file_path):
                # Lista o conteúdo do diretório
                content = self.list_files(file_path)

                # Retorna o conteúdo como resposta
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(content.encode())
            #se não for diretório
            elif os.path.isfile(file_path):
                # Obtém o tipo MIME do arquivo
                mime_type, _ = mimetypes.guess_type(file_path)

                if mime_type == 'text/plain':
                    # Se for arquivo TXT, o tratamento é diferenciado
                    with open(file_path, 'r') as file:
                        content = file.read()

                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(content.encode()) #precisa do encode senão o navegador não mostra
                else:
                # lendo o arquivo...será que o r é suficiente, ou tem que ter o rb?
                #tem que ter o rb
                    print(mime_type)
                    with open(file_path, 'rb') as file:
                        content = file.read()

                    self.send_response(200)
                    self.send_header('Content-type', mime_type)
                    self.end_headers()
                    self.wfile.write(content) #se tiver o encode, da erro
            
            else:
                # Se o arquivo ou diretório não existe, retorna um erro 404
                self.send_error(404)

# Configura o servidor com o handler personalizado
with socketserver.TCPServer(("", port), MyRequestHandler) as httpd:
    print(f"Servidor rodando na porta {port}")
    httpd.serve_forever()
