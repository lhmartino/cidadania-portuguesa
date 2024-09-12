from langchain_community.document_loaders import JSONLoader, DirectoryLoader
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import LlamaCpp


DRIVE_FOLDER = "discussoes/"
#loader = DirectoryLoader(DRIVE_FOLDER, glob='**/*.json', show_progress=True, loader_cls=JSONLoader, loader_kwargs = {'jq_schema':'.respostas[]?.resposta'}, text_content=False)
loader = JSONLoader(file_path="discussoes/forum.json", jq_schema=".discussoes[].respostas[].resposta", text_content=False)

documents = loader.load()


text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(documents)

# vectorstore = Chroma.from_documents(
#     documents=all_splits,
#     embedding=OllamaEmbeddings(model="llama3", show_progress=True),
#     persist_directory="/chroma_db",

# )

emb = OllamaEmbeddings(model="llama3", show_progress=True)

vectorstore = Chroma(    
    embedding_function=emb,
    persist_directory="/chroma_db",
)

llm = LlamaCpp(model_path="/models-gpt4all/Meta-Llama-3-8B-Instruct.Q4_0.gguf", max_tokens=100,n_ctx=512)


# Retrieve and generate using the relevant snippets of the blog.
retriever = vectorstore.as_retriever()
prompt = hub.pull("rlm/rag-prompt")


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

print(rag_chain.invoke("Quais os documentos necessários para ATRIBUIÇÃO de NETOS?"))


#print(f'document count: {len(documents)}')
#print(documents[0] if len(documents) > 0 else None)