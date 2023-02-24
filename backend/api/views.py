from django.http import JsonResponse
import spacy

ingles = True

if ingles:
    nlp = spacy.load("en_core_web_md")
else:
    nlp = spacy.load("es_core_news_md")


def api_home(request):
    arraySS = []
    arrayCadena = request.GET.get('user_stories', '')
    arrayCadenas = arrayCadena.split(sep='*')
    for h in range(0, len(arrayCadenas)):
        suma = 0
        divisor = 0
        cadena = arrayCadenas[h]
        cadenas = cadena.split(sep='/')
        if len(cadenas) > 1:
            for i in range(0, len(cadenas) - 1):
                for j in range(i+1, len(cadenas)):
                    hu1 = seleccionarSustantivosVerbos(cadenas[0])
                    token1 = nlp(hu1)
                    hu2 = seleccionarSustantivosVerbos(cadenas[1])
                    token2 = nlp(hu2)
                    suma += token1.similarity(token2)
                    divisor += 1

            semantic_similarity = suma / divisor
        else:
            semantic_similarity = 1

        arraySS.append(semantic_similarity)
    data = {"semantic_similarity": arraySS}
    return JsonResponse(data)


if ingles:
    def seleccionarSustantivosVerbos(historia):
        doc = nlp(historia)
        listaText = ''
        for token in doc:
            pos = token.pos_
            if pos == 'NOUN' or pos == 'PROPN':
                listaText += token.text + ' '
        return listaText
else: 
    def seleccionarSustantivosVerbos(historia):
        doc = nlp(historia)
        listaText = ''
        for token in doc:
            pos = token.pos_
            if pos == 'NOUN':
                listaText += token.text + ' '
            else:
                listaText += token.lemma_ + ' '
        return listaText
