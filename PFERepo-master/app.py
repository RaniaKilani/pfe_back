from datetime import datetime
from random import random
from urllib import request
from flask_cors import CORS, cross_origin

from flask_mail import Mail, Message
from flask import Flask, make_response, request, jsonify
from flask_mongoengine import MongoEngine
from mongoengine import EmbeddedDocumentListField, ReferenceField, EmbeddedDocumentField, ListField

from APIConst import db_name, user_pwd, secret_key

# configurations !
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
DB_URI = f"mongodb://localhost:27017/pfe"
app.config["MONGODB_HOST"] = DB_URI
db = MongoEngine()
mail = Mail()
db.init_app(app)
mail.init_app(app)



class Reparation(db.Document):
    vh = db.StringField(required=True)
    En = db.StringField(required=True)
    date = db.DateTimeField(required=True, default=datetime.now)

    def to_json(self):
        return {
            "CodeEnt": self.En,
            "Matricule": self.vh,
            "Date": self.date
        }


class Entretien(db.Document):
    codeEnt = db.StringField(required=True)
    Libelle = db.StringField(required=True)

    def to_json(self):
        return {
            "CodeEntretien": self.codeEnt,
            "NomEntretien": self.Libelle,
        }


class Vehicule(db.Document):
    mat = db.StringField(required=True)
    ty = db.StringField(required=True)
    an = db.IntField(required=True)
    mr = db.StringField(required=True)
    tyC = db.StringField(default="Essence")
    conso = db.FloatField(default=0.0)
    powr = db.IntField(default=5)
    etat = db.BooleanField(default=False)
    cap = db.FloatField(default=0.0)
    dispo = db.BooleanField(default=False)
    # rep = ListField(EmbeddedDocumentField(Reparation))
    kilo = db.FloatField()
    nb = db.IntField()

    def to_json(self):
        return {

            "Matricule": self.mat,
            "Typevehicules": self.ty,
            "AnneeFabrication": self.an,
            "Marque": self.mr,
            "Power": self.powr,
            "TypeCarburant": self.tyC,
            "ConsomationCarburant": self.conso,
            "Kilometrage": self.kilo,
            "NombrePlace": self.nb,
            "Capacite": self.cap,

            """Maintenance": [
                {
                    "Climatisation": self.clim,
                    "Parallelisme": self.para,
                    "Vidange": self.vid,
                    "Pneaumatique": self.pneau,
                    "Mouteur": self.mout,
                    "Etat": self.etat"
                 }
            ],"""

            "Disponibilite": self.dispo

        }


class Chauffeur(db.Document):
    counter = 0
    idCh = db.IntField()
    nom = db.StringField(required=True)
    pre = db.StringField(required=True)
    num = db.StringField(required=True)
    dn = db.StringField(required=True)
    de = db.StringField(required=True)
    mail = db.StringField(required=True)
    pwd = db.StringField(required=True)
    adr = db.StringField(required=True)
    nomSup = db.StringField(required=True)

    def addpwd(self):
        liste = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7',
                 '8', '9']
        motDePass = []
        n = 1
        while n <= 25:
            c = int(random() * 62)
            motDePass.append(liste[c])  # Liste motDePass mis a jour
            n = n + 1

        """msg = Message(
            f"Hello{self.nom} {self.pre} This is your App Password : {motDePass} use it to login and becareful ",
            sender="mail@gmail.com", recipients=self.mail)
        mail.send(msg)"""
        ch = ""
        for c in motDePass:
            ch = ch + str(c)

        return ch

    def set_id(self):
        Chauffeur.counter += 1
        self.idCh = Chauffeur.counter

    def set_pwd(self):
        self.pwd = str(hash(self.addpwd()))

    def to_json(self):
        return {

            "IDChauffeur ": self.idCh,
            "Nom": self.nom,
            "prenom": self.pre,
            "Telephone": self.num,
            "DateNaissance": self.dn,
            "DateEmbauche": self.de,
            "Adresse": self.adr,
            "Email": self.mail,
            "Motdepasse": self.pwd,
            "NomSuperviseur": self.nomSup,


        }


class Superviseur(db.Document):
    counter = 0
    idsup = db.IntField()
    nom = db.StringField(required=True)
    pre = db.StringField(required=True)
    num = db.StringField(required=True)
    dn = db.DateField(required=True)
    de = db.DateField(required=True)
    mail = db.StringField(required=True)
    pwd = db.StringField(required=True)
    adr = db.StringField(required=True)

    def set_id(self):
        Superviseur.counter += 1
        self.idsup = Superviseur.counter

    def set_pwd(self):
        self.pwd = str(hash(self.pwd))

    def to_json(self):
        return {

            "IDSuperviseur": self.idsup,
            "Nom": self.nom,
            "prenom": self.pre,
            "Telephone": self.num,
            "DateNaissance": self.dn,
            "DateEmbauche": self.de,
            "Adresse": self.adr,
            "Email": self.mail,
            "Motdepasse": self.pwd,

        }


class Users(db.Document):
    nom = db.StringField()
    pre = db.StringField()
    mail = db.StringField()
    pwd = db.StringField()
    id = db.StringField()

    def to_json(self):
        return {
            "ID": self.id,
            "Nom ": self.nom,
            "prenom": self.pre,
            "Email": self.mail,
            "Motdepasse ": self.pwd,
        }


# Routes !
# Reparation crud

@app.route("/rep", methods=['POST', 'GET', 'DELETE'])
def repar():
    if request.method == 'GET':
        Rs = []
        for r in Reparation.objects():
            Rs.append(r)
        return make_response(jsonify(Rs), 200)
    elif request.method == "POST":
        content = request.json
        n = Entretien.objects.count()
        E = Entretien.objects(codeEnt=content["codeEnt"]).first()
        V = Vehicule.objects(mat=content["Matricule"]).first()
        if E == None:
            return make_response("Entretien Inexistant", 201)
        elif V == None:
            return make_response("Véhicule Inexistante", 201)
        else:
            x = Reparation.objects(vh=content["Matricule"], En=content["codeEnt"]).count()
            if x == 0:
                R = Reparation(vh=content["Matricule"], En=content["codeEnt"])
                R.save()
                c = Reparation.objects(vh=content["Matricule"]).count()
                if c == n or c > n:
                    et = True
                else:
                    et = False
                R.update(etat=et, dispo=et)
                return make_response("Reparation ajoutée avec succées ", 200)

            else:
                return make_response("Réparation Existe déjà  ", 201)
    else:
        for r in Reparation.objects():
            r.delete()
        for v in Vehicule.objects():
            v.update(etat=False, dispo=False)
        return make_response("Suppression de tous les Réparations avec succées!", 200)


@app.route("/onerep/crud", methods=['POST', 'GET', 'DELETE'])
def one_rep():
    content = request.json
    if request.method == "GET":
        R = Reparation.objects(vh=content["Matricule"], En=content["codeEnt"]).first()
        if R == "None":
            return make_response("Réparation inexistante", 201)
        else:
            return make_response(jsonify("Réparation : ", R.to_jsoon()), 200)

    elif request.method == "POST":
        R = Reparation.objects(vh=content["Matricule"], En=content["codeEnt"]).first()
        if R == "None":
            return ("Réparation inexistante ! ", 201)
        else:
            n = Entretien.objects.count()
            R.update(date=datetime.now)
            c = Reparation.objects(vh=content["Matricule"]).count()
            if c == n or c > n:
                et = True
            else:
                et = False
            R.update(etat=et, dispo=et)
            return make_response("Mise à jour effectuée avec succées  ! ", 200)
    else:
        R = Reparation.objects(vh=content["Matricule"], En=content["codeEnt"]).first()
        if R == "None":
            return ("Réparation inexistante ! ", 201)
        else:
            n = Entretien.objects.count()
            R.delete()
            c = Reparation.objects(vh=content["Matricule"]).count()
            if c == n:
                et = True
            else:
                et = False
            R.update(etat=et, dispo=et)
            return make_response("Suppression effectuée avec succées  ! ", 200)


# Entretien crud
@app.route("/ent", methods=['POST', 'GET', 'DELETE'])
def Ent():
    if request.method == 'GET':
        Es = []
        for e in Entretien.objects():
            Es.append(e.to_json())
        return make_response(jsonify("Les entretiens disponibles : ", Es), 200)
    elif request.method == 'POST':
        content = request.json
        E = Entretien.objects(codeEnt=content["codeEnt"]).first()
        if E == None:
            E = Entretien(Libelle=content["Libelle"], codeEnt=content["codeEnt"])
            E.save()
            return make_response("Entretien Ajoutée", 200)

        else:
            return make_response("Entretien Existe Deja", 201)
    else:
        for e in Entretien.objects():
            e.delete()
        return make_response("Suppression de tous les Entretiens avec succées!", 200)


@app.route("/oneent/crud", methods=['POST', 'GET', 'DELETE'])
def one_ent():
    content = request.json
    if request.method == "GET":
        E = Entretien.objects(mat=content["codeEnt"]).first()
        if E == "None":
            return make_response("Entretien inexistante", 201)
        else:
            return make_response(jsonify("Entretien : ", E.to_jsoon()), 200)

    elif request.method == "POST":
        E = Entretien.objects(codeEnt=content["codeEnt"]).first()
        if E == "None":
            return make_response("Entretien Inexxistant", 201)
        else:
            E.update(codeEnt=content["codeEnt"], libelle=content["libelle"])
            return make_response("Mise à jour avec succés !", 200)
    else:
        E = Entretien.objects(codeEnt=content["codeEnt"]).first()
        if E == "None":
            return make_response("Entretien Inexxistant", 201)
        else:
            E.delete()
            return make_response("Suppression avec succés !", 200)


# Vehicule crud
@app.route("/vh", methods=['POST', 'GET', 'DELETE'])
def CrudVehicule():
    if request.method == "GET":
        Vs = []
        for v in Vehicule.objects():
            Vs.append(v.to_json())
        return make_response(jsonify("Tous les véhicules :", Vs), 200)

    elif request.method == "POST":

        MAT = request.form.get("Matricule")
        TYPE = request.form.get("Typevéhicules")
        ANNEE = request.form.get("AnneeFabrication")
        MARQ = request.form.get("Marque")
        CONSO = request.form.get("ConsomationCarburant")
        TYPC = request.form.get("TypeCarburant")
        POW = request.form.get("Power")
        NBr = request.form.get("NombrePlace")
        CAP = request.form.get("Capacité (kg)")
        DISPO = request.form.get("Disponibilite")
        KILO = request.form.get("Kilometrage")
        X = Vehicule.objects(mat=MAT).first()
        if X == "None":
            V = Vehicule(mat=MAT, ty=TYPE, an=ANNEE, mr=MARQ,
                         conso=CONSO, tyC=TYPC,
                         powr=POW, cap=CAP, dispo=DISPO, kilo=KILO,
                         nb=NBr)
            V.save()
            return make_response("Ajout avec succées ! ", 200)
        else:
            return make_response("Véhicule existe déjà!", 201)

    else:
        Vehicule.objects.delete()
        return make_response("Suppression avec succées du tous les véhicules !", 200)


@app.route("/onevh/crud", methods=['PUT', 'GET', 'DELETE'])
def OneVehicule():
    MAT = request.form.get("Matricule")

    if request.method == "GET":
        V = Vehicule.objects(mat=MAT).first()
        if V == "None":
            return make_response("Vehicule inexistante", 201)
        else:
            return make_response(jsonify("Véhicule : ", V.to_jsoon()), 200)

    elif request.method == "POST":
        TYPE = request.form.get("Typevehicules")
        ANNEE = request.form.get("AnneFabrication")
        MARQ = request.form.get("Marque")
        CONSO = request.form.get("ConsomationCarburant")
        TYPC = request.form.get("TypeCarburant")
        POW = request.form.get("Power")
        NBr = request.form.get("NombrePlace")
        CAP = request.form.get("Capacite")
        DISPO = request.form.get("Disponibilite")
        KILO = request.form.get("Kilometrage")
        V = Vehicule.objects(mat=MAT).first()
        if V == "None":
            return make_response("Vehicule inexistante", 201)
        else:
            V.update(mat=MAT, ty=TYPE, an=ANNEE, mr=MARQ,
                     conso=CONSO, tyC=TYPC,
                     powr=POW,
                     cap=CAP, dispo=DISPO, kilo=KILO,
                     nb=NBr)
            return make_response("Mise à jour avec sucées ! ", 200)

    elif request.method == "DELETE":
        V = Vehicule.objects(mat=MAT).first()
        if V == "None":
            return make_response("Vehicule inexistante", 201)
        else:
            V.delete()
            return make_response("Suppression avec Succés!", 200)


# Superviseur crud
@app.route("/sv", methods=['POST', 'GET', 'DELETE'])
def CrudSuperviseur():
    if request.method == "GET":
        Vs = []
        for v in Superviseur.objects():
            Vs.append(v.to_json())
        return make_response(jsonify("Les superviseurs sont : ", Vs), 200)
    elif request.method == "POST":
        content = request.json
        X = Superviseur.objects(mail=content["Email"])
        if X == "None":
            V = Superviseur(nom=content["Nom"], pre=content["prenom"], num=content["Telephone"],
                            dn=content["DateNaissance"], de=content["DateEmbauche"],
                            mail=content["Email"], adr=content["Adresse"])

            V.set_pwd()
            V.set_id()
            U = Users(nom=content["Nom"], pre=content["prenom"], mail=content["Email"], pwd=V.pwd, id="Sup")
            V.save()
            U.save()
            return make_response("Ajout avec succées !", 200)
        else:
            return make_response("Superviseur Existe déjà!", 201)
    else:
        Superviseur.objects.delete()
        U = Users.objects(id="Sup")
        for u in U:
            u.delete()
        return make_response("Suppression de tous les superviseurs du systéme!", 200)


@app.route("/onesv/crud", methods=['GET', 'POST', 'DELETE'])
def OneSuperviseur():
    content = request.json

    if request.method == "GET":
        V = Superviseur.objects(mail=content["Email"]).first()
        if V == "None":
            return make_response("Superviseur Inexistant", 201)
        else:
            return make_response(jsonify({"Superviseur : ": V.to_jsoon()}), 200)

    elif request.method == "PUT":
        V = Superviseur.objects(mail=content["Email"]).first()
        if V == "None":
            return make_response("Superviseur Inexistant", 201)
        else:
            V.update(nom=content["Nom"], pre=content["prenom"], num=content["Telephone"],
                     dn=content["DateNaissance"], de=content["DateEmbauche"],
                     mail=content["Email"], adr=content["Adresse"])
            U = Users.objects(mail=content["Email"]).first()
            U.update(nom=content["Nom"], pre=content["prenom"], mail=content["Email"], pwd=V.pwd, id="Sup")

            return make_response("Mise à jour avec succées! ", 200)

    else:
        V = Superviseur.objects(mail=content["Email"]).first()
        if V == "None":
            return make_response("Superviseur Inexistant", 201)
        else:
            V.delete()
            U = Users.objects(mail=content["Email"]).first
            U.delete()
            return make_response("Suppression du superviseur avec succées  !", 200)

@cross_origin()
# Chauffeur crud
@app.route("/ch", methods=['POST', 'GET', 'DELETE'])
def CrudChauffeur():
    if request.method == "GET":
        Vs = []
        for v in Chauffeur.objects():
            Vs.append(v.to_json())
        return make_response(jsonify(Vs), 200)

    elif request.method == "POST":
        content = request.json
        X = Chauffeur.objects(mail=content["Email"]).first()
        if X == "None":
            return make_response("Chauffeur existe déjà!", 201)
        else:

            V = Chauffeur(nom=content["Nom"], pre=content["prenom"], num=content["Telephone"],
                          dn=content["DateNaissance"], de=content["DateEmbauche"],
                          mail=content["Email"], adr=content["Adresse"], nomSup=content["NomSuperviseur"])
            V.set_pwd()
            U = Users(nom=content["Nom"], pre=content["prenom"], mail=content["Email"], pwd=V.pwd, id="Chauff")
            U.save()
            V.set_id()
            V.save()
            return make_response("Ajout d'un chauffeur avec succées", 200)
    elif request.method == "DELETE":
        Chauffeur.objects.delete()
        U = Users.objects(id="Chauff")
        for u in U:
            u.delete()
        return make_response("Suppression de tous les Chauffeurs avec succées", 200)


@app.route("/onech/crud", methods=['POST', 'GET', 'DELETE'])
def OneChauffeur():
    content = request.json
    if request.method == "GET":
        V = Chauffeur.objects(mail=content["Email"]).first()
        if V == "None":
            return make_response("Chauffeur inexistant ! ", 201)
        else:
            return make_response(jsonify({"Your Data ": V.to_jsoon()}), 200)
    elif request.method == "POST":
        V = Chauffeur.objects(mail=content["Email"]).first()
        if V == "None":
            return make_response("Chauffeur inexistant ! ", 201)
        else:
            U = Users.objects(mail=content["Email"]).first()

            V.update(nom=content["Nom"], pre=content["prenom"], num=content["Telephone"],
                     dn=content["DateNaissance"], de=content["DateEmbauche"],
                     mail=content["Email"], adr=content["Adresse"])
            U.update(nom=content["Nom"], pre=content["prenom"], mail=content["Email"], pwd=V.pwd)

            return make_response("Mise à jour d'un chauffeur avec succées ! ", 200)
    else:
        V = Chauffeur.objects(mail=content["Email"]).first()
        if V == "None":
            return make_response("Chauffeur inexistant ! ", 201)
        else:
            V.delete()
            U = Users.objects(mail=content["Email"]).first
            U.delete()
            return make_response("Suppression du chauffeur avec succées !", 200)


if __name__ == '__main__':
    app.run()
