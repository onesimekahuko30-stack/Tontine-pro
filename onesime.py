membres = [
{"nom":"onesime", "paye": True, "montant": 10},
{"nom":"daniel", "paye": False, "montant": 0},
{"nom":"kavet", "paye": True, "montant": 10},
{"nom":"edidiat", "paye": False, "montant": 0},
{"nom":"iconnu", "paye": True, "montant": 10},]
historique = [{"MOIS": "janvier", "beneficiaire": "kavet"}]

ordre_tontine = ["kavet", "iconnu", "daniel", "edidiat", "onesime"]
beneficiaire_actuel  = "iconnu"
prochain_beneficiaire = ""    
for personne in ordre_tontine: 
    deja_recu = False
    for item in historique: 
        if item["beneficiaire"]  == personne: 
            deja_recu = True
    if  deja_recu == False:
         prochain_beneficiaire = personne 
         break            
print("le prochais beneficiaire est:", prochain_beneficiaire)
position = ordre_tontine.index(beneficiaire_actuel)
if position + 1 < len(ordre_tontine):
    prochain_beneficiaire = ordre_tontine[position + 1]
print("beneficiaire actuel :", beneficiaire_actuel)
print("prochain beneficiare :", prochain_beneficiaire)
print("=== ETAT DE PAIEMENT ===")
total = 0
nombre_paye = 0
nombre_non_paye = 0
for membre in membres : 
    if membre["paye"]:
        statut = "A payé"
        nombre_paye = nombre_paye + 1 
    else : 
       statut = "N'a pas payé"
       nombre_non_paye = nombre_non_paye + 1 
    print(membre["nom"], "-", statut, "-", membre["montant"], "$")
    total = total + membre["montant"]
    print(" ")
print("total collecté :", total, "$")

print(" ")
print("=== RETARDATAIRES ===")
print(" ")
for membre in membres: 
    if membre["paye"] == False:
        print(membre["nom"])
        print(" ")
print(" ")
print(nombre_paye, "personnes ont payé")
print(" ")
print(nombre_non_paye, "personnes n'ont pas encore  payé")
print(" ")
print("=== Historique ===")
for item in historique: 
    print(item["MOIS"], ":",
item["beneficiaire"])
    
       
    