create table usuario (
	usuario_id serial primary key,
	email text unique not null,
	password text not null, --insert with sha256 no need for a trigger.
	especialista boolean not null  
);

create table examen(
	examen_id serial primary key,
	titulo text not null,
	fecha_creacion timestamp not null,
	codigo int unique not null,
	habilitado boolean not null
	
);

create table paciente(
	paciente_id serial primary key,
	primer_nombre text not null,
	segundo_nombre text not null,
	primer_apellido text not null,
	segundo_apellido text not null,
	email text unique not null,
	telefono int not null	
);

create table horario(
	horario_id serial primary key,
	fecha timestamp unique not null,
	disponible boolean not null
);

/*
Estado:
	1 confirmada por el usuario
	2 cancelado por el usuario
	3 cancelado por la lic no se haga disponible el horario
	4. finalizada
	5. el paciente se ausento
*/

create table estado(
	estado_id int primary key,
	descripcion text not null
);

create table cita(
	paciente_id int, 
	horario_id int, 
	estado_id int,
	comentario text
);

alter table cita
add constraint cita_pk
primary key(paciente_id, horario_id, estado_id);

alter table cita 
add constraint fkcita_paciente
foreign key(paciente_id) 
references paciente(paciente_id);

alter table cita
add constraint fkcita_horario
foreign key(horario_id)
references horario(horario_id)
on delete cascade;

alter table cita 
add constraint fkcita_estado
foreign key(estado_id)
references estado(estado_id)
on delete cascade;

create table pregunta(
	pregunta_id int,
	examen_id int,
	pregunta text not null
);

alter table pregunta
add constraint pregunta_pk
primary key(pregunta_id, examen_id);

alter table pregunta 
add constraint fkpregunta_examen
foreign key(examen_id)
references examen(examen_id)
on delete cascade;

create table respuesta(
	respuesta_id int,
	pregunta_id int,
	examen_id int,
	respuesta text not null,
	seleccion boolean not null
);

alter table respuesta
add constraint respuesta_pk
primary key(respuesta_id, pregunta_id, examen_id);

alter table respuesta
add constraint fkrespuesta_pregunta
foreign key(pregunta_id, examen_id)
references pregunta(pregunta_id, examen_id)
on delete cascade;

--drop table respuesta;
--drop table pregunta;
--drop table examen cascade;
--drop table usuario;
--drop table cita;
--drop table estado cascade;
--drop table horario cascade;
--drop table paciente cascade;


