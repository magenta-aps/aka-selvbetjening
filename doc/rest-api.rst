
NB: Denne
Anvendelse af Django til REST-api.

Vi kræver CSRF-token for alle(?) endpoints.

Til en start kan man få et token fra serveren ved at lave en GET-request til et endpoint der har decoratoren
'ensure_csrf_cookie'.

Endpoints:
  inkassosag - GET, POST
  filupload - GET, POST 

POSTe til serveren:
  Hvis man submitter en form på almindelig vis, skal den indeholde CSRF-token i et hidden-field
  med navnet 'csrfmiddlewaretoken'

  Hvis man submitter fra Javascript (AJAX) skal man sætte en header med navnet X-CSRFTOKEN,
  som indeholder token.

  Jeg har både prøver med decorator på metode og på klasse, og er lige nu endt med at have denne på klassen:
  @method_decorator(ensure_csrf_cookie, name='dispatch')

Det er nemt at afprøve i Postman.
