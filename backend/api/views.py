from django.http import JsonResponse
import spacy

# Create your views here.
def api_home(request):
    cadena = request.GET.get('user_stories','')
    suma = 0
    divisor = 0    
    cadenas = cadena.split(sep='/')

    nlp = spacy.load("en_core_web_md")

    for i in range(0, len(cadenas) - 1):
        for j in range(i+1, len(cadenas)):
            token1 = nlp(cadenas[0])
            token2 = nlp(cadenas[1])
            suma += token1.similarity(token2)
            divisor += 1
            
    semantic_similarity = suma / divisor
    data = {"semantic_similarity":semantic_similarity}
    
    return JsonResponse(data)
