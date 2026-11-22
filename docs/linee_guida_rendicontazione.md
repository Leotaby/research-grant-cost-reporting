# Linee guida per la rendicontazione dei costi

*Per il personale e l'amministrazione di un progetto di ricerca finanziato dall'UE (Horizon Europe).
Riferimenti puntuali in [rules_reference.md](rules_reference.md). In caso di dubbio prevalgono
l'Accordo di sovvenzione (Grant Agreement) firmato e le condizioni del bando.*

## 1. Le sette condizioni di ammissibilità (art. 6.1 del Grant Agreement)

Un costo reale è ammissibile solo se è:

1. effettivamente sostenuto dal beneficiario;
2. sostenuto durante il periodo di durata del progetto;
3. dichiarato in una delle categorie di budget previste;
4. collegato alle attività descritte nell'Allegato 1 e necessario per realizzarle;
5. identificabile e verificabile;
6. conforme alla normativa nazionale fiscale, del lavoro e previdenziale;
7. ragionevole, giustificato e conforme al principio di sana gestione finanziaria.

## 2. Personale

- Costo = tariffa giornaliera × giornate lavorate sul progetto, arrotondate alla mezza giornata.
- Tariffa giornaliera = costo annuo del personale / 215.
- Ogni persona può dichiarare al massimo **215 giornate l'anno sull'insieme delle sovvenzioni UE**:
  prima di rendicontare, verificare le giornate già dichiarate su altri progetti europei.
- Se l'esercizio non è ancora chiuso, si usa la tariffa dell'ultimo esercizio chiuso.
- **Ogni mese** va compilato un timesheet (o, per chi lavora solo sul progetto, una dichiarazione
  mensile delle giornate), **firmato dalla persona e dal responsabile scientifico**. Senza firma
  quelle giornate non sono rendicontabili.
- Scadenza consigliata: timesheet del mese firmati entro il giorno 5 del mese successivo.

## 3. Missioni (C.1)

- Seguire il regolamento missioni dell'ente: se prevede la classe economica, un volo in business
  va giustificato o rendicontato solo per la tariffa economica.
- Conservare biglietti, carte d'imbarco, fatture dell'alloggio e programma della riunione o del
  convegno, che deve essere collegato al progetto.

## 4. Attrezzature (C.2)

- Si rendiconta **solo l'ammortamento** dei mesi di utilizzo nel periodo, moltiplicato per la quota
  d'uso per il progetto, a partire da quando il bene è disponibile. Mai il prezzo intero, salvo
  che il bando preveda l'opzione del costo pieno.
- Registrare il bene in inventario con data di consegna, vita utile e quota d'uso.

## 5. Altri beni e servizi (C.3) e subappalto (B)

- Fatture intestate all'ente con riferimento al progetto (CUP) e pagamenti tracciabili.
- L'IVA è ammissibile solo se l'ente non può detrarla.
- Il subappalto, cioè l'affidamento a terzi di attività del progetto, deve essere previsto
  nell'Allegato 1; altrimenti serve un emendamento o l'approvazione con la procedura semplificata.

## 6. Acquisti: Codice dei contratti pubblici (D.Lgs. 36/2023)

- Servizi e forniture **sotto 140.000 euro**: affidamento diretto (art. 50, c. 1, lett. b).
- **Da 140.000 euro** fino alle soglie europee: procedura negoziata con almeno cinque operatori
  (art. 50, c. 1, lett. e).
- Sempre: miglior rapporto qualità-prezzo e assenza di conflitti di interesse; conservare la
  documentazione della procedura (CIG, determina, offerte).

## 7. Costi mai ammissibili (art. 6.3)

Interessi passivi, oneri del debito, accantonamenti per perdite future, perdite di cambio,
commissioni bancarie sui trasferimenti dell'ente finanziatore, spese eccessive o sconsiderate,
IVA detraibile, costi sostenuti durante una sospensione dell'accordo, costi già dichiarati su
un'altra sovvenzione UE (doppio finanziamento).

## 8. Costi indiretti

Sono un forfait sui costi diretti ammissibili (25% in Horizon Europe, escluso il subappalto) e non
richiedono giustificativi. Ogni costo diretto non ammissibile fa perdere anche il 25% calcolato su
di esso.

## 9. Certificato e conservazione dei documenti

- In Horizon Europe serve un **certificato di audit sui rendiconti (CFS)** con la relazione finale
  se il contributo UE richiesto raggiunge 430.000 euro: prevedere il costo dell'audit nel budget.
- Conservare tutti i giustificativi per **5 anni dal pagamento del saldo** (3 anni per
  sovvenzioni fino a 60.000 euro).

## 10. Progetti su fondi di coesione (FESR, FSE+)

Per i progetti finanziati con programmi nazionali o regionali cofinanziati dai fondi di coesione
valgono il Regolamento (UE) 2021/1060 e il DPR 10 marzo 2025, n. 66: il costo orario del personale
si calcola dividendo il costo annuo lordo documentato per **1.720 ore** (in proporzione per il
part-time), e l'IVA è ammissibile solo se non recuperabile.

## 11. Calendario dei controlli

| Quando | Cosa |
| --- | --- |
| Ogni mese | Timesheet e dichiarazioni firmati; fatture registrate con CUP |
| Ogni trimestre | Controllo con `python -m grantcheck`: giornate rispetto al limite di 215, ammortamenti, IVA, documenti mancanti |
| Prima di ogni relazione periodica | Correggere le non conformità, chiedere le approvazioni (subappalti, emendamenti), preparare il rendiconto |
| Relazione finale | Certificato di audit (CFS) se richiesto |
