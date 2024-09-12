from langchain_community.llms import LlamaCpp

llm = LlamaCpp(model_path="/models-gpt4all/Meta-Llama-3-8B-Instruct.Q4_0.gguf", max_tokens=100,n_ctx=512)



response = llm.invoke("Quais são os melhores amigos do Mickey Mouse?")

print(response)