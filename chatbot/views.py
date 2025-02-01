from django.shortcuts import render, redirect
from django.http import JsonResponse
from . models import FileMetadata
import os
import ollama
import uuid
import stanza
import chromadb
from django.conf import settings
import re
from transformers import pipeline
from django.db import transaction
from django.core.exceptions import ValidationError


client = chromadb.PersistentClient(path="vector_db")
collection = client.get_or_create_collection(name="docs")
def upload_text(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file_name = request.FILES['file'].name
        if FileMetadata.objects.filter(filename=file_name).exists():
            return JsonResponse({'status': 'error', 'message': 'File already uploaded'}, status=400)
        with transaction.atomic(): 
            file_metadata = FileMetadata.objects.create(
                id=uuid.uuid4(),
                filename=file_name
            )
        file_id = file_metadata.id      
        file_name = file_metadata.filename
        text = request.FILES['file'].read().decode('utf-8')
        nlp = stanza.Pipeline(lang='en', processors='tokenize')
        doc = nlp(text)
        for sentence in doc.sentences:
            sentence.text = re.sub(r'^[^\w]+|[^\w]+$', '', sentence.text)
        sentences = [sentence.text.lower() for sentence in doc.sentences]
        for i, d in enumerate(sentences):
            response = ollama.embed(model="llama3.2", input=d)
            embeddings = response["embeddings"]
            print(d)
            collection.add(
                ids=[f"{file_id}_{i}"], 
                embeddings=embeddings,
                documents=[d],
                metadatas=[{"source_file": str(file_name)}]

            )
    return render(request, 'upload.html')

def query_chatbot(request):
    if request.method == 'POST':
        query = request.POST.get('query').lower()
        print("hello after query") 
        try:
            query_embedding = ollama.embed(model="llama3.2", input=query)["embeddings"]
        except:
            return JsonResponse({'response': "Failure in embedding query"})
        print("hello after query embedding")
        results = collection.query(
            query_embeddings=query_embedding[0],
            n_results=1
        )
        print(results)
        if results["documents"]:
            try:
                retrieved_text, distance = results["documents"][0], results["distances"][0][0]
                source_file = results["metadatas"][0][0]["source_file"]
            except:
                return JsonResponse({'response': "No relevant results found.", 'source_file': "Unknown"})


        else:
            return JsonResponse({'response': "No relevant results found.", 'source_file': "Unknown"})

        print("Retrieved Text:", retrieved_text)
        print("Distance:", distance)
        if 0.50 <= distance <= 1.0:
            relevance = retrieved_text
        else:
            relevance = "I Don't Know"
            source_file = "Unknown source"
        return JsonResponse({'response': relevance, 'source_file': source_file})
    return render(request, 'chat.html')

def list_files(request):
    # Get all files from the MySQL database
    files = FileMetadata.objects.all()
    # print(files)
    file_list = [{"id": file.id, "filename": file.filename} for file in files]
    return render(request, 'list_files.html', {'files': file_list})
def delete_file(request, filename):
    if request.method == 'POST':
        try:
            print("hello")
            file_metadata = FileMetadata.objects.get(filename=filename)
            print("try")
            # file_metadata.delete()
            return JsonResponse({'status': 'success'})
        except FileMetadata.DoesNotExist:
            print("except")
            return JsonResponse({'status': 'error', 'message': 'File not found'}, status=404)
    print("konotai na")
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


