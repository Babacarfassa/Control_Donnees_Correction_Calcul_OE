import processing
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import * 
from qgis.utils import *
from collections import defaultdict
from collections import Counter

def Calcul_des_distances_PBO_SRO_function(shape_pbo,shape_cables,shape_sites,Fichier_CONF_PYTHON):
	#shape_cables_Nom_Colonne_Nom=string=CODE_CB
	#shape_cables_Nom_Origine_Depart_Valeur=string=TC-ST-BELL0101
	#shape_pbo_Nom_Colonne_Nom=string=CODE_BPE

	#Nom_Colonne_Origine_cable='originee'
	#Nom_Colonne_cable_Extremite='extremitee'

	#Creation dune liste de mon fichier de configuration
	list_file_con=[]
	layer_ref_conf = QgsVectorLayer(Fichier_CONF_PYTHON, 'Fichier_CONF_PYTHON', 'ogr')
	for field_ref in layer_ref_conf.getFeatures():
		list_file_con.append([field_ref[0],field_ref[1],field_ref[2],field_ref[3]])

	#Declaration des noms des colonnes
	shape_BP_name_BP_NOM='BP_NOM'
	shape_CB_name_CB_NOM='CB_NOM'
	shape_CB_name_CB_Origine='CB_Origine'
	shape_CB_name_CB_Extremite='CB_Extremite'
	shape_CB_name_CB_SECTION='CB_SECTION'
	#Declaration des noms des entites
	shape_CB_name_CB_Origine_SRO='CB_Origine_SRO'

	#Function pour la recuperation de mon code_parametre en fonction de mon fichier de parametrage
	def get_field_name(name_attribut,shape_name):
		field_name=''
		#prov = processing.getObject(shape_name).dataProvider()
		field_names_shape = [field.name() for field in shape_name.pendingFields()]
		for field_ref in list_file_con:
			for field_shape in field_names_shape:
				#if field_shape == field_ref[2]: #feat[1] == nom dattribut du shape dans le fichier de conf
				if field_ref[1] == name_attribut: #feat[4] == code du nom dattribut du shape dans le fichier de conf
						field_name=field_ref[2]
		return field_name

	shape_cables_Nom_Colonne_Nom=get_field_name(shape_CB_name_CB_NOM,shape_cables)#CODE_CB
	shape_cables_Nom_Origine_Depart_Valeur=get_field_name(shape_CB_name_CB_Origine_SRO,shape_cables)#TC-ST-BELL0101
	shape_pbo_Nom_Colonne_Nom=get_field_name(shape_BP_name_BP_NOM,shape_pbo)#CODE_BPE

	Nom_Colonne_Origine_cable=get_field_name(shape_CB_name_CB_Origine,shape_cables)#'originee'
	Nom_Colonne_cable_Extremite=get_field_name(shape_CB_name_CB_Extremite,shape_cables)#'extremitee'
	Nom_Colonne_CB_SECTION=get_field_name(shape_CB_name_CB_SECTION,shape_cables)#'CB_SECTION'


	Nom_Colonne_distance_PBO_NRO='D_PBO_NRO'


	layershape_pbo =  shape_pbo
	layershape_cables = shape_cables
	layershape_sites= shape_sites 

	def ajout_champs():
		
		#layershape_pbo = processing.getObject(shape_pbo)
		#layershape_cables = processing.getObject(shape_cables)

		#Partie des colonnes a ajouter  dans le shapefile shape_pbo
		nom_champs_shape_pbo=[]
		for j in layershape_pbo.dataProvider().fields():
			nom_champs_shape_pbo.append(j.name()) 
		if (Nom_Colonne_distance_PBO_NRO not in nom_champs_shape_pbo) :
			layershape_pbo.dataProvider().addAttributes([QgsField(Nom_Colonne_distance_PBO_NRO,QVariant.Int)])
		layershape_pbo.updateFields()
		layershape_pbo.commitChanges()


		#Partie des colonnes a ajouter  dans le shapefile Cable
		"""nom_champs_cable=[]
		for k in layershape_cables.dataProvider().fields():
			nom_champs_cable.append(k.name()) 
		if  (Nom_Colonne_Nbre_FO_Util not in nom_champs_cable) :
			layershape_cables.dataProvider().addAttributes([QgsField(Nom_Colonne_Nbre_FO_Util,QVariant.String)])
		if  (Nom_Colonne_Nbre_FO_Reel not in nom_champs_cable) :
			layershape_cables.dataProvider().addAttributes([QgsField(Nom_Colonne_Nbre_FO_Reel,QVariant.Int)])
		if  (Nom_Colonne_cable_utilisation not in nom_champs_cable) :
			layershape_cables.dataProvider().addAttributes([QgsField(Nom_Colonne_cable_utilisation,QVariant.Int)])
		if  (Nom_Colonne_Nbre_Log not in nom_champs_cable) :
			layershape_cables.dataProvider().addAttributes([QgsField(Nom_Colonne_Nbre_Log,QVariant.String)])

		layershape_cables.updateFields()
		layershape_cables.commitChanges()"""

	#Execution de la fonction ajout des champs
	ajout_champs()


	def calcul_distance_PBO_NRO(noeud, niveau,distance) :
		
		#somme_fo = 0
		if niveau < 1000:
			#print "debut sommefib " + noeud
			for shape_cables in listshape_cables:
				if shape_cables[1] == noeud:  
					distance_PBO_NRO= calcul_distance_PBO_NRO(shape_cables[2],niveau + 1,shape_cables[3]+distance)
						
			for shape_pbo in listshape_pbo:
				if shape_pbo[0]== noeud:
					shape_pbo[1]=distance                        
					#print shape_pbo[0],';',section,';',etat,';',cb_code,';',statu_cable,';',statu_boite
					#print noeud,';',niveau,';',cb_code,';',distance
		
		#print boite_amont
		#return somme_fo
			
		return 0,0
		

	listshape_cables = []
	for shape_cables in layershape_cables.getFeatures():
		#print shape_cables[0],';',shape_cables.geometry().length()
		#print shape_cables[Nom_Colonne_CB_SECTION],';',shape_cables['ETAT']
		cable = [shape_cables[shape_cables_Nom_Colonne_Nom],shape_cables[Nom_Colonne_Origine_cable],shape_cables[Nom_Colonne_cable_Extremite],shape_cables.geometry().length(),shape_cables[Nom_Colonne_CB_SECTION],-1,-1]
		listshape_cables.append(cable)
	listshape_pbo = []
	for shape_pbos in layershape_pbo.getFeatures():
		shape_pbo = [shape_pbos[shape_pbo_Nom_Colonne_Nom],-1,-1,-1]
		listshape_pbo.append(shape_pbo)

	calcul_distance_PBO_NRO(shape_cables_Nom_Origine_Depart_Valeur,1,0)

	index_distane_PBO_NRO=layershape_pbo.fieldNameIndex(Nom_Colonne_distance_PBO_NRO)
	layershape_pbo.startEditing()
	for shape_pbos in layershape_pbo.getFeatures():
		for boite in listshape_pbo:
			if shape_pbos[shape_pbo_Nom_Colonne_Nom]==boite[0]:
				layershape_pbo.changeAttributeValue(shape_pbos.id(),index_distane_PBO_NRO,boite[1])
				#print boite[0],';',boite[1]

	layershape_pbo.commitChanges()