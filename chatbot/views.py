from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import UploadedFile
import os
import ollama
import stanza
import chromadb
from django.conf import settings
import re
from transformers import pipeline

client = chromadb.PersistentClient(path="vector_db")
collection = client.get_or_create_collection(name="docs")

def upload_text(request):
    if request.method == 'POST' and request.FILES.get('file'):
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
    return render(request, 'upload.html')

def query_chatbot(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        query_embedding = ollama.embed(model="llama3.2", input=query)["embeddings"]
        results = collection.query(
            query_embeddings=query_embedding[0],
            n_results=1
        )
        retrieved_text,distance = results['documents'][0],results['distances'][0][0]
        if 0.50 <= distance <= 1.0:
            relevance = retrieved_text
        else:
            relevance = "I Don't Know"
        return JsonResponse({'response': relevance})
    return render(request, 'chat.html')
