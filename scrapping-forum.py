from bs4 import BeautifulSoup
import requests


def contain_last_page(css_class):
    if css_class is None or css_class.find("LastPage") == -1:
        return False
    else:
        return True

def contain_item_comment(css_class):
    if css_class is None or css_class.find("ItemComment") == -1:
        return False
    else:
        return True


#lista para armazenar todas as discussões do fórum
discussoes_list = []

# Raiz do scrapping é a pagina de categorias
url = "https://forum.cidadaniaportuguesa.com/categories"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# lista de categorias 
categorias = soup.find_all("a", class_="Title")


for categoria in categorias:
    #print("Link categoria:", categoria['href'])    

    #Lê página de discussões da categoria
    response = requests.get(categoria['href'])
    soup = BeautifulSoup(response.text, "html.parser")

    #Total de páginas de discussões da categoria exibida na paginação
    paginas = soup.find_all("a", class_=contain_last_page, limit=1)
    paginas = paginas[0].text
    #print("#Paginas: ", paginas.strip())

    #itera nas páginas de discussões (da 1 até a máxima exibida na paginação)
    for i in range(1, int(paginas)+1):
        url = categoria['href'] + "/p" + str(i)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        #Discussoes da pagina "i"
        discussoes = soup.find_all("div", class_="Title")
        for discussao in discussoes:
            #dicionário da discussao
            discussao_dict  = {}
            #print("Link da discussao:", discussao.find("a").get('href'))

            #carrega atributos da discussão:

            discussao_dict["categoria"] = categoria.text            

            url = discussao.find("a").get('href')
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            titulo = soup.find("div", class_="PageTitle").find("h1").text
            discussao_dict["titulo"] = titulo

            autor = soup.find("div", class_="Discussion").find("div", class_="AuthorWrap").find('a', class_="Username").text
            discussao_dict["autor"] = autor

            data_criacao = soup.find("div", class_="Discussion").find("div", class_="Meta DiscussionMeta").find('time').get('datetime')
            discussao_dict["data_criacao"] = data_criacao

            pergunta = soup.find("div", class_="Discussion").find("div", class_="Message userContent").find_all('p')
            pergunta = [p.text for p in pergunta]
            pergunta = "\n".join(pergunta)

            discussao_dict["pergunta"] = pergunta            

            paginas_respostas = 1

            #verifica se a pergunta tem paginação nas respostas
            if(soup.find(role="navigation") is not None):
              #print("#### Contém paginação")
              paginas_respostas = soup.find_all("a", class_=contain_last_page, limit=1)
              paginas_respostas = paginas_respostas[0].text
              #print("#### última pagina de respostas", paginas_respostas)

            #itera pelas páginas de respostas
            for j in range(1, int(paginas_respostas)+1):
              
              #print("Entrou no loop das paginas_respostas")
              url = url + "/p" + str(j)
              response = requests.get(url)
              soup = BeautifulSoup(response.text, "html.parser")

              respostas = soup.find_all("li", class_=contain_item_comment)

              #cria lista de respostas para a pergunta/discussao
              respostas_list = []

              #itera nas respostas da página "j"
              for resposta in respostas:
                  #dicionário da resposta
                  resposta_dict = {}
                  resposta = resposta.find("div", class_="Message userContent").find_all('p')
                  resposta = [p.text for p in resposta]
                  resposta = "\n".join(resposta)

                  #carrega atributos da resposta:

                  resposta_dict["resposta"] = resposta

                  autor = soup.find("div", class_="AuthorWrap").find('a', class_="Username").text
                  resposta_dict["autor"] = autor

                  data_criacao = soup.find("div", class_="Meta CommentMeta CommentInfo").find('time').get('datetime')
                  resposta_dict["data_criacao"] = data_criacao

                  #inclui resposta na lista
                  respostas_list.append(resposta_dict)                  

                  #print("   Resposta:", resposta)

              #adiona lista de respostas na discussao/pergunta    
              discussao_dict["respostas"] = (respostas_list)

            print(discussao_dict)

            #adiciona discussão na lista
            discussoes_list.append(discussao_dict)