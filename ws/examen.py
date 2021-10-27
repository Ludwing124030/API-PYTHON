# lista_de_examenes = {"listaDeExamenes": [{
#     "examen": {
#         "id": 1,
#         "preguntas": [{
#             "pid": 1,
#             "pregunta": "vale la pena vivir",
#             "respuestas": [{
#                 "rid": 1,
#                 "respuesta": "no"
#             }]
#         }]
#     }
#     }
# ]}

# # print(lista_de_examenes["listaDeExamenes"][0]["examen"]["preguntas"][0]["respuestas"][0])

# import datetime as dt
# import jwt
# print(dt.datetime.now() + dt.timedelta(minutes=60))

# key = 'secret'
# jwt_user = {    "exp": dt.datetime.utcnow() + dt.timedelta(minutes=60),
#                 "iat": dt.datetime.utcnow(),
#                 "iss": "pladigpsico:web_service"
#             }

# encode = jwt.encode(jwt_user, key, algorithm='HS256')


# decoded = jwt.decode(encode, key, algorithms='HS256')

# print(dt.datetime.utcnow().timestamp())

from io import BytesIO
from re import sub
from pdfdocument.document import PDFDocument

import json


def createPDF():
    with open('examenResuelto.json',) as f:
        data = json.load(f)

    f = BytesIO()
    pdf = PDFDocument(f)
    
    pdf.init_report()
    pdf.generate_style(font_name='Arial', font_size=20)
    
    pdf.h1('CLINICA PSICOLOGICA LICDA SOBALVARRO')
    
    
    paciente = data['paciente']['primer_nombre'] + ' ' + data['paciente']['primer_apellido']
    pdf.p('Paciente: ', style=pdf.style.bold)
    pdf.p(paciente)
    pdf.p(data['examen']['titulo'])

    pdf.generate()
    with open('test.pdf', 'wb') as outfile:
        outfile.write(f.getvalue())


from fpdf import FPDF
import datetime as dt

class ExamenPDF(FPDF):
    def header(self):
        self.set_font('times', 'B', 20)        
        self.cell(w=0, txt='CLINICA PSICOLOGICA LICDA SOBALVARRO', border=False, ln=1, align='C')
        self.ln(10)
    
    def informacion_examen(self, ie_titulo, ie_body):
        pdf.set_font('times', 'B', 14)
        pdf.cell(txt=ie_titulo, ln=0)
        pdf.set_font('times', '', 16)
        pdf.cell(txt=ie_body, ln=1)
        pdf.ln(h=3)
        
    def pregunta(self, pregunta):
        pdf.ln(h=10)
        pdf.cell(w=15, ln=0)
        pdf.set_font('times', 'B', 18)
        pdf.cell(txt=pregunta, ln=1)
        pdf.ln(h=5)
    
    def respuesta(self, respuesta, seleccionada=False):
        bala = 'BI' if seleccionada else ''
        pdf.ln(h=5)
        pdf.cell(w=30, ln=0)
        pdf.set_font('times', bala, 14)
        # pdf.cell(txt=bala, ln=0)
        pdf.cell(txt=respuesta, ln=1)
    
    def examen_pdf(self, data):
        paciente_nombre = data['paciente']['primer_nombre'] + ' ' + data['paciente']['segundo_nombre'] + ' ' + data['paciente']['primer_apellido'] + ' ' + data['paciente']['segundo_apellido']
        pdf.informacion_examen('Paciente: ', paciente_nombre)
        pdf.informacion_examen('Prueba Aplicada: ', data['examen']['titulo'])
        pdf.informacion_examen('Fecha: ', str(dt.datetime.now()))
        pdf.ln(h=5)

        for p in data['examen']['preguntas']:
            pdf.pregunta(str(p['preguntaID']) + ' ' + p['pregunta'])
            for r in p['respuestas']:
                pdf.respuesta(str(r['respuestaID']) + ' ' + r['respuesta'], r['respuestaDeUsuario'])


        
# pdf = ExamenPDF('P', 'mm', 'Letter')
# pdf.set_auto_page_break(auto=True, margin=15)
# pdf.add_page()

# pdf.informacion_examen('Paciente: ', 'Mario Estrada')
# pdf.informacion_examen('Prueba Aplicada: ', 'ExamenZERO')
# pdf.informacion_examen('Fecha: ', str(dt.datetime.now()))
# pdf.ln(h=15)
# pdf.pregunta('1. Vale la pena vivir?')
# pdf.respuesta('Si vale la pena')
# pdf.respuesta('No lo vale por lo miserable que es el hombre', seleccionada=True)

# with open('examenResuelto.json',) as f:
#         data = json.load(f)

# pdf.examen_pdf(data)

#ever hear of pretty format?
# paciente_nombre = data['paciente']['primer_nombre'] + ' ' + data['paciente']['segundo_nombre'] + ' ' + data['paciente']['primer_apellido'] + ' ' + data['paciente']['segundo_apellido']
# pdf.informacion_examen('Paciente: ', paciente_nombre)
# pdf.informacion_examen('Prueba Aplicada: ', data['examen']['titulo'])
# pdf.informacion_examen('Fecha: ', str(dt.datetime.now()))
# pdf.ln(h=15)

# for p in data['examen']['preguntas']:
#     pdf.pregunta(str(p['preguntaID']) + ' ' + p['pregunta'])
#     for r in p['respuestas']:
#         pdf.respuesta(str(r['respuestaID']) + ' ' + r['respuesta'], r['respuestaDeUsuario'])


# pdf.output('test.pdf')


# import yagmail

# try: 

#     yag = yagmail.SMTP('juliasoharig@gmail.com', password='')
#     yag.send(to='juliasoharig@gmail.com', subject="PruebaZERO", contents="Hola GMAIL", attachments="test.pdf")

# except Exception as err:
#     print("Error, email was not sent")
#     print(err)



d = 'default' # it shouldnt be with ''
timestamp = None
habilitado = True # all are available...

"""
    Code logic resides on timestamp as it needs:
        > each cita is 2 hours. 
        > starts each day from 8-12, !12-14, 14-18
        > skips weekends
        > start from september until december. 
"""


def insert_horarios():
    dates = {
        '09': ['01','02','03','06','07','08','09','10','13','14','16','17','20','21','22','23','24','27','28','29','30'],
        '10': ['01','04','05','06','07','08','11','12','13','14','15','18','19','20','21','22','25','26','27','28','29'],
        '11': ['02','03','04','05','08','09','10','11','12','15','16','17','18','19','22','23','24','25','26','29','30'],
        '12': ['01','02','03','06','07','08','09','10','13','14','15','16','17','20','21','22','23','27','28','29','30',]
    }

    fechas = []

    for mes in dates:
        anio = '-' + mes + '-2021 ' # '2021-' + mes + '-' 
        for day in dates[mes]:
            for hour in range(8,20, 2):
                if hour == 12: 
                    continue
                hora = str(hour) + ':00:00'
                fechas.append(day + anio + hora)


    from postgres import PostgresConnection 

    with PostgresConnection() as conn:
        for f in fechas:
            with conn.cursor() as cur:
                cur.execute(""" 
                    insert into horario
                    values(default, to_timestamp(%(f)s, 'dd-mm-yyyy hh24:mi:ss'), true)
                """, {'f': f})
            
            conn.commit()
            print("Se han insertado todos los horarios exitosamente!")


insert_horarios()