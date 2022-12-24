from django.http import JsonResponse
import spacy

# Create your views here.
def api_home(request):
    nlp = spacy.load("en_core_web_md")
    arraySS = []
    arrayCadena = request.GET.get('user_stories','')
    arrayCadenas = arrayCadena.split(sep='*')
    for h in range(0, len(arrayCadenas)):
        suma = 0
        divisor = 0
        cadena = arrayCadenas[h]
        cadenas = cadena.split(sep='/')
        if len(cadenas) > 1:
            for i in range(0, len(cadenas) - 1):
                for j in range(i+1, len(cadenas)):
                    token1 = nlp(cadenas[0])
                    token2 = nlp(cadenas[1])
                    suma += token1.similarity(token2)
                    divisor += 1
                    
            semantic_similarity = suma / divisor
        else:
            semantic_similarity = 1
            
        arraySS.append(semantic_similarity)
    data = {"semantic_similarity":arraySS}
    return JsonResponse(data)
