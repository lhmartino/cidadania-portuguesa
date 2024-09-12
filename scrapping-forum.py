from bs4 import BeautifulSoup
import requests
import json


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
    
def save_json(file_name, dictionary):
    json_object = json.dumps(dictionary, ensure_ascii=False, indent=4)
 
    # Writing to sample.json
    with open("discussoes/"+file_name+".json", "w", encoding='utf8') as outfile:
        outfile.write(json_object)


#lista para armazenar todas as discussões do fórum
discussoes_list = []

# Raiz do scrapping é a pagina de categorias
url = "https://forum.cidadaniaportuguesa.com/categories"
response = requests.get(url)
soup = BeautifulSoup(response.text, "lxml")

# lista de categorias
categorias = soup.find_all("a", class_="Title")

lista_categorias_pular = ["Backup do Orkut", "English", "Política de privacidade"]

for categoria in categorias:
    #print("Link categoria:", categoria['href'])

    if(categoria.text in lista_categorias_pular):
        continue

    print("#categoria atual: ", categoria.text)

    #Lê página de discussões da categoria
    response = requests.get(categoria['href'])
    soup = BeautifulSoup(response.text, "lxml")

    #Total de páginas de discussões da categoria exibida na paginação
    paginas = soup.find_all("a", class_=contain_last_page, limit=1)
    paginas = paginas[0].text
    #print("#Paginas: ", paginas.strip())

    #itera nas páginas de discussões (da 1 até a máxima exibida na paginação)
    for i in range(1, int(paginas)+1):
        url = categoria['href'] + "/p" + str(i)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")

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
            soup = BeautifulSoup(response.text, "lxml")

            titulo = soup.find("div", class_="PageTitle").find("h1").text
            discussao_dict["titulo"] = titulo

            autor = soup.find("div", class_="Discussion").find("div", class_="AuthorWrap").find('a', class_="Username").text
            discussao_dict["autor"] = autor

            data_criacao = soup.find("div", class_="Discussion").find("div", class_="Meta DiscussionMeta").find('time').get('datetime')
            discussao_dict["data_criacao"] = data_criacao

            pergunta = soup.find("div", class_="Discussion").find("div", class_="Message userContent").find_all('p')
            if pergunta:    
                pergunta = [p.text for p in pergunta]
                pergunta = " ".join(pergunta)
            else:
                pergunta = soup.find("div", class_="Discussion").find("div", class_="Message userContent").text.replace("<br>", "\n")

            discussion_id = soup.find("div", class_=["Item", "ItemDiscussion", 'Role_Member']).get('id')

            print("### Discussão atual: ", titulo + " - " + discussion_id)

            discussao_dict["pergunta"] = pergunta

            paginas_respostas = 1

            

            #itera pelas páginas de respostas
            for j in range(1, int(paginas_respostas)+1):
              
              #verifica se a pergunta tem paginação nas respostas
              if(j == 1 and soup.find(role="navigation") is not None):
                #print("#### Contém paginação")
                paginas_respostas = soup.find_all("a", class_=contain_last_page, limit=1)
                paginas_respostas = paginas_respostas[0].text
                #print("#### última pagina de respostas", paginas_respostas)

              #print("Entrou no loop das paginas_respostas")
              url = url + "/p" + str(j)
              response = requests.get(url)
              soup = BeautifulSoup(response.text, "lxml")

              

              respostas = soup.find_all("li", class_=contain_item_comment)

              #cria lista de respostas para a pergunta/discussao
              respostas_list = []

              #itera nas respostas da página "j"
              for resposta in respostas:
                  #dicionário da resposta
                  resposta_dict = {}
                  resposta_text = resposta.find("div", class_="Message userContent").find_all('p')
                  
                  if resposta_text:    
                    resposta_text = [p.text for p in resposta_text]
                    resposta_text = " ".join(resposta_text)
                  else:            
                    resposta_text = resposta.find("div", class_="Message userContent").text            
                    resposta_text = resposta_text.replace("\n                            ", "")

                  #carrega atributos da resposta:

                  resposta_dict["resposta"] = resposta_text.replace("\n\n","\n")

                  autor = soup.find("div", class_="AuthorWrap").find('a', class_="Username").text
                  resposta_dict["autor"] = autor

                  data_criacao = soup.find("div", class_="Meta CommentMeta CommentInfo").find('time').get('datetime')
                  resposta_dict["data_criacao"] = data_criacao

                  #inclui resposta na lista
                  respostas_list.append(resposta_dict)

                  #print("   Resposta:", resposta)

              #adiona lista de respostas na discussao/pergunta
              discussao_dict["respostas"] = (respostas_list)

            #print(discussao_dict)
            #save_json(discussion_id, discussao_dict)

            #adiciona discussão na lista
            discussoes_list.append(discussao_dict)
            save_json("forum", discussoes_list)