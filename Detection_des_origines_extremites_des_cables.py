import processing,os,sys,csv,fileinput
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import * 
from qgis.utils import *

def Detection_des_origines_extremites_des_cables_function(shape_pbo,shape_cables,shape_sro,Fichier_CONF_PYTHON,shape_suf):
	#Creation dune liste de mon fichier de configuration
	list_file_con=[]
	layer_ref_conf = QgsVectorLayer(Fichier_CONF_PYTHON, 'Fichier_CONF_PYTHON', 'ogr')
	for field_ref in layer_ref_conf.getFeatures():
		list_file_con.append([field_ref[0],field_ref[1],field_ref[2],field_ref[3]])


	#Declaration des noms des colonnes
	shape_BP_name_BP_NOM='BP_NOM'
	shape_BP_name_BP_FONCTION='BP_FONCTION'
	shape_CB_name_CB_NOM='CB_NOM'
	shape_CB_name_CB_Origine='CB_Origine'
	shape_CB_name_CB_Extremite='CB_Extremite'
	shape_CB_name_CB_CAPACITE='CB_CAPACITE'
	shape_CB_name_CB_LONGUEUR='CB_LONGUEUR'
	shape_CB_name_CB_TYPE_FONC='CB_TYPE_FONC'
	shape_ST_name_ST_NOM='ST_NOM'
	shape_SF_name_SF_NOM='SF_NOM'

	#Declaration des noms des entites
	shape_BP_name_BP_FONCTION_PBO='BP_FONCTION_PBO'
	shape_BP_name_BP_FONCTION_BPE='BP_FONCTION_BPE'
	shape_BP_name_BP_FONCTION_PEC_PBO='BP_FONCTION_PEC'
	shape_CB_name_CB_Origine_SRO='CB_Origine_SRO'
	shape_CB_name_CB_TYPE_FONC_RACCORDEMENT='CB_TYPE_FONC_RACCORDEMENT'
	shape_CB_name_CB_TYPE_FONC_DISTRIBUTION='CB_TYPE_FONC_DISTRIBUTION'


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



	shape_pbo_Nom_Colonne_Nom=get_field_name(shape_BP_name_BP_NOM,shape_pbo)#NOM
	shape_sro_Nom_Colonne_Nom_sro=get_field_name(shape_ST_name_ST_NOM,shape_sro)#CODE

	shape_pbo_Colonne_Nom=get_field_name(shape_BP_name_BP_NOM,shape_pbo)#NOM
	shape_cables_Colonne_Nom=get_field_name(shape_CB_name_CB_NOM,shape_cables)#NOM
	shape_cables_Colonne_Longueur_=get_field_name(shape_CB_name_CB_LONGUEUR,shape_cables)#LGR_CARTO
	shape_cables_Colonne_Capa=get_field_name(shape_CB_name_CB_CAPACITE,shape_cables)#CAPACITE

	Nom_Colonne_Origine_calculee_cable=get_field_name(shape_CB_name_CB_Origine,shape_cables)#originee
	Nom_Colonne_cable_Extremite_calculee=get_field_name(shape_CB_name_CB_Extremite,shape_cables)#extremitee

	Nom_Colonne_BP_FONCTION=get_field_name(shape_BP_name_BP_FONCTION,shape_pbo)
	Nom_Entite_BP_FONCTION_PBO=get_field_name(shape_BP_name_BP_FONCTION_PBO,shape_pbo)
	Nom_Entite_BP_FONCTION_BPE=get_field_name(shape_BP_name_BP_FONCTION_BPE,shape_pbo)
	Nom_Colonne_CB_TYPE_FONC=get_field_name(shape_CB_name_CB_TYPE_FONC,shape_cables)
	Nom_Entite_CB_TYPE_FONC_RACCORDEMENT=get_field_name(shape_CB_name_CB_TYPE_FONC_RACCORDEMENT,shape_cables)
	Nom_Entite_CB_TYPE_FONC_DISTRIBUTION=get_field_name(shape_CB_name_CB_TYPE_FONC_DISTRIBUTION,shape_cables)
	
	Nom_Colonne_SF_NOM=get_field_name(shape_SF_name_SF_NOM,shape_suf)


	#Partie dajout des champs pour des besoins ulterieur
	def ajout_champs(shape_cables,Nom_Colonne_Origine_calculee_cable,Nom_Colonne_cable_Extremite_calculee):
		
		layershape_cables =shape_cables
		nom_champs_cable=[]
		for k in layershape_cables.dataProvider().fields():
			nom_champs_cable.append(k.name()) 
		if (Nom_Colonne_Origine_calculee_cable not in nom_champs_cable):
			layershape_cables.dataProvider().addAttributes([QgsField(Nom_Colonne_Origine_calculee_cable,QVariant.String)])
		if (Nom_Colonne_cable_Extremite_calculee not in nom_champs_cable):
			layershape_cables.dataProvider().addAttributes([QgsField(Nom_Colonne_cable_Extremite_calculee,QVariant.String)])
		layershape_cables.updateFields()
		layershape_cables.commitChanges()



	def Ajout_SRO_BOITE(shape_pbo,shape_sro,shape_pbo_Nom_Colonne_Nom,shape_sro_Nom_Colonne_Nom_sro):
		
		layerPBO = shape_pbo
		layersro = shape_sro
		
		pr = layerPBO.dataProvider()
		
		
		for sro in layersro.getFeatures():
			a='ko'
			for pbo in layerPBO.getFeatures():
				if (QgsGeometry.fromWkt(sro.geometry().exportToWkt())).within(pbo.geometry().buffer(0.1,0.1)):
					a =''
			if a == 'ko':
				attrs=sro[shape_sro_Nom_Colonne_Nom_sro]
				fet = QgsFeature()
				fet.setGeometry(QgsGeometry.fromWkt(sro.geometry().exportToWkt()))
				fet.setAttributes([attrs])
				pr.addFeatures([fet])



	def detection_origine_extremite(shape_cables,shape_pbo,Nom_Colonne_Origine_calculee_cable,Nom_Colonne_cable_Extremite_calculee,shape_pbo_Nom_Colonne_Nom,shape_suf):
		
		#Partie detection des origines et des extremites des shape_cables
		#Description: Cette partie du script permet de detecter, de calculer et de remplir les origines et extremites des shape_cables en fonction des boites (PBO). Nous avons besoin de deux shapefiles: shape_cables et boites (PBO). Les contraintes sont les shape_cables de transports doivent avoir que des boites de transports et idem pour les shape_cables de distributions.
		
		
		'''qid = QInputDialog()
		title = "Enter Your Name"
		label = "Name: "
		mode = QLineEdit.Normal
		default = 'shape_pbo[shape_pbo_Nom_Colonne_Nom]'
		text,ok= QInputDialog.getText(qid, title, label, mode, default)
		print text'''   
		
		#global nom_fichier_synoptique
		
		#nom_fichier_synoptique=QFileDialog.getSaveFileName(caption=QCoreApplication.translate("Save node layer as","Save nodes layer as"),directory=os.getcwd(),filter="CSV file (*.csv)")
		#nombre_attribut_synoptique= open(nom_fichier_synoptique, 'w')
		#path_csv_save=os.path.abspath (nom_fichier_synoptique)
		
		layershape_cables = shape_cables
		layershape_pbo = shape_pbo
		layershape_pbo2 = shape_pbo
		layershape_suf = shape_suf#processing.getObject(shape_suf)

		ida=layershape_cables.fieldNameIndex(Nom_Colonne_Origine_calculee_cable)
		idb=layershape_cables.fieldNameIndex(Nom_Colonne_cable_Extremite_calculee)

		layershape_cables.startEditing()
		
		layerPBO = shape_pbo
		layerPBO2 = shape_pbo
		
		list_boite_superpose=[]
		
		for shape_pbo in layershape_pbo.getFeatures():
			count_sortant = 0
			count_rentrant = 0
			count_boite_extremite=0
			bboxshape_cables = shape_pbo.geometry().buffer(0.5,0.5).boundingBox()
			request = QgsFeatureRequest()
			request.setFilterRect(bboxshape_cables)
		
			for shape_pbo2 in layershape_pbo2.getFeatures(request):
				#ERREUR si boites qui se supperposent
			 if shape_pbo.geometry().within(shape_pbo2.geometry().buffer(0.1,0.1)) and shape_pbo[shape_pbo_Nom_Colonne_Nom] != shape_pbo2[shape_pbo_Nom_Colonne_Nom]:
				 
				 list_boite_superpose.append( shape_pbo[shape_pbo_Nom_Colonne_Nom])
		#print list_boite_superpose
		for ligne in layershape_cables.getFeatures():
			#Mettre des filtres pour des performances
			bboxshape_cables = ligne.geometry().buffer(5,5).boundingBox()
			request = QgsFeatureRequest()
			request.setFilterRect(bboxshape_cables)
			
			geom_cable=ligne.geometry()
			
			if geom_cable.wkbType()==QGis.WKBMultiLineString:
				geom_cable_type=geom_cable.asMultiPolyline()
				cable_origine=geom_cable_type[0][0]
				cable_extremite=geom_cable_type[-1][-1]
				
			if geom_cable.wkbType()==QGis.WKBLineString:
				geom_cable_type=geom_cable.asPolyline()
				cable_origine=geom_cable_type[0]
				cable_extremite=geom_cable_type[-1]
				

			if geom_cable.wkbType() in [QGis.WKBMultiLineString,QGis.WKBLineString]:  
				
				for geom_shape_pbo in layershape_pbo.getFeatures(request):
					a= geom_shape_pbo[0]
					
					if (QgsGeometry.fromPoint(QgsPoint(cable_origine))).within (geom_shape_pbo.geometry().buffer(0.1,0.1)):
						a= geom_shape_pbo[0]
						if geom_shape_pbo[shape_pbo_Nom_Colonne_Nom] in list_boite_superpose:
							
							if geom_shape_pbo[Nom_Colonne_BP_FONCTION] == Nom_Entite_BP_FONCTION_PBO and ligne[Nom_Colonne_CB_TYPE_FONC] ==Nom_Entite_CB_TYPE_FONC_RACCORDEMENT:
								layershape_cables.changeAttributeValue(ligne.id(),ida, unicode(geom_shape_pbo[shape_pbo_Nom_Colonne_Nom]))
							#Boite superposee si type de boite == BPE et type de cable == distri
							if geom_shape_pbo[Nom_Colonne_BP_FONCTION] == Nom_Entite_BP_FONCTION_BPE and ligne[Nom_Colonne_CB_TYPE_FONC] ==Nom_Entite_CB_TYPE_FONC_DISTRIBUTION:
								layershape_cables.changeAttributeValue(ligne.id(),ida, unicode(geom_shape_pbo[shape_pbo_Nom_Colonne_Nom]))
							elif (geom_shape_pbo[Nom_Colonne_BP_FONCTION] != Nom_Entite_BP_FONCTION_PBO and ligne[Nom_Colonne_CB_TYPE_FONC] !=Nom_Entite_CB_TYPE_FONC_RACCORDEMENT) and (geom_shape_pbo[Nom_Colonne_BP_FONCTION] != Nom_Entite_BP_FONCTION_BPE and ligne[Nom_Colonne_CB_TYPE_FONC] !=Nom_Entite_CB_TYPE_FONC_DISTRIBUTION):
								layershape_cables.changeAttributeValue(ligne.id(),ida, unicode('Il existe deux boites qui se superposent, veillez en choisir une'))
						else:
							layershape_cables.changeAttributeValue(ligne.id(),ida, unicode(geom_shape_pbo[shape_pbo_Nom_Colonne_Nom]))
							
					if  (QgsGeometry.fromPoint(QgsPoint(cable_extremite))).within (geom_shape_pbo.geometry().buffer(0.1,0.1)):
						if geom_shape_pbo[shape_pbo_Nom_Colonne_Nom] in list_boite_superpose:
							#Partie des jarrtieres
							jar='-1'
							if (QgsGeometry.fromPoint(QgsPoint(cable_extremite))).within((QgsGeometry.fromPoint(QgsPoint(cable_origine))).buffer(0.1,0.1)):
								
								if geom_shape_pbo[Nom_Colonne_BP_FONCTION] == Nom_Entite_BP_FONCTION_PBO and ligne[Nom_Colonne_CB_TYPE_FONC] ==Nom_Entite_CB_TYPE_FONC_DISTRIBUTION:
									layershape_cables.changeAttributeValue(ligne.id(),idb, unicode(geom_shape_pbo[shape_pbo_Nom_Colonne_Nom]))
									jar='ok'
							 #Partie des cables hormis jarrtires   
							elif geom_shape_pbo[Nom_Colonne_BP_FONCTION] == Nom_Entite_BP_FONCTION_BPE and ligne[Nom_Colonne_CB_TYPE_FONC] ==Nom_Entite_CB_TYPE_FONC_DISTRIBUTION:
								layershape_cables.changeAttributeValue(ligne.id(),idb, unicode(geom_shape_pbo[shape_pbo_Nom_Colonne_Nom]))
							
							#Autres que jartierres et cables non jartierres
							elif (geom_shape_pbo[Nom_Colonne_BP_FONCTION] != Nom_Entite_BP_FONCTION_BPE and ligne[Nom_Colonne_CB_TYPE_FONC] !=Nom_Entite_CB_TYPE_FONC_DISTRIBUTION) and jar=='-1':
								layershape_cables.changeAttributeValue(ligne.id(),idb, unicode('Il existe deux boites qui se superposent, veillez en choisir une'))
						#Cables sans boite en double
						else:
							layershape_cables.changeAttributeValue(ligne.id(),idb, unicode(geom_shape_pbo[shape_pbo_Nom_Colonne_Nom]))
					else:
						for suf in layershape_suf.getFeatures(request):
							if (QgsGeometry.fromPoint(QgsPoint(cable_extremite))).within(suf.geometry().buffer(0.1,0.1)):
								layershape_cables.changeAttributeValue(ligne.id(),idb, unicode(suf[Nom_Colonne_SF_NOM]))
			"""msgout_rentr = "%s; %s; %s; %s\n" % (ligne[Nom_Colonne_cable_Extremite_calculee],ligne[Nom_Colonne_Origine_calculee_cable],int(ligne[shape_cables_Colonne_Longueur_]),ligne[shape_cables_Colonne_Capa])
			unicode_message_rentr = msgout_rentr#.encode('utf-8')
			nombre_attribut_synoptique.write(unicode_message_rentr)"""
			  
		layershape_cables.commitChanges()
		'''
		lis_data=[]
		headers = [get_field_name(shape_CB_name_CB_Extremite,shape_cables),get_field_name(shape_CB_name_CB_Origine,shape_cables),get_field_name(shape_CB_name_CB_LONGUEUR,shape_cables),get_field_name(shape_CB_name_CB_CAPACITE,shape_cables)]
		for cable in layershape_cables.getFeatures():
			entite_headers=[cable[Nom_Colonne_cable_Extremite_calculee],cable[Nom_Colonne_Origine_calculee_cable],cable[shape_cables_Colonne_Longueur_],cable[shape_cables_Colonne_Capa]]
			lis_data.append(dict(zip(headers,entite_headers)))
		
		Fichier_CONF_PYTHON=QFileDialog.getOpenFileName(None, "Export_Origine_EXtremite", "", "csv files (*.csv)")
		with open(Fichier_CONF_PYTHON, 'w') as outfile:
			mywriter = csv.DictWriter(outfile, fieldnames=headers,delimiter=';',quotechar=';', quoting=csv.QUOTE_MINIMAL,lineterminator='\n')
			mywriter.writeheader()
			for d in lis_data:
				mywriter.writerow(d)
			outfile.close()'''
		
		#nombre_attribut_synoptique.close()
		

		

	#Execution de la fonction ajout des champs originees et extremites
	ajout_champs(shape_cables,Nom_Colonne_Origine_calculee_cable,Nom_Colonne_cable_Extremite_calculee)

	#Execution de la fonction ajout du sro dans boite
	Ajout_SRO_BOITE(shape_pbo,shape_sro,shape_pbo_Nom_Colonne_Nom,shape_sro_Nom_Colonne_Nom_sro)

	#Execution de la fonction detection des origines et extremites
	detection_origine_extremite(shape_cables,shape_pbo,Nom_Colonne_Origine_calculee_cable,Nom_Colonne_cable_Extremite_calculee,shape_pbo_Nom_Colonne_Nom,shape_suf)
