# Importación de bibliotecas y modelos necesarios
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import spacy
import json
from configuraciones.models import Configuracion
from microservicios.models import Microservicio
from urllib.parse import unquote

# Configuración del idioma (Inglés o Español)
ingles = True

# Vista protegida contra CSRF
@csrf_exempt
def api_home(request):
    print("\n------------- Inicio de la vista api_home -------------")

    # Verificación del método de la solicitud
    if request.method != "POST":
        print("Solicitud no válida. Se retorna una respuesta vacía.")
        return JsonResponse({})

    # Obtención de la información de historias de usuario desde la solicitud
    user_stories = request.POST.get('user_stories', '')

    # Procesamiento de la información de historias de usuario
    if not user_stories:
        # Carga de datos JSON desde el cuerpo de la solicitud
        JSON = json.loads(request.body)
        datos_JSON = json.dumps(JSON)

        # Extracción de información específica del primer elemento de userStories
        nom_proyecto = JSON[0]["userStories"][0]["project"]
        cant_microservicios = len(JSON)
        cant_historias = 0
        arreglo_stringsHUs = []

        # Iteración sobre cada microservicio en la solicitud
        for microservicio in JSON:
            cant_historias += len(microservicio["userStories"])
            cadena_historias = ""  # String para almacenar IDs de HUs

            # Iteración sobre cada historia de usuario en el microservicio
            for historia in microservicio["userStories"]:
                # Eliminación de "US" y "-" de los IDs de historias
                historia_sin_guion = historia["id"].replace("US", "")
                historia_sin_guion = historia_sin_guion.replace("-", "")
                cadena_historias += historia_sin_guion + ","

            # Procesamiento final del string de IDs de HUs
            cadena_historias = cadena_historias[:-1]
            arreglo_historias = cadena_historias.split(',')
            
            # Conversión de IDs a enteros y ordenamiento
            nums = [int(x) for x in arreglo_historias]
            nums.sort()
            
            # Reconstrucción del string de IDs de HUs con "US" agregado
            cadena_historias = ""
            for elemento in nums:
                cadena_historias += "US" + str(elemento) + ","

            cadena_historias = cadena_historias[:-1]
            arreglo_stringsHUs.append(cadena_historias)

        # Búsqueda de configuraciones en la base de datos
        configuraciones = Configuracion.objects.filter(
            nombre_proyecto=nom_proyecto,
            cantidad_microservicios=cant_microservicios,
            cantidad_historias=cant_historias
        )

        # Procesamiento de configuraciones encontradas
        if configuraciones:
            for configuracion in configuraciones:
                registros = Microservicio.objects.filter(
                    config_id=configuracion.id
                )
                if registros:
                    coincidencias_MSs = 0

                    # Comparación de strings de IDs de HUs entre solicitud y base de datos
                    for i in range(len(arreglo_stringsHUs)):
                        for j in range(len(registros)):
                            if arreglo_stringsHUs[i] == registros[j].historias:
                                coincidencias_MSs += 1

                    # Si todas las coincidencias son encontradas, se retorna el JSON de la base de datos
                    if coincidencias_MSs == cant_microservicios:
                        data = {"nueva_config": False,
                                "configuracion": configuracion.json_info}
                        print("Configuración existente encontrada en la base de datos.")
                        print("------------- Fin de la vista api_home -------------\n")
                        return JsonResponse(data)

            # Si no se encuentran todas las coincidencias, se guarda una nueva configuración en la BD
            Configuracion.objects.create(
                nombre_proyecto=nom_proyecto,
                cantidad_microservicios=cant_microservicios,
                cantidad_historias=cant_historias,
                json_info=datos_JSON
            )

            # Obtención del ID de la configuración recién guardada y almacenamiento de registros en Microservicios
            ultimo = Configuracion.objects.all().last()
            if ultimo:
                for microservicios in arreglo_stringsHUs:
                    Microservicio.objects.create(
                        config_id=ultimo.id,
                        historias=microservicios
                    )
                data = {"nueva_config": True}
                print("Nueva configuración creada y registrada en la base de datos.")
                print("------------- Fin de la vista api_home -------------\n")
                return JsonResponse(data)
            
        else:
            # Si no se encuentran configuraciones, se guarda una nueva configuración en la BD
            Configuracion.objects.create(
                nombre_proyecto=nom_proyecto,
                cantidad_microservicios=cant_microservicios,
                cantidad_historias=cant_historias,
                json_info=datos_JSON
            )

            # Obtención del ID de la configuración recién guardada y almacenamiento de registros en Microservicios
            ultimo = Configuracion.objects.all().last()
            if ultimo:
                for microservicios in arreglo_stringsHUs:
                    Microservicio.objects.create(
                        config_id=ultimo.id,
                        historias=microservicios
                    )
                data = {"nueva_config": True}
                print("Nueva configuración creada y registrada en la base de datos.")
                print("------------- Fin de la vista api_home -------------\n")
                return JsonResponse(data)
    else:
        # Procesamiento de la cadena de historias de usuario para calcular similitud semántica
        arrayCadena = request.POST.get('user_stories', '')
        if arrayCadena:
            if ingles:
                nlp = spacy.load("en_core_web_md")
            else:
                nlp = spacy.load("es_core_news_md")

            arraySS = []
            arrayCadenas = arrayCadena.split(sep='*')
            print("ArrayCadenas")
            print(arrayCadenas)

            # Iteración sobre cada cadena en la solicitud
            for h in range(0, len(arrayCadenas)):
                suma = 0
                divisor = 0
                cadena = arrayCadenas[h]
                print("Cadena antes del procesamiento:", cadena)
                
                # Decodificar caracteres especiales
                cadena_decodificada = unquote(cadena)
                
                # Separar las palabras por '/'
                palabras = cadena_decodificada.split('/')

                # Eliminar el carácter '/' de cada palabra y filtrar las palabras no vacías
                palabras_filtradas = [palabra.strip() for palabra in palabras if palabra.strip()]

                # Si no hay palabras, incluir la cadena original
                if not palabras_filtradas:
                    palabras_filtradas = [cadena_decodificada]

                print("Cadena después del procesamiento:", ' '.join(palabras_filtradas))
                
                if len(palabras_filtradas) > 1:
                    for i in range(0, len(palabras_filtradas) - 1):
                        for j in range(i + 1, len(palabras_filtradas)):
                            # Preprocesamiento de las cadenas antes de enviarlas a spaCy
                            doc1 = nlp(palabras_filtradas[i])
                            doc2 = nlp(palabras_filtradas[j])

                            # Cálculo de similitud semántica
                            suma += doc1.similarity(doc2)
                            divisor += 1

                    semantic_similarity = suma / divisor if divisor > 0 else 0
                else:
                    semantic_similarity = 1

                arraySS.append(semantic_similarity)

            data = {"semantic_similarity": arraySS}
            print("Similitud semántica calculada y retornada como respuesta.")
            print("Similitud semantica")
            print(arraySS)
            print("------------- Fin de la vista api_home -------------\n")
            return JsonResponse(data)
        else:
            print("Solicitud no válida. La cadena de historias de usuario está vacía.")
            return JsonResponse({})


# Configuración de cabeceras para permitir solicitudes desde http://localhost:3000
    JsonResponse["Access-Control-Allow-Origin"] = "http://localhost:3000"
    JsonResponse["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    JsonResponse["Access-Control-Allow-Headers"] = "Content-Type"

    print("Solicitud no válida. Se retorna una respuesta con información de solicitud inválida.")
    print("------------- Fin de la vista api_home -------------\n")
    return JsonResponse({"invalid": request.POST})


# if ingles:
#     nlp = spacy.load("en_core_web_md")
# else:
#     nlp = spacy.load("es_core_news_md")


# def api_home(request):
#     arraySS = []
#     arrayCadena = request.GET.get('user_stories', '')
#     arrayCadenas = arrayCadena.split(sep='*')
#     for h in range(0, len(arrayCadenas)):
#         suma = 0
#         divisor = 0
#         cadena = arrayCadenas[h]
#         cadenas = cadena.split(sep='/')
#         if len(cadenas) > 1:
#             for i in range(0, len(cadenas) - 1):
#                 for j in range(i+1, len(cadenas)):
#                     hu1 = seleccionarSustantivosVerbos(cadenas[0])
#                     token1 = nlp(hu1)
#                     hu2 = seleccionarSustantivosVerbos(cadenas[1])
#                     token2 = nlp(hu2)
#                     suma += token1.similarity(token2)
#                     divisor += 1

#             semantic_similarity = suma / divisor
#         else:
#             semantic_similarity = 1

#         arraySS.append(semantic_similarity)
#     data = {"semantic_similarity": arraySS}
#     return JsonResponse(data)


# if ingles:
#     def seleccionarSustantivosVerbos(historia):
#         doc = nlp(historia)
#         listaText = ''
#         for token in doc:
#             pos = token.pos_
#             if pos == 'NOUN' or pos == 'PROPN':
#                 listaText += token.text + ' '
#         return listaText
# else:
#     def seleccionarSustantivosVerbos(historia):
#         doc = nlp(historia)
#         listaText = ''
#         for token in doc:
#             pos = token.pos_
#             if pos == 'NOUN':
#                 listaText += token.text + ' '
#             else:
#                 listaText += token.lemma_ + ' '
#         return listaText


######  Código dado por el profe Vera (aún por adaptar e implementar)  ###########


# def init(self, lenguaje, modulo):
#     spacy.prefer_gpu()
#     if lenguaje == 'es':
#         if modulo == 'md':
#             self.nlp = spacy.load("es_core_news_md")
#         if modulo == 'sm':
#             self.nlp = spacy.load("es_core_news_sm")
#     if lenguaje == 'en':
#         if modulo == 'md':
#             self.nlp = spacy.load("en_core_web_md")
#         if modulo == 'sm':
#             self.nlp = spacy.load("en_core_web_sm")


# def identificarVerbosEntidades(self, historiaUsuario):
#     texto = historiaUsuario.nombre + ": " + historiaUsuario.descripcion
#     #texto = historiaUsuario.nombre
#     doc = self .n1p(texto)
#     listaText = ''
#     listLemmas = ''
#     lista = []
#     for token in doc:
#         pos = token.pos_
#         if pos == 'NOUN' or pos == 'PROPN':
#             hutoken = [token.text, token.lemma_, token.pos_, token.vector_norm, token.has_vector]
#             listaText += token.text + ' '
#             listLemmas += token.lemma_ + ' '
#     lista = [historiaUsuario, listaText, listLemmas]
#     return lista


# def identificarEntidadHistorias(self, listaHistorias):
#     listaEntidadesHU = []
#     for historia in listaHistorias:
#         lista = self.identificarVerbosEntidades(historia)
#         textos = lista[1]
#         lemmas = lista[2]
#         frecuenciaText = Counter(textos.split(' '))
#         frecuencaLema = Counter(lemmas.split(' '))

#         dicText = frecuenciaText.most_common(2)
#         dicLema = frecuencaLema.most_common(2)

#         entidadText = ""
#         for txt in dicText:
#             entidadText += str(txt[0]) + " "

#         entidadLema = ""
#         for txt in dicLema:
#             entidadLema += str(txt[0]) + " "

#         vector = [historia, entidadText, entidadLema]
#         listaEntidadesHU.append(vector)
#     return listaEntidadesHU


# def identificarEntidadesMicroservicio(self, ms):
#     historias = ms.getHistorias()
#     texto = ''
#     listaText = ""
#     listLemmas = ""
#     for hu in historias:
#         texto, " " + hu.historia.nombre + " " + hu.historia.descripcion + " "

#     doc = self.n1p(texto)
#     for token in doc:
#         pos = token.pos_
#         if pos == 'NOUN' or pos == 'PROPN':
#             listaText += token.text + ' '
#             listLemmas += token.lemma_ + ' '

#     frecuenciaText = Counter(listaText.split(' '))
#     frecuencaLema = Counter(listLemmas.split(' '))

#     dicText = frecuenciaText.most_common(3)
#     dicLema = frecuencaLema.most_common(3)

#     entidadText = ''
#     for txt in dicText:
#         entidadText += str(txt[0]) + " "

#     entidadLema = ''
#     for txt in dicLema:
#         entidadLema += str(txt[0]) + " "

#     lista = [ms, listaText, listLemmas, entidadText, entidadLema]
#     return lista


# def calcularSimilitud(self, listaHistorias, aplicarEn):
#     matrizSimilitud = []
#     textos = []
#     for historia in listaHistorias:
#         lista = self.identificarVerbosEntidades(historia)
#         textos.append(lista)

#     for texto in textos:
#         hu = texto[0]
#         tex = texto[1]
#         lem = texto[2]
#         if aplicarEn == 'lemma':
#             doc1 = self.n1p(lem)
#         if aplicarEn == 'text':
#             doc1 = self.n1p(tex)
#         similitudes = [hu]

#         for tex_hu in textos:
#             hu2 = tex_hu[0]
#             texto2 = tex_hu[1]
#             lemma2 = tex_hu[2]
#             if aplicarEn == 'lemma':
#                 doc2 = self.n1p(lemma2)
#             if aplicarEn == 'text':
#                 doc2 = self.n1p(texto2)
#             similitud = doc1.similarity(doc2)
#             dicc = [hu2, similitud]
#             similitudes.append(dicc)

#         matrizSimilitud.append(similitudes)
#     return matrizSimilitud


# def calcularDiccionarioSimilitud(self, listaHistorias, aplicarEn):
#     dicSimilitud = {}
#     n = len(listaHistorias)
#     for i in range(0, n-1):
#         for j in range((i+1), n):
#             historia = listaHistorias[i]
#             historia2 = listaHistorias[j]

#             texto1 = self.identificarVerbosEntidades(historia)
#             texto2 = self.identificarVerbosEntidades(historia2)

#             tex = texto1[1]
#             lem = texto1[2]

#             tex2 = texto2[1]
#             lem2 = texto2[2]

#             # tex = historia.nombre + ":" + historia.descripcion
#             # tex2 = historia2.nombre + ":" + historia2.descripcion

#             if aplicarEn == 'lemma':
#                 docl = self.n1p(lem)
#                 doc2 = self.n1p(lem2)
#             if aplicarEn == 'text':
#                 docl = self.n1p(tex)
#                 doc2 = self.n1p(tex2)

#             similitud = docl.similarity(doc2)
#             key = historia.identificador + '-' + historia2.identificador
#             dicSimilitud[key] = similitud

#             # print("---- Diccionario: , str(diccionario))
#             return dicSimilitud
