from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import UploadedFile
import os
import ollama
# import openai
import stanza
import chromadb
from django.conf import settings
import re
from transformers import pipeline

# client = chromadb.PersistentClient(path=os.path.join(settings.BASE_DIR, "vector_db"))
# collection = client.get_or_create_collection(name="embeddings")
client = chromadb.Client()
collection = client.create_collection(name="docs")
# openai.api_key = "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"

def upload_text(request):
    if request.method == 'POST' and request.FILES.get('file'):
        # print("success")
        # uploaded_file = UploadedFile(file=request.FILES['file'])
        # uploaded_file.save()

        text = request.FILES['file'].read().decode('utf-8')
        nlp = stanza.Pipeline(lang='en', processors='tokenize')
        doc = nlp(text)
        for sentence in doc.sentences:
            sentence.text = re.sub(r'^[^\w]+|[^\w]+$', '', sentence.text)
        sentences = [sentence.text for sentence in doc.sentences]
        for i, d in enumerate(sentences):
            response = ollama.embed(model="llama3.2", input=d)
            embeddings = response["embeddings"]
            collection.add(
                ids=[str(i)],
                embeddings=embeddings,
                documents=[d],
  )
    # return redirect('query_chatbot')

    return render(request, 'upload.html')

def query_chatbot(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        query_embedding = ollama.embed(model="llama3.2", input=query)["embeddings"]
        results = collection.query(
            query_embeddings=[query_embedding[0]],
            n_results=1
        )
        retrieved_text = results['documents'][0]
        print("WHattttt the")
        print(len(retrieved_text))
        print(retrieved_text if len(retrieved_text)> 0 else "I dont know")
        # print(response_text.encode('utf-8'))
        # return JsonResponse({'response': response_text})

    return render(request, 'chat.html')
