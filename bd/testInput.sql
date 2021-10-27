create extension pgcrypto;

select * from usuario ;

insert into usuario values(default, 'sobalvarro', encode(digest('sobalvarro', 'sha256'), 'hex'), true);
insert into usuario values(default, 'secretaria', encode(digest('secretaria', 'sha256'), 'hex'), false);

update usuario
set email = 'sobalvarro'
where usuario_id = 1;

delete from usuario where usuario_id = 1;

select usuario_id , email, especialista from usuario 
where email = 'sobalvarro'
	and password = encode(digest('sobalvarro', 'sha256'), 'hex');

select * from usuario;

insert into horario values(default, to_timestamp('25-08-2021 12:21:00', 'dd-mm-yyyy hh24:mi:ss'), true);
insert into horario values(default, to_timestamp('28-08-2021 14:00:00', 'dd-mm-yyyy hh24:mi:ss'), true) returning horario_id;

select to_char(fecha::timestamp, 'dd-mm-yyyy hh24:mi:ss') from horario;

select * from horario;
truncate table horario cascade;


select * from cita;
select * from horario;

/*
Estado:
	1 confirmada por el usuario
	2 cancelado por el usuario
	3 cancelado por la lic no se haga disponible el horario
	4. finalizada
	5. el paciente se ausento
*/

insert into estado values (1, 'confirmada por el usuario');
insert into estado values (2, 'cancelado por el usuario');
insert into estado values (3, 'cancelado por la lic');
insert into estado values (4, 'finalizada');
insert into estado values (5, 'el paciente se ausento');

select * from cita;

select * from horario where horario_id > 425 and horario_id  < 430 and disponible = false;

/*RU Citas*/

insert into paciente values(default, 'mario', 'rene', 'estrada', 'sobalvarro'
	, 'marito@andreas.com', 12344321
);

insert into paciente values(default, 'andrea', 'rana', 'guerra', 'de estrada', 'andreas@marito.com', 75664131);

select * from paciente p ;

select * from cita;

select now(); 

insert into cita values (1, 2, 1, 'soy tajante'); 

select p.paciente_id, p.primer_nombre, p.segundo_nombre, p.primer_apellido, p.segundo_apellido, p.email, p.telefono
	, h.horario_id , h.fecha
	, c.comentario , c.estado_id
from cita as c
inner join paciente as p on c.paciente_id = p.paciente_id
inner join horario as h on c.horario_id = h.horario_id; 


/*
 * Examenes
 * 
 * 
*/

select * from examen e ;

insert into examen values(default, 'examenZERO', '2020-01-22 11:22:22', 3939, true);
insert into examen values(default, 'Un Examen bonito', '2021-02-23 22:33:44', 9494, false);

select * from pregunta p ;

insert into pregunta values(10,7, 'vale la pena vivir?');
insert into pregunta values(2,1, 'es mejor un gato o un perro?');

insert into pregunta values(1,2, 'tener hijos en pobreza es buena idea?');
insert into pregunta values(2,2, 'realmente queremos tener pareja sexual o es influencia de la sociedad?');

select * from respuesta r ;

insert into respuesta values(1,1,2, 'Lo es para que nos mantengan en el futuro', true);
insert into respuesta values(2,1,2, 'Sin importar el estatus asi lo manda la naturaleza', true);
insert into respuesta values(1,2,2, 'Es un deseo natural', true);
insert into respuesta values(2,2,2, 'Los fetiches los induce la sociedad', true);


insert into respuesta values(1,1,1, 'no lo vale', true);
insert into respuesta values(2,1,1, 'pueda ser que valga la pena', true);
insert into respuesta values(1,2,1, 'gato', true);

select examen_id, titulo, fecha_creacion, codigo, habilitado
                    from examen;
insert into respuesta values(2,2,1, 'perro', true);

update examen
set codigo = 111
where examen_id = 2;

select * from examen e ;

select * from pregunta;

select * from respuesta where pregunta_id  = 2;




