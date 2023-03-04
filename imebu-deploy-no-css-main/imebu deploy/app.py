from flask import Flask, render_template, request, redirect, url_for, flash, session, app, make_response
from flask_mysqldb import MySQL
from datetime import datetime, date, time,timedelta
import hashlib

app = Flask(__name__)

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'empleo'


#ahora vamos a inicializar una sesion es decir datos que guarda nuestro servidor para luego poder reutilizarlos
#en este caso lo vamos a guardar dentro de la memoria de la aplicacion
#con secret_key le decimos como va a ir protegida nuestra sesion
app.secret_key = 'qwerty9230'

mysql = MySQL(app)
#cada vez que un usuario entre a nuestra ruta principal vamos a devolverle algo es esta linea:

def encrypt(session):
    h = hashlib.sha512()
    keys=session.keys()
    if 'rol' in keys and 'tipoDoc' in keys and 'docIdent' in keys and 'nombre' in keys and len(keys)==4:
        s=session['rol']+session['tipoDoc']+session['docIdent']+session['nombre']
        h.update(s.encode('utf-8'))
        return h.hexdigest()
    else:
        return False

def check(id,session):
    hs=encrypt(session)
    if hs:
        return id==hs
    else:
        return False

def checkExiste(consultas):
    check=True
    enters=False
    for con in consultas:
        enters=True
        check = check and con
    return bool(check and enters)





############################ FUNCIONES DE LOGIN Y REGISTRO
#funcion para el registro principal ya
@app.route('/registro', methods=['GET','POST'])
def FormPersonaGeneral():
    if request.method == 'GET':
        if session:
            if 'Usertype' in session:
                Usertype = session['Usertype']
            if 'Nombre' in session:
                Nombre = session['Nombre']
            flash('Ya iniciaste sesion')
            return render_template('main-dashboard.html', session = Usertype, session2 = Nombre)
        else:
            #tipo documento
            cur1 = mysql.connection.cursor()
            cur1.execute('SELECT * FROM tipodoc')
            documentos = cur1.fetchall()
            cur2 = mysql.connection.cursor()
            cur2.execute('SELECT * FROM genero')
            generos = cur2.fetchall()
            cur3 = mysql.connection.cursor()
            cur3.execute('SELECT * FROM etnia')
            etnias = cur3.fetchall()
            cur4 = mysql.connection.cursor()
            cur4.execute('SELECT * FROM vulnerabilidades')
            vulnerabilidades = cur4.fetchall()
            cur5 = mysql.connection.cursor()
            cur5.execute('SELECT * FROM barrios')
            barrios = cur5.fetchall()
            cur6 = mysql.connection.cursor()
            cur6.execute('SELECT * FROM estadocivil')
            estciviles = cur6.fetchall()
            cur8 = mysql.connection.cursor()
            cur8.execute("""SELECT u.usuario,pg.nombre1,pg.nombre2,pg.apellido1,pg.apellido2 FROM usuarios u
                         LEFT JOIN personageneral pg ON pg.usuario=u.usuario WHERE rol='Administrador'""")
            funcionarios = cur8.fetchall()
            cur9 = mysql.connection.cursor()
            cur9.execute("""
            SELECT PAIS_NAC FROM nacionalidad
            """)
            nacionalidades=cur9.fetchall()

            #datos personales
            return render_template('form-registro.html',documentos=documentos,generos=generos,etnias=etnias,vulnerabilidades=vulnerabilidades,barrios=barrios,estciviles=estciviles,funcionarios=funcionarios,nacionalidades=nacionalidades)

    if request.method == 'POST':
        if session:
            if 'Usertype' in session:
                Usertype = session['Usertype']
            if 'Nombre' in session:
                Nombre = session['Nombre']
            flash('Ya iniciaste sesion')
            return render_template('main-dashboard.html', session = Usertype, session2 = Nombre)
        else:
            #datos 
            primernombre = request.form['primer-nom']
            segundonombre = request.form['segundo-nom']
            primerapellido = request.form['primer-ape']
            segundoapellido = request.form['segundo-ape']
            tipodocumento = request.form['tipodocumento']
            numerodocumento = request.form['numdocumento']
            fechanacimiento = request.form['fechanacimiento']
            genero = request.form['genero']
            correoelectronico = request.form['correoelectronico']
            telefonofijo = request.form['telefijo']
            telefonocel = request.form['telecel']
            etnia = request.form['etnia']
            vulnerabilidad = request.form['vulnerabilidad']
            nacionalidad = request.form['nacionalidad']
            barrio = request.form['barrio']
            direccion = request.form['direccion']
            estadocivil = request.form['estadocivil']
            funcionario = request.form['funcionario']
            usuario = request.form['usuario']
            passuser = request.form['passuser']
            #datos direccion
            """nomenclatura = request.form['nomenclatura']
            numeroNombre = request.form['numeroNombre']
            letra1 = request.form['letra1']
            numero2 = request.form['numero2']
            letra2 = request.form['letra2']
            numero3 = request.form['numero3']
            letra3 = request.form['letra3']
            complemento = request.form['complemento']
            descripciones = request.form['descripciones']"""
            barrio = request.form['barrio']
            #conexion y guardado
            cur1 = mysql.connection.cursor()
            cur2 = mysql.connection.cursor()
            cur3 = mysql.connection.cursor()  # obtenemos conexion
            sql1=f"""
            INSERT INTO usuarios (usuario,contraseña)
            VALUE ('{usuario}',UNHEX(SHA2('{passuser}',256)));"""
            sql2=f"""INSERT INTO personageneral (docIdent, tipoDoc, nombre1, nombre2, apellido1, apellido2,celular,telefono,email,fechaNacimiento,nacionalidad,usuario,genero,etnia,estadoCivil,aceptaTerminos)
            VALUES ('{numerodocumento}', '{tipodocumento}', '{primernombre}', '{segundonombre}', '{primerapellido}', '{segundoapellido}','{telefonocel}','{telefonofijo}','{correoelectronico}','{fechanacimiento}','{nacionalidad}','{usuario}','{genero}','{etnia}','{estadocivil}',1);"""
            sql3=f"""INSERT INTO direccionpersona(docIdent,tipoDoc,nombreBarrio,direccionCompleta)
            VALUES('{numerodocumento}', '{tipodocumento}','{barrio}','{direccion}')
            """
            cur1.execute(sql1)
            cur2.execute(sql2)
            cur3.execute(sql3)  # escrbimos la consulta
            mysql.connection.commit()
            flash('Tu cuenta ha sido creada satisfactoriamente, ingresa con tu usuario y contraseña')
            return redirect(url_for('login'))  # nombre de la ruta

#funcion para login ya
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        if session:
            if 'rol' in session:
                rol=session['rol']
                tipoDoc=session['tipoDoc']
                docIdent=session['docIdent']
                nombre=session['nombre']
            flash('Ya iniciaste sesion')
            return redirect(url_for('Index'))
        else:
            return render_template('login.html')
            
    if request.method == 'POST':
        if session:
            if 'rol' in session:
                rol=session['rol']
                tipoDoc=session['tipoDoc']
                docIdent=session['docIdent']
                nombre=session['nombre']
            flash('Ya iniciaste sesion')
            return render_template('main-dashboard.html', rol = rol, tipoDoc = tipoDoc, docIdent=docIdent,nombre=nombre)
        else:
            nomusuario = request.form['usu-user']
            usuariopass = request.form['usu-pass']
            cur = mysql.connection.cursor()
            sql=f"""
            SELECT u.rol,pg.tipoDoc,pg.docIdent,pg.nombre1 FROM usuarios u
            LEFT JOIN personageneral pg ON pg.usuario=u.usuario
            WHERE u.usuario='{nomusuario}' AND u.contraseña=UNHEX(SHA2('{usuariopass}',256))  
            """
            cur.execute(sql)
            data = cur.fetchall()
            if len(data)>0:
                data=data[0]            
                session['rol'] = data[0]
                session['tipoDoc'] = data[1]
                session['docIdent'] = data[2]
                session['nombre'] = data[3]
                return render_template('main-dashboard.html')
            else:
                flash('usuario o contraseña incorrectos')
                return render_template('login.html')

############################ FUNCIONES DE MAIN PAGE
#dashboard principal ya
@app.route('/')
def Index():
    if session:
        if 'rol' in session:
            rol=session['rol']
            tipoDoc=session['tipoDoc']
            docIdent=session['docIdent']
            nombre=session['nombre']
        flash('Ya iniciaste sesion')
        return render_template('main-dashboard.html', rol = rol, tipoDoc = tipoDoc, docIdent=docIdent,nombre=nombre)
    else:
        flash('inicia sesion para poder continuar')
        return render_template('login.html')

############################ FUNCIONES DE EMPLEO
#funciones para empleo general ya
@app.route('/hoja-de-vida')
def MainHV():
    if session:
        if 'rol' in session:
            rol=session['rol']
            tipoDoc=session['tipoDoc']
            docIdent=session['docIdent']
            nombre=session['nombre']
        return render_template('main-hv.html')
    else:
        flash('inicia sesion para poder continuar')
        return render_template('login.html')

########## FUNCIONES DE FORMULARIOS POSTULADOS GENERAL
#funciones para postulados generales a empleo ya
@app.route('/postulados-empleo', methods=['GET','POST'])
def FormPersonaPostulados():
    if request.method == 'GET':
        if session:
            if 'rol' in session:
                rol=session['rol']
                tipoDoc=session['tipoDoc']
                docIdent=session['docIdent']
                nombre=session['nombre']
                cur1 = mysql.connection.cursor()
                cur1.execute('SELECT * FROM tipoempleado')
                tipoempleado = cur1.fetchall()
                cur2 = mysql.connection.cursor()
                cur2.execute('SELECT * FROM programagobiernoempleo')
                programasgobierno = cur2.fetchall()
                cur3 = mysql.connection.cursor()
                cur3.execute(f"""SELECT COUNT(*) FROM postulado WHERE docIdent='{session['docIdent']}' AND tipoDoc='{session['tipoDoc']}'""")
                existe = cur3.fetchall()[0][0]
                idPostulado=encrypt(session)
                if not existe:
                    return render_template('form-postulados.html', tipoempleados=tipoempleado,programasgobierno=programasgobierno,existe=existe)
                else:
                    cur4=mysql.connection.cursor()
                    cur4.execute(f"""
                    SELECT tieneLibretaMilitar,tipoEmpleado,minRangoSalarial,resumenPerfil FROM postulado WHERE docIdent='{docIdent}' AND tipoDoc='{tipoDoc}'
                    """)
                    data=cur4.fetchall()
                    cur5=mysql.connection.cursor()
                    cur5.execute(f"""
                    SELECT programaGobiernoEmpleo FROM programasgovpostulado WHERE docIdent='{docIdent}' AND tipoDoc='{tipoDoc}'
                    """)
                    data2=cur5.fetchall()
                    t=checkExiste([data,data2,existe])
                    if t:
                        return render_template('form-postulados.html',data=data,programasgobierno=data2,existe=existe,idPostulado=idPostulado)
                    else:
                        flash('error de la base de datos, pongase en contacto con el admin')
                        return render_template('main-hv.html',existe=existe)
            else:
                print('wtf')
                flash('inicia sesion para poder continuar')
                return render_template('login.html')
            
        else:
            flash('inicia sesion para continuar')
            return render_template('login.html')

    if request.method == 'POST':
        k=check(id, session)
        if k:
            if session:
                if 'rol' in session:
                    rol=session['rol']
                    tipoDoc=session['tipoDoc']
                    docIdent=session['docIdent']
                    nombre=session['nombre']
                    #comprobar con sql primero si no tiene mas de un registro
                    #datos generales postulado
                    ahora = datetime.now()
                    docident = session['docIdent']
                    tipo_doc = session['tipoDoc']
                    libretamil = request.form['libretamil']
                    tipoempleado = request.form['estadolaboral']
                    programagobierno = request.form['programasgobierno']
                    minrangosalarial = request.form['minrangosalarial']
                    perfillaboral = request.form['perfillaboral']
                    aceptaterminos = 'SI'
                    estadopostulado = 'ACTTIVO'
                    fecha_actual = date(ahora.year, ahora.month, ahora.day)
                    fecharegistro = fecha_actual
                    hora_actual = time(ahora.hour, ahora.minute, ahora.second)
                    horaregistro = hora_actual
                    if request.form.get('check')=='on':
                        #conexion y guardado
                        cur1 = mysql.connection.cursor()  # obtenemos conexion
                        sql1 = f"""
                        INSERT INTO postulado (docIdent,tipoDoc,TieneLibretaMilitar,minRangoSalarial,resumenPerfil,tipoEmpleado,estadoPostulado,aceptaTerminos)
                        VALUES('{docident}','{tipo_doc}',{libretamil},{minrangosalarial},'{perfillaboral}','{tipoempleado}','{estadopostulado}',1)
                        """
                        cur1.execute(sql1)  # escrbimos la consulta
                        cur2 = mysql.connection.cursor()
                        sql2 = f"""
                        INSERT INTO programasgovpostulado (docIdent,tipoDoc,programaGobiernoEmpleo)
                        VALUES('{docident}','{tipo_doc}','{programagobierno}')
                        """
                        cur2.execute(sql2)
                        mysql.connection.commit()
                        flash('Tu informacion ha sido guardada satisfactoriamente, podras editarla en cualquier momento')
                        return render_template('form-postulados.html')
                    else:
                        flash('Hey wat')
                        return render_template('form-postulados.html')
                else:
                    flash('inicia sesion para continuar')
                    return render_template('login.html')
        else:
            flash('inicia sesion para continuar')
            return render_template('login.html')

#funciones para editar formulario postulado inicial ya
@app.route('/edit-postulado/<id>', methods=['GET','POST'])
def EditPostulado(id):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        sql=(f"""SELECT pos.tieneLibretaMilitar,pgp.programaGobiernoEmpleo,pos.tipoEmpleado,pos.minRangoSalarial,pos.resumenPerfil FROM postulado pos
        JOIN programasgovpostulado pgp ON pgp.docIdent=pos.docIdent AND pgp.tipoDoc=pos.tipoDoc
            WHERE pos.docIdent= '{session['docIdent']}' AND pos.tipoDoc = '{session['tipoDoc']}'""")
        cur.execute(sql)
        dataedit = cur.fetchall()[0]
        cur1 = mysql.connection.cursor()
        sql1 = """
        SELECT * FROM programagobiernoempleo
        """
        cur1.execute(sql1)
        programasGobierno=cur1.fetchall()
        cur2=mysql.connection.cursor()
        sql2 = """
        SELECT tipoEmpleado FROM tipoempleado
        """
        cur2.execute(sql2)
        tipoEmpleados=cur2.fetchall()
        f={0:'No',1:'Si'}
        idPostulado=encrypt(session)
        return render_template('edit-postulado.html',data=dataedit,programasGobierno=programasGobierno,tipoEmpleados=tipoEmpleados,tieneLibreta=f,idPostulado=idPostulado)

    if request.method == 'POST':
        k = check(id,session)
        if k:
            #datos generales postulado
            rol=session['rol']
            tipoDoc=session['tipoDoc']
            docIdent=session['docIdent']
            nombre=session['nombre']
            #comprobar con sql primero si no tiene mas de un registro
            #datos generales postulado
            ahora = datetime.now()
            docident = session['docIdent']
            tipo_doc = session['tipoDoc']
            libretamil = request.form['libretamil']
            tipoempleado = request.form['estadolaboral']
            programagobierno = request.form['programasgobierno']
            minrangosalarial = request.form['minrangosalarial']
            perfillaboral = request.form['perfillaboral']
            aceptaterminos = 'SI'
            estadopostulado = 'ACTTIVO'
            fecha_actual = date(ahora.year, ahora.month, ahora.day)
            fecharegistro = fecha_actual
            hora_actual = time(ahora.hour, ahora.minute, ahora.second)
            horaregistro = hora_actual
            if request.form.get('check')=='on':
                #conexion y guardado
                cur1 = mysql.connection.cursor()  # obtenemos conexion
                sql1 = f"""
                UPDATE postulado SET
                TieneLibretaMilitar={libretamil},
                minRangoSalarial={minrangosalarial},
                resumenPerfil='{perfillaboral}',
                tipoEmpleado='{tipoempleado}',estadoPostulado='{estadopostulado}',aceptaTerminos=1
                WHERE tipoDoc='{tipo_doc}' AND docIdent='{docident}'
                """
                cur1.execute(sql1)  # escrbimos la consulta
                cur2 = mysql.connection.cursor()
                sql2 = f"""
                UPDATE programasgovpostulado SET programaGobiernoEmpleo='{programagobierno}'
                WHERE docIdent='{docident}' AND tipoDoc='{tipo_doc}'
                """
                cur2.execute(sql2)
                mysql.connection.commit()
                flash('Tu informacion ha sido guardada satisfactoriamente, podras editarla en cualquier momento')
                return render_template('form-postulados.html')
            else:
                flash('Nigga wtf')
                return render_template('form-postulados.html')
        else:
            #sesion pop
            return render_template('login.html')


#funcion para eliminar formulario de postulado inicial ya  
@app.route('/del-info-postulado/<id>')
def DeletePostulado(id):
    k = check(id,session)
    if k:
        cur = mysql.connection.cursor()
        sql=f"""DELETE FROM postulado WHERE docIdent ='{session['docIdent']}' AND tipoDoc='{session['tipoDoc']}' """
        cur.execute(sql)
        mysql.connection.commit()
        flash('informacion eliminada satisfactoriamente')
        return render_template('form-postulados.html')
    else:
        flash('inicia sesion para poder continuar')
        return render_template('login.html')
    
########## FUNCIONES DE FORMULARIOS ESTUDIOS
#funciones para formularios de estudios a empleo ya
@app.route('/estudios', methods=['GET','POST'])
def FormPersonaEstudios():
    if request.method == 'GET':
        if session:
            if 'rol' in session:
                rol=session['rol']
                tipoDoc=session['tipoDoc']
                docIdent=session['docIdent']
                nombre=session['nombre']
                #datos escolares
                cur1 = mysql.connection.cursor()
                cur1.execute('SELECT * FROM nivel_estudio')
                nivelestudios = cur1.fetchall()
                cur2 = mysql.connection.cursor()
                cur2.execute('SELECT * FROM definicion_niveles')
                definicionniveles = cur2.fetchall()
                return render_template('form-estudios.html')
            else:
                flash('inicia sesion para continuar')
                return render_template('login.html')

    if request.method == 'POST':
        if session:
            if 'Usertype' in session:
                Usertype = session['Usertype']
            if 'Nombre' in session:
                Nombre = session['Nombre']
            #datos generales postulado
            tituloobtenido = request.form['tituloobtenido']
            nivelestudio = request.form['nivelestudio']
            finalizado = request.form['finalizado']
            nombreinstitucion = request.form['nombreinstitucion']
            extranjero = request.form['extranjero']
            fechainicio = request.form['fechainicio']
            fechafinal = request.form['fechafinal']
            definicionniveles = request.form['definicionniveles']
            nivelaprobado = request.form['nivelaprobado']
            #conexion y guardado
            cur = mysql.connection.cursor()  # obtenemos conexion
            cur.execute()  # escrbimos la consulta
            mysql.connection.commit()
            flash('Tu informacion ha sido guardada satisfactoriamente, podras editarla en cualquier momento')
            return render_template('form-estudios.html')
        else:
            flash('inicia sesion para continuar')
            return render_template('login.html')

#funciones para editar formulario estudios ya
@app.route('/edit-estudios/<id>', methods=['GET','POST'])
def EditEstudios(id):
    if request.method == 'GET':
        if session:
            if 'Usertype' in session:
                Usertype = session['Usertype']
            if 'Nombre' in session:
                Nombre = session['Nombre']
            cur = mysql.connection.cursor()
            sql=('SELECT * FROM clientes WHERE CliNumDoc= {0}'.format(id))
            cur.execute(sql)
            dataedit = cur.fetchall()
            return render_template('edit-estudios.html')
        else:
            flash('inicia sesion para continuar')
            return render_template('login.html')

    if request.method == 'POST':
        if session:
            if 'Usertype' in session:
                Usertype = session['Usertype']
            if 'Nombre' in session:
                Nombre = session['Nombre']
            tituloobtenido = request.form['tituloobtenido']
            nivelestudio = request.form['nivelestudio']
            finalizado = request.form['finalizado']
            nombreinstitucion = request.form['nombreinstitucion']
            extranjero = request.form['extranjero']
            fechainicio = request.form['fechainicio']
            fechafinal = request.form['fechafinal']
            definicionniveles = request.form['definicionniveles']
            nivelaprobado = request.form['nivelaprobado']
            #conexion y guardado
            cur = mysql.connection.cursor()  # obtenemos conexion
            cur.execute()  # escrbimos la consulta
            mysql.connection.commit()
            flash('Tu informacion ha sido guardada satisfactoriamente, podras editarla en cualquier momento')
            return render_template('form-estudios.html')
        else:
            flash('inicia sesion para continuar')
            return render_template('login.html')

#funcion para eliminar formulario de estudios ya  
@app.route('/del-info-postulado/<id>')
def DeleteEstudios(id):
    if session:
        if 'Usertype' in session:
            Usertype = session['Usertype']
        if 'Nombre' in session:
            Nombre = session['Nombre']
        cur = mysql.connection.cursor()
        sql=('DELETE FROM usuarios WHERE UsuNumDoc = {0}'.format(id))
        cur.execute(sql)
        mysql.connection.commit()
        flash('usuario eliminado satisfactoriamente')
        return render_template('form-estudios.html')
    else:
        flash('inicia sesion para poder continuar')
        return render_template('login.html')
    


#funciones para configuraciones
@app.route('/profile')
def GeneralProfile():
    return render_template('general-profile.html')

#funciones formularios personas general, postulados, estudios, idiomas, experiencia
@app.route('/idiomas', methods=['GET','POST'])  
def FormPersonaIdiomas():
    if request.method == 'GET':
        #datos idiomas
        #cur1 = mysql.connection.cursor()
        #cur1.execute('SELECT * FROM idiomas')
        #idiomas = cur1.fetchall()
        #cur2 = mysql.connection.cursor()
        #cur2.execute('SELECT * FROM nivel_idiomas')
        #nivelesidiomas = cur2.fetchall()
        return render_template('form-idiomas.html')

    if request.method == 'POST':
        idioma = request.form['idioma']
        nivelidioma = request.form['nivelidioma']
        certifidioma = request.form['certifidioma']
        #conexion y guardado
        cur = mysql.connection.cursor()  # obtenemos conexion
        cur.execute()  # escrbimos la consulta
        mysql.connection.commit()
        flash('Tu informacion ha sido guardada satisfactoriamente, podras editarla en cualquier momento')
        return redirect(url_for('FormPersonaExperiencia'))  # nombre de la ruta

@app.route('/experiencia-laboral', methods=['GET','POST'])  
def FormPersonaExperiencia():
    if request.method == 'GET':
        #datos idiomas
        #cur1 = mysql.connection.cursor()
        #cur1.execute('SELECT * FROM profesiones')
        #profesiones = cur1.fetchall()
        return render_template('form-experiencia.html')

    if request.method == 'POST':
        trabajoactual = request.form['trabajoactual']
        fechainicio = request.form['fechainicio']
        fechafin = request.form['fechafin']
        nombreempresa = request.form['nombreempresa']
        telefonoempresa = request.form['telefonoempresa']
        cargo = request.form['cargo']
        otrocargo = request.form['otrocargo']
        funcioneslaborales = request.form['funcioneslaborales']
        #conexion y guardado
        cur = mysql.connection.cursor()  # obtenemos conexion
        cur.execute()  # escrbimos la consulta
        mysql.connection.commit()
        flash('Tu informacion ha sido guardada satisfactoriamente, podras editarla en cualquier momento')
        return redirect(url_for('FormPersonaPsico'))  # nombre de la ruta

@app.route('/prueba-psicotecnica', methods=['GET','POST'])  
def FormPersonaPsico():
    return render_template('form-psico.html')

#funcionarios
@app.route('/filtro-empleo', methods=['GET','POST'])  
def FuncionarioEmpleo():
    return render_template('filtro-empleo.html')

#funcionarios
@app.route('/cde-fort', methods=['GET','POST'])  
def CDEFortalecimiento():
    if request.method == 'GET':
        return render_template('cde-fortalecimiento.html')
    
    if request.method == 'POST':
        print(request.form.getlist('my_checkbox'))

#funciones para añadir
#añadir usuario
@app.route('/addPersonaGen', methods=['POST'])
def addPersonaGeneral():
    if request.method == 'POST':
        primernombre = request.form['primer-nom']
        segundonombre = request.form['segundo-nom']
        primerapellido = request.form['primer-ape']
        segundoapellido = request.form['segundo-ape']
        tipodocumento = request.form['tipodocumento']
        numerodocumento = request.form['numdocumento']
        fechanacimiento = request.form['fechanacimiento']
        genero = request.form['genero']
        correoelectronico = request.form['correoelectronico']
        telefonofijo = request.form['telefijo']
        telefonocel = request.form['telecel']
        discapacidad = request.form['discapacidad']
        nacionalidad = request.form['nacionalidad']
        barrio = request.form['barrio']
        direccion = request.form['direccion']
        estadocivil = request.form['estcivil']
        libretamil = request.form['libretamil']
        estadolaboral = request.form['estadolaboral']
        usuario = request.form['usuario']
        passuser = request.form['passuser']
        cur = mysql.connection.cursor()  # obtenemos conexion
        cur.execute()  # escrbimos la consulta
        mysql.connection.commit()
        flash('Cuenta creada satisfactoriamente, ingresa con tu usuario y contraseña')
        return redirect(url_for('Index'))  # nombre de la ruta

#añadir idiomas
@app.route('/addIdiomas', methods=['POST'])
def addIdioma():
    if request.method == 'POST':
        idiomapostulado = request.form['idiomapostulado']
        #sacarlo de la sesion
        #idpostulado = request.form['idiomapostulado']
        nivelidiomapost = request.form['nivelidiomapost']
        certifidioma = request.form['certifidioma']
        imagencertificado = request.form['imagencerti']
        cur = mysql.connection.cursor()  # obtenemos conexion
        cur.execute()  # escrbimos la consulta
        mysql.connection.commit()
        flash('Se ha agregado satisfactoriamente')
        return redirect(url_for('Index'))  # nombre de la ruta

#añadir escolaridad
@app.route('/addEscolaridad', methods=['POST'])
def addEscolaridad():
    if request.method == 'POST':
        tituloobtenido = request.form['tituloobtenido']
        #sacarlo de la sesion
        #idpostulado = request.form['idiomapostulado']
        nivelescolaridad = request.form['nivelescolaridad']
        estadoactual = request.form['estadoactual']
        definicionniveles = request.form['definicionniveles']
        fechainicio = request.form['fechainicio']
        fechafinal = request.form['fechafinal']
        nivelaprobado = request.form['nivelaprobado']
        cur = mysql.connection.cursor()  # obtenemos conexion
        cur.execute()  # escrbimos la consulta
        mysql.connection.commit()
        flash('Se ha agregado satisfactoriamente')
        return redirect(url_for('Index'))  # nombre de la ruta

if __name__ == '__main__':
    app.run(port=3000, debug=True)  # PUERTO Y MODO PRUEBAS
