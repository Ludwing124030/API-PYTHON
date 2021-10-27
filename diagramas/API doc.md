# PladigPsico API

- Los horarios son de dos horas de 7am a 5pm. 
- Hay dos tipos de usuarios: especialistas y no especialistas. Los no especialistas unicamente pueden ver y actualizar las citas. Los especialistas pueden hacer CRUD a usuarios y examenes (preguntas y respuestas).

## LOGIN

``` @pladigpsico/login ```

### _POST_
```
{
    "email": "sobalvarro@gmail.com",
    "password": "sobalvarro",
    "especialista": true
}
```
#### Respuesta

> JWT && OK
> ERROR : email/password no coinciden u otro error. 

## Examenes

``` @pladigpsico/especialista/examen ```

### _POST_

```
{
  "examen": {
  	"examenID": 1,
	"titulo": "examen01",
    "codigo": 1222,
    "habilitado": "True"
   },  
   "preguntas": [
	  { "preguntaID": 1, "pregunta": "vale la pena vivir?" },
	  { "preguntaID": 2,"pregunta": "vale la pena vivir?" }
    ],
   "respuestas": [
   		{ "respuestaID": 1, "respuesta": "no" },
      	{ "respuestaID": 1, "respuesta": "si" }
	]
}
```

### _UPDATE Examen:_ 

```
{
    "examen_id": 1,
	"campo": "titulo",
	"valor": "pokemones 101"
}
```

Si es una pregunta la que se va actualizar
``` PATCH@pladigpsico/especialista/examen/pregunta ```
```
{
    "examen_id": 1,
    "pregunta_id": 1,
    "pregunta": "somos realmente libres?"
}
```
Si es una respuesta:
``` PATCH@pladigpsico/especialista/examen/respuesta ```
```
{
    "examen_id": 1,
    "pregunta_id": 1,
    "respuesta_id": 1,
    "respuesta": "no somos libres...",
    "seleccion": false
}
```

### _DELETE Preguntas:_
``` DELETE@pladigpsico/especialista/examen/pregunta ```
```
{
	examen_id: int
	preguntas: [id: int, ...]
}
```

### _DELETE Respuestas:_
``` DELETE@pladigpsico/especialista/examen/respuesta ```
```
{
	examen_id: int,
	pregunta_id: int,
	respuestas: [id: int, ...]
}
```

### _DELETE Examen:_
``` DELETE@pladigpsico/especialista/examen ```
```{ examen_id: 1 }```

### _GET Examen:_
``` GET@pladigpsico/especialista/examen ```
```{ examen_id: 1 }```


## CITAS:

### _GET:_
Envian todas y en el front end se filtran.
``` GET@pladigpsico/secretaria/cita ```
```
{
	citas: 
    		[ { cita_id, usuario_id, nombres, apellidos, telefono, email, horario, comentario }, ...]
			[
				{ cita: 
}
```

### _UPDATE:_ 

No se borra la cita per se solo se actualiza su estado y dependiendo de este el horario estara disponible o no.
``` PATCH@pladigpsico/secretaria/cita ```
```
{
	cita_id: int,
	estado_id: int
}
```
2. paciente cancelo la cita
3. la psicologa no estara disponible (el horario no estara disponible)

## USUARIOS:

Todos los metodos requieren JWT que sea de especialista
``` POST|GET|PATCH|DELETE@pladigpsico/especialista/usuario ```
### _POST_:
```
{
	"usuario": "nuevo usuario",
	"password": "nuevo usuario",
	"especialista": 0
}
```
	
### _GET_:
	usuarios: [{usuario_id, usuario, especialista}, ...]

### _UPDATE:_
```
{
    "usuario_id": 1,
    "campo": "password",
    "valor": "nuevaPass"
}
```

### _DELETE:_
```
{
    "usuario_id": 1
}
```

## PACIENTE selecciona examen

``` GET|POST@pladigpsico/paciente/examen ```

### _GET:_

```{ examenes: [ {examen_id, titulo}, ... ] }```

 ### _POST:_ 

```{examen_id: 1}```

#### Respuesta: 

Si preguntaX: [] quiere decir que la respuesta es para que el usuario la redacte.

```
{
	examen_id: int, 
	preguntas: {
		preguntaX: [respuestas], ...
	}
}
```

## PACIENTE envia el examen resuelto
``` POST@pladigpsico/paciente/examen/respondido ```
### _POST_:

El codigo es el asignado a la prueba y las respuestas son las respuestas per se que selecciono el paciente (no el id) o redacto el mismo, esto quiere decir que la respuesta_1 es la respuesta a la pregunta_1 por lo que al momento de armar el PDF se utilizara dicha respuesta.  

```
{
    "examen_id": 1,
    "email": "paciente0@paciente.com",
    "codigo": 666,
    "preguntas": {
        "pregunta_1": "vale la pena vivir?"
    },
    "respuestas": {
        "respuesta_1": "no vale la pena"
    }
}
```

Con respecto al PDF que se planea armar, del email se obtendran los datos del paciente de la BD para integrarlos a este JSON y con estos nuevos datos generar el PDF.

#### Respuesta:

> OK o ERROR (con su codigo correspondiente)

## PACIENTE CREA CITA
``` GET|POST@pladigpsico/paciente/cita ```
### _GET:_

lista de horarios (id, timestamp: YYYY-MM-DD HH:MM:SS, disponible: si)

### _POST:_

```
{
    "primer_nombre": "mario",
    "segundo_nombre": "rene",
    "primer_apellido": "estrada",
    "segndo_apellido": "sobalvarro",
    "email": "paciente0@pacientes.com",
    "telefono": 12344321,
    "horario_id": 1,
    "comentario": "soy tajante y tengan una mascarilla porque se me olvida llevar una"
}
```

#### Respuesta:

> OK o ERROR (con su codigo correspondiente)
