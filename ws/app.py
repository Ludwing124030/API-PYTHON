from flask import Flask, jsonify, make_response, request
import datetime as dt
from postgres import PostgresConnection
from psycopg2 import sql
import jwt
from auth_token_required import auth_token_required
from ExamenPDF import ExamenPDF
import yagmail
from flask_cors import CORS, cross_origin 

app = Flask(__name__)
app = Flask(__name__.split('.')[0])
CORS(app)

@app.route('/login', methods=['POST'])
#@cross_origin()
def login():
    """
        Ruta de login para especialista y secretaria. 
        Regresa el JWT. 
    """
    data = request.get_json()
    key = 'secret'
    jwt_user = {    "exp": dt.datetime.utcnow() + dt.timedelta(minutes=60),
                    "iat": dt.datetime.utcnow(),
                    "iss": "pladigpsico:web_service"
                }
    with PostgresConnection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                select usuario_id, email, especialista from usuario 
                where email = %(email)s 
                    and password = encode(digest(%(password)s, 'sha256'), 'hex');
            """, 
            {'email': data['usuario'], 'password': data['password']}
            )
            
            row = cursor.fetchone()
            if row is None:
                return make_response(jsonify({"Error": "usuario/password incorrectos"}), 401)
            else:
                jwt_user['usuario'] = { 
                    'usuarioID': row[0], 
                    'email': row[1],
                    'especialista': row[2]
                    }            
                response_body = {"JWT": jwt.encode(jwt_user, key, algorithm='HS256')}
                return jsonify(response_body)
                


@app.route('/especialista/usuario', methods=['GET', 'POST', 'PUT'])
@app.route('/especialista/usuario/<int:usuario_id>', methods=['DELETE'])
@auth_token_required(especialista=True)
def crud_usuario():
    if request.method == 'GET':
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                cur.execute('select usuario_id, email, especialista from usuario')
                rows = cur.fetchall()
                data = {'listaDeUsuarios': [{'usuarioID': row[0], 'email': row[1], 'especialista': row[2]} for row in rows]}
                return jsonify(data)
                    
    if request.method == 'POST':
        data = request.get_json()
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    insert into usuario 
                    values(default, %(email)s, encode(digest(%(password)s, 'sha256'), 'hex'), %(especialista)s)
                """
                , {'email': data['email'], 'password': data['password'], 'especialista': data['especialista']}
                )
                conn.commit()
                return jsonify({"message": "usuario creado exitosamente"})

    if request.method == 'PUT':
        data = request.get_json()
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                if data['campo'] == 'password':
                    cur.execute(sql.SQL("""
                    update usuario
                    set {campo} = encode(digest(%(nuevo_valor)s, 'sha256'), 'hex')                    
                    where usuario_id = %(usuario_id)s
                    """).format(campo=sql.Identifier(data['campo']))
                    ,{'nuevo_valor': data['nuevoValor'], 'usuario_id': data['usuarioID']}
                    )
                else:
                    cur.execute(sql.SQL("""
                        update usuario
                        set {campo} = %(nuevo_valor)s
                        where usuario_id = %(usuario_id)s
                    """).format(campo=sql.Identifier(data['campo']))
                    ,{'nuevo_valor': data['nuevoValor'], 'usuario_id': data['usuarioID']}
                    )
                conn.commit()
                return jsonify({"message": "usuario actualizado exitosamente"})

    if request.method == 'DELETE':
        # La especialista se podria borrar a ella misma :D
        usuario_id = request.view_args['usuario_id']
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    delete from usuario 
                    where usuario_id = %(usuario_id)s
                """, {'usuario_id': usuario_id}
                )
                conn.commit()
                return jsonify({"message": "usuario eliminado"})
                


@app.route('/secretaria/cita', methods=['PUT', 'GET'])
@auth_token_required(especialista=False)
def ru_cita():
    if request.method == 'GET':
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                # Testear porque se cambio h.fecha a la funcion para estandarizar el formato de fecha!
                cur.execute("""
                    select p.paciente_id, p.primer_nombre, p.segundo_nombre
                        , p.primer_apellido, p.segundo_apellido
                        , p.email, p.telefono
                        , h.horario_id , to_char(h.fecha::timestamp, 'dd-mm-yyyy hh24:mi:ss')
                        , c.comentario, c.estado_id
                    from cita as c
                    inner join paciente as p on c.paciente_id = p.paciente_id
                    inner join horario as h on c.horario_id = h.horario_id; 
                    """
                    )
                rows = cur.fetchall()
                citas = {'listaDeCitas': [{
                    'paciente': {
                        'pacienteID': d[0],
                        'primer_nombre': d[1],
                        'segundo_nombre': d[2],
                        'primer_apellido': d[3],
                        'segundo_apellido': d[4],
                        'email': d[5],
                        'telefono': d[6]
                    },
                    'horario': {
                        'horarioID': d[7],
                        'fecha': d[8]
                    },
                    'comentario': d[9],
                    'estadoID': d[10]
                } for d in rows]
                }
                return jsonify(citas)
    if request.method == 'PUT':
        data = request.get_json()
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql.SQL("""
                    update cita
                    set {campo} = %(nuevoValor)s
                    where horario_id = %(hid)s
                        and paciente_id = %(pid)s
                """).format(campo=sql.Identifier(data['campo']))
                , {'nuevoValor': data['nuevoValor'], 'hid': data['horarioID'], 'pid': data['pacienteID'] })
                
                if data['campo'] == 'estado_id':
                    disponible = None
                    if data['nuevoValor'] == 2 or data['nuevoValor'] == 3: 
                        # 2: cancela usuario, 3: la psicologa
                        if data['nuevoValor'] == 2:
                            disponible = True
                        elif data['nuevoValor'] == 3:
                            disponible = False

                        cur.execute(""" 
                            update horario
                            set disponible = %(disponible)s
                            where horario_id = %(horario_id)s
                        """
                        , {'horario_id': data['horarioID'], 'disponible': disponible}
                        )
                conn.commit()
                return jsonify({"message": "cita actualizada"})
                
                
@app.route('/especialista/examen', methods=['GET', 'POST', 'PUT'])
@app.route('/especialista/examen/<int:examen_id>', methods=['DELETE'])
@auth_token_required(especialista=True)
def crud_examen():
    """
        POST: Es ineficiente para insertar (200P * 5R = 1000 inserciones ~ 10segundos??)
            ademas que si falla una insercion o algo se truena toda la creacion del examen
            por lo que habria que empezar de nuevo... 
    """

    if request.method == 'GET':
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                
                cur.execute("""
                    select examen_id, titulo, to_char(fecha_creacion::timestamp, 'dd-mm-yyyy hh24:mi:ss'), codigo, habilitado
                    from examen
                """)

                
                examenes = cur.fetchall()
                print(cur.rowcount)
                lista_de_examenes = []
                print(examenes)
                for e in examenes: 
                    print("examenes len: ", len(examenes))
                    print("examen:", e[1])
                    eid = e[0]
                    build_examen = {}
                    build_examen['examen'] = { 
                        "examenID": eid,
                        "titulo": e[1],
                        "fecha_creacion": e[2],
                        "codigo": e[3],
                        "habilitado": e[4],
                        "preguntas": []
                        
                    }
                    
                    
                    cur.execute(""" 
                        select pregunta_id, pregunta
                        from pregunta
                        where examen_id = %(eid)s
                    """, {'eid': eid})

                    preguntas = cur.fetchall()
                    # print("preguntas: ")
                    # print(preguntas)
                    for p in preguntas:
                        pid = p[0]
                        cur.execute(""" 
                            select respuesta_id, respuesta, seleccion
                            from respuesta
                            where pregunta_id = %(pid)s
                                and examen_id = %(eid)s
                        """, {'eid': eid, 'pid': pid})

                        respuestas = cur.fetchall()
                    
                        build_examen['examen']['preguntas'].append({
                            "preguntaID": pid,
                            "pregunta": p[1],
                            "respuestas": [
                                {
                                    "respuestaID": r[0],
                                    "respuesta": r[1],
                                    "seleccion": r[2]
                                }
                                for r in respuestas
                            ]
                        })

                    lista_de_examenes.append(build_examen)
                   

                        
                print(len(lista_de_examenes))
                return jsonify({"listaDeExamenes": lista_de_examenes})

    if request.method == 'DELETE':
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                examen_id = request.view_args['examen_id']
                cur.execute(""" 
                    delete from examen
                    where examen_id = %(eid)s
                """
                , {'eid': examen_id}
                )
                conn.commit()
                return jsonify({"message": "examen eliminado exitosamente"})
                
    if request.method == 'PUT':
        data = request.get_json()
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql.SQL(""" 
                    update examen
                    set {campo} = %(nuevoValor)s
                    where examen_id = %(eid)s
                """).format(campo = sql.Identifier(data['campo']))
                , {'eid': data['examenID'], 'nuevoValor': data['nuevoValor']}
                )
                conn.commit()
                return jsonify({"message": "examen actualizado!"})

    # metodo obsoleto...
    if request.method == 'POST':
        data = request.get_json()
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                # cambiar fechaCreacion a NOW
                cur.execute(""" 
                    insert into examen
                    values(default, %(titulo)s, to_timestamp(%(fechaCreacion)s, 'dd-mm-yyyy hh24:mi:ss'), %(codigo)s, %(habilitado)s)
                """
                , {'titulo': data['examen']['titulo'], 'fechaCreacion': data['examen']['fechaCreacion'], 'codigo': data['examen']['codigo'], 'habilitado': data['examen']['habilitado']}
                )
                
                cur.execute("""
                    select examen_id 
                    from examen 
                    where codigo = %(codigo)s
                """
                , {'codigo': data['examen']['codigo']}
                )
    
                examen_id = cur.fetchone()

                # Should I just move data to for p in data[][preguntas]??
                preguntas = data['examen']['preguntas']

                # It's slow to do it this way but whatever... 
                # Tops 200 Questions * 5 answers each = 1000 inserts <= 10sec~ (Requires testing but later...)
                for p in preguntas:
                    cur.execute(""" 
                        insert into pregunta
                        values(%(pregunta_id)s, %(examen_id)s, %(pregunta)s)                    
                    """
                    , {'pregunta_id': p['preguntaID'], 'pregunta': p['pregunta'], 'examen_id': examen_id}
                    )

                    respuestas = p['respuestas']
                    for r in respuestas:
                        cur.execute(""" 
                            insert into respuesta
                            values(%(rid)s, %(pid)s, %(eid)s, %(respuesta)s, %(seleccion)s)
                        """
                        ,{'rid': r['respuestaID'], 'pid': p['preguntaID'], 'eid': examen_id, 
                            'respuesta': r['respuesta'], 'seleccion': r['seleccion']
                         }
                        )
         
                conn.commit()
                return jsonify({"message": "examen creado exitosamente"})


@app.route('/secretaria/paciente', methods=['GET', 'PUT'])
@auth_token_required(especialista=False)
def ru_paciente():
    """
        GET: Listar todos los pacientes.
        PUT: Actualizar un campo de un paciente.
    """
    if request.method == 'GET':
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    select paciente_id, primer_nombre, segundo_nombre
                        , primer_apellido, segundo_apellido
                        , email, telefono
                    from paciente
                """
                )

                pacientes = cur.fetchall()

                lista_de_pacientes = [{
                    "pacienteID": p[0],
                    "primer_nombre": p[1],
                    "segundo_nombre": p[2],
                    "primer_apellido": p[3],
                    "segundo_apellido": p[4],
                    "email": p[5],
                    "telefono": p[6]
                } for p in pacientes]

                return jsonify({"listaDePacientes": lista_de_pacientes})

    if request.method == 'PUT':
        data = request.get_json()
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql.SQL(""" 
                    update paciente
                    set {campo} = %(valor)s
                    where paciente_id = %(pid)s
                """).format(campo = sql.Identifier(data['campo']))
                , {'valor': data['nuevoValor'], 'pid': data['pacienteID']}
                )

                conn.commit()
                return jsonify({"message": "informacion del paciente actualizada!"})


@app.route('/paciente/cita', methods=['POST'])
def paciente_crea_cita():
    data = request.get_json()
    with PostgresConnection() as conn:
        with conn.cursor() as cur:
            # check if patient already exists
            cur.execute(""" 
                select paciente_id 
                from paciente 
                where email = %(email)s 
                """
                , {'email': data['paciente']['email']}
            )

            pid = cur.fetchone()

            if pid is None:
                # insert paciente if doesn't exist... 
                cur.execute(""" 
                    insert into paciente
                    values (default, %(n1)s, %(n2)s, %(a1)s, %(a2)s, %(email)s, %(tel)s )
                    returning paciente_id
                """
                ,   {
                        'n1': data['paciente']['primer_nombre'], 'n2': data['paciente']['segundo_nombre']
                        , 'a1': data['paciente']['primer_apellido'], 'a2': data['paciente']['segundo_apellido']
                        , 'email': data['paciente']['email'], 'tel': data['paciente']['telefono']
                    }
                )

                pid = cur.fetchone()
                conn.commit()

            cur.execute(""" 
                insert into cita
                values (%(pid)s, %(hid)s, 1, %(comentario)s)
            """
            , {'pid': pid[0], 'hid': data['horario']['horarioID'], 'comentario': data['comentario']}
            )

            cur.execute(""" 
                update horario
                set disponible = false
                where horario_id = %(hid)s
            """, {'hid': data['horario']['horarioID']})

            conn.commit()
            return jsonify(dict(message='cita agendada exitosamente!'))

@app.route('/paciente/horario', methods=['GET'])
def listar_horarios_disponibles():
    with PostgresConnection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                select horario_id, to_char(fecha::timestamp, 'dd-mm-yyyy hh24:mi:ss')
                from horario
                where disponible = true
            """)

            horarios = cur.fetchall()
            return jsonify({
                'listaDeHorarios': [{'horarioID': h[0], 'fecha': h[1]} for h in horarios]
            })

@app.route('/paciente/examen', methods=['GET', 'POST'])
def paciente_examenes():
    if request.method == 'GET':
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(""" 
                    select examen_id, titulo 
                    from examen
                """)

                examenes = cur.fetchall()

                return jsonify({
                    "listaDeExamenes": [{
                        "examenID": e[0],
                        "titulo": e[1]
                    } for e in examenes]
                })

    if request.method == 'POST':
        data = request.get_json()
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                # check if codigo equals examen.codigo
                cur.execute("""
                    select examen_id 
                    from examen
                    where codigo = %(codigo)s
                    and examen_id = %(eid)s
                 """, {'codigo': data['examen']['codigo'], 'eid': data['examen']['examenID']})

                eid = cur.fetchone()

                if eid is None: 
                    return make_response(dict(message='El codigo del examen es incorrecto'), 401)
                
                pdf = ExamenPDF('P', 'mm', 'Letter')
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()
                titulo = pdf.construir_examen_pdf(data)
                print(titulo)
                try: 

                    yag = yagmail.SMTP('juliasoharig@gmail.com', password='ingrese password o lea de config')
                    yag.send(to='juliasoharig@gmail.com', subject=titulo, contents="Envio Examen desde la API", attachments=titulo)
                    # se deberia borrar el examen despues de esto... 
                except Exception as err:
                    return make_response(dict(message="La licenciada no recibio el examen, vuelva a intentar en un rato"), 500)
                #codigo para enviar el pdf por email...

                return jsonify(dict(message="examen recibido correctamente"))
        pass

# Tiraba error con GET para /paciente/examen/{id} porque no se como 
# Flask maneja multiples URL para el mismo metodo HTTP. 
@app.route('/paciente/solicitar/examen', methods=['POST'])
def paciente_selecciona_examen():
    data = request.get_json()
    eid = data['examenID']
    with PostgresConnection() as conn:
        with conn.cursor() as cur:
            # el titulo ya lo tiene el front end.
            examen = {"examen": {"examenID": eid, "preguntas": []}}

            cur.execute(""" 
                select pregunta_id, pregunta
                from pregunta
                where examen_id = %(eid)s
            """, {'eid': eid})

            preguntas = cur.fetchall()
            
            for p in preguntas:
                cur.execute(""" 
                    select respuesta_id, respuesta, seleccion
                    from respuesta
                    where pregunta_id = %(pid)s
                """, {'pid': p[0]})
                
                respuestas = cur.fetchall()
                
                pregunta = {"preguntaID": p[0], "pregunta": p[1], "respuestas":  [{"respuestaID": r[0], "respuesta": r[1], "seleccion": r[2]} for r in respuestas] }
                examen['examen']['preguntas'].append(pregunta)
            
            return jsonify(examen)

@app.route('/especialista/examen/pregunta', methods=['POST', 'PUT', 'DELETE'])
@auth_token_required(especialista=True)
def cud_pregunta():
    if request.method == 'POST':
        data = request.get_json()
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(""" 
                    insert into pregunta
                    values(%(pid)s, %(eid)s, %(pregunta)s)
                """, {'pid': data['preguntaID'], 'eid': data['examenID'], 'pregunta': data['pregunta']})

                for r in data['respuestas']:
                    cur.execute(""" 
                        insert into respuesta
                        values(%(rid)s, %(pid)s, %(eid)s, %(respuesta)s, %(seleccion)s)
                    """
                    , {'pid': data['preguntaID'], 'eid': data['examenID'], 'rid': r['respuestaID'], 'respuesta': r['respuesta'], 'seleccion': r['seleccion']}
                    )
                
                conn.commit()
                
                return jsonify(dict(message="pregunta y respuestas creadas!"))
                
    
    if request.method == 'PUT':
        data = request.get_json()
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(""" 
                    update pregunta
                    set pregunta = %(pregunta)s
                    where pregunta_id = %(pid)s
                """
                , {'pid': data['preguntaID'], 'pregunta': data['pregunta'], 'eid': data['examenID'] }
                )

                conn.commit()
                return jsonify(dict(message="pregunta actualizada!"))

    if request.method == 'DELETE':
        data = request.get_json()
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(""" 
                    delete from pregunta
                    where pregunta_id = %(pid)s 
                    and examen_id = %(eid)s
                """, {'pid': data['preguntaID'],  'eid': data['examenID']})

                conn.commit()
                return jsonify(dict(message='pregunta y sus respuestas eliminda')) 
                
    
@app.route('/especialista/examen/respuesta', methods=['GET','POST', 'PUT', 'DELETE'])
@auth_token_required(especialista=True)
def crud_respuesta():
    if request.method == 'GET':
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(""" 
                    select examen_id, pregunta_id, respuesta_id, respuesta, seleccion
                    from respuesta
                """)
                
                respuestas = cur.fetchall()

                return jsonify({
                    "listaDeRespuestas": [{
                        "examenID": r[0],
                        "preguntaID": r[1],
                        "respuestaID": r[2],
                        "respuesta": r[3],
                        "seleccion": r[4]
                    } for r in respuestas]
                })


    if request.method == 'POST':
        data = request.get_json()
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(""" 
                    insert into respuesta
                    values(%(rid)s, %(pid)s, %(eid)s, %(respuesta)s, %(seleccion)s)
                """
                , {'pid': data['preguntaID'], 'eid': data['examenID'], 'rid': data['respuestaID'], 'respuesta': data['respuesta'], 'seleccion': data['seleccion']}
                )

                conn.commit()
                return jsonify(dict(message='respuesta creada!'))
        
    if request.method == 'PUT':
        data = request.get_json()
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql.SQL(""" 
                    update respuesta
                    set {campo} = %(valor)s
                    where respuesta_id = %(rid)s
                        and pregunta_id = %(pid)s
                        and examen_id = %(eid)s
                    
                """).format(campo = sql.Identifier(data['campo']))
                , {'pid': data['preguntaID'], 'eid': data['examenID'], 'rid': data['respuestaID'], 'valor': data['nuevoValor']}
                )

                conn.commit()
                return jsonify(dict(message='respuesta actualizada!'))

    if request.method == 'DELETE':
        data = request.get_json()
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(""" 
                    delete from respuesta
                    where respuesta_id = %(rid)s
                        and pregunta_id = %(pid)s
                        and examen_id = %(eid)s
                    
                """
                , {'pid': data['preguntaID'], 'eid': data['examenID'], 'rid': data['respuestaID']}
                )

                conn.commit()
                return jsonify(dict(message='respuesta eliminada!'))
                

@app.route('/especialista/new-cr/examen', methods=['GET', 'POST'])                    
@auth_token_required(especialista=True)
def new_cr_examen():
    """
        Nuevos metodos para el front end, dado el diseno del mismo
        es requerido utilizar un GET y POST del examen simplificado.
    """

    if request.method == 'GET':
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    select examen_id, titulo, 
                    to_char(fecha_creacion::timestamp, 'dd-mm-yyyy hh24:mi:ss'), 
                    codigo, habilitado
                    from examen
                """)

                examenes = cur.fetchall()

                return jsonify({
                    "listaDeExamenes": [{
                        "examenID": e[0],
                        "titulo": e[1],
                        "fecha_creacion": e[2],
                        "codigo": e[3],
                        "habilitado": e[4]
                    } for e in examenes]
                })
        
    if request.method == 'POST':
        data = request.get_json()
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(""" 
                    insert into examen 
                    values(default, %(titulo)s, now(), %(codigo)s, %(habilitado)s)
                """
                , {'titulo': data['titulo'], 'codigo': data['codigo'], 'habilitado': data['habilitado']}
                )

                conn.commit()

                cur.execute("""
                    select examen_id 
                    from examen 
                    where codigo = %(codigo)s
                """
                , {'codigo': data['codigo']}
                )
    
                examen_id = cur.fetchone()

                return jsonify({'message': "Examen creado exitosamente!\n Este es el codigo del examen: " + str(examen_id[0])})

    return None

@app.route('/especialista/new-cr/pregunta', methods=['GET', 'POST'])                    
@auth_token_required(especialista=True)
def new_cr_pregunta():
    """
        Se requiere un metodo GET y POST simplificado dadas
        las nuevas especificaciones del front end.
    """

    if request.method == 'GET':
        with PostgresConnection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    select examen_id, pregunta_id, pregunta  
                    from pregunta
                """)

                preguntas = cur.fetchall()

                return jsonify({
                    "listaDePreguntas": [{
                        "examenID": p[0],
                        "preguntaID": p[1],
                        "pregunta": p[2]
                    } for p in preguntas]
                })

    if request.method == 'POST':
            data = request.get_json()
            with PostgresConnection() as conn:
                with conn.cursor() as cur:
                    cur.execute(""" 
                        insert into pregunta 
                        values(%(pid)s, %(eid)s, %(pregunta)s)
                    """
                    , {'pid': data['preguntaID'], 'eid': data['examenID'], 'pregunta': data['pregunta']}
                    )

                    conn.commit()

                    return jsonify({'message': "Pregunta creado exitosamente!"})

    


if __name__ == '__main__':
    app.run(host='localhost', debug=True)