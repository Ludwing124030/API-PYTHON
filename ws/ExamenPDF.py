from fpdf import FPDF
import datetime as dt

class ExamenPDF(FPDF):
    def header(self):
        self.set_font('times', 'B', 20)        
        self.cell(w=0, txt='CLINICA PSICOLOGICA LICDA SOBALVARRO', border=False, ln=1, align='C')
        self.ln(10)
    
    def informacion_examen(self, ie_titulo, ie_body):
        self.set_font('times', 'B', 14)
        self.cell(txt=ie_titulo, ln=0)
        self.set_font('times', '', 16)
        self.cell(txt=ie_body, ln=1)
        self.ln(h=3)
        
    def pregunta(self, pregunta):
        self.ln(h=10)
        self.cell(w=15, ln=0)
        self.set_font('times', 'B', 18)
        self.cell(txt=pregunta, ln=1)
        self.ln(h=5)
    
    def respuesta(self, respuesta, seleccionada=False):
        bala = 'BI' if seleccionada else ''
        self.ln(h=5)
        self.cell(w=30, ln=0)
        self.set_font('times', bala, 14)
        # self.cell(txt=bala, ln=0)
        self.multi_cell(txt=respuesta, align='J', w=125)
    
    def construir_examen_pdf(self, data):
        paciente_nombre = data['paciente']['primer_nombre'] + ' ' + data['paciente']['segundo_nombre'] + ' ' + data['paciente']['primer_apellido'] + ' ' + data['paciente']['segundo_apellido']
        self.informacion_examen('Paciente: ', paciente_nombre)
        self.informacion_examen('Prueba Aplicada: ', data['examen']['titulo'])
        self.informacion_examen('Fecha: ', str(dt.datetime.now()))
        self.ln(h=5)

        for p in data['examen']['preguntas']:
            self.pregunta(str(p['preguntaID']) + ' ' + p['pregunta'])
            for r in p['respuestas']:
                self.respuesta(str(r['respuestaID']) + ' ' + r['respuesta'], r['respuestaDeUsuario'])

        titulo = data['paciente']['primer_nombre'] + '_' + data['paciente']['segundo_nombre'] + '_' + data['examen']['titulo'] + '.pdf'
        self.output(titulo)
        return titulo
