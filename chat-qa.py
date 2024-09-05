from langchain.document_loaders.json_loader import JSONLoader, DirectoryLoader

DRIVE_FOLDER = "discussoes/"
loader = DirectoryLoader(DRIVE_FOLDER, glob='**/*.json', show_progress=True, loader_cls=JSONLoader, loader_kwargs = {'jq_schema':'.respostas[].resposta'})

documents = loader.load()

print(f'document count: {len(documents)}')
print(documents[0] if len(documents) > 0 else None)