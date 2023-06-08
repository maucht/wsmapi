from django.shortcuts import render
# Create your views here.
from .models import DailyStats
from django.http import JsonResponse, Http404
from .serializers import DataSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

import subprocess
from django.http import JsonResponse
import os

@api_view(['GET','POST'])
def datas(request):
    info = DailyStats.objects.all()
    if request.method == 'GET':
        serializer = DataSerializer(info,many=True)
        return Response({'datas':serializer.data})
    elif request.method == 'POST':
        serializer = DataSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'datas':serializer.data})
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','POST','DELETE'])
def data(request,id):
    try: 
        info = DailyStats.objects.get(pk=id)
    except DailyStats.DoesNotExist:
        raise Http404("Data does not exist")
    serializer = DataSerializer(info)

    if request.method == "GET":
        return Response({'data':serializer.data})
    elif request.method == "POST":
        serializer = DataSerializer(info, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'data':serializer.data})
        return Response(serializer.errors)
    elif request.method== "DELETE":
        info.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response({'data':serializer.data})

def execute_script(request):
    # Execute the Python script
    script_directory = '../pyscript/'
    script_directory_path = os.path.abspath(os.path.join(os.path.dirname(__file__), script_directory))
    os.chdir(script_directory_path)

    result = subprocess.run(['python', 'main.py'], capture_output=True, text=True)
    
    # Check for any errors during script execution
    if result.returncode != 0:
        error_message = result.stderr.strip()
        return JsonResponse({'error': f'Failed to execute script: {error_message}'})
    
    # Process the script output
    output = result.stdout.strip()  # Modify as per your script's output format
    
    # Return the output as the response
    return JsonResponse({'output': output})



