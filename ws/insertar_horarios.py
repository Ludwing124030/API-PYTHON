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


if __name__ == '__main__':
    insert_horarios()