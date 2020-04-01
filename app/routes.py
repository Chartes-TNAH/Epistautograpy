#Import de Flask et de la fonction render_template depuis le 
#module flask.
#Import de la variable request pour récupérer des informations depuis le formulaire
from flask import render_template, request, flash, redirect, url_for
from .app import app, db
from sqlalchemy import or_, and_
from sqlalchemy import distinct
from flask_login import login_user, current_user, logout_user
from .modeles.utilisateurs import User
from .constantes import LETTRES_PAR_PAGE
from flask import flash, redirect, request
from .modeles.donnees import Authorship, Lettre, Correspondance, Destinataire, Institution_Conservation, Image_Numerisee

#Nombre de résultats par page
LETTRES_PAR_PAGES = 2

#Chemin vers la page d'accueil

#Le décorateur crée une association entre l'URL donnée
#comme argument et la fonction. On définit ensuite une route 
#qui renvoie le contenu de la réponse liée à une requête. 
@app.route("/")
#Fonction render_template qui prend commme premier argument 
#le chemin du template et ensuite des arguments nommés utilisés 
#comme des variables dans les templates.
def accueil(exemple=None):
	lettres = Lettre.query.filter(Lettre.date_envoie_lettre).all()
	return render_template("pages/accueil.html", nom="Epistautograpy", lettres=lettres)


#Chemins vers les indexs 

@app.route("/index_lettres")
def index_lettres():
	lettres = Lettre.query.order_by(Lettre.id_lettre).all()
	return render_template("pages/index_lettres.html", nom="Epistautograpy", lettres=lettres)

@app.route("/index_dates")
def index_dates():
	dates = Lettre.query.order_by(Lettre.date_envoie_lettre).all()
	return render_template("pages/index_dates.html", nom="Epistautograpy", dates=dates, lettre=lettre)

@app.route("/index_destinataires")
def index_destinataires():
	destinataires = Destinataire.query.with_entities(Destinataire.identite_destinataire).distinct().order_by(Destinataire.identite_destinataire).all()
	return render_template("pages/index_destinataires.html", nom="Epistautograpy", destinataires=destinataires)

@app.route("/index_contresignataires")
def index_contresignataires():
	contresignataires = Lettre.query.with_entities(Lettre.contresignataire_lettre).distinct().order_by(Lettre.contresignataire_lettre).all()
	return render_template("pages/index_contresignataires.html", nom="Epistautograpy", contresignataires=contresignataires)

@app.route("/index_institutions_conservations")
def index_institutions_conservations():
	institutions_conservations = Institution_Conservation.query.with_entities(Institution_Conservation.nom_institution_conservation).distinct().order_by(Institution_Conservation.nom_institution_conservation).all()
	return render_template("pages/index_institutions_conservations.html", nom="Epistautograpy", institutions_conservations=institutions_conservations)


#Chemin vers les pages de contenu

#Création d'une route avec l'identifiant associé à chaque lettre dans la 
#base de données. On a conditionné le type de l'identifiant qui ne peut être
#qu'un entier.
@app.route("/lettre/<id_lettre>", methods=['GET', 'POST'])
def lettre(id_lettre):

	"""Création d'une page de résultat vers une lettre
	:param id_lettre: Clé primaire dans la table Lettre
	:type id_lettre: integer
	:returns: création de la page
	:rtype: page HTML de la lettre souhaitée"""
	
	#Après avoir récupérer les valeurs d'attributs de la table Lettre, on filtre les autres
	#tables qui ont une clé étrangère correspondant au paramètre id_lettre, pour récupérer
	#les informations adéquates
	unique_lettre = Lettre.query.get(id_lettre)
	destinataire = Destinataire.query.filter(db.and_(Destinataire.id_destinataire==Correspondance.destinataire_id,Correspondance.lettre_id==Lettre.id_lettre, Lettre.id_lettre==id_lettre)).first()
	institution_conservation = Institution_Conservation.query.filter(db.and_(Institution_Conservation.id_institution_conservation==Lettre.institution_id, Lettre.id_lettre==id_lettre)).first()
	image_numerisee = Image_Numerisee.query.filter(db.and_(Image_Numerisee.lettre_id==Lettre.id_lettre, Lettre.id_lettre==id_lettre)).first()
	
	return render_template("pages/lettre.html", nom="Epistautograpy", lettre=unique_lettre, contresignataire=contresignataire, destinataire=destinataire, institution_conservation=institution_conservation, institution=institution, image_numerisee=image_numerisee)

@app.route("/date/<date_envoie_lettre>", methods=['GET', 'POST'])
def date(date_envoie_lettre):

	"""Création d'une page de résultat depuis une date vers la lettre correspondante
	:param date_envoie_lettre: Attribut dans la table Lettre
	:type date_envoie_lettre: string
	:returns: création de la page
	:rtype: page HTML de la lettre souhaitée"""

	unique_date = Lettre.query.get(date_envoie_lettre)
	lettres = Lettre.query.filter(Lettre.date_envoie_lettre==date_envoie_lettre).order_by(Lettre.id_lettre).all()
	return render_template("pages/date.html", nom="Epistautograpy", date=unique_date, lettres=lettres, lettre=lettre)

@app.route("/destinataire/<id_destinataire>", methods=['GET', 'POST'])
def destinataire(id_destinataire):

	"""Création d'une page de résultat vers un destinataire
	:param id_destinataire: Clé primaire dans la table Destinataire
	:type id_destinataire: integer
	:returns: création de la page
	:rtype: page HTML du destinataire souhaité"""

	#Après avoir récupérer les valeurs d'attributs de la table Destinataire, on filtre les autres
	#tables qui ont une clé étrangère correspondant au paramètre id_destinataire pour récupérer
	#les informations adéquates
	unique_destinataire = Destinataire.query.get(id_destinataire)
	lettres = Lettre.query.filter(db.and_(Lettre.id_lettre==Correspondance.lettre_id, Correspondance.destinataire_id==Destinataire.id_destinataire, Destinataire.id_destinataire==id_destinataire)).order_by(Lettre.id_lettre).all()
	
	return render_template("pages/destinataire.html", nom="Epistautograpy", destinataire=unique_destinataire, lettres=lettres, lettre=lettre)

@app.route("/contresignataire/<nom_contresignataire>")
def contresignataire(nom_contresignataire):

	"""Création d'une page de résultat type pour les lettres signées par un même contresignataire
	:param nom_contresignataire: Nom du contresignataire indiqué dans la table Lettre
	:type id_lettre: string
	:returns: création de la page
	:rtype: page HTML de la lettre souhaitée"""

	unique_contresignataire = Lettre.query.get(nom_contresignataire)
	unique_lettre = Lettre.query.filter(Lettre.id_lettre)
	lettres_signees = Lettre.query.filter(db.and_(Lettre.contresignataire_lettre==unique_contresignataire, Lettre.id_lettre==unique_lettre)).order_by(Lettre.id_lettre).all()

	return render_template("pages/contresignataire.html", nom="Epistautograpy", contresignataire=unique_contresignataire, lettres_signees=lettres_signees, lettre=lettre)

@app.route("/institution/<id_institution_conservation>")
def institution(id_institution_conservation):

	"""Création d'une page de résultat vers une institution avec la liste des lettres qu'elle conserve
	:param id_institution_conservation: Clé primaire dans la table Institution_Conservation
	:type id_institution_conservation: integer
	:returns: création de la page
	:rtype: page HTML de l'institution souhaitée"""

	#Après avoir récupérer les valeurs d'attributs de la table Institution_Conservation, on filtre les autres
	#tables qui ont une clé étrangère correspondant au paramètre id_institution_conservation, pour récupérer
	#les informations adéquates
	unique_institution = Institution_Conservation.query.get(id_institution_conservation)
	lettres = Lettre.query.filter(db.and_(Lettre.institution_id==Institution_Conservation.id_institution_conservation, Institution_Conservation.id_institution_conservation)).all()
	
	return render_template("pages/contresignataire.html", nom="Epistautograpy", institution=unique_institution, lettres=lettres, lettre=lettre)


#Chemins vers pages dynamiques 

@app.route("/formulaire", methods=["GET", "POST"])
def formulaire():
	listedatelettre = Lettre.query.with_entities(Lettre.date_envoie_lettre).distinct()
	listelieulettre = Lettre.query.with_entities(Lettre.lieu_ecriture_lettre).distinct()
	listecontresignataire = Lettre.query.with_entities(Lettre.contresignataire_lettre).distinct()
	listelangue = Lettre.query.with_entities(Lettre.langue_lettre).distinct()
	listepronom = Lettre.query.with_entities(Lettre.pronom_personnel_employe_lettre).distinct()
	listecote = Lettre.query.with_entities(Lettre.cote_lettre).distinct()
	listestatut = Lettre.query.with_entities(Lettre.statut_lettre).distinct()
	listetypedestinataire = Destinataire.query.with_entities(Destinataire.type_destinataire).distinct()
	listetitredestinataire = Destinataire.query.with_entities(Destinataire.titre_destinataire).distinct()
	listeidentitedestinataire = Destinataire.query.with_entities(Destinataire.identite_destinataire).distinct()
	listenominstitution = Institution_Conservation.query.with_entities(Institution_Conservation.nom_institution_conservation).distinct()
	listeurlimage = Image_Numerisee.query.with_entities(Image_Numerisee.url_image_numerisee).distinct()

	if request.method=="POST":
		#Lettre
		date=request.form.get("Date", None)
		lieu= request.form.get("Lieu", None)
		contresignataire=request.form.get("Contresignataire", None)
		langue=request.form.get("Langue", None)
		pronom=request.form.get("Pronom", None)
		cote=request.form.get("Cote", None)
		statut=request.form.get("Statut", None)
		#Destinataire
		type_destinataire=request.form.get("Type_Destinataire", None)
		titre_destinataire=request.form.get("Titre_Destinataire", None)
		identite=request.form.get("Identite_Destinataire", None)
		#Institution
		nom=request.form.get("Nom_Institution", None)

		id_lettre=Lettre.ajouter(date, lieu, contresignataire, langue, pronom,cote, statut)
		id_destinataire=Destinataire.ajouter(type_destinataire, titre_destinataire, identite)
		id_institution=Institution_Conservation.ajouter(nom)
		Lettre.association_Destinataire_Lettre(id_destinataire, id_lettre)
		flash("Ajout réussi", "success")
		return render_template("pages/formulaire.html")


	return render_template("pages/formulaire.html", nom="Epistautograpy", listedatelettre=listedatelettre,
		listelieulettre=listelieulettre, listecontresignataire=listecontresignataire, listelangue=listelangue,
		listepronom=listepronom, listecote= listecote, listestatut=listestatut, listetypedestinataire=listetypedestinataire,
		listetitredestinataire=listetitredestinataire, listeidentitedestinataire=listeidentitedestinataire,
		listenominstitution=listenominstitution, listeurlimage=listeurlimage)


@app.route("/recherche")
def recherche():
	# On utilise .get ici pour partager les résultats de recherche de manière simple
	#  et qui nous permet d'éviter un if long en mettant les deux conditions entre parenthèses
	motclef = request.args.get("keyword", None)
	page = request.args.get("page", 1)
	#Association d'une page de résultat à un numéro de page ; s'il n'y a pas de résultats
	#retour automatique à la première page de résultats.
	if isinstance(page, str) and page.isdigit():
		page = int(page)
	else:
		page = 1

	# On crée une liste vide de résultat (qui restera vide par défaut
	#   si on n'a pas de mot clé)
	resultats = []
	# On fait de même pour le titre de la page
	titre = "Recherche"
	if motclef:
		resultats = Lettre.query.filter(or_(
			Lettre.objet_lettre.like("%{}%".format(motclef))),
			Lettre.date_envoie_lettre.like("%{}%".format(motclef)),
			Destinataire.type_destinataire.like("%{}%".format(motclef)),
			Destinataire.titre_destinataire.like("%{}%".format(motclef)),
			Destinataire.identite_destinataire.like("%{}%".format(motclef))

			).paginate(page=page, per_page=LETTRES_PAR_PAGES)

		titre = "Résultat pour la recherche `" + motclef + "`"

		return render_template("pages/recherche.html", resultats=resultats, titre=titre, keyword=motclef)


@app.route('/rechercheavancee', methods=["POST", "GET"])
def rechercheavancee ():
	page = request.args.get("page", 1)

	if isinstance(page, str) and page.isdigit():
		page = int(page)
	else:
		page = 1

	if request.method == "POST":

		resultats = []

		titre = "Recherche"

		keyword="test"
		question=Lettre.query

		 #Lettre
		date=request.form.get("Date", None)
		lieu= request.form.get("Lieu", None)
		contresignataire=request.form.get("Contresignataire", None)
		langue=request.form.get("Langue", None)
		pronom=request.form.get("Pronom", None)
		cote=request.form.get("Cote", None)
		statut=request.form.get("Statut", None)
		#Destinataire
		type_destinataire=request.form.get("Type_Destinataire", None)
		titre_destinataire=request.form.get("Titre_Destinataire", None)
		identite=request.form.get("Identite_Destinataire", None)
		#Institution
		nom=request.form.get("Nom_Institution", None)

		if date:
			question=question.filter(Lettre.Date.like("%{}%".format(date)))
		if lieu:
			question=question.filter(Lettre.Lieu.like("%{}%".format(lieu)))
		if contresignataire:
			question=question.filter(Lettre.contresignataire.like("%{}%".format(contresignataire)))
		if langue:
			question=question.filter(Lettre.langue.like("%{}%".format(langue)))
		if pronom:
			question=question.filter(Lettre.pronom.like("%{}%".format(pronom)))
		if cote:
			question=question.filter(Lettre.cote.like("%{}%".format(cote)))
		if statut:
			question=question.filter(Lettre.statut.like("%{}%".format(statut)))
		if type_destinataire:
			question=question.filter(Lettre.destinataires.any(Destinataire.type_destinatatire.like("%{}%".format(type_destinatatire))))
		if titre_destinataire:
			question=question.filter(Lettre.destinataires.any(Destinataire.titre_destinataire.like)("%{}%".format(titre_destinatatire)))
		if identite:
			question=question.filter((Lettre.destinataires.any(Destinataire.identite_destinataire.like)("%{}%".format(identite))))
		if nom:
			question=question.filter((Lettre.institutions.any(Institution_Conservation.nom_institution_conservation.like)("%{}%".format(nom))))
		question=question.paginate(page=page)

		return render_template(
			"pages/recherche.html",
			resultats=question,
			titre=titre,
			keyword=keyword
		)

	return render_template("pages/rechercheavancee.html",nom="Epistautograpy")


@app.route("/formulaire_lettre", methods=["GET", "POST"])
def formulaire_lettre():
	listeLettre = Lettre.query.all()
	if request.method == "POST" :
		date=request.form.get("Date", None)
		lieu=request.form.get("Lieu", None)
		objet=request.form.get("Objet", None)
		contresignataire=request.form.get("Contresignataire", None)
		langue=request.form.get("Langue", None)
		pronom=request.form.get("Pronom Personnel employé", None)
		cote=request.form.get("Cote", None)
		statut=request.form.get("Statut", None)

		Lettre.ajouter(date, lieu, objet, contresignataire, langue, pronom, cote, statut)
		flash("Ajout réussi", "success")
		return render_template('pages/formulaire_lettre.html', nom="Epistautograpy", listeLettre=listeLettre)

	return render_template('pages/formulaire_lettre.html', nom="Epistautograpy", listeLettre=listedatelettre)


@app.route("/formulaire_destinataire", methods=["GET", "POST"])
def formulaire_destinataire():
	listeDestinataire = Destinataire.query.all()
	if request.method == "POST" :
		type_destinataire=request.form.get("Type", None)
		titre=request.form.get("Titre", None)
		identite=request.form.get("Identité", None)
		naissance=request.form.get("Naissance", None)
		deces=request.form.get("Décès", None)

		Destinataire.ajouter(type_destinataire, titre, identite, naissance, deces)
		flash("Ajout réussi", "success")
		return render_template('pages/formulaire_destinataire.html', nom="Epistautograpy", listeDestinataire=listeDestinataire)

	return render_template('pages/formulaire_destinataire.html', nom="Epistautograpy", listeDestinataire=listeDestinataire)


@app.route("/formulaire_institution", methods=["GET", "POST"])
def formulaire_institution():
	listeInstitution = Institution_Conservation.query.all()
	if request.method == "POST" :
		nom=request.form.get("Nom", None)
		latitude=request.form.get("Latitude", None)
		longitude=request.form.get("Longitude", None)

		Institution_Conservation.ajouter(nom, latitude, longitude)
		flash("Ajout réussi", "success")
		return render_template('pages/formulaire_institution.html', nom="Epistautograpy", listeInstitution=listeInstitution)

	return render_template('pages/formulaire_institution.html', nom="Epistautograpy", listeInstitution=listeInstitution)


@app.route("/formulaire_image", methods=["GET", "POST"])
def formulaire_image():
	listeImage = Image_Numerisee.query.all()
	if request.method == "POST" :
		url=request.form.get("URL", None)
		biblio=request.form.get("Référence bibliographique", None)

		Image_Numerisee.ajouter(url, biblio)
		flash("Ajout réussi", "success")
		return render_template('pages/formulaire_image.html', nom="Epistautograpy", listeImage=listeImage)

	return render_template('pages/formulaire_image.html', nom="Epistautograpy", listeImage=listeImage)


@app.route("/register", methods=["GET", "POST"])
#Route appelant les différentes fonctions de l'identification et de la création
#de comptes séparées dans utilisateurs.py
def inscription():
	""" Route gérant les inscriptions
	"""
# Si on est en POST, cela veut dire que le formulaire a été envoyé
	if request.method == "POST":
		statut, donnees = User.creer(
			login=request.form.get("login", None),
			email=request.form.get("email", None),
			nom=request.form.get("nom", None),
			motdepasse=request.form.get("motdepasse", None)
		)
		if statut is True:
			flash("Enregistrement effectué. Identifiez-vous maintenant", "success")
			return redirect("/")
		else:
			flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
			return render_template("pages/inscription.html")
	else:
		return render_template("pages/inscription.html")


@app.route("/connexion", methods=["POST", "GET"])
def connexion():   
	if current_user.is_authenticated is True:
		flash("Vous êtes déjà connecté-e", "info")
		return redirect(url_for("accueil"))
# Si on est en POST, cela veut dire que le formulaire a été envoyé
	if request.method == "POST":
		utilisateur = User.identification(
			login=request.form.get("login", None),
			motdepasse=request.form.get("motdepasse", None)
		)
		if utilisateur:
			flash("Connexion effectuée", "success")
			login_user(utilisateur)
			return redirect(url_for("accueil"))
		else:
			flash("Les identifiants n'ont pas été reconnus", "error")

	return render_template("pages/connexion.html")


@app.route("/deconnexion", methods=["POST", "GET"])
def deconnexion():
	if current_user.is_authenticated is True:
		logout_user()
	flash("Vous êtes déconnecté-e", "info")
	return redirect("/")


#Chemin vers la page "Conditions générales d'utilisation"

@app.route('/cgu')
def cgu():
	return render_template("pages/cgu.html", nom="Epistautograpy")


#Chemin vers page "à propos"

@app.route('/about')
def about():
	return render_template("pages/apropos.html", nom="Epistautograpy")

